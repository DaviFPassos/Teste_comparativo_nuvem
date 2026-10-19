"""
Métricas conferidas contra contas feitas à mão.

Os dados aqui são FICTÍCIOS e servem só para conferir as fórmulas.
"""

import pytest

from analisar import (matriz_de_confusao, mcnemar_exato, mediana,
                      metricas_de_classificacao, percentil_posto_mais_proximo)
from anotacao import kappa_de_cohen

REF = ["positivo", "positivo", "positivo", "negativo", "negativo", "neutro", "neutro", "neutro"]
PRV = ["positivo", "positivo", "negativo", "negativo", "misto",    "neutro", "positivo", "neutro"]


def test_acuracia_e_f1_a_mao():
    m = metricas_de_classificacao(REF, PRV)
    # acertos: posições 0, 1, 3, 5, 7 → 5 de 8
    assert m["acertos"] == 5 and m["acuracia"] == pytest.approx(5 / 8)
    pos = m["por_classe"]["positivo"]
    # positivo: TP=2 (0,1); FP=1 (6); FN=1 (2) → P=2/3, R=2/3, F1=2/3
    assert (pos["tp"], pos["fp"], pos["fn"]) == (2, 1, 1)
    assert pos["f1"] == pytest.approx(2 / 3)
    neg = m["por_classe"]["negativo"]
    # negativo: TP=1 (3); FP=1 (2); FN=1 (4, previsto misto) → F1=1/2
    assert (neg["tp"], neg["fp"], neg["fn"]) == (1, 1, 1)
    assert neg["f1"] == pytest.approx(0.5)
    neu = m["por_classe"]["neutro"]
    # neutro: TP=2 (5,7); FP=0; FN=1 (6) → P=1, R=2/3, F1=0,8
    assert neu["f1"] == pytest.approx(0.8)
    assert m["macro_f1"] == pytest.approx((2 / 3 + 0.5 + 0.8) / 3)


def test_misto_previsto_conta_como_erro_e_nao_vira_neutro():
    m = metricas_de_classificacao(["negativo"], ["misto"])
    assert m["acertos"] == 0
    assert m["por_classe"]["negativo"]["fn"] == 1
    assert m["por_classe"]["neutro"]["fp"] == 0


def test_denominador_nulo_vale_zero_e_e_sinalizado():
    m = metricas_de_classificacao(["positivo", "positivo"], ["positivo", "positivo"])
    assert m["por_classe"]["negativo"]["f1"] == 0.0
    assert any("negativo" in x for x in m["indefinidos"])


def test_matriz_tem_coluna_misto():
    mc = matriz_de_confusao(REF, PRV)
    assert mc["negativo"]["misto"] == 1
    assert sum(sum(l.values()) for l in mc.values()) == len(REF)


def test_matriz_recusa_classe_fora_da_convencao():
    with pytest.raises(ValueError):
        matriz_de_confusao(["positivo"], ["positive"])


def test_percentil_posto_mais_proximo_a_mao():
    v = list(range(1, 21))                       # 1..20
    assert percentil_posto_mais_proximo(v, 95) == 19   # ceil(0,95×20)=19º valor
    assert percentil_posto_mais_proximo(v, 50) == 10
    assert percentil_posto_mais_proximo([7], 95) == 7
    assert percentil_posto_mais_proximo([], 95) is None


def test_mediana_par_e_impar():
    assert mediana([3, 1, 2]) == 2 and mediana([4, 1, 3, 2]) == 2.5


def test_mcnemar_exato_a_mao():
    # 6 discordâncias: A acertou 5 em que B errou, B acertou 1 em que A errou.
    a = [True] * 5 + [False] + [True] * 10
    b = [False] * 5 + [True] + [True] * 10
    r = mcnemar_exato(a, b)
    assert (r["b"], r["c"]) == (5, 1)
    # P(X<=1 | n=6, p=1/2) = (1 + 6)/64 ; bilateral = 14/64
    assert r["p_valor"] == pytest.approx(14 / 64)


def test_mcnemar_sem_discordancias():
    assert mcnemar_exato([True, False], [True, False])["p_valor"] == 1.0


def test_kappa_de_cohen_a_mao():
    a = ["pos", "pos", "neg", "neg"]
    b = ["pos", "neg", "neg", "neg"]
    # p_o = 3/4; p_e = (2·1 + 2·3)/16 = 1/2; kappa = (0,75−0,5)/(1−0,5) = 0,5
    assert kappa_de_cohen(a, b) == pytest.approx(0.5)
    assert kappa_de_cohen(["x", "x"], ["x", "x"]) is None


def _pred(i, prov, rotulo_norm, rotulo=None, score=None):
    return {"id": i, "provedor": prov, "status_final": "ok", "rotulo_original": rotulo,
            "score": score, "rotulo_normalizado": rotulo_norm, "simulado": False}


CONFIG = {"normalizacao": {"google": {"limiar": 0.25}}}
GABARITO = {"t1": {"rotulo_referencia": "positivo", "texto": "a"},
            "t2": {"rotulo_referencia": "negativo", "texto": "b"},
            "t3": {"rotulo_referencia": "neutro", "texto": "c"},
            "t4": {"rotulo_referencia": "misto", "texto": "d"}}


def test_analise_recalcula_a_classe_e_detecta_registro_adulterado():
    from analisar import analisar
    preds = [_pred("t1", "google", "positivo", score=0.8),
             _pred("t2", "google", "positivo", score=-0.7)]      # adulterado: -0,7 é negativo
    with pytest.raises(SystemExit, match="recalculada"):
        analisar(preds, [], CONFIG, {k: GABARITO[k] for k in ("t1", "t2")})


def test_intersecao_exclui_texto_que_falhou_em_um_provedor():
    from analisar import analisar
    preds = [_pred("t1", "azure", "positivo", "positive"), _pred("t1", "google", "positivo", score=0.9),
             _pred("t2", "azure", "misto", "mixed"),       _pred("t2", "google", "negativo", score=-0.9),
             _pred("t3", "azure", "neutro", "neutral"),
             {"id": "t3", "provedor": "google", "status_final": "erro", "codigo_erro_final": "timeout",
              "rotulo_normalizado": None, "simulado": False},
             _pred("t4", "azure", "misto", "mixed"),       _pred("t4", "google", "neutro", score=0.1)]
    tent = [{"provedor": "azure", "status": "ok", "duracao_ms": 100.0, "unidades_estimadas": 1}] * 4 + \
           [{"provedor": "google", "status": "ok", "duracao_ms": 50.0, "unidades_estimadas": 1}] * 3 + \
           [{"provedor": "google", "status": "erro", "codigo": "timeout", "duracao_ms": 30000.0,
             "unidades_estimadas": 1}]
    r = analisar(preds, tent, CONFIG, GABARITO)
    assert r["programados_3_classes"] == 3                 # t4 (misto) fora da avaliação principal
    assert r["intersecao"] == 2                            # t3 falhou no Google
    az, go = r["por_provedor"]["azure"], r["por_provedor"]["google"]
    assert az["qualidade_na_intersecao"]["acertos"] == 1   # t1 certo; t2 previsto misto = erro
    assert go["qualidade_na_intersecao"]["acertos"] == 2
    # acertos sobre programados: a Azure acerta t3 fora da interseção; o Google falhou nele
    assert az["acertos_sobre_programados"] == 2 and go["acertos_sobre_programados"] == 2
    assert go["sucesso_por_tentativa"] == pytest.approx(3 / 4)
    assert go["sucesso_por_texto"] == pytest.approx(2 / 3)
    assert go["timeouts"]["n"] == 1 and go["latencia_ms"]["maximo"] == 50.0  # timeout fora da latência
    assert r["exploratorio"]["misto"] == {"azure": {"misto": 1}, "google": {"neutro": 1}}
    assert r["comparacao_pareada"]["mcnemar_exato"] == {"b": 0, "c": 1, "p_valor": 1.0}


def test_avaliacao_sem_neutro_usa_so_positivo_e_negativo():
    from analisar import analisar
    gab = dict(GABARITO, t5={"rotulo_referencia": "positivo", "texto": "e"})
    preds = [_pred("t1", "azure", "positivo", "positive"), _pred("t1", "google", "positivo", score=0.9),
             _pred("t2", "azure", "misto", "mixed"),       _pred("t2", "google", "negativo", score=-0.9),
             _pred("t3", "azure", "neutro", "neutral"),    _pred("t3", "google", "neutro", score=0.0),
             _pred("t4", "azure", "misto", "mixed"),       _pred("t4", "google", "neutro", score=0.1),
             _pred("t5", "azure", "positivo", "positive"), _pred("t5", "google", "neutro", score=0.2)]
    r = analisar(preds, [], CONFIG, gab)
    sn = r["sem_neutro"]
    assert sn["n"] == 3                                    # t1, t2, t5: sem o neutro (t3) e o misto (t4)
    az, go = sn["por_provedor"]["azure"], sn["por_provedor"]["google"]
    assert az["acertos"] == 2 and go["acertos"] == 2       # misto e neutro previstos contam como erro
    # positivo: Azure TP=2 FN=0 FP=0 → F1 1; negativo: TP=0 FN=1 → F1 0; macro 0,5
    assert az["macro_f1"] == pytest.approx(0.5)
    assert sn["mcnemar_exato"] == {"b": 1, "c": 1, "p_valor": 1.0}
