# /// script
# requires-python = ">=3.10"
# dependencies = ["boto3"]
# ///
"""
Categoria: NLP / análise de texto
Provedor:  AWS — Amazon Comprehend
Operação:  DetectSentiment (síncrona, um documento por chamada)

ESTADO DE VALIDAÇÃO: exemplo ILUSTRATIVO, NÃO EXECUTADO pelo grupo.
    Adaptado da documentação oficial da AWS. A seção 3 do enunciado permite
    explicitamente que os exemplos da Etapa 1 não sejam executados.

FONTE DA ADAPTAÇÃO:
    https://docs.aws.amazon.com/comprehend/latest/dg/how-sentiment.html
    (consultado em 23/09/2026)

DEPENDÊNCIA (declarada no bloco PEP 723 no topo do arquivo):
    boto3

COMO EXECUTAR:
    uv run exemplos/nlp/aws_comprehend.py
    O uv lê o bloco `# /// script` e resolve a dependência sozinho, em
    ambiente isolado e efêmero — não é preciso criar venv nem usar pip.

AUTENTICAÇÃO:
    Credenciais IAM resolvidas pela cadeia padrão do SDK (variáveis de ambiente
    AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY, perfil ~/.aws/credentials ou role).
    Nenhuma credencial é escrita neste arquivo.

LIMITE RELEVANTE:
    Documento de até 5 KB (UTF-8) na operação síncrona de sentimento.
"""

import os

import boto3

# Mesmo texto usado nos três provedores, para permitir comparação direta.
TEXTO = "O atendimento foi excelente."
IDIOMA = "pt"  # o Comprehend não distingue pt-BR de pt-PT

# Região de referência adotada no trabalho.
REGIAO = os.environ.get("AWS_REGION", "us-east-1")


# --- TRECHO CITADO NO RELATÓRIO (início) ---
def detectar_sentimento(texto: str, idioma: str = IDIOMA) -> dict:
    """Envia um documento e devolve a resposta completa do DetectSentiment."""
    cliente = boto3.client("comprehend", region_name=REGIAO)
    return cliente.detect_sentiment(Text=texto, LanguageCode=idioma)
# --- TRECHO CITADO NO RELATÓRIO (fim) ---


def main() -> None:
    resposta = detectar_sentimento(TEXTO)

    # Sentiment: uma classe entre POSITIVE, NEGATIVE, NEUTRAL e MIXED.
    print("Classe:", resposta["Sentiment"])

    # SentimentScore: um score para CADA uma das quatro classes (somam ~1,0).
    for classe, score in resposta["SentimentScore"].items():
        print(f"  {classe}: {score:.4f}")


if __name__ == "__main__":
    main()
