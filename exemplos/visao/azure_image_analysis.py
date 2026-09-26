# /// script
# requires-python = ">=3.10"
# dependencies = ["azure-ai-vision-imageanalysis", "azure-core"]
# ///
"""
Categoria: Visão computacional
Provedor:  Microsoft Azure — Azure Vision in Foundry Tools (Image Analysis)
Operação:  Analyze Image com a feature TAGS

ESTADO DE VALIDAÇÃO: exemplo ILUSTRATIVO, NÃO EXECUTADO pelo grupo.
    Adaptado da documentação oficial da Microsoft, conforme permitido pela
    seção 3 do enunciado.

FONTE DA ADAPTAÇÃO:
    https://learn.microsoft.com/en-us/azure/ai-services/computer-vision/overview-image-analysis
    (consultado em 23/09/2026)

DEPENDÊNCIA (declarada no bloco PEP 723 no topo do arquivo):
    azure-ai-vision-imageanalysis
    azure-core

COMO EXECUTAR:
    uv run exemplos/visao/azure_image_analysis.py
    O uv lê o bloco `# /// script` e resolve a dependência sozinho, em
    ambiente isolado e efêmero — não é preciso criar venv nem usar pip.

AUTENTICAÇÃO:
    Chave e endpoint do recurso, lidos de variáveis de ambiente.
    Nenhuma credencial neste arquivo.
        AZURE_VISION_ENDPOINT=https://<seu-recurso>.cognitiveservices.azure.com/
        AZURE_VISION_KEY=<chave do recurso>

AVISO OFICIAL:
    A documentação informa que o Image Analysis 4.0 está descontinuado e será
    encerrado em 25/09/2028.

LIMITES RELEVANTES (v4.0):
    JPEG, PNG, GIF, BMP, WEBP, ICO, TIFF ou MPO; menos de 20 MB;
    dimensões entre 50x50 e 16.000x16.000 px.
    O recurso precisa ser criado em região suportada (East US está na lista).
"""

import os

from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential

CAMINHO_IMAGEM = os.environ.get("IMAGEM_EXEMPLO", "imagem_exemplo.jpg")


def criar_cliente() -> ImageAnalysisClient:
    """Monta o cliente a partir do endpoint e da chave do recurso."""
    endpoint = os.environ["AZURE_VISION_ENDPOINT"]
    chave = os.environ["AZURE_VISION_KEY"]
    return ImageAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(chave))


def main() -> None:
    cliente = criar_cliente()

    with open(CAMINHO_IMAGEM, "rb") as arquivo:
        bytes_imagem = arquivo.read()

    # Apenas TAGS: uma única feature, para manter a carga equivalente à dos
    # outros provedores no cenário de custo.
    # --- TRECHO CITADO NO RELATÓRIO (início) ---
    resultado = cliente.analyze(
        image_data=bytes_imagem,
        visual_features=[VisualFeatures.TAGS],
    )
    # --- TRECHO CITADO NO RELATÓRIO (fim) ---

    if resultado.tags is not None:
        for tag in resultado.tags.list:
            # A confiança da Azure vem na escala 0-1.
            print(f"{tag.name}: {tag.confidence:.4f}")


if __name__ == "__main__":
    main()
