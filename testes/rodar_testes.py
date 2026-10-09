# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pytest",
#     "pillow",
#     "soundfile",
#     "boto3==1.43.101",
#     "azure-ai-textanalytics==5.4.0",
#     "azure-ai-vision-imageanalysis==1.0.0",
#     "azure-core==1.41.0",
#     "google-cloud-language==2.21.0",
#     "google-cloud-vision==3.15.0",
#     "google-cloud-speech==2.40.0",
#     "google-cloud-storage",
#     "requests==2.34.2",
# ]
# ///
"""
Testa os 9 exemplos de código com dados reais: uma frase, uma foto e um áudio
(testes/dados/), cada um com resultado esperado em testes/dados/gabarito.json.

    uv run testes/rodar_testes.py          # offline: sem credenciais, sem custo
    uv run testes/rodar_testes.py --real   # contra os serviços de verdade (pede confirmação)

Offline, os testes conferem os arquivos de entrada contra os limites
documentados de cada provedor e executam cada exemplo de ponta a ponta com as
bibliotecas oficiais, trocando só a chamada de rede por uma resposta simulada.

Com --real, os mesmos arquivos vão para os serviços de verdade, a resposta é
conferida contra o gabarito e salva como evidência em testes/evidencias/. Os
provedores sem credencial configurada aparecem como SKIPPED, com o motivo.
"""

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).parent.parent
ARQUIVO_DE_CREDENCIAIS = RAIZ / ".env"

PLANO_REAL = """
  O que será enviado aos serviços reais (uma chamada por teste):

    NLP    frase.txt (28 caracteres)   Azure Language, Google Natural Language
    Visão  cachorro.jpg (690 KB)       AWS Rekognition, Azure Vision, Google Vision
    Fala   frase.flac (2,5 s)          Azure Speech (lote), Google Speech-to-Text V2

  AWS Comprehend e AWS Transcribe ficam DESLIGADOS: não existem no plano
  gratuito da AWS e exigiriam converter a conta para o plano pago.

  Proteção contra cobrança: ela vem do TIPO DE CONTA, não deste script.
    AWS     plano gratuito (Free plan): não cobra enquanto não houver upgrade
    Azure   Azure for Students: sem cartão; quando o crédito acaba, desativa
    Google  teste gratuito: não cobra sem upgrade manual da conta de faturamento
  Com contas desses tipos, o consumo acima cai na franquia ou no crédito
  promocional. Com contas pagas, ele custaria frações de centavo.

  As credenciais são lidas de {credenciais} e do ambiente.
  Nenhuma é escrita em arquivo, impressa na tela ou gravada nas evidências.
"""


def carregar_credenciais_locais():
    """Lê KEY=VALOR do .env local (ignorado pelo git) sem imprimir nenhum valor."""
    if not ARQUIVO_DE_CREDENCIAIS.is_file():
        return []
    nomes = []
    for linha in ARQUIVO_DE_CREDENCIAIS.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        nome, valor = linha.split("=", 1)
        os.environ.setdefault(nome.strip(), valor.strip().strip('"').strip("'"))
        nomes.append(nome.strip())
    return nomes


def chaves_soltas_no_repositorio():
    """
    Procura credenciais em arquivos que o git publicaria (versionados ou novos,
    não ignorados). Se achar alguma, o modo real não roda: um commit distraído
    a publicaria.
    """
    try:
        arquivos = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
            cwd=RAIZ, capture_output=True, text=True, check=True).stdout.split("\n")
    except (OSError, subprocess.CalledProcessError):
        return []
    # Padrões que exigem um VALOR de chave, para não acusar modelos com campos vazios.
    marcas = [re.compile(p) for p in (
        r"-----BEGIN [A-Z ]*PRIVATE KEY",                    # chave privada (ex.: JSON do Google)
        r'"private_key_id"\s*:\s*"[0-9a-f]{20,}"',
        r"AKIA[0-9A-Z]{16}",                                  # chave de acesso da AWS
        r"aws_secret_access_key\s*=\s*\S{20,}",
        r"AccountKey=[A-Za-z0-9+/=]{20,}",                    # cadeia de conexão do Azure Storage
        r"AZURE_\w*KEY\s*=\s*[A-Za-z0-9]{20,}",               # chave de recurso da Azure
    )]
    suspeitos = []
    for nome in filter(None, arquivos):
        caminho = RAIZ / nome
        if not caminho.is_file() or caminho.stat().st_size > 2_000_000:
            continue
        if nome.startswith("testes/") and nome.endswith(".py"):
            continue          # os testes citam os nomes das variáveis, sem valores
        try:
            conteudo = caminho.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if any(m.search(conteudo) for m in marcas):
            suspeitos.append(nome)
    return suspeitos


def preparar_modo_real(argumentos):
    suspeitos = chaves_soltas_no_repositorio()
    if suspeitos:
        print("\nABORTADO: possível credencial em arquivo que o git publicaria:")
        for s in suspeitos:
            print(f"   {s}")
        print("Mova para fora do repositório (ou para o .env) antes de rodar --real.")
        sys.exit(2)

    nomes = carregar_credenciais_locais()
    print(PLANO_REAL.format(credenciais=ARQUIVO_DE_CREDENCIAIS.name))
    if nomes:
        print(f"  Variáveis lidas do .env: {', '.join(sorted(nomes))}\n")

    if "--confirmo" in argumentos:
        argumentos.remove("--confirmo")
    elif input("  Digite 'sim' para chamar os serviços reais: ").strip().lower() != "sim":
        print("  Cancelado. Nenhum serviço foi chamado.")
        sys.exit(1)


if __name__ == "__main__":
    pasta = Path(__file__).parent
    argumentos = sys.argv[1:]
    if "--real" in argumentos:
        argumentos.remove("--real")
        preparar_modo_real(argumentos)
        filtro = ["-m", "real", "-rs"]          # -rs: mostra o motivo de cada SKIPPED
    else:
        filtro = ["-m", "not real"]
    sys.exit(pytest.main([str(pasta), "-v", "-p", "no:cacheprovider", *filtro, *argumentos]))
