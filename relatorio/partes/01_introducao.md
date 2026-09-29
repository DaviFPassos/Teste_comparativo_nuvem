## 1. Introdução

Este relatório apresenta a análise comparativa de serviços de inteligência artificial oferecidos por **Amazon Web Services (AWS)**, **Microsoft Azure** e **Google Cloud**, sob a perspectiva de um desenvolvedor que precisa escolher entre eles para incorporá-los a uma aplicação.

A perspectiva adotada é deliberadamente a de quem **consome** o serviço, e não a de quem estuda o modelo por trás dele. As perguntas que orientam cada capítulo são as de uma decisão de integração: o que o serviço faz, como se chama, o que aceita de entrada, o que devolve, como se autentica, que limites impõe, quanto custa e em que situação compensa.

### Como este relatório foi construído

Toda afirmação técnica e todo preço vêm de **documentação oficial dos provedores**, consultada **entre 23 e 26 de setembro de 2026** — a data exata de cada fonte está registrada em `referencias/fontes.md`. Todos os preços foram consultados em 23/09/2026; algumas confirmações técnicas complementares foram feitas em 26/09/2026, durante a revisão do relatório. Onde uma informação não foi localizada, ela aparece como **pendência declarada** — nunca preenchida por estimativa.

Duas decisões metodológicas merecem registro:

**Os preços vieram das APIs públicas de preço dos provedores, não das páginas comerciais.** As páginas de preço da Azure e do Google entregam suas tabelas por JavaScript, exibindo apenas `$-` no conteúdo estático. Em vez de recorrer a fontes secundárias, os valores foram obtidos da *AWS Price List API* e da *Azure Retail Prices API* — ambas públicas e mantidas pelos próprios provedores — e das tabelas servidas pela página de preços do Google.

**Os exemplos de código não foram executados.** A seção 3 do enunciado permite isso explicitamente nesta etapa, e cada arquivo declara esse estado. Nenhum resultado de execução, medição de latência ou taxa de acerto é apresentado neste relatório: tudo isso é objeto da Etapa 2.

### Região, moeda e data

| Parâmetro | Valor |
|---|---|
| AWS | **`us-east-1`** (N. Virginia) nas três categorias |
| Microsoft Azure | **`East US`** nas três categorias |
| Google Cloud | **Preço global** em Natural Language e Vision; **`us-central1`** (Iowa) em Speech-to-Text |
| Moeda | **USD** |
| Data de consulta dos preços | **23/09/2026** |

US East foi escolhida por ser a região de referência das tabelas da AWS e da Azure e por ter as nove ofertas disponíveis. Duas das APIs do Google comparadas (Natural Language e Vision) têm **preço global, não regional**.

**Uma ressalva explícita sobre a terceira.** A tabela da Cloud Speech-to-Text V2 é regional, e o preço utilizado é o de **`us-central1` (Iowa)** — que é US Central, **não** US East. Essa é a única linha do trabalho em que a região do Google não coincide com a das outras duas, e ela está registrada assim em `custos/premissas.csv` e na lista de limitações, em vez de ser apresentada como se fosse a mesma região.
