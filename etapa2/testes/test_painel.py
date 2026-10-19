"""
Painel local, com provedores SIMULADOS (e a Azure com o SDK real sem rede) e um
servidor HTTP de verdade em 127.0.0.1.

O que interessa provar aqui são as proteções — um site de terceiros não
consegue gastar a franquia, o painel não serve arquivo arbitrário, a trava de
orçamento recusa a chamada, o texto digitado não é gravado — e que o seletor
de provedor só deixa usar o que está disponível nesta máquina.
"""

import http.client
import json
import sys
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "painel"))
import custo  # noqa: E402
import servidor  # noqa: E402
from provedores.simulado import ProvedorSimulado  # noqa: E402


def _estado(tmp_path, provedores=None, indisponiveis=None, simulado=True, **kw):
    if provedores is None:
        provedores = {"google": ProvedorSimulado(respostas={"Gostei muito": "positivo"})}
    if indisponiveis is None:
        indisponiveis = {"azure": "faltam no .env: AZURE_LANGUAGE_KEY"}
    return servidor.Estado(provedores, indisponiveis, sessoes=tmp_path / "sessoes", bases={},
                           dados=tmp_path, simulado=simulado, **kw)


@pytest.fixture
def painel(tmp_path):
    estado = _estado(tmp_path)
    srv = ThreadingHTTPServer(("127.0.0.1", 0), servidor.BaseHTTPRequestHandler)
    srv.RequestHandlerClass = servidor.criar_manipulador(estado, srv.server_port)
    threading.Thread(target=srv.serve_forever, daemon=True).start()

    def pedir(metodo, caminho, corpo=None, host=None, cabecalhos=None):
        c = http.client.HTTPConnection("127.0.0.1", srv.server_port, timeout=5)
        h = {"Host": host or f"127.0.0.1:{srv.server_port}", **(cabecalhos or {})}
        dados = None if corpo is None else json.dumps(corpo).encode()
        c.request(metodo, caminho, body=dados, headers=h)
        r = c.getresponse()
        bruto = r.read()
        c.close()
        try:
            return r.status, json.loads(bruto), r
        except ValueError:
            return r.status, bruto.decode(), r

    yield estado, pedir
    srv.shutdown()
    srv.server_close()


VALIDO = {"Content-Type": "application/json", "X-Painel": "1"}


# ------------------------------------------------------------- página e API

def test_pagina_e_servida_com_cabecalhos_de_seguranca(painel):
    _, pedir = painel
    status, corpo, r = pedir("GET", "/")
    assert status == 200 and "<title>Painel de Sentimento</title>" in corpo
    assert "frame-ancestors 'none'" in r.getheader("Content-Security-Policy")
    assert r.getheader("X-Content-Type-Options") == "nosniff"


def test_estado_lista_os_dois_provedores_com_disponibilidade(painel):
    _, pedir = painel
    status, corpo, _ = pedir("GET", "/api/estado")
    provs = {p["id"]: p for p in corpo["provedores"]}
    assert list(provs) == ["google", "azure"]                    # ordem fixa do seletor
    assert provs["google"]["ativo"] is True
    assert provs["azure"]["ativo"] is False and "AZURE_LANGUAGE_KEY" in provs["azure"]["motivo"]


def test_analise_ao_vivo_no_provedor_escolhido(painel):
    _, pedir = painel
    status, corpo, _ = pedir("POST", "/api/analisar", {"texto": "Gostei muito", "provedor": "google"},
                             cabecalhos=VALIDO)
    assert status == 200 and corpo["classe"] == "positivo" and corpo["provedor"] == "google"


def test_provedor_indisponivel_e_recusado_com_o_motivo(painel):
    estado, pedir = painel
    status, corpo, _ = pedir("POST", "/api/analisar", {"texto": "x", "provedor": "azure"}, cabecalhos=VALIDO)
    assert status == 409 and "AZURE_LANGUAGE_KEY" in corpo["detalhe"] and estado.chamadas == 0


def test_provedor_desconhecido_e_recusado(painel):
    estado, pedir = painel
    status, _, _ = pedir("POST", "/api/analisar", {"texto": "x", "provedor": "aws"}, cabecalhos=VALIDO)
    assert status == 400 and estado.chamadas == 0


# ------------------------------------------------------------------ proteções

@pytest.mark.parametrize("cabecalhos", [
    {"Content-Type": "application/json"},                 # sem o cabeçalho próprio
    {"Content-Type": "text/plain", "X-Painel": "1"},      # formulário/"simple request"
])
def test_requisicao_de_outro_site_nao_gasta_franquia(painel, cabecalhos):
    estado, pedir = painel
    status, _, _ = pedir("POST", "/api/analisar", {"texto": "x"}, cabecalhos=cabecalhos)
    assert status == 403 and estado.chamadas == 0


def test_host_diferente_e_recusado_dns_rebinding(painel):
    estado, pedir = painel
    status, _, _ = pedir("POST", "/api/analisar", {"texto": "x"}, host="atacante.exemplo:80",
                         cabecalhos=VALIDO)
    assert status == 403 and estado.chamadas == 0
    assert pedir("GET", "/api/estado", host="atacante.exemplo")[0] == 403


def test_pre_verificacao_cors_e_negada(painel):
    _, pedir = painel
    assert pedir("OPTIONS", "/api/analisar")[0] == 403


def test_texto_longo_ou_vazio_e_recusado_sem_chamar(painel):
    estado, pedir = painel
    assert pedir("POST", "/api/analisar", {"texto": "a" * 1001}, cabecalhos=VALIDO)[0] == 400
    assert pedir("POST", "/api/analisar", {"texto": "   "}, cabecalhos=VALIDO)[0] == 400
    assert estado.chamadas == 0


def test_nao_serve_arquivo_fora_da_lista(painel):
    _, pedir = painel
    for alvo in ("/etc/passwd", "/../.env", "/api/execucao?id=../../.env", "/api/execucao?id=%2e%2e"):
        assert pedir("GET", alvo)[0] == 404


def test_texto_digitado_nao_e_gravado(painel):
    estado, pedir = painel
    pedir("POST", "/api/analisar", {"texto": "Frase secreta do professor"}, cabecalhos=VALIDO)
    gravado = estado.registro.read_text(encoding="utf-8")
    assert "secreta" not in gravado
    linha = json.loads(gravado.splitlines()[0])
    assert linha["provedor"] == "google" and linha["status"] == "ok"


def test_trava_de_orcamento_e_por_provedor(tmp_path, monkeypatch):
    """A franquia da Azure esgotada não pode bloquear o Google, e vice-versa."""
    g, a = ProvedorSimulado(), ProvedorSimulado()
    estado = _estado(tmp_path, {"google": g, "azure": a}, {}, simulado=False)
    monkeypatch.setattr(custo, "PASTAS_REAIS", ())
    monkeypatch.setattr(custo, "franquia_mensal", lambda p: 1 if p == "azure" else 5000)
    status, corpo = estado.analisar_texto("frase", "azure")
    assert status == 402 and "Trava de orçamento" in corpo["erro"]
    assert a.chamadas == []                                       # a Azure nem foi chamada
    assert estado.consumo_no_mes("google") == 0 and estado.limite("google") == 4500


def test_limite_de_chamadas_por_sessao(tmp_path, monkeypatch):
    estado = _estado(tmp_path)
    monkeypatch.setattr(servidor, "MAX_CHAMADAS_POR_SESSAO", 2)
    assert [estado.analisar_texto("a")[0] for _ in range(3)] == [200, 200, 429]


# ------------------------------------------------- Azure com o SDK real

def test_azure_pelo_painel_com_sdk_real_e_rede_substituida(tmp_path, monkeypatch):
    """
    O caminho completo da Azure no painel: SDK oficial, resposta no formato da
    API (aqui, `mixed`), normalização v1 e o corpo que a página desenha.
    """
    from test_adaptadores import TransporteFalso, _resposta_azure
    from azure.ai.textanalytics import TextAnalyticsClient
    from azure.core.credentials import AzureKeyCredential
    from provedores.azure import ProvedorAzure

    monkeypatch.setenv("AZURE_LANGUAGE_ENDPOINT", "https://meu-recurso.cognitiveservices.azure.com/")
    monkeypatch.setenv("AZURE_LANGUAGE_KEY", "0" * 32)
    monkeypatch.setattr(custo, "PASTAS_REAIS", ())
    azure = ProvedorAzure()
    azure._cliente = TextAnalyticsClient(
        endpoint="https://meu-recurso.cognitiveservices.azure.com/",
        credential=AzureKeyCredential("0" * 32), retry_total=0,
        transport=TransporteFalso([(200, _resposta_azure("mixed", 0.47, 0.01, 0.52))]))
    estado = _estado(tmp_path, {"azure": azure}, {"google": "sem login"}, simulado=False)

    status, corpo = estado.analisar_texto("Entrega rápida, mas veio quebrado.", "azure")
    assert status == 200
    assert corpo["rotulo_original"] == "mixed" and corpo["classe"] == "misto"
    assert corpo["confiancas"] == {"positive": 0.47, "neutral": 0.01, "negative": 0.52}
    assert corpo["score"] is None and corpo["versao_modelo"] == "2025-01-01"
    assert "meu-recurso" not in json.dumps(corpo)                 # endpoint sanitizado
    assert json.loads(estado.registro.read_text().splitlines()[0])["unidades_estimadas"] == 1


def test_motivo_de_indisponibilidade_da_azure(monkeypatch):
    cfg = {"orcamento": {"teto_usd": 0, "azure_tier": "F0"}}
    monkeypatch.delenv("AZURE_LANGUAGE_KEY", raising=False)
    monkeypatch.setenv("AZURE_LANGUAGE_ENDPOINT", "https://x.cognitiveservices.azure.com/")
    assert "AZURE_LANGUAGE_KEY" in servidor.motivo_indisponivel("azure", cfg)
    monkeypatch.setenv("AZURE_LANGUAGE_KEY", "k" * 32)
    assert servidor.motivo_indisponivel("azure", cfg) is None
    cfg["orcamento"]["azure_tier"] = "S"                          # tier pago com teto zero
    assert "F0" in servidor.motivo_indisponivel("azure", cfg)


# --------------------------------------------------------------- execuções

def test_lista_e_abre_execucoes_e_ignora_simuladas_e_outro_formato(tmp_path, monkeypatch):
    import csv as _csv
    import executar
    simul = tmp_path / "simulacoes"
    monkeypatch.setattr(executar, "SIMULACOES", simul)
    dados = tmp_path / "dados"
    dados.mkdir()
    with open(dados / "demo.csv", "w", encoding="utf-8", newline="") as f:
        w = _csv.DictWriter(f, fieldnames=["id", "texto", "rotulo_referencia"])
        w.writeheader()
        w.writerows([{"id": "d1", "texto": "bom", "rotulo_referencia": "positivo"},
                     {"id": "d2", "texto": "ruim", "rotulo_referencia": "negativo"}])
    cfg = {"max_tentativas": 1, "espera_entre_tentativas_s": 0, "limiar_google": 0.25,
           "semente_ordem": 1, "orcamento": {"teto_usd": 0, "azure_tier": "F0"},
           "provedores": {"simulado": {"respostas": {"bom": "positivo"}}}}
    (tmp_path / "cfg.json").write_text(json.dumps(cfg))
    executar.main(["--dados", str(dados / "demo.csv"), "--simulado", "--config", str(tmp_path / "cfg.json")])
    (exec_dir,) = list(simul.iterdir())
    estado = servidor.Estado({}, {}, sessoes=tmp_path / "s", bases={"demonstracao": simul},
                             dados=dados, simulado=True)
    assert estado.listar_execucoes() == []                        # simulada não aparece como execução

    # a mesma pasta marcada como demonstração passa a ser listada e aberta
    c = json.loads((exec_dir / "config.json").read_text())
    c.update(simulado=False, demonstracao=True)
    (exec_dir / "config.json").write_text(json.dumps(c))
    (simul / "rafael").mkdir()                                     # formato antigo, sem config.json
    lista = estado.listar_execucoes()
    assert [e["id"] for e in lista] == [exec_dir.name]
    status, corpo = estado.abrir_execucao(exec_dir.name)
    assert status == 200
    assert corpo["metricas"]["programados_3_classes"] == 2
    assert {t["id"]: t["acertou"] for t in corpo["textos"]} == {"d1": True, "d2": False}
