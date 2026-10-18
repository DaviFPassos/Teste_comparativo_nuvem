"""
Converte a saída de cada provedor para a convenção comum:
    positivo · negativo · neutro · misto

A regra é versionada. Cada execução grava a versão e os parâmetros usados, e a
análise recalcula a classe normalizada a partir da resposta original — assim a
tabela final não depende de uma classe calculada em outro momento, com outra
regra.

Regra v1 (proposta em etapa2/metodologia.md, a congelar antes do teste final):

- Azure: o serviço já devolve uma classe. positive → positivo,
  negative → negativo, neutral → neutro, mixed → misto. Os três scores de
  confiança são guardados, mas não decidem nada: a classe é a do serviço.
- Google: o serviço devolve um número (`score`, de −1 a +1), não uma classe.
      score >  +L  → positivo
      score <  −L  → negativo
      −L ≤ score ≤ +L → neutro   (intervalo FECHADO: ±L exatos são neutros)
  com L = 0,25 por padrão. Esse número é uma escolha metodológica, não uma
  regra do Google; só pode ser ajustado com o piloto, nunca com o teste.
  O Google nunca produz `misto` nesta regra. A `magnitude` é guardada para a
  análise exploratória, mas não entra na classe — usá-la exigiria um segundo
  limiar, também escolhido pelo grupo, e foi deixado fora da v1.
"""

VERSAO = "v1"
LIMIAR_GOOGLE_PADRAO = 0.25

_AZURE = {"positive": "positivo", "negative": "negativo",
          "neutral": "neutro", "mixed": "misto"}


def normalizar_azure(rotulo):
    try:
        return _AZURE[rotulo]
    except KeyError:
        raise ValueError(f"rótulo da Azure fora da documentação: {rotulo!r}") from None


def normalizar_google(score, limiar=LIMIAR_GOOGLE_PADRAO):
    if not 0 < limiar < 1:
        raise ValueError(f"limiar fora de (0, 1): {limiar}")
    if not -1.0 <= score <= 1.0:
        raise ValueError(f"score do Google fora de [-1, 1]: {score}")
    if score > limiar:
        return "positivo"
    if score < -limiar:
        return "negativo"
    return "neutro"


def normalizar(provedor, rotulo_original=None, score=None, limiar=LIMIAR_GOOGLE_PADRAO):
    if provedor == "azure":
        return normalizar_azure(rotulo_original)
    if provedor == "google":
        return normalizar_google(float(score), limiar)
    if provedor == "simulado":
        return rotulo_original
    raise ValueError(f"provedor desconhecido: {provedor}")


def descrever(limiar=LIMIAR_GOOGLE_PADRAO):
    """Descrição gravada junto de cada execução."""
    return {"versao": VERSAO,
            "azure": dict(_AZURE),
            "google": {"limiar": limiar,
                       "positivo": f"score > {limiar}",
                       "negativo": f"score < {-limiar}",
                       "neutro": f"{-limiar} <= score <= {limiar}"}}
