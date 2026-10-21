# STATUS do projeto

**Última atualização:** 19/10/2026 (Etapa 2 concluída: coleta nos dois provedores, análise e relatório; falta conferir o custo observado). Etapa 1 publicada e revisada em 26/09/2026.

## Objetivo atual

**Etapa 2 — Avaliação prática** (milestones 7 a 13, issues #28–#56): análise de sentimento em português na Azure e no Google. A Etapa 1 (milestones 1 a 6) foi concluída antes do prazo de 30/09/2026.

## Situação

**Etapa 1 publicada** no repositório em `abcd2f7` e **revisada em 26/09/2026**. **Todas as 27 issues fechadas e os 6 milestones completos**, 4 dias antes do prazo de 30/09/2026.

O repositório está **público** em https://github.com/DaviFPassos/Teste_comparativo_nuvem (exigência da seção 6 do enunciado).

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
| Diagnóstico das exigências | `etapa1/diagnostico.md` | **Documento histórico** (retrato do ponto de partida em 23/09/2026); não descreve o estado atual |
| Seleção e critérios das categorias | `etapa1/categorias.md` | Concluído |
| Capítulo de NLP | `etapa1/nlp.md` | Concluído, com custo e síntese |
| Capítulo de visão computacional | `etapa1/visao.md` | Concluído, com custo e síntese |
| Capítulo de fala para texto | `etapa1/fala.md` | Concluído, com custo e síntese |
| Exemplos de código | `exemplos/` — 9 arquivos | **Testados sem chamar os serviços reais**: `uv run testes/rodar_testes.py`, 18 testes, 10 de 10 defeitos injetados detectados |
| Premissas de preço | `custos/premissas.csv` | 9 preços, todos `verificado_oficial` |
| Franquias | `custos/franquias.csv` | 8 verificadas, 1 não localizada; cada uma com `aplicavel_ao_cenario` e justificativa |
| Cálculo de custos | `custos/calcular_custos.py` | Determinístico, só biblioteca padrão |
| Conferência das contas | `custos/verificar_calculos.py` | 31 conferências, todas passando |
| Resultados | `custos/resultados.csv` | 22 linhas (5 comprimentos de texto × 3 provedores + visão + fala) |
| Gráficos | `custos/graficos/` — 3 PNG | Gerados por código a partir do CSV |
| Fontes | `referencias/fontes.md` | 52 fontes com URL, data e afirmação sustentada, incluindo a seção da Etapa 2 (ET2-*, 18/10/2026) |
| Relatório | `relatorio/relatorio_etapa1.md` + `.html` | Montado por script a partir dos capítulos |
| PDF do relatório | `pdfs/relatorio_tecnico_etapa1.pdf` | **45 páginas**, A4, gerado por `relatorio/gerar_pdf.py`. Passou de 28 para 43 na revisão de 26/09: a comparação técnica inteira e os trechos de código entraram no relatório, para que ele seja legível fora do repositório. Todos os links são URLs do GitHub |
| README | `README.md` | Com integrantes, achados, links e reprodução |

## Decisões tomadas

| Decisão | Valor | Justificativa |
|---|---|---|
| Categorias | NLP, visão computacional, fala para texto | Três modalidades de entrada distintas (texto, imagem, áudio) |
| Operação comparada | Sentimento de documento · detecção de rótulos · transcrição em lote | Mesma tarefa nos três provedores |
| Região e moeda | `us-east-1` (AWS), `East US` (Azure), global em NLP/visão e `us-central1` em fala (Google); USD | US East é a referência das tabelas da AWS e da Azure. O `us-central1` do Google **não** é US East e está declarado como limitação |
| Fonte dos preços | APIs públicas de preço dos provedores | As páginas comerciais da Azure e do Google servem as tabelas por JavaScript |
| Base da comparação de custo | Sem franquia | As franquias têm naturezas diferentes (promocional, tier separado, faixa da tabela) |
| Gerenciador de pacotes | `uv` com blocos PEP 723 | Cada script declara suas dependências; não exige venv nem instalação manual |
| Lockfile | Só em `gerar_graficos.py` | É o único script com dependência externa que de fato executa. Os 9 exemplos não são executados nesta etapa, e travar versões de código que ninguém roda registraria precisão inexistente |
| PDF | HTML exportado pelo navegador | Evita instalar LaTeX; o grupo controla o visual final |

## Pendências

| Pendência | Motivo | Ação necessária |
|---|---|---|
| Cotas do Amazon Transcribe | Página não acessível na consulta de 23/09/2026 | Declarada como limitação no relatório; reverificar se necessário |
| Franquia da tabela Recognition V2 do Google | Não localizada (a de 60 min é da API V1) | Declarada como pendência em `custos/franquias.csv`; nada é descontado sem valor verificado |
| Limites de entrada do `BatchRecognize` do Google | Não localizados nas páginas consultadas | Declarada na seção 3.5 de `etapa1/fala.md` |
| Valor padrão de `MinConfidence` do `DetectLabels` | Não localizado | O exemplo fixa o parâmetro explicitamente |
| Limite de tags por imagem no Azure Image Analysis | Não localizado | Declarada em `etapa1/visao.md` |

Nenhuma dessas lacunas foi preenchida por estimativa. **Fechada em 26/09/2026:** os limites de entrada da transcrição em lote da Azure, antes não localizados, foram encontrados na tabela oficial de cotas e estão na seção 3.5 de `etapa1/fala.md`.

## Conferência executada em 26/09/2026

- Todos os links relativos do README resolvem
- Nenhuma credencial no repositório nem no histórico do git; os exemplos usam 13 variáveis de ambiente
- Os **14** scripts Python compilam
- `calcular_custos.py` é determinístico (mesmo md5 ao regerar)
- As **31** conferências de custo passam
- O PDF não contém nenhum link `file://` para caminho local
- O repositório responde 200 a uma consulta anônima da API do GitHub (é público)

## Revisão de 26/09/2026 — o que foi corrigido

Uma revisão externa apontou erros técnicos e de interpretação. Todos foram conferidos contra a documentação oficial e corrigidos:

| # | Problema apontado | Correção aplicada |
|---|---|---|
| 1 | O trabalho afirmava que a Azure **não** retorna `mixed` no nível de documento e que só a AWS distingue sentimento misto | Errado. A regra oficial devolve `mixed` quando há sentenças positivas e negativas no mesmo documento: três scores, **quatro rótulos**. Corrigido em `nlp.md`, `categorias.md`, no exemplo `azure_language.py` e no relatório, com a distinção real entre os dois mecanismos preservada |
| 2 | O cálculo descontava as 5 h gratuitas do tier F0 da Azure da **transcrição em lote**, que não existe no F0 | Corrigido. A cota oficial registra "Not available for F0"; o cenário volta a **$30,00**. A regra virou explícita: `franquias.csv` ganhou `aplicavel_ao_cenario` + justificativa, `resultados.csv` ganhou `franquia_aplicada`, e o F0 também deixou de ser abatido em NLP e visão |
| 3 | A análise de fala dizia que só o Google expõe escolha de modelo e deixava a diarização da Azure em branco | Corrigido. A Azure aceita `model` (base, *custom speech* ou Whisper) e configura diarização por `diarizationEnabled`/`diarization`. A recomendação de diarização agora inclui os três |
| 4 | A recomendação "acima de ~4.000 caracteres: indiferente no custo" | Delimitada. O empate só vale em múltiplos exatos de 1.000 caracteres: o cenário passou a incluir **4.100 caracteres**, onde a AWS cobra $410,00 contra $500,00 dos outros dois. Sete conferências novas travam esse resultado |
| 5 | A promessa de "prazo previsível" atribuída à AWS | Retirada. Nenhum dos três publica prazo garantido de conclusão; o texto agora descreve a assimetria de informação e de oferta, sem atribuir previsibilidade |
| 6 | Os três links do PDF apontavam para `file:///home/...` da máquina que gerou | Corrigidos para URLs do GitHub. O gerador agora recusa publicar link local |
| 7 | "$30 é um terço de $100" | É 30% — redução de 70%, ou 3,3× |
| 8 | Documentos contraditórios: capítulos com "preços não verificados", `categorias.md` com preços "não levantados", diagnóstico lido como pendência atual, contagens erradas em `STATUS.md` e `DEPENDENCIAS.md` | Todos sincronizados. O diagnóstico ganhou tarja de documento histórico |
| 9 | `us-central1` agrupada como "US East" | Corrigido em `fala.md`, no relatório e aqui; virou limitação declarada |
| 10 | Exemplo do Google usando `resultado.transcript`, campo descontinuado | Trocado por `inline_result.transcript`, com a fonte da referência |
| 11 | PDF/TIFF do Cloud Vision listados junto com `images:annotate` | Separados: PDF e TIFF exigem `files:annotate` |
| 12 | Custo do Google "sem franquia" apresentado como cobrança habitual | Declarado como simulação: a faixa de 0,00 USD é permanente, logo a cobrança habitual é $95,00 (NLP) e $148,50 (visão) |
| 13 | Premissas de áudio incompletas | Declaradas: mono, idioma fixo, sem recursos adicionais, e exclusão explícita de armazenamento e transferência |

## Próxima ação concreta

**Etapa 2:** conferir o custo observado nos consoles do Google e da Azure e registrar no relatório. Detalhes em [`etapa2/STATUS_ETAPA2.md`](etapa2/STATUS_ETAPA2.md).

## Etapa 2

**Iniciada em 18/10/2026; coleta e relatório concluídos em 19/10/2026.** Roteiro em `etapas/ROTEIRO_ETAPA2.md`; progresso em [`etapa2/STATUS_ETAPA2.md`](etapa2/STATUS_ETAPA2.md).

| Item | Situação |
|---|---|
| Decisões do grupo | Azure + Google · dataset público B2W-Reviews01 · gabarito de dois anotadores (A com rótulos gerados por IA; B humano) · orçamento US$ 0 |
| Fase 1 — viabilidade | Concluída |
| Fase 2 — dados e protocolo | Gabarito com kappa 0,791; teste com 115 textos; metodologia **aprovada** |
| Fase 3 — programa e piloto | 93 testes offline; pilotos 30/30 nos dois provedores |
| Coleta e análise | Teste 115/115 e exploratório 39/39 nos dois; sem diferença significativa de qualidade (McNemar p = 0,541); US$ 0 estimado |
| Relatório | [`relatorio/relatorio_etapa2.md`](relatorio/relatorio_etapa2.md) e [`pdfs/relatorio_tecnico_etapa2.pdf`](pdfs/relatorio_tecnico_etapa2.pdf) |
