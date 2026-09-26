# /// script
# requires-python = ">=3.10"
# dependencies = ["boto3"]
# ///
"""
Categoria: Fala para texto
Provedor:  AWS — Amazon Transcribe
Operação:  StartTranscriptionJob (transcrição em lote / assíncrona)

ESTADO DE VALIDAÇÃO: exemplo ILUSTRATIVO, NÃO EXECUTADO pelo grupo.
    Adaptado da documentação oficial da AWS, conforme permitido pela seção 3
    do enunciado.

FONTES DA ADAPTAÇÃO (consultadas em 23/09/2026):
    https://docs.aws.amazon.com/transcribe/latest/dg/how-it-works.html
    https://docs.aws.amazon.com/transcribe/latest/dg/how-input.html

DEPENDÊNCIA (declarada no bloco PEP 723 no topo do arquivo):
    boto3

COMO EXECUTAR:
    uv run exemplos/fala/aws_transcribe.py
    O uv lê o bloco `# /// script` e resolve a dependência sozinho, em
    ambiente isolado e efêmero — não é preciso criar venv nem usar pip.

AUTENTICAÇÃO:
    Credenciais IAM pela cadeia padrão do SDK, com permissão de leitura no
    bucket de origem. Nenhuma credencial neste arquivo.

LIMITES RELEVANTES:
    O arquivo precisa estar em um bucket do Amazon S3 (não há upload direto).
    Formatos em lote: AMR, FLAC, M4A, MP3, MP4, Ogg, WebM e WAV.
    Recomendados: FLAC ou WAV com PCM 16 bits. Máximo de dois canais de áudio.
    Se o bucket de saída for o padrão do serviço, a URI é válida por 15 minutos
    e o resultado é apagado quando o job expira (90 dias).
"""

import os
import time
import uuid

import boto3

REGIAO = os.environ.get("AWS_REGION", "us-east-1")

# Áudio de exemplo já enviado ao S3, no formato s3://bucket/chave.
URI_AUDIO = os.environ.get("TRANSCRIBE_URI_AUDIO", "s3://meu-bucket/audio_exemplo.flac")

IDIOMA = "pt-BR"  # Português brasileiro, suportado em lote e em streaming

INTERVALO_CONSULTA_S = 10


def iniciar_job(cliente, nome_job: str) -> None:
    """Passo 1 — envio: cria o job assíncrono de transcrição."""
    # --- TRECHO CITADO NO RELATÓRIO (início) ---
    cliente.start_transcription_job(
        TranscriptionJobName=nome_job,
        Media={"MediaFileUri": URI_AUDIO},
        MediaFormat="flac",
        LanguageCode=IDIOMA,
    )
    # --- TRECHO CITADO NO RELATÓRIO (fim) ---


def aguardar_conclusao(cliente, nome_job: str) -> dict:
    """Passo 2 — acompanhamento: consulta o job até concluir ou falhar."""
    while True:
        resposta = cliente.get_transcription_job(TranscriptionJobName=nome_job)
        situacao = resposta["TranscriptionJob"]["TranscriptionJobStatus"]

        if situacao in ("COMPLETED", "FAILED"):
            return resposta["TranscriptionJob"]

        print(f"job {nome_job}: {situacao}")
        time.sleep(INTERVALO_CONSULTA_S)


def main() -> None:
    cliente = boto3.client("transcribe", region_name=REGIAO)
    nome_job = f"transcricao-exemplo-{uuid.uuid4().hex[:8]}"

    iniciar_job(cliente, nome_job)
    job = aguardar_conclusao(cliente, nome_job)

    if job["TranscriptionJobStatus"] == "FAILED":
        print("Falhou:", job.get("FailureReason"))
        return

    # Passo 3 — obtenção: a URI aponta para o JSON com a transcrição.
    # No bucket padrão do serviço, essa URI expira em 15 minutos.
    print("Resultado em:", job["Transcript"]["TranscriptFileUri"])


if __name__ == "__main__":
    main()
