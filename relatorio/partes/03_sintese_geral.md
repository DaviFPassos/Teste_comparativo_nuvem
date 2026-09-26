## 6. Síntese geral

As sínteses por categoria estão ao final de cada capítulo. Esta seção reúne o que atravessa as três.

### 6.1 Não há um vencedor, e o motivo é estrutural

Em nenhuma das três categorias um provedor domina em todos os critérios. Mais do que isso: **em duas das três, a ordem de preço depende de um parâmetro da própria aplicação**, e não do provedor.

| Categoria | O parâmetro que decide | Efeito |
|---|---|---|
| NLP | Comprimento típico do texto | AWS cobra 30% dos concorrentes em textos de 100 caracteres; empata na janela de 3.901–4.000 caracteres, mas volta a ser mais barata a partir de 4.001 — o empate vale numa janela de 100 caracteres antes de cada múltiplo de 1.000, não num ponto isolado |
| Visão | Volume mensal | AWS e Azure empatam em 100 mil imagens; os degraus de faixa diferem acima de 1 milhão |
| Fala | Tolerância a fila de processamento | Azure e Google empatam em $30,00 no modo de menor urgência; a AWS cobra $60,00 sem exigir essa tolerância |

Quem escolher um provedor a partir de uma tabela de preço isolada, sem fixar esses parâmetros, escolherá errado com frequência.

### 6.2 A unidade de cobrança pesa mais que o preço unitário

O achado mais transferível deste trabalho é que **a granularidade da unidade de cobrança pode importar mais do que o preço da unidade**.

Em análise de sentimento, Azure e Google cobram uma unidade inteira de 1.000 caracteres mesmo para um comentário de 100 caracteres — pagando-se por 900 caracteres nunca enviados. A AWS, cobrando em unidades de 100 caracteres, cobra 30% disso no mesmo cenário — uma redução de 70%. Os três têm preços unitários da mesma ordem de grandeza; o que separa é como contam.

Na transcrição de áudio, a mesma lógica trabalhou a favor de todos: os três cobram em incrementos de um segundo, e a AWS declara não haver cobrança mínima.

### 6.3 A Azure é a mais completa tecnicamente e a mais arriscada no calendário

A Azure aparece à frente em vários critérios técnicos: é a única com **94 idiomas** e distinção formal entre `pt-BR` e `pt-PT` em sentimento; a única com **contêiner Docker** para execução local; a única que aceita **URI público** como origem de áudio; a única que publica **expectativa de latência** do processamento em lote; e a que oferece o caminho mais elaborado de isolamento de armazenamento.

Em contrapartida, é a única dos três provedores com **encerramento anunciado em duas das três categorias comparadas**:

| Serviço | Encerramento anunciado |
|---|---|
| Azure Language — análise de sentimento e opinion mining | **31/03/2029** |
| Azure Vision — Image Analysis 4.0 | **25/09/2028** |

Além disso, quatro funcionalidades do Image Analysis 4.0 em preview já foram desativadas em 31/03/2025. Nenhum serviço comparado da AWS ou do Google Cloud apresenta aviso equivalente nas páginas consultadas.

Esse é um custo que não aparece em cenário de preço nenhum: para um sistema com horizonte de manutenção de anos, escolher a Azure nessas duas categorias significa assumir uma migração com data marcada.

### 6.4 O custo de troca é maior do que parece

Nenhuma das três categorias permite trocar de provedor apenas trocando o endpoint:

- **Sentimento:** a saída do Google é um número contínuo; a da AWS tem quatro classes, cada uma com score próprio; a da Azure tem quatro rótulos possíveis no documento mas só três scores, e `mixed` só aparece por composição das sentenças. Migrar exige redefinir a lógica de classificação, não só ler outro campo.
- **Visão:** as escalas de confiança diferem (0–100 × 0–1) e os vocabulários de rótulos não têm tabela de equivalência oficial. Migrar exige recalibrar limiares e remapear termos.
- **Fala:** a origem do áudio é imposta de forma diferente (S3 obrigatório na AWS; URI público aceito na Azure; Cloud Storage no Google), o que atinge a arquitetura, não só o código de chamada.

### 6.5 Franquia gratuita não é desconto — e a diferença muda o número

As três nuvens anunciam "camada gratuita", e as três querem dizer coisas diferentes:

| Provedor | O que é | Entra no cenário? |
|---|---|---|
| AWS | Free Tier promocional, na mesma conta e no mesmo tier da operação | Sim, mas **só nos 12 primeiros meses** |
| Microsoft Azure | Tier **F0**, um recurso separado do tier pago, com cota e limites próprios | **Não** — e na transcrição em lote o F0 **nem oferece a operação** |
| Google Cloud | Primeira **faixa da própria tabela**, cobrada a 0,00 USD | Sim, permanente |

A consequência prática aparece no número: descontar as 5 horas gratuitas do F0 da Azure de uma fatura de transcrição em lote produziria $29,10 em vez dos **$30,00** corretos — um desconto que a Microsoft não concede, porque a operação não existe naquele tier. Por isso `custos/franquias.csv` registra, para cada franquia, se ela é aplicável ao cenário e por quê, e `custos/resultados.csv` carrega essa decisão na coluna `franquia_aplicada`.

Pela mesma razão, a comparação principal usa os preços **sem franquia**: é a única base que significa a mesma coisa nos três. Onde a franquia é permanente — Google em NLP e visão —, a cobrança habitual é a coluna com franquia, e isso está dito nos capítulos.

### 6.6 O que a documentação não permite concluir

A análise é **documental**. Ela não estabelece qual serviço classifica sentimento com mais acerto, qual rotula imagens de forma mais útil, ou qual transcreve português do Brasil com menos erros. Essas perguntas exigem execução, dados de teste, gabarito e medição — objeto da Etapa 2.
