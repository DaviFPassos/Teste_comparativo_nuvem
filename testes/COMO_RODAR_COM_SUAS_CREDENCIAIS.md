# Como rodar os testes contra os serviços reais com as suas credenciais

Este guia é para quem quer reproduzir os testes na própria máquina, com as próprias contas. Nada depende das credenciais do grupo: cada pessoa usa as suas, que ficam só no computador dela.

Cada provedor é independente. Configure só os que quiser: os demais aparecem como `SKIPPED`, com o motivo.

## 1. Preparar a máquina (uma vez)

Instale o [uv](https://docs.astral.sh/uv/):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh                 # Linux, macOS, WSL
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"      # Windows
```

Clone o repositório e confira que tudo funciona **offline**, sem credenciais e sem custo:

```bash
git clone https://github.com/DaviFPassos/Teste_comparativo_nuvem.git
cd Teste_comparativo_nuvem
uv run testes/rodar_testes.py
```

Resultado esperado: `45 passed`. Na primeira vez o `uv` baixa Python e bibliotecas (cerca de 30 s).

Crie o arquivo de credenciais a partir do modelo — ele é ignorado pelo git:

```bash
cp testes/modelo_de_credenciais.txt .env                        # Linux, macOS, WSL
copy testes\modelo_de_credenciais.txt .env                      # Windows
```

## 2. Configurar cada provedor

### Microsoft Azure — NLP, visão e fala

No [portal Azure](https://portal.azure.com), crie três recursos **na região East US**:

| Recurso | Tier | Variáveis no `.env` |
|---|---|---|
| Language (Azure Language in Foundry Tools) | **F0** (gratuito) | `AZURE_LANGUAGE_ENDPOINT`, `AZURE_LANGUAGE_KEY` |
| Computer Vision (Azure Vision in Foundry Tools) | **F0** (gratuito) | `AZURE_VISION_ENDPOINT`, `AZURE_VISION_KEY` |
| Speech (Azure Speech in Foundry Tools) | **S0** — o F0 não faz transcrição em lote | `AZURE_SPEECH_KEY` e `AZURE_SPEECH_REGION=eastus` |

Endpoint e chave ficam em *Recurso → Chaves e Ponto de Extremidade*. A Azure permite um único recurso F0 de cada tipo por assinatura; se já houver um, use o tier S (cobrança por uso, frações de centavo nestes testes).

O áudio é lido pela Azure direto da URL pública do arquivo no GitHub (`testes/dados/frase.flac` no branch `main`) — não é preciso subir nada.

### Google Cloud — NLP, visão e fala

Com a [CLI `gcloud`](https://cloud.google.com/sdk/docs/install) instalada, rode uma vez (troque `MEU_PROJETO` e `MEU_BUCKET`):

```bash
gcloud auth application-default login
gcloud auth application-default set-quota-project MEU_PROJETO
gcloud services enable language.googleapis.com vision.googleapis.com \
       speech.googleapis.com storage.googleapis.com --project=MEU_PROJETO
gcloud storage buckets create gs://MEU_BUCKET --location=us-central1 --project=MEU_PROJETO
```

No `.env`: `GOOGLE_CLOUD_PROJECT=MEU_PROJETO` e `TESTE_GCS_BUCKET=MEU_BUCKET`.

- **Não use arquivo de chave JSON.** O `application-default login` guarda a credencial fora do projeto (`~/.config/gcloud` ou `%APPDATA%\gcloud`).
- O `set-quota-project` é necessário: com credencial de usuário, as APIs de Vision e Natural Language recusam chamadas sem projeto de cota.
- O bucket precisa estar **no mesmo projeto**: é assim que o serviço de fala já tem permissão para ler o áudio. O teste envia o áudio ao bucket e o apaga ao terminar.

### AWS — visão (e, opcionalmente, NLP e fala)

Com a [CLI `aws`](https://aws.amazon.com/cli/) instalada, rode uma vez:

```bash
aws configure          # região: us-east-1
```

Use um usuário IAM com a política `AmazonRekognitionFullAccess`. A credencial fica em `~/.aws`, fora do projeto.

**Comprehend e Transcribe ficam desligados por padrão**: eles não existem no plano gratuito da AWS. Em uma conta no plano pago, para ligá-los, acrescente ao `.env`:

```
PERMITIR_AWS_PLANO_PAGO=sim
TESTE_S3_BUCKET=um-bucket-seu-em-us-east-1
```

e dê ao usuário também `ComprehendReadOnly`, `AmazonTranscribeFullAccess` e acesso de leitura e escrita ao bucket. O teste envia o áudio ao bucket e o apaga ao terminar.

## 3. Rodar

```bash
uv run testes/rodar_testes.py --real
```

O script mostra o que vai chamar e só segue se você digitar `sim`. Ele **aborta** se encontrar alguma chave em arquivo que o git publicaria.

| Categoria | Tempo típico |
|---|---|
| NLP e visão | segundos |
| Fala — Google | 1 a 2 minutos |
| Fala — Azure | alguns minutos; a fila de lote da Azure é *best-effort* e pode demorar mais em horário de pico |

## 4. Conferir o resultado

Cada teste confere a resposta do serviço contra [`testes/dados/gabarito.json`](dados/gabarito.json) e grava em `testes/evidencias/<categoria>_<provedor>.json`:

- a resposta bruta do serviço;
- o que se esperava, o que veio, e `aprovado: true/false`;
- o SHA-256 da entrada enviada, que deve bater com o de [`testes/dados/LEIAME.md`](dados/LEIAME.md).

A evidência é gravada **mesmo quando o resultado não bate**. Antes de gravar, são removidos tokens de URLs assinadas, nomes de bucket, ID de projeto, número de conta AWS e nome de recurso Azure.

## Custo

Uma execução completa consome, no total, menos de **um centavo de dólar** em contas pagas — e nada, nas franquias gratuitas e nos créditos promocionais:

| Serviço | Consumo | Franquia |
|---|---|---|
| AWS Rekognition | 1 imagem | 1.000 imagens/mês (12 meses) |
| Azure Language e Vision (F0) | 1 chamada cada | 5.000/mês |
| Azure Speech (S0) | 2,5 s de áudio | — (US$ 0,0001) |
| Google Natural Language | 1 unidade | 5.000/mês |
| Google Vision | 1 unidade | 1.000/mês |
| Google Speech-to-Text V2 | 3 s de áudio | — (US$ 0,0008) |

Nenhum recurso cobra por hora parada: todos são pagos por uso.

## Ao terminar

Revogue o que criou para o teste: apague a chave de acesso do usuário IAM, rode `gcloud auth application-default revoke`, regenere ou exclua as chaves dos recursos Azure e apague os buckets de teste.
