"""Testes dos exemplos de visão computacional / detecção de rótulos."""

from unittest import mock

import pytest


def test_aws_rekognition(carregar_exemplo, cliente_aws, imagem_falsa, monkeypatch, capsys):
    exemplo = carregar_exemplo("exemplos/visao/aws_rekognition.py",
                               IMAGEM_EXEMPLO=str(imagem_falsa))
    cliente, stubber = cliente_aws("rekognition")

    # Formato documentado em VIS-AWS-01, validado pelo Stubber contra o modelo
    # oficial do DetectLabels (inclusive o parâmetro Features).
    stubber.add_response(
        "detect_labels",
        {
            "Labels": [{
                "Name": "Dog", "Confidence": 98.7,
                "Parents": [{"Name": "Animal"}, {"Name": "Pet"}],
                "Categories": [{"Name": "Animals and Pets"}],
                "Aliases": [], "Instances": [],
            }],
            "LabelModelVersion": "3.0",
        },
        expected_params={
            "Image": {"Bytes": imagem_falsa.read_bytes()},
            "MaxLabels": 10,
            "MinConfidence": 55.0,
            "Features": ["GENERAL_LABELS"],
        },
    )
    monkeypatch.setattr(exemplo.boto3, "client", lambda servico, **kw: cliente)

    with stubber:
        exemplo.main()
    stubber.assert_no_pending_responses()

    saida = capsys.readouterr().out
    assert "Versão do modelo: 3.0" in saida
    assert "Dog: 98.70" in saida
    assert "rótulos-pai: Animal, Pet" in saida
    assert "categorias:  Animals and Pets" in saida


def test_azure_image_analysis(carregar_exemplo, imagem_falsa, monkeypatch, capsys):
    from azure.ai.vision.imageanalysis import ImageAnalysisClient
    from azure.ai.vision.imageanalysis.models import (DetectedTag, ImageAnalysisResult,
                                                      ImageMetadata, TagsResult,
                                                      VisualFeatures)

    exemplo = carregar_exemplo(
        "exemplos/visao/azure_image_analysis.py",
        IMAGEM_EXEMPLO=str(imagem_falsa),
        AZURE_VISION_ENDPOINT="https://teste.cognitiveservices.azure.com/",
        AZURE_VISION_KEY="chave-de-teste",
    )

    ClienteFalso = mock.create_autospec(ImageAnalysisClient)
    monkeypatch.setattr(exemplo, "ImageAnalysisClient", ClienteFalso)
    ClienteFalso.return_value.analyze.return_value = ImageAnalysisResult(
        model_version="2023-10-01",
        metadata=ImageMetadata(height=480, width=640),
        tags=TagsResult(list=[DetectedTag(name="dog", confidence=0.9921)]),
    )

    exemplo.main()

    ClienteFalso.return_value.analyze.assert_called_once_with(
        image_data=imagem_falsa.read_bytes(),
        visual_features=[VisualFeatures.TAGS],   # uma única feature
    )
    assert "dog: 0.9921" in capsys.readouterr().out


def _vision_falso(monkeypatch, exemplo, resposta):
    from google.cloud import vision

    ClienteFalso = mock.create_autospec(vision.ImageAnnotatorClient)
    monkeypatch.setattr(exemplo.vision, "ImageAnnotatorClient", ClienteFalso)
    ClienteFalso.return_value.label_detection.return_value = resposta
    return ClienteFalso


def test_google_vision(carregar_exemplo, imagem_falsa, monkeypatch, capsys):
    from google.cloud import vision

    exemplo = carregar_exemplo("exemplos/visao/google_vision.py",
                               IMAGEM_EXEMPLO=str(imagem_falsa))
    ClienteFalso = _vision_falso(monkeypatch, exemplo, vision.AnnotateImageResponse(
        label_annotations=[vision.EntityAnnotation(
            mid="/m/0bt9lr", description="Dog", score=0.97, topicality=0.97)],
    ))

    exemplo.main()

    chamada = ClienteFalso.return_value.label_detection.call_args
    assert chamada.kwargs["image"].content == imagem_falsa.read_bytes()
    assert chamada.kwargs["max_results"] == 10
    assert "Dog: score 0.9700 | topicality 0.9700 | mid /m/0bt9lr" in capsys.readouterr().out


def test_google_vision_erro_da_api_vira_excecao(carregar_exemplo, imagem_falsa, monkeypatch):
    """A Cloud Vision devolve erro DENTRO da resposta; o exemplo precisa checá-lo."""
    from google.cloud import vision

    exemplo = carregar_exemplo("exemplos/visao/google_vision.py",
                               IMAGEM_EXEMPLO=str(imagem_falsa))
    _vision_falso(monkeypatch, exemplo, vision.AnnotateImageResponse(
        error={"code": 3, "message": "Bad image data."}))

    with pytest.raises(RuntimeError, match="Bad image data."):
        exemplo.main()
