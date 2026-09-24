## 6. Síntese geral

As sínteses por categoria estão ao final de cada capítulo. Esta seção reúne o que atravessa as três.

### 6.1 Não há um vencedor, e o motivo é estrutural

Em nenhuma das três categorias um provedor domina em todos os critérios. Mais do que isso: **em duas das três, a ordem de preço depende de um parâmetro da própria aplicação**, e não do provedor.

| Categoria | O parâmetro que decide | Efeito |
|---|---|---|
| NLP | Comprimento típico do texto | AWS custa 1/3 dos concorrentes em textos de 100 caracteres e empata em 4.000 |
| Visão | Volume mensal | AWS e Azure empatam em 100 mil imagens; os degraus de faixa diferem acima de 1 milhão |
| Fala | Tolerância a fila de processamento | Azure e Google empatam em $30,00 no modo de menor urgência; a AWS cobra $60,00 sem exigir essa tolerância |

Quem escolher um provedor a partir de uma tabela de preço isolada, sem fixar esses parâmetros, escolherá errado com frequência.

### 6.2 A unidade de cobrança pesa mais que o preço unitário

O achado mais transferível deste trabalho é que **a granularidade da unidade de cobrança pode importar mais do que o preço da unidade**.

Em análise de sentimento, Azure e Google cobram uma unidade inteira de 1.000 caracteres mesmo para um comentário de 100 caracteres — pagando-se por 900 caracteres nunca enviados. A AWS, cobrando em unidades de 100 caracteres, custa um terço no mesmo cenário. Os três têm preços unitários da mesma ordem de grandeza; o que separa é como contam.

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

- **Sentimento:** a saída do Google é um número contínuo, a da AWS tem quatro classes e a da Azure tem três com granularidade de sentença. Migrar exige redefinir a lógica de classificação.
- **Visão:** as escalas de confiança diferem (0–100 × 0–1) e os vocabulários de rótulos não têm tabela de equivalência oficial. Migrar exige recalibrar limiares e remapear termos.
- **Fala:** a origem do áudio é imposta de forma diferente (S3 obrigatório na AWS; URI público aceito na Azure; Cloud Storage no Google), o que atinge a arquitetura, não só o código de chamada.

### 6.5 O que a documentação não permite concluir

A análise é **documental**. Ela não estabelece qual serviço classifica sentimento com mais acerto, qual rotula imagens de forma mais útil, ou qual transcreve português do Brasil com menos erros. Essas perguntas exigem execução, dados de teste, gabarito e medição — objeto da Etapa 2.
