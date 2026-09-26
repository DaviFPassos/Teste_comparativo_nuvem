# /// script
# requires-python = ">=3.10"
# dependencies = ["google-cloud-language"]
# ///
"""
Categoria: NLP / análise de texto
Provedor:  Google Cloud — Cloud Natural Language API (v1)
Operação:  analyzeSentiment

ESTADO DE VALIDAÇÃO: exemplo ILUSTRATIVO, NÃO EXECUTADO pelo grupo.
    Adaptado da documentação oficial do Google Cloud. A seção 3 do enunciado
    permite explicitamente que os exemplos da Etapa 1 não sejam executados.

FONTE DA ADAPTAÇÃO:
    https://docs.cloud.google.com/natural-language/docs/analyzing-sentiment
    (consultado em 23/09/2026)

DEPENDÊNCIA (declarada no bloco PEP 723 no topo do arquivo):
    google-cloud-language

COMO EXECUTAR:
    uv run exemplos/nlp/google_natural_language.py
    O uv lê o bloco `# /// script` e resolve a dependência sozinho, em
    ambiente isolado e efêmero — não é preciso criar venv nem usar pip.

AUTENTICAÇÃO:
    Application Default Credentials, via variável de ambiente apontando para o
    arquivo JSON da conta de serviço. Nenhuma credencial é escrita neste arquivo.
        GOOGLE_APPLICATION_CREDENTIALS=/caminho/para/conta-de-servico.json

DIFERENÇA IMPORTANTE DE SAÍDA:
    Diferentemente da AWS e da Azure, esta API NÃO retorna uma classe de
    sentimento. Retorna 'score' (de -1,0 a +1,0) e 'magnitude' (intensidade
    acumulada, não normalizada). Converter isso em positivo/neutro/negativo
    exige limiares definidos pela aplicação — ver a função classificar() abaixo.

LIMITES RELEVANTES:
    1.000.000 bytes de conteúdo; 100.000 tokens por requisição;
    600 requisições/minuto e 800.000 requisições/dia.
"""

from google.cloud import language_v1

# Mesmo texto usado nos três provedores, para permitir comparação direta.
TEXTO = "O atendimento foi excelente."
IDIOMA = "pt"  # a Cloud Natural Language não distingue pt-BR de pt-PT

# Limiares ILUSTRATIVOS. Não são uma regra do Google: são uma escolha da
# aplicação, que precisa ser justificada e fixada antes de qualquer avaliação.
LIMIAR_POSITIVO = 0.25
LIMIAR_NEGATIVO = -0.25


def classificar(score: float) -> str:
    """Converte o score contínuo em classe, usando limiares da aplicação."""
    if score > LIMIAR_POSITIVO:
        return "positivo"
    if score < LIMIAR_NEGATIVO:
        return "negativo"
    return "neutro"


def main() -> None:
    cliente = language_v1.LanguageServiceClient()

    # --- TRECHO CITADO NO RELATÓRIO (início) ---
    documento = language_v1.Document(
        content=TEXTO,
        type_=language_v1.Document.Type.PLAIN_TEXT,
        language=IDIOMA,
    )

    resposta = cliente.analyze_sentiment(
        request={"document": documento, "encoding_type": language_v1.EncodingType.UTF8}
    )
    # --- TRECHO CITADO NO RELATÓRIO (fim) ---

    sentimento = resposta.document_sentiment
    print(f"score:     {sentimento.score:.4f}")
    print(f"magnitude: {sentimento.magnitude:.4f}")
    print(f"classe derivada por limiar da aplicação: {classificar(sentimento.score)}")

    # A resposta também traz sentimento por sentença.
    for i, sentenca in enumerate(resposta.sentences, start=1):
        print(f"  sentença {i}: score {sentenca.sentiment.score:.4f} — {sentenca.text.content}")


if __name__ == "__main__":
    main()
