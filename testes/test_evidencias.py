"""
Confere, offline, o registro de evidências dos testes reais.

As evidências vão para um repositório público. A AWS devolve URLs
pré-assinadas e a Azure URLs com token SAS — em ambos os casos a credencial
temporária viaja na query string. Este teste garante que ela é removida.
"""

import json


def test_url_pre_assinada_da_aws_perde_a_credencial():
    from conftest import _sanitizar
    url = ("https://s3.us-east-1.amazonaws.com/aws-transcribe/job.json"
           "?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=ASIAEXEMPLO%2F20261008"
           "&X-Amz-Signature=abc123")
    limpa = _sanitizar({"Transcript": {"TranscriptFileUri": url}})
    texto = json.dumps(limpa)
    assert "X-Amz-Credential" not in texto and "X-Amz-Signature" not in texto
    assert texto.count("aws-transcribe/job.json") == 1


def test_url_com_token_sas_da_azure_perde_o_token():
    from conftest import _sanitizar
    url = "https://spsvc.blob.core.windows.net/res/contenturl_0.json?sv=2021&sig=SEGREDO"
    assert "sig=" not in json.dumps(_sanitizar({"links": {"contentUrl": url}}))


def test_metadados_http_da_aws_nao_vao_para_a_evidencia():
    from conftest import _sanitizar
    resposta = {"Sentiment": "POSITIVE", "ResponseMetadata": {"HTTPHeaders": {"x": "y"}}}
    assert _sanitizar(resposta) == {"Sentiment": "POSITIVE"}


def test_respostas_dos_tres_sdks_viram_json(tmp_path, monkeypatch, registrar_evidencia):
    """Tipos reais de cada SDK precisam ser serializáveis na evidência."""
    import conftest
    from azure.ai.textanalytics import AnalyzeSentimentResult, SentimentConfidenceScores
    from azure.ai.vision.imageanalysis.models import DetectedTag, ImageAnalysisResult, TagsResult
    from google.cloud import language_v1

    monkeypatch.setattr(conftest, "EVIDENCIAS", tmp_path)
    respostas = {
        "aws": {"Sentiment": "POSITIVE", "SentimentScore": {"Positive": 0.9}},
        "azure_texto": [AnalyzeSentimentResult(
            id="0", sentiment="positive", is_error=False, sentences=[],
            confidence_scores=SentimentConfidenceScores(positive=0.9, neutral=0.05, negative=0.05))],
        "azure_imagem": ImageAnalysisResult(tags=TagsResult(list=[DetectedTag(name="dog", confidence=0.99)])),
        "google": language_v1.AnalyzeSentimentResponse(
            document_sentiment=language_v1.Sentiment(score=0.9, magnitude=0.9)),
    }
    for nome, resposta in respostas.items():
        destino = registrar_evidencia(categoria="teste", provedor=nome, servico="s", regiao="r",
                                      entrada=conftest.FRASE, resposta=resposta,
                                      obtido="x", esperado="x", aprovado=True)
        registro = json.loads(destino.read_text(encoding="utf-8"))
        assert registro["entrada"]["sha256"] == conftest.sha256(conftest.FRASE)
        assert "<" not in json.dumps(registro["resposta_bruta_do_servico"])[:1], nome
        assert registro["resposta_bruta_do_servico"], nome
    assert "dog" in json.dumps(json.loads((tmp_path / "teste_azure_imagem.json").read_text()))
    assert "positive" in (tmp_path / "teste_azure_texto.json").read_text()
    assert "0.9" in (tmp_path / "teste_google.json").read_text()


def test_identificadores_da_conta_nao_vao_para_a_evidencia(monkeypatch):
    """Bucket, projeto, conta AWS e recurso Azure saem; o resultado fica."""
    from conftest import _sanitizar
    monkeypatch.setenv("TESTE_S3_BUCKET", "bucket-do-davi")
    monkeypatch.setenv("TESTE_GCS_BUCKET", "bucket-gcs-do-davi")
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "projeto-pessoal-123")
    monkeypatch.setenv("AZURE_VISION_ENDPOINT", "https://meu-recurso-visao.cognitiveservices.azure.com/")
    resposta = {
        "Media": {"MediaFileUri": "s3://bucket-do-davi/testes/frase.flac"},
        "arquivo": "gs://bucket-gcs-do-davi/testes/frase.flac",
        "reconhecedor": "projects/projeto-pessoal-123/locations/us-central1/recognizers/_",
        "arn": "arn:aws:transcribe:us-east-1:123456789012:transcription-job/x",
        "self": "https://meu-recurso-visao.cognitiveservices.azure.com/vision/x",
        "Sentiment": "POSITIVE",
    }
    texto = json.dumps(_sanitizar(resposta))
    for vazamento in ("bucket-do-davi", "bucket-gcs-do-davi", "projeto-pessoal-123",
                      "123456789012", "meu-recurso-visao"):
        assert vazamento not in texto, vazamento
    assert "POSITIVE" in texto and "us-central1" in texto


def test_identificador_usado_como_chave_tambem_sai(monkeypatch):
    """O Google indexa o resultado do lote pela URI do arquivo no bucket."""
    from conftest import _sanitizar
    monkeypatch.setenv("TESTE_GCS_BUCKET", "bucket-gcs-do-davi")
    resposta = {"results": {"gs://bucket-gcs-do-davi/testes/frase.flac": {"transcricao": "ok"}}}
    texto = json.dumps(_sanitizar(resposta))
    assert "bucket-gcs-do-davi" not in texto and '"transcricao": "ok"' in texto
