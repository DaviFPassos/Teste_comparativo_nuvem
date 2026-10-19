# Expectativas da Etapa 1 — registradas antes da coleta

O enunciado (seção 10) pede que a análise prática "confronte os resultados práticos com as conclusões obtidas na primeira etapa" e diga se os testes **confirmam, complementam ou modificam** a percepção formada pela documentação.

Para esse confronto ser honesto, as expectativas precisam ser escritas **antes** de ver os resultados. Escrevê-las depois convidaria a ajustar a expectativa ao que aconteceu. Por isso este arquivo foi criado em **18/10/2026**, quando **nenhum texto do conjunto de teste tinha sido enviado a nenhum serviço**.

**Como ler.**
- A coluna *Expectativa* vem dos capítulos da Etapa 1, com a seção indicada.
- A coluna *Como será verificado* diz qual métrica ou arquivo da coleta responde.
- A coluna *Evidência até 18/10/2026* traz só o que já foi observado e marca a origem de cada observação:
  - **[configuração]** — criação das contas;
  - **[demonstração]** — 8 frases do guia, fora do experimento;
  - **[verificação Azure]** — 5 frases do Rafael, fora do experimento.

  Nenhuma dessas observações substitui a coleta: são pistas.
- A coluna *Conclusão* fica em branco até a análise do teste.

## Integração e configuração

| # | Expectativa (Etapa 1) | Como será verificado | Evidência até 18/10/2026 | Conclusão |
|---|---|---|---|---|
| E1 | A Azure exige **criar um recurso** e administrar um par endpoint/chave; o Google exige um **projeto** com a API habilitada e credencial (`nlp.md`, 3.3) | Relato da configuração nas duas máquinas | **[configuração]** No Google, a documentação da Etapa 1 não antecipava quatro obstáculos reais: <br>(1) o ID do projeto é diferente do nome exibido, e o `.env` com o nome falha; <br>(2) a API exige conta de faturamento vinculada, mesmo dentro da franquia; <br>(3) o login para bibliotecas (ADC) é separado do login da CLI, e o consentimento recusa se a permissão "Google Cloud" ficar desmarcada; <br>(4) no WSL, o fluxo de login precisa de ajuste para chegar ao navegador do Windows. <br>Na Azure, o Rafael configurou recurso e chave sem relato de obstáculo | |
| E2 | Os exemplos de código da Etapa 1 representam a chamada real | Comparar o exemplo de `exemplos/nlp/` com o adaptador usado na coleta | **[configuração]** A chamada é a mesma, mas medir exigiu três mudanças que o exemplo não mostra: <br>• desligar as novas tentativas automáticas dos SDKs (o Google repete por até 600 s; a Azure, até 10 vezes — fontes ET2-SDK-02 e 03); <br>• fixar o timeout; <br>• capturar a resposta original | |

## Formato da resposta e normalização

| # | Expectativa (Etapa 1) | Como será verificado | Evidência até 18/10/2026 | Conclusão |
|---|---|---|---|---|
| E3 | A Azure devolve **classe pronta** — `positive`, `negative`, `neutral` ou `mixed` — com três confianças que somam 1; o Google devolve **só um número** (`score` de −1 a +1) e a classe depende de um limiar escolhido pela aplicação (`nlp.md`, 3.1) | `rotulo_original`, `confiancas` e `score` em `predicoes.jsonl` | **[demonstração]** O Google devolveu apenas `score` e `magnitude`. As duas demonstrações, feitas com 4 minutos de intervalo, deram **scores idênticos** nas 8 frases — indício de resposta determinística para a mesma entrada, o que sustenta fazer **uma rodada só** (`metodologia.md`, "Repetições"). **[verificação Azure]** A Azure devolveu rótulo + três confianças | |
| E4 | `mixed` da Azure é **composto a partir das sentenças** (≥ 1 positiva e ≥ 1 negativa); por isso a Azure deve rotular como misto textos que o gabarito humano — que decide por predominância — considera positivos ou negativos (`nlp.md`, 3.1; `dados/guia_de_anotacao.md`) | Frequência de previsões `misto` por classe do gabarito (`matriz_confusao`, coluna `misto`) e no conjunto exploratório | Ainda não observado: nenhuma das 5 frases da verificação Azure tinha sinais opostos | |
| E5 | O Google **não tem classe para texto ambíguo**; textos com elogio e crítica tendem a ficar perto de zero e cair em `neutro` pela regra de ±0,25 | Previsões do Google para textos do gabarito positivo/negativo que contêm ressalva; conjunto exploratório `misto` | **[demonstração]** As três frases de sinais opostos do guia receberam score ±0,10 → `neutro`. A ironia "Ótimo, veio faltando peça." recebeu +0,70 → `positivo`. São 8 frases difíceis de propósito, não uma medida | |
| E6 | O limiar ±0,25 é uma **escolha do grupo**, não uma regra do Google (`nlp.md`, 7) | Se o piloto indicar ajuste, ele é registrado em `metodologia.md` antes do teste | — | |

## Idioma

| # | Expectativa (Etapa 1) | Como será verificado | Evidência até 18/10/2026 | Conclusão |
|---|---|---|---|---|
| E7 | Só a Azure distingue `pt-BR` de `pt-PT`; **a documentação não promete resultado melhor** por isso (`nlp.md`, 3.2) | Não é isolável neste experimento: a diferença de acurácia entre os provedores não pode ser atribuída à variante de idioma. Registrar como hipótese não testada | — | |
| E8 | O Google detecta o idioma e devolve `language` | `idioma_detectado` em `predicoes.jsonl` | **[demonstração]** `pt` em todas as 8 frases | |

## Custo

| # | Expectativa (Etapa 1) | Como será verificado | Evidência até 18/10/2026 | Conclusão |
|---|---|---|---|---|
| E9 | Azure e Google cobram em unidades de **1.000 caracteres** (`nlp.md`, 5): para textos curtos, **as duas cobram o mesmo número de unidades** — a vantagem de granularidade era da AWS, que ficou fora | `unidades_estimadas` por provedor; os textos do teste têm mediana de ~100 caracteres | Os 330 candidatos somam 332 unidades nos dois provedores (só 2 textos passam de 1.000 caracteres) | |
| E10 | Dentro da franquia (Azure F0: 5.000 registros/mês; Google: 5.000 unidades/mês), o custo é **US$ 0** (`custos/franquias.csv`) | Custo estimado (`metricas.json`) **e** custo observado no painel de cada provedor | **[configuração]** ~20 unidades gastas no Google em verificações e demonstrações, todas dentro da franquia | |

## Limites e confiabilidade

| # | Expectativa (Etapa 1) | Como será verificado | Evidência até 18/10/2026 | Conclusão |
|---|---|---|---|---|
| E11 | Azure F0: **300 requisições/min**; Google: **600 requisições/min** (`nlp.md`, 3.4). Em envio sequencial, **nenhum erro de limite** é esperado | `falhas_por_codigo` (código `limite`) e `sucesso_por_tentativa` | **[demonstração]** 16/16 chamadas ao Google com sucesso. **[verificação Azure]** 5/5 | |
| E12 | A análise de sentimento da Azure tem **encerramento anunciado para 31/03/2029** (`nlp.md`, 3.5) | Não é testável; volta à síntese como risco de manutenção | — | |

## Latência

| # | Expectativa (Etapa 1) | Como será verificado | Evidência até 18/10/2026 | Conclusão |
|---|---|---|---|---|
| E13 | A Etapa 1 **não fez afirmação sobre latência** — a documentação não publica esse número para a análise de sentimento síncrona | Mediana e p95 por provedor. **Não comparáveis entre si**: cada provedor roda numa máquina (ver `metodologia.md`, "Mesmas condições") | **[demonstração]** Google: mediana ~1.070 ms. **[verificação Azure]** ~843 ms. Máquinas e redes diferentes, então não se comparam. Nos dois, a 1ª chamada foi ~70% mais lenta, o que motivou o aquecimento | |

## O que esta etapa **não** pode responder

- A qualidade de **visão** e de **fala**: só foram comparadas pela documentação na Etapa 1.
- Se a diferença de qualidade vale para **outros tipos de texto**: o conjunto é de avaliações de produto de um varejista, de 2018.
- Se a **latência** de um provedor é menor que a do outro: as máquinas são diferentes.
