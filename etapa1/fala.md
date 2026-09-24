# Categoria 3 — Fala para texto: transcrição de áudio

**Operação comparada:** transcrição assíncrona (em lote) do mesmo arquivo de áudio em português do Brasil
**Modo de chamada:** assíncrono / lote — único modo oferecido pelos três para arquivos longos
**Data da consulta às fontes:** 23/09/2026
**Região de referência:** US East (`us-east-1` / `East US` / `us-central1`)


## 1. Objetivo da categoria e caso de uso

Conversão de fala em texto transforma áudio gravado em transcrição pesquisável. O caso de uso típico é processar gravações de atendimento, reuniões ou conteúdo audiovisual para gerar legendas, permitir busca textual ou alimentar análises posteriores — inclusive análise de sentimento, o que liga esta categoria à primeira.

**Por que o modo em lote e não o tempo real:** transcrição em tempo real e em lote têm condições de uso, requisitos de formato e preços distintos. Comparar uma com a outra produziria números sem sentido. Os três provedores oferecem o modo em lote para arquivos armazenados, e é sobre ele que a comparação é feita.

## 2. Serviços comparados e operação equivalente

| Provedor | Serviço | Operação em lote | Operação em tempo real (fora da comparação) |
|---|---|---|---|
| AWS | Amazon Transcribe | `StartTranscriptionJob` | `StartStreamTranscription` |
| Microsoft Azure | Azure Speech in Foundry Tools | `Transcription_Create` (Speech to text REST API) | Reconhecimento em tempo real |
| Google Cloud | Cloud Speech-to-Text V2 | `BatchRecognize` | `StreamingRecognize`; `Recognize` para áudio < 60 s |

## 3. Comparação técnica

### 3.1 Entradas: formatos e origem do áudio

| Aspecto | Amazon Transcribe | Azure Speech (lote) | Cloud Speech-to-Text V2 |
|---|---|---|---|
| **Formatos em lote** | AMR, FLAC, M4A, MP3, MP4, Ogg, WebM, WAV | **WAV, MP3, OPUS/OGG, FLAC, WMA, AAC, ALAW em WAV, MULAW em WAV, AMR, WebM, SPEEX** | Formatos de áudio suportados pela API v2 |
| **Formatos recomendados** | FLAC ou WAV com PCM 16 bits | Formatos sem perda: WAV (PCM) e FLAC | — |
| **Origem do arquivo** | **Obrigatoriamente um bucket do Amazon S3** | URI público, URI com SAS, ou contêiner do Azure Blob Storage via *trusted Azure services* (identidade gerenciada) | Cloud Storage (`gs://`) para `BatchRecognize` |
| **Canais de áudio** | Mono e estéreo; **mais de dois canais não é suportado** | — | — |
| **Taxa de amostragem** | Opcional no lote; 8.000 Hz típico em telefonia e de 16.000 a 48.000 Hz em alta fidelidade | — | — |

A Azure aceita a lista mais ampla de formatos e é a única das três que permite **URI público** como origem, dispensando armazenamento no próprio provedor. A AWS é a mais restritiva nesse ponto: o arquivo precisa estar no S3, o que acrescenta um passo de upload e uma configuração de permissão ao fluxo.

### 3.2 Saídas

| Aspecto | Amazon Transcribe | Azure Speech (lote) | Cloud Speech-to-Text V2 |
|---|---|---|---|
| **Formato** | JSON | JSON | JSON |
| **Conteúdo mínimo** | Transcrição em bloco (`transcripts`), detalhamento por palavra e pontuação (`items`) com tempo de início, fim e confiança, e segmentos de áudio (`audio_segments`) | Transcrição com metadados da execução | Transcrição com alternativas e confiança |
| **Onde o resultado fica** | Bucket S3 do cliente **ou** bucket gerenciado pelo serviço, com **URI temporária válida por 15 minutos**; no bucket padrão, o resultado é **apagado quando o job expira, em 90 dias** | Contêiner de armazenamento, recuperado de forma assíncrona | Cloud Storage ou resposta da operação |
| **Recursos adicionais** | Diarização (separação de locutores), identificação de canal | — | Diarização disponível no modelo `chirp_3` |

O detalhe de retenção da AWS é operacionalmente relevante: quem usa o bucket padrão precisa baixar a transcrição antes de 90 dias, e a URI temporária expira em 15 minutos — se expirar, é preciso uma nova chamada `GetTranscriptionJob`.

### 3.3 Suporte ao português do Brasil

| Provedor | Código | Cobertura |
|---|---|---|
| Amazon Transcribe | **`pt-BR`** (Português, Brasileiro) e `pt-PT` (Português) | `pt-BR` em lote **e** streaming; suporta transcrição de números, acrônimos, *redaction* e Call Analytics pós-chamada e em tempo real |
| Azure Speech | **`pt-BR`** (Portuguese, Brazil) | Suportado, inclusive com *fast transcription* |
| Cloud Speech-to-Text V2 | **`pt-BR`** (Portuguese, Brazil) | Disponível nos modelos `chirp_3`, `long`, `short`, `telephony` e `telephony_short`; o `chirp_3` acrescenta diarização |

**Diferença em relação à categoria de NLP:** aqui os três provedores distinguem formalmente o português do Brasil. Na análise de sentimento, apenas a Azure faz essa distinção. Isso mostra que o suporte a variantes regionais não é uniforme nem dentro do mesmo provedor.

O Google é o único que **expõe a escolha do modelo** ao desenvolvedor na operação comparada, permitindo otimizar por tipo de áudio (telefonia, áudio longo, áudio curto). AWS e Azure não expõem essa escolha na transcrição padrão.

### 3.4 Formas de acesso, autenticação e configuração

| Aspecto | Amazon Transcribe | Azure Speech | Cloud Speech-to-Text V2 |
|---|---|---|---|
| **Acesso** | API REST, AWS CLI e SDKs (.NET, C++, Go, Java V2, JavaScript, PHP V3, Python/boto3, Ruby V3, Rust) | Speech to text REST API e Speech CLI | REST, gRPC e client libraries |
| **Autenticação** | Credenciais IAM, com permissão de leitura no bucket de origem e de escrita no de destino | Chave do recurso; para Blob Storage protegido, **identidade gerenciada atribuída pelo sistema** com papel *Storage Blob Data Reader* | Application Default Credentials |
| **Fluxo** | Inicia o job, consulta com `GetTranscriptionJob`, lê o resultado no S3 | Três passos: localizar áudio → criar transcrição → obter resultados | Inicia a operação de longa duração e consulta até concluir |

A Azure tem a configuração de segurança mais elaborada das três para o caso de armazenamento privado — exige habilitar identidade gerenciada no recurso de Speech e conceder papel específico na conta de armazenamento. É mais trabalho inicial, mas permite bloquear completamente o acesso externo ao armazenamento, algo que a documentação descreve passo a passo.

### 3.5 Latência de processamento e limites operacionais

| Aspecto | Amazon Transcribe | Azure Speech (lote) | Cloud Speech-to-Text V2 |
|---|---|---|---|
| **Agendamento** | Fila de jobs opcional quando não é necessário processar tudo simultaneamente | **Best-effort**: em horário de pico, pode levar **até 30 minutos para iniciar** e **até 24 horas para concluir** | Operação de longa duração |
| **Latência publicada** | — | **Percentil 90 abaixo de 6 horas**, com fórmula de latência normalizada publicada (`ProcessDuration − AudioLength/5`, com o serviço processando a cerca de 5× o tempo real) | — |
| **Recomendações de uso** | — | Enviar cerca de **1.000 arquivos por requisição**; distribuir envios ao longo de horas; consultar status **no máximo uma vez por minuto**, sendo suficiente a cada 10 minutos | — |

A Azure é a única das três que publica expectativa de latência e um método de cálculo para ela. Isso é transparência útil, mas também revela que o modo em lote da Azure **não é adequado a fluxos sensíveis a tempo**: a própria documentação admite picos de até 24 horas. Esse número descreve fila de processamento e não qualidade do reconhecimento.

### 3.6 Situação do serviço (avisos oficiais)

Nenhum dos três serviços desta categoria apresenta aviso de descontinuação nas páginas consultadas. É a única das três categorias deste trabalho em que isso ocorre — nas outras duas, a oferta da Azure tem encerramento anunciado.

## 4. Exemplos de código

Os três exemplos submetem o **mesmo áudio** à **mesma operação em lote**, com idioma `pt-BR`:

- `exemplos/fala/aws_transcribe.py`
- `exemplos/fala/azure_speech.py`
- `exemplos/fala/google_speech_to_text.py`

**Estado de validação:** exemplos **ilustrativos, não executados pelo grupo**, adaptados da documentação oficial, conforme a seção 3 do enunciado. Por serem operações assíncronas, cada exemplo mostra os três momentos do fluxo: envio, acompanhamento e obtenção do resultado. Nenhuma credencial está embutida.

## 5. Modelo de cobrança

| Provedor | Unidade de cobrança | Preço | Equivalente por minuto |
|---|---|---|---|
| Amazon Transcribe | **Segundo de áudio**, em incrementos de 1 segundo e **sem mínimo** | $0,0001 por segundo, **preço único sem faixas** | $0,006 |
| Azure Speech (lote) | **Hora de áudio** | $0,18 por hora | $0,003 |
| Cloud Speech-to-Text V2 (padrão) | Áudio processado, em **incrementos de 1 segundo** | $0,016 por minuto (até 500 mil min/mês) | $0,016 |
| Cloud Speech-to-Text V2 (*dynamic batch*) | Áudio processado, em incrementos de 1 segundo | $0,003 por minuto, preço único | $0,003 |

Preços de **US East, em USD, consultados em 23/09/2026**, registrados em `custos/premissas.csv`. Os da AWS vêm da *AWS Price List API* e os da Azure da *Azure Retail Prices API*.

**A granularidade do arredondamento é favorável em todos os três**: AWS e Google cobram em incrementos de 1 segundo, e a AWS declara explicitamente não haver cobrança mínima. Ou seja, um áudio de 20 segundos não é cobrado como um minuto inteiro — o que era o risco desta categoria.

**O Google tem dois preços para lote, e a diferença é de mais de 5×.** O modo padrão custa $0,016/min; o *dynamic batch*, descrito na documentação como processamento "com menor nível de urgência", custa $0,003/min. Isso importa na comparação: o lote da Azure também é declaradamente *best-effort*, com fila que pode chegar a 24 horas. **O par realmente comparável em urgência é Azure em lote × Google em dynamic batch** — e os dois custam exatamente o mesmo, $0,003/min.

## 6. Cenário de custo, fórmulas, premissas e resultados

### Carga do cenário

**10.000 minutos de áudio por mês** (cerca de 167 horas) em português do Brasil, transcritos em lote. A quantidade é hipotética e declarada como tal, e é idêntica nos três provedores.

### Fórmulas

```
AWS:     10.000 min x 60 = 600.000 segundos x $0,0001/s
Azure:   10.000 min / 60 = 166,667 horas x $0,18/h
Google:  10.000 min x $0,016/min  (padrão)
         10.000 min x $0,003/min  (dynamic batch)
```

### Resultados (USD/mês, sem franquia)

| Provedor e modo | Unidades cobradas | Custo | Urgência declarada |
|---|---|---|---|
| Azure — Speech to text Batch (S1) | 166,67 horas | **$30,00** | *Best-effort*: até 24 h em pico |
| Google — dynamic batch | 10.000 minutos | **$30,00** | Menor urgência |
| AWS — Transcribe em lote | 600.000 segundos | $60,00 | Fila opcional |
| Google — BatchRecognize padrão | 10.000 minutos | $160,00 | Prioridade padrão |

![Custo de transcrição em lote de 10.000 minutos](../custos/graficos/custos_fala.png)

### O que os números mostram

Esta é a categoria com a **maior dispersão de preço das três**: do mais barato ao mais caro há um fator de **5,3×**, contra 1,5× em visão computacional.

Mas o número isolado engana, e é por isso que a coluna de urgência está na tabela. **Comparar os $30,00 da Azure com os $160,00 do Google padrão é comparar serviços com compromissos de tempo diferentes.** Colocados na mesma condição — processamento de menor urgência — Azure e Google empatam exatamente em $30,00, e a AWS fica no dobro, $60,00, sem oferecer um modo mais barato de menor urgência.

A leitura correta é, portanto:

- **Se a aplicação tolera fila longa** (transcrição noturna de gravações, processamento de acervo): Azure e Google *dynamic batch* empatam em $30,00.
- **Se a aplicação precisa de prazo previsível**: a AWS entrega $60,00 sem depender de janela de baixa urgência, enquanto o equivalente no Google custa $160,00.

Este é o ponto do trabalho em que a análise econômica mais depende da análise técnica: sem a informação de fila da seção 3.5, o cenário produziria um ranking enganoso.

### Franquias

| Provedor | Franquia | Natureza |
|---|---|---|
| AWS | 60 minutos/mês | Promocional, 12 meses |
| Azure | 5 horas/mês | Tier F0; a página declara a franquia para transcrição em tempo real |
| Google | — | **Não localizada** para a tabela Recognition da V2 na página consultada |

A franquia do Google **não foi localizada** para a V2 e por isso aparece como pendência, não como zero: a faixa de 60 minutos gratuitos que consta da página pertence às tabelas da API V1.

### Reprodutibilidade

```
uv run custos/calcular_custos.py      # gera custos/resultados.csv (só stdlib)
uv run custos/verificar_calculos.py   # confere as contas à mão contra o programa
uv run custos/gerar_graficos.py       # gera os gráficos a partir do CSV
```

## 7. Síntese: vantagens, restrições e adequação por cenário

### O que separa as três ofertas

**A urgência é a variável escondida desta categoria.** Os três chamam de "lote" coisas com compromissos de tempo diferentes: a Azure admite abertamente fila de até 24 horas em pico (com p90 abaixo de 6 h e uma fórmula publicada para estimar a latência), o Google separa o modo padrão do *dynamic batch* de menor urgência, e a AWS oferece fila apenas como opção. Qualquer comparação que ignore isso produz ranking errado.

**A origem do áudio impõe arquitetura.** A AWS **obriga** o arquivo a estar em um bucket S3. A Azure é a única que aceita **URI público**, dispensando armazenamento no provedor — e, no outro extremo, oferece o caminho mais elaborado de segurança, com identidade gerenciada e papel *Storage Blob Data Reader* para bloquear totalmente o acesso externo ao armazenamento.

**Só o Google expõe a escolha do modelo.** `chirp_3`, `long`, `short`, `telephony` e `telephony_short` estão disponíveis para `pt-BR`, com diarização no `chirp_3`. AWS e Azure não oferecem essa decisão na transcrição padrão.

**Os três suportam `pt-BR` formalmente** — diferente da categoria de NLP, onde só a Azure distingue a variante brasileira. E **nenhum dos três tem aviso de descontinuação**, o que faz desta a única categoria do trabalho sem risco de calendário.

### Custo: maior dispersão das três categorias, mas só na aparência

Do mais barato ao mais caro há um fator de **5,3×** ($30,00 contra $160,00) — contra 1,5× em visão. Mas boa parte dessa distância desaparece quando se compara urgência equivalente:

- **Menor urgência:** Azure ($30,00) e Google *dynamic batch* ($30,00) empatam exatamente.
- **Prioridade padrão:** AWS ($60,00) contra Google padrão ($160,00).

A AWS ocupa uma posição intermediária peculiar: é o dobro do preço de menor urgência, mas **não oferece um modo mais barato** para quem tolera fila — e, em contrapartida, não obriga a aceitar janela de 24 horas para chegar ao preço competitivo.

Um alívio comum aos três: **o arredondamento é favorável**. AWS e Google cobram em incrementos de 1 segundo, e a AWS declara não haver cobrança mínima — o risco de um áudio de 20 segundos ser cobrado como um minuto inteiro não se concretizou em nenhum deles.

### Adequação por cenário

| Situação | Alternativa mais adequada | Por quê |
|---|---|---|
| Processamento **noturno ou de acervo**, sem pressa | **Azure** ou **Google dynamic batch** | $30,00 no cenário; empate exato |
| Necessidade de **prazo previsível** sem pagar prêmio alto | **Amazon Transcribe** | $60,00 sem depender de janela de baixa urgência; o equivalente no Google custa $160,00 |
| Áudio já hospedado **fora da nuvem do provedor** | **Azure** | Única que aceita URI público como origem |
| Requisito de **isolamento do armazenamento** | **Azure** | Caminho documentado com identidade gerenciada e acesso externo bloqueado |
| **Telefonia** ou tipos específicos de áudio | **Cloud Speech-to-Text V2** | Único que expõe a escolha do modelo (`telephony`, `long`, `short`) |
| Necessidade de **diarização** | AWS ou Google (`chirp_3`) | Ambos documentam separação de locutores |
| Fluxo **sensível a tempo** | Nenhum dos modos em lote | Usar transcrição em tempo real, que tem preço e condições próprios |

**O que esta etapa não responde:** qual serviço transcreve português do Brasil com menos erros. A taxa de erro exige execução e gabarito.

## 8. Referências e pendências de verificação

### Fontes usadas neste capítulo

| ID | O que sustenta |
|---|---|
| FAL-AWS-01 | Separação entre lote e streaming, operações `StartTranscriptionJob` e `StartStreamTranscription` |
| FAL-AWS-02 | Formatos de mídia por modo, canais suportados, taxas de amostragem, estrutura da saída JSON, retenção no bucket padrão (90 dias) e URI temporária de 15 minutos |
| FAL-AWS-03 | Códigos de idioma: `pt-BR` e `pt-PT` em lote e streaming, com recursos por idioma; SDKs disponíveis por modo |
| FAL-AZ-01 | Fluxo em três passos da transcrição em lote, `Transcription_Create`, agendamento best-effort (até 30 min para iniciar, até 24 h para concluir), p90 abaixo de 6 h, recomendações de lote e de polling |
| FAL-AZ-02 | Formatos e codecs aceitos no lote, origens de áudio (URI público, SAS, identidade gerenciada) e configuração de segurança do armazenamento |
| FAL-AZ-03 | Suporte ao locale `pt-BR` |
| FAL-GC-01 | Operações `Recognize`, `BatchRecognize` e `StreamingRecognize`; modelos `chirp_3`, `chirp_2` e `telephony` |
| FAL-GC-02 | Suporte a `pt-BR` nos modelos `chirp_3`, `long`, `short`, `telephony` e `telephony_short`, com diarização no `chirp_3` |

### Pendências

- **Preços não verificados** até esta data; as unidades da seção 5 estão marcadas como "a confirmar".
- A página de cotas do Amazon Transcribe **não foi acessível** na consulta de 23/09/2026; por isso, **tamanho máximo de arquivo, duração máxima de áudio e número de jobs simultâneos não estão registrados** para a AWS. Essa lacuna está declarada em vez de preenchida por estimativa.
- Limites numéricos equivalentes (tamanho e duração máximos) não foram localizados nas páginas consultadas da Azure e do Google para a operação em lote.
- Qual serviço transcreve português do Brasil com menos erros é pergunta **experimental**, não respondida nesta etapa.
