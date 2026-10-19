# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "azure-ai-textanalytics==5.4.0",
#   "azure-core==1.41.0",
#   "google-cloud-language==2.21.0",
# ]
# ///
"""
Executa a coleta: envia cada texto a cada provedor e registra tudo.

    # verificação local, SEM rede e SEM custo (marcada como simulada)
    uv run etapa2/src/executar.py --dados etapa2/dados/piloto.csv --simulado

    # coleta real (exige credenciais no .env e pede confirmação)
    uv run etapa2/src/executar.py --dados etapa2/dados/piloto.csv --provedores azure google

    # retomar uma coleta interrompida, sem repetir o que já foi feito
    uv run etapa2/src/executar.py --dados etapa2/dados/teste.csv --retomar <id_execucao>

Decisões de medição (etapa2/metodologia.md):

- **Um texto por chamada, em sequência.** Lotes misturariam duas cargas.
- **Provedores intercalados por texto, em ordem sorteada.** Para cada texto, os
  provedores são chamados em seguida um do outro, em ordem sorteada com semente
  fixa e gravada. Assim os dois enfrentam as mesmas condições de horário e de
  rede, e nenhum é sempre o primeiro.
- **Latência com relógio monotônico** (`time.perf_counter`) imediatamente antes e
  depois da chamada. A criação do cliente fica fora da medida. As esperas entre
  tentativas entram no tempo TOTAL do item, não no tempo de cada tentativa.
- **Novas tentativas só para erro transitório** (limite, timeout, servidor, rede),
  iguais nos dois provedores. Erro de autenticação ou cota esgotada interrompe o
  provedor — continuar só produziria a mesma falha.
- **Registro só de acréscimo** (JSONL, gravado e descarregado a cada linha):
  uma queda no meio não corrompe o que já foi coletado, e `--retomar` continua
  de onde parou.

Arquivos de uma execução em etapa2/resultados/<id_execucao>/:
    config.json          configuração SEM segredos, regra de normalização, plano de custo
    ambiente.json        Python, SO, versões dos SDKs, commit do git, hash do dataset e do código
    tentativas.jsonl     uma linha por tentativa (inclusive as que falharam)
    predicoes.jsonl      uma linha por (texto, provedor): resultado final
    respostas/<prov>/<id>.json   resposta original do serviço, sanitizada
    resumo.json          contagens ao final
"""

import argparse
import csv
import hashlib
import json
import platform
import random
import subprocess
import sys
import time
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import custo  # noqa: E402
import normalizar  # noqa: E402
import seguranca  # noqa: E402
from provedores import ErroProvedor, criar  # noqa: E402
from provedores.base import INTERROMPEM_PROVEDOR  # noqa: E402

RAIZ = AQUI.parents[1]
RESULTADOS = RAIZ / "etapa2" / "resultados"
SIMULACOES = RAIZ / "etapa2" / "simulacoes"        # ignorada pelo git
# Chamadas REAIS fora do experimento (ex.: demonstração ao professor com frases
# de exemplo). Ficam separadas para nunca serem confundidas com a coleta; contam
# no consumo do mês, porque gastam franquia como qualquer outra chamada real.
DEMONSTRACOES = RAIZ / "etapa2" / "demonstracoes"
CONFIG_PADRAO = RAIZ / "etapa2" / "config" / "experimento.json"
CONFIG_EXEMPLO = RAIZ / "etapa2" / "config" / "experimento.example.json"
MAX_CARACTERES = 5000
FRASE_DE_AQUECIMENTO = "O atendimento foi excelente."


def _rel(caminho):
    """Caminho relativo à raiz do projeto, quando estiver dentro dela."""
    try:
        return Path(caminho).resolve().relative_to(RAIZ)
    except ValueError:
        return caminho


# ----------------------------------------------------------------- entrada

def ler_dataset(caminho):
    with open(caminho, encoding="utf-8-sig", newline="") as f:
        linhas = list(csv.DictReader(f))
    if not linhas or "id" not in linhas[0] or "texto" not in linhas[0]:
        raise SystemExit(f"{caminho}: precisa das colunas 'id' e 'texto'.")
    vistos, problemas = set(), []
    for l in linhas:
        if l["id"] in vistos:
            problemas.append(f"ID repetido: {l['id']}")
        vistos.add(l["id"])
        if not l["texto"].strip():
            problemas.append(f"{l['id']}: texto vazio")
        elif len(l["texto"]) > MAX_CARACTERES:
            problemas.append(f"{l['id']}: {len(l['texto'])} caracteres (máx. {MAX_CARACTERES})")
    if problemas:
        raise SystemExit("Dataset inválido:\n  " + "\n  ".join(problemas[:20]))
    return linhas


def sha256_arquivo(caminho):
    return hashlib.sha256(Path(caminho).read_bytes()).hexdigest()


def conferir_congelamento(caminho):
    """
    Se o dataset é um dos conjuntos montados, confere o hash registrado no
    manifesto. Um teste.csv editado depois de montado não é mais o conjunto
    congelado — e a coleta não deve usá-lo sem que isso fique explícito.
    """
    manifesto = Path(caminho).parent / "manifesto_conjuntos.json"
    if not manifesto.exists():
        return None
    registrado = json.loads(manifesto.read_text(encoding="utf-8"))["arquivos"].get(Path(caminho).name)
    if registrado and registrado != sha256_arquivo(caminho):
        raise SystemExit(f"{caminho} foi alterado depois de congelado (hash diferente do "
                         "manifesto_conjuntos.json). Não colete com um conjunto modificado.")
    return registrado


def carregar_config(caminho):
    caminho = Path(caminho)
    if not caminho.exists():
        if caminho == CONFIG_PADRAO:
            caminho = CONFIG_EXEMPLO
        else:
            raise SystemExit(f"Configuração não encontrada: {caminho}")
    return json.loads(caminho.read_text(encoding="utf-8")), caminho


# ---------------------------------------------------------------- ambiente

def _versao(pacote):
    try:
        return version(pacote)
    except PackageNotFoundError:
        return None


def _git(*args):
    try:
        return subprocess.run(["git", *args], cwd=RAIZ, capture_output=True, text=True,
                              check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


ARQUIVO_MAQUINA = Path.home() / ".cache" / "teste_comparativo_nuvem" / "maquina_id"


def identificador_da_maquina():
    """
    Identificador ALEATÓRIO desta máquina, criado na primeira coleta e guardado
    fora do repositório. Serve só para a análise saber se duas coletas vieram do
    mesmo computador (a latência de máquinas diferentes não é comparável). Não é
    derivado do nome do computador nem do usuário, então não revela nenhum dos dois.
    """
    import uuid
    try:
        if ARQUIVO_MAQUINA.exists():
            return ARQUIVO_MAQUINA.read_text(encoding="utf-8").strip()
        ARQUIVO_MAQUINA.parent.mkdir(parents=True, exist_ok=True)
        novo = uuid.uuid4().hex[:12]
        ARQUIVO_MAQUINA.write_text(novo + "\n", encoding="utf-8")
        return novo
    except OSError:
        return None


def descrever_ambiente(caminho_dados):
    codigo = hashlib.sha256()
    for arq in sorted(AQUI.rglob("*.py")):
        codigo.update(arq.relative_to(AQUI).as_posix().encode())
        codigo.update(arq.read_bytes())
    return {
        "python": platform.python_version(),
        "sistema": f"{platform.system()} {platform.release()}",
        "pacotes": {p: _versao(p) for p in ("azure-ai-textanalytics", "azure-core",
                                            "google-cloud-language", "google-api-core",
                                            "google-auth", "protobuf")},
        "git_commit": _git("rev-parse", "HEAD"),
        "git_alteracoes_nao_commitadas": bool(_git("status", "--porcelain", "--", "etapa2/src")),
        "dataset": {"arquivo": Path(caminho_dados).name, "sha256": sha256_arquivo(caminho_dados)},
        "codigo_sha256": codigo.hexdigest(),
        "maquina": identificador_da_maquina(),
    }


# ----------------------------------------------------------------- registro

class Registro:
    """Arquivos JSONL só de acréscimo, descarregados a cada linha."""

    def __init__(self, pasta, simulado, identificadores):
        self.pasta = pasta
        self.simulado = simulado
        self.identificadores = identificadores
        self._tent = open(pasta / "tentativas.jsonl", "a", encoding="utf-8")
        self._pred = open(pasta / "predicoes.jsonl", "a", encoding="utf-8")

    def _linha(self, arquivo, dados):
        dados = seguranca.sanitizar({**dados, "simulado": self.simulado}, self.identificadores)
        arquivo.write(json.dumps(dados, ensure_ascii=False) + "\n")
        arquivo.flush()

    def tentativa(self, **dados):
        self._linha(self._tent, dados)

    def predicao(self, **dados):
        self._linha(self._pred, dados)

    def resposta(self, provedor, id_texto, bruta):
        destino = self.pasta / "respostas" / provedor / f"{id_texto}.json"
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(json.dumps(seguranca.sanitizar(bruta, self.identificadores),
                                      ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return destino.relative_to(self.pasta).as_posix()

    def fechar(self):
        self._tent.close()
        self._pred.close()


def concluidos(pasta):
    """(id, provedor) que já têm resultado final — não serão chamados de novo."""
    arq = pasta / "predicoes.jsonl"
    if not arq.exists():
        return set()
    feitos = set()
    for linha in arq.read_text(encoding="utf-8").splitlines():
        if linha.strip():
            p = json.loads(linha)
            feitos.add((p["id"], p["provedor"]))
    return feitos


# ------------------------------------------------------------------ coleta

def agora_utc():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def executar_item(prov, item, cfg, registro, execucao, ordem, ultima_chamada, dormir=time.sleep):
    """Chama um provedor para um texto, com a política de tentativas. Devolve o código final."""
    texto = item["texto"]
    max_t = cfg["max_tentativas"]
    espera = cfg["espera_entre_tentativas_s"]
    intervalo = cfg.get("intervalo_minimo_s", {}).get(prov.nome, 0)
    unidades = 0 if prov.simulado else custo.unidades(prov.nome, texto)
    limiar = cfg["limiar_google"]

    inicio_item = time.perf_counter()
    ultimo_erro, resposta, n = None, None, 0
    for n in range(1, max_t + 1):
        # respeita o intervalo mínimo entre chamadas ao mesmo provedor (limite de taxa)
        decorrido = time.perf_counter() - ultima_chamada.get(prov.nome, -1e9)
        if decorrido < intervalo:
            dormir(intervalo - decorrido)
        quando = agora_utc()
        t0 = time.perf_counter()
        try:
            resposta = prov.analisar(texto)
            erro = None
        except ErroProvedor as e:
            erro = e
        dt_ms = (time.perf_counter() - t0) * 1000
        ultima_chamada[prov.nome] = time.perf_counter()

        registro.tentativa(
            execucao=execucao, id=item["id"], provedor=prov.nome, tentativa=n,
            data_hora_utc=quando, duracao_ms=round(dt_ms, 3),
            status="ok" if erro is None else "erro",
            codigo=None if erro is None else erro.codigo,
            status_http=None if erro is None else erro.status_http,
            mensagem=None if erro is None else erro.mensagem,
            unidades_estimadas=unidades)
        if erro is None:
            break
        ultimo_erro = erro
        resposta = None
        if not erro.transitorio or n == max_t:
            break
        dormir(espera * n)          # espera linear: 1×, 2×, ... a espera configurada

    total_ms = (time.perf_counter() - inicio_item) * 1000
    base = dict(execucao=execucao, id=item["id"], provedor=prov.nome, ordem_no_texto=ordem,
                n_tentativas=n, duracao_total_ms=round(total_ms, 3),
                duracao_ultima_tentativa_ms=round(dt_ms, 3),
                caracteres=len(texto), bytes_utf8=len(texto.encode("utf-8")),
                unidades_estimadas=unidades * n)
    if resposta is not None:
        arquivo = registro.resposta(prov.nome, item["id"], resposta.bruta)
        rotulo = (resposta.rotulo_original if prov.simulado else
                  normalizar.normalizar(prov.nome, resposta.rotulo_original, resposta.score, limiar))
        registro.predicao(**base, status_final="ok", codigo_erro_final=None,
                          rotulo_original=resposta.rotulo_original, score=resposta.score,
                          magnitude=resposta.magnitude, confiancas=resposta.confiancas,
                          idioma_detectado=resposta.idioma, versao_modelo=resposta.versao_modelo,
                          rotulo_normalizado=rotulo, resposta_arquivo=arquivo)
        return "ok"
    registro.predicao(**base, status_final="erro", codigo_erro_final=ultimo_erro.codigo,
                      mensagem_erro_final=ultimo_erro.mensagem, rotulo_original=None,
                      score=None, magnitude=None, confiancas=None, idioma_detectado=None,
                      versao_modelo=None, rotulo_normalizado=None, resposta_arquivo=None)
    return ultimo_erro.codigo


def aquecer(provedores, registro, execucao, saida=print):
    """
    Uma chamada por provedor antes do primeiro texto (metodologia: "Aquecimento").
    A 1ª chamada carrega a abertura da conexão e a autenticação (~1,6–1,9 s
    contra ~0,85–1,1 s depois, nas verificações de 18/10/2026). Ela é registrada
    em tentativas.jsonl com `aquecimento: true`, conta no consumo, e a análise a
    exclui da latência e do sucesso. Uma falha aqui não interrompe nada: o erro
    real, se persistir, aparece no primeiro texto.
    """
    for prov in provedores:
        quando = agora_utc()
        t0 = time.perf_counter()
        try:
            prov.analisar(FRASE_DE_AQUECIMENTO)
            erro = None
        except ErroProvedor as e:
            erro = e
        dt_ms = (time.perf_counter() - t0) * 1000
        registro.tentativa(
            execucao=execucao, id="aquecimento", provedor=prov.nome, tentativa=1,
            data_hora_utc=quando, duracao_ms=round(dt_ms, 3), aquecimento=True,
            status="ok" if erro is None else "erro",
            codigo=None if erro is None else erro.codigo,
            status_http=None if erro is None else erro.status_http,
            mensagem=None if erro is None else erro.mensagem,
            unidades_estimadas=0 if prov.simulado else custo.unidades(prov.nome, FRASE_DE_AQUECIMENTO))
        saida(f"  aquecimento {prov.nome}: {dt_ms:.0f} ms" + (f" (falhou: {erro.codigo})" if erro else ""))


def coletar(itens, provedores, cfg, registro, execucao, semente, pular=frozenset(),
            dormir=time.sleep, saida=print):
    """Laço principal. Devolve {provedor: Counter de status}."""
    from collections import Counter
    contagem = {p.nome: Counter() for p in provedores}
    interrompidos = {}
    ultima_chamada = {}
    for i, item in enumerate(itens, start=1):
        ordem = list(provedores)
        random.Random(f"{semente}-{item['id']}").shuffle(ordem)
        for posicao, prov in enumerate(ordem, start=1):
            if (item["id"], prov.nome) in pular:
                continue
            if prov.nome in interrompidos:
                registro.predicao(execucao=execucao, id=item["id"], provedor=prov.nome,
                                  ordem_no_texto=posicao, n_tentativas=0, status_final="nao_executado",
                                  codigo_erro_final=interrompidos[prov.nome],
                                  mensagem_erro_final="provedor interrompido nesta execução",
                                  caracteres=len(item["texto"]),
                                  bytes_utf8=len(item["texto"].encode("utf-8")),
                                  unidades_estimadas=0, rotulo_normalizado=None)
                contagem[prov.nome]["nao_executado"] += 1
                continue
            final = executar_item(prov, item, cfg, registro, execucao, posicao,
                                  ultima_chamada, dormir)
            contagem[prov.nome][final] += 1
            if final in INTERROMPEM_PROVEDOR:
                interrompidos[prov.nome] = final
                saida(f"\n  {prov.nome}: INTERROMPIDO por '{final}' no texto {item['id']}. "
                      "Os demais textos ficam como 'nao_executado'.")
        if i % 10 == 0 or i == len(itens):
            saida(f"  {i}/{len(itens)} textos   " + "   ".join(
                f"{n}: {dict(c)}" for n, c in contagem.items()))
    return contagem


# --------------------------------------------------------------------- main

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--dados", required=True, type=Path)
    p.add_argument("--provedores", nargs="+", default=["azure", "google"],
                   choices=["azure", "google"])
    p.add_argument("--config", type=Path, default=CONFIG_PADRAO)
    p.add_argument("--rodada", default="1", help="rótulo da rodada (repetições)")
    p.add_argument("--retomar", metavar="ID_EXECUCAO")
    modo = p.add_mutually_exclusive_group()
    modo.add_argument("--simulado", action="store_true",
                      help="sem rede e sem custo; grava em etapa2/simulacoes/")
    modo.add_argument("--demonstracao", action="store_true",
                      help="chamada REAL fora do experimento; grava em etapa2/demonstracoes/")
    p.add_argument("--sim", action="store_true", help="não pedir confirmação (coleta real)")
    a = p.parse_args(argv)

    cfg, cfg_caminho = carregar_config(a.config)
    itens = ler_dataset(a.dados)
    hash_congelado = conferir_congelamento(a.dados)

    if a.simulado:
        nomes = ["simulado"]
        destino_base = SIMULACOES
        identificadores = []
        print("MODO SIMULADO — nenhum serviço é chamado; nada aqui é evidência de execução.\n")
    else:
        nomes = a.provedores
        destino_base = DEMONSTRACOES if a.demonstracao else RESULTADOS
        if a.demonstracao:
            print("DEMONSTRAÇÃO — chamadas REAIS, mas FORA do experimento: nada daqui entra "
                  "nas métricas da Etapa 2.\n")
        lidas = seguranca.carregar_env()
        suspeitos = seguranca.chaves_soltas_no_repositorio()
        if suspeitos:
            raise SystemExit("ABORTADO: possível credencial em arquivo que o git publicaria:\n  "
                             + "\n  ".join(suspeitos))
        sem = {n: seguranca.faltando(n) for n in nomes if seguranca.faltando(n)}
        if sem:
            raise SystemExit("Faltam credenciais no .env: " + "; ".join(
                f"{n}: {', '.join(v)}" for n, v in sem.items())
                + "\nVeja etapa2/COMO_EXECUTAR.md.")
        if lidas:
            print(f"Variáveis lidas do .env: {', '.join(sorted(lidas))}")
        identificadores = seguranca.identificadores_da_conta()

    # o aquecimento também gasta franquia: entra no plano como mais um texto
    textos_do_plano = [i["texto"] for i in itens] + ([FRASE_DE_AQUECIMENTO] if cfg.get("aquecimento") else [])
    plano = custo.planejar(textos_do_plano, nomes, cfg["max_tentativas"], cfg["orcamento"])

    if a.retomar:
        execucao = a.retomar
        pasta = destino_base / execucao
        if not pasta.exists():
            raise SystemExit(f"Execução não encontrada: {pasta}")
        anterior = json.loads((pasta / "ambiente.json").read_text(encoding="utf-8"))
        if anterior["dataset"]["sha256"] != sha256_arquivo(a.dados):
            raise SystemExit("O dataset mudou desde o início desta execução; não é possível retomar.")
        pular = concluidos(pasta)
    else:
        execucao = f"{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-{Path(a.dados).stem}-r{a.rodada}"
        pasta = destino_base / execucao
        if pasta.exists():
            raise SystemExit(f"{pasta} já existe. Use --retomar {execucao} para continuar.")
        pular = set()

    instancias = []
    for nome in nomes:
        conf = dict(cfg.get("provedores", {}).get(nome, {}))
        if nome == "azure":
            conf.setdefault("tier", cfg["orcamento"].get("azure_tier", "F0"))
        instancias.append(criar(nome, conf))

    pendentes = len(itens) * len(nomes) - len(pular)
    print(f"Execução: {execucao}")
    print(f"Dataset:  {a.dados}  ({len(itens)} textos{', congelado' if hash_congelado else ''})")
    print(f"Chamadas pendentes: {pendentes} (máx. {cfg['max_tentativas']} tentativas cada)")
    for nome, pl in plano.items():
        if nome != "simulado":
            print(f"  {nome}: {pl['unidades_planejadas']} unidades/rodada, pior caso {pl['pior_caso']}, "
                  f"já usado no mês {pl['consumo_no_mes_antes']} de {pl['franquia_mensal']} "
                  f"→ custo estimado no pior caso US$ {pl['custo_estimado_pior_caso_usd']:.2f}")
    if not a.simulado and not a.sim:
        if input("\nDigite 'sim' para chamar os serviços reais: ").strip().lower() != "sim":
            raise SystemExit("Cancelado.")

    pasta.mkdir(parents=True, exist_ok=True)
    if not a.retomar:
        cfg_gravada = {"execucao": execucao, "rodada": a.rodada, "simulado": a.simulado,
                       "demonstracao": a.demonstracao,
                       "inicio_utc": agora_utc(), "arquivo_config": cfg_caminho.name,
                       "parametros": cfg, "provedores": [i.descrever() for i in instancias],
                       "normalizacao": normalizar.descrever(cfg["limiar_google"]),
                       "plano_de_custo": plano, "semente_ordem": cfg["semente_ordem"],
                       "dataset_congelado": bool(hash_congelado)}
        (pasta / "config.json").write_text(json.dumps(seguranca.sanitizar(cfg_gravada, identificadores),
                                                      ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (pasta / "ambiente.json").write_text(json.dumps(descrever_ambiente(a.dados),
                                                        ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    registro = Registro(pasta, a.simulado, identificadores)
    if cfg.get("aquecimento"):
        aquecer(instancias, registro, execucao)
    try:
        contagem = coletar(itens, instancias, cfg, registro, execucao, cfg["semente_ordem"], pular)
    except KeyboardInterrupt:
        print(f"\nInterrompido. Para continuar sem repetir chamadas:\n  "
              f"uv run etapa2/src/executar.py --dados {a.dados} --retomar {execucao}")
        raise SystemExit(130)
    finally:
        registro.fechar()

    resumo = {"execucao": execucao, "fim_utc": agora_utc(),
              "por_provedor": {n: dict(c) for n, c in contagem.items()}}
    (pasta / "resumo.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=2) + "\n",
                                       encoding="utf-8")
    print(f"\nConcluído. Resultados em {_rel(pasta)}")
    opcao = " --simulado" if a.simulado else " --demonstracao" if a.demonstracao else ""
    print(f"Analisar: uv run etapa2/src/analisar.py --execucao {execucao}{opcao}")


if __name__ == "__main__":
    sys.exit(main())
