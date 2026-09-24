# /// script
# requires-python = ">=3.10"
# dependencies = ["google-cloud-speech"]
# ///
"""
Categoria: Fala para texto
Provedor:  Google Cloud — Cloud Speech-to-Text V2
Operação:  BatchRecognize (transcrição em lote / assíncrona)

ESTADO DE VALIDAÇÃO: exemplo ILUSTRATIVO, NÃO EXECUTADO pelo grupo.
    Adaptado da documentação oficial do Google Cloud, conforme permitido pela
    seção 3 do enunciado.

FONTES DA ADAPTAÇÃO (consultadas em 23/09/2026):
    https://docs.cloud.google.com/speech-to-text/v2/docs/transcription-model
    https://docs.cloud.google.com/speech-to-text/v2/docs/speech-to-text-supported-languages

DEPENDÊNCIA (declarada no bloco PEP 723 no topo do arquivo):
    google-cloud-speech

COMO EXECUTAR:
    uv run exemplos/fala/google_speech_to_text.py
    O uv lê o bloco `# /// script` e resolve a dependência sozinho, em
    ambiente isolado e efêmero — não é preciso criar venv nem usar pip.

AUTENTICAÇÃO:
    Application Default Credentials. Nenhuma credencial neste arquivo.
        GOOGLE_APPLICATION_CREDENTIALS=/caminho/para/conta-de-servico.json

PARTICULARIDADE DESTE PROVEDOR:
    É o único dos três que expõe a ESCOLHA DO MODELO na operação comparada.
    Para pt-BR estão documentados os modelos chirp_3, long, short, telephony e
    telephony_short. Usamos 'long', adequado a arquivos de áudio longos.
    O modelo chirp_3 acrescenta diarização (separação de locutores).
"""

import os

from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech

PROJETO = os.environ["GOOGLE_CLOUD_PROJECT"]
REGIAO = os.environ.get("GOOGLE_CLOUD_REGION", "us-central1")

# BatchRecognize lê o áudio do Cloud Storage.
URI_AUDIO = os.environ.get("GCS_URI_AUDIO", "gs://meu-bucket/audio_exemplo.flac")

IDIOMA = "pt-BR"
MODELO = "long"

TEMPO_LIMITE_S = 600


def main() -> None:
    cliente = SpeechClient()
    reconhecedor = f"projects/{PROJETO}/locations/{REGIAO}/recognizers/_"

    config = cloud_speech.RecognitionConfig(
        auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
        language_codes=[IDIOMA],
        model=MODELO,
    )

    # Passo 1 — envio: BatchRecognize devolve uma operação de longa duração.
    requisicao = cloud_speech.BatchRecognizeRequest(
        recognizer=reconhecedor,
        config=config,
        files=[cloud_speech.BatchRecognizeFileMetadata(uri=URI_AUDIO)],
        recognition_output_config=cloud_speech.RecognitionOutputConfig(
            inline_response_config=cloud_speech.InlineOutputConfig(),
        ),
    )

    operacao = cliente.batch_recognize(request=requisicao)

    # Passo 2 — acompanhamento: aguarda a operação concluir.
    print("Aguardando a conclusão da operação em lote...")
    resposta = operacao.result(timeout=TEMPO_LIMITE_S)

    # Passo 3 — obtenção: lê a transcrição de cada arquivo enviado.
    for uri, resultado in resposta.results.items():
        print(f"\nArquivo: {uri}")
        for trecho in resultado.transcript.results:
            if trecho.alternatives:
                alternativa = trecho.alternatives[0]
                print(f"  {alternativa.transcript} (confiança {alternativa.confidence:.4f})")


if __name__ == "__main__":
    main()
