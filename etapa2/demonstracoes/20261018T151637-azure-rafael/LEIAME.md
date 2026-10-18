# Verificação de infraestrutura da Azure — Rafael, 18/10/2026

Chamadas **reais** à Azure Language, feitas por **Rafael Fonseca Pessoa** com o pipeline do ramo `feat/azure-nlp-sentimento` (commit `82e25f9`), em 18/10/2026. **Fora do experimento.**

| Item | Valor |
|---|---|
| Arquivo | `azure_20261018_151637.json` — preservado **byte a byte** como saiu do script original |
| Entrada | 5 frases de `etapa2/dados/fumaca_azure.csv`. As três primeiras são os exemplos **ilustrativos** do roteiro da Etapa 2; os rótulos foram dados pelo autor |
| Resultado | 5/5 respostas válidas; 4 coincidiram com o rótulo; 1ª chamada 1.580 ms, demais ~843 ms |
| Formato | O do pipeline original (um JSON por execução), **diferente** do formato do executor integrado — por isso `analisar.py` não lê este arquivo |

Serve como evidência de que o recurso Azure Language e a credencial do Rafael funcionam. Não é coleta do experimento: não usa o conjunto congelado nem o protocolo de `etapa2/metodologia.md`.
