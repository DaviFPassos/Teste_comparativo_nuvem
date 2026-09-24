# STATUS do projeto

**Última atualização:** 24/09/2026 (Etapa 1 concluída e publicada)

## Objetivo atual

Concluir a **Etapa 1 — Análise comparativa** (milestones 1 a 6, issues #1 a #27). Prazo: **30/09/2026**.

## Situação

**Etapa 1 publicada** no repositório em `abcd2f7`. **Todas as 27 issues fechadas e os 6 milestones completos**, 6 dias antes do prazo de 30/09/2026.

| Fase | Milestone | Issues | Situação |
|---|---|---|---|
| 1 — Ler os documentos e diagnosticar | 1 | #1–#4 | ✅ Concluída |
| 2 — Confirmar ofertas e critérios comuns | 2 | #5–#8 | ✅ Concluída |
| 3 — Completar os capítulos e exemplos | 3 | #9–#13 | ✅ Concluída |
| 4 — Construir e conferir os custos | 4 | #14–#19 | ✅ Concluída |
| 5 — Escrever as sínteses e consolidar | 5 | #20–#23 | ✅ Concluída |
| 6 — Preparar a entrega no GitHub | 6 | #24–#27 | ✅ Concluída |

## Artefatos produzidos

| Artefato | Arquivo | Estado |
|---|---|---|
| Diagnóstico das exigências | `etapa1/diagnostico.md` | Concluído |
| Seleção e critérios das categorias | `etapa1/categorias.md` | Concluído |
| Capítulo de NLP | `etapa1/nlp.md` | Concluído, com custo e síntese |
| Capítulo de visão computacional | `etapa1/visao.md` | Concluído, com custo e síntese |
| Capítulo de fala para texto | `etapa1/fala.md` | Concluído, com custo e síntese |
| Exemplos de código | `exemplos/` — 9 arquivos | Ilustrativos, **não executados** (permitido pela seção 3 do enunciado) |
| Premissas de preço | `custos/premissas.csv` | 9 preços, todos `verificado_oficial` |
| Franquias | `custos/franquias.csv` | 8 verificadas, 1 não localizada |
| Cálculo de custos | `custos/calcular_custos.py` | Determinístico, só biblioteca padrão |
| Conferência das contas | `custos/verificar_calculos.py` | 18 conferências, todas passando |
| Resultados | `custos/resultados.csv` | 19 linhas |
| Gráficos | `custos/graficos/` — 3 PNG | Gerados por código a partir do CSV |
| Fontes | `referencias/fontes.md` | 38 fontes com URL, data e afirmação sustentada |
| Relatório | `relatorio/relatorio_etapa1.md` + `.html` | Montado por script a partir dos capítulos |
| PDF do relatório | `pdfs/relatorio_etapa1.pdf` | 30 páginas, A4, gerado por `relatorio/gerar_pdf.py` |
| README | `README.md` | Com integrantes, achados, links e reprodução |

## Decisões tomadas

| Decisão | Valor | Justificativa |
|---|---|---|
| Categorias | NLP, visão computacional, fala para texto | Três modalidades de entrada distintas (texto, imagem, áudio) |
| Operação comparada | Sentimento de documento · detecção de rótulos · transcrição em lote | Mesma tarefa nos três provedores |
| Região e moeda | US East, USD | Região de referência das três tabelas, com as nove ofertas disponíveis |
| Fonte dos preços | APIs públicas de preço dos provedores | As páginas comerciais da Azure e do Google servem as tabelas por JavaScript |
| Base da comparação de custo | Sem franquia | As franquias têm naturezas diferentes (promocional, tier separado, faixa da tabela) |
| Gerenciador de pacotes | `uv` com blocos PEP 723 | Cada script declara suas dependências; não exige venv nem instalação manual |
| Lockfile | Só em `gerar_graficos.py` | É o único script com dependência externa que de fato executa. Os 9 exemplos não são executados nesta etapa, e travar versões de código que ninguém roda registraria precisão inexistente |
| PDF | HTML exportado pelo navegador | Evita instalar LaTeX; o grupo controla o visual final |

## Pendências

| Pendência | Motivo | Ação necessária |
|---|---|---|
| Cotas do Amazon Transcribe | Página não acessível na consulta de 23/09/2026 | Declarada como limitação no relatório; reverificar se necessário |
| Franquia da tabela Recognition V2 do Google | Não localizada (a de 60 min é da API V1) | Declarada como pendência em `custos/franquias.csv` |

Nenhuma dessas lacunas foi preenchida por estimativa.

## Conferência final executada em 24/09/2026

- Todos os links relativos do README resolvem
- Nenhuma credencial no repositório; os exemplos usam 13 variáveis de ambiente
- Os 12 scripts Python compilam
- `calcular_custos.py` é determinístico (mesmo md5 ao regerar)
- As 18 conferências de custo passam

## Próxima ação concreta

Iniciar a **Etapa 2** pela Fase 1 (milestone 7).

Para a Etapa 2, as issues #28, #29, #30, #31 e #35 já receberam os insumos produzidos na Etapa 1: ofertas confirmadas, diferenças de formato de saída entre os provedores, estimativa de custo do experimento (menos de US$ 1, dentro das franquias gratuitas) e sugestão de divisão do trabalho entre os três integrantes.

## Etapa 2

Planejada em `etapas/ROTEIRO_ETAPA2.md` (milestones 7 a 13, issues #28–#56). Começa após a publicação da Etapa 1.
