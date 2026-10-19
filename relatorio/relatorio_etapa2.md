# Comparação de Serviços de Inteligência Artificial em Nuvem

## Etapa 2 — Avaliação Prática

**Disciplina:** Computação em Nuvem — Mestrado em Ciência da Computação, Universidade de Fortaleza (UNIFOR)

**Integrantes:** Davi Fonseca Passos · Rafael Fonseca Pessoa · Lucca Melo Nunes

**Repositório público:** https://github.com/DaviFPassos/Teste_comparativo_nuvem

> **Estado deste documento (19/10/2026): ESQUELETO.**
> As seções 1 a 5 e 8 descrevem o que já está definido e implementado.
> As seções marcadas **PENDENTE** dependem da coleta — que ainda não ocorreu — ou de conclusões que cabem ao grupo.
> Nenhum número de resultado aparece aqui antes de existir: as tabelas da seção 6 são geradas por `etapa2/src/analisar.py` a partir dos arquivos da coleta e **copiadas sem edição**.

---

## 1. Pergunta e escopo

Diante dos **mesmos textos em português**, como a **Azure Language** e a **Cloud Natural Language API** do Google se comparam em **qualidade da classificação de sentimento**, **sucesso das requisições**, **custo** e **latência**?

O enunciado (seção 7) pede avaliar uma ou mais das categorias estudadas, com serviços equivalentes de pelo menos dois provedores. O grupo escolheu **análise de sentimento de documento**, da categoria NLP. Três razões:

- é a operação com equivalente direto nos dois provedores (Etapa 1, `etapa1/nlp.md`);
- é a categoria em que a Etapa 1 encontrou as diferenças de **formato de resposta** mais consequentes: classe pronta na Azure, número contínuo no Google;
- o volume necessário cabe nas franquias gratuitas — orçamento de US$ 0.

A AWS ficou de fora porque o Comprehend exige conta em plano pago, o que conflita com o orçamento.

## 2. Serviços comparados

| Provedor | Serviço | Operação | SDK | Região |
|---|---|---|---|---|
| Microsoft Azure | Azure Language in Foundry Tools | Sentiment analysis, síncrona, 1 documento por chamada, idioma `pt-BR` | `azure-ai-textanalytics` 5.4.0 | East US, tier **F0** |
| Google Cloud | Cloud Natural Language API v1 | `analyzeSentiment`, 1 documento por chamada, idioma `pt` | `google-cloud-language` 2.21.0 | global |

## 3. Dados de teste

*(seção 8 do enunciado — detalhes em `etapa2/dados/README.md`)*

- **Fonte:** B2W-Reviews01 — 132.373 avaliações reais da Americanas.com, de janeiro a maio de 2018, publicadas pela B2W Digital sob CC BY-NC-SA 4.0 (fontes ET2-DADOS-01 e 02).
- **Filtros:** foram retirados textos vazios, todas as cópias de textos duplicados e textos com indício de dado pessoal — código de rastreio dos Correios, números de protocolo ou de nota fiscal. Restaram **124.926** elegíveis. Nenhum campo pessoal do dataset foi copiado. Na leitura, mais **3 textos com o nome do autor** foram excluídos por decisão registrada (`etapa2/dados/exclusoes.csv`).
- **Sorteio:** estratificado por estrelas, com semente fixa — 30 textos de piloto e 300 candidatos ao teste, 60 por estrela. Reprodutível byte a byte.
- **Gabarito:** **dois anotadores** independentes, sem ver as estrelas nem as respostas das APIs. O anotador A é Davi Fonseca Passos, com rótulos **gerados por IA** e adotados por ele; o anotador B é um integrante humano, que não consultou a sugestão. A concordância entre os dois mostra quanto o rótulo da IA se aproxima de uma leitura humana. As divergências são resolvidas por discussão registrada, e a concordância é medida por kappa de Cohen. As estrelas **não** são o gabarito: o próprio artigo do dataset mostra que reduzir a escala de 5 pontos a 3 classes "pode levar a conclusões erradas".
- **Conjunto final:** até 50 textos por classe (positivo, negativo, neutro). Os textos rotulados *misto* formam um conjunto exploratório separado, **antes** de qualquer chamada.

**Resultado da anotação** (fonte: `etapa2/dados/manifesto_conjuntos.json`, gerado por `anotacao.py montar`):

| | Valor |
|---|---|
| Textos anotados pelos dois anotadores | 330 |
| Concordância bruta | 87,0% |
| Kappa de Cohen (A × B) | **0,791** |
| Divergências | 43 — decididas pela regra "prevalece o anotador humano (B)" |
| Excluídos | 2 inválidos e 3 com nome do autor |
| Disponíveis entre os candidatos ao teste | 134 positivos · 107 negativos · **15 neutros** |
| **Conjunto de teste** | **115 textos: 50 positivos, 50 negativos, 15 neutros** |
| Piloto | 30 textos |
| Conjunto exploratório (mistos) | 39 textos |

Das 43 divergências, 27 foram entre positivo/negativo (IA) e misto (Rafael): a IA tendeu a escolher o lado predominante, e o anotador humano marcou misto com mais facilidade. A classe neutra ficou com **15** textos, abaixo da meta de 50; por isso a análise traz também a avaliação sem a classe neutra (seção 4).

## 4. Metodologia e métricas

*(seção 9 do enunciado — protocolo completo em `etapa2/metodologia.md`)*

**Normalização para uma convenção comum** (`positivo`, `negativo`, `neutro`, `misto`):

- **Azure:** tradução direta da classe do serviço, `mixed` → `misto`.
- **Google:** o serviço devolve só um número. `score > +0,25` → positivo; `score < −0,25` → negativo; caso contrário, neutro. O limiar é uma escolha do grupo e pode ser ajustado **apenas com o piloto**.

Uma previsão `misto` conta como erro no plano de três classes.

**Avaliação sem a classe neutra.** Avaliação de produto quase sempre opina, e a classe neutra ficou escassa entre os candidatos. Por isso, **antes da coleta**, o grupo decidiu reportar ao lado da principal a mesma comparação só com os textos de gabarito positivo e negativo: acurácia, macro-F1 das duas classes e McNemar. Uma previsão neutro ou misto continua contando como erro.

**Métricas:**

| Aspecto | Métrica | População |
|---|---|---|
| Qualidade | Acurácia, precisão/revocação/F1 por classe, **macro-F1**, matriz de confusão | Interseção: textos com resposta utilizável nos dois provedores |
| Qualidade, sem esconder falhas | Acertos ÷ todos os textos programados | Todos os textos |
| Diferença entre provedores | **McNemar exato** e kappa entre as previsões | Interseção |
| Sucesso | Por tentativa e por texto | Todas as chamadas |
| Latência | Mediana e p95 (posto mais próximo), sem a chamada de aquecimento | Tentativas bem-sucedidas |
| Custo | Unidades × tarifa, com e sem franquia; e custo observado no painel | Todas as chamadas, incluindo o piloto |

## 5. Programa de teste e condições

*(seções 8 e 10 do enunciado)*

O programa (`etapa2/src/`) envia **um texto por chamada**. Cada tentativa tem timeout de 30 s, e só os erros transitórios são repetidos, até 3 vezes. As **novas tentativas automáticas dos SDKs ficam desligadas** (fontes ET2-SDK-02 e 03). Cada tentativa é registrada, com a resposta original sem identificadores da conta. Uma trava recusa a coleta se o pior caso passar de 90% da franquia gratuita. Há 93 testes offline, que usam os SDKs oficiais com a rede substituída.

**Arranjo de execução:** cada provedor roda no laptop de quem tem a credencial. O Google fica com o Davi e a Azure com o Rafael, sobre o **mesmo** `teste.csv` congelado. A análise junta as duas execuções e só aceita a junção se o dataset for idêntico byte a byte e a regra de normalização for a mesma.

| Condição (seção 10) | Mesma nos dois? |
|---|---|
| Textos, gabarito, normalização, política de tentativas, timeout, versões de SDK, aquecimento | **Sim** |
| Máquina, rede, horário | **Não** — por isso a **latência não é comparada entre provedores**; a de cada um vale isoladamente |

## 6. Resultados

> **PENDENTE — coleta do experimento.** Depois de rodar o teste nos dois laptops:
>
> ```bash
> uv run etapa2/src/analisar.py --execucao <id_google> <id_azure>
> ```
>
> Copiar **sem edição**:
> - a tabela de `etapa2/resultados/comparacoes/<nome>/analise/tabela_principal.md`;
> - os gráficos de `etapa2/graficos/<nome>/`: `qualidade.png`, `matriz_confusao.png` e `latencia.png`.
>
> Informar o número de textos na interseção, os excluídos e por quê, e o resultado do McNemar.

### 6.1 Qualidade — PENDENTE

### 6.2 Sucesso e falhas — PENDENTE

### 6.3 Custo — estimado e observado — PENDENTE

### 6.4 Latência — cada provedor isoladamente — PENDENTE

### 6.5 Conjunto exploratório (textos mistos) — PENDENTE

## 7. Confronto com a Etapa 1

*(seção 10 do enunciado)*

As expectativas foram registradas **antes** da coleta, em `etapa2/expectativas_etapa1.md`: 13 itens, cada um com a expectativa vinda da Etapa 1 e o modo de verificação. Duas delas já têm evidência da fase de configuração:

- **E1 — configuração:** a Etapa 1 subestimou o trabalho de configurar o Google. Houve quatro obstáculos que a documentação não antecipava: a diferença entre o ID e o nome do projeto, a exigência de faturamento vinculado, o login de aplicação (ADC) separado do login da CLI, com consentimento obrigatório, e o ajuste do login no WSL.
- **E2 — exemplos de código:** medir exigiu três mudanças que os exemplos da Etapa 1 não mostram — desligar as novas tentativas dos SDKs, fixar o timeout e capturar a resposta original.

> **PENDENTE — conclusões do grupo.** Para cada item de `expectativas_etapa1.md`, preencher a coluna *Conclusão* com: **confirma**, **complementa** ou **modifica**.

## 8. Limitações

- **Um domínio:** avaliações de produtos de um varejista, de 2018. Os resultados não valem para redes sociais, notícias ou atendimento.
- **Textos de 50 caracteres ou mais:** a fonte quase não tem textos menores. Comentários muito curtos não estão representados.
- **A classe neutra é curta:** avaliação de produto quase sempre opina. O número real por classe é informado, e a avaliação sem a classe neutra (seção 4) mostra o resultado sem depender dela.
- **Rótulos do anotador A gerados por IA:** usar IA de linguagem para rotular o gabarito de serviços de IA de linguagem pode aproximar o gabarito do "jeito de máquina" de ler sentimento. O anotador B humano, o kappa e a discussão das divergências existem para medir e corrigir isso.
- **Latência não comparável entre provedores:** máquinas e redes diferentes (seção 5).
- **Uma rodada:** as duas demonstrações do Google deram scores idênticos para as mesmas frases, o que sugere resposta determinística. A variação entre rodadas não foi medida.
- **`misto` tem definições diferentes:** no gabarito, é decidido por predominância; na Azure, é composto mecanicamente pelas sentenças. Parte dos "erros" da Azure nessa coluna é diferença de definição, e será analisada à parte.
- **Variante de idioma:** a vantagem de a Azure distinguir `pt-BR` não é isolável neste desenho.

## 9. Conclusões

> **PENDENTE — redigidas pelo grupo, a partir das seções 6 e 7.**

## 10. Reprodução

```bash
uv run etapa2/rodar_testes.py                                  # 93 testes offline, sem custo
uv run etapa2/src/analisar.py --execucao <id_google> <id_azure> # recalcula tudo a partir dos arquivos, sem chamar API
```

Nova coleta (exige credenciais e gera custo dentro da franquia): ver `etapa2/COMO_EXECUTAR.md`.

## Referências

Fontes com URL, data de acesso e afirmação sustentada: `referencias/fontes.md`, seção "Etapa 2 — avaliação prática" (ET2-*), além de NLP-AZ-04, NLP-GC-01, NLP-GC-03 e PRE-*.
