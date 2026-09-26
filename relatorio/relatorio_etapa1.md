# Comparação de Serviços de Inteligência Artificial em Nuvem

## Etapa 1 — Análise Comparativa

**Disciplina:** Computação em Nuvem

**Programa:** Mestrado em Ciência da Computação — Universidade de Fortaleza (UNIFOR)

**Integrantes:**

- Davi Fonseca Passos
- Rafael Fonseca Pessoa
- Lucca Melo Nunes

**Provedores analisados:** Amazon Web Services · Microsoft Azure · Google Cloud

**Região dos preços:** `us-east-1` (AWS) · `East US` (Azure) · global em NLP e visão e `us-central1` em fala (Google Cloud)

**Moeda:** USD · **Preços consultados em:** 23/09/2026

**Repositório público (código, dados, gráficos e capítulos completos):** https://github.com/DaviFPassos/Teste_comparativo_nuvem

---


## 1. Introdução

Este relatório apresenta a análise comparativa de serviços de inteligência artificial oferecidos por **Amazon Web Services (AWS)**, **Microsoft Azure** e **Google Cloud**, sob a perspectiva de um desenvolvedor que precisa escolher entre eles para incorporá-los a uma aplicação.

A perspectiva adotada é deliberadamente a de quem **consome** o serviço, e não a de quem estuda o modelo por trás dele. As perguntas que orientam cada capítulo são as de uma decisão de integração: o que o serviço faz, como se chama, o que aceita de entrada, o que devolve, como se autentica, que limites impõe, quanto custa e em que situação compensa.

### Como este relatório foi construído

Toda afirmação técnica e todo preço vêm de **documentação oficial dos provedores**, consultada em **23 e 24 de setembro de 2026**, com URL e data registradas em `referencias/fontes.md`. Onde uma informação não foi localizada, ela aparece como **pendência declarada** — nunca preenchida por estimativa.

Duas decisões metodológicas merecem registro:

**Os preços vieram das APIs públicas de preço dos provedores, não das páginas comerciais.** As páginas de preço da Azure e do Google entregam suas tabelas por JavaScript, exibindo apenas `$-` no conteúdo estático. Em vez de recorrer a fontes secundárias, os valores foram obtidos da *AWS Price List API* e da *Azure Retail Prices API* — ambas públicas e mantidas pelos próprios provedores — e das tabelas servidas pela página de preços do Google.

**Os exemplos de código não foram executados.** A seção 3 do enunciado permite isso explicitamente nesta etapa, e cada arquivo declara esse estado. Nenhum resultado de execução, medição de latência ou taxa de acerto é apresentado neste relatório: tudo isso é objeto da Etapa 2.

### Região, moeda e data

| Parâmetro | Valor |
|---|---|
| AWS | **`us-east-1`** (N. Virginia) nas três categorias |
| Microsoft Azure | **`East US`** nas três categorias |
| Google Cloud | **Preço global** em Natural Language e Vision; **`us-central1`** (Iowa) em Speech-to-Text |
| Moeda | **USD** |
| Data de consulta dos preços | **23/09/2026** |

US East foi escolhida por ser a região de referência das tabelas da AWS e da Azure e por ter as nove ofertas disponíveis. Duas das APIs do Google comparadas (Natural Language e Vision) têm **preço global, não regional**.

**Uma ressalva explícita sobre a terceira.** A tabela da Cloud Speech-to-Text V2 é regional, e o preço utilizado é o de **`us-central1` (Iowa)** — que é US Central, **não** US East. Essa é a única linha do trabalho em que a região do Google não coincide com a das outras duas, e ela está registrada assim em `custos/premissas.csv` e na lista de limitações, em vez de ser apresentada como se fosse a mesma região.


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


## 3. NLP / análise de texto: análise de sentimento

**Operação comparada:** sentimento em nível de documento, sobre o mesmo texto em português (`O atendimento foi excelente.`)
**Modo de chamada:** síncrono, um documento por chamada
**Data da consulta às fontes:** 23/09/2026
**Região de referência:** US East (`us-east-1` / `East US` / global no caso do Google)


### 1. Objetivo da categoria e caso de uso

Análise de sentimento classifica a opinião predominante expressa em um texto. O caso de uso típico é processar avaliações de clientes, comentários de suporte ou menções em redes sociais para priorizar atendimento ou medir satisfação, sem que a equipe precise treinar um modelo próprio.

Todos os três provedores oferecem essa funcionalidade em modelos **pré-treinados**, acessíveis por chamada de API: o desenvolvedor envia texto e recebe uma avaliação de sentimento, sem etapa de treinamento, rotulagem ou hospedagem de modelo.

### 2. Serviços comparados e operação equivalente

| Provedor | Serviço | Operação síncrona de documento único |
|---|---|---|
| AWS | Amazon Comprehend | `DetectSentiment` |
| Microsoft Azure | Azure Language in Foundry Tools (antes Azure AI Language / Text Analytics) | Análise de sentimento via REST API ou client library |
| Google Cloud | Cloud Natural Language API (v1) | `analyzeSentiment` |

Cada provedor também oferece modos adicionais, que **não** entram na comparação por não serem equivalentes em carga: `BatchDetectSentiment` (até 25 documentos) e `StartSentimentDetectionJob` (assíncrono) na AWS; requisições assíncronas em lote na Azure; processamento de textos longos no Google.

### 3. Comparação técnica

As tabelas abaixo comparam entradas, saídas, formas de acesso, autenticação, limites e avisos oficiais dos três serviços. O capítulo completo — com a fonte oficial de cada afirmação e as pendências de verificação — está em [`etapa1/nlp.md`](https://github.com/DaviFPassos/Teste_comparativo_nuvem/blob/main/etapa1/nlp.md).


#### 3.1 Funcionalidades, entradas e saídas

| Aspecto | Amazon Comprehend | Azure Language | Cloud Natural Language |
|---|---|---|---|
| **Formato da saída** | Uma classe entre `POSITIVE`, `NEGATIVE`, `NEUTRAL` e `MIXED`, mais `SentimentScore` com um score para cada uma das quatro classes | Rótulo `positive`, `neutral`, `negative` ou `mixed` — este último **só em nível de documento**; três scores de confiança de 0 a 1 (positivo, neutro e negativo), que somam 1 | **Não retorna classe.** Devolve `score` (de −1,0 a +1,0) e `magnitude` (intensidade acumulada, não normalizada) |
| **Granularidade** | Documento | **Documento e sentença** (ambos na mesma resposta) | Documento e sentença |
| **Classe para texto ambíguo** | `MIXED` é uma **classe do próprio modelo**, distinta de `NEUTRAL`, com score próprio em `SentimentScore` | **`mixed` existe em nível de documento**, mas é **composto a partir das sentenças**: sai quando há ao menos uma sentença positiva e ao menos uma negativa. Não tem score de confiança próprio | Não há classe; cabe ao desenvolvedor definir limiares |
| **Codificação de entrada** | UTF-8 | Texto (string única por documento) | UTF-8 |
| **Tamanho máximo do documento** | **5 KB** por documento na operação síncrona de sentimento | **5.120 caracteres** por documento (síncrono), medidos por `StringInfo.LengthInTextElements` | **1.000.000 bytes** de conteúdo; até 100.000 tokens por requisição |
| **Documentos por requisição** | 1 (`DetectSentiment`); até 25 em `BatchDetectSentiment` | **10** documentos por requisição em análise de sentimento | 1 documento por requisição |
| **Tamanho máximo da requisição** | — | 1 MB | — |

O contraste mais importante para quem integra: **a AWS e a Azure entregam uma decisão pronta (uma classe), enquanto o Google entrega apenas um número contínuo.** Usar o Google exige que a aplicação defina os limiares que separam positivo, neutro e negativo — uma decisão de produto que os outros dois já tomam pelo desenvolvedor. Além disso, `magnitude` (Google) e `SentimentScore` (AWS) e confiança (Azure) são grandezas diferentes e não podem ser comparadas entre si.

**Como a Azure decide o rótulo do documento.** A documentação oficial publica a regra, e ela **não** é "o maior dos três scores":

| Sentenças do documento | Rótulo devolvido para o documento |
|---|---|
| Ao menos uma positiva, as demais neutras | `positive` |
| Ao menos uma negativa, as demais neutras | `negative` |
| Ao menos uma positiva **e** ao menos uma negativa | **`mixed`** |
| Todas neutras | `neutral` |

São, portanto, **três scores de confiança e quatro rótulos possíveis** no nível do documento. Isso muda a leitura da comparação: **dois dos três provedores rotulam texto ambíguo** — o que difere é o caminho. Na AWS, `MIXED` é uma classe do próprio modelo, com score próprio, e pode sair de um documento de uma única frase. Na Azure, `mixed` é composto a partir dos rótulos das sentenças, o que exige sentenças de sinais opostos no mesmo documento e não vem acompanhado de score próprio. O Google não rotula.

#### 3.2 Suporte a português

| Provedor | Códigos aceitos | Total de idiomas na operação |
|---|---|---|
| Amazon Comprehend | `pt` (Português, sem distinção de variante) | 12 idiomas, e o sentimento cobre todos eles |
| Azure Language | **`pt-BR` (Português do Brasil)** e `pt-PT` (Português de Portugal); `pt` também é aceito | **94 códigos de idioma** |
| Cloud Natural Language | `pt` (Português, sem distinção de variante) | 16 idiomas na análise de sentimento |

**Diferença relevante para aplicações brasileiras:** apenas a Azure distingue formalmente o português do Brasil do português de Portugal na análise de sentimento. AWS e Google tratam "português" como um único idioma. A documentação não afirma que essa distinção produza resultado melhor em textos brasileiros — isso seria uma conclusão experimental, fora do escopo desta etapa.

#### 3.3 Formas de acesso, autenticação e configuração

| Aspecto | Amazon Comprehend | Azure Language | Cloud Natural Language |
|---|---|---|---|
| **Acesso** | API REST, AWS SDKs (Python/boto3, Java, .NET, Node.js, Ruby...), AWS CLI | REST API, client libraries (C#, Java, JavaScript, Python), **contêiner Docker para execução local** | REST (`POST .../v1/documents:analyzeSentiment`), gRPC, client libraries |
| **Autenticação** | Credenciais IAM (chave de acesso/segredo ou role), resolvidas pela cadeia padrão do SDK | **Chave do recurso + endpoint** próprios do recurso criado, ou Microsoft Entra ID | Conta de serviço com Application Default Credentials (`GOOGLE_APPLICATION_CREDENTIALS`) ou chave de API |
| **Endpoint** | Regional (`comprehend.us-east-1.amazonaws.com`) | Endpoint próprio do recurso, vinculado à região escolhida na criação | `language.googleapis.com` (global) |
| **Configuração mínima** | Região + credenciais | Criar um recurso *Azure Language in Foundry Tools*, obter chave e endpoint | Projeto com a API habilitada + credenciais |

A Azure é a única das três que oferece **execução em contêiner local** da análise de sentimento, o que importa em cenários com restrição de saída de dados. Em contrapartida, é a única que exige criar previamente um recurso e administrar um par chave/endpoint específico dele.

#### 3.4 Limites operacionais e de taxa

| Aspecto | Amazon Comprehend | Azure Language | Cloud Natural Language |
|---|---|---|---|
| **Limite de requisições** | *Throttling* dinâmico: a AWS ajusta a vazão conforme a banda de processamento disponível, sem número fixo publicado para o modo síncrono | Depende do tier: **S/Multi-service 1.000 req/s**; **S0/F0 100 req/s e 300 req/min** | **600 requisições/minuto** e **800.000 requisições/dia** |
| **Regiões** | 13 regiões, incluindo US East (N. Virginia) e US East (Ohio); **não há região no Brasil** na lista publicada | Endpoint regional; East US disponível | API global |
| **Previsibilidade de vazão** | Baixa: não há cota publicada para planejar | Alta: cota explícita por tier | Alta: cota explícita |

O *throttling* dinâmico da AWS é uma diferença prática relevante: não é possível dimensionar a aplicação a partir de um número publicado, e a própria documentação recomenda implementar limitação de taxa no cliente e ativar alertas de cobrança.

#### 3.5 Situação do serviço (avisos oficiais)

| Provedor | Aviso na documentação oficial |
|---|---|
| AWS | Nenhum aviso de descontinuação encontrado. |
| **Azure** | **"Sentiment analysis and opinion mining retire from Azure Language on March 31, 2029"**, com recomendação de migrar cargas existentes e direcionar novos projetos ao Microsoft Foundry. |
| Google | Nenhum aviso de descontinuação na página do `analyzeSentiment`. A única descontinuação oficial da API é a da versão `v1beta1`, encerrada em **27/12/2019**, que não atinge a `v1` em uso. |

Este é um critério de decisão concreto: escolher a análise de sentimento da Azure hoje significa assumir uma migração antes de **31/03/2029**.

### 4. Exemplos de código

Os três exemplos executam a **mesma operação** sobre o **mesmo texto**, e estão em:


**[`exemplos/nlp/aws_comprehend.py`](https://github.com/DaviFPassos/Teste_comparativo_nuvem/blob/main/exemplos/nlp/aws_comprehend.py)** — trecho essencial. O arquivo completo, no link, traz a autenticação por variável de ambiente, o tratamento de erro, os limites do serviço e a fonte da adaptação:

```python
def detectar_sentimento(texto: str, idioma: str = IDIOMA) -> dict:
    """Envia um documento e devolve a resposta completa do DetectSentiment."""
    cliente = boto3.client("comprehend", region_name=REGIAO)
    return cliente.detect_sentiment(Text=texto, LanguageCode=idioma)
```


**[`exemplos/nlp/azure_language.py`](https://github.com/DaviFPassos/Teste_comparativo_nuvem/blob/main/exemplos/nlp/azure_language.py)** — trecho essencial. O arquivo completo, no link, traz a autenticação por variável de ambiente, o tratamento de erro, os limites do serviço e a fonte da adaptação:

```python
# A API recebe uma LISTA de documentos, mesmo para um único texto.
resultados = cliente.analyze_sentiment(documents=[TEXTO], language=IDIOMA)
```


**[`exemplos/nlp/google_natural_language.py`](https://github.com/DaviFPassos/Teste_comparativo_nuvem/blob/main/exemplos/nlp/google_natural_language.py)** — trecho essencial. O arquivo completo, no link, traz a autenticação por variável de ambiente, o tratamento de erro, os limites do serviço e a fonte da adaptação:

```python
documento = language_v1.Document(
    content=TEXTO,
    type_=language_v1.Document.Type.PLAIN_TEXT,
    language=IDIOMA,
)

resposta = cliente.analyze_sentiment(
    request={"document": documento, "encoding_type": language_v1.EncodingType.UTF8}
)
```


**Estado de validação:** os três exemplos são **ilustrativos e não foram executados pelo grupo**. Foram adaptados da documentação oficial de cada provedor, conforme permitido pela seção 3 do enunciado ("Nesta etapa, os exemplos não precisam ter sido desenvolvidos ou executados pelo grupo"). Cada arquivo declara sua dependência, a fonte da adaptação e o mecanismo de autenticação. Nenhuma credencial está embutida no código: todos leem variáveis de ambiente.

### 5. Modelo de cobrança

| Provedor | Unidade de cobrança | Regra de contagem | Preço na primeira faixa |
|---|---|---|---|
| Amazon Comprehend | Unidade de **100 caracteres** | `ceil(caracteres/100)`, com **mínimo de 3 unidades (300 caracteres) por requisição** | $0,0001 por unidade (até 10M de unidades/mês) |
| Azure Language | Registro de texto de **1.000 caracteres** | `ceil(caracteres/1000)` por documento | $1,00 por 1.000 registros (até 0,5M de registros/mês) |
| Cloud Natural Language | Unidade de **1.000 caracteres Unicode** | `ceil(caracteres/1000)`, com mínimo de 1 unidade por requisição | $1,00 por 1.000 unidades (de 5 mil a 1M de unidades/mês) |

Todos os preços acima são de **US East, em USD, consultados em 23/09/2026**, e estão em `custos/premissas.csv` com a URL da fonte. Os da AWS vêm da *AWS Price List API* e os da Azure da *Azure Retail Prices API* — ambas APIs públicas oficiais dos próprios provedores, usadas porque as páginas comerciais de preço entregam as tabelas por JavaScript.

A regra de contagem do Google foi confirmada pelo exemplo da própria página de preços: 800, 1.500 e 600 caracteres são cobrados como 1 + 2 + 1 = **4 unidades**, ou seja, arredondamento para cima com mínimo de uma unidade.

A diferença de unidade é o fator que mais afeta o custo comparado: **um texto curto de 100 caracteres consome 1 unidade na AWS (sujeita ao mínimo da requisição) e 1 unidade inteira de 1.000 caracteres na Azure e no Google.** O efeito disso sobre o custo real é calculado na Fase 4, com cenários de comprimento variável, e é exatamente por isso que o cenário usa textos de 100, 500, 1.200 e 4.000 caracteres.

### 6. Cenário de custo, fórmulas, premissas e resultados

#### Carga do cenário

**100.000 documentos por mês**, submetidos um por chamada síncrona, em cinco comprimentos: **100, 500, 1.200, 4.000 e 4.100 caracteres**. A quantidade é hipotética e declarada como tal; o que importa é que **é idêntica nos três provedores**, como exige a seção 4 do enunciado. Os comprimentos existem para expor o efeito do tamanho da unidade de cobrança, e o de 4.100 entra especificamente para testar se o empate que aparece em 4.000 é um patamar ou uma coincidência.

**Condições de entrada assumidas.** Um documento por requisição, texto plano, sem *opinion mining* nem análise por aspecto, e **um único idioma declarado** (`pt-BR` na Azure, `pt` na AWS e no Google). O limite do Comprehend é de **5 KB, medido em bytes**, e não em caracteres: em UTF-8 cada caractere acentuado ocupa 2 bytes, de modo que 4.100 caracteres só cabem nos 5 KB enquanto no máximo cerca de 25% deles forem acentuados (em português corrente, com 4% a 6% de acentuados, o documento fica em torno de 4,2 KB). Textos fora dessa condição precisariam ser divididos, e a divisão mudaria a contagem de unidades. Os limites da Azure (5.120 caracteres) e do Google (1.000.000 de bytes) não são atingidos em nenhum dos comprimentos.

#### Fórmulas

```
AWS:     unidades = max(3, ceil(caracteres/100)) x 100.000 documentos
Azure:   registros = ceil(caracteres/1000) x 100.000 documentos
Google:  unidades = max(1, ceil(caracteres/1000)) x 100.000 documentos
```

O custo é progressivo por faixa: cada parcela do volume é cobrada ao preço da faixa em que cai — nunca o volume inteiro ao preço da última faixa.

#### Resultados (USD/mês, sem franquia)

| Comprimento | Unidades cobradas AWS | AWS | Azure | Google |
|---|---|---|---|---|
| 100 caracteres | 300.000 (mínimo de 3/doc) | **$30,00** | $100,00 | $100,00 |
| 500 caracteres | 500.000 | **$50,00** | $100,00 | $100,00 |
| 1.200 caracteres | 1.200.000 | **$120,00** | $200,00 | $200,00 |
| 4.000 caracteres | 4.000.000 | $400,00 | $400,00 | $400,00 |
| 4.100 caracteres | 4.100.000 | **$410,00** | $500,00 | $500,00 |

![Custo de análise de sentimento por comprimento de documento](../custos/graficos/custos_nlp.png)

#### O que os números mostram

O cenário revela um efeito que a tabela de preços isolada esconde: **para textos curtos, a granularidade da unidade importa mais que o preço unitário**. Um comentário de 100 caracteres consome 3 unidades de 100 caracteres na AWS, mas **uma unidade inteira de 1.000 caracteres** na Azure e no Google — pagando-se, nos dois casos, por 900 caracteres não enviados. O resultado é que a AWS cobra **30% do que cobram os concorrentes** nesse comprimento — uma redução de 70%, ou 3,3× mais barato.

A vantagem encolhe conforme o texto cresce e some perto de 4.000 caracteres — mas não só no ponto exato. Recalculando com as próprias funções do projeto para toda a vizinhança:

| Comprimento | AWS | Azure | Google |
|---|---|---|---|
| 3.900 caracteres | $390,00 | $400,00 | $400,00 |
| **3.901 a 4.000 caracteres** | **$400,00** | $400,00 | $400,00 |
| 4.001 caracteres | **$410,00** | $500,00 | $500,00 |
| 4.100 caracteres | **$410,00** | $500,00 | $500,00 |

**O empate vale para toda uma janela de 100 caracteres — de 3.901 a 4.000 —, não apenas para 4.000 exato.** A razão é aritmética: nesse trecho, `ceil(c/100)` (a regra da AWS) já chegou a 40 e só muda em 4.001, enquanto `ceil(c/1000)` (a regra de Azure e Google) permanece em 4 até 4.000 e só sobe em 4.001. As duas contagens colam nesse intervalo específico, não em um ponto isolado. O mesmo padrão se repete perto de cada múltiplo de 1.000 (por exemplo, 2.901 a 3.000, ou 1.901 a 2.000): é uma janela de 100 caracteres logo abaixo de cada múltiplo, não o múltiplo isolado.

Fora dessas janelas, a diferença volta — até cerca de 22% a mais na Azure e no Google na vizinhança de 4.000 caracteres. O que muda a partir daí é que a granularidade deixa de ser o único fator: passa a dividir espaço com as faixas de volume.

Isso tem consequência prática direta: **a escolha mais econômica depende do comprimento típico do texto da aplicação.** Para avaliações curtas de produto ou mensagens de chat, a diferença chega a 3,3 para 1; para documentos longos, cai para a casa de 0% a 22%, e só pode ser resolvida calculando com a distribuição real de comprimentos da aplicação.

#### Franquias

As três franquias existem, mas **não são a mesma coisa** e por isso não entram na comparação principal:

| Provedor | Franquia | Natureza | Aplicável a este cenário? |
|---|---|---|---|
| AWS | 50.000 unidades/mês por API | **Promocional**: vale 12 meses a partir da primeira requisição | **Sim, só nos 12 primeiros meses** — abate a fatura da própria operação, na mesma conta e no mesmo tier |
| Azure | 5.000 registros/mês | **Tier F0 separado**, compartilhado entre várias features do Azure Language | **Não** — é um recurso à parte, não um desconto no tier S usado no cenário |
| Google | 5.000 unidades/mês | **Faixa da própria tabela** cobrada a $0,00; permanente | **Sim** — é a primeira faixa da tabela que já está sendo aplicada |

**Regra adotada em todo o trabalho.** A coluna `custo_usd_com_franquia` de `custos/resultados.csv` desconta **somente** as franquias que incidem sobre a operação comparada; a coluna `franquia_aplicada` registra a decisão linha por linha e `custos/franquias.csv` guarda a justificativa de cada caso. Abater o tier F0 da Azure de uma fatura do tier pago somaria duas coisas que a Microsoft cobra separadamente: o F0 é um **recurso à parte**, com cota e limites próprios, e não um desconto no recurso pago. Usá-lo exigiria dividir a carga entre dois recursos — uma hipótese de arquitetura que teria de ser definida e justificada, e que este cenário não adota.

Aplicada essa regra ao cenário de 100 caracteres: **$25,00 na AWS** (e só durante os 12 primeiros meses), **$100,00 na Azure** (sem abatimento) e **$95,00 no Google** (permanente).

**Leitura honesta da coluna do Google.** Como a faixa de 0,00 USD é parte permanente da tabela on-demand, **a cobrança habitual do Google é $95,00, não $100,00**. O valor sem franquia é uma simulação criada para manter a comparação simétrica com AWS e Azure, e não a fatura esperada. Nas tabelas deste capítulo os dois números aparecem lado a lado justamente por isso. Como duas das três franquias são temporárias ou inaplicáveis, **a comparação principal usa os preços sem franquia**, por ser a única base que significa a mesma coisa nos três — um **cenário comparativo sem franquias**, não a fatura esperada de nenhum dos três (a do Google, em especial, costuma ser menor por causa da faixa permanente).

### 7. Síntese: vantagens, restrições e adequação por cenário

#### As três diferenças que mais pesam

**1. O Google não entrega uma decisão, entrega um número.** AWS e Azure devolvem uma classe pronta (`POSITIVE`/`positive`); o Google devolve `score` e `magnitude` e deixa para a aplicação definir onde ficam as fronteiras entre positivo, neutro e negativo. Isso não é detalhe de formato: é trabalho de produto transferido para quem integra, e uma decisão que precisa ser justificada e congelada antes de qualquer avaliação. Em compensação, dá controle a quem quer calibrar o limiar ao próprio domínio.

**2. AWS e Azure rotulam texto ambíguo; o Google não — e as duas chegam lá por caminhos diferentes.** Na AWS, `MIXED` é uma classe do modelo, com score próprio em `SentimentScore`, e pode sair de um documento de uma única frase. Na Azure, `mixed` é um rótulo **de documento**, composto pela regra oficial: ao menos uma sentença positiva e ao menos uma negativa. A consequência prática para quem integra é essa: a AWS distingue "opinião dividida" de "sem opinião" já em textos de uma frase; a Azure só produz esse rótulo quando o documento tem sentenças de sinais opostos, e sem score próprio para ele. No Google não há classe alguma — quem integra define os limiares.

**3. Só a Azure distingue português do Brasil.** `pt-BR` e `pt-PT` são códigos separados na Azure, contra um `pt` genérico na AWS e no Google. Para um produto brasileiro isso é atraente — mas **a documentação não promete resultado melhor**, e afirmar que produz seria extrapolar. É exatamente o tipo de hipótese que a Etapa 2 pode testar.

#### Custo: a granularidade da unidade domina em textos curtos

O cenário de 100.000 documentos mostrou que **a AWS cobra 30% do que cobram os concorrentes em textos de 100 caracteres** ($30,00 contra $100,00 — redução de 70%), porque cobra em unidades de 100 caracteres enquanto Azure e Google cobram uma unidade inteira de 1.000. A vantagem cai a zero na janela de 3.901 a 4.000 caracteres, onde os três empatam em $400,00, mas volta em 4.001 ($410,00 contra $500,00): o empate vale para essa janela específica de 100 caracteres antes de cada múltiplo de 1.000, e não para documentos longos em geral.

Ou seja: **não existe "o mais barato" nesta categoria — existe o mais barato para o seu comprimento de texto.**

#### O risco que nenhuma tabela de preço mostra

A análise de sentimento da Azure tem **encerramento anunciado para 31/03/2029**, com migração recomendada para o Microsoft Foundry. Nenhum concorrente comparado tem aviso equivalente. Para um sistema que se espera manter por anos, isso é um custo futuro de migração que não aparece em nenhum cenário de preço.

#### Adequação por cenário

| Situação | Alternativa mais adequada | Por quê |
|---|---|---|
| Alto volume de **textos curtos** (avaliações, chat, comentários) | **Amazon Comprehend** | Unidade de 100 caracteres reduz o custo em 70% no cenário de 100 caracteres; `MIXED` sai com score próprio mesmo em textos de uma única frase |
| Necessidade de **sentimento por sentença** junto com o do documento | **Azure Language** | Entrega os dois níveis na mesma resposta |
| Restrição de **saída de dados** do ambiente próprio | **Azure Language** | Único dos três com contêiner Docker para execução local |
| Aplicação que quer **calibrar o limiar** ao próprio domínio | **Cloud Natural Language** | O score contínuo é matéria-prima, não uma decisão já tomada |
| Sistema com **horizonte longo de manutenção** | AWS ou Google | A oferta da Azure tem encerramento datado |
| **Documentos longos** (acima de ~4.000 caracteres) | Calcular com o comprimento real | O empate só vale na janela de 100 caracteres logo abaixo de cada múltiplo de 1.000 (ex.: 3.901–4.000); fora dela a AWS continua até ~22% mais barata |

**O que esta etapa não responde:** qual dos três classifica melhor sentimento em português. Isso exige execução, gabarito e medição — é o objeto da Etapa 2.


## 4. Visão computacional: detecção de rótulos em imagem

**Operação comparada:** detecção de rótulos (labels/tags) do conteúdo da mesma imagem, sem localização
**Modo de chamada:** síncrono, uma imagem por chamada
**Data da consulta às fontes:** 23/09/2026
**Região de referência:** US East (`us-east-1` / `East US` / global no caso do Google)


### 1. Objetivo da categoria e caso de uso

Detecção de rótulos responde à pergunta "o que aparece nesta imagem?", devolvendo termos como *pessoa*, *carro* ou *praia* com um grau de confiança. O caso de uso típico é indexar e tornar pesquisável um acervo de imagens enviadas por usuários, alimentar filtros de catálogo ou fazer uma triagem inicial de conteúdo antes de revisão humana.

Escolheu-se a detecção de rótulos — e não detecção de objetos com caixas delimitadoras — porque é a operação com equivalente direto nos três provedores e a que produz saída mais comparável.

### 2. Serviços comparados e operação equivalente

| Provedor | Serviço | Operação comparada |
|---|---|---|
| AWS | Amazon Rekognition | `DetectLabels`, feature `GENERAL_LABELS` |
| Microsoft Azure | Azure Vision in Foundry Tools — Image Analysis | *Tag visual features* (Tags), via Analyze Image |
| Google Cloud | Cloud Vision API | Feature `LABEL_DETECTION`, via `images:annotate` |

### 3. Comparação técnica

As tabelas abaixo comparam entradas, saídas, formas de acesso, autenticação, limites e avisos oficiais dos três serviços. O capítulo completo — com a fonte oficial de cada afirmação e as pendências de verificação — está em [`etapa1/visao.md`](https://github.com/DaviFPassos/Teste_comparativo_nuvem/blob/main/etapa1/visao.md).


#### 3.1 Entradas: formatos e limites

| Aspecto | Amazon Rekognition | Azure Image Analysis | Cloud Vision API |
|---|---|---|---|
| **Formatos aceitos** | **Apenas PNG e JPEG** | v4.0: JPEG, PNG, GIF, BMP, WEBP, ICO, TIFF, MPO · v3.2: JPEG, PNG, GIF, BMP | Em `images:annotate` (o endpoint comparado): JPEG, PNG8, PNG24, GIF, GIF animado (só o primeiro quadro), BMP, WEBP, RAW, ICO. **PDF e TIFF existem, mas por outro endpoint** — ver nota abaixo |
| **Tamanho máximo** | **15 MB** como objeto no Amazon S3; **5 MB** quando enviada como bytes na requisição | v4.0: **menos de 20 MB** · v3.2: **menos de 4 MB** | **20 MB** por imagem; requisição JSON limitada a **10 MB** |
| **Dimensões** | Mínimo 80×80 px; máximo **10.000 px** de largura e altura para `DetectLabels` | Entre **50×50** e **16.000×16.000** px | Resolução recomendada de **640×480 px** para `LABEL_DETECTION` |
| **Origem da imagem** | Objeto no Amazon S3 ou bytes na requisição | Bytes na requisição ou URL da imagem | Arquivo local em base64, URI do Cloud Storage (`gs://`) ou URL remota |

O Cloud Vision aceita a maior variedade de formatos e o Rekognition a menor (só PNG e JPEG). Para um pipeline que recebe upload livre de usuários, isso significa que **a AWS exige uma etapa de conversão** que os outros dois dispensam em vários casos.

**PDF e TIFF no Cloud Vision são outro caminho, não o mesmo.** A lista oficial de formatos suportados inclui PDF e TIFF, mas eles **não** são aceitos pelo `images:annotate` usado nesta comparação: exigem o endpoint **`files:annotate`**, que trata o arquivo como documento de várias páginas. O `LABEL_DETECTION` está entre as features suportadas nesse endpoint, de modo que a capacidade existe — porém com fluxo, limites e condições próprios (entre eles, chaves de API não são aceitas em `files:annotate`). Misturar as duas coisas na mesma linha da tabela superestimaria a compatibilidade do endpoint comparado, e por isso os dois caminhos ficam separados aqui.

#### 3.2 Saídas

| Aspecto | Amazon Rekognition | Azure Image Analysis | Cloud Vision API |
|---|---|---|---|
| **Campos por rótulo** | `Name`, `Confidence`, `Parents` (hierarquia), `Aliases` (sinônimos), `Categories`, `Instances` (com `BoundingBox` quando aplicável) | Tags com nome e confiança | `mid` (identificador no Google Knowledge Graph), `description`, `score`, `topicality` |
| **Escala da confiança** | **0 a 100** | 0 a 1 | **0 a 1** |
| **Estrutura semântica** | Hierarquia explícita: um rótulo traz seus rótulos-pai, apelidos e categoria | Lista plana de tags | `mid` permite ligar o rótulo a uma entidade do Knowledge Graph |
| **Controle de quantidade** | `MaxLabels` e `MinConfidence` | Parâmetros da chamada Analyze | `maxResults` (**padrão 10** se omitido) |
| **Filtros** | `LabelInclusionFilters`, `LabelExclusionFilters`, `LabelCategoryInclusionFilters`, `LabelCategoryExclusionFilters` | — | — |
| **Versão do modelo na resposta** | `LabelModelVersion` | — | — |

Três diferenças importam na integração:

1. **A escala de confiança não é a mesma.** A AWS usa 0–100 e os outros dois 0–1. Qualquer comparação ou limiar compartilhado exige normalização explícita.
2. **A AWS é a única que devolve taxonomia.** `Parents`, `Aliases` e `Categories` permitem agrupar rótulos sem manter um dicionário próprio, e os filtros de inclusão/exclusão permitem restringir a resposta no servidor. Nos outros dois isso fica por conta da aplicação.
3. **O Google é o único que devolve identificador estável** (`mid`) ligado ao Knowledge Graph, útil para associar rótulos a uma base de conhecimento em vez de comparar strings.

Os vocabulários de rótulos **não são compatíveis entre provedores**: nomes, granularidade e idioma dos termos diferem, e não há tabela oficial de equivalência. Comparar "quantos rótulos cada um acertou" exigiria um gabarito próprio — trabalho de avaliação prática, não desta etapa.

#### 3.3 Formas de acesso, autenticação e configuração

| Aspecto | Amazon Rekognition | Azure Image Analysis | Cloud Vision API |
|---|---|---|---|
| **Acesso** | API REST, AWS SDKs (Python, Java, .NET, Node.js, Ruby), AWS CLI | REST API (`aka.ms/vision-4-0-ref`) e client library SDK | REST (`POST https://vision.googleapis.com/v1/images:annotate`), gRPC, client libraries, `gcloud ml vision detect-labels` |
| **Autenticação** | Credenciais IAM; para ler imagem do S3, também permissão de leitura no bucket | Chave + endpoint do recurso *Azure Vision in Foundry Tools* | Application Default Credentials ou chave de API |
| **Configuração mínima** | Região + credenciais (+ bucket S3, se usar essa origem) | Criar o recurso **em região suportada** (East US está na lista) | Projeto com a API habilitada |

A Azure é a única das três com **restrição de região documentada para a própria funcionalidade**: a página oficial lista as regiões em que o Image Analysis existe, e recursos criados fora delas não atendem à operação. AWS e Google não impõem essa barreira para a operação comparada.

#### 3.4 Limites operacionais e de taxa

| Aspecto | Amazon Rekognition | Azure Image Analysis | Cloud Vision API |
|---|---|---|---|
| **Limite de requisições** | TPS por operação e por região, ajustável via AWS Service Quotas; erros `ProvisionedThroughputExceededException` e `ThrottlingException` são documentados como reentráveis | Conforme o tier do recurso | Cotas por projeto |
| **Recomendação oficial** | Suavizar picos de tráfego (fila), configurar *retries* com *backoff* exponencial e *jitter* | — | — |
| **Processamento em massa** | Image Bulk Analysis: lotes de até 10.000 imagens, manifesto de até 50 MB | — | — |

#### 3.5 Situação do serviço (avisos oficiais)

| Provedor | Aviso na documentação oficial |
|---|---|
| AWS | Nenhum aviso de descontinuação para `DetectLabels`. |
| **Azure** | **"The Image Analysis 4.0 service in Azure Vision in Foundry Tools is deprecated and will be retired on September 25, 2028"**, com guia de migração indicado. Funcionalidades da versão 4.0 em preview já foram encerradas antes: Custom Image Classification, Custom Object Detection, Product Recognition e a API Segment / remoção de fundo foram desativadas em **31/03/2025**. |
| Google | Nenhum aviso de descontinuação para `LABEL_DETECTION`. |

Esse é o segundo serviço da Azure comparado neste trabalho com encerramento anunciado — o primeiro foi a análise de sentimento (31/03/2029). O histórico de funcionalidades já retiradas em 2025 reforça que a cadência de mudança da oferta de visão da Azure é mais alta que a dos concorrentes, o que é um fator de risco de manutenção para quem integra hoje.

### 4. Exemplos de código

Os três exemplos executam a **mesma operação** sobre a **mesma imagem**:


**[`exemplos/visao/aws_rekognition.py`](https://github.com/DaviFPassos/Teste_comparativo_nuvem/blob/main/exemplos/visao/aws_rekognition.py)** — trecho essencial. O arquivo completo, no link, traz a autenticação por variável de ambiente, o tratamento de erro, os limites do serviço e a fonte da adaptação:

```python
return cliente.detect_labels(
    Image={"Bytes": bytes_imagem},
    MaxLabels=MAX_LABELS,
    MinConfidence=MIN_CONFIANCA,
    Features=["GENERAL_LABELS"],
)
```


**[`exemplos/visao/azure_image_analysis.py`](https://github.com/DaviFPassos/Teste_comparativo_nuvem/blob/main/exemplos/visao/azure_image_analysis.py)** — trecho essencial. O arquivo completo, no link, traz a autenticação por variável de ambiente, o tratamento de erro, os limites do serviço e a fonte da adaptação:

```python
resultado = cliente.analyze(
    image_data=bytes_imagem,
    visual_features=[VisualFeatures.TAGS],
)
```


**[`exemplos/visao/google_vision.py`](https://github.com/DaviFPassos/Teste_comparativo_nuvem/blob/main/exemplos/visao/google_vision.py)** — trecho essencial. O arquivo completo, no link, traz a autenticação por variável de ambiente, o tratamento de erro, os limites do serviço e a fonte da adaptação:

```python
resposta = cliente.label_detection(image=imagem, max_results=MAX_RESULTADOS)
```


**Estado de validação:** exemplos **ilustrativos, não executados pelo grupo**, adaptados da documentação oficial de cada provedor, conforme a seção 3 do enunciado. Nenhuma credencial está embutida: todos leem variáveis de ambiente.

### 5. Modelo de cobrança

| Provedor | Unidade de cobrança | Preço na primeira faixa |
|---|---|---|
| Amazon Rekognition | Por **imagem processada** (APIs do Grupo 2, onde está o `DetectLabels`) | $0,0010 por imagem (até 1M de imagens/mês) |
| Azure Image Analysis | Por **transação**, cobrada a cada 1.000 (feature *Tag* pertence ao **Grupo 1**) | $1,00 por 1.000 transações (até 1M/mês) |
| Cloud Vision API | Por **unidade**, onde cada feature aplicada a uma imagem conta como uma unidade | $1,50 por 1.000 unidades (de 1.000 a 5M/mês) |

Preços de **US East, em USD, consultados em 23/09/2026**, registrados em `custos/premissas.csv`. Os da AWS vêm da *AWS Price List API* e os da Azure da *Azure Retail Prices API*.

A regra do Cloud Vision confirma-se na página oficial: aplicar duas features à mesma imagem gera duas unidades cobradas. Como o cenário usa **uma única feature por imagem** (`LABEL_DETECTION`), a carga permanece equivalente entre os três. O enquadramento da feature *Tag* no Grupo 1 da Azure — e não no Grupo 2, mais caro na primeira faixa — também foi confirmado na página de preços, que lista `Tag` entre as features do Grupo 1.

### 6. Cenário de custo, fórmulas, premissas e resultados

#### Carga do cenário

**100.000 imagens por mês**, uma chamada por imagem, com **uma única feature de detecção de rótulos** em cada. A quantidade é hipotética e declarada como tal, e é idêntica nos três provedores.

Restringir a uma feature por imagem não é detalhe: é o que mantém a carga comparável, já que o Cloud Vision cobra por feature aplicada e não por imagem.

#### Fórmulas

```
AWS:     100.000 imagens (1 unidade por imagem)
Azure:   100.000 transações (1 imagem com 1 feature = 1 transação)
Google:  100.000 unidades (1 feature x 1 imagem = 1 unidade)
```

#### Resultados (USD/mês)

| Provedor | Unidades cobradas | Sem franquia | Com a franquia aplicável |
|---|---|---|---|
| AWS — Rekognition | 100.000 imagens | **$100,00** | $99,00 (só nos 12 primeiros meses) |
| Azure — Image Analysis (Grupo 1) | 100.000 transações | **$100,00** | **$100,00** (o F0 não abate o tier pago) |
| Google — Cloud Vision | 100.000 unidades | $150,00 | $148,50 (faixa permanente da tabela) |

![Custo de detecção de rótulos em 100.000 imagens](../custos/graficos/custos_visao.png)

#### O que os números mostram

Nesta categoria a comparação é mais simples que em NLP, porque **a unidade de cobrança é praticamente a mesma nos três** — uma imagem analisada. Não há efeito de granularidade a explorar: o que se compara é o preço direto.

AWS e Azure ficam empatados em $100,00 no volume do cenário, e o Google fica **50% acima**, em $150,00. Vale registrar que essa ordem não é estável em qualquer volume: as faixas têm degraus diferentes (a Azure desce para $0,65/mil a partir de 1M de transações, a AWS para $0,0008/imagem a partir de 1M de imagens, e o Google só desce para $1,00/mil depois de 5M de unidades), de modo que um volume muito maior muda as distâncias relativas.

#### Franquias

| Provedor | Franquia | Natureza | Aplicável a este cenário? |
|---|---|---|---|
| AWS | 1.000 imagens/mês | Promocional, 12 meses a partir da criação da conta | **Sim, só nos 12 primeiros meses** |
| Azure | 5.000 transações/mês (limite de 20/minuto) | Tier F0 separado | **Não** — recurso à parte, não desconto no tier pago. O que de fato impede o F0 de sustentar o cenário é a **cota mensal de 5.000 transações** (5% das 100.000 necessárias); o limite de 20/minuto, isoladamente, processaria as 100.000 imagens em cerca de 83 horas, o que caberia num mês — não é ele o fator restritivo |
| Google | 1.000 unidades/mês | Primeira faixa da tabela, permanente | **Sim** |

Como a faixa de 0,00 USD do Google é permanente, **a cobrança habitual dele é $148,50, não $150,00**; o valor sem franquia é uma simulação para manter a comparação simétrica com AWS e Azure.

**Regra adotada em todo o trabalho.** A coluna `custo_usd_com_franquia` de `custos/resultados.csv` desconta **somente** as franquias que incidem sobre a operação comparada; a coluna `franquia_aplicada` registra a decisão linha por linha e `custos/franquias.csv` guarda a justificativa de cada caso. Abater o tier F0 da Azure de uma fatura do tier pago somaria duas coisas que a Microsoft cobra separadamente: o F0 é um **recurso à parte**, com cota e limites próprios, e não um desconto no recurso pago. Usá-lo exigiria dividir a carga entre dois recursos — uma hipótese de arquitetura que teria de ser definida e justificada, e que este cenário não adota.

### 7. Síntese: vantagens, restrições e adequação por cenário

#### O que separa as três ofertas

**A AWS é a única que entrega taxonomia junto com o rótulo.** `Parents`, `Aliases` e `Categories` permitem agrupar e filtrar rótulos sem manter um dicionário próprio, e os filtros de inclusão/exclusão rodam no servidor. Nos outros dois, essa camada fica por conta da aplicação.

**O Google é o mais permissivo na entrada e o único com identificador estável.** No endpoint comparado aceita RAW, WEBP, GIF, BMP e ICO além de PNG e JPEG — contra **apenas PNG e JPEG na AWS** —, o que elimina uma etapa de conversão em pipelines que recebem upload livre; PDF e TIFF também são suportados, mas pelo endpoint `files:annotate`, com fluxo próprio. E o campo `mid` liga cada rótulo a uma entidade do Knowledge Graph, em vez de obrigar comparação por string.

**A Azure é a que exige mais atenção à região e ao calendário.** É a única com lista fechada de regiões para a própria funcionalidade, e a única com **encerramento anunciado: o Image Analysis 4.0 sai de operação em 25/09/2028**. O histórico reforça o ponto: quatro funcionalidades em preview já foram desativadas em 31/03/2025.

Um detalhe que atravessa a integração dos três: **a escala de confiança não é a mesma** (0–100 na AWS, 0–1 nos outros dois), e os vocabulários de rótulos não têm equivalência oficial. Trocar de provedor aqui não é trocar de endpoint — é recalibrar limiares e remapear termos.

#### Custo: a categoria mais previsível das três

Como a unidade de cobrança é essencialmente a mesma nos três — uma imagem analisada — não há efeito de granularidade a explorar. No cenário de 100.000 imagens, **AWS e Azure empatam em $100,00 e o Google fica 50% acima, em $150,00**.

Essa ordem não vale para qualquer volume: os degraus de faixa são diferentes, e o Google só reduz o preço depois de 5 milhões de unidades, enquanto AWS e Azure já reduzem a partir de 1 milhão.

#### Adequação por cenário

| Situação | Alternativa mais adequada | Por quê |
|---|---|---|
| Pipeline com **formatos heterogêneos** de upload | **Cloud Vision** | Aceita RAW, WEBP, GIF, BMP e ICO no mesmo endpoint, e PDF/TIFF por `files:annotate`; a AWS exigiria conversão para PNG/JPEG |
| Necessidade de **agrupar rótulos por categoria ou hierarquia** | **Amazon Rekognition** | Único que devolve `Parents`, `Aliases` e `Categories` |
| Integração com **base de conhecimento** | **Cloud Vision** | O `mid` dá identificador estável em vez de string |
| Sensibilidade a **custo** no volume analisado | **AWS ou Azure** | $100,00 contra $150,00 do Google em 100 mil imagens |
| **Volume muito alto** (acima de 1 milhão/mês) | Recalcular | Os degraus de faixa diferem e mudam a ordem |
| Sistema com **horizonte longo de manutenção** | AWS ou Google | O Image Analysis 4.0 da Azure encerra em 25/09/2028 |

**O que esta etapa não responde:** qual serviço produz rótulos mais corretos ou mais úteis. Sem gabarito e sem execução, isso não é afirmável.


## 5. Fala para texto: transcrição de áudio

**Operação comparada:** transcrição assíncrona (em lote) do mesmo arquivo de áudio em português do Brasil
**Modo de chamada:** assíncrono / lote — único modo oferecido pelos três para arquivos longos
**Data da consulta às fontes:** 23/09/2026
**Região de referência:** `us-east-1` (N. Virginia) na AWS e `East US` na Azure; no Google, **`us-central1` (Iowa)** — a tabela da Cloud Speech-to-Text V2 é regional e `us-central1` **não** é uma região US East. A diferença está declarada como limitação em vez de ser tratada como equivalência


### 1. Objetivo da categoria e caso de uso

Conversão de fala em texto transforma áudio gravado em transcrição pesquisável. O caso de uso típico é processar gravações de atendimento, reuniões ou conteúdo audiovisual para gerar legendas, permitir busca textual ou alimentar análises posteriores — inclusive análise de sentimento, o que liga esta categoria à primeira.

**Por que o modo em lote e não o tempo real:** transcrição em tempo real e em lote têm condições de uso, requisitos de formato e preços distintos. Comparar uma com a outra produziria números sem sentido. Os três provedores oferecem o modo em lote para arquivos armazenados, e é sobre ele que a comparação é feita.

### 2. Serviços comparados e operação equivalente

| Provedor | Serviço | Operação em lote | Operação em tempo real (fora da comparação) |
|---|---|---|---|
| AWS | Amazon Transcribe | `StartTranscriptionJob` | `StartStreamTranscription` |
| Microsoft Azure | Azure Speech in Foundry Tools | `Transcription_Create` (Speech to text REST API) | Reconhecimento em tempo real |
| Google Cloud | Cloud Speech-to-Text V2 | `BatchRecognize` | `StreamingRecognize`; `Recognize` para áudio < 60 s |

### 3. Comparação técnica

As tabelas abaixo comparam entradas, saídas, formas de acesso, autenticação, limites e avisos oficiais dos três serviços. O capítulo completo — com a fonte oficial de cada afirmação e as pendências de verificação — está em [`etapa1/fala.md`](https://github.com/DaviFPassos/Teste_comparativo_nuvem/blob/main/etapa1/fala.md).


#### 3.1 Entradas: formatos e origem do áudio

| Aspecto | Amazon Transcribe | Azure Speech (lote) | Cloud Speech-to-Text V2 |
|---|---|---|---|
| **Formatos em lote** | AMR, FLAC, M4A, MP3, MP4, Ogg, WebM, WAV | **WAV, MP3, OPUS/OGG, FLAC, WMA, AAC, ALAW em WAV, MULAW em WAV, AMR, WebM, SPEEX** | Formatos de áudio suportados pela API v2 |
| **Formatos recomendados** | FLAC ou WAV com PCM 16 bits | Formatos sem perda: WAV (PCM) e FLAC | — |
| **Origem do arquivo** | **Obrigatoriamente um bucket do Amazon S3** | URI público, URI com SAS, ou contêiner do Azure Blob Storage via *trusted Azure services* (identidade gerenciada) | Cloud Storage (`gs://`) para `BatchRecognize` |
| **Canais de áudio** | Mono e estéreo; **mais de dois canais não é suportado** | — | — |
| **Taxa de amostragem** | Opcional no lote; 8.000 Hz típico em telefonia e de 16.000 a 48.000 Hz em alta fidelidade | — | — |

A Azure aceita a lista mais ampla de formatos e é a única das três que permite **URI público** como origem, dispensando armazenamento no próprio provedor. A AWS é a mais restritiva nesse ponto: o arquivo precisa estar no S3, o que acrescenta um passo de upload e uma configuração de permissão ao fluxo.

#### 3.2 Saídas

| Aspecto | Amazon Transcribe | Azure Speech (lote) | Cloud Speech-to-Text V2 |
|---|---|---|---|
| **Formato** | JSON | JSON | JSON |
| **Conteúdo mínimo** | Transcrição em bloco (`transcripts`), detalhamento por palavra e pontuação (`items`) com tempo de início, fim e confiança, e segmentos de áudio (`audio_segments`) | Transcrição com metadados da execução | Transcrição com alternativas e confiança |
| **Onde o resultado fica** | Bucket S3 do cliente **ou** bucket gerenciado pelo serviço, com **URI temporária válida por 15 minutos**; no bucket padrão, o resultado é **apagado quando o job expira, em 90 dias** | Contêiner de armazenamento, recuperado de forma assíncrona | Cloud Storage ou resposta da operação |
| **Recursos adicionais** | Diarização (separação de locutores), identificação de canal | **Diarização** (`diarizationEnabled` para dois locutores; `diarization` com `minCount`/`maxCount` para três ou mais, máximo abaixo de 36), identificação de idioma (`languageIdentification`), timestamps por palavra, modo de pontuação e filtro de profanidade | Diarização disponível no modelo `chirp_3` |

O detalhe de retenção da AWS é operacionalmente relevante: quem usa o bucket padrão precisa baixar a transcrição antes de 90 dias, e a URI temporária expira em 15 minutos — se expirar, é preciso uma nova chamada `GetTranscriptionJob`.

#### 3.3 Suporte ao português do Brasil

| Provedor | Código | Cobertura |
|---|---|---|
| Amazon Transcribe | **`pt-BR`** (Português, Brasileiro) e `pt-PT` (Português) | `pt-BR` em lote **e** streaming; suporta transcrição de números, acrônimos, *redaction* e Call Analytics pós-chamada e em tempo real |
| Azure Speech | **`pt-BR`** (Portuguese, Brazil) | Suportado, inclusive com *fast transcription* |
| Cloud Speech-to-Text V2 | **`pt-BR`** (Portuguese, Brazil) | Disponível nos modelos `chirp_3`, `long`, `short`, `telephony` e `telephony_short`; o `chirp_3` acrescenta diarização |

**Diferença em relação à categoria de NLP:** aqui os três provedores distinguem formalmente o português do Brasil. Na análise de sentimento, apenas a Azure faz essa distinção. Isso mostra que o suporte a variantes regionais não é uniforme nem dentro do mesmo provedor.

**Escolha do modelo: Google e Azure expõem, a AWS não.** O Google publica modelos nomeados e otimizados por tipo de áudio (`telephony`, `long`, `short`, `chirp_3`) e o desenvolvedor escolhe um deles no campo `model` da configuração. A Azure também aceita um campo `model` na criação da transcrição em lote, mas o que ele recebe é a **URI de um modelo**: um modelo base específico, um modelo de *custom speech* treinado pelo grupo, ou o **Whisper** da OpenAI hospedado no serviço; omitido o campo, usa-se o modelo base padrão do locale. São duas liberdades diferentes — o Google deixa escolher entre perfis prontos de áudio, a Azure deixa apontar para outro modelo, inclusive treinado. A AWS não expõe essa escolha na transcrição em lote padrão.

Uma ressalva documentada na Azure: identificação de idioma e modelo customizado **não se combinam** no lote — pedindo os dois, o serviço cai para os modelos base dos idiomas candidatos.

#### 3.4 Formas de acesso, autenticação e configuração

| Aspecto | Amazon Transcribe | Azure Speech | Cloud Speech-to-Text V2 |
|---|---|---|---|
| **Acesso** | API REST, AWS CLI e SDKs (.NET, C++, Go, Java V2, JavaScript, PHP V3, Python/boto3, Ruby V3, Rust) | Speech to text REST API e Speech CLI | REST, gRPC e client libraries |
| **Autenticação** | Credenciais IAM, com permissão de leitura no bucket de origem e de escrita no de destino | Chave do recurso; para Blob Storage protegido, **identidade gerenciada atribuída pelo sistema** com papel *Storage Blob Data Reader* | Application Default Credentials |
| **Fluxo** | Inicia o job, consulta com `GetTranscriptionJob`, lê o resultado no S3 | Três passos: localizar áudio → criar transcrição → obter resultados | Inicia a operação de longa duração e consulta até concluir |

A Azure tem a configuração de segurança mais elaborada das três para o caso de armazenamento privado — exige habilitar identidade gerenciada no recurso de Speech e conceder papel específico na conta de armazenamento. É mais trabalho inicial, mas permite bloquear completamente o acesso externo ao armazenamento, algo que a documentação descreve passo a passo.

#### 3.5 Latência de processamento e limites operacionais

| Aspecto | Amazon Transcribe | Azure Speech (lote) | Cloud Speech-to-Text V2 |
|---|---|---|---|
| **Agendamento** | Fila de jobs opcional quando não é necessário processar tudo simultaneamente | **Best-effort**: em horário de pico, pode levar **até 30 minutos para iniciar** e **até 24 horas para concluir** | Operação de longa duração |
| **Latência publicada** | — | **Percentil 90 abaixo de 6 horas**, com fórmula de latência normalizada publicada (`ProcessDuration − AudioLength/5`, com o serviço processando a cerca de 5× o tempo real) | — |
| **Recomendações de uso** | — | Enviar cerca de **1.000 arquivos por requisição**; distribuir envios ao longo de horas; consultar status **no máximo uma vez por minuto**, sendo suficiente a cada 10 minutos | — |
| **Limites de entrada publicados** | **Não localizados**: a página de cotas não estava acessível na consulta | **1 GB** por arquivo de áudio; **1.000 arquivos** por requisição de transcrição; **10.000 blobs** por contêiner; **240 min** por arquivo quando a diarização está ativada | Não localizados nas páginas consultadas para o `BatchRecognize` |
| **Cota de requisições** | Não localizada | **600 requisições/minuto**, compartilhadas com a *fast transcription*; ajustável no tier S0 e **indisponível no F0** | Cotas por projeto |
| **Retenção do resultado** | Bucket padrão: apagado quando o job expira, em 90 dias | `timeToLiveHours` obrigatório, de **6 horas a 31 dias** | Cloud Storage ou resposta da operação |

A Azure é a única das três que publica expectativa de latência e um método de cálculo para ela. Isso é transparência útil, mas também revela que o modo em lote da Azure **não é adequado a fluxos sensíveis a tempo**: a própria documentação admite picos de até 24 horas. Esse número descreve fila de processamento e não qualidade do reconhecimento.

#### 3.6 Situação do serviço (avisos oficiais)

Nenhum dos três serviços desta categoria apresenta aviso de descontinuação nas páginas consultadas. É a única das três categorias deste trabalho em que isso ocorre — nas outras duas, a oferta da Azure tem encerramento anunciado.

### 4. Exemplos de código

Os três exemplos submetem o **mesmo áudio** à **mesma operação em lote**, com idioma `pt-BR`:


**[`exemplos/fala/aws_transcribe.py`](https://github.com/DaviFPassos/Teste_comparativo_nuvem/blob/main/exemplos/fala/aws_transcribe.py)** — trecho essencial. O arquivo completo, no link, traz a autenticação por variável de ambiente, o tratamento de erro, os limites do serviço e a fonte da adaptação:

```python
cliente.start_transcription_job(
    TranscriptionJobName=nome_job,
    Media={"MediaFileUri": URI_AUDIO},
    MediaFormat="flac",
    LanguageCode=IDIOMA,
)
```


**[`exemplos/fala/azure_speech.py`](https://github.com/DaviFPassos/Teste_comparativo_nuvem/blob/main/exemplos/fala/azure_speech.py)** — trecho essencial. O arquivo completo, no link, traz a autenticação por variável de ambiente, o tratamento de erro, os limites do serviço e a fonte da adaptação:

```python
corpo = {
    "contentUrls": [URL_AUDIO],
    "locale": IDIOMA,
    "displayName": "transcricao-exemplo-etapa1",
    "properties": {"wordLevelTimestampsEnabled": True},
}
resposta = requests.post(BASE, headers=CABECALHOS, json=corpo, timeout=30)
```


**[`exemplos/fala/google_speech_to_text.py`](https://github.com/DaviFPassos/Teste_comparativo_nuvem/blob/main/exemplos/fala/google_speech_to_text.py)** — trecho essencial. O arquivo completo, no link, traz a autenticação por variável de ambiente, o tratamento de erro, os limites do serviço e a fonte da adaptação:

```python
requisicao = cloud_speech.BatchRecognizeRequest(
    recognizer=reconhecedor,
    config=config,
    files=[cloud_speech.BatchRecognizeFileMetadata(uri=URI_AUDIO)],
    recognition_output_config=cloud_speech.RecognitionOutputConfig(
        inline_response_config=cloud_speech.InlineOutputConfig(),
    ),
)

operacao = cliente.batch_recognize(request=requisicao)
```


**Estado de validação:** exemplos **ilustrativos, não executados pelo grupo**, adaptados da documentação oficial, conforme a seção 3 do enunciado. Por serem operações assíncronas, cada exemplo mostra os três momentos do fluxo: envio, acompanhamento e obtenção do resultado. Nenhuma credencial está embutida.

### 5. Modelo de cobrança

| Provedor | Unidade de cobrança | Preço | Equivalente por minuto |
|---|---|---|---|
| Amazon Transcribe | **Segundo de áudio**, em incrementos de 1 segundo e **sem mínimo** | $0,0001 por segundo, **preço único sem faixas** | $0,006 |
| Azure Speech (lote) | **Hora de áudio** | $0,18 por hora | $0,003 |
| Cloud Speech-to-Text V2 (padrão) | Áudio processado, em **incrementos de 1 segundo** | $0,016 por minuto (até 500 mil min/mês) | $0,016 |
| Cloud Speech-to-Text V2 (*dynamic batch*) | Áudio processado, em incrementos de 1 segundo | $0,003 por minuto, preço único | $0,003 |

Preços de **US East, em USD, consultados em 23/09/2026**, registrados em `custos/premissas.csv`. Os da AWS vêm da *AWS Price List API* e os da Azure da *Azure Retail Prices API*.

**A granularidade do arredondamento é favorável em todos os três**: AWS e Google cobram em incrementos de 1 segundo, e a AWS declara explicitamente não haver cobrança mínima. Ou seja, um áudio de 20 segundos não é cobrado como um minuto inteiro — o que era o risco desta categoria.

**O Google tem dois preços para lote, e a diferença é de mais de 5×.** O modo padrão custa $0,016/min; o *dynamic batch*, descrito na documentação como processamento "com menor nível de urgência", custa $0,003/min. Isso importa na comparação: o lote da Azure também é declaradamente *best-effort*, com fila que pode chegar a 24 horas. **O par realmente comparável em urgência é Azure em lote × Google em dynamic batch** — e os dois custam exatamente o mesmo, $0,003/min.

### 6. Cenário de custo, fórmulas, premissas e resultados

#### Carga do cenário

**10.000 minutos de áudio por mês** (cerca de 167 horas) em português do Brasil, transcritos em lote. A quantidade é hipotética e declarada como tal, e é idêntica nos três provedores.

**Condições de entrada assumidas**, porque os três cobram por tempo de áudio e não por arquivo:

| Premissa | Valor adotado | Por que importa |
|---|---|---|
| Canais | **1 (mono)** | Na AWS, até dois canais são cobrados pela **duração total do áudio**, sem dobrar o preço — a página de preços é explícita: "for a two-channel conversation, you only pay for the total audio duration". A diarização da Azure exige mono; na Azure, os canais processados são declarados em `properties.channels`, e o comportamento de cobrança por canal não foi verificado nas fontes consultadas. O cenário fixa um canal para manter a equivalência entre os três, não porque dois custassem mais na AWS |
| Idioma | **`pt-BR` declarado**, sem identificação automática de idioma | Identificação de idioma é recurso adicional nos três e, segundo a documentação da Azure, aumenta a latência do lote. A tabela da Azure ainda traz um medidor separado de *S1 Speech to Text Enhanced Feature Audio* ($0,30/h), fora do escopo deste cenário — quais recursos caem nele não foi verificado e não é afirmado aqui |
| Recursos adicionais | **Nenhum** — sem *redaction*, sem Call Analytics, sem vocabulário customizado além do padrão | Na **AWS**, diarização, vocabulário customizado, filtragem de vocabulário e identificação de idioma estão **incluídos no preço padrão** — a página de preços lista essas features como parte do que "this pricing includes". Nem todo recurso adicional é cobrado à parte nos três; isso não foi verificado para Azure e Google e não é afirmado aqui |
| Distribuição dos arquivos | Irrelevante para o custo, **desde que nenhum arquivo estoure os limites** (1 GB e, na Azure com diarização, 240 min) | Os três cobram por duração total, em incrementos de 1 s (AWS e Google) ou por hora (Azure); 10.000 minutos custam o mesmo em 100 arquivos de 100 min ou em 1.000 de 10 min |
| Custos **excluídos** | Armazenamento (S3, Blob Storage, Cloud Storage), transferência de dados, requisições de listagem e qualquer processamento posterior | O cenário compara **apenas** o preço da transcrição. A AWS obriga o áudio a estar no S3, o que acrescenta um custo de armazenamento que os outros dois podem dispensar (URI público na Azure) — esse custo não está nos $60,00 |

#### Fórmulas

```
AWS:     10.000 min x 60 = 600.000 segundos x $0,0001/s
Azure:   10.000 min / 60 = 166,667 horas x $0,18/h
Google:  10.000 min x $0,016/min  (padrão)
         10.000 min x $0,003/min  (dynamic batch)
```

#### Resultados (USD/mês, sem franquia)

| Provedor e modo | Unidades cobradas | Custo | Urgência declarada |
|---|---|---|---|
| Azure — Speech to text Batch (S1) | 166,67 horas | **$30,00** | *Best-effort*: até 24 h em pico |
| Google — dynamic batch | 10.000 minutos | **$30,00** | Menor urgência |
| AWS — Transcribe em lote | 600.000 segundos | $60,00 | Fila opcional |
| Google — BatchRecognize padrão | 10.000 minutos | $160,00 | Prioridade padrão |

![Custo de transcrição em lote de 10.000 minutos](../custos/graficos/custos_fala.png)

#### O que os números mostram

Esta é a categoria com a **maior dispersão de preço das três**: do mais barato ao mais caro há um fator de **5,3×**, contra 1,5× em visão computacional.

Mas o número isolado engana, e é por isso que a coluna de urgência está na tabela. **Comparar os $30,00 da Azure com os $160,00 do Google padrão é comparar serviços com compromissos de tempo diferentes.** Colocados na mesma condição — processamento de menor urgência — Azure e Google empatam exatamente em $30,00, e a AWS fica no dobro, $60,00, sem oferecer um modo mais barato de menor urgência.

A leitura correta é, portanto:

- **Se a aplicação tolera fila longa** (transcrição noturna de gravações, processamento de acervo): Azure e Google *dynamic batch* empatam em $30,00.
- **Se a aplicação não quer depender de uma janela declaradamente de baixa urgência**: AWS por $60,00 e Google padrão por $160,00.

**Uma ressalva importante sobre prazo.** Nenhum dos três publica prazo garantido de conclusão para o lote, e este trabalho não tem base para atribuir "previsibilidade" a nenhum deles. O que existe é assimetria de **informação** e de **oferta**: a Azure é a única que publica uma expectativa (p90 abaixo de 6 h, admitindo até 24 h em pico) e o Google é o único que separa a prioridade padrão do modo de menor urgência no próprio preço. A AWS não publica expectativa de prazo nem oferece modo mais barato — a fila de jobs é apenas uma opção de enfileiramento do cliente, e por si só não demonstra previsibilidade. Medir tempo real de conclusão é objeto da Etapa 2.

Este é o ponto do trabalho em que a análise econômica mais depende da análise técnica: sem a informação de fila da seção 3.5, o cenário produziria um ranking enganoso.

#### Franquias

| Provedor | Franquia | Natureza | Aplicável a este cenário? |
|---|---|---|---|
| AWS | 60 minutos/mês | Promocional, 12 meses | **Sim, só nos 12 primeiros meses** ($59,64 em vez de $60,00) |
| Azure | 5 horas/mês | Tier F0; a página de preços declara a franquia para transcrição **em tempo real** | **Não** — ver abaixo |
| Google | — | **Não localizada** para a tabela Recognition da V2 na página consultada | **Não** — nada é descontado sem valor verificado |

**Por que a franquia da Azure não entra neste cenário.** A tabela oficial de cotas do serviço registra, para *batch transcription*, **"Not available for F0"**: a transcrição em lote simplesmente não existe no tier gratuito onde estão as 5 horas. Além disso, o medidor efetivamente cobrado no cenário é o **`S1 Speech to Text Batch`**, do tier pago. Descontar as 5 horas do F0 de uma fatura S1 misturaria dois tiers distintos, e por isso o custo da Azure permanece em **$30,00** nas duas colunas de `custos/resultados.csv`.

**Regra adotada em todo o trabalho.** A coluna `custo_usd_com_franquia` de `custos/resultados.csv` desconta **somente** as franquias que incidem sobre a operação comparada; a coluna `franquia_aplicada` registra a decisão linha por linha e `custos/franquias.csv` guarda a justificativa de cada caso. Abater o tier F0 da Azure de uma fatura do tier pago somaria duas coisas que a Microsoft cobra separadamente: o F0 é um **recurso à parte**, com cota e limites próprios, e não um desconto no recurso pago. Usá-lo exigiria dividir a carga entre dois recursos — uma hipótese de arquitetura que teria de ser definida e justificada, e que este cenário não adota.

A franquia do Google **não foi localizada** para a V2 e por isso aparece como pendência, não como zero: a faixa de 60 minutos gratuitos que consta da página pertence às tabelas da API V1.

### 7. Síntese: vantagens, restrições e adequação por cenário

#### O que separa as três ofertas

**A urgência é a variável escondida desta categoria.** Os três chamam de "lote" coisas com compromissos de tempo diferentes: a Azure admite abertamente fila de até 24 horas em pico (com p90 abaixo de 6 h e uma fórmula publicada para estimar a latência), o Google separa o modo padrão do *dynamic batch* de menor urgência, e a AWS oferece fila apenas como opção. Qualquer comparação que ignore isso produz ranking errado.

**A origem do áudio impõe arquitetura.** A AWS **obriga** o arquivo a estar em um bucket S3. A Azure é a única que aceita **URI público**, dispensando armazenamento no provedor — e, no outro extremo, oferece o caminho mais elaborado de segurança, com identidade gerenciada e papel *Storage Blob Data Reader* para bloquear totalmente o acesso externo ao armazenamento.

**Google e Azure expõem a escolha do modelo; a AWS não.** No Google são perfis prontos por tipo de áudio (`chirp_3`, `long`, `short`, `telephony`, `telephony_short`, todos com `pt-BR`, e diarização no `chirp_3`). Na Azure, o campo `model` aponta para a URI de outro modelo — base, *custom speech* treinado pelo grupo ou Whisper —, o que é uma liberdade de natureza diferente: não escolher entre perfis, mas trocar o modelo. Na AWS a transcrição em lote padrão não oferece essa decisão.

**Os três documentam diarização.** A AWS a lista entre os recursos do lote, o Google a oferece no `chirp_3` e a Azure a configura por `diarizationEnabled` (dois locutores) ou `diarization` com `minCount`/`maxCount` (três ou mais, máximo abaixo de 36), com duas condições explícitas: canal mono e áudio de no máximo 240 minutos por arquivo.

**Os três suportam `pt-BR` formalmente** — diferente da categoria de NLP, onde só a Azure distingue a variante brasileira. E **nenhum dos três tem aviso de descontinuação**, o que faz desta a única categoria do trabalho sem risco de calendário.

#### Custo: maior dispersão das três categorias, mas só na aparência

Do mais barato ao mais caro há um fator de **5,3×** ($30,00 contra $160,00) — contra 1,5× em visão. Mas boa parte dessa distância desaparece quando se compara urgência equivalente:

- **Menor urgência:** Azure ($30,00) e Google *dynamic batch* ($30,00) empatam exatamente.
- **Prioridade padrão:** AWS ($60,00) contra Google padrão ($160,00).

A AWS ocupa uma posição intermediária peculiar: é o dobro do preço de menor urgência e **não oferece um modo mais barato** para quem tolera fila. Também não publica expectativa de prazo — nem a favor nem contra —, de modo que a comparação de tempo de conclusão entre os três fica em aberto nesta etapa.

Um alívio comum aos três: **o arredondamento é favorável**. AWS e Google cobram em incrementos de 1 segundo, e a AWS declara não haver cobrança mínima — o risco de um áudio de 20 segundos ser cobrado como um minuto inteiro não se concretizou em nenhum deles.

#### Adequação por cenário

| Situação | Alternativa mais adequada | Por quê |
|---|---|---|
| Processamento **noturno ou de acervo**, sem pressa | **Azure** ou **Google dynamic batch** | $30,00 no cenário; empate exato |
| Não depender de uma janela declarada de **baixa urgência** | **Amazon Transcribe** ($60,00) ou **Google padrão** ($160,00) | Nenhum dos dois pede que se aceite fila de baixa prioridade para chegar ao preço — mas nenhum dos três publica prazo garantido de conclusão |
| Áudio já hospedado **fora da nuvem do provedor** | **Azure** | Única que aceita URI público como origem |
| Requisito de **isolamento do armazenamento** | **Azure** | Caminho documentado com identidade gerenciada e acesso externo bloqueado |
| **Telefonia** ou tipos específicos de áudio | **Cloud Speech-to-Text V2** | Tem perfil de modelo pronto para telefonia (`telephony`); a Azure também permite apontar para outro modelo via `model`, mas exige treinar ou hospedar esse modelo primeiro — o Google entrega o perfil pronto |
| Necessidade de **diarização** | Os três | AWS no lote, Google no `chirp_3` e Azure por `diarizationEnabled`/`diarization` — nesta última, com canal mono e no máximo 240 min por arquivo |
| Fluxo **sensível a tempo** | Nenhum dos modos em lote | Usar transcrição em tempo real, que tem preço e condições próprios |

**O que esta etapa não responde:** qual serviço transcreve português do Brasil com menos erros. A taxa de erro exige execução e gabarito.


## 6. Síntese geral

As sínteses por categoria estão ao final de cada capítulo. Esta seção reúne o que atravessa as três.

### 6.1 Não há um vencedor, e o motivo é estrutural

Em nenhuma das três categorias um provedor domina em todos os critérios. Mais do que isso: **em duas das três, a ordem de preço depende de um parâmetro da própria aplicação**, e não do provedor.

| Categoria | O parâmetro que decide | Efeito |
|---|---|---|
| NLP | Comprimento típico do texto | AWS cobra 30% dos concorrentes em textos de 100 caracteres; empata na janela de 3.901–4.000 caracteres, mas volta a ser mais barata a partir de 4.001 — o empate vale numa janela de 100 caracteres antes de cada múltiplo de 1.000, não num ponto isolado |
| Visão | Volume mensal | AWS e Azure empatam em 100 mil imagens; os degraus de faixa diferem acima de 1 milhão |
| Fala | Tolerância a fila de processamento | Azure e Google empatam em $30,00 no modo de menor urgência; a AWS cobra $60,00 sem exigir essa tolerância |

Quem escolher um provedor a partir de uma tabela de preço isolada, sem fixar esses parâmetros, escolherá errado com frequência.

### 6.2 A unidade de cobrança pesa mais que o preço unitário

O achado mais transferível deste trabalho é que **a granularidade da unidade de cobrança pode importar mais do que o preço da unidade**.

Em análise de sentimento, Azure e Google cobram uma unidade inteira de 1.000 caracteres mesmo para um comentário de 100 caracteres — pagando-se por 900 caracteres nunca enviados. A AWS, cobrando em unidades de 100 caracteres, cobra 30% disso no mesmo cenário — uma redução de 70%. Os três têm preços unitários da mesma ordem de grandeza; o que separa é como contam.

Na transcrição de áudio, a mesma lógica trabalhou a favor de todos: os três cobram em incrementos de um segundo, e a AWS declara não haver cobrança mínima.

### 6.3 A Azure é a mais completa tecnicamente e a mais arriscada no calendário

A Azure aparece à frente em vários critérios técnicos: é a única com **94 idiomas** e distinção formal entre `pt-BR` e `pt-PT` em sentimento; a única com **contêiner Docker** para execução local; a única que aceita **URI público** como origem de áudio; a única que publica **expectativa de latência** do processamento em lote; e a que oferece o caminho mais elaborado de isolamento de armazenamento.

Em contrapartida, é a única dos três provedores com **encerramento anunciado em duas das três categorias comparadas**:

| Serviço | Encerramento anunciado |
|---|---|
| Azure Language — análise de sentimento e opinion mining | **31/03/2029** |
| Azure Vision — Image Analysis 4.0 | **25/09/2028** |

Além disso, quatro funcionalidades do Image Analysis 4.0 em preview já foram desativadas em 31/03/2025. Nenhum serviço comparado da AWS ou do Google Cloud apresenta aviso equivalente nas páginas consultadas.

Esse é um custo que não aparece em cenário de preço nenhum: para um sistema com horizonte de manutenção de anos, escolher a Azure nessas duas categorias significa assumir uma migração com data marcada.

### 6.4 O custo de troca é maior do que parece

Nenhuma das três categorias permite trocar de provedor apenas trocando o endpoint:

- **Sentimento:** a saída do Google é um número contínuo; a da AWS tem quatro classes, cada uma com score próprio; a da Azure tem quatro rótulos possíveis no documento mas só três scores, e `mixed` só aparece por composição das sentenças. Migrar exige redefinir a lógica de classificação, não só ler outro campo.
- **Visão:** as escalas de confiança diferem (0–100 × 0–1) e os vocabulários de rótulos não têm tabela de equivalência oficial. Migrar exige recalibrar limiares e remapear termos.
- **Fala:** a origem do áudio é imposta de forma diferente (S3 obrigatório na AWS; URI público aceito na Azure; Cloud Storage no Google), o que atinge a arquitetura, não só o código de chamada.

### 6.5 Franquia gratuita não é desconto — e a diferença muda o número

As três nuvens anunciam "camada gratuita", e as três querem dizer coisas diferentes:

| Provedor | O que é | Entra no cenário? |
|---|---|---|
| AWS | Free Tier promocional, na mesma conta e no mesmo tier da operação | Sim, mas **só nos 12 primeiros meses** |
| Microsoft Azure | Tier **F0**, um recurso separado do tier pago, com cota e limites próprios | **Não** — e na transcrição em lote o F0 **nem oferece a operação** |
| Google Cloud | Primeira **faixa da própria tabela**, cobrada a 0,00 USD | Sim, permanente |

A consequência prática aparece no número: descontar as 5 horas gratuitas do F0 da Azure de uma fatura de transcrição em lote produziria $29,10 em vez dos **$30,00** corretos — um desconto que a Microsoft não concede, porque a operação não existe naquele tier. Por isso `custos/franquias.csv` registra, para cada franquia, se ela é aplicável ao cenário e por quê, e `custos/resultados.csv` carrega essa decisão na coluna `franquia_aplicada`.

Pela mesma razão, a comparação principal usa os preços **sem franquia**: é a única base que significa a mesma coisa nos três. Onde a franquia é permanente — Google em NLP e visão —, a cobrança habitual é a coluna com franquia, e isso está dito nos capítulos.

### 6.6 O que a documentação não permite concluir

A análise é **documental**. Ela não estabelece qual serviço classifica sentimento com mais acerto, qual rotula imagens de forma mais útil, ou qual transcreve português do Brasil com menos erros. Essas perguntas exigem execução, dados de teste, gabarito e medição — objeto da Etapa 2.


## 7. Limitações

Registradas para delimitar o alcance das conclusões:

**1. Nenhum exemplo de código foi executado.** A seção 3 do enunciado permite isso nesta etapa. Consequentemente, não há neste relatório qualquer medição de latência, taxa de acerto, taxa de erro ou comportamento em produção.

**2. As conclusões valem para a data e a região declaradas.** Preços de nuvem mudam. Todos os valores são de **23/09/2026, em USD**, com a fonte de cada um registrada em `custos/premissas.csv`. Uma consulta futura pode divergir, e a reprodução dos cálculos exige reverificar as premissas.

**2a. As regiões não são idênticas nas três nuvens.** AWS em `us-east-1` e Azure em `East US`; no Google, Natural Language e Vision têm preço global, e a Cloud Speech-to-Text V2 foi consultada em **`us-central1` (Iowa)**, que é US Central. A comparação de custo de transcrição, portanto, não é entre três regiões equivalentes, e a diferença de preço entre regiões do Google não foi levantada.

**3. As cargas dos cenários são hipotéticas.** 100.000 documentos, 100.000 imagens e 10.000 minutos de áudio são quantidades escolhidas pelo grupo para permitir comparação, não estimativas de uso real de nenhuma aplicação. O que garante a validade da comparação não é a quantidade em si, mas o fato de ser **idêntica entre provedores**.

**4. Os resultados não se generalizam para outros volumes sem recálculo.** As faixas de preço têm degraus em pontos diferentes em cada provedor. A ordem observada em 100.000 imagens pode se inverter em 10 milhões.

**5. Comparou-se uma operação por categoria.** Sentimento de documento, detecção de rótulos e transcrição em lote. Cada serviço oferece dezenas de outras operações, com preços e limites próprios, que não foram analisadas.

**6. Informações não localizadas ficaram como pendência.** Especificamente:

| Pendência | Onde |
|---|---|
| Tamanho máximo de arquivo, duração máxima de áudio e número de jobs simultâneos do Amazon Transcribe | Página de cotas não acessível na consulta |
| Franquia gratuita da tabela Recognition da Cloud Speech-to-Text **V2** | Não localizada; a faixa de 60 minutos consta das tabelas da V1 |
| Valor padrão de `MinConfidence` do `DetectLabels` | Não localizado; o exemplo de código fixa o parâmetro explicitamente |
| Limite de tags por imagem no Azure Image Analysis | Não localizado nas páginas consultadas |
| Limites de tamanho e duração do `BatchRecognize` da Cloud Speech-to-Text V2 | Não localizados nas páginas consultadas (os equivalentes da Azure foram localizados na tabela oficial de cotas) |

Nenhuma dessas lacunas foi preenchida por estimativa.

**7. A distinção `pt-BR` da Azure não foi testada.** A documentação registra que a Azure distingue português do Brasil de português de Portugal, e que AWS e Google não. **Ela não afirma que isso produza melhor resultado em textos brasileiros**, e este relatório não o afirma. É uma hipótese verificável na Etapa 2.


## 8. Referências

Registro exigido pela seção 12 do enunciado (p. 5): "a pesquisa deverá utilizar prioritariamente a documentação oficial dos provedores, em especial a documentação das APIs/SDKs e as páginas oficiais de preços".

**Como ler este arquivo.** Cada fonte tem um identificador interno usado nos capítulos. O campo *afirmação sustentada* diz exatamente o que aquela página comprova — fontes não são listadas de forma decorativa. O campo *estado* usa: **verificado** (página acessada e conteúdo conferido na data indicada), **inacessível**, **informação não localizada** ou **precisa de confirmação**.

Todas as datas são datas reais de acesso. Todas as páginas são documentação oficial dos próprios provedores.

> No PDF do relatório esta seção aparece de forma compacta (identificador, provedor, título, URL, data e estado). O campo *afirmação sustentada* de cada fonte — que registra exatamente o que aquela página comprova — está neste arquivo.

### NLP / análise de texto

| ID | Provedor / serviço | Título e URL | Data de acesso | Afirmação sustentada | Estado |
|---|---|---|---|---|---|
| NLP-AWS-01 | AWS — Amazon Comprehend | Sentiment — https://docs.aws.amazon.com/comprehend/latest/dg/how-sentiment.html | 23/09/2026 | Operações `DetectSentiment`, `BatchDetectSentiment` e `StartSentimentDetectionJob`; classes `POSITIVE`, `NEGATIVE`, `MIXED` e `NEUTRAL`; resposta com `SentimentScore` contendo um score por classe; documentos em UTF-8 | verificado |
| NLP-AWS-02 | AWS — Amazon Comprehend | Guidelines and quotas — https://docs.aws.amazon.com/comprehend/latest/dg/guidelines-and-limits.html | 23/09/2026 | Tamanho máximo de 5 KB por documento nas operações de sentimento (síncrona e assíncrona); 5 KB e 25 documentos por requisição nas operações em lote; *throttling* dinâmico sem cota publicada no modo síncrono; 13 regiões suportadas, incluindo US East (N. Virginia) e **sem região no Brasil** | verificado |
| NLP-AWS-03 | AWS — Amazon Comprehend | Languages supported — https://docs.aws.amazon.com/comprehend/latest/dg/supported-languages.html | 23/09/2026 | 12 idiomas suportados, com `pt` (Português) entre eles e sem distinção de variante; o recurso *Sentiment* cobre todos os idiomas suportados (diferente de *Targeted sentiment*, restrito ao inglês) | verificado |
| NLP-AZ-01 | Azure — Azure Language in Foundry Tools | What is sentiment analysis and opinion mining in Azure Language service? — https://learn.microsoft.com/en-us/azure/ai-services/language-service/sentiment-opinion-mining/overview | 23/09/2026 | Nome atual do serviço; **aviso oficial de encerramento em 31/03/2029** com recomendação de migrar para o Microsoft Foundry; rótulos `positive`/`neutral`/`negative` com confiança de 0 a 1; sentimento em nível de documento e de sentença; acesso por REST API, client library (C#, Java, JavaScript, Python) e contêiner Docker; autenticação por chave + endpoint | verificado |
| NLP-AZ-04 | Azure — Azure Language in Foundry Tools | How to perform sentiment analysis and opinion mining — https://learn.microsoft.com/en-us/azure/ai-services/language-service/sentiment-opinion-mining/how-to/call-api | 26/09/2026 | **Regra oficial do rótulo de documento**: "The labels are *positive*, *negative*, and *neutral*. At the document level, the ***mixed*** sentiment label also can be returned", com a tabela que devolve `mixed` quando há ao menos uma sentença positiva **e** ao menos uma negativa; três scores de confiança (positivo, neutro, negativo) que somam 1 por documento e por sentença | verificado |
| NLP-AZ-02 | Azure — Azure Language in Foundry Tools | Data limits for Language service features — https://learn.microsoft.com/en-us/azure/ai-services/language-service/concepts/data-limits | 23/09/2026 | **"A text record is measured as 1000 characters"** (unidade de cobrança); 5.120 caracteres por documento no modo síncrono; 125.000 caracteres e 25 documentos no assíncrono; 1 MB por requisição; **10 documentos por requisição na análise de sentimento**; limites de taxa por tier (S/Multi-service 1.000 req/s; S0/F0 100 req/s e 300 req/min) | verificado |
| NLP-AZ-03 | Azure — Azure Language in Foundry Tools | Sentiment Analysis and Opinion Mining language support — https://learn.microsoft.com/en-us/azure/ai-services/language-service/sentiment-opinion-mining/language-support | 23/09/2026 | **94 códigos de idioma** na análise de sentimento, com **`pt-BR` (Português do Brasil) e `pt-PT` (Português de Portugal) como entradas distintas**; `pt` também aceito | verificado |
| NLP-GC-01 | Google Cloud — Cloud Natural Language API | Analyzing Sentiment — https://docs.cloud.google.com/natural-language/docs/analyzing-sentiment | 23/09/2026 | Operação `analyzeSentiment`; saída com `score` e `magnitude`; **ausência de aviso de descontinuação** na página oficial da operação | verificado |
| NLP-GC-02 | Google Cloud — Cloud Natural Language API | Cloud Natural Language API v1beta1 Deprecation Notice — https://cloud.google.com/natural-language/deprecation | 23/09/2026 | Única descontinuação oficial registrada é a da versão `v1beta1`, encerrada em 27/12/2019; não atinge a `v1` | verificado |
| NLP-GC-03 | Google Cloud — Cloud Natural Language API | Quotas and limits — https://docs.cloud.google.com/natural-language/quotas | 23/09/2026 | Conteúdo de até 1.000.000 bytes; até 100.000 tokens por requisição; 600 requisições/minuto e 800.000 requisições/dia | verificado |
| NLP-GC-04 | Google Cloud — Cloud Natural Language API | Language support — https://docs.cloud.google.com/natural-language/docs/languages | 23/09/2026 | 16 idiomas na análise de sentimento, incluindo `pt` (Português), sem distinção de variante | verificado |

### Visão computacional

| ID | Provedor / serviço | Título e URL | Data de acesso | Afirmação sustentada | Estado |
|---|---|---|---|---|---|
| VIS-AWS-01 | AWS — Amazon Rekognition | Detecting labels in an image — https://docs.aws.amazon.com/rekognition/latest/dg/labels-detect-labels-image.html | 23/09/2026 | Operação `DetectLabels`; entrada por objeto no Amazon S3 ou bytes da imagem; parâmetros `MaxLabels`, `MinConfidence`, `Features` (`GENERAL_LABELS`, `IMAGE_PROPERTIES`) e `Settings` com filtros de inclusão/exclusão; resposta com `Name`, `Confidence`, `Parents`, `Aliases`, `Categories`, `Instances` com `BoundingBox` e `LabelModelVersion` | verificado |
| VIS-AWS-02 | AWS — Amazon Rekognition | Guidelines and quotas — https://docs.aws.amazon.com/rekognition/latest/dg/limits.html | 23/09/2026 | Imagem de até **15 MB** como objeto no S3 e **5 MB** como bytes na requisição; **apenas PNG e JPEG**; máximo de 10.000 px de largura e altura para `DetectLabels`; mínimo de 80 px; orientação de tratar `ProvisionedThroughputExceededException` e `ThrottlingException` com *retry*, *backoff* exponencial e *jitter*; Image Bulk Analysis com lotes de até 10.000 imagens | verificado |
| VIS-AZ-01 | Azure — Azure Vision in Foundry Tools | What is Image Analysis? — https://learn.microsoft.com/en-us/azure/ai-services/computer-vision/overview-image-analysis | 23/09/2026 | **Aviso oficial: Image Analysis 4.0 descontinuado, encerramento em 25/09/2028**; funcionalidades de preview retiradas em 31/03/2025 (Custom Image Classification, Custom Object Detection, Product Recognition, Segment/remoção de fundo); funcionalidade *Tag visual features* nas versões 4.0 e 3.2; entrada v4.0 (JPEG, PNG, GIF, BMP, WEBP, ICO, TIFF, MPO; < 20 MB; 50×50 a 16.000×16.000 px) e v3.2 (JPEG, PNG, GIF, BMP; < 4 MB); East US entre as regiões suportadas | verificado |
| VIS-GC-01 | Google Cloud — Cloud Vision API | Detect labels — https://docs.cloud.google.com/vision/docs/labels | 23/09/2026 | Feature `LABEL_DETECTION` via `POST https://vision.googleapis.com/v1/images:annotate`; entrada por base64, URI do Cloud Storage ou URL remota; resposta com `mid`, `description`, `score` (0 a 1) e `topicality`; `maxResults` padrão de 10 | verificado |
| VIS-GC-03 | Google Cloud — Cloud Vision API | Detect text and labels in files (PDF/TIFF) — https://docs.cloud.google.com/vision/docs/file-small-batch | 26/09/2026 | Arquivos **PDF e TIFF** são processados pelo endpoint **`files:annotate`**, e não por `images:annotate`; `LABEL_DETECTION` está entre as features aceitas nesse endpoint, ao lado de `DOCUMENT_TEXT_DETECTION`, `TEXT_DETECTION`, `FACE_DETECTION` e outras; chaves de API não são aceitas em `files:annotate` | verificado |
| VIS-GC-02 | Google Cloud — Cloud Vision API | Supported images — https://docs.cloud.google.com/vision/docs/supported-files | 23/09/2026 | Formatos JPEG, PNG8, PNG24, GIF, GIF animado (primeiro quadro), BMP, WEBP, RAW, ICO, PDF e TIFF; até **20 MB por imagem** e **10 MB por requisição JSON**; resolução recomendada de 640×480 px para `LABEL_DETECTION` | verificado |

### Fala para texto

| ID | Provedor / serviço | Título e URL | Data de acesso | Afirmação sustentada | Estado |
|---|---|---|---|---|---|
| FAL-AWS-01 | AWS — Amazon Transcribe | How Amazon Transcribe works — https://docs.aws.amazon.com/transcribe/latest/dg/how-it-works.html | 23/09/2026 | Separação entre lote (`StartTranscriptionJob`, arquivos no Amazon S3) e streaming (`StartStreamTranscription`); suporte a recursos e idiomas difere entre os dois modos | verificado |
| FAL-AWS-02 | AWS — Amazon Transcribe | Data input and output — https://docs.aws.amazon.com/transcribe/latest/dg/how-input.html | 23/09/2026 | Formatos em lote (AMR, FLAC, M4A, MP3, MP4, Ogg, WebM, WAV) e em streaming (FLAC, Ogg Opus, PCM); recomendados FLAC e WAV PCM 16 bits; suporte a um ou dois canais apenas; taxas de 8.000 Hz a 48.000 Hz; saída JSON com `transcripts`, `items` (tempo e confiança por palavra) e `audio_segments`; no bucket padrão, **URI temporária válida por 15 minutos** e resultado **apagado quando o job expira, em 90 dias** | verificado |
| FAL-AWS-03 | AWS — Amazon Transcribe | Supported languages — https://docs.aws.amazon.com/transcribe/latest/dg/supported-languages.html | 23/09/2026 | **`pt-BR` (Portuguese, Brazilian)** e `pt-PT` suportados em lote e streaming; `pt-BR` com transcrição de números, acrônimos, *redaction* e Call Analytics pós-chamada e em tempo real; SDKs disponíveis por modo | verificado |
| FAL-AZ-01 | Azure — Azure Speech in Foundry Tools | Batch transcription overview — https://learn.microsoft.com/en-us/azure/ai-services/speech-service/batch-transcription | 23/09/2026 | Transcrição em lote pela Speech to text REST API com `Transcription_Create`; fluxo assíncrono em três passos; agendamento *best-effort*, podendo levar **até 30 min para iniciar e até 24 h para concluir** em horário de pico; **latência de percentil 90 inferior a 6 h**, com fórmula `ProcessDuration − AudioLength/5`; recomendação de ~1.000 arquivos por requisição e polling no máximo 1×/minuto | verificado |
| FAL-AZ-02 | Azure — Azure Speech in Foundry Tools | Locate audio files for batch transcription — https://learn.microsoft.com/en-us/azure/ai-services/speech-service/batch-transcription-audio-data | 23/09/2026 | Formatos e codecs aceitos (WAV, MP3, OPUS/OGG, FLAC, WMA, AAC, ALAW e MULAW em WAV, AMR, WebM, SPEEX); origens: URI público, URI com SAS ou contêiner do Blob Storage via identidade gerenciada com papel *Storage Blob Data Reader*; campos `contentUrls` e `contentContainerUrl` | verificado |
| FAL-AZ-03 | Azure — Azure Speech in Foundry Tools | Language and voice support — https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support | 23/09/2026 | Locale **`pt-BR` (Portuguese, Brazil)** suportado em speech to text | verificado |
| FAL-AWS-04 | AWS — Amazon Transcribe | Amazon Transcribe pricing — https://aws.amazon.com/transcribe/pricing/ | 26/09/2026 | **"This pricing includes features such as custom vocabularies, vocabulary filtering, speaker diarization, and language identification"** — esses recursos não têm cobrança separada no preço padrão; e **"for a two-channel conversation, you only pay for the total audio duration and won't be charged separately for each channel"** — até dois canais são cobrados pela duração total, sem dobrar | verificado |
| FAL-AZ-04 | Azure — Azure Speech in Foundry Tools | Quotas and limits for Azure Speech — https://learn.microsoft.com/en-us/azure/ai-services/speech-service/speech-services-quotas-and-limits | 26/09/2026 | Tabela de *Batch transcription*: **"Shared maximum requests per minute — Not available for F0 / 600"** (ou seja, **a transcrição em lote não existe no tier gratuito F0**, onde estão as 5 horas mensais); **1 GB** por arquivo de áudio; **10.000 blobs** por contêiner; **1.000 arquivos** por requisição; **240 minutos** por arquivo com diarização; cota de requisições compartilhada com a *fast transcription* e ajustável apenas no tier S0 | verificado |
| FAL-AZ-05 | Azure — Azure Speech in Foundry Tools | Create a batch transcription — https://learn.microsoft.com/en-us/azure/ai-services/speech-service/batch-transcription-create | 26/09/2026 | Campo **`model`** no nível raiz do corpo, aceitando modelo base específico, modelo de *custom speech* ou **Whisper**; **`diarization`** (com `minCount`/`maxCount`, máximo abaixo de 36, só canal mono, áudio ≤ 240 min) e **`diarizationEnabled`** (dois locutores) dentro de `properties`; `languageIdentification` com 2 a 10 locales candidatos; `timeToLiveHours` obrigatório, de 6 horas a 31 dias; identificação de idioma **não** se combina com modelo customizado no lote | verificado |
| FAL-GC-01 | Google Cloud — Cloud Speech-to-Text V2 | Transcription models — https://docs.cloud.google.com/speech-to-text/v2/docs/transcription-model | 23/09/2026 | Reconhecimento síncrono (áudio < 60 s), em lote (`BatchRecognize`, arquivos no Cloud Storage) e streaming; modelos `chirp_3`, `chirp_2` e `telephony` | verificado |
| FAL-GC-03 | Google Cloud — Cloud Speech-to-Text V2 | `BatchRecognizeFileResult` (referência da client library Python) — https://docs.cloud.google.com/python/docs/reference/speech/latest/google.cloud.speech_v2.types.BatchRecognizeFileResult | 26/09/2026 | O campo `transcript` do resultado por arquivo está **descontinuado** ("Deprecated. Use `inline_result.transcript` instead"); com `InlineOutputConfig` a transcrição vem em `inline_result.transcript` e com `GcsOutputConfig` em `cloud_storage_result` | verificado |
| FAL-GC-02 | Google Cloud — Cloud Speech-to-Text V2 | Supported languages — https://docs.cloud.google.com/speech-to-text/v2/docs/speech-to-text-supported-languages | 23/09/2026 | **`pt-BR` (Portuguese, Brazil)** suportado nos modelos `chirp_3`, `long`, `short`, `telephony` e `telephony_short`; diarização disponível no `chirp_3` | verificado |

### Enunciado do trabalho

| ID | Documento | Data de acesso | Afirmação sustentada | Estado |
|---|---|---|---|---|
| ENU-01 | `pdfs/Computação em Nuvem - Trabalho I_ Comparação de Serviços de Inteligência Artificial em Nuvem.pdf` (5 páginas) | 23/09/2026 | Todas as exigências citadas em `etapa1/diagnostico.md`, com seção e página | verificado |

### Preços

Região **US East**, moeda **USD**, consulta em **23/09/2026**. Todos os valores estão em `custos/premissas.csv`, com a URL da fonte em cada linha.

**Por que APIs de preço e não as páginas comerciais:** as páginas de preço da Azure e do Google servem suas tabelas por JavaScript — o conteúdo estático exibe apenas `$-`. Em vez de recorrer a fonte secundária, os valores foram lidos das APIs públicas de preço mantidas pelos próprios provedores, que são a fonte oficial dos mesmos números.

| ID | Provedor / serviço | Título e URL | Data de acesso | Afirmação sustentada | Estado |
|---|---|---|---|---|---|
| PRE-AWS-01 | AWS — Amazon Comprehend | AWS Price List API — https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/comprehend/current/index.json | 23/09/2026 | `USE1-DetectSentiment`: $0,0001 por unidade até 10M; $0,00005 de 10M a 50M; $0,000025 acima de 50M. `publicationDate` 2026-09-11 | verificado |
| PRE-AWS-02 | AWS — Amazon Comprehend | Pricing — https://aws.amazon.com/comprehend/pricing/ | 23/09/2026 | Unidade de 100 caracteres com **mínimo de 3 unidades (300 caracteres) por requisição**; franquia de 50.000 unidades/mês por API durante 12 meses | verificado |
| PRE-AWS-03 | AWS — Amazon Rekognition | AWS Price List API — https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonRekognition/current/index.json | 23/09/2026 | `USE1-Group2-AsyncImagesProcessed`: $0,0010/imagem até 1M; $0,0008 de 1M a 5M; $0,0006 de 5M a 35M; $0,00025 acima. `publicationDate` 2026-09-11 | verificado |
| PRE-AWS-04 | AWS — Amazon Rekognition | Pricing — https://aws.amazon.com/rekognition/pricing/ | 23/09/2026 | `DetectLabels` pertence às APIs do **Grupo 2**; franquia de 1.000 imagens/mês por 12 meses | verificado |
| PRE-AWS-05 | AWS — Amazon Transcribe | AWS Price List API — https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/transcribe/current/index.json | 23/09/2026 | `USE1-TranscribeAudio`: **$0,0001 por segundo, preço único sem faixas** (equivale a $0,006/min). `publicationDate` 2026-09-11 | verificado |
| PRE-AWS-06 | AWS — Amazon Transcribe | Pricing — https://aws.amazon.com/transcribe/pricing/ | 23/09/2026 | Cobrança em incrementos de 1 segundo, **sem mínimo**; franquia de 60 min/mês por 12 meses | verificado |
| PRE-AZ-01 | Azure — Azure Language | Azure Retail Prices API — https://prices.azure.com/api/retail/prices (serviceName `Foundry Tools`, região `eastus`) | 23/09/2026 | `Standard Text Records`: $1,00 por 1.000 registros até 0,5M; $0,75 de 0,5M a 2,5M; $0,30 de 2,5M a 10M; $0,25 acima | verificado |
| PRE-AZ-02 | Azure — Azure Vision | Azure Retail Prices API — https://prices.azure.com/api/retail/prices | 23/09/2026 | `Image Analysis Group 1 Transactions`: $1,00 por 1.000 até 1M; $0,65 de 1M a 10M; $0,60 de 10M a 100M; $0,40 acima | verificado |
| PRE-AZ-03 | Azure — Azure Vision | Pricing — https://azure.microsoft.com/en-us/pricing/details/computer-vision/ | 23/09/2026 | A feature **`Tag` pertence ao Grupo 1** (o Grupo 2 reúne Describe, Read, Caption e Dense Captions); franquia F0 de 5.000 transações/mês, 20/minuto | verificado |
| PRE-AZ-04 | Azure — Azure Speech | Azure Retail Prices API — https://prices.azure.com/api/retail/prices | 23/09/2026 | `S1 Speech to Text Batch`: **$0,18 por hora** (equivale a $0,003/min); `S1 Speech To Text` em tempo real: $1,00/hora | verificado |
| PRE-AZ-05 | Azure — Azure Speech | Pricing — https://azure.microsoft.com/en-us/pricing/details/speech/ | 23/09/2026 | Franquia F0 de 5 horas de áudio por mês em transcrição em tempo real | verificado |
| PRE-GC-01 | Google Cloud — Cloud Natural Language | Pricing — https://cloud.google.com/natural-language/pricing | 23/09/2026 | Sentiment Analysis: 0 a 5.000 unidades gratuitas; $1,00 por 1.000 de 5 mil a 1M; $0,50 de 1M a 5M; $0,25 acima. Unidade de 1.000 caracteres Unicode, **arredondada para cima**, conforme o exemplo oficial (800 + 1.500 + 600 caracteres = 4 unidades) | verificado |
| PRE-GC-02 | Google Cloud — Cloud Vision | Pricing — https://cloud.google.com/vision/pricing | 23/09/2026 | Label Detection: primeiras 1.000 unidades/mês gratuitas; $1,50 por 1.000 de 1.001 a 5M; $1,00 acima de 5M. **Cada feature aplicada a uma imagem conta como uma unidade** | verificado |
| PRE-GC-03 | Google Cloud — Cloud Speech-to-Text V2 | Pricing — https://cloud.google.com/speech-to-text/pricing | 23/09/2026 | Recognition Standard: $0,016/min até 500 mil; $0,010 de 500 mil a 1M; $0,008 de 1M a 2M; $0,004 acima. **Dynamic Batch Recognition: $0,003/min**, descrito como processamento de menor urgência. Cobrança em incrementos de 1 segundo | verificado |

### Fontes não oficiais consultadas e descartadas

Registradas por transparência: foram lidas durante a pesquisa, mas **não sustentam nenhuma afirmação** do trabalho.

| Fonte | Motivo do descarte |
|---|---|
| Tópico "Analyze sentiment deprecation?" no fórum Google Developer (discuss.google.dev) | Um respondente afirma que a Cloud Natural Language API estaria "depreciada" em favor do Vertex AI. A afirmação **não se confirma** na documentação oficial: a página de `analyzeSentiment` não traz aviso de descontinuação (NLP-GC-01) e a única descontinuação oficial é a do `v1beta1` (NLP-GC-02). Fórum não é fonte oficial e a afirmação foi descartada. |



---

*Relatório montado automaticamente a partir dos arquivos do repositório em 26/09/2026 por `relatorio/montar_relatorio.py`. Para regerar: `uv run relatorio/montar_relatorio.py --html`.*
