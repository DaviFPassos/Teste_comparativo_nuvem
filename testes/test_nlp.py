"""Testes dos exemplos de NLP / análise de sentimento."""

from unittest import mock

import pytest

TEXTO = "O atendimento foi excelente."


def test_aws_comprehend(carregar_exemplo, cliente_aws, monkeypatch, capsys):
    exemplo = carregar_exemplo("exemplos/nlp/aws_comprehend.py")
    cliente, stubber = cliente_aws("comprehend")

    # Resposta no formato documentado em NLP-AWS-01; o Stubber a valida contra
    # o modelo de saída oficial do DetectSentiment.
    stubber.add_response(
        "detect_sentiment",
        {
            "Sentiment": "POSITIVE",
            "SentimentScore": {"Positive": 0.95, "Negative": 0.01,
                               "Neutral": 0.03, "Mixed": 0.01},
        },
        expected_params={"Text": TEXTO, "LanguageCode": "pt"},
    )

    servicos_pedidos = []
    monkeypatch.setattr(exemplo.boto3, "client",
                        lambda servico, **kw: servicos_pedidos.append((servico, kw)) or cliente)

    with stubber:
        exemplo.main()
    stubber.assert_no_pending_responses()

    assert servicos_pedidos == [("comprehend", {"region_name": "us-east-1"})]
    saida = capsys.readouterr().out
    assert "Classe: POSITIVE" in saida
    assert "Positive: 0.9500" in saida


def test_azure_language(carregar_exemplo, monkeypatch, capsys):
    from azure.ai.textanalytics import (AnalyzeSentimentResult, SentenceSentiment,
                                        SentimentConfidenceScores, TextAnalyticsClient)
    from azure.core.credentials import AzureKeyCredential

    exemplo = carregar_exemplo(
        "exemplos/nlp/azure_language.py",
        AZURE_LANGUAGE_ENDPOINT="https://teste.cognitiveservices.azure.com/",
        AZURE_LANGUAGE_KEY="chave-de-teste",
    )

    # autospec: o cliente falso tem exatamente os métodos e assinaturas do real.
    ClienteFalso = mock.create_autospec(TextAnalyticsClient)
    monkeypatch.setattr(exemplo, "TextAnalyticsClient", ClienteFalso)

    escores = SentimentConfidenceScores(positive=0.98, neutral=0.01, negative=0.01)
    ClienteFalso.return_value.analyze_sentiment.return_value = [
        AnalyzeSentimentResult(
            id="0", sentiment="positive", confidence_scores=escores, is_error=False,
            sentences=[SentenceSentiment(text=TEXTO, sentiment="positive",
                                         confidence_scores=escores)],
        )
    ]

    exemplo.main()

    _, kwargs = ClienteFalso.call_args
    assert kwargs["endpoint"] == "https://teste.cognitiveservices.azure.com/"
    assert isinstance(kwargs["credential"], AzureKeyCredential)
    ClienteFalso.return_value.analyze_sentiment.assert_called_once_with(
        documents=[TEXTO], language="pt-BR")

    saida = capsys.readouterr().out
    assert "Classe do documento: positive" in saida
    assert "positive: 0.9800" in saida
    assert f"sentença 1: positive — {TEXTO}" in saida


def test_google_natural_language(carregar_exemplo, monkeypatch, capsys):
    from google.cloud import language_v1

    exemplo = carregar_exemplo("exemplos/nlp/google_natural_language.py")

    ClienteFalso = mock.create_autospec(language_v1.LanguageServiceClient)
    monkeypatch.setattr(exemplo.language_v1, "LanguageServiceClient", ClienteFalso)

    # Resposta montada com os tipos reais do SDK: um campo inexistente seria
    # rejeitado na construção.
    ClienteFalso.return_value.analyze_sentiment.return_value = language_v1.AnalyzeSentimentResponse(
        document_sentiment=language_v1.Sentiment(score=0.9, magnitude=0.9),
        language="pt",
        sentences=[language_v1.Sentence(
            text=language_v1.TextSpan(content=TEXTO, begin_offset=0),
            sentiment=language_v1.Sentiment(score=0.9, magnitude=0.9),
        )],
    )

    exemplo.main()

    pedido = ClienteFalso.return_value.analyze_sentiment.call_args.kwargs["request"]
    assert pedido["document"].content == TEXTO
    assert pedido["document"].language == "pt"
    assert pedido["document"].type_ == language_v1.Document.Type.PLAIN_TEXT
    assert pedido["encoding_type"] == language_v1.EncodingType.UTF8

    saida = capsys.readouterr().out
    assert "score:     0.9000" in saida
    assert "classe derivada por limiar da aplicação: positivo" in saida


@pytest.mark.parametrize("score, classe", [
    (0.90, "positivo"),
    (0.26, "positivo"),
    (0.25, "neutro"),    # o limiar em si é neutro
    (0.00, "neutro"),
    (-0.25, "neutro"),
    (-0.26, "negativo"),
    (-0.90, "negativo"),
])
def test_google_limiares_de_classificacao(carregar_exemplo, score, classe):
    """O Google não devolve classe; o exemplo deriva uma por limiar."""
    exemplo = carregar_exemplo("exemplos/nlp/google_natural_language.py")
    assert exemplo.classificar(score) == classe
