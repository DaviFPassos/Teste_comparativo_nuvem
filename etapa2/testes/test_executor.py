"""
Executor com provedor SIMULADO: política de tentativas, interrupção, retomada,
ordem dos provedores e separação entre simulado e real.
"""

import csv
import json

import pytest

import executar
from provedores.simulado import ProvedorSimulado

CFG = {"max_tentativas": 3, "espera_entre_tentativas_s": 2.0, "intervalo_minimo_s": {},
       "limiar_google": 0.25, "semente_ordem": 7,
       "orcamento": {"teto_usd": 0, "azure_tier": "F0"}}


class Simulado2(ProvedorSimulado):
    nome = "simulado2"


def _registro(tmp_path, identificadores=()):
    return executar.Registro(tmp_path, True, list(identificadores))


def _jsonl(caminho):
    return [json.loads(l) for l in caminho.read_text(encoding="utf-8").splitlines() if l]


def test_erro_transitorio_e_repetido_com_espera_linear(tmp_path):
    prov = ProvedorSimulado(respostas={"bom": "positivo"}, falhas={"bom": ["timeout", "servidor"]})
    esperas = []
    reg = _registro(tmp_path)
    final = executar.executar_item(prov, {"id": "a", "texto": "bom"}, CFG, reg, "e", 1, {},
                                   dormir=esperas.append)
    reg.fechar()
    assert final == "ok"
    tent = _jsonl(tmp_path / "tentativas.jsonl")
    assert [t["status"] for t in tent] == ["erro", "erro", "ok"]
    assert [t["codigo"] for t in tent] == ["timeout", "servidor", None]
    assert esperas == [2.0, 4.0]                      # 1× e 2× a espera configurada
    pred = _jsonl(tmp_path / "predicoes.jsonl")[0]
    assert pred["n_tentativas"] == 3 and pred["rotulo_normalizado"] == "positivo"


def test_transitorio_esgotado_fica_como_erro(tmp_path):
    prov = ProvedorSimulado(falhas={"x": ["limite"] * 5})
    reg = _registro(tmp_path)
    final = executar.executar_item(prov, {"id": "a", "texto": "x"}, CFG, reg, "e", 1, {}, lambda s: None)
    reg.fechar()
    assert final == "limite" and len(prov.chamadas) == 3
    assert _jsonl(tmp_path / "predicoes.jsonl")[0]["status_final"] == "erro"


def test_erro_nao_transitorio_nao_e_repetido(tmp_path):
    prov = ProvedorSimulado(falhas={"x": ["entrada_invalida"]})
    reg = _registro(tmp_path)
    executar.executar_item(prov, {"id": "a", "texto": "x"}, CFG, reg, "e", 1, {}, lambda s: None)
    reg.fechar()
    assert len(prov.chamadas) == 1


def test_autenticacao_interrompe_o_provedor_e_nao_gasta_mais_chamadas(tmp_path):
    prov = ProvedorSimulado(falhas={"t1": ["autenticacao"]})
    reg = _registro(tmp_path)
    itens = [{"id": f"i{k}", "texto": f"t{k}"} for k in range(1, 5)]
    contagem = executar.coletar(itens, [prov], CFG, reg, "e", 1, dormir=lambda s: None,
                                saida=lambda *a: None)
    reg.fechar()
    assert prov.chamadas == ["t1"]
    assert contagem["simulado"]["nao_executado"] == 3
    preds = _jsonl(tmp_path / "predicoes.jsonl")
    assert [p["status_final"] for p in preds] == ["erro"] + ["nao_executado"] * 3


def test_ordem_dos_provedores_e_sorteada_por_texto_e_reprodutivel(tmp_path):
    itens = [{"id": f"i{k:02d}", "texto": f"t{k}"} for k in range(40)]

    def rodar(pasta):
        pasta.mkdir()
        reg = executar.Registro(pasta, True, [])
        executar.coletar(itens, [ProvedorSimulado(), Simulado2()], CFG, reg, "e", 11,
                         dormir=lambda s: None, saida=lambda *a: None)
        reg.fechar()
        return [(p["id"], p["provedor"], p["ordem_no_texto"]) for p in _jsonl(pasta / "predicoes.jsonl")]

    a, b = rodar(tmp_path / "a"), rodar(tmp_path / "b")
    assert a == b                                           # mesma semente, mesma ordem
    primeiros = {p for _, p, o in a if o == 1}
    assert primeiros == {"simulado", "simulado2"}           # ninguém é sempre o primeiro


def test_retomada_pula_o_que_ja_foi_concluido(tmp_path):
    itens = [{"id": "a", "texto": "x"}, {"id": "b", "texto": "y"}]
    reg = _registro(tmp_path)
    executar.coletar(itens[:1], [ProvedorSimulado()], CFG, reg, "e", 1, dormir=lambda s: None,
                     saida=lambda *a: None)
    reg.fechar()
    feitos = executar.concluidos(tmp_path)
    assert feitos == {("a", "simulado")}
    prov = ProvedorSimulado()
    reg = _registro(tmp_path)
    executar.coletar(itens, [prov], CFG, reg, "e", 1, pular=feitos, dormir=lambda s: None,
                     saida=lambda *a: None)
    reg.fechar()
    assert prov.chamadas == ["y"]                           # "x" não foi chamado de novo
    assert len(_jsonl(tmp_path / "predicoes.jsonl")) == 2


def test_registro_remove_identificadores_da_conta(tmp_path):
    reg = _registro(tmp_path, ["meu-recurso"])
    arq = reg.resposta("azure", "a", {"url": "https://meu-recurso.cognitiveservices.azure.com/x?sig=abc"})
    reg.fechar()
    texto = (tmp_path / arq).read_text(encoding="utf-8")
    assert "meu-recurso" not in texto and "sig=abc" not in texto


def _dataset(caminho, linhas):
    with open(caminho, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "texto", "rotulo_referencia"])
        w.writeheader()
        w.writerows(linhas)


def test_simulado_ponta_a_ponta_grava_fora_de_resultados_e_analisa(tmp_path, monkeypatch):
    import analisar
    resultados, simulacoes = tmp_path / "resultados", tmp_path / "simulacoes"
    for mod in (executar, analisar):
        monkeypatch.setattr(mod, "RESULTADOS", resultados)
        monkeypatch.setattr(mod, "SIMULACOES", simulacoes)
    dados = tmp_path / "dados.csv"
    _dataset(dados, [{"id": "t1", "texto": "ótimo", "rotulo_referencia": "positivo"},
                     {"id": "t2", "texto": "péssimo", "rotulo_referencia": "negativo"},
                     {"id": "t3", "texto": "abre às 9h", "rotulo_referencia": "neutro"},
                     {"id": "t4", "texto": "bom mas caro", "rotulo_referencia": "misto"}])
    cfg = {**CFG, "provedores": {"simulado": {"respostas": {"ótimo": "positivo", "péssimo": "misto"}}}}
    (tmp_path / "cfg.json").write_text(json.dumps(cfg))
    executar.main(["--dados", str(dados), "--simulado", "--config", str(tmp_path / "cfg.json")])
    assert not resultados.exists()                          # simulado NUNCA vai para resultados/
    execucao = next(simulacoes.iterdir()).name
    analisar.main(["--execucao", execucao, "--simulado", "--dados", str(dados)])
    m = json.loads((simulacoes / execucao / "analise" / "metricas.json").read_text(encoding="utf-8"))
    q = m["por_provedor"]["simulado"]["qualidade_na_intersecao"]
    assert m["programados_3_classes"] == 3 and m["fora_da_avaliacao_principal"] == {"misto": 1}
    assert q["acertos"] == 2                                 # ótimo→positivo, abre→neutro (padrão)
    assert m["por_provedor"]["simulado"]["previsoes_misto_na_intersecao"] == 1
    assert (simulacoes / execucao / "graficos" / "qualidade.png").exists()


def test_dataset_congelado_alterado_e_recusado(tmp_path):
    dados = tmp_path / "teste.csv"
    _dataset(dados, [{"id": "t1", "texto": "a", "rotulo_referencia": "neutro"}])
    (tmp_path / "manifesto_conjuntos.json").write_text(json.dumps({"arquivos": {"teste.csv": "0" * 64}}))
    with pytest.raises(SystemExit, match="alterado depois de congelado"):
        executar.conferir_congelamento(dados)


def test_analise_recusa_gabarito_de_outro_arquivo(tmp_path):
    import analisar
    dados = tmp_path / "d.csv"
    _dataset(dados, [{"id": "t1", "texto": "a", "rotulo_referencia": "neutro"}])
    with pytest.raises(SystemExit, match="não é o arquivo usado"):
        analisar.carregar_gabarito(dados, "0" * 64)


def test_simulado_e_demonstracao_nao_se_combinam(tmp_path):
    dados = tmp_path / "d.csv"
    _dataset(dados, [{"id": "t1", "texto": "a", "rotulo_referencia": "neutro"}])
    with pytest.raises(SystemExit):
        executar.main(["--dados", str(dados), "--simulado", "--demonstracao"])


def test_analise_recusa_abrir_execucao_com_o_tipo_errado(tmp_path, monkeypatch):
    """Uma execução simulada não pode ser analisada como demonstração, nem o contrário."""
    import analisar
    simulacoes = tmp_path / "simulacoes"
    for mod in (executar, analisar):
        monkeypatch.setattr(mod, "SIMULACOES", simulacoes)
    monkeypatch.setattr(analisar, "DEMONSTRACOES", simulacoes)   # mesma pasta, tipo diferente
    dados = tmp_path / "dados.csv"
    _dataset(dados, [{"id": "t1", "texto": "ótimo", "rotulo_referencia": "positivo"}])
    (tmp_path / "cfg.json").write_text(json.dumps(CFG))
    executar.main(["--dados", str(dados), "--simulado", "--config", str(tmp_path / "cfg.json")])
    execucao = next(simulacoes.iterdir()).name
    with pytest.raises(SystemExit, match="não confere"):
        analisar.main(["--execucao", execucao, "--demonstracao", "--dados", str(dados)])
