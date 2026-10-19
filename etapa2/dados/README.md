# Dados da Etapa 2

## Origem

**B2W-Reviews01** — corpus aberto de avaliações de produtos em português do Brasil, publicado pela **B2W Digital**.

| Item | Valor |
|---|---|
| Repositório | https://github.com/americanas-tech/b2w-reviews01 |
| Arquivo | `B2W-Reviews01.csv` — 49.453.175 bytes, 132.373 avaliações |
| SHA-256 conferido | `821fb0bf9f7230b0fba4e4f9fadd75a66d1a9ff0b1657810791d33007eb2ab38` |
| Coleta original | Americanas.com, **janeiro a maio de 2018** |
| Artigo | REAL, L.; OSHIRO, M.; MAFRA, A. *B2W-Reviews01: an open product reviews corpus*. B2W Digital — Tech Labs. Distribuído no repositório do dataset como `b2wreviews01_stil2019.pdf`. |
| Consultado em | 18/10/2026 |

## Licença

O dataset é distribuído sob **Creative Commons Atribuição-NãoComercial-CompartilhaIgual 4.0 Internacional (CC BY-NC-SA 4.0)** — https://creativecommons.org/licenses/by-nc-sa/4.0/.

Os arquivos desta pasta que contêm textos do B2W-Reviews01 (`candidatos_*.csv`, `anotacao/planilha_*.csv`, `anotacao/divergencias.csv`, `piloto.csv`, `teste.csv`, `exploratorio_misto.csv`) são **trabalho derivado** e são distribuídos sob a **mesma licença CC BY-NC-SA 4.0**, com crédito à **B2W Digital**. O uso deste repositório é acadêmico e não comercial.

## Como o conjunto foi construído

Tudo é reproduzível pelos scripts; nada foi selecionado à mão.

**1. Filtros** (`etapa2/src/amostrar.py`). Das 132.373 avaliações, **124.926 são elegíveis**:

| Exclusão | Textos | Por quê |
|---|---|---|
| Texto vazio | 3.275 | Nada a analisar |
| Texto duplicado | 4.154 | **Todas** as cópias saem: um texto repetido (ex.: "Muito bom") não é uma avaliação independente, e manter "a primeira" faria o resultado depender da ordem do arquivo |
| Código de rastreio dos Correios | 4 | Dado pessoal: identifica uma entrega e o destinatário |
| Sequência de 7+ dígitos | 14 | Dado pessoal: número de protocolo, nota fiscal ou pedido |
| E-mail, telefone, CPF | 0 | Procurados; nenhum encontrado na fonte |

Textos com dado pessoal são **excluídos, não editados**: editar seria uma transformação a aplicar igualmente a todos os provedores; excluir não altera o que os serviços recebem.

**Exclusões por decisão** (`exclusoes.csv`). Na leitura dos 330 candidatos apareceram **3 textos com o nome do autor** (t196, t219, t300) — dado pessoal que nenhum filtro automático simples detecta. Eles continuam em `candidatos_teste.csv`, porque o sorteio é reproduzível byte a byte a partir da fonte pública, mas `anotacao.py montar` os deixa **fora** do piloto, do teste e do conjunto exploratório, e o manifesto lista cada um com o motivo. Nenhum deles é enviado a provedor algum.

**2. Campos descartados.** O dataset traz gênero, ano de nascimento, estado e um identificador do avaliador. **Nenhum desses campos é copiado** para este repositório, nem o nome e a marca do produto e o título da avaliação. Ficam só: o texto, as estrelas (usadas apenas para estratificar o sorteio), a categoria do produto e o número da linha na fonte (para rastreabilidade).

**3. Sorteio estratificado por estrelas**, semente `20261018`:

| Arquivo | Textos | Composição |
|---|---|---|
| `candidatos_piloto.csv` | 30 | 6 por estrela |
| `candidatos_teste.csv` | 300 | 60 por estrela, sem sobreposição com o piloto |

Estratificar por estrela serve só para que o conjunto tenha **variedade de opinião**: sorteando ao acaso, 36% dos textos seriam de 5 estrelas e só 6% de 2 estrelas. **As estrelas não são o gabarito.** O artigo do próprio dataset mostra que reduzir a escala de 5 pontos a 3 classes "pode levar a conclusões erradas". Os IDs são atribuídos depois de embaralhar, para que não revelem a nota.

Hashes, contagens e parâmetros de cada lote ficam em `manifesto_amostragem.json`.

**4. Anotação** (`etapa2/src/anotacao.py`, regras em [`guia_de_anotacao.md`](guia_de_anotacao.md)). Dois anotadores rotulam os 330 textos de forma independente, sem ver as estrelas nem as respostas das APIs. O anotador A é Davi Fonseca Passos, com rótulos **gerados por IA** e adotados por ele ([`anotacao/LEIAME_sugestao_ia.md`](anotacao/LEIAME_sugestao_ia.md)); o anotador B é um integrante humano. As divergências são resolvidas por discussão registrada.

**5. Montagem dos conjuntos** (`anotacao.py montar`), **antes de qualquer chamada real**:

| Arquivo | Conteúdo |
|---|---|
| `piloto.csv` | Os 30 textos do piloto com rótulo final — para depurar o programa e, se necessário, ajustar o limiar do Google |
| `teste.csv` | Até 50 textos por classe (`positivo`, `negativo`, `neutro`) do conjunto de candidatos, sorteados entre os que receberam essa classe |
| `exploratorio_misto.csv` | Os textos rotulados `misto`, analisados à parte |
| `manifesto_conjuntos.json` | Contagens, concordância entre anotadores e SHA-256 de cada arquivo. O executor **recusa** coletar com um arquivo cujo hash não confere |

Fora do experimento ficam `demonstracao.csv` (8 frases escritas para o guia de anotação) e `fumaca_azure.csv` (5 frases da verificação da Azure feita pelo Rafael: as três primeiras são os exemplos ilustrativos do roteiro). Nenhuma delas vem do B2W-Reviews01, e nenhuma entra nas métricas.

## Estado atual

| Arquivo | Estado em 19/10/2026 |
|---|---|
| `candidatos_piloto.csv`, `candidatos_teste.csv` | **Sorteados** |
| `anotacao/planilha_A.csv` | **Preenchida** (330/330) |
| `anotacao/planilha_B.csv` | **Preenchida** (330/330) por Rafael Fonseca Pessoa |
| `exclusoes.csv` | 3 textos com nome do autor |
| `piloto.csv`, `teste.csv`, `exploratorio_misto.csv` | **Congelados em 19/10/2026**: 30, 115 (50 positivos, 50 negativos, 15 neutros) e 39 textos. Kappa 0,791 |

## Limitações a declarar no relatório

- **Domínio único:** avaliações de produtos de um único varejista. Os resultados não se estendem a redes sociais, notícias, atendimento ou outros tipos de texto.
- **Época:** textos de 2018. A linguagem e os produtos mudaram.
- **Comprimento:** a fonte praticamente não tem textos com menos de 50 caracteres (1 em 124.926) — comentários muito curtos, como "Ótimo!", não estão representados.
- **`neutro` é escasso:** avaliação de produto quase sempre avalia — a sugestão de rótulos achou ~10 entre 300 candidatos. O teste fica com o **número real**, declarado, e a análise traz também a avaliação **sem a classe neutra** (positivo × negativo), decidida antes da coleta (`metodologia.md`).
- **Duplicatas removidas:** os textos mais comuns e mais curtos ("Muito bom", "Recomendo") saem do sorteio por serem repetidos — o conjunto sub-representa avaliações genéricas.
