## 2. Seleção das categorias e critérios

O enunciado (seção 2) determina que a seleção "deverá privilegiar a relevância para o desenvolvimento de aplicações e a diversidade de funcionalidades", evitando "selecionar vários serviços pertencentes essencialmente ao mesmo domínio de aplicação".

O grupo selecionou **três categorias**, aplicando três critérios:

**1. Diversidade de domínio de entrada.** As categorias tratam modalidades diferentes — **texto, imagem e áudio**. Isso evita o erro que o próprio enunciado adverte: analisar sentimento, entidades e frases-chave seria comparar três *funcionalidades do mesmo domínio* (processamento de linguagem natural), não três categorias distintas.

**2. Relevância para quem integra IA a uma aplicação.** As três resolvem problemas correntes de produto — classificar opinião de usuários, indexar e moderar imagens, transcrever áudio — e todas são consumíveis por API ou SDK com modelos pré-treinados, sem treinar modelo próprio.

**3. Existência de oferta concorrente nos três provedores.** O enunciado exige pelo menos dois provedores por categoria e recomenda incluir os três quando houver equivalência. Nas três categorias há oferta gerenciada equivalente na AWS, na Azure e no Google Cloud, de modo que **os três entram em todas as comparações**.

### Categorias e serviços comparados

| Categoria | AWS | Microsoft Azure | Google Cloud | Operação comparada |
|---|---|---|---|---|
| NLP / análise de texto | Amazon Comprehend | Azure Language in Foundry Tools | Cloud Natural Language API | Sentimento de documento |
| Visão computacional | Amazon Rekognition | Azure Vision in Foundry Tools | Cloud Vision API | Detecção de rótulos |
| Fala para texto | Amazon Transcribe | Azure Speech in Foundry Tools | Cloud Speech-to-Text V2 | Transcrição em lote |

Categorias consideradas e descartadas: **tradução automática** (domínio de entrada próximo demais de NLP), **análise de documentos/OCR** (sobreposição com visão computacional) e **modelos generativos** (comparação dominada pela escolha de modelo, com preços por token de alta volatilidade).

### Nomenclatura atualizada

Durante a pesquisa constatou-se que **a Microsoft reorganizou suas ofertas de IA sob a marca *Foundry Tools***. Os nomes usados neste relatório são os vigentes em setembro de 2026; os nomes anteriores (Azure AI Language, Text Analytics, Azure AI Vision, Azure AI Speech) aparecem entre parênteses na primeira ocorrência de cada capítulo.

### Equivalência e seus limites

A comparação é entre serviços **concorrentes**, não idênticos. Três limites à equivalência foram identificados já na seleção e são retomados nos capítulos:

- **O formato de saída do sentimento diverge nos três.** A AWS retorna uma de quatro classes, com um score para cada uma. A Azure retorna rótulo em nível de documento **e** de sentença, com três scores de confiança — mas **quatro** rótulos possíveis no documento, porque `mixed` aparece quando há sentenças positivas e negativas. O Google não retorna classe alguma, apenas `score` e `magnitude`.
- **Os vocabulários de rótulos de imagem não têm equivalência oficial**, e as escalas de confiança diferem (0–100 na AWS, 0–1 nos demais).
- **"Lote" significa compromissos de tempo diferentes** em cada provedor na transcrição de áudio, o que afeta diretamente a comparação de preço.
