# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pytest==9.1.1",
#   "azure-ai-textanalytics==5.4.0",
#   "azure-core==1.41.0",
#   "google-cloud-language==2.21.0",
#   "matplotlib==3.11.2",
# ]
# ///
"""
Testes offline da Etapa 2: sem credenciais, sem rede e sem custo.

    uv run etapa2/rodar_testes.py

Conferem as regras (normalização, métricas, trava de orçamento), o executor
(tentativas, interrupção, retomada) e os adaptadores com os SDKs REAIS, trocando
só o transporte de rede. Não substituem a coleta real exigida pelo enunciado.
"""

import sys
from pathlib import Path

import pytest

if __name__ == "__main__":
    pasta = Path(__file__).parent / "testes"
    sys.exit(pytest.main([str(pasta), "-q", "-p", "no:cacheprovider", *sys.argv[1:]]))
