"""A trava de orçamento é o que garante o teto de US$ 0 decidido pelo grupo."""

import json

import pytest

import custo

F0 = {"teto_usd": 0, "azure_tier": "F0"}


def test_unidades_seguem_as_regras_da_etapa1():
    assert custo.unidades("google", "a" * 1) == 1          # mínimo de 1
    assert custo.unidades("google", "a" * 1001) == 2
    assert custo.unidades("azure", "a" * 1000) == 1
    assert custo.unidades("azure", "a" * 1001) == 2


def test_franquias_vem_do_csv_da_etapa1():
    assert custo.franquia_mensal("azure") == 5000
    assert custo.franquia_mensal("google") == 5000


def test_rodada_pequena_passa(tmp_path):
    plano = custo.planejar(["texto curto"] * 330, ["azure", "google"], 3, F0, tmp_path)
    assert plano["google"]["pior_caso"] == 990
    assert plano["google"]["custo_estimado_pior_caso_usd"] == 0


def test_pior_caso_conta_todas_as_tentativas(tmp_path):
    # 1.600 × 3 tentativas = 4.800 > 4.500 (90% de 5.000): recusada, embora 1.600 caiba
    with pytest.raises(custo.OrcamentoExcedido):
        custo.planejar(["x"] * 1600, ["google"], 3, F0, tmp_path)


def test_azure_fora_do_f0_e_recusada_com_teto_zero(tmp_path):
    with pytest.raises(custo.OrcamentoExcedido, match="F0"):
        custo.planejar(["x"], ["azure"], 1, {"teto_usd": 0, "azure_tier": "S"}, tmp_path)


def test_consumo_declarado_e_descontado(tmp_path):
    orc = {**F0, "consumo_externo_no_mes": {"google": 4400}}
    with pytest.raises(custo.OrcamentoExcedido):
        custo.planejar(["x"] * 50, ["google"], 3, orc, tmp_path)


def test_consumo_de_coletas_reais_do_mes_e_descontado(tmp_path):
    from datetime import datetime, timezone
    mes = datetime.now(timezone.utc).strftime("%Y-%m")
    pasta = tmp_path / "exec1"
    pasta.mkdir()
    linhas = [{"provedor": "google", "simulado": False, "data_hora_utc": f"{mes}-01T00:00:00",
               "unidades_estimadas": 4400},
              {"provedor": "google", "simulado": True, "data_hora_utc": f"{mes}-01T00:00:00",
               "unidades_estimadas": 999999}]          # simulada: não conta
    (pasta / "tentativas.jsonl").write_text("\n".join(json.dumps(l) for l in linhas))
    assert custo.consumo_local_no_mes("google", tmp_path) == 4400
    with pytest.raises(custo.OrcamentoExcedido):
        custo.planejar(["x"] * 50, ["google"], 3, F0, tmp_path)


def test_demonstracao_conta_no_consumo_do_mes(tmp_path, monkeypatch):
    """Demonstração ao professor gasta a mesma franquia que a coleta: tem de contar."""
    from datetime import datetime, timezone
    mes = datetime.now(timezone.utc).strftime("%Y-%m")
    resultados, demos = tmp_path / "resultados", tmp_path / "demonstracoes"
    for pasta, unidades in ((resultados / "e1", 100), (demos / "d1", 8)):
        pasta.mkdir(parents=True)
        (pasta / "tentativas.jsonl").write_text(json.dumps(
            {"provedor": "google", "simulado": False, "data_hora_utc": f"{mes}-02T10:00:00",
             "unidades_estimadas": unidades}) + "\n")
    monkeypatch.setattr(custo, "PASTAS_REAIS", (resultados, demos))
    assert custo.consumo_local_no_mes("google") == 108
