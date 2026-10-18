"""
Azure Language in Foundry Tools — análise de sentimento, um documento por chamada.

Mesma operação do exemplo exemplos/nlp/azure_language.py (Etapa 1), com três
diferenças necessárias para medir:
- novas tentativas do SDK desligadas (`retry_total=0`);
- timeout explícito de conexão e de leitura;
- a resposta JSON original é capturada pelo `raw_response_hook`, para guardar
  exatamente o que o serviço devolveu (inclusive `modelVersion`).

Credenciais: AZURE_LANGUAGE_ENDPOINT e AZURE_LANGUAGE_KEY, do .env local.
"""

import json
import os

from .base import ErroProvedor, Provedor, Resposta


class ProvedorAzure(Provedor):
    nome = "azure"
    servico = "Azure Language in Foundry Tools — Sentiment analysis"

    def __init__(self, idioma="pt-BR", timeout_s=30, regiao="eastus", tier="F0",
                 opinion_mining=False):
        from azure.ai.textanalytics import TextAnalyticsClient
        from azure.core.credentials import AzureKeyCredential

        self.idioma = idioma
        self.timeout_s = timeout_s
        self.regiao = regiao
        self.tier = tier
        self.opinion_mining = opinion_mining
        self._cliente = TextAnalyticsClient(
            endpoint=os.environ["AZURE_LANGUAGE_ENDPOINT"],
            credential=AzureKeyCredential(os.environ["AZURE_LANGUAGE_KEY"]),
            retry_total=0,
        )

    def descrever(self):
        from importlib.metadata import version
        return {**super().descrever(), "idioma": self.idioma, "tier_declarado": self.tier,
                "timeout_s": self.timeout_s, "opinion_mining": self.opinion_mining,
                "sdk": f"azure-ai-textanalytics {version('azure-ai-textanalytics')}",
                "novas_tentativas_do_sdk": "desligadas (retry_total=0)"}

    def analisar(self, texto):
        from azure.core.exceptions import (ClientAuthenticationError, HttpResponseError,
                                           ServiceRequestError, ServiceResponseError)
        capturado = {}

        def gancho(resposta):
            try:
                capturado["json"] = json.loads(resposta.http_response.text())
            except (ValueError, AttributeError):
                capturado["json"] = None

        try:
            resultado = self._cliente.analyze_sentiment(
                documents=[texto], language=self.idioma,
                show_opinion_mining=self.opinion_mining,
                raw_response_hook=gancho,
                connection_timeout=self.timeout_s, read_timeout=self.timeout_s,
            )[0]
        except ClientAuthenticationError as e:
            raise ErroProvedor("autenticacao", _curta(e), getattr(e, "status_code", 401)) from e
        except HttpResponseError as e:
            raise _erro_http(e) from e
        except (ServiceRequestError, ServiceResponseError) as e:
            codigo = "timeout" if "timed out" in str(e).lower() or "timeout" in str(e).lower() else "rede"
            raise ErroProvedor(codigo, _curta(e)) from e

        bruta = capturado.get("json") or {}
        if resultado.is_error:
            erro = resultado.error
            raise ErroProvedor("entrada_invalida", f"{erro.code}: {erro.message}", 200, bruta)
        if resultado.sentiment not in ("positive", "negative", "neutral", "mixed"):
            raise ErroProvedor("resposta_invalida", f"rótulo inesperado: {resultado.sentiment!r}",
                               200, bruta)
        c = resultado.confidence_scores
        return Resposta(
            rotulo_original=resultado.sentiment,
            confiancas={"positive": c.positive, "neutral": c.neutral, "negative": c.negative},
            versao_modelo=bruta.get("modelVersion") or (bruta.get("results") or {}).get("modelVersion"),
            bruta=bruta,
        )


def _curta(e, limite=300):
    """Mensagem de erro curta e sem quebras; a sanitização vem depois."""
    return " ".join(str(getattr(e, "message", None) or e).split())[:limite]


def _erro_http(e):
    status = getattr(e, "status_code", None)
    msg = _curta(e)
    if status == 403 and "quota" in msg.lower():
        # F0 esgotado: "Out of call volume quota for ... F0 pricing tier"
        return ErroProvedor("cota_esgotada", msg, status)
    if status in (401, 403):
        return ErroProvedor("autenticacao", msg, status)
    if status == 429:
        return ErroProvedor("limite", msg, status)
    if status == 400:
        return ErroProvedor("entrada_invalida", msg, status)
    if status and status >= 500:
        return ErroProvedor("servidor", msg, status)
    return ErroProvedor("desconhecido", msg, status)
