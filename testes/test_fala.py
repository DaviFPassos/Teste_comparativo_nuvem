"""Testes dos exemplos de fala para texto / transcrição em lote."""

from unittest import mock

from botocore.stub import ANY

URI_S3 = "s3://meu-bucket/audio_exemplo.flac"
URI_GCS = "gs://meu-bucket/audio_exemplo.flac"


# --------------------------------------------------------------------- AWS

def _transcribe_com_respostas(cliente_aws, monkeypatch, exemplo, estados_finais):
    """Prepara envio + consultas sucessivas; o 'sleep' vira registro, sem espera."""
    cliente, stubber = cliente_aws("transcribe")
    stubber.add_response(
        "start_transcription_job",
        {"TranscriptionJob": {"TranscriptionJobName": "x",
                              "TranscriptionJobStatus": "IN_PROGRESS"}},
        expected_params={"TranscriptionJobName": ANY, "Media": {"MediaFileUri": URI_S3},
                         "MediaFormat": "flac", "LanguageCode": "pt-BR"},
    )
    for job in estados_finais:
        stubber.add_response("get_transcription_job", {"TranscriptionJob": job},
                             expected_params={"TranscriptionJobName": ANY})
    monkeypatch.setattr(exemplo.boto3, "client", lambda servico, **kw: cliente)
    esperas = []
    monkeypatch.setattr(exemplo.time, "sleep", esperas.append)
    return stubber, esperas


def test_aws_transcribe(carregar_exemplo, cliente_aws, monkeypatch, capsys):
    exemplo = carregar_exemplo("exemplos/fala/aws_transcribe.py", TRANSCRIBE_URI_AUDIO=URI_S3)
    url = "https://s3.amazonaws.com/bucket/transcricao.json"
    stubber, esperas = _transcribe_com_respostas(cliente_aws, monkeypatch, exemplo, [
        {"TranscriptionJobName": "x", "TranscriptionJobStatus": "IN_PROGRESS"},
        {"TranscriptionJobName": "x", "TranscriptionJobStatus": "COMPLETED",
         "Transcript": {"TranscriptFileUri": url}},
    ])

    with stubber:
        exemplo.main()
    stubber.assert_no_pending_responses()

    assert esperas == [10]          # consultou, esperou uma vez, consultou de novo
    assert f"Resultado em: {url}" in capsys.readouterr().out


def test_aws_transcribe_job_com_falha(carregar_exemplo, cliente_aws, monkeypatch, capsys):
    exemplo = carregar_exemplo("exemplos/fala/aws_transcribe.py", TRANSCRIBE_URI_AUDIO=URI_S3)
    stubber, _ = _transcribe_com_respostas(cliente_aws, monkeypatch, exemplo, [
        {"TranscriptionJobName": "x", "TranscriptionJobStatus": "FAILED",
         "FailureReason": "Unsupported media format"},
    ])

    with stubber:
        exemplo.main()

    assert "Falhou: Unsupported media format" in capsys.readouterr().out


# ------------------------------------------------------------------- Azure

class RespostaHttpFalsa:
    def __init__(self, corpo):
        self._corpo = corpo

    def raise_for_status(self):
        pass

    def json(self):
        return self._corpo


def test_azure_speech(carregar_exemplo, monkeypatch, capsys):
    url_audio = "https://exemplo.blob.core.windows.net/audios/audio.wav?sv=sas"
    exemplo = carregar_exemplo("exemplos/fala/azure_speech.py",
                               AZURE_SPEECH_KEY="chave-de-teste",
                               AZURE_SPEECH_REGION="eastus",
                               AZURE_SPEECH_AUDIO_URL=url_audio)

    base = "https://eastus.api.cognitive.microsoft.com/speechtotext/v3.2/transcriptions"
    recurso = f"{base}/abc-123"
    resultado = "https://spsvcprodeus.blob.core.windows.net/resultado/contenturl_0.json"

    post = mock.Mock(return_value=RespostaHttpFalsa({"self": recurso, "status": "NotStarted"}))
    get = mock.Mock(side_effect=[
        RespostaHttpFalsa({"status": "Running"}),
        RespostaHttpFalsa({"status": "Succeeded"}),
        RespostaHttpFalsa({"values": [
            {"kind": "TranscriptionReport", "links": {"contentUrl": "https://relatorio"}},
            {"kind": "Transcription", "links": {"contentUrl": resultado}},
        ]}),
    ])
    monkeypatch.setattr(exemplo.requests, "post", post)
    monkeypatch.setattr(exemplo.requests, "get", get)
    esperas = []
    monkeypatch.setattr(exemplo.time, "sleep", esperas.append)

    exemplo.main()

    # Passo 1 — o pedido de criação vai ao endpoint e com o corpo documentados.
    args, kwargs = post.call_args
    assert args == (base,)
    assert kwargs["headers"]["Ocp-Apim-Subscription-Key"] == "chave-de-teste"
    assert kwargs["json"]["contentUrls"] == [url_audio]
    assert kwargs["json"]["locale"] == "pt-BR"

    # Passo 2 — consultou o recurso criado e respeitou o intervalo de 1 minuto.
    assert get.call_args_list[0].args == (recurso,)
    assert esperas == [60]

    # Passo 3 — buscou a lista de arquivos e escolheu só a transcrição.
    assert get.call_args_list[2].args == (f"{recurso}/files",)
    saida = capsys.readouterr().out
    assert f"Resultado em: {resultado}" in saida
    assert "https://relatorio" not in saida


# ------------------------------------------------------------------ Google

def test_google_speech_to_text(carregar_exemplo, monkeypatch, capsys):
    from google.cloud.speech_v2 import SpeechClient
    from google.cloud.speech_v2.types import cloud_speech

    exemplo = carregar_exemplo("exemplos/fala/google_speech_to_text.py",
                               GOOGLE_CLOUD_PROJECT="projeto-teste",
                               GOOGLE_CLOUD_REGION="us-central1",
                               GCS_URI_AUDIO=URI_GCS)

    ClienteFalso = mock.create_autospec(SpeechClient)
    monkeypatch.setattr(exemplo, "SpeechClient", ClienteFalso)

    # Resposta com os tipos reais do SDK, no caminho NÃO descontinuado:
    # results[uri].inline_result.transcript.results[...].alternatives[...]
    operacao = ClienteFalso.return_value.batch_recognize.return_value
    operacao.result.return_value = cloud_speech.BatchRecognizeResponse(results={
        URI_GCS: cloud_speech.BatchRecognizeFileResult(
            inline_result=cloud_speech.InlineResult(
                transcript=cloud_speech.BatchRecognizeResults(results=[
                    cloud_speech.SpeechRecognitionResult(alternatives=[
                        cloud_speech.SpeechRecognitionAlternative(
                            transcript="bom dia, em que posso ajudar", confidence=0.95),
                    ]),
                ]),
            ),
        ),
    })

    exemplo.main()

    pedido = ClienteFalso.return_value.batch_recognize.call_args.kwargs["request"]
    assert isinstance(pedido, cloud_speech.BatchRecognizeRequest)
    assert pedido.recognizer == "projects/projeto-teste/locations/us-central1/recognizers/_"
    assert list(pedido.config.language_codes) == ["pt-BR"]
    assert pedido.config.model == "long"
    assert pedido.files[0].uri == URI_GCS
    assert "inline_response_config" in pedido.recognition_output_config
    operacao.result.assert_called_once_with(timeout=600)

    assert "bom dia, em que posso ajudar (confiança 0.9500)" in capsys.readouterr().out
