# Seleção das categorias e critérios de comparação

**Data da verificação das ofertas:** 23/09/2026
**Fontes:** documentação oficial dos três provedores (registrada em `referencias/fontes.md`).

## 1. Critérios de seleção

O enunciado (seção 2, p. 2) determina que a seleção "deverá privilegiar a relevância para o desenvolvimento de aplicações e a diversidade de funcionalidades", evitando "selecionar vários serviços pertencentes essencialmente ao mesmo domínio de aplicação". O grupo aplicou três critérios:

1. **Diversidade de domínio de entrada.** As três categorias tratam modalidades diferentes — **texto, imagem e áudio**. Isso evita o erro explicitamente citado no enunciado: analisar sentimento, entidades e frases-chave seria comparar três *funcionalidades do mesmo domínio* (NLP), não três categorias.
2. **Relevância para quem integra IA a uma aplicação.** As três resolvem problemas correntes em produto: classificar opinião de usuários, indexar/moderar imagens e transcrever áudio. Todas são consumíveis por API/SDK sem treinar modelo próprio, que é a perspectiva adotada pelo enunciado (seção 1).
3. **Existência de oferta concorrente nos três provedores.** O enunciado exige pelo menos dois provedores por categoria e recomenda incluir os três quando houver equivalência. Nas três categorias escolhidas há oferta gerenciada equivalente na AWS, na Azure e no Google Cloud — portanto os três entram em todas as comparações.

Categorias consideradas e descartadas: **tradução automática** (próxima demais de NLP em domínio de entrada), **análise de documentos/OCR** (sobreposição com visão computacional) e **modelos generativos** (comparação dominada por escolha de modelo e não por características do serviço gerenciado, além de preços por token que mudam com frequência alta).

## 2. Ofertas confirmadas

Todos os nomes abaixo foram conferidos na documentação oficial em 23/09/2026. **Vários diferem do nome citado no roteiro**, porque a Microsoft reorganizou suas ofertas de IA sob a marca *Foundry Tools*.

| Categoria | AWS | Microsoft Azure | Google Cloud |
|---|---|---|---|
| NLP / análise de texto | **Amazon Comprehend** | **Azure Language in Foundry Tools** (antes Azure AI Language / Text Analytics) | **Cloud Natural Language API** |
| Visão computacional | **Amazon Rekognition** | **Azure Vision in Foundry Tools** — Image Analysis | **Cloud Vision API** |
| Fala para texto | **Amazon Transcribe** | **Azure Speech in Foundry Tools** | **Cloud Speech-to-Text V2** |

### Avisos de encerramento encontrados na documentação oficial

Dois dos serviços da Azure trazem aviso formal de descontinuação. Isso é uma diferença relevante entre provedores para quem precisa escolher hoje, e por isso é registrado aqui e retomado nas sínteses:

| Serviço | Aviso oficial | Data de encerramento |
|---|---|---|
| Azure Language — análise de sentimento e opinion mining | "Sentiment analysis and opinion mining retire from Azure Language on March 31, 2029", com recomendação de migrar para o Microsoft Foundry | **31/03/2029** |
| Azure Vision — Image Analysis 4.0 | "The Image Analysis 4.0 service in Azure Vision in Foundry Tools is deprecated and will be retired on September 25, 2028" | **25/09/2028** |

Nenhum aviso equivalente foi encontrado nas páginas oficiais correspondentes da AWS ou do Google Cloud consultadas nesta data. Em particular, a documentação do `analyzeSentiment` da Cloud Natural Language API **não apresenta aviso de descontinuação**; a única descontinuação oficial dessa API é a da versão `v1beta1`, encerrada em 27/12/2019.

## 3. Operação comparável por categoria

Para que a comparação técnica e a de custos usem a mesma tarefa, foi fixada uma operação por categoria, executada sobre a mesma entrada nos três provedores.

| Categoria | Operação comparada | Entrada padronizada |
|---|---|---|
| NLP | Sentimento **de documento** (não por sentença, não por aspecto) | Mesmo texto em português: `O atendimento foi excelente.` |
| Visão computacional | **Detecção de rótulos** do conteúdo da imagem (labels/tags), sem localização | Mesma imagem JPEG |
| Fala para texto | **Transcrição assíncrona (em lote)** de arquivo de áudio | Mesmo arquivo de áudio, pt-BR, formato declarado |

### Operações correspondentes em cada provedor

| Categoria | AWS | Azure | Google Cloud |
|---|---|---|---|
| NLP | `DetectSentiment` (síncrona, 1 documento); `BatchDetectSentiment`; `StartSentimentDetectionJob` (assíncrona) | Análise de sentimento via REST API ou client library, nível de documento e de sentença | `analyzeSentiment` (v1) |
| Visão | `DetectLabels` (feature `GENERAL_LABELS`) | Image Analysis — *Tag visual features* (Tags) | `LABEL_DETECTION` via `images:annotate` |
| Fala | `StartTranscriptionJob` (lote); `StartStreamTranscription` (streaming) | `Transcription_Create` na Speech to text REST API (lote) | `BatchRecognize` (lote); `Recognize` (síncrona, < 60 s); `StreamingRecognize` |

## 4. Modo de chamada escolhido e por que

| Categoria | Modo | Justificativa |
|---|---|---|
| NLP | **Síncrono, um documento por chamada** | Os três oferecem chamada síncrona de documento único. Comparar 1 documento em um provedor com lotes de 25 em outro misturaria cargas diferentes. |
| Visão | **Síncrono, uma imagem por chamada** | Modo nativo e equivalente nos três. |
| Fala | **Assíncrono / em lote** | É o único modo oferecido pelos três para arquivos longos. A transcrição em tempo real existe na AWS e no Google, mas tem condições e preços distintos e **não deve ser comparada com a transcrição em lote**. |

## 5. Limites à equivalência (a declarar no relatório)

A comparação é entre serviços concorrentes, não entre implementações idênticas. As diferenças abaixo foram identificadas já na fase de seleção e impedem tratar as saídas como intercambiáveis:

- **Formato de saída do sentimento diverge entre os três.** A AWS retorna uma classe entre `POSITIVE`, `NEGATIVE`, `NEUTRAL` e `MIXED`, mais um score para cada uma. A Azure retorna rótulo em nível de documento **e** de sentença, com três scores de confiança de 0 a 1; no documento o rótulo pode ainda ser `mixed`, quando há sentenças positivas e negativas. O Google **não retorna classe**: devolve `score` (de −1 a +1) e `magnitude`, exigindo que o desenvolvedor defina limiares. Comparar diretamente o `score` do Google com a confiança da Azure seria comparar grandezas diferentes.
- **Rótulos de imagem não têm taxonomia comum.** A AWS retorna `Name` com `Parents`, `Aliases` e `Categories` e confiança de 0 a 100; o Google retorna `description`, `score` (0 a 1), `topicality` e `mid` (identificador do Knowledge Graph); a Azure retorna tags com confiança própria. Nomes e granularidade não coincidem.
- **Processamento em lote de áudio tem latência muito diferente de tempo real.** A própria documentação da Azure afirma que a fila de lote pode levar até 30 minutos para iniciar e até 24 horas para concluir em horários de pico, com p90 abaixo de 6 horas. Isso não é medida de qualidade do modelo e não será apresentado como tal nesta etapa.

## 6. Roteiro comum de perguntas por capítulo

Os capítulos `nlp.md`, `visao.md` e `fala.md` respondem às mesmas oito perguntas, na mesma ordem, para que a comparação seja simétrica:

1. **O que o serviço faz** na operação comparada?
2. **Como se acessa** (REST, SDKs disponíveis, CLI, contêiner)?
3. **O que recebe** (formatos de entrada, tamanho máximo, idioma)?
4. **O que devolve** (estrutura da resposta e significado dos campos)?
5. **Como se autentica e configura** (tipo de credencial, endpoint, região)?
6. **Quais limites e restrições** se aplicam (tamanho, cota, idioma, região, avisos de descontinuação)?
7. **Quanto custa** (unidade de cobrança, faixas, franquia, cenário calculado)?
8. **Para qual cenário é adequado**, considerando técnica e custo em conjunto.

## 7. Situação das pendências desta fase

Este documento foi escrito na Fase 2, antes dos capítulos e dos custos. As três pendências que ele registrou foram todas resolvidas depois — e ficam aqui com o desfecho, para que não reste dúvida sobre qual informação vale:

| Pendência registrada na Fase 2 | Situação atual | Onde está |
|---|---|---|
| Confirmar o **suporte a português** de cada serviço na operação comparada | **Resolvida.** Os nove serviços foram conferidos nas páginas oficiais de idiomas | Seção 3.2 de `nlp.md`, 3.3 de `fala.md`; fontes `NLP-*-03`, `FAL-*-03` |
| Confirmar os **limites numéricos de entrada** do Comprehend e da Cloud Natural Language | **Resolvida.** 5 KB por documento no Comprehend; 1.000.000 de bytes e 100.000 tokens no Google | Seção 3.1 de `nlp.md`; fontes `NLP-AWS-02` e `NLP-GC-03` |
| Levantar os **preços** | **Resolvida.** Nove linhas de preço verificadas em fonte oficial, com região e data | `custos/premissas.csv`, `custos/resultados.csv` e a seção 6 de cada capítulo |

As pendências que **continuam** abertas ao fim da Etapa 1 estão listadas em `relatorio/partes/04_limitacoes.md` e no fim de cada capítulo.
