# Comparação de Serviços de Inteligência Artificial em Nuvem

Trabalho da disciplina de Computação em Nuvem — Mestrado em Ciência da Computação, UNIFOR.

## Integrantes

- Davi Fonseca Passos
- Rafael Fonseca Pessoa
- Lucca Melo Nunes

## Objetivo

Comparar serviços de inteligência artificial oferecidos por **AWS, Microsoft Azure e Google Cloud**, sob a perspectiva de quem deseja integrá-los a uma aplicação. O trabalho é dividido em duas etapas:

- **Etapa 1 — Análise comparativa:** seleção de categorias, análise técnica, exemplos ilustrativos de código, análise econômica e síntese entre os três provedores.
- **Etapa 2 — Avaliação prática:** execução real de testes de análise de sentimento em português em pelo menos dois dos provedores estudados na Etapa 1.

## Entrega da Etapa 1

**→ [Relatório completo da Etapa 1](relatorio/relatorio_etapa1.md)** · [versão HTML para exportar em PDF](relatorio/relatorio_etapa1.html)

### Categorias analisadas

Três categorias, escolhidas por tratarem modalidades de entrada diferentes (texto, imagem e áudio) e por terem oferta equivalente nos três provedores:

| Categoria | AWS | Microsoft Azure | Google Cloud | Capítulo |
|---|---|---|---|---|
| NLP / análise de texto | Amazon Comprehend | Azure Language in Foundry Tools | Cloud Natural Language API | [nlp.md](etapa1/nlp.md) |
| Visão computacional | Amazon Rekognition | Azure Vision in Foundry Tools | Cloud Vision API | [visao.md](etapa1/visao.md) |
| Fala para texto | Amazon Transcribe | Azure Speech in Foundry Tools | Cloud Speech-to-Text V2 | [fala.md](etapa1/fala.md) |

### Principais achados

- **A unidade de cobrança pesa mais que o preço unitário.** Em análise de sentimento, a AWS cobra **30% do que cobram os concorrentes** para textos de 100 caracteres ($30,00 contra $100,00) — porque cobra em unidades de 100 caracteres enquanto Azure e Google cobram uma unidade inteira de 1.000. Os três empatam em 4.000 caracteres, mas **o empate é pontual**: em 4.100 a AWS volta a $410,00 contra $500,00 dos outros dois, porque só ela não arredonda para o milhar.
- **"Lote" significa coisas diferentes em cada provedor.** Na transcrição de áudio, Azure e Google *dynamic batch* empatam em $30,00 no modo de menor urgência, mas o lote da Azure admite fila de até 24 h. A AWS cobra $60,00 sem exigir essa tolerância.
- **Dois serviços da Azure têm encerramento anunciado:** análise de sentimento em **31/03/2029** e Image Analysis 4.0 em **25/09/2028**. Nenhum concorrente comparado tem aviso equivalente.
- **Só a Azure distingue `pt-BR` de `pt-PT`** em análise de sentimento; na transcrição de áudio, os três distinguem.
- **Texto ambíguo tem tratamento em dois dos três.** A AWS devolve `MIXED` como classe do modelo, com score próprio; a Azure devolve `mixed` no nível do documento, composto quando há sentenças positivas e negativas; o Google não rotula — devolve um número e deixa o limiar para a aplicação.
- **Franquia gratuita não é desconto automático.** O tier F0 da Azure é um recurso separado do tier pago e, na transcrição em lote, sequer oferece a operação. Os cenários só descontam franquias que incidem sobre a operação comparada, e cada decisão está justificada em [custos/franquias.csv](custos/franquias.csv).

## Organização do repositório

| Caminho | Conteúdo |
|---|---|
| [relatorio/relatorio_etapa1.md](relatorio/relatorio_etapa1.md) | **Relatório consolidado da Etapa 1** |
| [etapa1/diagnostico.md](etapa1/diagnostico.md) | **Documento histórico:** retrato do ponto de partida (23/09/2026), antes de o conteúdo existir. Não descreve o estado atual |
| [etapa1/categorias.md](etapa1/categorias.md) | Seleção das categorias, critérios e operação comparada |
| [etapa1/nlp.md](etapa1/nlp.md) · [etapa1/visao.md](etapa1/visao.md) · [etapa1/fala.md](etapa1/fala.md) | Capítulos por categoria |
| [exemplos/](exemplos/) | 9 exemplos de código (3 categorias × 3 provedores) |
| [testes/](testes/) | Testes dos 9 exemplos com frase, foto e áudio reais — offline (`uv run testes/rodar_testes.py`) ou contra os serviços reais (`--real`) |
| [custos/](custos/) | Premissas, script de cálculo, resultados e gráficos |
| [referencias/fontes.md](referencias/fontes.md) | Todas as fontes, com URL, data de consulta e o que cada uma sustenta |
| [DEPENDENCIAS.md](DEPENDENCIAS.md) | Bibliotecas e versões, e como instalá-las com `uv` |
| [STATUS.md](STATUS.md) | Progresso, decisões e pendências |
| [etapa2/](etapa2/) | **Etapa 2** — metodologia, dados, programa de coleta e análise ([estado](etapa2/STATUS_ETAPA2.md)) |
| [etapas/](etapas/) | Roteiros de trabalho das duas etapas |
| [pdfs/](pdfs/) | Enunciado do professor |

O andamento detalhado está nos [Milestones](../../milestones) e [Issues](../../issues) do repositório.

## Exemplos de código

Os nove exemplos estão em [exemplos/](exemplos/), organizados por categoria e provedor. Dentro de cada categoria os três executam **a mesma operação sobre a mesma entrada**, para tornar as diferenças de API visíveis.

### Testar os exemplos

Os testes usam **dados reais com resposta conhecida**, em [testes/dados/](testes/dados/):

| Entrada | Conteúdo | Resultado esperado ([gabarito](testes/dados/gabarito.json)) |
|---|---|---|
| `frase.txt` | "O atendimento foi excelente." | Sentimento **positivo** |
| `cachorro.jpg` | Foto de um labrador (domínio público, Wikimedia Commons) | Rótulo **dog** |
| `frase.flac` | A mesma frase falada em pt-BR (2,5 s) | Transcrição com **atendimento** e **excelente** |

Origem, licença e SHA-256 de cada arquivo estão em [testes/dados/LEIAME.md](testes/dados/LEIAME.md). O áudio foi conferido por um reconhecedor de fala local (Whisper), sem nuvem, que transcreveu exatamente a frase.

**Modo offline — sem credenciais, sem rede, sem custo:**

```bash
uv run testes/rodar_testes.py
```

Resultado esperado: `45 passed`. Confere os arquivos contra os limites documentados de cada provedor (formato, tamanho, dimensões, canais, taxa de amostragem) e executa os 9 exemplos de ponta a ponta com as bibliotecas oficiais, trocando só a chamada de rede por uma resposta simulada. Na AWS, o `botocore.Stubber` confere cada parâmetro contra o modelo oficial do serviço; na Azure e no Google, o cliente simulado tem as mesmas assinaturas do real e as respostas usam os tipos do próprio SDK.

Inclui também um **ensaio geral do modo real**: as próprias funções do modo real são executadas com a rede de cada SDK simulada, conferindo que a frase, a foto e o áudio reais são o que é enviado, que a resposta é lida corretamente e que a evidência é gravada sem identificadores da conta. Todos os testes offline passam com a rede cortada pelo sistema operacional.

**Modo real — os mesmos arquivos vão aos serviços de verdade:**

```bash
uv run testes/rodar_testes.py --real
```

Qualquer pessoa reproduz com **as próprias contas** — passo a passo em [testes/COMO_RODAR_COM_SUAS_CREDENCIAIS.md](testes/COMO_RODAR_COM_SUAS_CREDENCIAIS.md). Mostra o plano do que será chamado e só segue com a confirmação `sim`. Cada resposta é conferida contra o gabarito e gravada em `testes/evidencias/` — **inclusive quando não bate** —, com o SHA-256 da entrada usada. Provedor sem credencial aparece como `SKIPPED`, com o motivo.

| Cuidado | Como é garantido |
|---|---|
| Credenciais não vão para o repositório nem para os colegas | Lidas do `.env` local (ignorado pelo git) e das configurações de `aws configure` / `gcloud auth application-default login`, fora do projeto. Modelo em [testes/modelo_de_credenciais.txt](testes/modelo_de_credenciais.txt). O modo real **aborta** se achar uma chave em arquivo que o git publicaria |
| Evidências não identificam a conta | Tokens de URLs assinadas, nomes de bucket, ID de projeto, número da conta AWS e nome de recurso Azure são removidos antes de gravar |
| Não gerar cobrança | A proteção vem do tipo de conta: plano gratuito da AWS, Azure for Students e teste gratuito do Google não cobram sem upgrade manual. **Comprehend e Transcribe ficam desligados**, porque não existem no plano gratuito da AWS |

**Os testes detectam erro de verdade.** Foram injetados 10 defeitos nos exemplos (parâmetro com nome errado, método inexistente, campo descontinuado...) e 8 nos dados (imagem corrompida, PNG disfarçado de JPEG, áudio mudo, áudio a 8 kHz, 3 canais...). Todos os 18 foram detectados.

**O que o modo offline não prova:** como a resposta é simulada, ele não diz o que o serviço real responde. Isso é o que o modo real verifica — e a avaliação de qualidade em escala é objeto da Etapa 2. **Nenhuma credencial está no código**: todos os exemplos leem variáveis de ambiente.

### Origem dos testes: o que é de cada empresa e o que foi extraído

**As bibliotecas são as oficiais dos três provedores.** Conferido nos metadados dos pacotes instalados no ambiente dos testes:

| Biblioteca | Versão | Publicada por | Repositório oficial |
|---|---|---|---|
| `boto3` / `botocore` | 1.43.101 / 1.43.110 | Amazon Web Services | github.com/boto/boto3 · github.com/boto/botocore |
| `azure-ai-textanalytics` | 5.4.0 | Microsoft Corporation | github.com/Azure/azure-sdk-for-python |
| `azure-ai-vision-imageanalysis` | 1.0.0 | Microsoft Corporation | github.com/Azure/azure-sdk-for-python |
| `azure-core` | 1.41.0 | Microsoft Corporation | github.com/Azure/azure-sdk-for-python |
| `google-cloud-language` | 2.21.0 | Google LLC | github.com/googleapis/google-cloud-python |
| `google-cloud-vision` | 3.15.0 | Google LLC | github.com/googleapis/google-cloud-python |
| `google-cloud-speech` | 2.40.0 | Google LLC | github.com/googleapis/google-cloud-python |

O exemplo de fala da Azure não usa SDK: chama a API REST oficial com `requests`, como mostra a documentação da Microsoft.

**Os exemplos apontam para os endereços oficiais de cada serviço.** Resolvido pelo próprio SDK, sem rede:

| Provedor | Serviço | Endereço |
|---|---|---|
| AWS | Comprehend · Rekognition · Transcribe | `comprehend.us-east-1.amazonaws.com` · `rekognition.us-east-1.amazonaws.com` · `transcribe.us-east-1.amazonaws.com` |
| Microsoft | Language · Vision | `<recurso>.cognitiveservices.azure.com` (endpoint do recurso criado no portal) |
| Microsoft | Speech (lote) | `eastus.api.cognitive.microsoft.com/speechtotext/v3.2/transcriptions` |
| Google | Natural Language · Vision · Speech-to-Text V2 | `language.googleapis.com` · `vision.googleapis.com` · `speech.googleapis.com` |

**O que foi extraído de APIs dos provedores, e o que não foi:**

| Informação | De onde veio | Chamou serviço de IA? |
|---|---|---|
| Preços da AWS | **AWS Price List API** (`pricing.us-east-1.amazonaws.com/offers/v1.0/aws/...`), pública e sem autenticação, publicação de 11/09/2026 | Não |
| Preços da Azure | **Azure Retail Prices API** (`prices.azure.com/api/retail/prices`, serviço `Foundry Tools`, região `eastus`), pública e sem autenticação | Não |
| Preços do Google | Tabelas da página oficial de preços (`cloud.google.com/.../pricing`). O Google não tem API pública de preços sem autenticação | Não |
| Regras de validação da AWS nos testes | Modelos oficiais de API embutidos no `botocore` (`botocore/data/<serviço>/<versão>/service-2.json`): Comprehend 2017-11-27, Rekognition 2016-06-27, Transcribe 2017-10-26 | Não |
| Regras de validação da Azure e do Google | Classes e tipos de dados dos próprios SDKs oficiais | Não |
| Formato das respostas simuladas | Documentação oficial de cada serviço (ver `referencias/fontes.md`), validado pelos SDKs acima | Não |
| Limites técnicos (tamanho, formato, idiomas) | Páginas de documentação oficial, citadas por ID em `referencias/fontes.md` | Não |

**Nenhuma resposta de serviço de IA foi obtida até agora.** Sem credenciais, nenhum dos nove serviços foi chamado. As respostas usadas no modo offline são simuladas no formato documentado. O modo `--real` é o que obtém respostas de verdade e as grava em `testes/evidencias/`.

**Fontes que não são dos provedores**, usadas só para produzir os dados de teste: a foto veio do Wikimedia Commons (domínio público); o áudio foi sintetizado localmente com o Piper (voz `pt_BR-faber-medium`, conjunto de dados CC0, baixada do Hugging Face); a conferência do áudio foi feita localmente com o Whisper (`faster-whisper`). Nenhuma dessas etapas envolve os serviços comparados.

### O quanto os testes atendem ao enunciado

| Exigência do enunciado | Situação | Por quê |
|---|---|---|
| **Seção 3** — "breves exemplos de código", operações equivalentes, fonte indicada; "não precisam ter sido [...] executados" | **Atendida e superada** | Os 9 exemplos existem, com fonte, e além disso são testados |
| **Pedido do professor** — testar os exemplos | **Parcial até rodar `--real`** | Offline, o código executa de ponta a ponta com frase, foto e áudio reais e é validado pelos SDKs oficiais. Mas só o modo real mostra o que os serviços respondem, e ele ainda não foi executado |
| **Seção 12** — documentação oficial como fonte prioritária | **Atendida** | Bibliotecas oficiais; preços de APIs oficiais; limites com fonte |
| **Seção 7** — mesmos dados em pelo menos dois provedores | **Atendida no desenho** | O modo real envia a mesma frase, a mesma foto e o mesmo áudio a todos os provedores habilitados |
| **Seção 8** — código "efetivamente executado" | **Pendente** | Depende de rodar `--real` com credenciais |
| **Seção 8** — dados "de tamanho e diversidade suficientes para [...] análise minimamente representativa" | **Não atendida — e não é o objetivo** | Uma entrada por categoria verifica se o exemplo funciona, mas não mede qualidade. O conjunto representativo é trabalho da Etapa 2 |
| **Seção 9** — métricas e critério de qualidade definidos antes | **Parcial** | Há um critério objetivo por entrada (`gabarito.json`), mas não há métricas como acurácia, latência ou taxa de sucesso |
| **Seção 10** — tabelas, gráficos e confronto com a Etapa 1 | **Não atendida** | Também é escopo da Etapa 2 |

Em resumo: os testes **validam os exemplos da Etapa 1** e já deixam pronta a infraestrutura que a Etapa 2 vai usar (dados com gabarito, chamada real, evidência). Eles **não são** a avaliação prática da Etapa 2 e não devem ser apresentados como tal.

**Defeitos que só a verificação na documentação e o ensaio revelaram — todos corrigidos antes da primeira execução real:**

- O exemplo do Google pedia o modelo `long` em `us-central1`, combinação que **não existe** para `pt-BR` (lá só há `chirp`, `chirp_2` e `chirp_telephony`), e usava o endereço global com um reconhecedor regional, o que a API recusa. Passou a usar `chirp_2` e o endereço `us-central1-speech.googleapis.com`. Um teste confere a combinação contra a tabela oficial.
- O Google indexa o resultado do lote pela URI do arquivo no bucket; a limpeza da evidência só tratava valores, não chaves, e o nome do bucket vazaria. Corrigido, com teste.
- O teste real de fala da Azure deixava o `requests.get` substituído ao terminar. Corrigido.

**Sobre a versão da API de fala da Azure:** o exemplo de fala da Azure usa a versão **v3.2** da API REST. Segundo a [referência oficial](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/rest-speech-to-text) (atualizada em 05/06/2026), a v3.2 estável **continua em vigor**: foram aposentadas em 31/03/2026 apenas a v3.0 e as prévias `3.2-preview.1` e `3.2-preview.2`. A versão estável mais recente, porém, é a `2025-10-15`, que usa outro caminho (`/speechtotext/transcriptions:submit?api-version=...`). O teste offline não detecta esse tipo de defasagem, porque confere o código contra o formato que o próprio grupo documentou; só a chamada real ou a leitura da documentação revelam.

Cada exemplo declara suas dependências em um bloco [PEP 723](https://peps.python.org/pep-0723/) no topo do arquivo, então o [uv](https://docs.astral.sh/uv/) resolve tudo sozinho:

```bash
uv run exemplos/nlp/aws_comprehend.py
```

Não é preciso criar ambiente virtual nem instalar nada manualmente. Executar de fato exige credenciais válidas do provedor e **gera custo**.

## Como reproduzir a análise de custos

Os números do relatório não são digitados: saem de `custos/premissas.csv`, onde cada preço tem URL da fonte, região, moeda e data de consulta.

```bash
# recalcula os custos e regrava custos/resultados.csv (só biblioteca padrão)
uv run custos/calcular_custos.py

# confere as contas feitas à mão contra o que o programa calculou (31 verificações)
uv run custos/verificar_calculos.py

# regera os gráficos a partir do CSV de resultados
uv run custos/gerar_graficos.py

# remonta o relatório a partir dos capítulos e gera o HTML
uv run relatorio/montar_relatorio.py --html
```

Nenhum desses comandos chama API de nuvem nem gera custo.

**Sobre travamento de versões:** `calcular_custos.py`, `verificar_calculos.py` e `montar_relatorio.py` usam **apenas a biblioteca padrão** do Python — não há o que travar, e os números do relatório são reproduzíveis sem instalar nada. O único script com dependência externa que de fato executa é `gerar_graficos.py`, e ele tem lockfile (`custos/gerar_graficos.py.lock`), para que os gráficos sejam regerados a partir da mesma resolução de pacotes.

Os testes dos exemplos também têm lockfile (`testes/rodar_testes.py.lock`), e as versões das bibliotecas dos provedores estão fixadas no próprio script — é com essas versões que os exemplos foram validados.

**Parâmetros dos cenários** — quantidades hipotéticas, idênticas entre provedores:

| Categoria | Carga | Região dos preços | Moeda | Preços consultados em |
|---|---|---|---|---|
| NLP | 100.000 documentos de 100, 500, 1.200, 4.000 e 4.100 caracteres | AWS `us-east-1` · Azure `East US` · Google global | USD | 23/09/2026 |
| Visão | 100.000 imagens, 1 feature por imagem | AWS `us-east-1` · Azure `East US` · Google global | USD | 23/09/2026 |
| Fala | 10.000 minutos de áudio em pt-BR, em lote, mono, sem recursos adicionais | AWS `us-east-1` · Azure `East US` · Google **`us-central1`** | USD | 23/09/2026 |

A região do Google em fala (`us-central1`, Iowa) **não** é US East: a tabela da Cloud Speech-to-Text V2 é regional, e essa diferença está declarada como limitação em vez de tratada como equivalência.

Preços de nuvem mudam. Para uma data diferente, reverifique `custos/premissas.csv` antes de reutilizar os resultados.

## Gerar o PDF do relatório

**→ [pdfs/relatorio_tecnico_etapa1.pdf](pdfs/relatorio_tecnico_etapa1.pdf)** — 45 páginas, A4, texto pesquisável. Slides da apresentação: [Etapa 1](pdfs/apresentacao_etapa1.pdf) · [Etapa 2](pdfs/apresentacao_etapa2.pdf).

O PDF é feito para ser lido **fora do repositório**: traz, por categoria, os serviços comparados, entradas e saídas, formas de acesso e autenticação, limites e cotas, avisos oficiais de encerramento, o trecho essencial de cada exemplo de código, o cenário de custo com gráfico e a síntese. Todos os links apontam para as URLs públicas deste repositório no GitHub — o gerador recusa montar o relatório se algum link só funcionar localmente.

O que fica apenas nos capítulos [etapa1/nlp.md](etapa1/nlp.md), [etapa1/visao.md](etapa1/visao.md) e [etapa1/fala.md](etapa1/fala.md) é o aparato de rastreabilidade: a tabela que liga cada afirmação à sua fonte oficial e as pendências de verificação.

Para regerar:

```bash
uv run relatorio/gerar_pdf.py
```

O script remonta o HTML a partir dos capítulos (para o PDF nunca sair defasado) e converte usando o Chromium do Playwright — o mesmo motor de um navegador, então o CSS de impressão é respeitado exatamente como em Ctrl+P. O Chromium é baixado no cache do usuário na primeira execução, sem `sudo`.

Em WSL e imagens enxutas de Ubuntu, o Chromium pode não iniciar por falta da `libasound` (biblioteca de áudio, que ele exige para subir mas não usa para gerar PDF). Nesse caso:

```bash
uv run relatorio/gerar_pdf.py --resolver-libs
```

Isso baixa e extrai a biblioteca em `~/.local/lib/chromium-deps`, sem `sudo` e sem alterar o sistema.

Alternativa sem instalar nada: abrir `relatorio/relatorio_etapa1.html` no navegador e usar **Ctrl+P → Salvar como PDF**.

## Etapa 2 — avaliação prática

Análise de sentimento em português com execução real na **Microsoft Azure** e no **Google Cloud**, sobre os mesmos textos: avaliações de produtos do corpus público [B2W-Reviews01](https://github.com/americanas-tech/b2w-reviews01) (CC BY-NC-SA 4.0), com gabarito de dois anotadores (kappa 0,791).

> **Coleta concluída em 19/10/2026:** 115 textos de teste nos dois provedores, 100% de sucesso, US$ 0. Acurácia de 74,8% (Azure) e 78,3% (Google), **sem diferença estatisticamente significativa** (McNemar p = 0,541). Resultados e conclusões em [relatorio/relatorio_etapa2.md](relatorio/relatorio_etapa2.md) ([PDF](pdfs/relatorio_tecnico_etapa2.pdf)).

| Caminho | Conteúdo |
|---|---|
| [etapa2/metodologia.md](etapa2/metodologia.md) | Protocolo: decisões, normalização, métricas e denominadores (**aprovado em 19/10/2026**) |
| [etapa2/dados/](etapa2/dados/) | Origem, licença e limitações dos dados; guia de anotação; candidatos e planilhas |
| [etapa2/src/](etapa2/src/) | Amostragem, anotação, adaptadores, executor, normalização, trava de orçamento e análise |
| [etapa2/COMO_EXECUTAR.md](etapa2/COMO_EXECUTAR.md) | Credenciais, piloto, teste em dois laptops, análise conjunta, retomada e o que vai ou não para o repositório |
| [etapa2/expectativas_etapa1.md](etapa2/expectativas_etapa1.md) | O que a Etapa 1 levou a esperar — registrado **antes** da coleta, para o confronto exigido pela seção 10 |
| [relatorio/relatorio_etapa2.md](relatorio/relatorio_etapa2.md) · [PDF](pdfs/relatorio_tecnico_etapa2.pdf) | **Relatório da Etapa 2**: resultados, confronto com a Etapa 1 e conclusões |
| [etapa2/resultados/](etapa2/resultados/) · [etapa2/graficos/](etapa2/graficos/) | Dados coletados (respostas sanitizadas, tentativas, ambiente), métricas, análise conjunta e gráficos |
| [etapa2/painel/](etapa2/painel/) | Painel de apresentação: Google e Azure ao vivo e execuções gravadas |

```bash
uv run etapa2/rodar_testes.py                          # 93 testes offline: sem rede, credencial ou custo
uv run etapa2/src/analisar.py --execucao <id>          # recalcula métricas de uma coleta, sem chamar API
uv run etapa2/src/analisar.py --execucao <id1> <id2>   # junta coletas de máquinas diferentes (Google + Azure)
uv run etapa2/src/executar.py --dados etapa2/dados/piloto.csv --provedores azure google   # coleta real
uv run etapa2/painel/servidor.py                       # painel no navegador: Google e Azure ao vivo + execuções gravadas
```
