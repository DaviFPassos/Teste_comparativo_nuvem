"""
Cloud Natural Language API (v1) — analyzeSentiment, um documento por chamada.

Mesma operação do exemplo exemplos/nlp/google_natural_language.py (Etapa 1), com:
- `retry=None`: desliga as novas tentativas embutidas (por padrão o cliente
  repete por até 600 s em DeadlineExceeded e ServiceUnavailable);
- `timeout` explícito por chamada;
- `quota_project_id` explícito: com credencial de usuário (ADC), as APIs do
  Google recusam chamadas sem projeto de cota;
- a resposta original é guardada como JSON (MessageToDict).

Credenciais: Application Default Credentials (`gcloud auth application-default
login`), fora do projeto. GOOGLE_CLOUD_PROJECT vem do .env local.
"""

import os

from .base import ErroProvedor, Provedor, Resposta


class ProvedorGoogle(Provedor):
    nome = "google"
    servico = "Cloud Natural Language API v1 — analyzeSentiment"
    regiao = "global"

    def __init__(self, idioma="pt", timeout_s=30):
        from google.cloud import language_v1

        self.idioma = idioma
        self.timeout_s = timeout_s
        self._lv1 = language_v1
        self._cliente = language_v1.LanguageServiceClient(
            client_options={"quota_project_id": os.environ["GOOGLE_CLOUD_PROJECT"]})

    def descrever(self):
        from importlib.metadata import version
        return {**super().descrever(), "idioma": self.idioma, "timeout_s": self.timeout_s,
                "sdk": f"google-cloud-language {version('google-cloud-language')}",
                "novas_tentativas_do_sdk": "desligadas (retry=None)"}

    def analisar(self, texto):
        import google.auth.exceptions as gauth
        from google.api_core import exceptions as gexc
        from google.protobuf.json_format import MessageToDict

        lv1 = self._lv1
        documento = lv1.Document(content=texto, type_=lv1.Document.Type.PLAIN_TEXT,
                                 language=self.idioma)
        try:
            resposta = self._cliente.analyze_sentiment(
                request={"document": documento, "encoding_type": lv1.EncodingType.UTF8},
                retry=None, timeout=self.timeout_s)
        except (gexc.Unauthenticated, gexc.PermissionDenied) as e:
            raise ErroProvedor("autenticacao", _curta(e), getattr(e, "code", None)) from e
        except gexc.ResourceExhausted as e:
            raise ErroProvedor("limite", _curta(e), 429) from e
        except gexc.InvalidArgument as e:
            raise ErroProvedor("entrada_invalida", _curta(e), 400) from e
        except gexc.DeadlineExceeded as e:
            raise ErroProvedor("timeout", _curta(e), 504) from e
        except (gexc.ServiceUnavailable, gexc.InternalServerError) as e:
            raise ErroProvedor("servidor", _curta(e), getattr(e, "code", 503)) from e
        except (gauth.DefaultCredentialsError, gauth.RefreshError) as e:
            raise ErroProvedor("autenticacao", _curta(e)) from e
        except gauth.TransportError as e:
            raise ErroProvedor("rede", _curta(e)) from e
        except gexc.GoogleAPICallError as e:
            raise ErroProvedor("desconhecido", _curta(e), getattr(e, "code", None)) from e

        bruta = MessageToDict(resposta._pb)
        s = resposta.document_sentiment
        if not -1.0 <= s.score <= 1.0:
            raise ErroProvedor("resposta_invalida", f"score fora de [-1, 1]: {s.score}", 200, bruta)
        return Resposta(rotulo_original=None, score=s.score, magnitude=s.magnitude,
                        idioma=resposta.language or None, bruta=bruta)


def _curta(e, limite=300):
    return " ".join(str(getattr(e, "message", None) or e).split())[:limite]
