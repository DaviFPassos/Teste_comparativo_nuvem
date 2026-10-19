# STATUS da Etapa 2 — avaliação prática

**Última atualização:** 19/10/2026

> **Coleta concluída em 19/10/2026 nos dois provedores.** Resultados, análise conjunta e conclusões em [`relatorio/relatorio_etapa2.md`](../relatorio/relatorio_etapa2.md). Falta só conferir o **custo observado** nos consoles. Os dados simulados das verificações offline ficam em `etapa2/simulacoes/`, fora do git.

## Onde estamos

| Fase do roteiro | Estado | O que falta |
|---|---|---|
| 1 — Conferir a Etapa 1 e a viabilidade | **Concluída** | — |
| 2 — Preparar dados e protocolo | **Concluída** (19/10/2026) | — Gabarito: kappa 0,791; teste com 115 textos (50/50/15); metodologia aprovada |
| 3 — Implementar e fazer o piloto | **Concluída** (19/10/2026) | — Pilotos 30/30 nos dois; limiar mantido |
| 4 — Avaliação final | **Concluída** (19/10/2026) | — Teste 115/115 e exploratório 39/39 nos dois |
| 5 — Processar e interpretar | **Concluída** | — Análise conjunta em `resultados/comparacoes/` |
| 6 — Confrontar com a Etapa 1 | **Concluída** | — E1–E13 com conclusão em `expectativas_etapa1.md` |
| 7 — Consolidar e entregar | **Concluída**, salvo o custo observado | Conferir o custo nos consoles do Google e da Azure |

## Decisões tomadas pelo grupo (18/10/2026)

| Decisão | Valor |
|---|---|
| Provedores | **Azure + Google** |
| Fonte dos textos | **Dataset público**: B2W-Reviews01 (CC BY-NC-SA 4.0) |
| Gabarito | **Dois anotadores**, independentes, com discussão das divergências. A: Davi, com rótulos gerados por IA (19/10/2026); B: Rafael |
| Orçamento | **US$ 0 — só franquia** (Azure F0; Google na faixa gratuita) |

As demais decisões do protocolo foram **aprovadas em 19/10/2026** em [`metodologia.md`](metodologia.md), por Davi em nome do grupo. Entre elas: avaliação complementar sem a classe neutra e exclusão de 3 textos com nome do autor (`dados/exclusoes.csv`).

## Viabilidade (Fase 1)

| Item | Situação |
|---|---|
| Operação equivalente nos dois | Confirmada na Etapa 1: Azure *Sentiment analysis* e Google `analyzeSentiment`, um documento por chamada |
| Limites de entrada | Azure 5.120 caracteres/documento; Google 1.000.000 bytes. Maior texto sorteado: 1.168 caracteres |
| Limites de taxa | Azure F0: 300 req/min (conferido em 18/10/2026); Google: 600 req/min |
| Custo previsto | ~330 unidades por rodada completa (piloto + candidatos) em cada provedor; pior caso com 3 tentativas: ~1.000. Franquia: 5.000/mês em cada. **US$ 0,00 estimado** |
| SDKs | `azure-ai-textanalytics` 5.4.0 e `google-cloud-language` **2.21.0** — as mesmas versões da Etapa 1, para o projeto ter uma versão só de cada biblioteca. A demonstração de 18/10/2026 rodou com 2.22.0 (registrado no `ambiente.json` dela); a coleta usará 2.21.0 |
| Credenciais | **Google:** configurado na máquina do Davi (18/10/2026). **Azure:** recurso e chave funcionando na máquina do Rafael (verificação com 5 frases, 18/10/2026) |

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
| Testes offline | `etapa2/rodar_testes.py` — **93 testes** | Passando |
| Instruções | `etapa2/COMO_EXECUTAR.md` | Concluído |
| **Expectativas da Etapa 1** (para o confronto da seção 10) | `etapa2/expectativas_etapa1.md` | **Registradas antes da coleta** (13 itens); evidência de configuração e de demonstração já anotada, marcada como fora do experimento |
| **Relatório da Etapa 2** | `relatorio/relatorio_etapa2.md` | **Esqueleto**: seções definidas preenchidas; resultados e conclusões marcados PENDENTE |
| Análise de execuções de máquinas diferentes | `analisar.py --execucao <id1> <id2>` | Implementado e testado; confere dataset, regra e tipo, e marca a latência como não comparável |
| Aquecimento na coleta | `executar.py`, `"aquecimento": true` | Implementado; excluído da latência e do sucesso, contado no custo |
| **Painel de apresentação (Google e Azure)** | `etapa2/painel/` — `servidor.py` + `index.html` | Implementado e testado (17 testes). Ativa sozinho o provedor com credencial em cada máquina. **Google verificado contra o serviço real** em 18/10/2026. **Azure verificada só offline** (SDK real, rede substituída): a primeira chamada real será no laptop do Rafael |

## O que bloqueava a coleta (tudo resolvido)

| # | Bloqueio | Quem | Ação |
|---|---|---|---|
| 1 | ~~Gabarito~~ | — | **Concluído em 19/10/2026**: kappa 0,791; 43 divergências decididas (prevalece o anotador humano); `piloto.csv` (30), `teste.csv` (115: 50 positivos, 50 negativos, 15 neutros) e `exploratorio_misto.csv` (39) congelados |
| 2 | ~~Protocolo~~ | — | **Aprovado em 19/10/2026** |
| 3 | ~~Credenciais Azure~~ | Rafael | **Funcionando na máquina do Rafael.** Confirmar no portal que o recurso é **F0** (exigência do orçamento US$ 0) |
| 3a | **Os dois provedores na mesma máquina** — *na apresentação, cada um mostra o seu no próprio laptop (decidido em 18/10/2026); para a coleta do experimento, ainda a decidir* | Grupo | A metodologia intercala Azure e Google no mesmo texto, na mesma máquina. Opções: (a) **recomendada** — o Davi adiciona o Rafael ao projeto Google com o papel *Service Usage Consumer*, e o Rafael roda tudo na máquina dele com a própria conta Google, sem compartilhar chave; (b) o Rafael passa a chave da Azure ao Davi; (c) cada um roda o seu provedor, e a metodologia declara que a latência não é comparável |
| 4 | ~~Credenciais Google~~ | — | **Resolvido em 18/10/2026** na máquina do Davi: projeto com faturamento, `language.googleapis.com` ativada, login ADC com projeto de cota, `GOOGLE_CLOUD_PROJECT` no `.env`. Uma chamada de verificação respondeu (1 unidade). Falta só o alerta de orçamento de US$ 1, recomendado |

Os itens 1–2 e 3–4 podem andar em paralelo. O piloto só depende de 3–4 e de `piloto.csv` (item 1).

## Execuções

| ID | Conjunto | Provedores | Tipo | Resultado |
|---|---|---|---|---|
| `20261018T151637-azure-rafael` | `dados/fumaca_azure.csv` — 5 frases (3 do roteiro, 2 do autor) | Azure | **Verificação real** pelo Rafael, com o pipeline do ramo `feat/azure-nlp-sentimento`; em `etapa2/demonstracoes/` | 5/5 respostas; 1ª chamada 1.580 ms, demais ~843 ms. **Não é resultado do experimento** |
| `20261018T191648Z-demonstracao-r1` | `dados/demonstracao.csv` — 8 frases **do guia de anotação**, fora do experimento | Google | **Demonstração real** (`--demonstracao`), em `etapa2/demonstracoes/` | 8/8 respostas, mediana 1.074 ms. **Não é resultado do experimento**: rótulos ilustrativos, n = 8, frases difíceis de propósito |
| `20261019T132214Z-demonstracao-r1` | `dados/demonstracao.csv` — as mesmas 8 frases | Azure | **Demonstração real** pelo Rafael, no laptop dele, com o programa do `main` (`f83feff`); relato em `etapa2/RELATORIO_AZURE_RAFAEL.md` | 8/8 respostas, 4 de 6 válidas certas, mediana 224 ms (p95 262 ms), nenhuma previsão `misto`. **Não é resultado do experimento** |
| `20261019T171950Z-piloto-r1` | `dados/piloto.csv` — 30 textos | Google | **Piloto** (fora das métricas principais) | 30/30; acurácia 87,0% (23 textos de 3 classes); limiar ±0,25 mantido |
| `20261019T172351Z-teste-r1` | `dados/teste.csv` — 115 textos | Google | **Teste do experimento** | 115/115; acurácia 78,3%, macro-F1 71,2%; sem a classe neutra 81,0%; mediana 1.092 ms; 116 unidades, US$ 0 |
| `20261019T172623Z-exploratorio_misto-r1` | `dados/exploratorio_misto.csv` — 39 textos | Google | **Conjunto exploratório** | 39/39; 24 → neutro, 11 → positivo, 4 → negativo |
| `20261019T174849Z-piloto-r1` | `dados/piloto.csv` — 30 textos | Azure | **Piloto**, no laptop do Rafael | 30/30; acurácia 87,0% (23 textos); mediana 258 ms |
| `20261019T175816Z-teste-r1` | `dados/teste.csv` — 115 textos | Azure | **Teste do experimento**, no laptop do Rafael | 115/115; acurácia 74,8%, macro-F1 65,9%; sem a classe neutra 82,0%; 9 previsões `misto`; mediana 253 ms; 116 unidades, US$ 0 |
| `20261019T175924Z-exploratorio_misto-r1` | `dados/exploratorio_misto.csv` — 39 textos | Azure | **Conjunto exploratório**, no laptop do Rafael | 39/39; 10 → misto, 21 → positivo, 8 → negativo |
| `comparacao__20261019T172351Z-teste-r1__20261019T175816Z-teste-r1` | — | Os dois | **Análise conjunta** (`resultados/comparacoes/`) | McNemar p = 0,541 (3 classes) e 1,000 (sem neutro): **sem diferença significativa** |
| — | — | — | — | Antes do experimento: Também em 18/10/2026: uma chamada de verificação de credencial (não gravada) e o teste real do exemplo da Etapa 1 (`testes/evidencias/nlp_google.json`) |

## Observações registradas

- **O README do B2W diz que o separador é ponto e vírgula; o arquivo real usa vírgula.** O script lê com vírgula.
- **A fonte contém códigos de rastreio dos Correios e números de protocolo/nota fiscal** (18 textos). Foram tratados como dado pessoal e excluídos.
- **`neutro` deve ficar escasso.** Avaliações de 3 estrelas tendem a ser mistas, não neutras. Se a classe ficar abaixo de 50, a decisão (aceitar ou sortear lote extra) tem de ser tomada antes das chamadas.
- **A Azure e o guia de anotação definem "misto" de jeitos diferentes.** A Azure é mecânica (qualquer sentença positiva + qualquer negativa → `mixed`); o guia é por predominância. Previsões `mixed` da Azure em textos que o gabarito considera `positivo` ou `negativo` são esperadas — e são uma pergunta da Fase 6.
- **A primeira chamada é mais lenta (aquecimento) — nos dois provedores.** Na Azure (verificação do Rafael), 1.580 ms contra ~843 ms. No Google, na demonstração real, a 1ª chamada levou 1.819 ms e as outras sete entre 1.041 e 1.099 ms: é a abertura da conexão e a obtenção do token. Com n pequeno ela vira o p95. **Decisão a tomar antes do teste**: descartar uma chamada de aquecimento por provedor ou reportá-la à parte (proposta em `metodologia.md`).
- **O Google tende a pôr frases de sinais opostos perto de zero.** Na demonstração, "Bom, mas a tampa é meio frágil.", "A cor é bonita, mas parou de funcionar..." e "Produto ótimo, porém a entrega atrasou..." receberam score ±0,1 → `neutro`, e a ironia "Ótimo, veio faltando peça." recebeu +0,7. São 8 frases escolhidas por serem difíceis — **uma pista para a Fase 6, não uma conclusão**.
- **A Azure não marcou `misto` em frases de sinais opostos escritas como uma sentença só** (demonstração de 19/10/2026). "Bom, mas a tampa é meio frágil." → `positive` (0,86); "A cor é bonita, mas parou de funcionar..." → `negative` (0,62); "Produto ótimo, porém a entrega atrasou..." → `positive` (0,98). Nas três, a Azure encontrou **uma** sentença, e o `mixed` só nasce de sentenças diferentes com sinais opostos. A ironia "Ótimo, veio faltando peça." também enganou a Azure (`positive`, 1,00), como o Google. **Pista para E4 e E5, não conclusão.**
- **Os dois SDKs repetem chamadas sozinhos por padrão** (o do Google por até 600 s). Os adaptadores desligam isso para que cada tentativa seja medida e registrada; os testes provam que só uma requisição sai.

## Lista final de conferência (roteiro, seção 11)

- [x] O recorte de sentimento foi justificado a partir da Etapa 1.
- [x] Pelo menos dois provedores foram realmente testados. — *Azure e Google, 115/115 cada*
- [x] Dados, origem, limitações e gabarito foram documentados. — *kappa 0,791; manifesto em `dados/manifesto_conjuntos.json`*
- [x] Piloto e teste final estão separados. — *`piloto.csv` (30) e `teste.csv` (115), congelados em 19/10/2026*
- [x] Metodologia, limiares, classes e política de falhas foram definidos antes da avaliação final. — *aprovada em 19/10/2026*
- [x] Os mesmos textos foram usados nas comparações, com exclusões explicadas. — *mesmo SHA-256 conferido pela análise; 115/115 na interseção*
- [x] Respostas brutas, tentativas, configurações e versões foram preservadas sem segredos. — *em `etapa2/resultados/`, sanitizadas*
- [x] Métricas e gráficos são calculados por código a partir dos registros.
- [x] Qualidade, cobertura e falhas são apresentadas com denominadores claros.
- [x] Estimativas de custo estão distinguidas dos valores observados.
- [x] Resultados foram confrontados com as conclusões da Etapa 1. — *relatório, seção 7*
- [x] Limitações impedem generalizações indevidas para outras tarefas ou populações. — *relatório, seção 8*
- [x] Relatório, código, dados/instruções, metodologia, registros e gráficos estão no mesmo repositório público.
- [x] README explica como reproduzir análises e como realizar nova coleta, sem expor credenciais. — *em `COMO_EXECUTAR.md`*

## Próxima ação

Conferir o **custo observado** nos consoles (Google: *Faturamento → Relatórios*; Azure: recurso Language → *Métricas* e *Gerenciamento de Custos*) e registrar na seção 6.3 do relatório.
