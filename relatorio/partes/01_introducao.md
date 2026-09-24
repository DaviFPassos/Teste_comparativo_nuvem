## 1. Introdução

Este relatório apresenta a análise comparativa de serviços de inteligência artificial oferecidos por **Amazon Web Services (AWS)**, **Microsoft Azure** e **Google Cloud**, sob a perspectiva de um desenvolvedor que precisa escolher entre eles para incorporá-los a uma aplicação.

A perspectiva adotada é deliberadamente a de quem **consome** o serviço, e não a de quem estuda o modelo por trás dele. As perguntas que orientam cada capítulo são as de uma decisão de integração: o que o serviço faz, como se chama, o que aceita de entrada, o que devolve, como se autentica, que limites impõe, quanto custa e em que situação compensa.

### Como este relatório foi construído

Toda afirmação técnica e todo preço vêm de **documentação oficial dos provedores**, consultada em **23 e 24 de setembro de 2026**, com URL e data registradas em `referencias/fontes.md`. Onde uma informação não foi localizada, ela aparece como **pendência declarada** — nunca preenchida por estimativa.

Duas decisões metodológicas merecem registro:

**Os preços vieram das APIs públicas de preço dos provedores, não das páginas comerciais.** As páginas de preço da Azure e do Google entregam suas tabelas por JavaScript, exibindo apenas `$-` no conteúdo estático. Em vez de recorrer a fontes secundárias, os valores foram obtidos da *AWS Price List API* e da *Azure Retail Prices API* — ambas públicas e mantidas pelos próprios provedores — e das tabelas servidas pela página de preços do Google.

**Os exemplos de código não foram executados.** A seção 3 do enunciado permite isso explicitamente nesta etapa, e cada arquivo declara esse estado. Nenhum resultado de execução, medição de latência ou taxa de acerto é apresentado neste relatório: tudo isso é objeto da Etapa 2.

### Região, moeda e data

| Parâmetro | Valor |
|---|---|
| Região de referência | **US East** — `us-east-1` (N. Virginia) / `East US` / `us-central1` |
| Moeda | **USD** |
| Data de consulta dos preços | **23/09/2026** |

A região US East foi escolhida por ser a região de referência das três tabelas de preço e por ter as nove ofertas disponíveis. Duas das APIs do Google comparadas (Natural Language e Vision) têm **preço global, não regional** — o que está registrado nas premissas.
