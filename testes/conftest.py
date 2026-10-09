"""Utilitários compartilhados pelos testes dos exemplos."""

import hashlib
import importlib.util
import itertools
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import pytest

RAIZ = Path(__file__).parent.parent
DADOS = Path(__file__).parent / "dados"
EVIDENCIAS = Path(__file__).parent / "evidencias"

FRASE = DADOS / "frase.txt"
IMAGEM = DADOS / "cachorro.jpg"
AUDIO = DADOS / "frase.flac"
GABARITO = json.loads((DADOS / "gabarito.json").read_text(encoding="utf-8"))

_contador = itertools.count()


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "real: chama o serviço de verdade (exige credenciais e gera custo)")


def sha256(caminho):
    return hashlib.sha256(Path(caminho).read_bytes()).hexdigest()


@pytest.fixture
def carregar_exemplo(monkeypatch):
    """
    Carrega um arquivo de exemplos/ como módulo, do jeito que ele está no disco.

    As variáveis de ambiente são definidas ANTES do carregamento porque vários
    exemplos as leem no topo do arquivo (ex.: GOOGLE_CLOUD_PROJECT).
    """

    def _carregar(caminho_relativo, **ambiente):
        for nome, valor in ambiente.items():
            monkeypatch.setenv(nome, valor)
        caminho = RAIZ / caminho_relativo
        nome = f"exemplo_{caminho.stem}_{next(_contador)}"
        spec = importlib.util.spec_from_file_location(nome, caminho)
        modulo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modulo)
        return modulo

    return _carregar


@pytest.fixture
def cliente_aws(monkeypatch):
    """
    Devolve (cliente, stubber) de um serviço AWS real, sem rede.

    O Stubber do botocore confere cada parâmetro enviado contra o modelo oficial
    do serviço — nome, tipo e obrigatoriedade — e confere a resposta simulada
    contra o formato de saída oficial.
    """
    import boto3
    from botocore.stub import Stubber

    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "teste")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "teste")

    def _criar(servico):
        cliente = boto3.client(servico, region_name="us-east-1")
        return cliente, Stubber(cliente)

    return _criar


# ---------------------------------------------------------------------------
# Evidências dos testes reais
# ---------------------------------------------------------------------------

def _para_json(objeto):
    """Converte respostas dos três SDKs (dict, proto, modelos Azure) em JSON."""
    if objeto is None or isinstance(objeto, (str, int, float, bool)):
        return objeto
    if isinstance(objeto, bytes):
        return f"<{len(objeto)} bytes>"
    if isinstance(objeto, datetime):
        return objeto.isoformat()
    if isinstance(objeto, dict):
        return {str(k): _para_json(v) for k, v in objeto.items()}
    if isinstance(objeto, (list, tuple)):
        return [_para_json(v) for v in objeto]
    if hasattr(objeto, "_pb"):                                  # proto-plus (Google)
        from google.protobuf.json_format import MessageToDict
        return MessageToDict(objeto._pb)
    if hasattr(objeto, "as_dict"):                              # modelos Azure novos
        return _para_json(objeto.as_dict())
    if hasattr(objeto, "__dict__"):                             # modelos Azure antigos
        return {k: _para_json(v) for k, v in vars(objeto).items() if not k.startswith("_")}
    return repr(objeto)


def _identificadores_da_conta():
    """Valores que, sem ser senha, identificam a conta de quem rodou o teste."""
    import os
    from urllib.parse import urlparse
    valores = [os.environ.get(v) for v in ("TESTE_S3_BUCKET", "TESTE_GCS_BUCKET",
                                           "GOOGLE_CLOUD_PROJECT")]
    for v in ("AZURE_LANGUAGE_ENDPOINT", "AZURE_VISION_ENDPOINT"):
        if os.environ.get(v):
            valores.append(urlparse(os.environ[v]).hostname.split(".")[0])
    return sorted({x for x in valores if x}, key=len, reverse=True)


_PADROES_DE_CONTA = [
    (re.compile(r"\b\d{12}\b"), "<removido: conta AWS>"),                     # ID de conta AWS
    (re.compile(r"projects/[^/\s\"]+"), "projects/<removido: projeto>"),       # projeto Google
    (re.compile(r"[a-z0-9-]+\.cognitiveservices\.azure\.com"),
     "<removido: recurso>.cognitiveservices.azure.com"),                      # recurso Azure
]


def _sanitizar(objeto, identificadores=None):
    """
    Tira o que não pode ir para um repositório público — nem para os colegas.

    1. Credenciais temporárias: a AWS devolve URLs pré-assinadas (com
       X-Amz-Credential) e a Azure URLs com token SAS. Em ambos os casos a
       credencial está na query string, que é removida.
    2. Identificadores da conta: nome de bucket, ID de projeto do Google,
       número da conta AWS e nome do recurso Azure. Não são senha, mas
       identificam a conta de quem rodou o teste.
    3. Metadados HTTP da AWS, que não acrescentam nada à evidência.
    """
    if identificadores is None:
        identificadores = _identificadores_da_conta()
    if isinstance(objeto, dict):
        # As chaves também passam pela limpeza: o Google indexa o resultado do
        # lote pela URI do arquivo (gs://<bucket>/...), que identifica a conta.
        return {_sanitizar(k, identificadores): _sanitizar(v, identificadores)
                for k, v in objeto.items() if k != "ResponseMetadata"}
    if isinstance(objeto, list):
        return [_sanitizar(v, identificadores) for v in objeto]
    if isinstance(objeto, str):
        if re.match(r"https?://", objeto) and "?" in objeto:
            objeto = objeto.split("?", 1)[0] + "?<removido: token de acesso>"
        for valor in identificadores:
            objeto = objeto.replace(valor, "<removido: identificador da conta>")
        for padrao, troca in _PADROES_DE_CONTA:
            objeto = padrao.sub(troca, objeto)
    return objeto


@pytest.fixture
def registrar_evidencia():
    """Grava a resposta real de um serviço, com a entrada e o veredito."""

    def _registrar(*, categoria, provedor, servico, regiao, entrada, resposta,
                   obtido, esperado, aprovado):
        EVIDENCIAS.mkdir(exist_ok=True)
        registro = {
            "data_hora_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "categoria": categoria,
            "provedor": provedor,
            "servico": servico,
            "regiao": regiao,
            "entrada": {"arquivo": f"testes/dados/{Path(entrada).name}",
                        "sha256": sha256(entrada)},
            "esperado": esperado,
            "obtido": _sanitizar(_para_json(obtido)),
            "aprovado": aprovado,
            "resposta_bruta_do_servico": _sanitizar(_para_json(resposta)),
        }
        destino = EVIDENCIAS / f"{categoria}_{provedor}.json"
        destino.write_text(json.dumps(registro, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
        return destino

    return _registrar
