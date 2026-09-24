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

- **A unidade de cobrança pesa mais que o preço unitário.** Em análise de sentimento, a AWS custa **um terço** dos concorrentes para textos de 100 caracteres — porque cobra em unidades de 100 caracteres enquanto Azure e Google cobram uma unidade inteira de 1.000. A diferença desaparece em textos de 4.000 caracteres.
- **"Lote" significa coisas diferentes em cada provedor.** Na transcrição de áudio, Azure e Google *dynamic batch* empatam em $30,00 no modo de menor urgência, mas o lote da Azure admite fila de até 24 h. A AWS cobra $60,00 sem exigir essa tolerância.
- **Dois serviços da Azure têm encerramento anunciado:** análise de sentimento em **31/03/2029** e Image Analysis 4.0 em **25/09/2028**. Nenhum concorrente comparado tem aviso equivalente.
- **Só a Azure distingue `pt-BR` de `pt-PT`** em análise de sentimento; na transcrição de áudio, os três distinguem.

## Organização do repositório

| Caminho | Conteúdo |
|---|---|
| [relatorio/relatorio_etapa1.md](relatorio/relatorio_etapa1.md) | **Relatório consolidado da Etapa 1** |
| [etapa1/diagnostico.md](etapa1/diagnostico.md) | Exigências do enunciado × material existente × pendências |
| [etapa1/categorias.md](etapa1/categorias.md) | Seleção das categorias, critérios e operação comparada |
| [etapa1/nlp.md](etapa1/nlp.md) · [etapa1/visao.md](etapa1/visao.md) · [etapa1/fala.md](etapa1/fala.md) | Capítulos por categoria |
| [exemplos/](exemplos/) | 9 exemplos de código (3 categorias × 3 provedores) |
| [custos/](custos/) | Premissas, script de cálculo, resultados e gráficos |
| [referencias/fontes.md](referencias/fontes.md) | Todas as fontes, com URL, data de consulta e o que cada uma sustenta |
| [STATUS.md](STATUS.md) | Progresso, decisões e pendências |
| [etapas/](etapas/) | Roteiros de trabalho das duas etapas |
| [pdfs/](pdfs/) | Enunciado do professor |

O andamento detalhado está nos [Milestones](../../milestones) e [Issues](../../issues) do repositório.

## Exemplos de código

Os nove exemplos estão em [exemplos/](exemplos/), organizados por categoria e provedor. Dentro de cada categoria os três executam **a mesma operação sobre a mesma entrada**, para tornar as diferenças de API visíveis.

> **Estado de validação:** os exemplos são **ilustrativos e não foram executados pelo grupo**. Foram adaptados da documentação oficial de cada provedor, conforme a seção 3 do enunciado permite explicitamente nesta etapa. Cada arquivo declara sua fonte, data de consulta e estado. **Nenhuma credencial está no código** — todos leem variáveis de ambiente.

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

# confere as contas feitas à mão contra o que o programa calculou (18 verificações)
uv run custos/verificar_calculos.py

# regera os gráficos a partir do CSV de resultados
uv run custos/gerar_graficos.py

# remonta o relatório a partir dos capítulos e gera o HTML
uv run relatorio/montar_relatorio.py --html
```

Nenhum desses comandos chama API de nuvem nem gera custo.

**Sobre travamento de versões:** `calcular_custos.py`, `verificar_calculos.py` e `montar_relatorio.py` usam **apenas a biblioteca padrão** do Python — não há o que travar, e os números do relatório são reproduzíveis sem instalar nada. O único script com dependência externa que de fato executa é `gerar_graficos.py`, e ele tem lockfile (`custos/gerar_graficos.py.lock`), para que os gráficos sejam regerados a partir da mesma resolução de pacotes.

Os 9 exemplos **não têm lockfile por decisão**: eles são ilustrativos e não são executados nesta etapa, então travar versões de código que ninguém roda registraria uma precisão inexistente. Suas dependências ficam declaradas nos blocos PEP 723. Na Etapa 2, onde o código será efetivamente executado, as versões passam a ser registradas conforme o roteiro exige.

**Parâmetros dos cenários** — quantidades hipotéticas, idênticas entre provedores:

| Categoria | Carga | Região | Moeda | Preços consultados em |
|---|---|---|---|---|
| NLP | 100.000 documentos de 100, 500, 1.200 e 4.000 caracteres | US East | USD | 23/09/2026 |
| Visão | 100.000 imagens, 1 feature por imagem | US East | USD | 23/09/2026 |
| Fala | 10.000 minutos de áudio em pt-BR, em lote | US East | USD | 23/09/2026 |

Preços de nuvem mudam. Para uma data diferente, reverifique `custos/premissas.csv` antes de reutilizar os resultados.

## Gerar o PDF do relatório

```bash
uv run relatorio/montar_relatorio.py --html
```

Depois abra `relatorio/relatorio_etapa1.html` no navegador e use **Ctrl+P → Salvar como PDF**. Os gráficos estão embutidos no HTML, e o arquivo tem CSS de impressão para evitar quebras de página dentro de tabelas e figuras.

## Etapa 2

Planejada em [etapas/ROTEIRO_ETAPA2.md](etapas/ROTEIRO_ETAPA2.md): avaliação prática de análise de sentimento em português, com execução real em pelo menos dois provedores. Os artefatos serão adicionados a este mesmo repositório.
