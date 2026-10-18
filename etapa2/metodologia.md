# Metodologia da Etapa 2 — avaliação prática de análise de sentimento

> **Estado: RASCUNHO — aguardando aprovação do grupo.**
> As linhas marcadas **decidido** foram escolhidas pelo grupo em 18/10/2026. As marcadas **proposto** precisam ser aprovadas (ou alteradas) **antes da coleta no conjunto de teste**. Depois de aprovado, este protocolo é congelado: qualquer mudança passa a ser registrada na seção [Alterações](#alterações-ao-protocolo), com data e motivo.

## Pergunta do experimento

Diante dos **mesmos textos em português**, como a Azure Language e a Cloud Natural Language se comparam em **qualidade das respostas**, **tempo de resposta**, **sucesso das requisições** e **custo**?

## Decisões

| Decisão | Valor | Estado | Justificativa |
|---|---|---|---|
| Categoria | Análise de sentimento de documento (NLP), modelos pré-treinados | decidido (roteiro) | Recorte do plano da Etapa 2; o enunciado (seção 7) permite avaliar uma ou mais categorias |
| Provedores | **Microsoft Azure** e **Google Cloud** | **decidido** | Mínimo de dois exigido pela seção 7. As duas contas têm acesso sem cartão ou com teste gratuito, e as franquias cobrem o volume. A AWS fica fora: segundo o levantamento de `testes/`, o Comprehend exige plano pago — conflita com o orçamento de US$ 0 |
| Serviços e operação | Azure Language in Foundry Tools — *Sentiment analysis* (síncrono, SDK `azure-ai-textanalytics` 5.4.0); Cloud Natural Language API v1 — `analyzeSentiment` (SDK `google-cloud-language` 2.21.0) | proposto | As mesmas operações comparadas na Etapa 1 (`etapa1/nlp.md`), com as **mesmas versões de SDK** que os testes da Etapa 1 usam (`DEPENDENCIAS.md`). Travadas em `src/executar.py.lock` |
| Idioma declarado | `pt-BR` na Azure; `pt` no Google | proposto | Cada um com o código mais específico que aceita (Etapa 1, seção 3.2 de `nlp.md`) |
| Modo de chamada | **Um documento por chamada, sequencial** | proposto | Lotes misturariam duas cargas (roteiro, seção 3) |
| Ordem | Para cada texto, os dois provedores em sequência, em **ordem sorteada por texto** (semente 20261018, gravada) | proposto | Os dois enfrentam as mesmas condições de horário e rede; nenhum é sempre o primeiro |
| Dados | **B2W-Reviews01** (CC BY-NC-SA 4.0), sorteio estratificado por estrelas, sem dados pessoais — ver [`dados/README.md`](dados/README.md) | **decidido** (fonte) · proposto (filtros) | Avaliações reais de clientes, com origem citável |
| Tamanho | Piloto: 30 textos. Teste: até **50 por classe** (meta de 150), escolhidos entre 300 candidatos anotados | proposto | Sugestão do roteiro; custa ~330 unidades por rodada nos dois provedores, menos de 7% da franquia mensal |
| Gabarito | **Dois integrantes**, independentes, sem ver estrelas nem APIs; divergências resolvidas por discussão registrada; concordância medida por **kappa de Cohen** | **decidido** | Exigência da seção 9 (critério de qualidade) e do roteiro (rótulo humano identificado) |
| Classes de referência | `positivo`, `negativo`, `neutro` na avaliação principal. `misto` e `invalido` ficam **fora** dela; os mistos formam um conjunto exploratório separado **antes** das chamadas | proposto | Plano de três classes do roteiro (seção 5) |
| Normalização — Azure | `positive`/`negative`/`neutral`/`mixed` → `positivo`/`negativo`/`neutro`/`misto` | proposto | A Azure devolve classe; a regra só traduz. Regra v1 em `src/normalizar.py` |
| Normalização — Google | `score > 0,25` → positivo · `score < −0,25` → negativo · `−0,25 ≤ score ≤ 0,25` → neutro | proposto | O Google não devolve classe (Etapa 1). O limiar ±0,25 é uma escolha inicial do roteiro, **não** uma regra do Google. Pode ser ajustado **somente com o piloto** e é congelado antes do teste |
| Previsão `misto` | Resposta utilizável; **conta como erro** no plano de três classes; frequência reportada à parte | proposto | Roteiro, seção 6, regra 5. Não vira `neutro` automaticamente |
| Métricas de qualidade | Acurácia, precisão/revocação/F1 por classe, **macro-F1**, matriz de confusão (3 linhas × 4 colunas) | proposto | Ver [Métricas](#métricas-e-denominadores) |
| Comparação entre provedores | **McNemar exato** sobre os mesmos textos; kappa entre as previsões dos dois | proposto | Com ~150 textos, uma diferença de poucos pontos pode ser acaso; o teste pareado diz quanto |
| Latência | `time.perf_counter()` imediatamente antes e depois da chamada; **mediana e p95** (posto mais próximo) das tentativas bem-sucedidas; timeouts à parte; criação do cliente fora da medida | proposto | Roteiro, seção 7. Inclui rede + processamento; não é a velocidade do modelo isolado |
| Aquecimento | **Proposta:** antes do primeiro texto, uma chamada de aquecimento por provedor com uma frase fixa fora do conjunto, registrada à parte e excluída da latência | proposto | Na demonstração real de 18/10/2026, a 1ª chamada ao Google levou 1.819 ms e as demais ~1.070 ms (conexão + token). O roteiro (seção 7) pede definir se o aquecimento entra na medida. *Ainda não implementado* — implementar só se aprovado |
| Sucesso | Por tentativa e por texto, com a mesma política nos dois | proposto | Roteiro, seção 7 |
| Repetições | **Uma rodada** do teste. Repetições só se houver motivo registrado antes | proposto | Roteiro, seção 3 |
| Erros e tentativas | Timeout de **30 s**; até **3 tentativas** só para erro transitório (limite, timeout, servidor, rede), com espera de 2 s × nº da tentativa; autenticação ou cota esgotada **interrompem** o provedor; novas tentativas embutidas nos SDKs **desligadas** | proposto | Sem desligar, o SDK do Google repetiria sozinho por até 600 s e esconderia falhas da medida |
| Intervalo entre chamadas | ≥ 0,25 s na Azure (F0: 300 req/min); ≥ 0,15 s no Google (600 req/min) | proposto | Abaixo dos limites documentados com folga |
| Custo | **Teto US$ 0 — só franquia.** Azure no tier **F0** (5.000 registros/mês, sem cobrança); Google dentro da faixa gratuita (5.000 unidades/mês). O executor **recusa** a coleta se o pior caso (todas as tentativas) passar de 90% da franquia | **decidido** (teto) · proposto (trava) | Hipóteses conservadoras: toda tentativa consome unidade, inclusive as que falham |
| Custo observado | Conferido no painel de cada provedor depois da coleta e registrado à parte da estimativa | proposto | Roteiro, seção 7 |
| Ambiente | Gravado automaticamente em cada execução: Python, SO, versões dos SDKs, commit do git, SHA-256 do dataset e do código | proposto | — |

## Métricas e denominadores

Implementadas em `src/analisar.py` e conferidas contra contas feitas à mão em `testes/test_metricas.py`.

| Métrica | Fórmula | População |
|---|---|---|
| Acurácia | acertos / textos avaliados | **Interseção**: textos de gabarito positivo/negativo/neutro com resposta utilizável nos **dois** provedores |
| Precisão da classe | TP / (TP + FP) | Interseção |
| Revocação da classe | TP / (TP + FN); uma previsão `misto` é FN da classe verdadeira | Interseção |
| F1 da classe | 2·P·R / (P + R); denominador nulo vale 0 e é **sinalizado** | Interseção |
| Macro-F1 | média do F1 das três classes de referência | Interseção |
| Acertos sobre programados | acertos / todos os textos programados; falha conta como não acerto | Todos os textos do teste |
| Sucesso por tentativa | tentativas com resposta / tentativas | Todas as tentativas |
| Sucesso por texto | textos com resposta ao final / textos programados | Todos os textos |
| Latência | mediana e p95 (posto mais próximo: `ceil(0,95·n)`-ésimo valor ordenado) | Tentativas bem-sucedidas |
| Custo estimado | unidades × tarifa, com e sem franquia (`custos/premissas.csv`) | Todas as tentativas, inclusive piloto |

A tabela principal informa sempre **quantos textos ficaram na interseção, quantos foram excluídos e por quê**.

## Ordem de execução

1. Anotar, consolidar e **montar** os conjuntos (`src/anotacao.py`). A partir daqui o teste está congelado.
2. **Aprovar este protocolo** (trocar o estado no topo e registrar a data).
3. Rodar o **piloto** nos dois provedores. O piloto serve para detectar problemas de entrada, permissão e formato — e, se o grupo decidir, ajustar o limiar do Google. **Fica fora das métricas principais.**
4. Registrar qualquer ajuste em [Alterações](#alterações-ao-protocolo).
5. Rodar o **teste** uma vez. Não interromper nem descartar resultados por favorecerem um provedor.
6. Analisar (`src/analisar.py`) e confrontar com a Etapa 1.

## Alterações ao protocolo

| Data | Alteração | Motivo | Antes ou depois de ver o teste? |
|---|---|---|---|
| — | — | — | — |

## Aprovação

| Integrante | Aprovou em |
|---|---|
| Davi Fonseca Passos | |
| Rafael Fonseca Pessoa | |
| Lucca Melo Nunes | |
