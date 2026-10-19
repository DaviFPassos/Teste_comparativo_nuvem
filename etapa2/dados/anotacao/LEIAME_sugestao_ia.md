# `sugestao_ia.csv` — rótulos sugeridos por IA

**O que é:** um rótulo para cada um dos 330 candidatos, sugerido por um modelo de linguagem (IA) em 19/10/2026, seguindo `etapa2/dados/guia_de_anotacao.md`. A coluna `observacao` traz o motivo nos casos de fronteira.

**O que não é:** anotação manual. Sozinhos, estes rótulos **não** são o gabarito. O roteiro da Etapa 2 admite rótulos sugeridos por IA **desde que haja revisão humana identificada**, e o relatório precisa declarar como o gabarito foi construído.

**Como foi usado (decisão de 19/10/2026):** os rótulos foram copiados para `planilha_A.csv`. O anotador A é **Davi Fonseca Passos**, que os adotou e responde por eles, e o método fica registrado em `anotadores.json` (campo `como_A`) e em `etapa2/metodologia.md`. A `planilha_B.csv` fica com um integrante humano, que **não** deve abrir este arquivo nem a planilha A antes de terminar.

**Como o modelo trabalhou:**
- leu os textos pela planilha de anotação, sem ver as estrelas;
- não teve acesso a nenhuma resposta da Azure ou do Google sobre estes textos — nenhuma foi pedida.

**Duas formas válidas de usar:**
1. **IA × humano.** Um integrante preenche `planilha_B.csv` sem consultar este arquivo. A concordância IA × humano é medida pelo kappa de Cohen, e as divergências são decididas pelo integrante.
2. **Revisão humana de tudo.** Um integrante revisa as 330 sugestões, aceitando ou corrigindo cada uma, e o relatório declara "rótulos sugeridos por IA com revisão humana identificada (nome)". Não há kappa nesta forma.

**Limitação a declarar em qualquer das duas:** usar uma IA de linguagem para sugerir o gabarito de serviços de IA de linguagem pode aproximar o gabarito do "jeito de máquina" de ler sentimento. A revisão humana existe para corrigir isso.

**Achados durante a rotulagem** (valem para qualquer forma):
- Só **10 neutros** entre os 300 candidatos ao teste, contra a meta de 50.
- **3 textos com nome próprio do autor** (t196, t219, t300). Isso é dado pessoal, que o filtro automático não pegou e que deve ser tratado antes de congelar o teste.
