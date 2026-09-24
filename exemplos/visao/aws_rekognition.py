# /// script
# requires-python = ">=3.10"
# dependencies = ["boto3"]
# ///
"""
Categoria: Visão computacional
Provedor:  AWS — Amazon Rekognition
Operação:  DetectLabels (síncrona, uma imagem por chamada)

ESTADO DE VALIDAÇÃO: exemplo ILUSTRATIVO, NÃO EXECUTADO pelo grupo.
    Adaptado da documentação oficial da AWS, conforme permitido pela seção 3
    do enunciado.

FONTE DA ADAPTAÇÃO:
    https://docs.aws.amazon.com/rekognition/latest/dg/labels-detect-labels-image.html
    (consultado em 23/09/2026)

DEPENDÊNCIA (declarada no bloco PEP 723 no topo do arquivo):
    boto3

COMO EXECUTAR:
    uv run exemplos/visao/aws_rekognition.py
    O uv lê o bloco `# /// script` e resolve a dependência sozinho, em
    ambiente isolado e efêmero — não é preciso criar venv nem usar pip.

AUTENTICAÇÃO:
    Credenciais IAM pela cadeia padrão do SDK. Nenhuma credencial neste arquivo.

LIMITES RELEVANTES:
    Apenas PNG e JPEG. Até 5 MB quando enviada como bytes na requisição e até
    15 MB como objeto no Amazon S3. Máximo de 10.000 px de largura e altura.
"""

import os

import boto3

CAMINHO_IMAGEM = os.environ.get("IMAGEM_EXEMPLO", "imagem_exemplo.jpg")
REGIAO = os.environ.get("AWS_REGION", "us-east-1")

# Definidos explicitamente para não depender de valores padrão do serviço.
MAX_LABELS = 10
MIN_CONFIANCA = 55.0  # a escala da AWS vai de 0 a 100, não de 0 a 1


def detectar_rotulos(caminho: str) -> dict:
    """Envia os bytes da imagem e devolve a resposta completa do DetectLabels."""
    cliente = boto3.client("rekognition", region_name=REGIAO)

    with open(caminho, "rb") as arquivo:
        bytes_imagem = arquivo.read()

    return cliente.detect_labels(
        Image={"Bytes": bytes_imagem},
        MaxLabels=MAX_LABELS,
        MinConfidence=MIN_CONFIANCA,
        Features=["GENERAL_LABELS"],
    )


def main() -> None:
    resposta = detectar_rotulos(CAMINHO_IMAGEM)

    print("Versão do modelo:", resposta.get("LabelModelVersion"))
    for rotulo in resposta["Labels"]:
        # Confidence vem na escala 0-100.
        print(f"{rotulo['Name']}: {rotulo['Confidence']:.2f}")

        # A AWS é a única das três que devolve a taxonomia do rótulo.
        pais = [p["Name"] for p in rotulo.get("Parents", [])]
        categorias = [c["Name"] for c in rotulo.get("Categories", [])]
        if pais:
            print("   rótulos-pai:", ", ".join(pais))
        if categorias:
            print("   categorias: ", ", ".join(categorias))


if __name__ == "__main__":
    main()
