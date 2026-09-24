# /// script
# requires-python = ">=3.10"
# dependencies = ["azure-ai-textanalytics", "azure-core"]
# ///
"""
Categoria: NLP / análise de texto
Provedor:  Microsoft Azure — Azure Language in Foundry Tools
           (nome anterior: Azure AI Language / Text Analytics)
Operação:  Análise de sentimento (nível de documento e de sentença)

ESTADO DE VALIDAÇÃO: exemplo ILUSTRATIVO, NÃO EXECUTADO pelo grupo.
    Adaptado da documentação oficial da Microsoft. A seção 3 do enunciado
    permite explicitamente que os exemplos da Etapa 1 não sejam executados.

FONTE DA ADAPTAÇÃO:
    https://learn.microsoft.com/en-us/azure/ai-services/language-service/sentiment-opinion-mining/overview
    (consultado em 23/09/2026)

DEPENDÊNCIA (declarada no bloco PEP 723 no topo do arquivo):
    azure-ai-textanalytics
    azure-core

COMO EXECUTAR:
    uv run exemplos/nlp/azure_language.py
    O uv lê o bloco `# /// script` e resolve a dependência sozinho, em
    ambiente isolado e efêmero — não é preciso criar venv nem usar pip.

AUTENTICAÇÃO:
    Chave e endpoint do recurso, lidos de variáveis de ambiente.
    Nenhuma credencial é escrita neste arquivo.
        AZURE_LANGUAGE_ENDPOINT=https://<seu-recurso>.cognitiveservices.azure.com/
        AZURE_LANGUAGE_KEY=<chave do recurso>

AVISO OFICIAL:
    A documentação informa que a análise de sentimento e o opinion mining
    serão encerrados no Azure Language em 31/03/2029, com migração
    recomendada para o Microsoft Foundry.

LIMITES RELEVANTES:
    5.120 caracteres por documento (síncrono); 10 documentos por requisição.
"""

import os

from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

# Mesmo texto usado nos três provedores, para permitir comparação direta.
TEXTO = "O atendimento foi excelente."
IDIOMA = "pt-BR"  # a Azure é a única das três que distingue pt-BR de pt-PT


def criar_cliente() -> TextAnalyticsClient:
    """Monta o cliente a partir do endpoint e da chave do recurso."""
    endpoint = os.environ["AZURE_LANGUAGE_ENDPOINT"]
    chave = os.environ["AZURE_LANGUAGE_KEY"]
    return TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(chave))


def main() -> None:
    cliente = criar_cliente()

    # A API recebe uma LISTA de documentos, mesmo para um único texto.
    resultados = cliente.analyze_sentiment(documents=[TEXTO], language=IDIOMA)

    for documento in resultados:
        if documento.is_error:
            print("Erro:", documento.error)
            continue

        # Rótulo do documento: positive, neutral ou negative.
        print("Classe do documento:", documento.sentiment)
        print(f"  positive: {documento.confidence_scores.positive:.4f}")
        print(f"  neutral:  {documento.confidence_scores.neutral:.4f}")
        print(f"  negative: {documento.confidence_scores.negative:.4f}")

        # A resposta traz também o sentimento de cada sentença.
        for i, sentenca in enumerate(documento.sentences, start=1):
            print(f"  sentença {i}: {sentenca.sentiment} — {sentenca.text}")


if __name__ == "__main__":
    main()
