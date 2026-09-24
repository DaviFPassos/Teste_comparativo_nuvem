# /// script
# requires-python = ">=3.10"
# dependencies = ["requests"]
# ///
"""
Categoria: Fala para texto
Provedor:  Microsoft Azure — Azure Speech in Foundry Tools
Operação:  Transcription_Create (transcrição em lote, Speech to text REST API)

ESTADO DE VALIDAÇÃO: exemplo ILUSTRATIVO, NÃO EXECUTADO pelo grupo.
    Adaptado da documentação oficial da Microsoft, conforme permitido pela
    seção 3 do enunciado.

FONTES DA ADAPTAÇÃO (consultadas em 23/09/2026):
    https://learn.microsoft.com/en-us/azure/ai-services/speech-service/batch-transcription
    https://learn.microsoft.com/en-us/azure/ai-services/speech-service/batch-transcription-audio-data

DEPENDÊNCIA (declarada no bloco PEP 723 no topo do arquivo):
    requests

COMO EXECUTAR:
    uv run exemplos/fala/azure_speech.py
    O uv lê o bloco `# /// script` e resolve a dependência sozinho, em
    ambiente isolado e efêmero — não é preciso criar venv nem usar pip.

AUTENTICAÇÃO:
    Chave e região do recurso de Speech, lidas de variáveis de ambiente.
    Nenhuma credencial neste arquivo.
        AZURE_SPEECH_KEY=<chave do recurso>
        AZURE_SPEECH_REGION=eastus
        AZURE_SPEECH_AUDIO_URL=<URI público ou SAS do arquivo de áudio>

LIMITES E COMPORTAMENTO RELEVANTES:
    Formatos aceitos: WAV, MP3, OPUS/OGG, FLAC, WMA, AAC, ALAW e MULAW em
    contêiner WAV, AMR, WebM e SPEEX. Recomendados: WAV (PCM) e FLAC.
    O agendamento é best-effort: em horário de pico o job pode levar até 30
    minutos para iniciar e até 24 horas para concluir (p90 abaixo de 6 horas).
    A documentação recomenda consultar o status no máximo uma vez por minuto.
"""

import os
import time

import requests

CHAVE = os.environ["AZURE_SPEECH_KEY"]
REGIAO = os.environ.get("AZURE_SPEECH_REGION", "eastus")

# URI público ou com SAS. Alternativamente, usa-se contentContainerUrl para
# transcrever um contêiner inteiro do Azure Blob Storage.
URL_AUDIO = os.environ["AZURE_SPEECH_AUDIO_URL"]

IDIOMA = "pt-BR"

BASE = f"https://{REGIAO}.api.cognitive.microsoft.com/speechtotext/v3.2/transcriptions"
CABECALHOS = {"Ocp-Apim-Subscription-Key": CHAVE, "Content-Type": "application/json"}

# A documentação desaconselha polling mais frequente que 1x por minuto.
INTERVALO_CONSULTA_S = 60


def criar_transcricao() -> str:
    """Passo 1 — envio: cria a transcrição e devolve a URL do recurso criado."""
    corpo = {
        "contentUrls": [URL_AUDIO],
        "locale": IDIOMA,
        "displayName": "transcricao-exemplo-etapa1",
        "properties": {"wordLevelTimestampsEnabled": True},
    }
    resposta = requests.post(BASE, headers=CABECALHOS, json=corpo, timeout=30)
    resposta.raise_for_status()
    return resposta.json()["self"]


def aguardar_conclusao(url_transcricao: str) -> dict:
    """Passo 2 — acompanhamento: consulta até o job sair do estado em execução."""
    while True:
        resposta = requests.get(url_transcricao, headers=CABECALHOS, timeout=30)
        resposta.raise_for_status()
        corpo = resposta.json()
        situacao = corpo["status"]

        if situacao in ("Succeeded", "Failed"):
            return corpo

        print(f"status: {situacao}")
        time.sleep(INTERVALO_CONSULTA_S)


def main() -> None:
    url_transcricao = criar_transcricao()
    resultado = aguardar_conclusao(url_transcricao)

    if resultado["status"] == "Failed":
        print("Falhou:", resultado.get("properties", {}).get("error"))
        return

    # Passo 3 — obtenção: os arquivos de resultado são listados à parte.
    arquivos = requests.get(
        f"{url_transcricao}/files", headers=CABECALHOS, timeout=30
    ).json()

    for arquivo in arquivos.get("values", []):
        if arquivo["kind"] == "Transcription":
            print("Resultado em:", arquivo["links"]["contentUrl"])


if __name__ == "__main__":
    main()
