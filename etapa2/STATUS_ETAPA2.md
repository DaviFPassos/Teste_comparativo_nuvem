# STATUS da Etapa 2 — avaliação prática

**Última atualização:** 18/10/2026

> **Nenhuma chamada real a serviço de IA foi feita na Etapa 2.** Não há resultado experimental neste repositório ainda. Tudo o que existe foi verificado offline, e os dados simulados usados nas verificações ficam em `etapa2/simulacoes/`, fora do git.

## Onde estamos

| Fase do roteiro | Estado | O que falta |
|---|---|---|
| 1 — Conferir a Etapa 1 e a viabilidade | **Concluída** | — |
| 2 — Preparar dados e protocolo | **Em andamento** | Anotação pelos dois integrantes; aprovação da metodologia |
| 3 — Implementar e fazer o piloto | **Implementado localmente** · piloto real **não executado** | Credenciais Azure e Google; rodar o piloto |
| 4 — Avaliação final | Planejado | Depende das fases 2 e 3 |
| 5 — Processar e interpretar | **Implementado localmente** (`analisar.py`) | Depende da coleta |
| 6 — Confrontar com a Etapa 1 | Planejado | Depende da coleta |
| 7 — Consolidar e entregar | Planejado | — |

## Decisões tomadas pelo grupo (18/10/2026)

| Decisão | Valor |
|---|---|
| Provedores | **Azure + Google** |
| Fonte dos textos | **Dataset público**: B2W-Reviews01 (CC BY-NC-SA 4.0) |
| Gabarito | **Dois integrantes**, independentes, com discussão das divergências |
| Orçamento | **US$ 0 — só franquia** (Azure F0; Google na faixa gratuita) |

As demais decisões do protocolo estão **propostas** em [`metodologia.md`](metodologia.md) e aguardam aprovação.

## Viabilidade (Fase 1)

| Item | Situação |
|---|---|
| Operação equivalente nos dois | Confirmada na Etapa 1: Azure *Sentiment analysis* e Google `analyzeSentiment`, um documento por chamada |
| Limites de entrada | Azure 5.120 caracteres/documento; Google 1.000.000 bytes. Maior texto sorteado: 1.168 caracteres |
| Limites de taxa | Azure F0: 300 req/min (conferido em 18/10/2026); Google: 600 req/min |
| Custo previsto | ~330 unidades por rodada completa (piloto + candidatos) em cada provedor; pior caso com 3 tentativas: ~1.000. Franquia: 5.000/mês em cada. **US$ 0,00 estimado** |
| SDKs | `azure-ai-textanalytics` 5.4.0 e `google-cloud-language` **2.21.0** — as mesmas versões da Etapa 1, para o projeto ter uma versão só de cada biblioteca. A demonstração de 18/10/2026 rodou com 2.22.0 (registrado no `ambiente.json` dela); a coleta usará 2.21.0 |
| Credenciais nesta máquina | **Google: configurado** (18/10/2026). **Azure: ainda não** |

## Artefatos

| Artefato | Arquivo | Estado |
|---|---|---|
| Protocolo | `etapa2/metodologia.md` | **Rascunho**, aguardando aprovação |
| Origem, licença e limitações dos dados | `etapa2/dados/README.md` | Concluído |
| Guia de anotação | `etapa2/dados/guia_de_anotacao.md` | Concluído |
| Candidatos sorteados | `etapa2/dados/candidatos_piloto.csv` (30), `candidatos_teste.csv` (300) | **Sorteados**, reprodutíveis (mesmo SHA-256 em duas execuções) |
| Planilhas de anotação | `etapa2/dados/anotacao/planilha_A.csv`, `planilha_B.csv` | **Geradas, em branco** |
| Conjuntos congelados | `piloto.csv`, `teste.csv`, `exploratorio_misto.csv` | Não existem: dependem da anotação |
| Amostragem | `etapa2/src/amostrar.py` | Implementado |
| Anotação e concordância | `etapa2/src/anotacao.py` | Implementado |
| Adaptadores | `etapa2/src/provedores/` (Azure, Google, simulado) | Implementado, testado com os SDKs reais e a rede substituída |
| Executor | `etapa2/src/executar.py` | Implementado; executado só em modo simulado |
| Normalização | `etapa2/src/normalizar.py` (regra v1) | Implementado |
| Trava de orçamento | `etapa2/src/custo.py` | Implementado |
| Análise | `etapa2/src/analisar.py` | Implementado; executado só com dados simulados |
| Testes offline | `etapa2/rodar_testes.py` — **66 testes** | Passando |
| Instruções | `etapa2/COMO_EXECUTAR.md` | Concluído |

## O que bloqueia a coleta — e a ação exata

| # | Bloqueio | Quem | Ação |
|---|---|---|---|
| 1 | Gabarito | **Dois integrantes** | Preencher `planilha_A.csv` e `planilha_B.csv` seguindo o guia; nomes em `anotacao/anotadores.json`; depois `anotacao.py consolidar` → discutir divergências → `montar` |
| 2 | Protocolo | Grupo | Revisar `metodologia.md`, alterar o que for preciso, registrar a aprovação |
| 3 | Credenciais Azure | Quem tiver a conta | Recurso **Language F0** em East US → endpoint e chave no `.env` (passo 2 de `COMO_EXECUTAR.md`) |
| 4 | ~~Credenciais Google~~ | — | **Resolvido em 18/10/2026** na máquina do Davi: projeto com faturamento, `language.googleapis.com` ativada, login ADC com projeto de cota, `GOOGLE_CLOUD_PROJECT` no `.env`. Uma chamada de verificação respondeu (1 unidade). Falta só o alerta de orçamento de US$ 1, recomendado |

Os itens 1–2 e 3–4 podem andar em paralelo. O piloto só depende de 3–4 e de `piloto.csv` (item 1).

## Execuções

| ID | Conjunto | Provedores | Tipo | Resultado |
|---|---|---|---|---|
| `20261018T191648Z-demonstracao-r1` | `dados/demonstracao.csv` — 8 frases **do guia de anotação**, fora do experimento | Google | **Demonstração real** (`--demonstracao`), em `etapa2/demonstracoes/` | 8/8 respostas, mediana 1.074 ms. **Não é resultado do experimento**: rótulos ilustrativos, n = 8, frases difíceis de propósito |
| — | — | — | — | Nenhuma execução do experimento. Também em 18/10/2026: uma chamada de verificação de credencial (não gravada) e o teste real do exemplo da Etapa 1 (`testes/evidencias/nlp_google.json`) |

## Observações registradas

- **O README do B2W diz que o separador é ponto e vírgula; o arquivo real usa vírgula.** O script lê com vírgula.
- **A fonte contém códigos de rastreio dos Correios e números de protocolo/nota fiscal** (18 textos). Foram tratados como dado pessoal e excluídos.
- **`neutro` deve ficar escasso.** Avaliações de 3 estrelas tendem a ser mistas, não neutras. Se a classe ficar abaixo de 50, a decisão (aceitar ou sortear lote extra) tem de ser tomada antes das chamadas.
- **A Azure e o guia de anotação definem "misto" de jeitos diferentes.** A Azure é mecânica (qualquer sentença positiva + qualquer negativa → `mixed`); o guia é por predominância. Previsões `mixed` da Azure em textos que o gabarito considera `positivo` ou `negativo` são esperadas — e são uma pergunta da Fase 6.
- **A primeira chamada é mais lenta (aquecimento).** Na demonstração real, a 1ª chamada levou 1.819 ms e as outras sete entre 1.041 e 1.099 ms: é a abertura da conexão e a obtenção do token. Com n pequeno ela vira o p95. **Decisão a tomar antes do teste**: descartar uma chamada de aquecimento por provedor ou reportá-la à parte (proposta em `metodologia.md`).
- **O Google tende a pôr frases de sinais opostos perto de zero.** Na demonstração, "Bom, mas a tampa é meio frágil.", "A cor é bonita, mas parou de funcionar..." e "Produto ótimo, porém a entrega atrasou..." receberam score ±0,1 → `neutro`, e a ironia "Ótimo, veio faltando peça." recebeu +0,7. São 8 frases escolhidas por serem difíceis — **uma pista para a Fase 6, não uma conclusão**.
- **Os dois SDKs repetem chamadas sozinhos por padrão** (o do Google por até 600 s). Os adaptadores desligam isso para que cada tentativa seja medida e registrada; os testes provam que só uma requisição sai.

## Lista final de conferência (roteiro, seção 11)

- [x] O recorte de sentimento foi justificado a partir da Etapa 1.
- [ ] Pelo menos dois provedores foram realmente testados. — *bloqueado: credenciais*
- [ ] Dados, origem, limitações e gabarito foram documentados. — *origem e limitações: sim; gabarito: aguardando anotação*
- [ ] Piloto e teste final estão separados. — *candidatos separados; conjuntos montados após a anotação*
- [ ] Metodologia, limiares, classes e política de falhas foram definidos antes da avaliação final. — *rascunho aguardando aprovação*
- [ ] Os mesmos textos foram usados nas comparações, com exclusões explicadas. — *garantido pelo executor; falta a coleta*
- [ ] Respostas brutas, tentativas, configurações e versões foram preservadas sem segredos. — *implementado e testado; falta a coleta*
- [x] Métricas e gráficos são calculados por código a partir dos registros.
- [x] Qualidade, cobertura e falhas são apresentadas com denominadores claros.
- [x] Estimativas de custo estão distinguidas dos valores observados.
- [ ] Resultados foram confrontados com as conclusões da Etapa 1.
- [ ] Limitações impedem generalizações indevidas para outras tarefas ou populações. — *limitações dos dados redigidas; falta o relatório*
- [ ] Relatório, código, dados/instruções, metodologia, registros e gráficos estão no mesmo repositório público.
- [x] README explica como reproduzir análises e como realizar nova coleta, sem expor credenciais. — *em `COMO_EXECUTAR.md`*

## Próxima ação

**Anotar** (bloqueio 1) e **criar as contas** (bloqueios 3–4), em paralelo. Assim que existirem `piloto.csv` e o `.env`, rodar o piloto.
