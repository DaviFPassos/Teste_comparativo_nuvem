# Roteiro de trabalho — Etapa 2: avaliação prática de serviços de IA em nuvem

> **Para a IA do VS Code:** leia este arquivo, `ROTEIRO_ETAPA1.md`, `STATUS.md`, o enunciado em `documentos_base/` e os capítulos já produzidos. Não suponha que a Etapa 1 está concluída apenas porque existe um roteiro. Verifique o estado do projeto e comece pela Fase 1 abaixo. Explique as decisões em português e registre o progresso.

## 1. Contexto e escopo

Este projeto acadêmico compara serviços de IA de AWS, Microsoft Azure e Google Cloud, sob a perspectiva de quem os integra a aplicações. O grupo confirmou três categorias para a **Etapa 1**:

1. NLP / análise de texto.
2. Visão computacional.
3. Fala para texto.

Já existe uma pesquisa inicial de NLP que será aproveitada e revisada. O plano de trabalho para a **Etapa 2** é aprofundar **análise de sentimento em português**, dentro de NLP, com execução real em **pelo menos dois provedores** estudados na Etapa 1. Incluir o terceiro se houver acesso, tempo e orçamento.

Esse recorte é uma escolha metodológica do projeto. O professor permite avaliar uma ou mais categorias; não exige que todas as três sejam testadas. Caso o grupo queira ampliar o experimento, documentar a mudança antes de coletar dados.

**Pergunta do experimento:** diante dos mesmos textos em português, como os serviços se comparam em qualidade das respostas, tempo de resposta, sucesso das requisições e custo?

As métricas propostas neste roteiro podem ser ajustadas antes da coleta, com justificativa. O professor não fixa número de textos, quantidade de repetições nem limiares de classificação.

## 2. Exigências do professor, transcritas

As citações abaixo são do enunciado do Trabalho I enviado pelo grupo. As páginas indicam a posição no PDF.

### Seleção e comparação — seção 7, página 4

> “A partir dos serviços investigados na primeira etapa, o grupo deverá selecionar uma ou mais categorias para avaliação prática.”

> “Para cada categoria escolhida, deverão ser testados serviços equivalentes ou concorrentes de pelo menos dois provedores, de forma que os mesmos dados ou requisições possam ser utilizados, sempre que possível, nos diferentes serviços.”

**Como cumprir:** escolher serviços que já foram estudados e submeter a eles o mesmo conjunto de textos, com parâmetros comparáveis.

### Execução e dados — seção 8, página 4

> “Diferentemente dos exemplos de código apresentados na primeira etapa, o código desenvolvido nesta etapa deverá ser efetivamente executado pelo grupo.”

> “O conjunto de dados deverá ter tamanho e diversidade suficientes para permitir uma análise minimamente representativa dos serviços. Caso sejam utilizados dados provenientes de fontes externas, sua origem deverá ser identificada.”

**Como cumprir:** desenvolver e executar o programa, preservar entradas e respostas reais, identificar a origem dos textos e justificar a amostra.

### Metodologia — seção 9, páginas 4–5

> “Antes da realização dos testes, o grupo deverá definir quais aspectos dos serviços serão avaliados e como serão medidos.”

> “Não é necessário utilizar todas essas métricas. O grupo deverá selecionar aquelas que sejam pertinentes aos serviços avaliados e explicar como serão calculadas ou observadas.”

> “Quando a avaliação envolver a qualidade ou acurácia das respostas, deverá ser definido um critério que permita determinar ou estimar a qualidade dos resultados produzidos.”

**Como cumprir:** escrever o protocolo antes de executar a avaliação final. Para medir acurácia, produzir um gabarito independente das respostas dos provedores.

### Análise — seção 10, página 5

> “Os serviços equivalentes deverão ser submetidos, tanto quanto possível, às mesmas condições de teste, permitindo uma comparação entre os provedores.”

> “Os resultados deverão ser consolidados e apresentados por meio de tabelas e gráficos, acompanhados de uma análise das principais diferenças observadas entre os serviços.”

> “A análise deverá também confrontar os resultados práticos com as conclusões obtidas na primeira etapa.”

**Como cumprir:** registrar configurações, medir de forma consistente, gerar tabelas e gráficos a partir das respostas e discutir as expectativas da Etapa 1.

### Entrega — seção 11, página 5

> “Ao final da segunda etapa, o mesmo repositório público no GitHub utilizado na primeira etapa deverá ser atualizado com os artefatos da avaliação prática.”

O enunciado exige código-fonte, dados de teste ou instruções para obtê-los, metodologia, dados coletados, processamento, tabelas, gráficos e conclusões. O README deve orientar a organização e a execução. Credenciais não podem ser incluídas no repositório.

## 3. Decisões que precisam estar registradas antes da coleta

Crie `etapa2/metodologia.md` com a tabela abaixo preenchida. Não usar valores fictícios como se tivessem sido decididos pelo grupo.

| Decisão | Orientação inicial |
|---|---|
| Funcionalidade | Sentimento de documento em português, em modelos pré-treinados. |
| Provedores | Pelo menos dois entre AWS, Azure e Google, conforme acesso verificado. |
| Serviços e versões | Confirmar a operação e a versão na documentação oficial e nos recursos disponíveis. |
| Modo de chamada | Preferir um documento por chamada e processamento sequencial para facilitar a comparação inicial. |
| Dados | Textos com IDs estáveis, origem documentada, variedade de tamanho e sentimento. |
| Classes de referência | Positivo, negativo e neutro na avaliação principal; tratamento separado de casos ambíguos. |
| Normalização | Regras de classes e de conversão de score definidas antes da avaliação final. |
| Métricas | Proposta: acurácia, macro-F1, latência, taxa de sucesso e custo. Justificar a seleção final. |
| Repetições | Uma rodada completa inicialmente; repetições adicionais somente se úteis e previstas no orçamento. |
| Erros | Timeout, máximo de tentativas, espera entre tentativas e condições para interromper uma execução. |
| Custo | Tarifa verificada, franquia aplicável, custo estimado e teto de gasto definido pelo grupo. |
| Ambiente | Máquina, local da execução, regiões dos serviços, data, Python e versões dos SDKs. |

**Explicação:** comparar latência com um texto por chamada em um provedor e lotes de 25 em outro mistura duas cargas diferentes. Se o objetivo for estudar lotes, criar um experimento separado com essa pergunta explícita.

## 4. Organização dos arquivos

Use a mesma pasta e o mesmo repositório da Etapa 1. Preserve os artefatos já concluídos.

| Caminho sugerido | Conteúdo |
|---|---|
| `ROTEIRO_ETAPA2.md` | Este roteiro, na raiz. |
| `STATUS.md` | Visão geral das duas etapas e próxima ação. |
| `etapa2/STATUS_ETAPA2.md` | Fases, decisões, pendências e execuções da avaliação prática. |
| `etapa2/metodologia.md` | Protocolo aprovado pelo grupo antes da coleta final. |
| `etapa2/dados/README.md` | Origem, licença, construção, anotação e limitações do conjunto. |
| `etapa2/dados/piloto.csv` | Entradas para depurar o programa e definir regras. |
| `etapa2/dados/teste.csv` | Conjunto final, separado do piloto. |
| `etapa2/dados/anotacoes.csv` | Rótulos humanos, divergências e decisão final, quando aplicável. |
| `etapa2/config/experimento.example.json` | Estrutura de configuração sem credenciais. |
| `etapa2/src/provedores/` | Integração de cada serviço. |
| `etapa2/src/executar.py` | Percorre dados, chama os serviços e registra resultados. |
| `etapa2/src/normalizar.py` | Converte respostas ao formato comum. |
| `etapa2/src/analisar.py` | Calcula métricas e gera tabelas e gráficos. |
| `etapa2/requirements.txt` | Dependências efetivamente usadas, com versões registradas. |
| `etapa2/resultados/<id_execucao>/` | Configuração sem segredos, respostas, tentativas, predições e métricas de uma execução. |
| `etapa2/graficos/` | Figuras geradas por código a partir dos resultados identificados. |
| `relatorio/relatorio_etapa2.md` e `.pdf` | Metodologia, resultados, discussão e conclusões. |
| `README.md` | Navegação e instruções das duas etapas. |

Os nomes são sugestões. Caso o projeto já tenha estrutura equivalente, aproveitá-la e explicar o mapeamento. Não criar um segundo repositório para a Etapa 2.

## 5. Construir um conjunto de teste compreensível

### Tamanho e variedade

Uma configuração inicial possível é **150 textos: 50 positivos, 50 negativos e 50 neutros**, além de um pequeno piloto separado. Isso é uma sugestão de trabalho, não uma exigência nem garantia de representatividade.

Antes de fixar a quantidade, estimar o custo, verificar limites e avaliar a diversidade. Incluir comprimentos diferentes, formas de escrita e assuntos relevantes. Se os textos forem criados pelo grupo, identificá-los como dados controlados e limitar as conclusões ao tipo de texto estudado.

### Gabarito de referência

Gabarito é o rótulo que será usado para verificar se o serviço acertou. Definir regras como:

- **Positivo:** expressa avaliação favorável predominante.
- **Negativo:** expressa avaliação desfavorável predominante.
- **Neutro:** comunica informação sem avaliação predominante.
- **Ambíguo/misto:** combina posições ou não permite uma decisão consistente segundo as regras.

Sempre que possível, duas pessoas anotam sem consultar a saída das APIs; depois discutem divergências. Registrar quem revisou e como chegaram à decisão. Se houver somente um anotador, declarar essa limitação. Rótulos sugeridos por IA precisam de revisão humana identificada.

No plano de três classes, separar casos ambíguos em uma análise exploratória **antes** de consultar os provedores. Não retirar depois os textos em que uma API errou. Alternativamente, definir desde o início um experimento de quatro classes, se houver uma regra comparável justificável para todos os serviços.

### Colunas sugeridas

`id`, `texto`, `rotulo_referencia`, `origem`, `subconjunto`, `observacao_anotacao`.

Exemplos abaixo são apenas ilustrações das colunas, não resultados coletados:

| id | texto | rotulo_referencia |
|---|---|---|
| ex001 | O atendimento foi excelente. | positivo |
| ex002 | O pedido chegou danificado e estou insatisfeito. | negativo |
| ex003 | O estabelecimento abre às nove horas. | neutro |

Verificar IDs únicos, textos não vazios, ausência de duplicatas entre piloto e teste, codificação UTF-8 e compatibilidade com o menor limite relevante das APIs. Remover dados pessoais antes de congelar a versão final. Documentar qualquer transformação aplicada igualmente aos textos enviados aos provedores.

## 6. Tornar as respostas comparáveis

As saídas não devem ser tratadas como idênticas. Confirmar o formato atual de cada serviço na documentação e no piloto. A pesquisa inicial aponta classes de sentimento em AWS/Azure e score contínuo no Google.

### Regra inicial a documentar

1. Guardar a resposta original de cada serviço, sem segredos.
2. Converter nomes de classes para uma convenção comum, como `positivo`, `negativo`, `neutro` e `misto`.
3. Para score contínuo, definir limiares antes de analisar o teste final. Exemplo metodológico: abaixo de −0,25 → negativo; acima de +0,25 → positivo; intervalo inclusivo entre −0,25 e +0,25 → neutro. Esses números são uma escolha inicial a justificar, não uma regra universal do Google.
4. Se os limiares forem ajustados, usar somente o piloto/desenvolvimento. Congelar a regra antes de avaliar `teste.csv`.
5. Preservar `misto` como saída distinta. No conjunto principal de três classes, uma previsão `misto` conta como erro de classificação, sem virar automaticamente `neutro`. Reportar também a frequência dessa saída.

Não comparar diretamente score de sentimento com probabilidade/confiança de outra API. São grandezas diferentes. Não usar a resposta de um dos provedores como gabarito dos demais.

## 7. Métricas e denominadores

Definir a população avaliada evita números aparentemente comparáveis calculados sobre textos diferentes.

### Qualidade

Na comparação principal, usar os **mesmos IDs com resposta utilizável em todos os provedores comparados**. Informar quantos textos ficaram nessa interseção, quantos foram excluídos por falha e os motivos. A saída `misto` continua sendo resposta utilizável e entra como erro no plano de três classes.

- **Acurácia = acertos / textos avaliados.** Exemplo didático: 80 acertos em 100 textos = 80%; não é resultado real do trabalho.
- **Precisão de uma classe = TP / (TP + FP).** TP: acertou essa classe; FP: previu essa classe quando o gabarito era outra.
- **Revocação de uma classe = TP / (TP + FN).** FN: o gabarito era essa classe, mas a previsão foi outra, inclusive `misto`.
- **F1 da classe = 2 × precisão × revocação / (precisão + revocação).** Definir no código o tratamento de denominadores nulos e informar classes sem exemplos.
- **Macro-F1:** média do F1 das três classes de referência. Reportar também o número de exemplos por classe.

Gerar matriz de confusão com três linhas de referência e, se necessário, uma coluna extra de previsão `misto`. Se a biblioteca usada exigir uma matriz quadrada, incluir a categoria adicional de maneira explícita e explicar que o macro-F1 principal considera as três classes de referência.

Apresentar separadamente a taxa de falha e a **fração de acertos sobre todos os textos programados**, na qual falha de serviço não é acerto. Isso evita que um provedor pareça melhor apenas por ter respondido a poucos casos fáceis. Se a interseção for muito pequena, reconhecer que a comparação de qualidade ficou limitada.

### Latência

Latência é o tempo de espera pela resposta. Medir com relógio monotônico, como `time.perf_counter()`, imediatamente antes e depois da chamada. Registrar cada tentativa e também o tempo total do item com eventuais novas tentativas e esperas.

Relatar mediana e percentil 95 das chamadas bem-sucedidas, com tamanho da amostra e método de cálculo do percentil. Tratar durações de timeout separadamente. Definir se inicialização do cliente e aquecimento entram na medição. A medida inclui rede e processamento do serviço; não representa isoladamente a velocidade do modelo.

### Sucesso

- **Sucesso por tentativa = tentativas com resposta utilizável / total de tentativas.**
- **Sucesso por texto = textos com resposta utilizável ao final da política de novas tentativas / total de textos programados.**

Registrar erros de autenticação, limite, timeout e resposta inválida. O denominador e a política de tentativas devem ser os mesmos em todos os provedores.

### Custo

Registrar unidades consumidas ou estimadas segundo a cobrança documentada, tarifa, franquia aplicável, região e data. Separar custo estimado por tabela de custo efetivamente observado no painel/fatura. Não assumir que todo erro ou repetição seja gratuito; verificar as regras e registrar incertezas.

Se não houver acesso a custo observado, declarar isso e apresentar somente estimativa. Incluir piloto e repetições no total do projeto, separando-os do custo da rodada final.

## 8. Programa de teste e registro das execuções

Construir uma interface comum para os provedores, com a mesma entrada textual e um registro comum de saída. O programa deve permitir selecionar provedores, dataset, configuração e diretório de resultados.

Campos mínimos de registro:

- ID da execução, ID do texto, provedor e número da tentativa.
- Data/hora, duração da tentativa e duração total do item.
- Estado de sucesso/erro, código e mensagem sanitizada.
- Classe original, score/confiança quando disponíveis e classe normalizada.
- Quantidade de caracteres e bytes da entrada; unidades cobradas/estimadas quando disponíveis.
- Referência ao arquivo de resposta original.

Salvar a configuração sem credenciais, versões do ambiente, versão/hash do dataset, regra de normalização e versão do código. Para retomar uma execução interrompida, identificar itens já concluídos e evitar chamadas repetidas acidentalmente.

Verificações locais podem usar respostas fictícias para conferir parsing, normalização e fórmulas. Marcar esses dados como **simulados** e mantê-los fora dos diretórios das execuções reais. Testes locais não substituem a coleta exigida pelo professor.

## 9. Fases de execução para a IA

### Fase 1 — Conferir a Etapa 1 e a viabilidade

Leia o enunciado, os capítulos de NLP e os registros de custos. Verifique quais provedores foram estudados, quais operações aceitam a entrada definida e quais contas estão disponíveis. Liste pendências em `etapa2/STATUS_ETAPA2.md`.

Código, dataset e metodologia podem ser preparados localmente enquanto faltarem credenciais. Se orçamento ou autorização de uso pago ainda não estiverem definidos, apresentar estimativa concreta e obter essa definição antes das chamadas com custo. Se já houver limite autorizado, trabalhar dentro dele sem pedir novamente.

**Concluído quando:** houver uma seleção justificada de pelo menos dois provedores, dependências conhecidas e plano de custo. A falta de acesso deve aparecer como bloqueio da coleta, não como experimento concluído.

### Fase 2 — Preparar dados e protocolo

Criar piloto separado, conjunto final e gabarito revisado. Escrever a metodologia, as métricas, o tratamento de falhas, a regra de `misto` e os limiares. Verificar se a amostra atende à pergunta do estudo.

**Concluído quando:** o conjunto e o protocolo estiverem versionados, com critérios claros antes de consultar as respostas do teste final.

### Fase 3 — Implementar e fazer o piloto

Implementar os adaptadores, o executor e o processamento. Confirmar instalação e configuração no Windows/PowerShell; preferir chamar diretamente o Python do ambiente virtual se houver dificuldade com ativação. Fazer verificações locais e um piloto real pequeno nos provedores disponíveis, dentro do orçamento.

O piloto serve para detectar problemas de entrada, idioma, permissão e formato de saída. Se ele indicar mudanças, atualizar o protocolo antes da rodada final. Excluir o piloto das métricas principais.

**Concluído quando:** o programa chamar os serviços reais, salvar respostas e permitir calcular as métricas planejadas para os itens do piloto. Registrar quantidades, data e resultados observados.

### Fase 4 — Executar a avaliação final

Usar o dataset e o protocolo congelados. Manter máquina, política de envio e parâmetros equivalentes. Alternar ou sortear de modo reproduzível a ordem dos provedores para reduzir efeitos de horário; registrar a ordem. Preservar todos os erros e tentativas.

Se repetir a coleta, usar rodadas identificadas e incluir o custo. Não contar previsões repetidas do mesmo texto como novos textos independentes. Não interromper nem selecionar resultados porque favorecem um provedor; qualquer parada deve seguir o protocolo ou ser explicada.

**Concluído quando:** houver registros reais para o conjunto planejado em pelo menos dois provedores, incluindo falhas, e identificação completa das condições de execução.

### Fase 5 — Processar e interpretar

Executar o script de análise, conferir manualmente alguns exemplos e uma métrica simples, gerar tabelas e gráficos. Cada tabela deve apontar para a execução e o conjunto usados.

Tabela principal sugerida: provedor, textos programados, respostas válidas, tamanho da interseção, acurácia, macro-F1, latência mediana/p95, sucesso e custo. Usar unidades explícitas, como ms e USD. Não preencher lacunas com números estimados sem identificá-los.

Gráficos úteis: matriz de confusão, comparação de qualidade, distribuição de latência e custo. Escolher os que respondem à pergunta do experimento.

**Concluído quando:** as métricas forem reproduzíveis a partir dos arquivos brutos e os resultados não dependerem de edição manual de tabelas.

### Fase 6 — Confrontar com a Etapa 1

Criar uma tabela com **expectativa documental → evidência experimental → conclusão**. Exemplos de perguntas, sem resultados antecipados:

- A configuração foi tão simples quanto os exemplos da documentação sugeriam?
- A diferença de cobrança por tamanho de texto apareceu no conjunto real?
- Foi necessário tratar saídas mistas ou definir limiares? Como isso afetou a avaliação?
- Houve falhas ou restrições relevantes que o levantamento inicial não havia destacado?

Explicar se os testes confirmam, complementam ou modificam o entendimento anterior. Limitar conclusões à amostra e às condições observadas. Os resultados de sentimento não estabelecem a qualidade de visão e fala, que foram apenas comparadas documentalmente.

**Concluído quando:** houver discussão apoiada em evidências, limitações e ligação explícita com a Etapa 1.

### Fase 7 — Consolidar e entregar

Produzir relatório editável e PDF, revisar visualmente a versão final e atualizar o mesmo repositório público. Preservar a entrega da Etapa 1 e acrescentar a avaliação prática. O README deve explicar instalação, configuração sem segredos, coleta real e reprodução das métricas já coletadas.

Separar os comandos: **recalcular métricas dos arquivos existentes** deve funcionar sem chamar novamente as APIs; **executar nova coleta** requer credenciais e pode gerar custo. Informar os caminhos e parâmetros reais do código criado, sem inventar comandos que não foram implementados.

**Concluído quando:** todos os sete tipos de artefato exigidos estiverem acessíveis no mesmo repositório e houver evidência de execução real.

## 10. Registro do progresso e pendências

Em `etapa2/STATUS_ETAPA2.md`, manter: fase atual; arquivos concluídos; decisões do protocolo; provedores disponíveis; orçamento definido; IDs das execuções; problemas; próxima ação. Atualizar o `STATUS.md` principal com um resumo e link para esse arquivo, preservando o histórico da Etapa 1.

Estados úteis: **planejado**, **implementado localmente**, **piloto executado**, **coleta final executada**, **analisado**, **publicado**. Esses estados não são equivalentes.

Se uma dependência externa bloquear a coleta, concluir o trabalho local possível e informar a ação exata necessária. Nunca apresentar resultados de exemplo como evidência de execução.

## 11. Lista final de conferência

- [ ] O recorte de sentimento foi justificado a partir da Etapa 1.
- [ ] Pelo menos dois provedores foram realmente testados.
- [ ] Dados, origem, limitações e gabarito foram documentados.
- [ ] Piloto e teste final estão separados.
- [ ] Metodologia, limiares, classes e política de falhas foram definidos antes da avaliação final.
- [ ] Os mesmos textos foram usados nas comparações, com exclusões explicadas.
- [ ] Respostas brutas, tentativas, configurações e versões foram preservadas sem segredos.
- [ ] Métricas e gráficos são calculados por código a partir dos registros.
- [ ] Qualidade, cobertura e falhas são apresentadas com denominadores claros.
- [ ] Estimativas de custo estão distinguidas dos valores observados.
- [ ] Resultados foram confrontados com as conclusões da Etapa 1.
- [ ] Limitações impedem generalizações indevidas para outras tarefas ou populações.
- [ ] Relatório, código, dados/instruções, metodologia, registros e gráficos estão no mesmo repositório público.
- [ ] README explica como reproduzir análises e como realizar nova coleta, sem expor credenciais.

## 12. Mensagens para usar no VS Code

### Começar a Etapa 2

> Leia `ROTEIRO_ETAPA2.md`, `ROTEIRO_ETAPA1.md`, `STATUS.md`, o enunciado e o material produzido na Etapa 1. Nosso plano é avaliar sentimento em português em pelo menos dois provedores já estudados. Comece conferindo o estado real do projeto e a viabilidade. Prepare os arquivos locais, a metodologia, o dataset e o programa conforme as fases. Explique didaticamente as decisões. Registre pendências de credenciais e orçamento; avance no trabalho local possível. Não invente resultados nem declare execução de APIs sem evidência. Mantenha `etapa2/STATUS_ETAPA2.md` atualizado.

### Retomar outra sessão

> Leia os dois roteiros, `STATUS.md` e `etapa2/STATUS_ETAPA2.md`. Confira os arquivos e registros das execuções antes de agir. Continue a próxima atividade pendente, preservando resultados reais e decisões já tomadas. Não repita chamadas às APIs se a tarefa puder ser resolvida com os dados coletados.
