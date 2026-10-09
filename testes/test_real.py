"""
Testes contra os serviços REAIS — só rodam com:  uv run testes/rodar_testes.py --real

Cada teste envia o arquivo de testes/dados/ ao serviço de verdade, executando o
main() do próprio exemplo, sem nada simulado. Uma "escuta" registra a resposta
bruta que o SDK recebeu. A resposta é conferida contra testes/dados/gabarito.json
e gravada em testes/evidencias/ — inclusive quando o resultado NÃO bate com o
gabarito, porque evidência que só registra sucesso não prova nada.

Provedor sem credencial configurada aparece como SKIPPED, com o motivo.
Custo: todas as chamadas cabem nas franquias gratuitas, exceto a transcrição em
lote da Azure (exige tier S0) e a do Google (sem franquia na V2): ambas custam
frações de centavo para 2,5 s de áudio.
"""

import os
import re
import unicodedata
import uuid
from pathlib import Path

import pytest
import requests

from conftest import AUDIO, FRASE, GABARITO, IMAGEM

pytestmark = pytest.mark.real

TEXTO = FRASE.read_text(encoding="utf-8")
URL_PUBLICA_DO_AUDIO = ("https://raw.githubusercontent.com/DaviFPassos/"
                        "Teste_comparativo_nuvem/main/testes/dados/frase.flac")


# ----------------------------------------------------------------- apoio

def exigir_variaveis(*nomes):
    faltando = [n for n in nomes if not os.environ.get(n)]
    if faltando:
        pytest.skip(f"faltam variáveis de ambiente: {', '.join(faltando)}")


def exigir_aws():
    # Fora de uma VM da AWS, procurar credenciais no serviço de metadados só gasta tempo.
    os.environ.setdefault("AWS_EC2_METADATA_DISABLED", "true")
    import boto3
    if boto3.Session().get_credentials() is None:
        pytest.skip("sem credenciais da AWS (configure com 'aws configure' ou AWS_ACCESS_KEY_ID)")


def exigir_aws_plano_pago(servico):
    """
    Comprehend e Transcribe NÃO estão no plano gratuito da AWS (o Transcribe só
    existe no plano pago; o Comprehend nem consta da lista do novo cadastro).
    Usá-los exige converter a conta para o plano pago, o que passa a permitir
    cobrança no cartão. Por isso ficam desligados, a menos que o dono da conta
    decida o contrário de forma explícita.
    """
    if os.environ.get("PERMITIR_AWS_PLANO_PAGO") != "sim":
        pytest.skip(f"{servico} não existe no plano gratuito da AWS; exige plano pago "
                    "(que permite cobrança). Para rodar mesmo assim: PERMITIR_AWS_PLANO_PAGO=sim")


def exigir_google():
    """
    Confere se há credencial do Google sem chamar google.auth.default(), que fora
    de uma VM do Google gasta ~12 s sondando o servidor de metadados.
    """
    from google.auth import _cloud_sdk
    arquivo = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if arquivo and not Path(arquivo).is_file():
        pytest.skip(f"GOOGLE_APPLICATION_CREDENTIALS aponta para arquivo inexistente: {arquivo}")
    if not arquivo and not Path(_cloud_sdk.get_application_default_credentials_path()).is_file():
        pytest.skip("sem credenciais do Google (GOOGLE_APPLICATION_CREDENTIALS ou "
                    "'gcloud auth application-default login')")


def espiar(objeto, metodo, capturas):
    """Deixa a chamada real acontecer e guarda o que o serviço respondeu."""
    original = getattr(objeto, metodo)

    def espiao(*args, **kwargs):
        resposta = original(*args, **kwargs)
        capturas.append(resposta)
        return resposta

    setattr(objeto, metodo, espiao)


def boto3_espionado(monkeypatch, exemplo, metodo, capturas):
    original = exemplo.boto3.client

    def fabrica(*args, **kwargs):
        cliente = original(*args, **kwargs)
        espiar(cliente, metodo, capturas)
        return cliente

    monkeypatch.setattr(exemplo.boto3, "client", fabrica)


def classe_espionada(monkeypatch, alvo, nome_classe, metodo, capturas):
    Original = getattr(alvo, nome_classe)

    def fabrica(*args, **kwargs):
        cliente = Original(*args, **kwargs)
        espiar(cliente, metodo, capturas)
        return cliente

    monkeypatch.setattr(alvo, nome_classe, fabrica)


def normalizar(texto):
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z ]", " ", sem_acento.lower())


def tem_cachorro(rotulos):
    return any("dog" in r.lower() for r in rotulos)


def transcricao_confere(transcricao):
    texto = normalizar(transcricao)
    return all(p in texto.split() for p in GABARITO["audio"]["palavras_chave"])


# ===================================================================== NLP

def test_real_nlp_aws(carregar_exemplo, monkeypatch, registrar_evidencia):
    exigir_aws_plano_pago("Amazon Comprehend")
    exigir_aws()
    exemplo = carregar_exemplo("exemplos/nlp/aws_comprehend.py")
    capturas = []
    boto3_espionado(monkeypatch, exemplo, "detect_sentiment", capturas)

    exemplo.main()

    obtido = capturas[0]["Sentiment"]
    aprovado = obtido == "POSITIVE"
    registrar_evidencia(categoria="nlp", provedor="aws", servico="Amazon Comprehend DetectSentiment",
                        regiao=exemplo.REGIAO, entrada=FRASE, resposta=capturas[0],
                        obtido=obtido, esperado=GABARITO["texto"]["criterio"]["aws"],
                        aprovado=aprovado)
    assert aprovado, f"esperado POSITIVE, o serviço respondeu {obtido}"


def test_real_nlp_azure(carregar_exemplo, monkeypatch, registrar_evidencia):
    exigir_variaveis("AZURE_LANGUAGE_ENDPOINT", "AZURE_LANGUAGE_KEY")
    exemplo = carregar_exemplo("exemplos/nlp/azure_language.py")
    capturas = []
    classe_espionada(monkeypatch, exemplo, "TextAnalyticsClient", "analyze_sentiment", capturas)

    exemplo.main()

    documento = capturas[0][0]
    obtido = documento.sentiment
    aprovado = obtido == "positive"
    registrar_evidencia(categoria="nlp", provedor="azure", servico="Azure Language — sentiment analysis",
                        regiao=os.environ.get("AZURE_REGIAO", "eastus"), entrada=FRASE,
                        resposta=list(capturas[0]), obtido=obtido,
                        esperado=GABARITO["texto"]["criterio"]["azure"], aprovado=aprovado)
    assert aprovado, f"esperado positive, o serviço respondeu {obtido}"


def test_real_nlp_google(carregar_exemplo, monkeypatch, registrar_evidencia):
    exigir_google()
    exemplo = carregar_exemplo("exemplos/nlp/google_natural_language.py")
    capturas = []
    classe_espionada(monkeypatch, exemplo.language_v1, "LanguageServiceClient",
                     "analyze_sentiment", capturas)

    exemplo.main()

    score = capturas[0].document_sentiment.score
    aprovado = exemplo.classificar(score) == "positivo"
    registrar_evidencia(categoria="nlp", provedor="google", servico="Cloud Natural Language analyzeSentiment",
                        regiao="global", entrada=FRASE, resposta=capturas[0],
                        obtido={"score": score, "classe_pelo_limiar": exemplo.classificar(score)},
                        esperado=GABARITO["texto"]["criterio"]["google"], aprovado=aprovado)
    assert aprovado, f"esperado score > 0.25, o serviço respondeu {score}"


# =================================================================== visão

def test_real_visao_aws(carregar_exemplo, monkeypatch, registrar_evidencia):
    exigir_aws()
    exemplo = carregar_exemplo("exemplos/visao/aws_rekognition.py", IMAGEM_EXEMPLO=str(IMAGEM))
    capturas = []
    boto3_espionado(monkeypatch, exemplo, "detect_labels", capturas)

    exemplo.main()

    rotulos = [r["Name"] for r in capturas[0]["Labels"]]
    aprovado = tem_cachorro(rotulos)
    registrar_evidencia(categoria="visao", provedor="aws", servico="Amazon Rekognition DetectLabels",
                        regiao=exemplo.REGIAO, entrada=IMAGEM, resposta=capturas[0],
                        obtido=rotulos, esperado=GABARITO["imagem"]["criterio"], aprovado=aprovado)
    assert aprovado, f"nenhum rótulo de cachorro em {rotulos}"


def test_real_visao_azure(carregar_exemplo, monkeypatch, registrar_evidencia):
    exigir_variaveis("AZURE_VISION_ENDPOINT", "AZURE_VISION_KEY")
    exemplo = carregar_exemplo("exemplos/visao/azure_image_analysis.py", IMAGEM_EXEMPLO=str(IMAGEM))
    capturas = []
    classe_espionada(monkeypatch, exemplo, "ImageAnalysisClient", "analyze", capturas)

    exemplo.main()

    rotulos = [t.name for t in capturas[0].tags.list]
    aprovado = tem_cachorro(rotulos)
    registrar_evidencia(categoria="visao", provedor="azure", servico="Azure Vision Image Analysis — Tags",
                        regiao=os.environ.get("AZURE_REGIAO", "eastus"), entrada=IMAGEM,
                        resposta=capturas[0], obtido=rotulos,
                        esperado=GABARITO["imagem"]["criterio"], aprovado=aprovado)
    assert aprovado, f"nenhum rótulo de cachorro em {rotulos}"


def test_real_visao_google(carregar_exemplo, monkeypatch, registrar_evidencia):
    exigir_google()
    exemplo = carregar_exemplo("exemplos/visao/google_vision.py", IMAGEM_EXEMPLO=str(IMAGEM))
    capturas = []
    classe_espionada(monkeypatch, exemplo.vision, "ImageAnnotatorClient", "label_detection", capturas)

    exemplo.main()

    rotulos = [a.description for a in capturas[0].label_annotations]
    aprovado = tem_cachorro(rotulos)
    registrar_evidencia(categoria="visao", provedor="google", servico="Cloud Vision LABEL_DETECTION",
                        regiao="global", entrada=IMAGEM, resposta=capturas[0], obtido=rotulos,
                        esperado=GABARITO["imagem"]["criterio"], aprovado=aprovado)
    assert aprovado, f"nenhum rótulo de cachorro em {rotulos}"


# ==================================================================== fala

def test_real_fala_aws(carregar_exemplo, monkeypatch, registrar_evidencia):
    """O Transcribe só lê do S3: o áudio é enviado ao bucket antes."""
    exigir_aws_plano_pago("Amazon Transcribe")
    exigir_aws()
    exigir_variaveis("TESTE_S3_BUCKET")
    import boto3

    bucket, chave = os.environ["TESTE_S3_BUCKET"], f"testes/frase-{uuid.uuid4().hex[:8]}.flac"
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.upload_file(str(AUDIO), bucket, chave)
    try:
        exemplo = carregar_exemplo("exemplos/fala/aws_transcribe.py",
                                   TRANSCRIBE_URI_AUDIO=f"s3://{bucket}/{chave}")
        capturas = []
        boto3_espionado(monkeypatch, exemplo, "get_transcription_job", capturas)

        exemplo.main()

        job = capturas[-1]["TranscriptionJob"]
        resultado = requests.get(job["Transcript"]["TranscriptFileUri"], timeout=30).json()
        transcricao = resultado["results"]["transcripts"][0]["transcript"]
    finally:
        s3.delete_object(Bucket=bucket, Key=chave)

    aprovado = transcricao_confere(transcricao)
    registrar_evidencia(categoria="fala", provedor="aws", servico="Amazon Transcribe StartTranscriptionJob",
                        regiao=exemplo.REGIAO, entrada=AUDIO,
                        resposta={"job": job, "transcricao": resultado},
                        obtido=transcricao, esperado=GABARITO["audio"]["criterio"], aprovado=aprovado)
    assert aprovado, f"transcrição sem as palavras-chave: {transcricao!r}"


def test_real_fala_azure(carregar_exemplo, monkeypatch, registrar_evidencia):
    """A Azure aceita URL pública: por padrão, o próprio arquivo publicado no GitHub."""
    exigir_variaveis("AZURE_SPEECH_KEY")
    url_audio = os.environ.get("AZURE_SPEECH_AUDIO_URL", URL_PUBLICA_DO_AUDIO)
    if requests.head(url_audio, timeout=15, allow_redirects=True).status_code != 200:
        pytest.skip(f"áudio inacessível em {url_audio}: publique o repositório (git push) "
                    "ou defina AZURE_SPEECH_AUDIO_URL")

    exemplo = carregar_exemplo("exemplos/fala/azure_speech.py", AZURE_SPEECH_AUDIO_URL=url_audio,
                               AZURE_SPEECH_REGION=os.environ.get("AZURE_SPEECH_REGION", "eastus"))
    # Espiona o requests.get do módulo inteiro via monkeypatch, para que ele
    # volte ao original ao fim do teste e não contamine os seguintes.
    capturas, get_original = [], exemplo.requests.get

    def get_espionado(*args, **kwargs):
        resposta = get_original(*args, **kwargs)
        capturas.append(resposta)
        return resposta

    monkeypatch.setattr(exemplo.requests, "get", get_espionado)
    exemplo.main()

    arquivos = capturas[-1].json()["values"]
    url = next(a["links"]["contentUrl"] for a in arquivos if a["kind"] == "Transcription")
    resultado = requests.get(url, timeout=30).json()
    transcricao = resultado["combinedRecognizedPhrases"][0]["display"]

    aprovado = transcricao_confere(transcricao)
    registrar_evidencia(categoria="fala", provedor="azure", servico="Azure Speech — batch transcription",
                        regiao=exemplo.REGIAO, entrada=AUDIO,
                        resposta={"arquivos": arquivos, "transcricao": resultado},
                        obtido=transcricao, esperado=GABARITO["audio"]["criterio"], aprovado=aprovado)
    assert aprovado, f"transcrição sem as palavras-chave: {transcricao!r}"


def test_real_fala_google(carregar_exemplo, monkeypatch, registrar_evidencia):
    """O BatchRecognize só lê do Cloud Storage: o áudio é enviado ao bucket antes."""
    exigir_google()
    exigir_variaveis("GOOGLE_CLOUD_PROJECT", "TESTE_GCS_BUCKET")
    from google.cloud import storage

    blob = storage.Client().bucket(os.environ["TESTE_GCS_BUCKET"]).blob(
        f"testes/frase-{uuid.uuid4().hex[:8]}.flac")
    blob.upload_from_filename(str(AUDIO))
    try:
        exemplo = carregar_exemplo("exemplos/fala/google_speech_to_text.py",
                                   GCS_URI_AUDIO=f"gs://{blob.bucket.name}/{blob.name}")
        # A resposta final vem de operacao.result(), chamado pelo próprio exemplo.
        import google.api_core.operation as op
        respostas, result_original = [], op.Operation.result

        def result_espionado(self, *args, **kwargs):
            resposta = result_original(self, *args, **kwargs)
            respostas.append(resposta)
            return resposta

        monkeypatch.setattr(op.Operation, "result", result_espionado)

        exemplo.main()
    finally:
        blob.delete()

    arquivo = next(iter(respostas[-1].results.values()))
    transcricao = " ".join(r.alternatives[0].transcript
                           for r in arquivo.inline_result.transcript.results if r.alternatives)
    aprovado = transcricao_confere(transcricao)
    registrar_evidencia(categoria="fala", provedor="google", servico="Cloud Speech-to-Text V2 BatchRecognize",
                        regiao=exemplo.REGIAO, entrada=AUDIO, resposta=respostas[-1],
                        obtido=transcricao, esperado=GABARITO["audio"]["criterio"], aprovado=aprovado)
    assert aprovado, f"transcrição sem as palavras-chave: {transcricao!r}"
