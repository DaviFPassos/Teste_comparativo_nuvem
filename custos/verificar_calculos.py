# /// script
# requires-python = ">=3.10"
# ///
"""
Conferência manual dos cálculos de custo — exigência da Fase 4 do roteiro:
"conferir manualmente pelo menos um caso por regra de cobrança e os pontos em
que muda o arredondamento ou a faixa".

Cada caso abaixo traz a conta feita à mão, em comentário, e a compara com o que
o programa produziu. Rode com:

    uv run custos/verificar_calculos.py

Sai com código 1 se qualquer conferência falhar.
"""

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from calcular_custos import (  # noqa: E402
    carregar_premissas, custo_por_faixas, unidades_comprehend,
    registros_azure_language, unidades_google_nl,
)

AQUI = Path(__file__).parent
falhas = []


def conferir(descricao, obtido, esperado, conta):
    ok = abs(float(obtido) - float(esperado)) < 1e-6
    print(f"[{'OK ' if ok else 'ERRO'}] {descricao}")
    print(f"        conta manual: {conta}")
    print(f"        esperado {esperado} | obtido {obtido}\n")
    if not ok:
        falhas.append(descricao)


print("=" * 78)
print("1. REGRAS DE CONTAGEM DE UNIDADES")
print("=" * 78)

# AWS: unidade de 100 caracteres COM MÍNIMO de 3 unidades por requisição.
conferir("AWS · 100 caracteres aciona o mínimo de 3 unidades",
         unidades_comprehend(100), 3,
         "ceil(100/100) = 1, mas o mínimo de 3 unidades por requisição prevalece")
conferir("AWS · 250 caracteres ainda está sob o mínimo",
         unidades_comprehend(250), 3,
         "ceil(250/100) = 3; coincide com o mínimo")
conferir("AWS · 301 caracteres passa do mínimo (ponto de virada)",
         unidades_comprehend(301), 4,
         "ceil(301/100) = 4 > 3, o mínimo deixa de valer")

# Azure: registro de 1.000 caracteres, arredondado para cima.
conferir("Azure · 1.000 caracteres = 1 registro (limite exato da faixa)",
         registros_azure_language(1000), 1, "ceil(1000/1000) = 1")
conferir("Azure · 1.001 caracteres = 2 registros (ponto de virada)",
         registros_azure_language(1001), 2, "ceil(1001/1000) = 2")

# Google: unidade de 1.000 caracteres, mínimo de 1 por requisição.
# Exemplo oficial da página de preços: 800, 1.500 e 600 caracteres = 4 unidades.
total_exemplo_oficial = (unidades_google_nl(800) + unidades_google_nl(1500)
                         + unidades_google_nl(600))
conferir("Google · reproduz o exemplo oficial (800 + 1.500 + 600 caracteres)",
         total_exemplo_oficial, 4,
         "1 unidade (800) + 2 unidades (1.500) + 1 unidade (600) = 4 unidades")

print("=" * 78)
print("2. PREÇO PROGRESSIVO ATRAVESSANDO FAIXAS")
print("=" * 78)

faixas = carregar_premissas()

# AWS Comprehend com 15.000.000 de unidades atravessa a faixa de 10M.
fx = faixas[("nlp", "aws", "DetectSentiment")]
conferir("AWS · 15.000.000 unidades atravessam a faixa de 10M",
         custo_por_faixas(15_000_000, fx), 1250.0,
         "10.000.000 x $0,0001 = $1.000 ; 5.000.000 x $0,00005 = $250 ; total $1.250")

# Azure com 3.000.000 de registros atravessa duas faixas.
fx = faixas[("nlp", "azure", "Sentiment analysis")]
conferir("Azure · 3.000.000 registros atravessam duas faixas",
         custo_por_faixas(3_000_000, fx, por_mil=True), 2150.0,
         "500 mil x $1,00/mil = $500 ; 2 milhões x $0,75/mil = $1.500 ; "
         "500 mil x $0,30/mil = $150 ; total $2.150")

# Rekognition com 2.000.000 de imagens atravessa a faixa de 1M.
fx = faixas[("visao", "aws", "DetectLabels (Group 2)")]
conferir("AWS · 2.000.000 imagens atravessam a faixa de 1M",
         custo_por_faixas(2_000_000, fx), 1800.0,
         "1.000.000 x $0,0010 = $1.000 ; 1.000.000 x $0,0008 = $800 ; total $1.800")

print("=" * 78)
print("3. RESULTADOS PUBLICADOS EM resultados.csv")
print("=" * 78)

with open(AQUI / "resultados.csv", encoding="utf-8") as f:
    linhas = list(csv.DictReader(f))


def buscar(categoria, provedor, contem_carga=None, contem_operacao=None):
    for l in linhas:
        if l["categoria"] != categoria or l["provedor"] != provedor:
            continue
        if contem_carga and contem_carga not in l["carga"]:
            continue
        if contem_operacao and contem_operacao not in l["operacao"]:
            continue
        return l
    raise LookupError(f"{categoria}/{provedor}/{contem_carga}")


conferir("NLP · AWS · 100.000 docs de 100 caracteres",
         buscar("nlp", "aws", "x 100 chars")["custo_usd_sem_franquia"], 30.0,
         "3 unidades/doc x 100.000 docs = 300.000 unidades x $0,0001 = $30,00")

conferir("NLP · Azure · 100.000 docs de 1.200 caracteres",
         buscar("nlp", "azure", "x 1200 chars")["custo_usd_sem_franquia"], 200.0,
         "2 registros/doc x 100.000 = 200.000 registros = 200 x $1,00/mil = $200,00")

conferir("NLP · Google · 100.000 docs de 100 caracteres, com franquia",
         buscar("nlp", "google", "x 100 chars")["custo_usd_com_franquia"], 95.0,
         "100.000 unidades - 5.000 gratuitas = 95.000 = 95 x $1,00/mil = $95,00")

conferir("Visão · Google · 100.000 imagens, com franquia",
         buscar("visao", "google")["custo_usd_com_franquia"], 148.5,
         "100.000 - 1.000 gratuitas = 99.000 unidades = 99 x $1,50/mil = $148,50")

conferir("Visão · AWS · 100.000 imagens",
         buscar("visao", "aws")["custo_usd_sem_franquia"], 100.0,
         "100.000 imagens x $0,0010 = $100,00 (tudo na primeira faixa)")

conferir("Fala · AWS · 10.000 minutos",
         buscar("fala", "aws")["custo_usd_sem_franquia"], 60.0,
         "10.000 min x 60 = 600.000 s x $0,0001/s = $60,00 (equivale a $0,006/min)")

conferir("Fala · Azure · 10.000 minutos",
         buscar("fala", "azure")["custo_usd_sem_franquia"], 30.0,
         "10.000 / 60 = 166,667 h x $0,18/h = $30,00 (equivale a $0,003/min)")

conferir("Fala · Google padrão · 10.000 minutos",
         buscar("fala", "google", contem_operacao="Standard")["custo_usd_sem_franquia"], 160.0,
         "10.000 min x $0,016/min = $160,00")

conferir("Fala · Google dynamic batch · 10.000 minutos",
         buscar("fala", "google", contem_operacao="dynamic")["custo_usd_sem_franquia"], 30.0,
         "10.000 min x $0,003/min = $30,00")

print("=" * 78)
print("4. O EMPATE DE 4.000 CARACTERES É PONTUAL, NÃO UM PATAMAR")
print("=" * 78)

# Em 4.000 caracteres os três empatam; em 4.100 a AWS volta a ser mais barata,
# porque Azure e Google arredondam para o milhar seguinte.
for prov, esperado in (("aws", 400.0), ("azure", 400.0), ("google", 400.0)):
    conferir(f"NLP · {prov} · 100.000 docs de 4.000 caracteres (empate)",
             buscar("nlp", prov, "x 4000 chars")["custo_usd_sem_franquia"], esperado,
             "4.000 é múltiplo exato de 100 e de 1.000: 40 unidades (AWS) e "
             "4 registros/unidades (Azure e Google) por documento = $400,00 nos três")

conferir("NLP · AWS · 100.000 docs de 4.100 caracteres (empate desfeito)",
         buscar("nlp", "aws", "x 4100 chars")["custo_usd_sem_franquia"], 410.0,
         "ceil(4100/100) = 41 unidades x 100.000 = 4.100.000 x $0,0001 = $410,00")
conferir("NLP · Azure · 100.000 docs de 4.100 caracteres (arredonda o milhar)",
         buscar("nlp", "azure", "x 4100 chars")["custo_usd_sem_franquia"], 500.0,
         "ceil(4100/1000) = 5 registros x 100.000 = 500.000 = 500 x $1,00/mil = $500,00")
conferir("NLP · Google · 100.000 docs de 4.100 caracteres (arredonda o milhar)",
         buscar("nlp", "google", "x 4100 chars")["custo_usd_sem_franquia"], 500.0,
         "ceil(4100/1000) = 5 unidades x 100.000 = 500.000 = 500 x $1,00/mil = $500,00")

print("=" * 78)
print("5. REGRA DE APLICAÇÃO DAS FRANQUIAS")
print("=" * 78)

# O tier F0 da Azure é um recurso separado, não um desconto no tier pago: não
# pode ser abatido do cenário. Na transcrição em lote, o F0 nem oferece a
# operação ("Not available for F0" na tabela oficial de cotas).
for categoria, carga, valor in (("nlp", "x 100 chars", 100.0),
                                ("visao", None, 100.0),
                                ("fala", None, 30.0)):
    linha = buscar(categoria, "azure", carga)
    conferir(f"{categoria} · Azure · franquia F0 NÃO é descontada",
             linha["custo_usd_com_franquia"], valor,
             "F0 é tier/recurso separado; em fala o lote nem está disponível no F0, "
             "logo custo com franquia = custo sem franquia")
    conferir(f"{categoria} · Azure · CSV registra franquia_aplicada = nao",
             linha["franquia_aplicada"] == "nao", True,
             "a coluna franquia_aplicada documenta a decisão no próprio resultado")

# A franquia do Google em NLP e visão é a primeira faixa da tabela (permanente):
# essa sim é descontada. A de fala não foi localizada e não é descontada.
conferir("Fala · Google · franquia não localizada NÃO é descontada",
         buscar("fala", "google", contem_operacao="Standard")["custo_usd_com_franquia"], 160.0,
         "nenhuma franquia verificada para a tabela Recognition da V2")

print("=" * 78)
if falhas:
    print(f"FALHARAM {len(falhas)} conferências:")
    for f_ in falhas:
        print("  -", f_)
    sys.exit(1)
print("TODAS AS CONFERÊNCIAS PASSARAM")
