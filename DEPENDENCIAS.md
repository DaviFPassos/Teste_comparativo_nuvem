# Dependências do projeto

Versões resolvidas pelo `uv` em **24/09/2026**, com Python 3.12.

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

### Exemplos de código (ilustrativos, não executados)

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

Executar esses exemplos de verdade exige credenciais do provedor e **gera custo**. Nesta etapa eles são ilustrativos: nenhum foi executado pelo grupo, conforme a seção 3 do enunciado permite.

## Resumo dos pacotes

Somando as dependências diretas, são **8 pacotes**:

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

## Por que só um lockfile

Apenas `custos/gerar_graficos.py` tem lockfile. Ele é o único script com dependência externa **que de fato executa** e produz um artefato versionado (os três gráficos) — travar a resolução garante que regerar os gráficos dê o mesmo resultado.

Os nove exemplos não têm lockfile porque não são executados nesta etapa: travar versões de código que ninguém roda registraria uma precisão que não existe. As versões acima ficam aqui como registro do que o `uv` resolveria hoje.

Na Etapa 2 isso muda: lá o código é executado de verdade, e o roteiro exige registrar as versões efetivamente usadas.

## Requisito de sistema para gerar o PDF

`relatorio/gerar_pdf.py` usa o Chromium do Playwright, baixado no cache do usuário (~150 MB) sem `sudo`.

Em WSL e imagens enxutas de Ubuntu, o Chromium não inicia por falta da `libasound` — biblioteca de áudio que ele exige para subir, mas não usa para gerar PDF. Nesse caso:

```bash
uv run relatorio/gerar_pdf.py --resolver-libs
```

Isso baixa e extrai a biblioteca em `~/.local/lib/chromium-deps`, sem `sudo` e sem alterar o sistema.
