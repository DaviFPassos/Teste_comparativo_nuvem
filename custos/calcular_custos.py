"""
Calcula os cenários de custo da Etapa 1 a partir de custos/premissas.csv.

Nenhum preço está embutido neste arquivo: todos vêm do CSV de premissas, que
registra fonte oficial, região, moeda e data de consulta de cada valor. O
resultado é gravado em custos/resultados.csv.

Usa apenas a biblioteca padrão do Python, para que qualquer pessoa consiga
reproduzir os números sem instalar dependências:

    python3 custos/calcular_custos.py

Região de referência: US East (us-east-1 / eastus / us-central1). Moeda: USD.
As APIs do Google comparadas em NLP e visão têm preço global, não regional.
"""

import csv
import math
from pathlib import Path

AQUI = Path(__file__).parent
PREMISSAS = AQUI / "premissas.csv"
FRANQUIAS = AQUI / "franquias.csv"
RESULTADOS = AQUI / "resultados.csv"

# ---------------------------------------------------------------------------
# Cenários. Quantidades são HIPOTÉTICAS e iguais entre provedores, como exige
# a seção 4 do enunciado ("cargas equivalentes").
# ---------------------------------------------------------------------------
DOCUMENTOS_NLP = 100_000
COMPRIMENTOS_NLP = (100, 500, 1_200, 4_000)  # caracteres por documento
IMAGENS_VISAO = 100_000
MINUTOS_FALA = 10_000


def carregar_premissas():
    """Agrupa as faixas de preço por (categoria, provedor, operação)."""
    faixas = {}
    with open(PREMISSAS, encoding="utf-8") as f:
        for linha in csv.DictReader(f):
            chave = (linha["categoria"], linha["provedor"], linha["operacao"])
            faixas.setdefault(chave, []).append({
                "min": float(linha["faixa_min"]),
                "max": float(linha["faixa_max"]) if linha["faixa_max"] else math.inf,
                "preco": float(linha["preco_usd"]),
                "unidade_preco": linha["unidade_preco"],
                "servico": linha["servico"],
                "unidade_cobranca": linha["unidade_cobranca"],
            })
    for lista in faixas.values():
        lista.sort(key=lambda x: x["min"])
    return faixas


def carregar_franquias():
    with open(FRANQUIAS, encoding="utf-8") as f:
        return {(l["categoria"], l["provedor"]): l for l in csv.DictReader(f)}


def custo_por_faixas(quantidade, faixas, por_mil=False):
    """
    Aplica preço progressivo por faixa de volume.

    `quantidade` está na unidade de cobrança do provedor (unidades, registros,
    transações, imagens, minutos ou segundos). Quando `por_mil` é True, o preço
    da faixa vale por 1.000 unidades.

    As faixas são cumulativas: cada parcela do volume é cobrada ao preço da
    faixa em que cai — e não o volume todo ao preço da faixa final.
    """
    restante = quantidade
    total = 0.0
    for faixa in faixas:
        if restante <= 0:
            break
        largura = faixa["max"] - faixa["min"]
        nesta = min(restante, largura)
        total += (nesta / 1000 * faixa["preco"]) if por_mil else (nesta * faixa["preco"])
        restante -= nesta
    return total


# ---------------------------------------------------------------------------
# Regras de contagem de unidades, uma por provedor.
# Cada função converte a carga do cenário na unidade cobrada pelo provedor.
# ---------------------------------------------------------------------------

def unidades_comprehend(caracteres):
    """AWS: unidade de 100 caracteres, com mínimo de 3 unidades por requisição."""
    return max(3, math.ceil(caracteres / 100))


def registros_azure_language(caracteres):
    """Azure: registro de texto de 1.000 caracteres, arredondado para cima."""
    return math.ceil(caracteres / 1000)


def unidades_google_nl(caracteres):
    """
    Google: unidade de 1.000 caracteres Unicode, arredondada para cima, com o
    mínimo de 1 unidade por requisição. Confirmado pelo exemplo oficial da
    página de preços: 800, 1.500 e 600 caracteres = 1 + 2 + 1 = 4 unidades.
    """
    return max(1, math.ceil(caracteres / 1000))


def calcular():
    faixas = carregar_premissas()
    franquias = carregar_franquias()
    linhas = []

    def registrar(categoria, cenario, carga, provedor, operacao, unidades,
                  nome_unidade, custo_sem, custo_com, obs=""):
        ref = faixas[(categoria, provedor, operacao)][0]
        linhas.append({
            "categoria": categoria,
            "cenario": cenario,
            "carga": carga,
            "provedor": provedor,
            "servico": ref["servico"],
            "operacao": operacao,
            "unidades_cobradas": unidades,
            "unidade_cobranca": nome_unidade,
            "custo_usd_sem_franquia": round(custo_sem, 4),
            "custo_usd_com_franquia": round(custo_com, 4),
            "tipo_franquia": franquias.get((categoria, provedor), {}).get("tipo", ""),
            "observacao": obs,
        })

    # ----------------------------- NLP -------------------------------------
    for chars in COMPRIMENTOS_NLP:
        cenario = f"{DOCUMENTOS_NLP} documentos de {chars} caracteres"
        carga = f"{DOCUMENTOS_NLP} docs x {chars} chars"

        # AWS — unidades de 100 caracteres, mínimo de 3 por requisição
        un = unidades_comprehend(chars) * DOCUMENTOS_NLP
        fx = faixas[("nlp", "aws", "DetectSentiment")]
        franquia = float(franquias[("nlp", "aws")]["franquia"])
        registrar("nlp", cenario, carga, "aws", "DetectSentiment", un,
                  "unidades de 100 caracteres",
                  custo_por_faixas(un, fx),
                  custo_por_faixas(max(0, un - franquia), fx),
                  f"{unidades_comprehend(chars)} unidades por documento "
                  f"(minimo de 3 aplicado)" if chars <= 300 else
                  f"{unidades_comprehend(chars)} unidades por documento")

        # Azure — registros de 1.000 caracteres
        reg = registros_azure_language(chars) * DOCUMENTOS_NLP
        fx = faixas[("nlp", "azure", "Sentiment analysis")]
        franquia = float(franquias[("nlp", "azure")]["franquia"])
        registrar("nlp", cenario, carga, "azure", "Sentiment analysis", reg,
                  "registros de texto de 1000 caracteres",
                  custo_por_faixas(reg, fx, por_mil=True),
                  custo_por_faixas(max(0, reg - franquia), fx, por_mil=True),
                  f"{registros_azure_language(chars)} registros por documento")

        # Google — unidades de 1.000 caracteres; a franquia já é a 1a faixa
        un = unidades_google_nl(chars) * DOCUMENTOS_NLP
        fx = faixas[("nlp", "google", "analyzeSentiment")]
        sem_franquia = [f for f in fx if f["preco"] > 0]
        # sem franquia: desloca as faixas pagas para começar em zero
        deslocado = [{**f, "min": 0 if f is sem_franquia[0] else f["min"]} for f in sem_franquia]
        registrar("nlp", cenario, carga, "google", "analyzeSentiment", un,
                  "unidades de 1000 caracteres",
                  custo_por_faixas(un, deslocado, por_mil=True),
                  custo_por_faixas(un, fx, por_mil=True),
                  f"{unidades_google_nl(chars)} unidades por documento; "
                  "franquia e a primeira faixa da tabela")

    # ---------------------------- VISÃO ------------------------------------
    cenario = f"{IMAGENS_VISAO} imagens com deteccao de rotulos"
    carga = f"{IMAGENS_VISAO} imagens x 1 feature"

    fx = faixas[("visao", "aws", "DetectLabels (Group 2)")]
    franquia = float(franquias[("visao", "aws")]["franquia"])
    registrar("visao", cenario, carga, "aws", "DetectLabels (Group 2)", IMAGENS_VISAO,
              "imagens processadas",
              custo_por_faixas(IMAGENS_VISAO, fx),
              custo_por_faixas(max(0, IMAGENS_VISAO - franquia), fx))

    fx = faixas[("visao", "azure", "Image Analysis Tag (Group 1)")]
    franquia = float(franquias[("visao", "azure")]["franquia"])
    registrar("visao", cenario, carga, "azure", "Image Analysis Tag (Group 1)",
              IMAGENS_VISAO, "transacoes",
              custo_por_faixas(IMAGENS_VISAO, fx, por_mil=True),
              custo_por_faixas(max(0, IMAGENS_VISAO - franquia), fx, por_mil=True))

    fx = faixas[("visao", "google", "LABEL_DETECTION")]
    sem = [f for f in fx if f["preco"] > 0]
    deslocado = [{**f, "min": 0 if f is sem[0] else f["min"]} for f in sem]
    registrar("visao", cenario, carga, "google", "LABEL_DETECTION", IMAGENS_VISAO,
              "unidades",
              custo_por_faixas(IMAGENS_VISAO, deslocado, por_mil=True),
              custo_por_faixas(IMAGENS_VISAO, fx, por_mil=True),
              "franquia e a primeira faixa da tabela")

    # ----------------------------- FALA ------------------------------------
    cenario = f"{MINUTOS_FALA} minutos de audio em lote"
    carga = f"{MINUTOS_FALA} minutos"

    # AWS cobra por segundo
    segundos = MINUTOS_FALA * 60
    fx = faixas[("fala", "aws", "StartTranscriptionJob (lote)")]
    franquia_seg = float(franquias[("fala", "aws")]["franquia"]) * 60
    registrar("fala", cenario, carga, "aws", "StartTranscriptionJob (lote)", segundos,
              "segundos de audio",
              custo_por_faixas(segundos, fx),
              custo_por_faixas(max(0, segundos - franquia_seg), fx),
              "preco unico por segundo, sem faixas e sem minimo")

    # Azure cobra por hora
    horas = MINUTOS_FALA / 60
    fx = faixas[("fala", "azure", "Speech to text Batch (S1)")]
    franquia_h = float(franquias[("fala", "azure")]["franquia"])
    registrar("fala", cenario, carga, "azure", "Speech to text Batch (S1)",
              round(horas, 4), "horas de audio",
              custo_por_faixas(horas, fx),
              custo_por_faixas(max(0, horas - franquia_h), fx),
              "modo best-effort: documentacao admite ate 24h em horario de pico")

    # Google: dois modos de lote com preços diferentes
    for operacao, obs in (
        ("BatchRecognize (Standard)", "prioridade padrao"),
        ("BatchRecognize com dynamic batch", "modo de menor urgencia, comparavel ao lote da Azure"),
    ):
        fx = faixas[("fala", "google", operacao)]
        registrar("fala", cenario, carga, "google", operacao, MINUTOS_FALA,
                  "minutos de audio",
                  custo_por_faixas(MINUTOS_FALA, fx),
                  custo_por_faixas(MINUTOS_FALA, fx),
                  f"{obs}; franquia nao localizada na tabela V2")

    return linhas


def main():
    linhas = calcular()
    campos = ["categoria", "cenario", "carga", "provedor", "servico", "operacao",
              "unidades_cobradas", "unidade_cobranca", "custo_usd_sem_franquia",
              "custo_usd_com_franquia", "tipo_franquia", "observacao"]

    with open(RESULTADOS, "w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(linhas)

    print(f"{len(linhas)} linhas gravadas em {RESULTADOS.relative_to(AQUI.parent)}\n")
    atual = None
    for l in linhas:
        if l["cenario"] != atual:
            atual = l["cenario"]
            print(f"\n{atual}")
            print(f"  {'provedor':8s} {'unidades':>14s} {'sem franquia':>14s} {'com franquia':>14s}")
        print(f"  {l['provedor']:8s} {l['unidades_cobradas']:>14,.0f} "
              f"{l['custo_usd_sem_franquia']:>13,.2f}$ {l['custo_usd_com_franquia']:>13,.2f}$")


if __name__ == "__main__":
    main()
