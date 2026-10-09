"""
Ensaio geral do modo real, offline.

Executa as próprias funções de test_real.py — as mesmas que rodam com
`--real` na máquina de quem tem credenciais —, trocando apenas a camada de
rede de cada SDK por uma resposta no formato documentado. Assim, todo o código
do modo real (envio dos arquivos, espionagem da resposta, leitura do
resultado, gravação e limpeza da evidência) é exercitado antes da primeira
execução de verdade.

O que o ensaio NÃO substitui: a resposta real de cada serviço. Ele garante que,
recebendo a resposta no formato documentado, o modo real funciona.
"""

import json
from unittest import mock

import boto3
import pytest
from botocore.stub import ANY, Stubber

import conftest
import test_real
from conftest import AUDIO, FRASE, IMAGEM

BUCKET_S3, BUCKET_GCS = "bucket-ensaio-s3", "bucket-ensaio-gcs"
PROJETO, RECURSO = "projeto-ensaio-123", "recurso-ensaio"
URL_AWS = ("https://s3.us-east-1.amazonaws.com/aws-transcribe/job.json"
           "?X-Amz-Credential=ASIAEXEMPLO&X-Amz-Signature=abc")
URL_AZURE = "https://spsvc.blob.core.windows.net/res/contenturl_0.json?sv=2021&sig=SEGREDO"
IDENTIFICADORES = (BUCKET_S3, BUCKET_GCS, PROJETO, RECURSO, "X-Amz-Credential", "sig=SEGREDO")


@pytest.fixture
def ensaio(monkeypatch, tmp_path):
    """Credenciais fictícias para que os testes reais não sejam pulados."""
    chave = tmp_path / "adc.json"
    chave.write_text("{}")
    for nome, valor in {
        "AWS_ACCESS_KEY_ID": "ensaio", "AWS_SECRET_ACCESS_KEY": "ensaio",
        "AWS_EC2_METADATA_DISABLED": "true", "PERMITIR_AWS_PLANO_PAGO": "sim",
        "TESTE_S3_BUCKET": BUCKET_S3, "TESTE_GCS_BUCKET": BUCKET_GCS,
        "AZURE_LANGUAGE_ENDPOINT": f"https://{RECURSO}.cognitiveservices.azure.com/",
        "AZURE_LANGUAGE_KEY": "ensaio",
        "AZURE_VISION_ENDPOINT": f"https://{RECURSO}.cognitiveservices.azure.com/",
        "AZURE_VISION_KEY": "ensaio", "AZURE_SPEECH_KEY": "ensaio", "AZURE_SPEECH_REGION": "eastus",
        "GOOGLE_APPLICATION_CREDENTIALS": str(chave), "GOOGLE_CLOUD_PROJECT": PROJETO,
    }.items():
        monkeypatch.setenv(nome, valor)
    monkeypatch.setattr(conftest, "EVIDENCIAS", tmp_path / "evidencias")
    monkeypatch.setattr("time.sleep", lambda s: None)
    return tmp_path / "evidencias"


def conferir_evidencia(pasta, nome, entrada):
    """A evidência existe, está aprovada, aponta a entrada certa e não vaza nada."""
    texto = (pasta / f"{nome}.json").read_text(encoding="utf-8")
    registro = json.loads(texto)
    assert registro["aprovado"] is True
    assert registro["entrada"]["sha256"] == conftest.sha256(entrada)
    for vazamento in IDENTIFICADORES:
        assert vazamento not in texto, f"{vazamento} vazou para a evidência {nome}"
    return registro


def aws_falsa(monkeypatch, respostas):
    """boto3.client devolve clientes reais com Stubber: valida contra o modelo da AWS."""
    original = boto3.client
    criados = {}

    def fabrica(servico, **kwargs):
        if servico == "s3":
            criados["s3"] = mock.Mock()
            return criados["s3"]
        cliente = original(servico, **kwargs)
        stubber = Stubber(cliente)
        for operacao, resposta, esperado in respostas[servico]:
            stubber.add_response(operacao, resposta, esperado)
        stubber.activate()
        criados[servico] = stubber
        return cliente

    monkeypatch.setattr(boto3, "client", fabrica)
    return criados


# ===================================================================== NLP

def test_ensaio_nlp_aws(ensaio, carregar_exemplo, monkeypatch, registrar_evidencia):
    criados = aws_falsa(monkeypatch, {"comprehend": [(
        "detect_sentiment",
        {"Sentiment": "POSITIVE", "SentimentScore": {"Positive": 0.98, "Negative": 0.0,
                                                     "Neutral": 0.02, "Mixed": 0.0}},
        {"Text": FRASE.read_text(encoding="utf-8"), "LanguageCode": "pt"})]})
    test_real.test_real_nlp_aws(carregar_exemplo, monkeypatch, registrar_evidencia)
    criados["comprehend"].assert_no_pending_responses()
    assert conferir_evidencia(ensaio, "nlp_aws", FRASE)["obtido"] == "POSITIVE"


def test_ensaio_nlp_azure(ensaio, carregar_exemplo, monkeypatch, registrar_evidencia):
    import azure.ai.textanalytics as ta
    Cliente = mock.create_autospec(ta.TextAnalyticsClient)
    escores = ta.SentimentConfidenceScores(positive=0.99, neutral=0.01, negative=0.0)
    Cliente.return_value.analyze_sentiment.return_value = [ta.AnalyzeSentimentResult(
        id="0", sentiment="positive", confidence_scores=escores, is_error=False, sentences=[])]
    monkeypatch.setattr(ta, "TextAnalyticsClient", Cliente)
    chamada = Cliente.return_value.analyze_sentiment      # antes do espião substituí-la

    test_real.test_real_nlp_azure(carregar_exemplo, monkeypatch, registrar_evidencia)

    assert chamada.call_args.kwargs["documents"] == [
        FRASE.read_text(encoding="utf-8")]
    assert conferir_evidencia(ensaio, "nlp_azure", FRASE)["obtido"] == "positive"


def test_ensaio_nlp_google(ensaio, carregar_exemplo, monkeypatch, registrar_evidencia):
    from google.cloud import language_v1
    Cliente = mock.create_autospec(language_v1.LanguageServiceClient)
    Cliente.return_value.analyze_sentiment.return_value = language_v1.AnalyzeSentimentResponse(
        document_sentiment=language_v1.Sentiment(score=0.9, magnitude=0.9))
    monkeypatch.setattr(language_v1, "LanguageServiceClient", Cliente)
    chamada = Cliente.return_value.analyze_sentiment

    test_real.test_real_nlp_google(carregar_exemplo, monkeypatch, registrar_evidencia)

    pedido = chamada.call_args.kwargs["request"]
    assert pedido["document"].content == FRASE.read_text(encoding="utf-8")
    assert conferir_evidencia(ensaio, "nlp_google", FRASE)["obtido"]["classe_pelo_limiar"] == "positivo"


# =================================================================== visão

def test_ensaio_visao_aws(ensaio, carregar_exemplo, monkeypatch, registrar_evidencia):
    criados = aws_falsa(monkeypatch, {"rekognition": [(
        "detect_labels",
        {"Labels": [{"Name": "Dog", "Confidence": 99.1}, {"Name": "Labrador Retriever", "Confidence": 92.0}],
         "LabelModelVersion": "3.0"},
        {"Image": {"Bytes": IMAGEM.read_bytes()}, "MaxLabels": 10, "MinConfidence": 55.0,
         "Features": ["GENERAL_LABELS"]})]})
    test_real.test_real_visao_aws(carregar_exemplo, monkeypatch, registrar_evidencia)
    criados["rekognition"].assert_no_pending_responses()      # a foto real foi a enviada
    assert "Dog" in conferir_evidencia(ensaio, "visao_aws", IMAGEM)["obtido"]


def test_ensaio_visao_azure(ensaio, carregar_exemplo, monkeypatch, registrar_evidencia):
    import azure.ai.vision.imageanalysis as ia
    from azure.ai.vision.imageanalysis.models import DetectedTag, ImageAnalysisResult, TagsResult
    Cliente = mock.create_autospec(ia.ImageAnalysisClient)
    Cliente.return_value.analyze.return_value = ImageAnalysisResult(
        tags=TagsResult(list=[DetectedTag(name="dog", confidence=0.99), DetectedTag(name="grass", confidence=0.9)]))
    monkeypatch.setattr(ia, "ImageAnalysisClient", Cliente)
    chamada = Cliente.return_value.analyze

    test_real.test_real_visao_azure(carregar_exemplo, monkeypatch, registrar_evidencia)

    assert chamada.call_args.kwargs["image_data"] == IMAGEM.read_bytes()
    assert "dog" in conferir_evidencia(ensaio, "visao_azure", IMAGEM)["obtido"]


def test_ensaio_visao_google(ensaio, carregar_exemplo, monkeypatch, registrar_evidencia):
    from google.cloud import vision
    Cliente = mock.create_autospec(vision.ImageAnnotatorClient)
    Cliente.return_value.label_detection.return_value = vision.AnnotateImageResponse(
        label_annotations=[vision.EntityAnnotation(description="Dog", score=0.97, mid="/m/0bt9lr")])
    monkeypatch.setattr(vision, "ImageAnnotatorClient", Cliente)
    chamada = Cliente.return_value.label_detection

    test_real.test_real_visao_google(carregar_exemplo, monkeypatch, registrar_evidencia)

    assert chamada.call_args.kwargs["image"].content == IMAGEM.read_bytes()
    assert "Dog" in conferir_evidencia(ensaio, "visao_google", IMAGEM)["obtido"]


# ==================================================================== fala

class RespostaHttp:
    def __init__(self, corpo=None, status=200):
        self._corpo, self.status_code = corpo, status

    def raise_for_status(self):
        pass

    def json(self):
        return self._corpo


def test_ensaio_fala_aws(ensaio, carregar_exemplo, monkeypatch, registrar_evidencia):
    midia = {"MediaFileUri": f"s3://{BUCKET_S3}/testes/frase.flac"}
    criados = aws_falsa(monkeypatch, {"transcribe": [
        ("start_transcription_job",
         {"TranscriptionJob": {"TranscriptionJobName": "x", "TranscriptionJobStatus": "IN_PROGRESS"}},
         {"TranscriptionJobName": ANY, "Media": ANY, "MediaFormat": "flac", "LanguageCode": "pt-BR"}),
        ("get_transcription_job",
         {"TranscriptionJob": {"TranscriptionJobName": "x", "TranscriptionJobStatus": "IN_PROGRESS"}},
         {"TranscriptionJobName": ANY}),
        ("get_transcription_job",
         {"TranscriptionJob": {"TranscriptionJobName": "x", "TranscriptionJobStatus": "COMPLETED",
                               "Media": midia, "Transcript": {"TranscriptFileUri": URL_AWS}}},
         {"TranscriptionJobName": ANY}),
    ]})
    monkeypatch.setattr(test_real.requests, "get", lambda url, **k: RespostaHttp(
        {"results": {"transcripts": [{"transcript": "O atendimento foi excelente."}]}}))

    test_real.test_real_fala_aws(carregar_exemplo, monkeypatch, registrar_evidencia)

    criados["transcribe"].assert_no_pending_responses()
    envio = criados["s3"].upload_file.call_args.args
    assert envio[0] == str(AUDIO) and envio[1] == BUCKET_S3       # o áudio real foi enviado
    criados["s3"].delete_object.assert_called_once()                # e apagado depois
    conferir_evidencia(ensaio, "fala_aws", AUDIO)


def test_ensaio_fala_azure(ensaio, carregar_exemplo, monkeypatch, registrar_evidencia):
    base = "https://eastus.api.cognitive.microsoft.com/speechtotext/v3.2/transcriptions"
    recurso = f"{base}/abc"
    estados = iter(["Running", "Succeeded"])

    def get(url, **kwargs):
        if url == recurso:
            return RespostaHttp({"status": next(estados)})
        if url == f"{recurso}/files":
            return RespostaHttp({"values": [{"kind": "Transcription", "links": {"contentUrl": URL_AZURE}}]})
        if url == URL_AZURE:
            return RespostaHttp({"combinedRecognizedPhrases": [{"display": "O atendimento foi excelente."}]})
        raise AssertionError(f"GET inesperado: {url}")

    post = mock.Mock(return_value=RespostaHttp({"self": recurso}))
    monkeypatch.setattr("requests.get", get)
    monkeypatch.setattr("requests.post", post)
    monkeypatch.setattr("requests.head", lambda url, **k: RespostaHttp(status=200))

    test_real.test_real_fala_azure(carregar_exemplo, monkeypatch, registrar_evidencia)

    assert post.call_args.kwargs["json"]["contentUrls"] == [test_real.URL_PUBLICA_DO_AUDIO]
    assert post.call_args.kwargs["json"]["locale"] == "pt-BR"
    conferir_evidencia(ensaio, "fala_azure", AUDIO)


def test_ensaio_fala_google(ensaio, carregar_exemplo, monkeypatch, registrar_evidencia):
    from google.api_core import operation
    from google.cloud import speech_v2, storage
    from google.cloud.speech_v2.types import cloud_speech
    from google.longrunning import operations_pb2
    from google.protobuf import any_pb2

    # Blob/bucket falsos: registram o upload e a remoção do áudio.
    blob = mock.Mock()
    blob.bucket.name, blob.name = BUCKET_GCS, "testes/frase.flac"
    Storage = mock.Mock()
    Storage.return_value.bucket.return_value.blob.return_value = blob
    monkeypatch.setattr(storage, "Client", Storage)

    # Operação de longa duração REAL do google-api-core, já concluída: o
    # result() verdadeiro desempacota a resposta, como faria contra o serviço.
    resposta = cloud_speech.BatchRecognizeResponse(results={
        f"gs://{BUCKET_GCS}/testes/frase.flac": cloud_speech.BatchRecognizeFileResult(
            inline_result=cloud_speech.InlineResult(transcript=cloud_speech.BatchRecognizeResults(results=[
                cloud_speech.SpeechRecognitionResult(alternatives=[
                    cloud_speech.SpeechRecognitionAlternative(transcript="O atendimento foi excelente.",
                                                              confidence=0.93)])])))})
    pacote = any_pb2.Any()
    pacote.Pack(cloud_speech.BatchRecognizeResponse.pb(resposta))
    pronta = operations_pb2.Operation(name=f"projects/{PROJETO}/operations/1", done=True, response=pacote)
    Cliente = mock.create_autospec(speech_v2.SpeechClient)
    Cliente.return_value.batch_recognize.return_value = operation.Operation(
        pronta, refresh=lambda: pronta, cancel=lambda: None,
        result_type=cloud_speech.BatchRecognizeResponse)
    monkeypatch.setattr(speech_v2, "SpeechClient", Cliente)

    test_real.test_real_fala_google(carregar_exemplo, monkeypatch, registrar_evidencia)

    blob.upload_from_filename.assert_called_once_with(str(AUDIO))   # o áudio real foi enviado
    blob.delete.assert_called_once()                                 # e apagado depois
    assert Cliente.call_args.kwargs["client_options"].api_endpoint == "us-central1-speech.googleapis.com"
    pedido = Cliente.return_value.batch_recognize.call_args.kwargs["request"]
    assert pedido.config.model == "chirp_2" and list(pedido.config.language_codes) == ["pt-BR"]
    conferir_evidencia(ensaio, "fala_google", AUDIO)
