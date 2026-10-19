# /// script
# requires-python = ">=3.10"
# ///
"""
Anotação humana do gabarito: planilhas, concordância e montagem dos conjuntos.

    uv run etapa2/src/anotacao.py planilhas     # 1. gera uma planilha por anotador
    uv run etapa2/src/anotacao.py consolidar    # 2. concordância + lista de divergências
    uv run etapa2/src/anotacao.py montar        # 3. piloto.csv, teste.csv, exploratorio_misto.csv

Por que o fluxo é assim:

- **Cada anotador recebe a sua planilha, em ordem diferente e sem as estrelas.**
  Ordem diferente evita que o cansaço do fim da lista caia nos mesmos textos para
  os dois; esconder as estrelas evita que a nota dada pelo cliente decida o
  rótulo por quem anota.
- **Ninguém vê a resposta das APIs antes de anotar.** Este script não lê nada de
  etapa2/resultados/. O gabarito precisa ser independente dos provedores.
- **Divergência se resolve por discussão registrada**, não por média nem por
  escolha automática. O script lista as divergências; os anotadores preenchem a
  decisão e a justificativa.
- **Os conjuntos são montados antes de qualquer chamada às APIs.** Separar os
  casos mistos depois de ver onde uma API errou seria escolher o resultado.

Rótulos aceitos na planilha:
    positivo · negativo · neutro · misto · invalido
"misto" cobre "ambíguo/misto" do roteiro. "invalido" é para texto que não é uma
avaliação em português legível (spam, outro idioma, sequência sem sentido).
"""

import argparse
import csv
import hashlib
import io
import json
import random
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DADOS = RAIZ / "etapa2" / "dados"
ANOTACAO = DADOS / "anotacao"

ROTULOS = ("positivo", "negativo", "neutro", "misto", "invalido")
CLASSES_PRINCIPAIS = ("positivo", "negativo", "neutro")
SEMENTE_MONTAGEM = 20261018
MAX_POR_CLASSE_PADRAO = 50

CAMPOS_PLANILHA = ["id", "texto", "rotulo", "observacao"]
CAMPOS_DIVERGENCIA = ["id", "texto", "rotulo_A", "rotulo_B", "rotulo_final", "justificativa"]
CAMPOS_CONJUNTO = ["id", "texto", "rotulo_referencia", "origem", "subconjunto",
                   "observacao_anotacao", "caracteres", "bytes_utf8"]


# --------------------------------------------------------------------- E/S

def ler_csv(caminho):
    """
    Lê CSV editado por gente: aceita vírgula ou ponto e vírgula e BOM ou não.

    O Excel em português abre e salva CSV com ponto e vírgula; o Google Planilhas
    e o LibreOffice, com vírgula. Quem anota não deveria precisar saber disso.
    """
    texto = Path(caminho).read_text(encoding="utf-8-sig")
    primeira = texto.split("\n", 1)[0]
    separador = ";" if primeira.count(";") > primeira.count(",") else ","
    return list(csv.DictReader(io.StringIO(texto, newline=""), delimiter=separador))


def gravar_csv(caminho, campos, linhas, para_humanos=False):
    """`para_humanos` grava com BOM, para o Excel reconhecer os acentos."""
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w", encoding="utf-8-sig" if para_humanos else "utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        w.writeheader()
        w.writerows(linhas)


def sha256(caminho):
    return hashlib.sha256(Path(caminho).read_bytes()).hexdigest()


def candidatos(dados=DADOS):
    """Todos os candidatos (piloto, teste e lotes extras), indexados por ID."""
    todos = {}
    for arq in sorted(dados.glob("candidatos_*.csv")):
        for l in ler_csv(arq):
            if l["id"] in todos:
                raise SystemExit(f"ID repetido entre arquivos de candidatos: {l['id']}")
            todos[l["id"]] = l
    if not todos:
        raise SystemExit("Nenhum candidato. Rode antes: uv run etapa2/src/amostrar.py")
    return todos


# --------------------------------------------------------------- métricas

def kappa_de_cohen(a, b):
    """
    Kappa de Cohen entre duas listas de rótulos do mesmo tamanho.

        kappa = (p_o - p_e) / (1 - p_e)

    p_o é a concordância observada; p_e, a esperada por acaso dadas as
    frequências de cada anotador. Devolve None quando p_e = 1 (os dois usaram um
    único e mesmo rótulo para tudo), caso em que o kappa não é definido.
    """
    if len(a) != len(b) or not a:
        raise ValueError("listas vazias ou de tamanhos diferentes")
    n = len(a)
    p_o = sum(x == y for x, y in zip(a, b)) / n
    fa, fb = Counter(a), Counter(b)
    p_e = sum(fa[k] * fb[k] for k in set(a) | set(b)) / (n * n)
    if p_e == 1:
        return None
    return (p_o - p_e) / (1 - p_e)


# ---------------------------------------------------------------- comandos

def cmd_planilhas(a):
    (a.dados / "anotacao").mkdir(parents=True, exist_ok=True)
    textos = candidatos(a.dados)
    anotadores = (a.dados / "anotacao") / "anotadores.json"
    if not anotadores.exists():
        anotadores.write_text(json.dumps(
            {"A": "", "B": "",
             "instrucao": "Preencha o nome de quem anotou cada planilha. A identificação "
                          "é exigida pelo roteiro (rótulo humano identificado)."},
            ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    for quem in ("A", "B"):
        destino = (a.dados / "anotacao") / f"planilha_{quem}.csv"
        existentes = {}
        if destino.exists():
            existentes = {l["id"]: l for l in ler_csv(destino)}
            preenchidos = sum(1 for l in existentes.values() if l["rotulo"].strip())
            novos = set(textos) - set(existentes)
            if not novos:
                print(f"{destino}: já existe ({preenchidos} rótulos preenchidos); nada a fazer")
                continue
            print(f"{destino}: acrescentando {len(novos)} textos novos "
                  f"(os {preenchidos} rótulos já preenchidos são preservados)")
        # ordem própria de cada anotador, reprodutível
        ordem = sorted(set(textos) - set(existentes))
        random.Random(f"{SEMENTE_MONTAGEM}-{quem}").shuffle(ordem)
        linhas = list(existentes.values()) + [
            {"id": i, "texto": textos[i]["texto"], "rotulo": "", "observacao": ""} for i in ordem]
        gravar_csv(destino, CAMPOS_PLANILHA, linhas, para_humanos=True)
        print(f"gravado: {destino}  ({len(linhas)} textos)")
    print(f"\nPreencha os nomes em {anotadores} e a coluna 'rotulo' de cada "
          f"planilha com: {' · '.join(ROTULOS)}.\nSiga etapa2/dados/guia_de_anotacao.md. "
          "NÃO consulte a planilha do colega nem a resposta de nenhuma API.")


def _ler_planilha(dados, quem, ids_esperados):
    caminho = dados / "anotacao" / f"planilha_{quem}.csv"
    if not caminho.exists():
        raise SystemExit(f"Falta {caminho}. Rode: anotacao.py planilhas")
    linhas = {l["id"]: l for l in ler_csv(caminho)}
    faltando = ids_esperados - set(linhas)
    if faltando:
        raise SystemExit(f"planilha_{quem}.csv não tem {len(faltando)} IDs: {sorted(faltando)[:5]}...")
    problemas = []
    for i in sorted(ids_esperados):
        r = linhas[i]["rotulo"].strip().lower()
        if r not in ROTULOS:
            problemas.append(f"{i}: {r!r}" if r else f"{i}: em branco")
    return {i: linhas[i]["rotulo"].strip().lower() for i in ids_esperados}, problemas


def cmd_consolidar(a):
    textos = candidatos(a.dados)
    nomes = json.loads(((a.dados / "anotacao") / "anotadores.json").read_text(encoding="utf-8"))
    if not nomes.get("A", "").strip() or not nomes.get("B", "").strip():
        raise SystemExit("Preencha os nomes dos dois anotadores em anotacao/anotadores.json.")
    if nomes["A"].strip().casefold() == nomes["B"].strip().casefold():
        raise SystemExit("Os anotadores A e B precisam ser pessoas diferentes.")

    ids = set(textos)
    rot_a, prob_a = _ler_planilha(a.dados, "A", ids)
    rot_b, prob_b = _ler_planilha(a.dados, "B", ids)
    if prob_a or prob_b:
        for quem, prob in (("A", prob_a), ("B", prob_b)):
            for p in prob[:10]:
                print(f"  planilha_{quem}: {p}")
            if len(prob) > 10:
                print(f"  planilha_{quem}: ... e mais {len(prob) - 10}")
        raise SystemExit(f"Rótulos ausentes ou inválidos. Aceitos: {', '.join(ROTULOS)}.")

    ordem = sorted(ids)
    concordancia = sum(rot_a[i] == rot_b[i] for i in ordem) / len(ordem)
    kappa = kappa_de_cohen([rot_a[i] for i in ordem], [rot_b[i] for i in ordem])

    # preserva decisões já preenchidas numa consolidação anterior
    caminho_div = (a.dados / "anotacao") / "divergencias.csv"
    decididas = {}
    if caminho_div.exists():
        decididas = {l["id"]: l for l in ler_csv(caminho_div)}
    divergencias = []
    for i in ordem:
        if rot_a[i] != rot_b[i]:
            antes = decididas.get(i, {})
            divergencias.append({"id": i, "texto": textos[i]["texto"],
                                 "rotulo_A": rot_a[i], "rotulo_B": rot_b[i],
                                 "rotulo_final": antes.get("rotulo_final", ""),
                                 "justificativa": antes.get("justificativa", "")})
    gravar_csv(caminho_div, CAMPOS_DIVERGENCIA, divergencias, para_humanos=True)

    anotacoes, pendentes = [], 0
    final_por_id = {d["id"]: d for d in divergencias}
    for i in ordem:
        if rot_a[i] == rot_b[i]:
            final, decisao, just = rot_a[i], "consenso", ""
        else:
            d = final_por_id[i]
            final = d["rotulo_final"].strip().lower()
            just = d["justificativa"].strip()
            if final in ROTULOS and just:
                decisao = "discussao"
            else:
                final, decisao = "", "pendente"
                pendentes += 1
        anotacoes.append({"id": i, "rotulo_A": rot_a[i], "rotulo_B": rot_b[i],
                          "rotulo_final": final, "decisao": decisao, "justificativa": just})
    gravar_csv(a.dados / "anotacoes.csv",
               ["id", "rotulo_A", "rotulo_B", "rotulo_final", "decisao", "justificativa"],
               anotacoes)

    resumo = {"anotador_A": nomes["A"].strip(), "anotador_B": nomes["B"].strip(),
              "textos": len(ordem), "concordancia_bruta": round(concordancia, 4),
              "kappa_de_cohen": None if kappa is None else round(kappa, 4),
              "divergencias": len(divergencias), "pendentes": pendentes,
              "rotulos_A": dict(Counter(rot_a.values())),
              "rotulos_B": dict(Counter(rot_b.values()))}
    ((a.dados / "anotacao") / "concordancia.json").write_text(
        json.dumps(resumo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"textos anotados pelos dois: {len(ordem)}")
    print(f"concordância bruta: {concordancia:.1%}   kappa de Cohen: "
          f"{'indefinido' if kappa is None else f'{kappa:.3f}'}")
    print(f"divergências: {len(divergencias)}   pendentes de decisão: {pendentes}")
    if pendentes:
        print(f"\nResolvam as divergências em {caminho_div}: preencham "
              "'rotulo_final' e 'justificativa', e rodem 'consolidar' de novo.")


def cmd_montar(a):
    textos = candidatos(a.dados)
    caminho = a.dados / "anotacoes.csv"
    if not caminho.exists():
        raise SystemExit("Falta anotacoes.csv. Rode: anotacao.py consolidar")
    anot = {l["id"]: l for l in ler_csv(caminho)}
    if set(anot) != set(textos):
        raise SystemExit("anotacoes.csv não cobre exatamente os candidatos. Rode 'consolidar' de novo.")
    pendentes = [i for i, l in anot.items() if l["decisao"] == "pendente"]
    if pendentes:
        raise SystemExit(f"{len(pendentes)} divergências sem decisão. Resolva antes de montar.")
    # textos retirados por decisão registrada (ex.: dado pessoal que o filtro não pegou)
    exclusoes = {}
    if (a.dados / "exclusoes.csv").exists():
        for l in ler_csv(a.dados / "exclusoes.csv"):
            if l["id"] not in textos:
                raise SystemExit(f"exclusoes.csv: id {l['id']!r} não é um candidato.")
            if not l.get("motivo", "").strip():
                raise SystemExit(f"exclusoes.csv: {l['id']} sem motivo.")
            exclusoes[l["id"]] = l["motivo"].strip()
    for nome in ("piloto.csv", "teste.csv", "exploratorio_misto.csv"):
        if (a.dados / nome).exists() and not a.refazer:
            raise SystemExit(f"{nome} já existe: o conjunto foi congelado. Use --refazer só "
                             "se NENHUMA coleta real tiver usado esta versão.")

    def linha(i, subconjunto):
        c, l = textos[i], anot[i]
        obs = f"A={l['rotulo_A']}, B={l['rotulo_B']}, decisao={l['decisao']}"
        if l["justificativa"]:
            obs += f": {l['justificativa']}"
        return {"id": i, "texto": c["texto"], "rotulo_referencia": l["rotulo_final"],
                "origem": f"B2W-Reviews01, linha {c['linha_origem']}",
                "subconjunto": subconjunto, "observacao_anotacao": obs,
                "caracteres": c["caracteres"], "bytes_utf8": c["bytes_utf8"]}

    piloto = [linha(i, "piloto") for i in sorted(textos)
              if i.startswith("p") and anot[i]["rotulo_final"] != "invalido" and i not in exclusoes]

    rng = random.Random(SEMENTE_MONTAGEM)
    teste, disponiveis = [], {}
    ids_teste = sorted(i for i in textos if i.startswith("t") and i not in exclusoes)
    for classe in CLASSES_PRINCIPAIS:
        grupo = [i for i in ids_teste if anot[i]["rotulo_final"] == classe]
        disponiveis[classe] = len(grupo)
        escolhidos = grupo if len(grupo) <= a.max_por_classe else rng.sample(grupo, a.max_por_classe)
        teste += [linha(i, "teste") for i in sorted(escolhidos)]
    teste.sort(key=lambda x: x["id"])
    misto = [linha(i, "exploratorio_misto") for i in ids_teste
             if anot[i]["rotulo_final"] == "misto"]

    for nome, linhas in (("piloto.csv", piloto), ("teste.csv", teste),
                         ("exploratorio_misto.csv", misto)):
        gravar_csv(a.dados / nome, CAMPOS_CONJUNTO, linhas)
        print(f"gravado: etapa2/dados/{nome}  ({len(linhas)} textos)")

    no_teste = Counter(l["rotulo_referencia"] for l in teste)
    manifesto = {
        "max_por_classe": a.max_por_classe, "semente": SEMENTE_MONTAGEM,
        "disponiveis_no_conjunto_de_candidatos": disponiveis,
        "no_teste": dict(no_teste),
        "invalidos_excluidos": sum(1 for l in anot.values() if l["rotulo_final"] == "invalido"),
        "excluidos_por_decisao": [{"id": i, "motivo": m} for i, m in sorted(exclusoes.items())],
        "concordancia": json.loads(((a.dados / "anotacao") / "concordancia.json").read_text(encoding="utf-8")),
        "arquivos": {n: sha256(a.dados / n)
                     for n in ("piloto.csv", "teste.csv", "exploratorio_misto.csv")},
    }
    (a.dados / "manifesto_conjuntos.json").write_text(
        json.dumps(manifesto, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for classe in CLASSES_PRINCIPAIS:
        if disponiveis[classe] < a.max_por_classe:
            print(f"ATENÇÃO: só {disponiveis[classe]} textos '{classe}' entre os candidatos "
                  f"(meta {a.max_por_classe}). Registre na metodologia ou sorteie um lote "
                  "extra ANTES de qualquer chamada real: amostrar.py --lote extra")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--dados", type=Path, default=DADOS)
    sub = p.add_subparsers(dest="comando", required=True)
    sub.add_parser("planilhas")
    sub.add_parser("consolidar")
    m = sub.add_parser("montar")
    m.add_argument("--max-por-classe", type=int, default=MAX_POR_CLASSE_PADRAO)
    m.add_argument("--refazer", action="store_true")
    a = p.parse_args(argv)
    {"planilhas": cmd_planilhas, "consolidar": cmd_consolidar, "montar": cmd_montar}[a.comando](a)


if __name__ == "__main__":
    sys.exit(main())
