# /// script
# requires-python = ">=3.10"
# dependencies = ["google-cloud-vision"]
# ///
"""
Categoria: Visão computacional
Provedor:  Google Cloud — Cloud Vision API
Operação:  LABEL_DETECTION (via images:annotate)

ESTADO DE VALIDAÇÃO: exemplo ILUSTRATIVO, NÃO EXECUTADO pelo grupo.
    Adaptado da documentação oficial do Google Cloud, conforme permitido pela
    seção 3 do enunciado.

FONTE DA ADAPTAÇÃO:
    https://docs.cloud.google.com/vision/docs/labels
    (consultado em 23/09/2026)

DEPENDÊNCIA (declarada no bloco PEP 723 no topo do arquivo):
    google-cloud-vision

COMO EXECUTAR:
    uv run exemplos/visao/google_vision.py
    O uv lê o bloco `# /// script` e resolve a dependência sozinho, em
    ambiente isolado e efêmero — não é preciso criar venv nem usar pip.

AUTENTICAÇÃO:
    Application Default Credentials. Nenhuma credencial neste arquivo.
        GOOGLE_APPLICATION_CREDENTIALS=/caminho/para/conta-de-servico.json

LIMITES RELEVANTES:
    JPEG, PNG8, PNG24, GIF, BMP, WEBP, RAW, ICO, PDF e TIFF.
    Até 20 MB por imagem e 10 MB por requisição JSON.
    Resolução recomendada de 640x480 px para LABEL_DETECTION.
"""

import os

from google.cloud import vision

CAMINHO_IMAGEM = os.environ.get("IMAGEM_EXEMPLO", "imagem_exemplo.jpg")

# Definido explicitamente: se omitido, a API devolve 10 resultados por padrão.
MAX_RESULTADOS = 10


def detectar_rotulos(caminho: str):
    """Envia os bytes da imagem e devolve as anotações de rótulo."""
    cliente = vision.ImageAnnotatorClient()

    with open(caminho, "rb") as arquivo:
        imagem = vision.Image(content=arquivo.read())

    # --- TRECHO CITADO NO RELATÓRIO (início) ---
    resposta = cliente.label_detection(image=imagem, max_results=MAX_RESULTADOS)
    # --- TRECHO CITADO NO RELATÓRIO (fim) ---

    if resposta.error.message:
        raise RuntimeError(resposta.error.message)

    return resposta.label_annotations


def main() -> None:
    for rotulo in detectar_rotulos(CAMINHO_IMAGEM):
        # score e topicality vêm na escala 0-1; mid é o identificador do rótulo
        # no Google Knowledge Graph, algo que os outros dois não fornecem.
        print(f"{rotulo.description}: score {rotulo.score:.4f} "
              f"| topicality {rotulo.topicality:.4f} | mid {rotulo.mid}")


if __name__ == "__main__":
    main()
