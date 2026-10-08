"""Utilitários compartilhados pelos testes dos exemplos."""

import importlib.util
import itertools
from pathlib import Path

import pytest

RAIZ = Path(__file__).parent.parent
_contador = itertools.count()


@pytest.fixture
def carregar_exemplo(monkeypatch):
    """
    Carrega um arquivo de exemplos/ como módulo, do jeito que ele está no disco.

    As variáveis de ambiente são definidas ANTES do carregamento porque vários
    exemplos as leem no topo do arquivo (ex.: GOOGLE_CLOUD_PROJECT). Os valores
    são fictícios: nenhum teste fala com a nuvem.
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
def imagem_falsa(tmp_path):
    """Um arquivo de imagem qualquer; o conteúdo só precisa ser lido em bytes."""
    caminho = tmp_path / "imagem_exemplo.jpg"
    caminho.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 64)
    return caminho


@pytest.fixture
def cliente_aws(monkeypatch):
    """
    Devolve (cliente, stubber) de um serviço AWS real, sem rede.

    O Stubber do botocore confere cada parâmetro enviado contra o modelo oficial
    do serviço — nome, tipo e obrigatoriedade — e confere a resposta simulada
    contra o formato de saída oficial. Parâmetro inventado ou com tipo errado
    faz o teste falhar.
    """
    import boto3
    from botocore.stub import Stubber

    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "teste")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "teste")

    def _criar(servico):
        cliente = boto3.client(servico, region_name="us-east-1")
        stubber = Stubber(cliente)
        return cliente, stubber

    return _criar
