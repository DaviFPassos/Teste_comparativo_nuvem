# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pytest",
#     "boto3==1.43.101",
#     "azure-ai-textanalytics==5.4.0",
#     "azure-ai-vision-imageanalysis==1.0.0",
#     "azure-core==1.41.0",
#     "google-cloud-language==2.21.0",
#     "google-cloud-vision==3.15.0",
#     "google-cloud-speech==2.40.0",
#     "requests==2.34.2",
# ]
# ///
"""
Testa os 9 exemplos de código, sem credenciais, sem rede e sem custo.

    uv run testes/rodar_testes.py

Cada teste carrega o arquivo do exemplo exatamente como ele está em exemplos/
e executa o main() de ponta a ponta. A única coisa substituída é a chamada de
rede ao provedor, que devolve uma resposta simulada. Todo o resto é real: as
bibliotecas oficiais da AWS, da Azure e do Google estão instaladas e são elas
que validam o que o exemplo envia e recebe.
"""

import sys
from pathlib import Path

import pytest

if __name__ == "__main__":
    pasta = Path(__file__).parent
    sys.exit(pytest.main([str(pasta), "-v", "-p", "no:cacheprovider", *sys.argv[1:]]))
