"""
Unidades cobradas e trava de orçamento da coleta real.

As regras de contagem NÃO são reescritas aqui: vêm de custos/calcular_custos.py,
as mesmas que a Etapa 1 conferiu (31 conferências). As franquias vêm de
custos/franquias.csv e os preços de custos/premissas.csv.

Orçamento decidido pelo grupo: **US$ 0 — só franquia**. Com teto zero:

- Azure: só o tier F0 é aceito. O F0 não tem cobrança; ao esgotar a cota
  mensal ele recusa as chamadas (HTTP 403) em vez de cobrar. A trava existe para
  não começar uma rodada que a cota não comporta e que pararia no meio.
- Google: a franquia é a primeira faixa da tabela (5.000 unidades/mês). Acima
  dela há cobrança — então aqui a trava é o que impede gasto.

Hipóteses conservadoras, porque errar para menos geraria custo:
- toda tentativa consome unidades, inclusive as que falham (a documentação não
  garante o contrário);
- planeja-se o pior caso: cada texto usando todas as tentativas permitidas;
- usa-se no máximo 90% da franquia, para sobrar margem a usos fora deste programa
  e a diferenças de fuso no fechamento do mês;
- o consumo já feito neste mês por esta máquina (lido de etapa2/resultados/) e o
  declarado na configuração são descontados antes.
"""

import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "custos"))
from calcular_custos import registros_azure_language, unidades_google_nl  # noqa: E402

FRACAO_SEGURA = 0.9


class OrcamentoExcedido(SystemExit):
    pass


def unidades(provedor, texto):
    """Unidades cobradas por UMA chamada com este texto."""
    n = len(texto)
    if provedor == "google":
        return unidades_google_nl(n)
    if provedor == "azure":
        return max(1, registros_azure_language(n))
    if provedor == "simulado":
        return 0
    raise ValueError(provedor)


def franquia_mensal(provedor, arquivo=RAIZ / "custos" / "franquias.csv"):
    """Franquia mensal de sentimento (nlp) registrada na Etapa 1."""
    with open(arquivo, encoding="utf-8", newline="") as f:
        for l in csv.DictReader(f):
            if l["categoria"] == "nlp" and l["provedor"] == provedor:
                return int(float(l["franquia"]))
    raise KeyError(provedor)


def preco_por_unidade(provedor, arquivo=RAIZ / "custos" / "premissas.csv"):
    """Preço da primeira faixa paga (USD por unidade), para estimativa de custo."""
    with open(arquivo, encoding="utf-8", newline="") as f:
        faixas = [l for l in csv.DictReader(f)
                  if l["categoria"] == "nlp" and l["provedor"] == provedor
                  and float(l["preco_usd"]) > 0]
    faixa = min(faixas, key=lambda l: float(l["faixa_min"]))
    preco = float(faixa["preco_usd"])
    return preco / 1000 if "1000" in faixa["unidade_preco"] else preco


# Toda chamada real gasta a mesma franquia: coleta, demonstrações e o painel ao vivo.
PASTAS_REAIS = (RAIZ / "etapa2" / "resultados", RAIZ / "etapa2" / "demonstracoes",
                RAIZ / "etapa2" / "painel" / "sessoes")


def consumo_local_no_mes(provedor, resultados=None, agora=None):
    """
    Unidades enviadas a este provedor no mês corrente (UTC) por chamadas reais:
    as da coleta E as de demonstração, que gastam a mesma franquia.
    """
    agora = agora or datetime.now(timezone.utc)
    mes = agora.strftime("%Y-%m")
    pastas = [Path(resultados)] if resultados else PASTAS_REAIS
    total = 0
    for arq in (a for pasta in pastas for a in pasta.glob("*/tentativas.jsonl")):
        for linha in arq.read_text(encoding="utf-8").splitlines():
            if not linha.strip():
                continue
            t = json.loads(linha)
            if (t.get("provedor") == provedor and not t.get("simulado")
                    and t.get("data_hora_utc", "").startswith(mes)):
                total += int(t.get("unidades_estimadas") or 0)
    return total


def planejar(textos, provedores, max_tentativas, orcamento, resultados=None):
    """
    Devolve o plano de consumo por provedor e LEVANTA OrcamentoExcedido se a
    rodada puder ultrapassar o teto. `textos` é a lista de strings a enviar.
    """
    teto = float(orcamento.get("teto_usd", 0))
    externo = orcamento.get("consumo_externo_no_mes", {}) or {}
    plano, problemas = {}, []
    for prov in provedores:
        if prov == "simulado":
            plano[prov] = {"unidades_planejadas": 0, "pior_caso": 0}
            continue
        por_rodada = sum(unidades(prov, t) for t in textos)
        pior = por_rodada * max_tentativas
        local = consumo_local_no_mes(prov, resultados)
        ja_usado = local + int(externo.get(prov, 0))
        franquia = franquia_mensal(prov)
        limite = int(franquia * FRACAO_SEGURA)
        excedente = max(0, ja_usado + pior - franquia)
        custo_pior = excedente * preco_por_unidade(prov)
        plano[prov] = {"unidades_planejadas": por_rodada, "pior_caso": pior,
                       "consumo_no_mes_antes": ja_usado, "franquia_mensal": franquia,
                       "limite_usado_pela_trava": limite,
                       "custo_estimado_pior_caso_usd": round(custo_pior, 4)}

        if prov == "azure" and teto == 0 and orcamento.get("azure_tier", "").upper() != "F0":
            problemas.append("azure: com teto US$ 0 só o tier F0 é aceito (declare "
                             "\"azure_tier\": \"F0\" e confira no portal que o recurso é F0).")
        if teto == 0 and ja_usado + pior > limite:
            problemas.append(f"{prov}: pior caso {pior} + já usado {ja_usado} unidades passa de "
                             f"{limite} ({FRACAO_SEGURA:.0%} da franquia de {franquia}/mês).")
        if teto > 0 and custo_pior > teto:
            problemas.append(f"{prov}: custo no pior caso US$ {custo_pior:.2f} passa do teto "
                             f"de US$ {teto:.2f}.")
    if problemas:
        raise OrcamentoExcedido("Coleta recusada pela trava de orçamento:\n  - "
                                + "\n  - ".join(problemas))
    return plano
