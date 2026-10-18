# /// script
# requires-python = ">=3.11"
# dependencies = ["matplotlib==3.11.2"]
# ///
"""
Calcula as métricas de uma execução a partir dos arquivos brutos. Não chama API.

    uv run etapa2/src/analisar.py --execucao <id_execucao>
    uv run etapa2/src/analisar.py --execucao <id_execucao> --simulado   # verificação local

Tudo sai dos arquivos da execução (predicoes.jsonl, tentativas.jsonl) e do
dataset com o gabarito; nada é digitado à mão. Saídas:
    <execucao>/analise/metricas.json, tabela_principal.md/.csv, por_texto.csv,
    matriz_confusao_<provedor>.csv
    etapa2/graficos/<execucao>/*.png      (execuções simuladas: dentro da própria pasta)

Denominadores (etapa2/metodologia.md, seção de métricas):
- **Qualidade** (acurácia, F1, macro-F1): só textos de gabarito positivo/negativo/
  neutro que tiveram resposta utilizável em TODOS os provedores da execução — a
  interseção. Uma previsão `misto` é resposta utilizável e conta como erro.
- **Acertos sobre programados**: acertos / todos os textos programados; falha
  de serviço conta como não acerto.
- **Sucesso por tentativa** e **por texto**: separados.
- **Latência**: só tentativas bem-sucedidas; mediana e p95 pelo método do
  posto mais próximo (nearest-rank); timeouts à parte.
- **Custo**: estimado pela tabela; o observado no painel não é inferido aqui.
"""

import argparse
import csv
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import custo  # noqa: E402
import normalizar  # noqa: E402
from anotacao import kappa_de_cohen  # noqa: E402

RAIZ = AQUI.parents[1]
RESULTADOS = RAIZ / "etapa2" / "resultados"
SIMULACOES = RAIZ / "etapa2" / "simulacoes"
DEMONSTRACOES = RAIZ / "etapa2" / "demonstracoes"
GRAFICOS = RAIZ / "etapa2" / "graficos"
DADOS = RAIZ / "etapa2" / "dados"

CLASSES = ("positivo", "negativo", "neutro")
PREVISOES = CLASSES + ("misto",)


def _rel(caminho):
    """Caminho relativo à raiz do projeto, quando estiver dentro dela."""
    try:
        return Path(caminho).resolve().relative_to(RAIZ)
    except ValueError:
        return caminho


# --------------------------------------------------------------- métricas

def percentil_posto_mais_proximo(valores, p):
    """
    Percentil pelo posto mais próximo: o menor valor com pelo menos p% dos dados
    em ou abaixo dele. posto = ceil(p/100 × n). Não interpola — o p95 é sempre
    uma latência que de fato ocorreu.
    """
    if not valores:
        return None
    ordenados = sorted(valores)
    posto = max(1, math.ceil(p / 100 * len(ordenados)))
    return ordenados[posto - 1]


def mediana(valores):
    if not valores:
        return None
    s = sorted(valores)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def metricas_de_classificacao(referencia, previsto, classes=CLASSES):
    """
    Acurácia, precisão/revocação/F1 por classe e macro-F1.

    Denominador nulo (classe nunca prevista ou sem exemplos) vale 0,0 e é
    sinalizado em `indefinidos` — esconder isso inflaria ou reduziria o
    macro-F1 sem aviso. O macro-F1 é a média das classes de REFERÊNCIA;
    `misto` nunca é classe de referência, mas uma previsão `misto` conta como
    falso negativo da classe verdadeira.
    """
    if len(referencia) != len(previsto):
        raise ValueError("tamanhos diferentes")
    n = len(referencia)
    acertos = sum(r == p for r, p in zip(referencia, previsto))
    por_classe, indefinidos = {}, []
    for c in classes:
        tp = sum(r == c and p == c for r, p in zip(referencia, previsto))
        fp = sum(r != c and p == c for r, p in zip(referencia, previsto))
        fn = sum(r == c and p != c for r, p in zip(referencia, previsto))
        if tp + fp == 0:
            precisao = 0.0
            indefinidos.append(f"precisão de '{c}': classe nunca prevista")
        else:
            precisao = tp / (tp + fp)
        if tp + fn == 0:
            revocacao = 0.0
            indefinidos.append(f"revocação de '{c}': sem exemplos no gabarito")
        else:
            revocacao = tp / (tp + fn)
        f1 = 0.0 if precisao + revocacao == 0 else 2 * precisao * revocacao / (precisao + revocacao)
        por_classe[c] = {"suporte": tp + fn, "tp": tp, "fp": fp, "fn": fn,
                         "precisao": precisao, "revocacao": revocacao, "f1": f1}
    return {"n": n, "acertos": acertos, "acuracia": acertos / n if n else None,
            "macro_f1": sum(v["f1"] for v in por_classe.values()) / len(classes) if n else None,
            "por_classe": por_classe, "indefinidos": indefinidos}


def matriz_de_confusao(referencia, previsto, linhas=CLASSES, colunas=PREVISOES):
    """Linhas: gabarito (3 classes). Colunas: previsão (3 classes + misto)."""
    m = {r: {c: 0 for c in colunas} for r in linhas}
    for r, p in zip(referencia, previsto):
        if r not in m:
            continue
        if p not in colunas:
            raise ValueError(f"previsão fora da convenção comum: {p!r}")
        m[r][p] += 1
    return m


def mcnemar_exato(certo_a, certo_b):
    """
    Teste de McNemar exato (binomial, bilateral) para dois classificadores
    avaliados nos MESMOS textos. Só os discordantes informam: b = A acertou e B
    errou; c = o contrário. Sob a hipótese de mesma acurácia, b ~ Bin(b+c, 1/2).
    """
    b = sum(x and not y for x, y in zip(certo_a, certo_b))
    c = sum(y and not x for x, y in zip(certo_a, certo_b))
    n = b + c
    if n == 0:
        return {"b": 0, "c": 0, "p_valor": 1.0}
    k = min(b, c)
    cauda = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return {"b": b, "c": c, "p_valor": min(1.0, 2 * cauda)}


# ----------------------------------------------------------------- leitura

def ler_jsonl(caminho):
    return [json.loads(l) for l in Path(caminho).read_text(encoding="utf-8").splitlines() if l.strip()]


def carregar_execucao(pasta):
    predicoes = ler_jsonl(pasta / "predicoes.jsonl")
    tentativas = ler_jsonl(pasta / "tentativas.jsonl")
    config = json.loads((pasta / "config.json").read_text(encoding="utf-8"))
    ambiente = json.loads((pasta / "ambiente.json").read_text(encoding="utf-8"))
    vistos = Counter((p["id"], p["provedor"]) for p in predicoes)
    repetidos = [k for k, v in vistos.items() if v > 1]
    if repetidos:
        raise SystemExit(f"predicoes.jsonl tem (texto, provedor) repetidos: {repetidos[:5]}. "
                         "Isso não deveria acontecer; não é seguro analisar.")
    return predicoes, tentativas, config, ambiente


def carregar_gabarito(caminho, sha256_esperado):
    obtido = hashlib.sha256(Path(caminho).read_bytes()).hexdigest()
    if obtido != sha256_esperado:
        raise SystemExit(f"{caminho} não é o arquivo usado na execução (SHA-256 diferente).")
    with open(caminho, encoding="utf-8-sig", newline="") as f:
        linhas = list(csv.DictReader(f))
    if "rotulo_referencia" not in linhas[0]:
        raise SystemExit(f"{caminho} não tem coluna 'rotulo_referencia' — não há gabarito para medir qualidade.")
    return {l["id"]: l for l in linhas}


# ------------------------------------------------------------------ análise

def analisar(predicoes, tentativas, config, gabarito):
    provedores = sorted({p["provedor"] for p in predicoes})
    limiar = config["normalizacao"]["google"]["limiar"]

    # 1. recalcula a classe normalizada a partir da resposta original
    divergentes = []
    for p in predicoes:
        if p["status_final"] == "ok" and not p.get("simulado"):
            rec = normalizar.normalizar(p["provedor"], p.get("rotulo_original"), p.get("score"), limiar)
            if rec != p["rotulo_normalizado"]:
                divergentes.append((p["id"], p["provedor"], p["rotulo_normalizado"], rec))
    if divergentes:
        raise SystemExit(f"Classe gravada ≠ classe recalculada pela regra: {divergentes[:5]}")

    por = {(p["id"], p["provedor"]): p for p in predicoes}
    programados = sorted(i for i, g in gabarito.items() if g["rotulo_referencia"] in CLASSES)
    fora = Counter(g["rotulo_referencia"] for g in gabarito.values()
                   if g["rotulo_referencia"] not in CLASSES)
    intersecao = [i for i in programados
                  if all(por.get((i, prov), {}).get("status_final") == "ok" for prov in provedores)]

    resultado = {"provedores": provedores, "textos_no_dataset": len(gabarito),
                 "programados_3_classes": len(programados),
                 "fora_da_avaliacao_principal": dict(fora),
                 "intersecao": len(intersecao),
                 "excluidos_da_intersecao": len(programados) - len(intersecao),
                 "por_provedor": {}}

    ref_inter = [gabarito[i]["rotulo_referencia"] for i in intersecao]
    previsoes_inter = {}
    for prov in provedores:
        preds = [por.get((i, prov)) for i in programados]
        falhas = Counter(p["codigo_erro_final"] if p else "sem_registro"
                         for p in preds if not p or p["status_final"] != "ok")
        tent = [t for t in tentativas if t["provedor"] == prov]
        ok_t = [t for t in tent if t["status"] == "ok"]
        prev = [por[(i, prov)]["rotulo_normalizado"] for i in intersecao]
        previsoes_inter[prov] = prev
        qualidade = metricas_de_classificacao(ref_inter, prev)
        acertos_prog = sum(1 for i in programados
                           if por.get((i, prov), {}).get("status_final") == "ok"
                           and por[(i, prov)]["rotulo_normalizado"] == gabarito[i]["rotulo_referencia"])
        lat = [t["duracao_ms"] for t in ok_t]
        timeouts = [t["duracao_ms"] for t in tent if t.get("codigo") == "timeout"]
        unidades = sum(int(t.get("unidades_estimadas") or 0) for t in tent)
        simulado = prov == "simulado"
        franquia = 0 if simulado else custo.franquia_mensal(prov)
        preco = 0 if simulado else custo.preco_por_unidade(prov)
        resultado["por_provedor"][prov] = {
            "respostas_validas": sum(1 for p in preds if p and p["status_final"] == "ok"),
            "falhas_por_codigo": dict(falhas),
            "tentativas": len(tent),
            "sucesso_por_tentativa": len(ok_t) / len(tent) if tent else None,
            "sucesso_por_texto": (sum(1 for p in preds if p and p["status_final"] == "ok")
                                  / len(programados)) if programados else None,
            "qualidade_na_intersecao": qualidade,
            "previsoes_misto_na_intersecao": prev.count("misto"),
            "acertos_sobre_programados": acertos_prog,
            "fracao_acertos_sobre_programados": acertos_prog / len(programados) if programados else None,
            "latencia_ms": {"n": len(lat), "metodo_percentil": "posto mais próximo",
                            "mediana": mediana(lat), "p95": percentil_posto_mais_proximo(lat, 95),
                            "minimo": min(lat) if lat else None, "maximo": max(lat) if lat else None},
            "timeouts": {"n": len(timeouts), "duracoes_ms": timeouts},
            "matriz_confusao": matriz_de_confusao(ref_inter, prev),
            "custo": {"unidades_estimadas_todas_tentativas": unidades,
                      "estimado_sem_franquia_usd": round(unidades * preco, 4),
                      "estimado_com_franquia_usd": round(max(0, unidades - franquia) * preco, 4),
                      "franquia_mensal_unidades": franquia,
                      "observado_usd": None,
                      "nota": "Estimativa pela tabela de custos/premissas.csv. O valor "
                              "observado no painel do provedor é registrado à parte."},
        }

    if len(provedores) == 2 and intersecao:
        a, b = provedores
        ca = [p == r for p, r in zip(previsoes_inter[a], ref_inter)]
        cb = [p == r for p, r in zip(previsoes_inter[b], ref_inter)]
        resultado["comparacao_pareada"] = {
            "provedores": [a, b], "n": len(intersecao),
            "mcnemar_exato": mcnemar_exato(ca, cb),
            "kappa_entre_provedores": kappa_de_cohen(previsoes_inter[a], previsoes_inter[b]),
            "nota": "b = só o primeiro acertou; c = só o segundo acertou."}

    # análise exploratória: textos com gabarito fora das três classes (ex.: misto)
    explor = defaultdict(lambda: defaultdict(Counter))
    for i, g in gabarito.items():
        if g["rotulo_referencia"] not in CLASSES:
            for prov in provedores:
                p = por.get((i, prov))
                explor[g["rotulo_referencia"]][prov][
                    p["rotulo_normalizado"] if p and p["status_final"] == "ok" else "falha"] += 1
    resultado["exploratorio"] = {k: {p: dict(c) for p, c in v.items()} for k, v in explor.items()}
    resultado["_intersecao_ids"] = intersecao
    return resultado


# ------------------------------------------------------------------ saídas

def _pct(x):
    return "—" if x is None else f"{x:.1%}".replace(".", ",")


def _ms(x):
    return "—" if x is None else f"{x:,.0f}".replace(",", ".")


def gravar_tabelas(res, gabarito, predicoes, destino, execucao):
    destino.mkdir(parents=True, exist_ok=True)
    linhas = []
    for prov, m in res["por_provedor"].items():
        q = m["qualidade_na_intersecao"]
        linhas.append({
            "provedor": prov, "programados": res["programados_3_classes"],
            "respostas_validas": m["respostas_validas"], "intersecao": res["intersecao"],
            "acuracia": q["acuracia"], "macro_f1": q["macro_f1"],
            "acertos_sobre_programados": m["fracao_acertos_sobre_programados"],
            "previsoes_misto": m["previsoes_misto_na_intersecao"],
            "latencia_mediana_ms": m["latencia_ms"]["mediana"], "latencia_p95_ms": m["latencia_ms"]["p95"],
            "latencia_n": m["latencia_ms"]["n"],
            "sucesso_por_tentativa": m["sucesso_por_tentativa"],
            "sucesso_por_texto": m["sucesso_por_texto"],
            "unidades_estimadas": m["custo"]["unidades_estimadas_todas_tentativas"],
            "custo_estimado_com_franquia_usd": m["custo"]["estimado_com_franquia_usd"],
            "custo_estimado_sem_franquia_usd": m["custo"]["estimado_sem_franquia_usd"],
        })
    with open(destino / "tabela_principal.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0]))
        w.writeheader()
        w.writerows(linhas)

    md = [f"Execução `{execucao}` · interseção de {res['intersecao']} de "
          f"{res['programados_3_classes']} textos programados (3 classes)\n",
          "| Provedor | Respostas válidas | Acurácia | Macro-F1 | Acertos / programados | "
          "Previsões `misto` | Latência mediana (ms) | Latência p95 (ms) | Sucesso por tentativa | "
          "Custo estimado (USD, com franquia) |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for l in linhas:
        md.append(f"| {l['provedor']} | {l['respostas_validas']}/{l['programados']} | "
                  f"{_pct(l['acuracia'])} | {_pct(l['macro_f1'])} | {_pct(l['acertos_sobre_programados'])} | "
                  f"{l['previsoes_misto']} | {_ms(l['latencia_mediana_ms'])} | {_ms(l['latencia_p95_ms'])} "
                  f"(n={l['latencia_n']}) | {_pct(l['sucesso_por_tentativa'])} | "
                  f"{l['custo_estimado_com_franquia_usd']:.2f} |")
    if "comparacao_pareada" in res:
        c = res["comparacao_pareada"]
        k = c["kappa_entre_provedores"]
        md += ["", f"Comparação pareada ({c['n']} textos): McNemar exato b={c['mcnemar_exato']['b']}, "
                   f"c={c['mcnemar_exato']['c']}, p={c['mcnemar_exato']['p_valor']:.3f}; "
                   f"kappa entre provedores = {'indefinido' if k is None else f'{k:.3f}'}."]
    (destino / "tabela_principal.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    for prov, m in res["por_provedor"].items():
        with open(destino / f"matriz_confusao_{prov}.csv", "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["referencia \\ previsto", *PREVISOES])
            for r in CLASSES:
                w.writerow([r, *(m["matriz_confusao"][r][c] for c in PREVISOES)])

    # uma linha por texto: permite conferir à mão qualquer acerto ou erro
    por = {(p["id"], p["provedor"]): p for p in predicoes}
    provs = res["provedores"]
    with open(destino / "por_texto.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "rotulo_referencia", "na_intersecao",
                    *[f"{p}_{c}" for p in provs for c in ("status", "previsto", "acertou")], "texto"])
        inter = set(res["_intersecao_ids"])
        for i, g in sorted(gabarito.items()):
            cel = []
            for p in provs:
                pr = por.get((i, p), {})
                prev = pr.get("rotulo_normalizado")
                cel += [pr.get("status_final", "sem_registro"), prev or "",
                        "" if prev is None or g["rotulo_referencia"] not in CLASSES
                        else int(prev == g["rotulo_referencia"])]
            w.writerow([i, g["rotulo_referencia"], int(i in inter), *cel, g["texto"]])

    publico = {k: v for k, v in res.items() if not k.startswith("_")}
    (destino / "metricas.json").write_text(json.dumps(publico, ensure_ascii=False, indent=2) + "\n",
                                           encoding="utf-8")


# ----------------------------------------------------------------- gráficos
# Cores fixas por provedor, as mesmas dos gráficos da Etapa 1 (a cor acompanha
# a entidade). Par Azure/Google validado para daltonismo; o verde tem contraste
# baixo sobre o fundo, então todo valor também vem escrito como rótulo.

COR = {"azure": "#eb6834", "google": "#1baf7a", "simulado": "#8a8984"}
NOME = {"azure": "Microsoft Azure", "google": "Google Cloud", "simulado": "SIMULADO"}
SUPERFICIE, TINTA, TINTA_FRACA, GRADE = "#fcfcfb", "#0b0b0b", "#52514e", "#e5e4e0"


def _eixo(ax, titulo, subtitulo):
    ax.set_facecolor(SUPERFICIE)
    ax.set_title(titulo, fontsize=12, fontweight="bold", color=TINTA, pad=20, loc="left")
    ax.text(0, 1.02, subtitulo, transform=ax.transAxes, fontsize=8.5, color=TINTA_FRACA, va="bottom")
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.spines["bottom"].set_color(GRADE)
    ax.tick_params(colors=TINTA_FRACA, length=0, labelsize=9)


AVISO_DO_MODO = {"real": "",
                 "simulado": "SIMULADO — não é resultado de serviço real · ",
                 "demonstracao": "DEMONSTRAÇÃO — fora do experimento · "}


def gerar_graficos(res, tentativas, destino, execucao, modo="real"):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap

    destino.mkdir(parents=True, exist_ok=True)
    provs = res["provedores"]
    aviso = AVISO_DO_MODO[modo]
    rodape = f"{aviso}execução {execucao} · interseção de {res['intersecao']} textos"
    gerados = []

    # 1. qualidade — barras agrupadas, um eixo (0–100%), valores escritos
    metricas = [("acuracia", "Acurácia"), ("macro_f1", "Macro-F1"),
                ("fracao_acertos_sobre_programados", "Acertos / programados")]
    fig, ax = plt.subplots(figsize=(8.5, 4.6), facecolor=SUPERFICIE)
    largura = 0.8 / len(provs)
    for j, prov in enumerate(provs):
        m = res["por_provedor"][prov]
        vals = [m["qualidade_na_intersecao"]["acuracia"], m["qualidade_na_intersecao"]["macro_f1"],
                m["fracao_acertos_sobre_programados"]]
        vals = [0 if v is None else v * 100 for v in vals]
        xs = [i + (j - (len(provs) - 1) / 2) * largura for i in range(len(metricas))]
        barras = ax.bar(xs, vals, largura * 0.92, color=COR.get(prov, "#888"), label=NOME.get(prov, prov),
                        edgecolor=SUPERFICIE, linewidth=2)
        for b, v in zip(barras, vals):
            ax.text(b.get_x() + b.get_width() / 2, v + 1.5, f"{v:.1f}%".replace(".", ","),
                    ha="center", fontsize=9, color=TINTA)
    ax.set_xticks(range(len(metricas)), [n for _, n in metricas])
    ax.set_ylim(0, 110)
    ax.set_yticks(range(0, 101, 20), [f"{v}%" for v in range(0, 101, 20)])
    ax.grid(axis="y", color=GRADE, linewidth=0.8)
    ax.set_axisbelow(True)
    _eixo(ax, "Qualidade da classificação de sentimento", rodape)
    ax.legend(frameon=False, fontsize=9, labelcolor=TINTA_FRACA, ncols=len(provs),
              loc="upper left", bbox_to_anchor=(0, -0.08))
    fig.tight_layout()
    fig.savefig(destino / "qualidade.png", dpi=170, facecolor=SUPERFICIE)
    plt.close(fig)
    gerados.append("qualidade.png")

    # 2. matrizes de confusão — escala sequencial de um só matiz, contagens escritas
    rampa = LinearSegmentedColormap.from_list("seq", ["#f4f3ef", "#2f4b66"])
    # largura mínima: com um provedor só, o rodapé não cabia e era cortado
    fig, eixos = plt.subplots(1, len(provs), figsize=(max(7.5, 4.4 * len(provs)), 4.2), facecolor=SUPERFICIE,
                              squeeze=False)
    maximo = max(max(max(l.values()) for l in res["por_provedor"][p]["matriz_confusao"].values())
                 for p in provs) or 1
    for ax, prov in zip(eixos[0], provs):
        mc = res["por_provedor"][prov]["matriz_confusao"]
        dados = [[mc[r][c] for c in PREVISOES] for r in CLASSES]
        ax.imshow(dados, cmap=rampa, vmin=0, vmax=maximo)
        for i, linha in enumerate(dados):
            for k, v in enumerate(linha):
                ax.text(k, i, str(v), ha="center", va="center", fontsize=11,
                        color="white" if v > maximo * 0.55 else TINTA)
        ax.set_xticks(range(len(PREVISOES)), PREVISOES, fontsize=9, color=TINTA_FRACA)
        ax.set_yticks(range(len(CLASSES)), CLASSES, fontsize=9, color=TINTA_FRACA)
        ax.set_xlabel("previsto", fontsize=9, color=TINTA_FRACA)
        ax.set_ylabel("gabarito", fontsize=9, color=TINTA_FRACA)
        ax.set_title(NOME.get(prov, prov), fontsize=11, fontweight="bold", color=TINTA, loc="left")
        for lado in ax.spines.values():
            lado.set_visible(False)
        ax.tick_params(length=0)
    fig.tight_layout(rect=(0, 0.04, 1, 0.90))
    fig.suptitle("Matriz de confusão", x=0.02, y=0.97, ha="left", fontsize=12,
                 fontweight="bold", color=TINTA)
    fig.text(0.02, 0.01, rodape, fontsize=8, color=TINTA_FRACA)
    fig.savefig(destino / "matriz_confusao.png", dpi=170, facecolor=SUPERFICIE)
    plt.close(fig)
    gerados.append("matriz_confusao.png")

    # 3. latência — distribuição por provedor, mediana e p95 escritos
    fig, ax = plt.subplots(figsize=(8.5, 1.4 + 1.1 * len(provs)), facecolor=SUPERFICIE)
    for j, prov in enumerate(provs):
        lat = sorted(t["duracao_ms"] for t in tentativas if t["provedor"] == prov and t["status"] == "ok")
        if not lat:
            continue
        ys = [j + (((k * 7919) % 100) / 100 - 0.5) * 0.35 for k in range(len(lat))]  # dispersão determinística
        ax.scatter(lat, ys, s=12, color=COR.get(prov, "#888"), alpha=0.55, linewidths=0)
        med = mediana(lat)
        p95 = percentil_posto_mais_proximo(lat, 95)
        ax.plot([med, med], [j - 0.3, j + 0.3], color=TINTA, linewidth=2)
        ax.plot([p95, p95], [j - 0.3, j + 0.3], color=TINTA_FRACA, linewidth=1.5, linestyle=(0, (3, 2)))
        ax.text(med, j + 0.36, f"mediana {_ms(med)} ms", ha="center", fontsize=8.5, color=TINTA)
        ax.text(p95, j - 0.46, f"p95 {_ms(p95)} ms", ha="center", fontsize=8.5, color=TINTA_FRACA)
    ax.set_yticks(range(len(provs)), [NOME.get(p, p) for p in provs])
    ax.set_ylim(-0.7, len(provs) - 0.3)
    ax.set_xlabel("latência por tentativa bem-sucedida (ms)", fontsize=9, color=TINTA_FRACA)
    ax.grid(axis="x", color=GRADE, linewidth=0.8)
    ax.set_axisbelow(True)
    _eixo(ax, "Latência das chamadas", rodape)
    fig.tight_layout()
    fig.savefig(destino / "latencia.png", dpi=170, facecolor=SUPERFICIE)
    plt.close(fig)
    gerados.append("latencia.png")
    return gerados


# --------------------------------------------------------------------- main

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--execucao", required=True)
    p.add_argument("--dados", type=Path, help="dataset com gabarito (padrão: o usado na execução)")
    modo = p.add_mutually_exclusive_group()
    modo.add_argument("--simulado", action="store_true")
    modo.add_argument("--demonstracao", action="store_true")
    p.add_argument("--sem-graficos", action="store_true")
    a = p.parse_args(argv)

    modo = "simulado" if a.simulado else "demonstracao" if a.demonstracao else "real"
    base = {"simulado": SIMULACOES, "demonstracao": DEMONSTRACOES, "real": RESULTADOS}[modo]
    pasta = base / a.execucao
    if not pasta.exists():
        raise SystemExit(f"Execução não encontrada: {pasta}")
    predicoes, tentativas, config, ambiente = carregar_execucao(pasta)
    if bool(config.get("simulado")) != a.simulado or bool(config.get("demonstracao")) != a.demonstracao:
        raise SystemExit("O tipo da execução (real, simulada ou demonstração) não confere com a opção usada.")
    dados = a.dados or DADOS / ambiente["dataset"]["arquivo"]
    gabarito = carregar_gabarito(dados, ambiente["dataset"]["sha256"])

    res = analisar(predicoes, tentativas, config, gabarito)
    destino = pasta / "analise"
    gravar_tabelas(res, gabarito, predicoes, destino, a.execucao)
    print((destino / "tabela_principal.md").read_text(encoding="utf-8"))
    if not a.sem_graficos:
        # só a coleta do experimento vai para etapa2/graficos/; o resto fica na própria pasta
        dest_graf = GRAFICOS / a.execucao if modo == "real" else pasta / "graficos"
        for g in gerar_graficos(res, tentativas, dest_graf, a.execucao, modo):
            print(f"gráfico: {_rel(dest_graf / g)}")
    print(f"tabelas e métricas: {_rel(destino)}")


if __name__ == "__main__":
    sys.exit(main())
