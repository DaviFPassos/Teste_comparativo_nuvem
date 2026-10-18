import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
from dotenv import load_dotenv

load_dotenv()

def analisar_sentimento_azure(texto: str) -> dict:
    key = os.environ.get("AZURE_LANGUAGE_KEY")
    endpoint = os.environ.get("AZURE_LANGUAGE_ENDPOINT")

    if not key or not endpoint:
        raise ValueError("Credenciais da Azure não encontradas no .env")

    credential = AzureKeyCredential(key)
    client = TextAnalyticsClient(endpoint=endpoint, credential=credential)
    
    try:
        resposta = client.analyze_sentiment([texto], language="pt-br")
        doc = resposta[0]
        if doc.is_error:
            return {"sucesso": False, "erro": str(doc.error)}
        return {
            "sucesso": True,
            "sentimento": doc.sentiment, 
            "scores": {
                "positivo": doc.confidence_scores.positive,
                "neutro": doc.confidence_scores.neutral,
                "negativo": doc.confidence_scores.negative
            }
        }
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}

if __name__ == "__main__":
    print(analisar_sentimento_azure("O atendimento foi excelente."))
