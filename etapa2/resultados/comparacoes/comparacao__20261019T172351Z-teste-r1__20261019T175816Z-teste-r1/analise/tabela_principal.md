Execução `comparacao__20261019T172351Z-teste-r1__20261019T175816Z-teste-r1` · interseção de 115 de 115 textos programados (3 classes)

| Provedor | Respostas válidas | Acurácia | Macro-F1 | Acertos / programados | Previsões `misto` | Latência mediana (ms) | Latência p95 (ms) | Sucesso por tentativa | Custo estimado (USD, com franquia) |
|---|---|---|---|---|---|---|---|---|---|
| azure | 115/115 | 74,8% | 65,9% | 74,8% | 9 | 253 | 487 (n=115) | 100,0% | 0.00 |
| google | 115/115 | 78,3% | 71,2% | 78,3% | 0 | 1.092 | 1.282 (n=115) | 100,0% | 0.00 |

**Latência não comparável entre provedores** — execuções separadas em máquinas diferentes: a latência de cada provedor é válida, mas a comparação entre eles não é. Execuções: `20261019T172351Z-teste-r1` (google), `20261019T175816Z-teste-r1` (azure).

Comparação pareada (115 textos): McNemar exato b=10, c=14, p=0.541; kappa entre provedores = 0.613.

Sem a classe neutra (positivo × negativo, 100 textos da interseção; previsão neutro ou misto conta como erro):

| Provedor | Acurácia | Macro-F1 |
|---|---|---|
| azure | 82,0% | 88,2% |
| google | 81,0% | 88,2% |

McNemar exato sem a classe neutra: b=10, c=9, p=1.000.
