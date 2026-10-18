"""A regra de normalização é a fronteira entre a resposta do serviço e a métrica."""

import pytest

import normalizar


@pytest.mark.parametrize("rotulo,esperado", [
    ("positive", "positivo"), ("negative", "negativo"),
    ("neutral", "neutro"), ("mixed", "misto")])
def test_azure_quatro_rotulos_inclusive_misto(rotulo, esperado):
    assert normalizar.normalizar("azure", rotulo) == esperado


def test_azure_rotulo_desconhecido_falha_em_vez_de_virar_neutro():
    with pytest.raises(ValueError):
        normalizar.normalizar("azure", "Positive")


@pytest.mark.parametrize("score,esperado", [
    (0.9, "positivo"), (0.2501, "positivo"),
    (0.25, "neutro"), (0.0, "neutro"), (-0.25, "neutro"),   # intervalo FECHADO
    (-0.2501, "negativo"), (-1.0, "negativo")])
def test_google_limiares_inclusivos(score, esperado):
    assert normalizar.normalizar("google", score=score) == esperado


def test_google_nunca_produz_misto():
    vistos = {normalizar.normalizar("google", score=s / 100) for s in range(-100, 101)}
    assert vistos == {"positivo", "negativo", "neutro"}


def test_google_score_fora_do_intervalo_documentado_falha():
    with pytest.raises(ValueError):
        normalizar.normalizar("google", score=1.2)


def test_descricao_registra_versao_e_limiar():
    d = normalizar.descrever(0.3)
    assert d["versao"] == normalizar.VERSAO and d["google"]["limiar"] == 0.3
