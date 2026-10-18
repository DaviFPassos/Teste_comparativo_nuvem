# Dependências do projeto

Versões resolvidas pelo `uv` em **24/09/2026** (Etapa 1) e **18/10/2026** (Etapa 2), com Python 3.12. **Uma versão só de cada biblioteca no projeto inteiro**: a Etapa 2 usa as mesmas da Etapa 1.

## Em uma linha

Não é preciso instalar nada manualmente. Cada script declara as próprias dependências em um bloco [PEP 723](https://peps.python.org/pep-0723/) no topo do arquivo, e o `uv` resolve e instala em ambiente isolado na hora de executar:

```bash
uv run <caminho-do-script>
```

Se você ainda não tem o `uv`:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh     # Linux, macOS e WSL
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"   # Windows
```

## O que cada script precisa

### Scripts que produzem a entrega

| Script | Dependência | Versão | Observação |
|---|---|---|---|
| `custos/calcular_custos.py` | — | — | **Só biblioteca padrão.** Os números do relatório são reproduzíveis sem instalar nada |
| `custos/verificar_calculos.py` | — | — | **Só biblioteca padrão** |
| `relatorio/montar_relatorio.py` | — | — | **Só biblioteca padrão** |
| `custos/gerar_graficos.py` | `matplotlib` | **3.11.2** | Tem lockfile (`gerar_graficos.py.lock`), então a resolução é reproduzível |
| `relatorio/gerar_pdf.py` | `playwright` | **1.63.0** | Baixa o Chromium no cache do usuário na primeira execução |
| `testes/rodar_testes.py` | `pytest` + as 8 bibliotecas dos exemplos | **9.1.1** + versões da tabela abaixo | Testa os 9 exemplos sem credenciais nem rede. Versões fixadas no script e lockfile (`rodar_testes.py.lock`) |

### Etapa 2 — avaliação prática

| Script | Dependência | Versão | Observação |
|---|---|---|---|
| `etapa2/src/amostrar.py` | — | — | **Só biblioteca padrão.** Sorteio reprodutível do dataset |
| `etapa2/src/anotacao.py` | — | — | **Só biblioteca padrão.** Planilhas, concordância (kappa) e montagem dos conjuntos |
| `etapa2/src/executar.py` | `azure-ai-textanalytics`<br>`azure-core`<br>`google-cloud-language` | **5.4.0**<br>**1.41.0**<br>**2.21.0** | A coleta. Lockfile `executar.py.lock`. Também usa, só com biblioteca padrão, `normalizar.py`, `custo.py`, `seguranca.py` e `provedores/` |
| `etapa2/src/analisar.py` | `matplotlib` | **3.11.2** | Métricas, tabelas e gráficos a partir dos arquivos da coleta; não chama API. Lockfile `analisar.py.lock`. Exige Python ≥ 3.11 (exigência do matplotlib 3.11) |
| `etapa2/rodar_testes.py` | `pytest` + as bibliotecas de `executar.py` e `analisar.py` | **9.1.1** + versões acima | 66 testes offline, com os SDKs reais e a rede substituída. Lockfile `rodar_testes.py.lock` |

O roteiro da Etapa 2 sugere um `etapa2/requirements.txt`. O projeto mantém a convenção da Etapa 1 — dependências declaradas no próprio script (PEP 723) e travadas no `.lock` ao lado —, que cumpre o mesmo papel: as versões efetivamente usadas ficam registradas e são reproduzidas pelo `uv run`.

### Exemplos de código (testados com `uv run testes/rodar_testes.py`)

| Categoria | Script | Dependência | Versão |
|---|---|---|---|
| NLP | `exemplos/nlp/aws_comprehend.py` | `boto3` | **1.43.101** |
| NLP | `exemplos/nlp/azure_language.py` | `azure-ai-textanalytics`<br>`azure-core` | **5.4.0**<br>**1.41.0** |
| NLP | `exemplos/nlp/google_natural_language.py` | `google-cloud-language` | **2.21.0** |
| Visão | `exemplos/visao/aws_rekognition.py` | `boto3` | **1.43.101** |
| Visão | `exemplos/visao/azure_image_analysis.py` | `azure-ai-vision-imageanalysis`<br>`azure-core` | **1.0.0**<br>**1.41.0** |
| Visão | `exemplos/visao/google_vision.py` | `google-cloud-vision` | **3.15.0** |
| Fala | `exemplos/fala/aws_transcribe.py` | `boto3` | **1.43.101** |
| Fala | `exemplos/fala/azure_speech.py` | `requests` | **2.34.2** |
| Fala | `exemplos/fala/google_speech_to_text.py` | `google-cloud-speech` | **2.40.0** |

Estas são as versões **com que os exemplos foram testados** — os testes as fixam em `testes/rodar_testes.py`. Os testes não chamam os serviços; executar os exemplos contra a nuvem de verdade exige credenciais do provedor e **gera custo**.

## Resumo dos pacotes

Somando as dependências diretas, são **10 pacotes** — 8 dos exemplos (exercitados pelos testes), 2 dos scripts de gráfico e PDF (`matplotlib` e `playwright`) — mais o `pytest`, usado só pelos testes. A Etapa 2 **não acrescenta pacote novo**: usa `azure-ai-textanalytics`, `azure-core`, `google-cloud-language` e `matplotlib`, nas mesmas versões:

```
azure-ai-textanalytics==5.4.0
azure-ai-vision-imageanalysis==1.0.0
azure-core==1.41.0
boto3==1.43.101
google-cloud-language==2.21.0
google-cloud-speech==2.40.0
google-cloud-vision==3.15.0
matplotlib==3.11.2
playwright==1.63.0
requests==2.34.2
```

As dependências transitivas variam de 4 a 20 por script e são resolvidas pelo `uv` — não precisam ser instaladas à mão.

## Se preferir instalar manualmente

O `uv run` dispensa isso, mas caso queira um ambiente próprio:

```bash
uv venv
source .venv/bin/activate        # Linux, macOS e WSL
.venv\Scripts\activate           # Windows

uv pip install boto3==1.43.101 \
  azure-ai-textanalytics==5.4.0 azure-core==1.41.0 \
  azure-ai-vision-imageanalysis==1.0.0 \
  google-cloud-language==2.21.0 google-cloud-vision==3.15.0 \
  google-cloud-speech==2.40.0 requests==2.34.2 \
  matplotlib==3.11.2 playwright==1.63.0
```

O `.venv/` está no `.gitignore` e não vai para o repositório.

## Lockfiles

Têm lockfile os scripts com dependência externa que **de fato executam** e cujo resultado precisa ser reproduzível:

- `custos/gerar_graficos.py.lock` — os três gráficos versionados são regerados a partir da mesma resolução de pacotes;
- `testes/rodar_testes.py.lock` — os testes dos exemplos rodam sempre contra as mesmas versões das bibliotecas dos provedores;
- `etapa2/src/executar.py.lock` — a coleta da Etapa 2 chama os serviços sempre com as mesmas versões dos SDKs;
- `etapa2/src/analisar.py.lock` — as métricas e os gráficos da Etapa 2 são regerados com a mesma resolução;
- `etapa2/rodar_testes.py.lock` — os testes da Etapa 2 rodam contra as mesmas versões da coleta.

Os exemplos em si não têm lockfile próprio: quem os valida são os testes, e é no lockfile dos testes que as versões ficam travadas.

## Requisito de sistema para gerar o PDF

`relatorio/gerar_pdf.py` usa o Chromium do Playwright, baixado no cache do usuário (~150 MB) sem `sudo`.

Em WSL e imagens enxutas de Ubuntu, o Chromium não inicia por falta da `libasound` — biblioteca de áudio que ele exige para subir, mas não usa para gerar PDF. Nesse caso:

```bash
uv run relatorio/gerar_pdf.py --resolver-libs
```

Isso baixa e extrai a biblioteca em `~/.local/lib/chromium-deps`, sem `sudo` e sem alterar o sistema.
