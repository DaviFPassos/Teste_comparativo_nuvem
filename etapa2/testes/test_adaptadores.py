"""
Adaptadores com os SDKs REAIS e a rede substituída.

- Azure: o cliente oficial roda inteiro (serialização, pipeline, desserialização)
  sobre um transporte HTTP falso que devolve JSON no formato da API.
- Google: o cliente oficial roda inteiro até o stub gRPC, que é trocado por uma
  função que devolve o tipo oficial `AnalyzeSentimentResponse`.

O que estes testes provam e o modo simulado não prova: que a requisição sai com
o idioma e o texto certos, que a resposta do formato documentado é lida
corretamente, que os erros viram os códigos comuns — e que as novas tentativas
embutidas nos SDKs estão de fato desligadas.

As respostas são FICTÍCIAS no formato documentado; não são saída de serviço real.
"""

import json

import pytest

from provedores import ErroProvedor

# ------------------------------------------------------------------- Azure


def _resposta_azure(sentimento="mixed", pos=0.47, neu=0.01, neg=0.52):
    return {"kind": "SentimentAnalysisResults",
            "results": {"documents": [{"id": "0", "sentiment": sentimento,
                                       "confidenceScores": {"positive": pos, "neutral": neu,
                                                            "negative": neg},
                                       "sentences": [{"sentiment": sentimento, "text": "x",
                                                      "offset": 0, "length": 1,
                                                      "confidenceScores": {"positive": pos,
                                                                           "neutral": neu,
                                                                           "negative": neg}}],
                                       "warnings": []}],
                        "errors": [], "modelVersion": "2025-01-01"}}


class TransporteFalso:
    """Transporte HTTP do azure-core que devolve respostas pré-definidas, em ordem."""

    def __init__(self, respostas):
        self.respostas = list(respostas)       # [(status, corpo_dict), ...]
        self.enviadas = []

    def __enter__(self):
        return self

    def __exit__(self, *a):
        pass

    def open(self):
        pass

    def close(self):
        pass

    def send(self, request, **kwargs):
        from azure.core.pipeline.transport import HttpResponse
        self.enviadas.append(request)
        status, corpo = self.respostas.pop(0)
        dados = json.dumps(corpo).encode()

        class Resposta(HttpResponse):
            def body(self_inner):
                return dados

        r = Resposta(request, None)
        r.status_code = status
        r.reason = "OK" if status == 200 else "Erro"
        r.headers = {"Content-Type": "application/json"}
        r.content_type = "application/json"
        return r


@pytest.fixture
def azure(monkeypatch):
    monkeypatch.setenv("AZURE_LANGUAGE_ENDPOINT", "https://meu-recurso.cognitiveservices.azure.com/")
    monkeypatch.setenv("AZURE_LANGUAGE_KEY", "0" * 32)

    def _criar(respostas):
        from azure.ai.textanalytics import TextAnalyticsClient
        from azure.core.credentials import AzureKeyCredential
        from provedores.azure import ProvedorAzure
        prov = ProvedorAzure()
        transporte = TransporteFalso(respostas)
        # mesmo cliente que o adaptador monta, com o transporte trocado
        prov._cliente = TextAnalyticsClient(
            endpoint="https://meu-recurso.cognitiveservices.azure.com/",
            credential=AzureKeyCredential("0" * 32), retry_total=0, transport=transporte)
        return prov, transporte

    return _criar


def test_azure_le_misto_e_os_tres_scores(azure):
    prov, transp = azure([(200, _resposta_azure("mixed"))])
    r = prov.analisar("A entrega foi rápida, mas o produto veio quebrado.")
    assert r.rotulo_original == "mixed"
    assert r.confiancas == {"positive": 0.47, "neutral": 0.01, "negative": 0.52}
    assert r.versao_modelo == "2025-01-01"
    assert r.bruta["results"]["documents"][0]["sentiment"] == "mixed"   # JSON original guardado
    corpo = json.loads(transp.enviadas[0].body)
    doc = corpo["analysisInput"]["documents"][0]
    assert doc["language"] == "pt-BR"
    assert doc["text"] == "A entrega foi rápida, mas o produto veio quebrado."
    assert len(corpo["analysisInput"]["documents"]) == 1                 # um texto por chamada


def test_azure_nao_repete_sozinha_um_erro_de_servidor(azure):
    prov, transp = azure([(503, {"error": {"code": "ServiceUnavailable", "message": "x"}}),
                          (200, _resposta_azure())])
    with pytest.raises(ErroProvedor) as e:
        prov.analisar("teste")
    assert e.value.codigo == "servidor" and e.value.transitorio
    assert len(transp.enviadas) == 1                 # retry_total=0: uma única requisição


@pytest.mark.parametrize("status,mensagem,codigo", [
    (401, "Access denied due to invalid subscription key", "autenticacao"),
    (403, "Out of call volume quota for TextAnalytics F0 pricing tier", "cota_esgotada"),
    (429, "Rate limit is exceeded", "limite"),
    (400, "Invalid document", "entrada_invalida"),
])
def test_azure_erros_http_viram_codigos_comuns(azure, status, mensagem, codigo):
    prov, _ = azure([(status, {"error": {"code": "Erro", "message": mensagem}})])
    with pytest.raises(ErroProvedor) as e:
        prov.analisar("teste")
    assert e.value.codigo == codigo


def test_azure_erro_de_documento_vira_entrada_invalida(azure):
    corpo = {"kind": "SentimentAnalysisResults",
             "results": {"documents": [], "modelVersion": "2025-01-01",
                         "errors": [{"id": "0", "error": {"code": "InvalidArgument",
                                                          "message": "Document text is empty."}}]}}
    prov, _ = azure([(200, corpo)])
    with pytest.raises(ErroProvedor) as e:
        prov.analisar("x")
    assert e.value.codigo == "entrada_invalida" and not e.value.transitorio


# ------------------------------------------------------------------ Google


@pytest.fixture
def google(monkeypatch):
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "meu-projeto")

    def _criar(efeitos):
        """efeitos: lista de respostas (AnalyzeSentimentResponse) ou exceções, em ordem."""
        from google.api_core import gapic_v1, retry as retries
        from google.api_core import exceptions as gexc
        from google.auth.credentials import AnonymousCredentials
        from google.cloud import language_v1
        from provedores.google import ProvedorGoogle

        chamadas = []

        def stub(request, timeout=None, metadata=None, **kw):
            chamadas.append({"request": request, "timeout": timeout})
            efeito = efeitos.pop(0)
            if isinstance(efeito, Exception):
                raise efeito
            return efeito

        prov = ProvedorGoogle.__new__(ProvedorGoogle)
        prov.idioma, prov.timeout_s, prov._lv1 = "pt", 30, language_v1
        prov._cliente = language_v1.LanguageServiceClient(credentials=AnonymousCredentials())
        t = prov._cliente._transport
        # O stub entra com a MESMA política de nova tentativa padrão do cliente
        # (DeadlineExceeded/ServiceUnavailable): se o adaptador não a desligasse,
        # o stub seria chamado mais de uma vez.
        t._wrapped_methods[t.analyze_sentiment] = gapic_v1.method.wrap_method(
            stub, default_retry=retries.Retry(
                initial=0.001, maximum=0.001, multiplier=1, deadline=2,
                predicate=retries.if_exception_type(gexc.DeadlineExceeded,
                                                    gexc.ServiceUnavailable)),
            default_timeout=600.0)
        return prov, chamadas

    return _criar


def _resposta_google(score, magnitude=0.8):
    from google.cloud import language_v1
    return language_v1.AnalyzeSentimentResponse(
        document_sentiment=language_v1.Sentiment(score=score, magnitude=magnitude),
        language="pt")


def test_google_le_score_e_magnitude_e_envia_portugues(google):
    prov, chamadas = google([_resposta_google(-0.6, 1.2)])
    r = prov.analisar("Péssimo atendimento.")
    assert r.rotulo_original is None
    assert r.score == pytest.approx(-0.6) and r.magnitude == pytest.approx(1.2)
    assert r.idioma == "pt"
    assert r.bruta["documentSentiment"]["score"] == pytest.approx(-0.6)
    req = chamadas[0]["request"]
    assert req.document.content == "Péssimo atendimento."
    assert req.document.language == "pt"
    assert chamadas[0]["timeout"] == 30                    # timeout explícito, não os 600 s padrão


def test_google_nao_repete_sozinho_service_unavailable(google):
    from google.api_core import exceptions as gexc
    prov, chamadas = google([gexc.ServiceUnavailable("indisponível"), _resposta_google(0.5)])
    with pytest.raises(ErroProvedor) as e:
        prov.analisar("teste")
    assert e.value.codigo == "servidor"
    assert len(chamadas) == 1                              # retry=None: uma única chamada


@pytest.mark.parametrize("excecao,codigo", [
    ("PermissionDenied", "autenticacao"), ("Unauthenticated", "autenticacao"),
    ("ResourceExhausted", "limite"), ("InvalidArgument", "entrada_invalida"),
    ("DeadlineExceeded", "timeout")])
def test_google_erros_viram_codigos_comuns(google, excecao, codigo):
    from google.api_core import exceptions as gexc
    prov, _ = google([getattr(gexc, excecao)("x")])
    with pytest.raises(ErroProvedor) as e:
        prov.analisar("teste")
    assert e.value.codigo == codigo
