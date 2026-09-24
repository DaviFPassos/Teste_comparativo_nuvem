# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib"]
# ///
"""
Gera os gráficos de custo da Etapa 1 a partir de custos/resultados.csv.

Os gráficos são produzidos POR CÓDIGO, a partir do arquivo de resultados — não
há número digitado à mão em nenhuma figura. Rode o cálculo antes:

    uv run custos/calcular_custos.py     (gera resultados.csv, só stdlib)
    uv run custos/gerar_graficos.py      (gera custos/graficos/*.png)

Cor segue o provedor, em ordem fixa, nunca o ranking: a mesma cor identifica o
mesmo provedor em todas as figuras. Os dois modos de lote do Google dividem a
mesma cor e são separados por textura, porque são o mesmo provedor.

Todas as barras recebem rótulo direto com o valor, o que também atende à regra
de contraste da paleta em fundo claro.
"""

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

AQUI = Path(__file__).parent
RESULTADOS = AQUI / "resultados.csv"
SAIDA = AQUI / "graficos"

# Paleta categórica validada (checagens de banda de luminosidade, croma,
# separação para daltonismo e piso de visão normal — todas PASS).
COR = {"aws": "#2a78d6", "azure": "#eb6834", "google": "#1baf7a"}
NOME = {"aws": "AWS", "azure": "Microsoft Azure", "google": "Google Cloud"}

SUPERFICIE = "#fcfcfb"
TINTA = "#0b0b0b"
TINTA_FRACA = "#52514e"


def carregar():
    with open(RESULTADOS, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def estilizar(ax, titulo, subtitulo, rotulo_y):
    """Eixos recessivos, título informativo, sem moldura desnecessária."""
    ax.set_title(titulo, fontsize=13, fontweight="bold", color=TINTA, pad=18, loc="left")
    ax.text(0, 1.02, subtitulo, transform=ax.transAxes, fontsize=9,
            color=TINTA_FRACA, va="bottom")
    ax.set_ylabel(rotulo_y, fontsize=10, color=TINTA_FRACA)
    ax.grid(axis="y", color="#e5e4e0", linewidth=0.8)
    ax.set_axisbelow(True)
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.spines["bottom"].set_color("#d6d5d0")
    ax.tick_params(colors=TINTA_FRACA, length=0, labelsize=9)


def formatar(valor):
    """Sem centavos quando o valor é inteiro — rótulos curtos não colidem."""
    return f"${valor:,.0f}" if float(valor).is_integer() else f"${valor:,.2f}"


def rotular(ax, barras, fonte=8.5):
    for b in barras:
        ax.annotate(formatar(b.get_height()),
                    (b.get_x() + b.get_width() / 2, b.get_height()),
                    textcoords="offset points", xytext=(0, 4),
                    ha="center", fontsize=fonte, color=TINTA)


def salvar(fig, nome):
    SAIDA.mkdir(exist_ok=True)
    caminho = SAIDA / nome
    fig.savefig(caminho, dpi=160, bbox_inches="tight", facecolor=SUPERFICIE)
    plt.close(fig)
    print(f"gerado: {caminho.relative_to(AQUI.parent)}")


def grafico_nlp(linhas):
    """Barras agrupadas: custo por comprimento de documento, nos três provedores."""
    dados = [l for l in linhas if l["categoria"] == "nlp"]
    comprimentos = []
    for l in dados:
        c = int(l["carga"].split("x")[1].replace("chars", "").strip())
        if c not in comprimentos:
            comprimentos.append(c)

    fig, ax = plt.subplots(figsize=(10.5, 5.2), facecolor=SUPERFICIE)
    ax.set_facecolor(SUPERFICIE)
    largura = 0.24

    for i, prov in enumerate(("aws", "azure", "google")):
        valores = []
        for c in comprimentos:
            v = next(float(l["custo_usd_sem_franquia"]) for l in dados
                     if l["provedor"] == prov and f"x {c} chars" in l["carga"])
            valores.append(v)
        posicoes = [x + (i - 1) * (largura + 0.035) for x in range(len(comprimentos))]
        barras = ax.bar(posicoes, valores, largura, label=NOME[prov],
                        color=COR[prov], edgecolor=SUPERFICIE, linewidth=1.2)
        rotular(ax, barras)

    ax.set_xticks(range(len(comprimentos)))
    ax.set_xticklabels([f"{c:,} caracteres".replace(",", ".") for c in comprimentos])
    estilizar(ax,
              "Análise de sentimento: custo de 100.000 documentos",
              "Por comprimento do documento · US East · USD · sem franquia · preços de 23/09/2026",
              "Custo mensal (USD)")
    ax.legend(frameon=False, fontsize=9, labelcolor=TINTA_FRACA, ncols=3,
              loc="upper left", bbox_to_anchor=(0, -0.09))
    salvar(fig, "custos_nlp.png")


def grafico_visao(linhas):
    dados = [l for l in linhas if l["categoria"] == "visao"]
    fig, ax = plt.subplots(figsize=(7, 4.6), facecolor=SUPERFICIE)
    ax.set_facecolor(SUPERFICIE)

    provedores = [l["provedor"] for l in dados]
    valores = [float(l["custo_usd_sem_franquia"]) for l in dados]
    barras = ax.bar([NOME[p] for p in provedores], valores, 0.5,
                    color=[COR[p] for p in provedores],
                    edgecolor=SUPERFICIE, linewidth=1.2)
    rotular(ax, barras)
    estilizar(ax,
              "Detecção de rótulos: custo de 100.000 imagens",
              "Uma feature por imagem · US East · USD · sem franquia · preços de 23/09/2026",
              "Custo mensal (USD)")
    salvar(fig, "custos_visao.png")


def grafico_fala(linhas):
    """Os dois modos do Google compartilham a cor do provedor e se separam por textura."""
    dados = [l for l in linhas if l["categoria"] == "fala"]
    fig, ax = plt.subplots(figsize=(8.2, 4.8), facecolor=SUPERFICIE)
    ax.set_facecolor(SUPERFICIE)

    rotulos, valores, cores, texturas = [], [], [], []
    for l in dados:
        prov = l["provedor"]
        modo = ""
        if prov == "google":
            modo = "\n(dynamic batch)" if "dynamic" in l["operacao"] else "\n(padrão)"
        rotulos.append(NOME[prov] + modo)
        valores.append(float(l["custo_usd_sem_franquia"]))
        cores.append(COR[prov])
        texturas.append("//" if "dynamic" in l["operacao"] else "")

    barras = ax.bar(rotulos, valores, 0.5, color=cores,
                    edgecolor=SUPERFICIE, linewidth=1.2, hatch=texturas)
    rotular(ax, barras)
    estilizar(ax,
              "Transcrição em lote: custo de 10.000 minutos de áudio",
              "pt-BR · US East · USD · sem franquia · preços de 23/09/2026",
              "Custo mensal (USD)")
    salvar(fig, "custos_fala.png")


def main():
    linhas = carregar()
    grafico_nlp(linhas)
    grafico_visao(linhas)
    grafico_fala(linhas)


if __name__ == "__main__":
    main()
