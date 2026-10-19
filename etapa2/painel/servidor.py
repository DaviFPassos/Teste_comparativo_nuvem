# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "azure-ai-textanalytics==5.4.0",
#   "azure-core==1.41.0",
#   "google-cloud-language==2.21.0",
# ]
# ///
"""
Painel local da Etapa 2 — Google Cloud Natural Language e Azure Language.

    uv run etapa2/painel/servidor.py              # abre http://127.0.0.1:8765
    uv run etapa2/painel/servidor.py --provedores azure --sem-aquecimento

O painel ativa só os provedores com credencial NESTA máquina e mostra os
demais desabilitados, com o motivo. No laptop de quem tem a conta Google, o
Google fica ativo; no de quem tem a chave da Azure, a Azure. Com as duas, o
seletor alterna entre elas.

Duas abas:
- **Ao vivo:** digita-se uma frase e o painel mostra o que o serviço responde,
  com a mesma regra de classe do experimento (src/normalizar.py).
- **Execuções:** abre as coletas gravadas em etapa2/demonstracoes/ e
  etapa2/resultados/, com as métricas calculadas pelo mesmo analisar.py da linha
  de comando — o painel não tem conta própria.

Por que é um servidor local e não uma página publicada: para analisar uma frase
digitada na hora, alguém precisa chamar o serviço com a credencial de quem
apresenta. Essa credencial nunca sai do computador: o navegador fala só com
este servidor, e o servidor fala com o provedor.

Segurança:
- escuta só em 127.0.0.1 (nada na rede local enxerga o painel);
- confere o cabeçalho Host (bloqueia "DNS rebinding") e exige um cabeçalho
  próprio nas chamadas que gastam franquia, o que um site de terceiros não
  consegue enviar sem autorização do navegador;
- não serve arquivo nenhum além da própria página: as execuções são abertas
  por ID, conferido contra a lista das que existem;
- cada chamada ao vivo passa pela trava de orçamento do provedor (90% da
  franquia mensal, contando coleta, demonstrações e o próprio painel) e por um
  limite por sessão; a Azure só é ativada se a configuração declarar o tier F0;
- o texto digitado NÃO é gravado em disco; só a contagem de unidades, para a
  trava, em etapa2/painel/sessoes/ (ignorada pelo git).
"""

import argparse
import csv
import json
import os
import sys
import threading
import time
import webbrowser
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

AQUI = Path(__file__).resolve().parent
SRC = AQUI.parent / "src"
sys.path.insert(0, str(SRC))

import analisar  # noqa: E402
import custo  # noqa: E402
import normalizar  # noqa: E402
import seguranca  # noqa: E402
from provedores import ErroProvedor  # noqa: E402

RAIZ = AQUI.parents[1]
PAGINA = AQUI / "index.html"
SESSOES = AQUI / "sessoes"
DADOS = RAIZ / "etapa2" / "dados"
CONFIG = RAIZ / "etapa2" / "config" / "experimento.example.json"
BASES = {"demonstracao": RAIZ / "etapa2" / "demonstracoes",
         "experimento": RAIZ / "etapa2" / "resultados"}

NOMES = {"google": "Google Cloud Natural Language", "azure": "Microsoft Azure Language"}
ORDEM = ("google", "azure")

# 1.000 caracteres = 1 unidade no Google e 1 registro na Azure: cada frase custa 1.
MAX_CARACTERES_AO_VIVO = 1000
MAX_CHAMADAS_POR_SESSAO = 200
MAX_CORPO_BYTES = 16_384
FRASE_DE_AQUECIMENTO = "O atendimento foi excelente."


class Estado:
    """Tudo o que o servidor guarda entre requisições."""

    def __init__(self, provedores, indisponiveis=None, sessoes=SESSOES,
                 limiar=normalizar.LIMIAR_GOOGLE_PADRAO, bases=None, dados=DADOS,
                 consumo_externo=None, simulado=False):
        """
        provedores:    {"google": instância, "azure": instância} — só os ativos
        indisponiveis: {"azure": "motivo legível"} — exibidos desabilitados
        """
        self.provedores = dict(provedores)
        self.indisponiveis = dict(indisponiveis or {})
        self.limiar = limiar
        self.bases = BASES if bases is None else bases
        self.dados = dados
        self.consumo_externo = dict(consumo_externo or {})
        self.simulado = simulado
        self.trava = threading.Lock()          # uma chamada a serviço por vez
        self.chamadas = 0
        self.aquecimento_ms = {}
        self.sessao = sessoes / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ-painel")
        self.sessao.mkdir(parents=True, exist_ok=True)
        self.registro = self.sessao / "tentativas.jsonl"

    # ------------------------------------------------------------- orçamento
    def consumo_no_mes(self, prov):
        if self.simulado:
            return 0
        pastas = {Path(p).resolve() for p in custo.PASTAS_REAIS} | {self.sessao.parent.resolve()}
        return (sum(custo.consumo_local_no_mes(prov, p) for p in pastas)
                + int(self.consumo_externo.get(prov, 0)))

    def limite(self, prov):
        return int(custo.franquia_mensal(prov) * custo.FRACAO_SEGURA)

    def _registrar(self, prov, ident, dt_ms, unidades, erro=None):
        linha = {"execucao": self.sessao.name, "id": ident, "provedor": prov,
                 "tentativa": 1, "data_hora_utc": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
                 "duracao_ms": round(dt_ms, 3), "status": "erro" if erro else "ok",
                 "codigo": erro.codigo if erro else None, "unidades_estimadas": unidades,
                 "simulado": self.simulado}
        with open(self.registro, "a", encoding="utf-8") as f:
            f.write(json.dumps(linha, ensure_ascii=False) + "\n")

    # ---------------------------------------------------------------- chamada
    def analisar_texto(self, texto, prov="google", ident=None):
        """Uma chamada real (ou simulada) ao provedor. Devolve (status_http, corpo)."""
        if prov not in NOMES:
            return HTTPStatus.BAD_REQUEST, {"erro": "Provedor desconhecido."}
        if prov not in self.provedores:
            return HTTPStatus.CONFLICT, {"erro": f"{NOMES[prov]} não está disponível nesta máquina.",
                                         "detalhe": self.indisponiveis.get(prov, "")}
        texto = (texto or "").strip()
        if not texto:
            return HTTPStatus.BAD_REQUEST, {"erro": "Digite uma frase."}
        if len(texto) > MAX_CARACTERES_AO_VIVO:
            return HTTPStatus.BAD_REQUEST, {
                "erro": f"No máximo {MAX_CARACTERES_AO_VIVO} caracteres por frase "
                        f"(assim cada chamada custa exatamente 1 unidade)."}
        with self.trava:
            if self.chamadas >= MAX_CHAMADAS_POR_SESSAO:
                return HTTPStatus.TOO_MANY_REQUESTS, {
                    "erro": f"Limite de {MAX_CHAMADAS_POR_SESSAO} chamadas por sessão do painel. "
                            "Reinicie o servidor se precisar de mais."}
            unidades = 0 if self.simulado else custo.unidades(prov, texto)
            if self.consumo_no_mes(prov) + unidades > self.limite(prov):
                return HTTPStatus.PAYMENT_REQUIRED, {
                    "erro": "Trava de orçamento: esta chamada passaria de 90% da franquia "
                            "gratuita do mês. Nenhuma chamada foi feita."}
            ident = ident or f"ao_vivo_{self.chamadas + 1:03d}"
            t0 = time.perf_counter()
            try:
                r = self.provedores[prov].analisar(texto)
                erro = None
            except ErroProvedor as e:
                r, erro = None, e
            dt_ms = (time.perf_counter() - t0) * 1000
            self.chamadas += 1
            self._registrar(prov, ident, dt_ms, unidades, erro)
        if erro:
            return HTTPStatus.BAD_GATEWAY, {
                "erro": f"{NOMES[prov]} recusou a chamada ({erro.codigo}).",
                "detalhe": seguranca.sanitizar(erro.mensagem), "latencia_ms": round(dt_ms, 1)}
        if self.simulado:
            classe = r.rotulo_original
        else:
            classe = normalizar.normalizar(prov, r.rotulo_original, r.score, self.limiar)
        return HTTPStatus.OK, {
            "provedor": prov, "texto": texto, "classe": classe, "limiar": self.limiar,
            "score": r.score, "magnitude": r.magnitude,                       # Google
            "rotulo_original": r.rotulo_original, "confiancas": r.confiancas,  # Azure
            "versao_modelo": r.versao_modelo, "idioma": r.idioma,
            "latencia_ms": round(dt_ms, 1), "unidades": unidades,
            "resposta_original": seguranca.sanitizar(r.bruta), "simulado": self.simulado}

    def aquecer(self):
        """
        Uma chamada por provedor antes da primeira frase de verdade. A 1ª chamada
        é bem mais lenta (conexão + autenticação: ~1,8 s no Google e ~1,6 s na
        Azure, contra ~1,0 s e ~0,85 s depois); sem isso, a primeira frase
        mostrada teria uma latência que não é a típica. Custa 1 unidade cada.
        """
        resultado = {}
        for prov in self.provedores:
            status, corpo = self.analisar_texto(FRASE_DE_AQUECIMENTO, prov, ident="aquecimento")
            if status == HTTPStatus.OK:
                self.aquecimento_ms[prov] = corpo["latencia_ms"]
            resultado[prov] = (status, corpo)
        return resultado

    # -------------------------------------------------------------- execuções
    def listar_execucoes(self):
        lista = []
        for tipo, base in self.bases.items():
            if not base.exists():
                continue
            for pasta in sorted(base.iterdir(), reverse=True):
                cfg, amb = pasta / "config.json", pasta / "ambiente.json"
                if not (cfg.is_file() and amb.is_file()):
                    continue                    # ex.: verificação do Rafael (outro formato)
                c = json.loads(cfg.read_text(encoding="utf-8"))
                a = json.loads(amb.read_text(encoding="utf-8"))
                if c.get("simulado"):
                    continue                    # simulação nunca é exibida como execução
                lista.append({"id": pasta.name, "tipo": tipo,
                              "provedores": [p["nome"] for p in c.get("provedores", [])],
                              "dataset": a["dataset"]["arquivo"], "inicio": c.get("inicio_utc")})
        return lista

    def abrir_execucao(self, ident):
        conhecidas = {e["id"]: e for e in self.listar_execucoes()}
        if ident not in conhecidas:            # nada de caminho vindo do navegador
            return HTTPStatus.NOT_FOUND, {"erro": "Execução não encontrada."}
        meta = conhecidas[ident]
        pasta = self.bases[meta["tipo"]] / ident
        predicoes, tentativas, config, ambiente = analisar.carregar_execucao(pasta)
        try:
            gabarito = analisar.carregar_gabarito(self.dados / ambiente["dataset"]["arquivo"],
                                                  ambiente["dataset"]["sha256"])
        except (SystemExit, FileNotFoundError) as e:
            return HTTPStatus.CONFLICT, {"erro": f"Gabarito indisponível: {e}"}
        res = analisar.analisar(predicoes, tentativas, config, gabarito)
        res.pop("_intersecao_ids", None)
        textos = []
        for p in sorted(predicoes, key=lambda x: (x["id"], x["provedor"])):
            g = gabarito.get(p["id"], {})
            ref = g.get("rotulo_referencia")
            prev = p.get("rotulo_normalizado")
            conf = p.get("confiancas") or None
            textos.append({"id": p["id"], "provedor": p["provedor"], "texto": g.get("texto", ""),
                           "referencia": ref, "previsto": prev, "status": p["status_final"],
                           "score": p.get("score"), "magnitude": p.get("magnitude"),
                           "confiancas": conf,
                           # Azure não tem score: a posição no gráfico é a polaridade
                           # DERIVADA (confiança positiva − negativa), só para visualizar.
                           "polaridade": (conf["positive"] - conf["negative"]) if conf else p.get("score"),
                           "rotulo_original": p.get("rotulo_original"),
                           "latencia_ms": p.get("duracao_ultima_tentativa_ms"),
                           "avaliado": ref in analisar.CLASSES,
                           "acertou": None if ref not in analisar.CLASSES or prev is None else prev == ref})
        latencias = {prov: [t["duracao_ms"] for t in tentativas
                            if t["provedor"] == prov and t["status"] == "ok" and not t.get("aquecimento")]
                     for prov in res["provedores"]}
        return HTTPStatus.OK, {"meta": meta, "metricas": res, "textos": textos,
                               "latencias": latencias, "limiar": config["normalizacao"]["google"]["limiar"]}

    def exemplos(self):
        caminho = self.dados / "demonstracao.csv"
        if not caminho.exists():
            return []
        with open(caminho, encoding="utf-8", newline="") as f:
            return [{"texto": l["texto"], "rotulo": l["rotulo_referencia"]} for l in csv.DictReader(f)]

    def resumo(self):
        provs = []
        for prov in ORDEM:
            item = {"id": prov, "nome": NOMES[prov], "ativo": prov in self.provedores,
                    "motivo": self.indisponiveis.get(prov)}
            if prov in self.provedores:
                item.update(consumo_no_mes=self.consumo_no_mes(prov), limite=self.limite(prov),
                            franquia=custo.franquia_mensal(prov),
                            aquecimento_ms=self.aquecimento_ms.get(prov))
            provs.append(item)
        return {"provedores": provs, "simulado": self.simulado, "limiar": self.limiar,
                "max_caracteres": MAX_CARACTERES_AO_VIVO, "chamadas_na_sessao": self.chamadas,
                "max_chamadas": MAX_CHAMADAS_POR_SESSAO}


def criar_manipulador(estado, porta):
    hosts_validos = {f"127.0.0.1:{porta}", f"localhost:{porta}"}

    class Manipulador(BaseHTTPRequestHandler):
        server_version = "PainelEtapa2"
        sys_version = ""

        def log_message(self, formato, *args):      # sem eco de URL/corpo no terminal
            pass

        def _responder(self, status, corpo, tipo="application/json; charset=utf-8"):
            dados = corpo if isinstance(corpo, bytes) else json.dumps(corpo, ensure_ascii=False).encode()
            self.send_response(status)
            self.send_header("Content-Type", tipo)
            self.send_header("Content-Length", str(len(dados)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Content-Security-Policy",
                             "default-src 'self'; style-src 'self' 'unsafe-inline'; "
                             "script-src 'self' 'unsafe-inline'; img-src 'self' data:; "
                             "connect-src 'self'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(dados)

        def _host_ok(self):
            return self.headers.get("Host", "") in hosts_validos

        def do_GET(self):
            if not self._host_ok():
                return self._responder(HTTPStatus.FORBIDDEN, {"erro": "Host não permitido."})
            url = urlparse(self.path)
            if url.path in ("/", "/index.html"):
                return self._responder(HTTPStatus.OK, PAGINA.read_bytes(), "text/html; charset=utf-8")
            if url.path == "/api/estado":
                return self._responder(HTTPStatus.OK, estado.resumo())
            if url.path == "/api/exemplos":
                return self._responder(HTTPStatus.OK, estado.exemplos())
            if url.path == "/api/execucoes":
                return self._responder(HTTPStatus.OK, estado.listar_execucoes())
            if url.path == "/api/execucao":
                ident = parse_qs(url.query).get("id", [""])[0]
                return self._responder(*estado.abrir_execucao(ident))
            return self._responder(HTTPStatus.NOT_FOUND, {"erro": "Não encontrado."})

        def do_POST(self):
            if not self._host_ok():
                return self._responder(HTTPStatus.FORBIDDEN, {"erro": "Host não permitido."})
            if urlparse(self.path).path != "/api/analisar":
                return self._responder(HTTPStatus.NOT_FOUND, {"erro": "Não encontrado."})
            # Cabeçalho próprio + JSON: um site de terceiros não consegue mandar isso
            # sem uma pré-verificação CORS, que este servidor nunca autoriza.
            if self.headers.get("X-Painel") != "1" or \
                    not self.headers.get("Content-Type", "").startswith("application/json"):
                return self._responder(HTTPStatus.FORBIDDEN, {"erro": "Requisição recusada."})
            tamanho = int(self.headers.get("Content-Length") or 0)
            if tamanho > MAX_CORPO_BYTES:
                return self._responder(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, {"erro": "Texto grande demais."})
            try:
                corpo = json.loads(self.rfile.read(tamanho) or b"{}")
            except ValueError:
                return self._responder(HTTPStatus.BAD_REQUEST, {"erro": "JSON inválido."})
            return self._responder(*estado.analisar_texto(corpo.get("texto"),
                                                          corpo.get("provedor", "google")))

        def do_OPTIONS(self):                         # pré-verificação CORS: sempre negada
            self._responder(HTTPStatus.FORBIDDEN, {"erro": "Origem não permitida."})

    return Manipulador


# --------------------------------------------------------- disponibilidade

def motivo_indisponivel(prov, cfg):
    """None se o provedor pode ser ativado nesta máquina; senão, o motivo legível."""
    falta = seguranca.faltando(prov)
    if falta:
        return f"faltam no .env: {', '.join(falta)}"
    if prov == "google":
        from google.auth import _cloud_sdk
        arquivo = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if not (arquivo and Path(arquivo).is_file()) and \
                not Path(_cloud_sdk.get_application_default_credentials_path()).is_file():
            return "sem login do Google (gcloud auth application-default login)"
    if prov == "azure" and float(cfg["orcamento"].get("teto_usd", 0)) == 0 \
            and cfg["orcamento"].get("azure_tier", "").upper() != "F0":
        return "com teto de US$ 0 só o tier F0 é aceito (declare azure_tier = F0)"
    return None


def abrir_navegador(url):
    """
    No WSL, o webbrowser do Python pode abrir um navegador de TEXTO no próprio
    terminal (lynx, w3m). O explorer.exe abre o navegador padrão do Windows, que
    alcança o 127.0.0.1 do WSL pelo encaminhamento de localhost do WSL2.
    """
    import platform
    import subprocess
    try:
        if "microsoft" in platform.release().lower():
            subprocess.Popen(["explorer.exe", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            webbrowser.open(url)
    except OSError:
        pass                                   # o endereço já foi impresso no terminal


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--porta", type=int, default=8765)
    p.add_argument("--provedores", nargs="+", choices=ORDEM, default=list(ORDEM),
                   help="quais provedores tentar ativar (padrão: os dois)")
    p.add_argument("--sem-aquecimento", action="store_true")
    p.add_argument("--nao-abrir-navegador", action="store_true")
    a = p.parse_args(argv)

    seguranca.carregar_env()
    suspeitos = seguranca.chaves_soltas_no_repositorio()
    if suspeitos:
        raise SystemExit("ABORTADO: possível credencial em arquivo que o git publicaria:\n  "
                         + "\n  ".join(suspeitos))

    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    from provedores import criar
    ativos, indisponiveis = {}, {}
    for prov in ORDEM:
        if prov not in a.provedores:
            indisponiveis[prov] = "desligado na linha de comando (--provedores)"
            continue
        motivo = motivo_indisponivel(prov, cfg)
        if motivo:
            indisponiveis[prov] = motivo
            continue
        conf = dict(cfg["provedores"][prov])
        if prov == "azure":
            conf["tier"] = cfg["orcamento"]["azure_tier"]
        ativos[prov] = criar(prov, conf)

    estado = Estado(ativos, indisponiveis, limiar=cfg["limiar_google"],
                    consumo_externo=cfg["orcamento"].get("consumo_externo_no_mes", {}))
    for prov in ORDEM:
        if prov in ativos:
            print(f"  {NOMES[prov]}: ATIVO — franquia usada no mês {estado.consumo_no_mes(prov)} "
                  f"de {custo.franquia_mensal(prov)} (trava em {estado.limite(prov)})")
        else:
            print(f"  {NOMES[prov]}: desabilitado — {indisponiveis[prov]}")
    if not ativos:
        print("\nNenhum provedor ativo: o painel abre só para ver as execuções gravadas.")
    elif not a.sem_aquecimento:
        for prov, (status, corpo) in estado.aquecer().items():
            print(f"  aquecimento {prov}: {corpo.get('latencia_ms')} ms" if status == HTTPStatus.OK
                  else f"  aquecimento {prov} falhou: {corpo.get('erro')} {corpo.get('detalhe', '')}")

    servidor = ThreadingHTTPServer(("127.0.0.1", a.porta), criar_manipulador(estado, a.porta))
    url = f"http://127.0.0.1:{a.porta}/"
    print(f"\nPainel em {url}   (Ctrl+C para encerrar)")
    if not a.nao_abrir_navegador:
        threading.Timer(0.6, abrir_navegador, args=(url,)).start()
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print(f"\nEncerrado. Chamadas nesta sessão: {estado.chamadas}.")
    finally:
        servidor.server_close()


if __name__ == "__main__":
    sys.exit(main())
