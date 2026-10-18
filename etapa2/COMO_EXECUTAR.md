# Como executar a Etapa 2

Há dois tipos de comando, e eles não se misturam:

| Tipo | Precisa de credencial? | Gera custo? | Chama API? |
|---|---|---|---|
| Testes offline, anotação, análise de execuções já coletadas | Não | Não | **Não** |
| Coleta real (`executar.py` sem `--simulado`) | Sim | **Não, dentro da franquia** — e a trava recusa o que passar dela | **Sim** |

## 0. Conferir que tudo funciona sem nada configurado

```bash
uv run etapa2/rodar_testes.py
```

Resultado esperado: `66 passed`. Sem rede, sem credencial, sem custo. Inclui os dois SDKs oficiais rodando com a rede substituída.

## Demonstração ao vivo (ex.: para o professor)

Chamada **real**, mas **fora do experimento**: usa as 8 frases do guia de anotação, que não estão no dataset, e grava em `etapa2/demonstracoes/`. Gasta 8 unidades da franquia, que contam na trava de orçamento.

```bash
uv run etapa2/src/executar.py --dados etapa2/dados/demonstracao.csv --provedores google --demonstracao
uv run etapa2/src/analisar.py --execucao <id_execucao> --demonstracao
```

**Nunca rode a demonstração (nem nada) sobre `candidatos_*.csv`, `piloto.csv` ou `teste.csv` antes da anotação**: ver a resposta da API enviesaria o gabarito.

## 1. Anotar o gabarito (antes de qualquer chamada real)

Siga [`dados/guia_de_anotacao.md`](dados/guia_de_anotacao.md). Em resumo:

```bash
# as planilhas já foram geradas; este comando só acrescenta textos de lotes novos
uv run etapa2/src/anotacao.py planilhas

# depois que os DOIS anotadores terminarem
uv run etapa2/src/anotacao.py consolidar    # concordância + divergencias.csv
#   ...discutir e preencher rotulo_final/justificativa em divergencias.csv...
uv run etapa2/src/anotacao.py consolidar    # de novo, até 'pendentes: 0'
uv run etapa2/src/anotacao.py montar        # congela piloto.csv, teste.csv, exploratorio_misto.csv
```

Se `montar` avisar que uma classe ficou abaixo de 50 textos, decidam **agora**, antes de chamar as APIs: aceitar o número real (e declarar) ou sortear mais candidatos com `uv run etapa2/src/amostrar.py --lote extra --teste-por-estrela 20` e anotá-los.

## 2. Configurar as credenciais (uma vez)

O `.env` é o mesmo dos testes da Etapa 1 e é **ignorado pelo git**:

```bash
cp testes/modelo_de_credenciais.txt .env        # se ainda não existir
```

A Etapa 2 usa só três variáveis dele: `AZURE_LANGUAGE_ENDPOINT`, `AZURE_LANGUAGE_KEY` e `GOOGLE_CLOUD_PROJECT`.

### Microsoft Azure — Language, tier F0

1. No [portal Azure](https://portal.azure.com) (a conta *Azure for Students* não pede cartão), crie um recurso **Language** na região **East US**, tier de preço **F0 (Free)**.
2. Em *Recurso → Chaves e Ponto de Extremidade*, copie o endpoint e uma das chaves para o `.env`.
3. **Confira que o tier é F0.** É o F0 que garante custo zero: ao esgotar a cota mensal de 5.000 registros, ele recusa as chamadas em vez de cobrar. O executor exige `"azure_tier": "F0"` na configuração, mas não consegue ler o tier da conta — essa conferência no portal é de vocês.

A Azure permite um único recurso F0 de cada tipo por assinatura. Se já existir um Language F0 (por exemplo, dos testes da Etapa 1), reutilize-o.

### Google Cloud — Natural Language API

Com a [CLI `gcloud`](https://cloud.google.com/sdk/docs/install) instalada (troque `MEU_PROJETO`):

```bash
gcloud auth application-default login
gcloud auth application-default set-quota-project MEU_PROJETO
gcloud services enable language.googleapis.com --project=MEU_PROJETO
```

No `.env`: `GOOGLE_CLOUD_PROJECT=MEU_PROJETO`.

- **Não use arquivo de chave JSON.** A credencial fica em `~/.config/gcloud`, fora do projeto.
- O projeto precisa de conta de faturamento — o **teste gratuito** cria uma e não cobra sem upgrade manual. Dentro das 5.000 unidades mensais de sentimento, nada é cobrado.
- **Recomendado:** em *Faturamento → Orçamentos e alertas*, crie um orçamento de US$ 1 com alerta. A trava do executor só enxerga o que este programa enviou; o alerta enxerga a conta inteira.

## 3. Rodar o piloto

```bash
uv run etapa2/src/executar.py --dados etapa2/dados/piloto.csv --provedores azure google
```

Antes de chamar qualquer serviço, o programa:

1. procura credencial em arquivo que o git publicaria — e **aborta** se achar;
2. confere que as variáveis do `.env` existem (sem imprimir valores);
3. calcula o consumo no **pior caso** e **recusa** se passar de 90% da franquia do mês;
4. mostra o plano e pede que se digite `sim`.

Os resultados vão para `etapa2/resultados/<id_execucao>/`. Analise:

```bash
uv run etapa2/src/analisar.py --execucao <id_execucao>
```

O piloto serve para encontrar problemas (permissão, idioma, formato) e, se o grupo decidir, ajustar o limiar do Google. **Registre qualquer ajuste em `etapa2/metodologia.md` antes do teste.** Para mudar um parâmetro, copie `config/experimento.example.json` para `config/experimento.json` (ignorado pelo git) e edite a cópia.

## 4. Rodar o teste final

Com a metodologia aprovada e o conjunto congelado:

```bash
uv run etapa2/src/executar.py --dados etapa2/dados/teste.csv --provedores azure google
uv run etapa2/src/analisar.py --execucao <id_execucao>
```

Se cair no meio (rede, Ctrl+C), **não comece de novo**: retome, e o que já foi coletado não é chamado outra vez.

```bash
uv run etapa2/src/executar.py --dados etapa2/dados/teste.csv --retomar <id_execucao>
```

## 5. Depois da coleta

- Confira o consumo no painel de cada provedor e registre em `etapa2/STATUS_ETAPA2.md` (custo **observado**, separado do estimado).
- **Recalcular métricas não chama API:** `analisar.py` lê só os arquivos da execução. Qualquer pessoa reproduz as tabelas a partir do repositório.

## O que vai para o repositório público — e o que não vai

| Vai | Não vai |
|---|---|
| Respostas originais dos serviços, **sanitizadas** (sem endpoint do recurso, ID do projeto ou chave) | `.env`, chaves, credenciais |
| Tentativas, durações, erros, configuração sem segredos, versões | `etapa2/config/experimento.json` (local) |
| Métricas, tabelas e gráficos | `etapa2/simulacoes/` (verificações locais com provedor simulado — **nunca** evidência de execução) |
