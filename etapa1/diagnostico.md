# Diagnóstico da Etapa 1 — exigências do enunciado × material existente

> ## ⚠️ DOCUMENTO HISTÓRICO — NÃO DESCREVE O ESTADO ATUAL
>
> Este é o **retrato do ponto de partida**, feito em 23/09/2026, antes de qualquer
> conteúdo ser produzido. É por isso que quase toda exigência aparece como
> `ausente`: naquele momento ela estava mesmo.
>
> **Nenhuma linha deste arquivo deve ser lida como pendência atual.** Ele é
> mantido no repositório porque registra o que existia antes e justifica as
> decisões tomadas em seguida — não porque descreva a entrega.
>
> Para o estado atual, ver: `STATUS.md` (situação geral, artefatos produzidos e
> pendências que restam), `relatorio/relatorio_etapa1.md` (entrega consolidada) e a
> seção de pendências ao fim de cada capítulo em `etapa1/`. Os artefatos previstos
> nas ações desta tabela existem todos, e estão listados em `STATUS.md`.

**Data do diagnóstico:** 23/09/2026
**Fonte das exigências:** `pdfs/Computação em Nuvem - Trabalho I_ Comparação de Serviços de Inteligência Artificial em Nuvem.pdf` (5 páginas), seções 1 a 6 e 12.

## Observação inicial sobre o material de partida

O `etapas/ROTEIRO_ETAPA1.md` (seções 1 e 4) pressupõe que o grupo já possui uma pesquisa inicial de NLP em PDF (`parte1_comparacao_nlp_aws_azure_gcp.pdf`), a ser reaproveitada como um dos três capítulos.

**Esse arquivo não existe no repositório.** A pasta `pdfs/` contém apenas:

| Arquivo | Relação com este trabalho |
|---|---|
| `Computação em Nuvem - Trabalho I_ Comparação de Serviços de Inteligência Artificial em Nuvem.pdf` | Enunciado do professor — **é a base das exigências**. |
| `Questionario_computacao_nuvem_nabor.pdf` | Perguntas sobre história/economia da nuvem (Stallman, relatório Berkeley 2009, serverless). **Outro trabalho**; não integra esta entrega e não deve ser publicado neste repositório. |

**Consequência:** não há material anterior a reaproveitar ou revisar. Os três capítulos (NLP, visão computacional, fala para texto) serão produzidos do zero, a partir de documentação oficial dos provedores. Por isso, quase todas as exigências abaixo aparecem como `ausente` — este é o ponto de partida real, e não uma omissão do diagnóstico.

## Situações utilizadas

- **atendido** — existe artefato no repositório que cumpre a exigência.
- **parcial** — existe artefato, mas incompleto ou não verificado.
- **ausente** — não existe artefato.
- **a verificar** — existe afirmação ou artefato cuja correção ainda não foi conferida contra a fonte.

## Tabela de exigências

| # | Exigência | Seção / página | Evidência hoje no repositório | Situação | Ação necessária |
|---|---|---|---|---|---|
| 1 | Pesquisar os serviços de IA de AWS, Azure e Google Cloud e identificar categorias com ofertas equivalentes em pelo menos dois provedores | 2, p. 1–2 | Nenhuma pesquisa registrada | ausente | Pesquisar as 9 ofertas em documentação oficial (Fase 2) |
| 2 | Selecionar entre três e cinco categorias, privilegiando relevância e diversidade de funcionalidades | 2, p. 2 | Três categorias decididas pelo grupo (NLP, visão, fala), registradas apenas no roteiro e no README | parcial | Formalizar a seleção em `etapa1/categorias.md` (Fase 2) |
| 3 | Explicar no relatório os critérios usados para selecionar as categorias | 2, p. 2 | Nenhum texto de critérios | ausente | Escrever os critérios em `etapa1/categorias.md` e no relatório (Fases 2 e 5) |
| 4 | Identificar, por categoria, os serviços de pelo menos dois provedores; incluir os três quando houver equivalência | 2, p. 2 | Nenhum serviço confirmado na documentação oficial | ausente | Confirmar nome atual, operação e disponibilidade das 9 ofertas (Fase 2) |
| 5 | Análise técnica: funcionalidades, formas de acesso (REST/SDK), operações, entradas e formatos, resultados, autenticação e configuração, parâmetros, limitações e diferenças entre provedores | 3, p. 2 | Nenhum capítulo | ausente | Produzir `nlp.md`, `visao.md` e `fala.md` (Fase 3) |
| 6 | Breves exemplos de código ilustrando o uso dos serviços, representando operações equivalentes entre provedores | 3, p. 2 | Nenhum exemplo | ausente | Criar 9 exemplos em `exemplos/` (Fase 3) |
| 7 | Indicar a fonte original dos exemplos adaptados de documentação ou de terceiros | 3, p. 2 | — | ausente | Registrar URL da adaptação em cada exemplo e em `referencias/fontes.md` (Fase 3) |
| 8 | Identificar a unidade de cobrança de cada serviço (requisições, imagens, minutos de áudio, caracteres etc.) | 4, p. 2–3 | Nenhum preço levantado | ausente | Levantar unidades em páginas oficiais de preço (Fase 4) |
| 9 | Registrar faixas de preço, franquias gratuitas e descontos por volume quando relevantes | 4, p. 3 | — | ausente | Registrar em `custos/premissas.csv` (Fase 4) |
| 10 | Apresentar cenários concretos de utilização com cargas equivalentes entre provedores | 4, p. 3 | — | ausente | Definir cenários por categoria e calcular (Fase 4) |
| 11 | Apresentar resultados em tabelas e/ou gráficos | 4, p. 3 | — | ausente | Gerar `custos/resultados.csv` e gráficos por código (Fase 4) |
| 12 | Explicitar todas as hipóteses usadas nos cálculos | 4, p. 3 | — | ausente | Documentar premissas e regras de cobrança (Fase 4) |
| 13 | Indicar fonte, região e data de consulta dos valores de preço | 4, p. 3 | — | ausente | Campos obrigatórios em `custos/premissas.csv`; região fixada em US East, moeda USD (Fase 4) |
| 14 | Síntese por categoria, considerando conjuntamente os resultados técnicos e econômicos | 5, p. 3 | — | ausente | Escrever síntese ao final de cada capítulo (Fase 5) |
| 15 | Repositório público no GitHub com os resultados da análise | 6, p. 3 | Repositório público já existe, com README e roteiros | parcial | Publicar os artefatos de conteúdo (Fase 6) |
| 16 | Repositório contendo relatório, exemplos de código, planilhas/dados de custo, gráficos e referências | 6, p. 3 | Nenhum desses artefatos | ausente | Produzir nas Fases 3 a 5 e publicar (Fase 6) |
| 17 | README identificando o trabalho e os integrantes e dando acesso aos artefatos | 6, p. 3 | README publicado com título, integrantes, objetivo, categorias e estrutura; links para artefatos ainda apontam para itens "a criar" | parcial | Atualizar os links quando os arquivos existirem (Fase 6) |
| 18 | Usar prioritariamente documentação oficial dos provedores, em especial APIs/SDKs e páginas de preços | 12, p. 5 | — | ausente | Registrar cada fonte em `referencias/fontes.md` com data real de consulta (Fases 2 a 4) |

## Resumo do ponto de partida (23/09/2026 — não do estado atual)

- **atendido:** 0
- **parcial:** 3 (itens 2, 15, 17)
- **ausente:** 15
- **a verificar:** 0 (ainda não há afirmações produzidas para conferir)

## Entregas da Etapa 1 derivadas deste diagnóstico

1. `etapa1/categorias.md` — seleção e critérios (itens 2, 3, 4).
2. `etapa1/nlp.md`, `etapa1/visao.md`, `etapa1/fala.md` — análise técnica, custos e síntese por categoria (itens 5, 14).
3. `exemplos/{nlp,visao,fala}/{aws,azure,gcp}.py` — 9 exemplos ilustrativos com fonte declarada (itens 6, 7).
4. `custos/premissas.csv`, `custos/calcular_custos.py`, `custos/resultados.csv`, `custos/graficos/` — análise econômica reproduzível (itens 8 a 13).
5. `referencias/fontes.md` — rastreabilidade das afirmações (item 18).
6. `relatorio/relatorio_etapa1.md` (+ versão para PDF) — consolidação (itens 3, 5, 14).
7. README atualizado e repositório publicado (itens 15, 16, 17).

## Pendências e riscos identificados neste diagnóstico

- A pesquisa de NLP mencionada no roteiro não existe; todo o conteúdo técnico depende de pesquisa nova em documentação oficial.
- Nomes de serviços mudaram desde a redação do roteiro: as ofertas de IA da Azure hoje aparecem sob **Azure AI Foundry**. O nome atual precisa ser confirmado serviço a serviço antes de escrever os capítulos.
- Preços podem não estar publicados em página aberta (risco maior na Azure, que usa calculadora). Nesse caso o valor entra como pendência declarada, sem cálculo apresentado como definitivo.
