# Roteiro de trabalho — Etapa 1: comparação de serviços de IA em nuvem

> **Para a IA do VS Code:** leia este arquivo inteiro e os dois PDFs da pasta `documentos_base/` antes de propor alterações. Este roteiro contém o contexto necessário para trabalhar sem acesso à conversa em que ele foi criado. Comece pela Fase 1 e mantenha o andamento registrado em `STATUS.md`.

> **Decisão confirmada pelo grupo:** a Etapa 1 terá exatamente três categorias: **NLP / análise de texto, visão computacional e fala para texto**. A pesquisa existente cobre somente NLP e deve ser aproveitada como um dos três capítulos. O roteiro da avaliação prática está em `ROTEIRO_ETAPA2.md`.

## 1. Como o aluno deve preparar a pasta

1. Crie uma pasta chamada `trabalho-ia-nuvem` no computador.
2. Coloque os arquivos `ROTEIRO_ETAPA1.md` e `ROTEIRO_ETAPA2.md` dentro dela. Comece pelo primeiro.
3. Crie a subpasta `documentos_base`.
4. Coloque nessa subpasta os dois PDFs abaixo. Para facilitar, você pode copiar os arquivos usando os nomes simplificados indicados na tabela.
5. Abra a pasta `trabalho-ia-nuvem` no VS Code: **Arquivo → Abrir Pasta**.
6. Abra o chat da IA, anexe ou mencione este roteiro e envie o pedido da seção 14.

| Arquivo original | Nome sugerido dentro de `documentos_base/` |
|---|---|
| `Computação em Nuvem - Trabalho I_ Comparação de Serviços de Inteligência Artificial em Nuvem.pdf` | `enunciado_professor.pdf` |
| `parte1_comparacao_nlp_aws_azure_gcp.pdf` ou a cópia com `(1)` | `pesquisa_nlp_inicial.pdf` |

Os dois PDFs são necessários: o primeiro determina as exigências; o segundo contém pesquisa que deve ser aproveitada. Mantenha os originais preservados. Se a IA não conseguir ler PDF, ela deve tentar extrair o texto localmente e avisar caso a leitura continue indisponível.

## 2. Contexto e objetivo

Estamos desenvolvendo um trabalho acadêmico de Computação em Nuvem, no mestrado em Ciência da Computação da UNIFOR. O trabalho compara serviços de inteligência artificial oferecidos por **AWS, Microsoft Azure e Google Cloud**, sob a perspectiva de quem deseja integrá-los a uma aplicação.

O enunciado divide o trabalho em:

- **Etapa 1 — Análise comparativa:** seleção de categorias, análise técnica, exemplos ilustrativos de código, análise econômica e síntese.
- **Etapa 2 — Avaliação prática:** programa efetivamente executado, dados de teste, métricas, resultados e discussão.

**Escopo atual: concluir a Etapa 1.** Os testes reais da Etapa 2 serão desenvolvidos posteriormente. Nesta fase, a IA deve ajudar a pesquisar, escrever, organizar arquivos e conferir os cálculos. Não é necessário executar chamadas pagas às APIs.

### Hierarquia das informações

1. O enunciado do professor define as exigências acadêmicas.
2. A documentação oficial consultada define informações atuais sobre os serviços.
3. A pesquisa inicial de NLP é a base já produzida pelo grupo; suas informações devem ser verificadas antes da versão final.
4. Este roteiro define uma maneira de cumprir as exigências. As três categorias são uma escolha já confirmada pelo grupo; os nomes de pastas e a organização dos arquivos são sugestões práticas.

Se houver divergência, registre-a e ajuste o trabalho à fonte apropriada. Não transforme uma sugestão deste roteiro em exigência atribuída ao professor.

## 3. Exigências essenciais do professor

Os trechos entre aspas abaixo foram transcritos do enunciado fornecido. As páginas são as páginas do PDF.

### 3.1 Categorias e provedores — seção 2, página 2

> “Caso sejam identificadas muitas categorias, o grupo deverá selecionar entre três e cinco para uma análise mais aprofundada.”

> “O relatório deverá explicar brevemente os critérios utilizados pelo grupo para selecionar as categorias analisadas.”

> “Para cada categoria selecionada, deverão ser identificados os serviços correspondentes oferecidos por pelo menos dois dos três provedores. Sempre que houver serviços equivalentes nos três provedores, recomenda-se incluir os três na comparação.”

**Como interpretar:** pesquisar os três provedores; selecionar categorias diversas e justificadas; comparar pelo menos dois provedores por categoria e incluir os três quando houver equivalência. A regra de três a cinco categorias é condicionada à identificação de muitas opções. Neste projeto, o grupo já escolheu três: NLP, visão computacional e fala para texto.

### 3.2 Exemplos de código — seção 3, página 2

> “A análise de cada categoria deverá incluir também breves exemplos de código que ilustrem como os serviços comparados podem ser utilizados na prática.”

> “Nesta etapa, os exemplos não precisam ter sido desenvolvidos ou executados pelo grupo.”

**Como interpretar:** apresentar pequenos exemplos de operações equivalentes e citar a fonte de adaptações. Informar se foram executados, apenas revisados ou adaptados da documentação. Não declarar execução que não aconteceu.

A análise técnica também deve abordar, quando aplicável: funcionalidades, formas de acesso, operações, entradas, saídas, autenticação, configuração, parâmetros, restrições e diferenças relevantes. Essa lista é um resumo da seção 3.

### 3.3 Custos — seção 4, página 3

> “Os cenários deverão utilizar cargas equivalentes para permitir uma comparação direta dos custos entre os provedores.”

> “Todas as hipóteses utilizadas nos cálculos deverão ser explicitadas.”

> “Como os preços dos serviços em nuvem podem variar ao longo do tempo e entre regiões, o relatório deverá indicar a fonte, região e data de consulta dos valores utilizados.”

**Como interpretar:** comparar a mesma tarefa e carga; explicar unidades, arredondamento, faixas, franquias e cálculos. Uma lista de preços isolados não demonstra o custo de um cenário.

### 3.4 Síntese — seção 5, página 3

> “Para cada categoria investigada, o grupo deverá apresentar uma síntese das principais diferenças encontradas entre os provedores.”

**Como interpretar:** reunir implicações técnicas e econômicas. Explicar em quais situações cada alternativa é adequada, sem precisar eleger um vencedor universal.

### 3.5 Entrega — seção 6, página 3

> “Ao final da primeira etapa, o grupo deverá disponibilizar em um repositório público no GitHub os resultados da análise comparativa.”

> “O arquivo README.md do repositório deverá identificar o trabalho e os integrantes do grupo e fornecer acesso aos diferentes artefatos produzidos.”

O repositório deve conter relatório, exemplos de código, planilhas ou dados usados nos custos, gráficos quando aplicável e referências. A seção 12, página 5, determina o uso prioritário de documentação oficial, especialmente APIs/SDKs e preços.

## 4. O que já temos e deve ser aproveitado

O PDF de NLP possui cinco páginas e compara **Amazon Comprehend, Azure Language e Cloud Natural Language API**. Ele já representa uma parte relevante da Etapa 1.

| Conteúdo existente | Local no PDF de NLP | Ação da IA |
|---|---|---|
| Escolha da categoria e justificativa | Página 1 | Reaproveitar e conectar à seleção das outras categorias. |
| SDKs, clientes, autenticação e configuração | Página 1 | Reaproveitar, verificar e explicitar entradas/saídas. |
| Funcionalidades e limites | Página 2 | Preservar a comparação e revisar valores e equivalência. |
| Preços e cenário de 100 mil documentos | Página 3 | Reproduzir os cálculos em arquivos editáveis e verificar premissas. |
| Síntese para o desenvolvedor | Página 4 | Reaproveitar, ajustando conclusões ao que for confirmado. |
| Referências | Páginas 4–5 | Conferir links e relacionar cada fonte às afirmações. |

### Pendências já identificadas no PDF

- Faltam exemplos de código: nomes de métodos nas tabelas ainda não constituem exemplos completos.
- O preço de Azure NLP aparece como aproximado, obtido em fonte secundária. Deve ser confirmado ou continuar claramente marcado como pendência, sem sustentar conclusão definitiva.
- Região/aplicabilidade regional e data devem ficar claras para todos os preços.
- Há referências a “Parte 2” e “Parte 3” que não correspondem à divisão do enunciado. Corrigir para Etapa 1 e Etapa 2 conforme o contexto.
- Sentimento, entidades e frases-chave são funcionalidades de NLP; não devem ser usadas como três categorias distintas para justificar diversidade de domínios.
- As outras categorias ainda precisam ser desenvolvidas.

**Orientação:** converter a pesquisa útil em um capítulo editável e registrar correções. Evitar reescrever do zero informações aproveitáveis. Também não apresentar informação antiga como recém-verificada.

## 5. Escopo confirmado para a Etapa 1

| Categoria | Candidatos a verificar na documentação oficial | Operação ilustrativa |
|---|---|---|
| NLP / análise de texto | Amazon Comprehend; Azure Language; Cloud Natural Language | Sentimento do mesmo texto em português. |
| Visão computacional | Amazon Rekognition; oferta de visão da Microsoft Azure; Google Cloud Vision | Identificação de rótulos de conteúdo na mesma imagem. Se a operação escolhida for detecção de objetos com localização, comparar essa mesma operação em todos. |
| Conversão de fala em texto | Amazon Transcribe; oferta de fala da Microsoft Azure; Google Cloud Speech-to-Text | Transcrição do mesmo áudio, com idioma e formato declarados. |

As categorias estão definidas; esses nomes de serviços são pontos de partida da pesquisa, não confirmação de disponibilidade atual. Verifique nome atual, operação, região, versão e acesso para novos clientes. Se uma oferta não for viável, documente o motivo e procure outra oferta equivalente dentro da mesma categoria. Mantenha pelo menos dois provedores por categoria. Caso isso seja inviável, exponha a evidência ao grupo antes de propor mudança de categoria.

Justificativa sugerida: texto, imagem e áudio permitem comparar funcionalidades diferentes, relevantes para aplicações, com serviços gerenciados acessíveis por APIs ou SDKs.

### Diferença entre categoria, serviço e operação

- **Categoria:** domínio da funcionalidade, como visão computacional.
- **Serviço:** produto do provedor que oferece a funcionalidade.
- **Operação:** tarefa específica chamada pelo código, como detectar rótulos em uma imagem.

Comparar AWS, Azure e Google em sentimento representa **uma categoria em três provedores**. Sentimento, entidades e frases-chave continuam sendo funcionalidades do domínio de NLP. O relatório final da Etapa 1 deve conter os três capítulos, com análise técnica, exemplo de código, custo e síntese em cada um. Não é necessário construir três aplicações completas nem executar os exemplos nesta etapa.

### Matriz de conclusão por categoria

Preencha esta matriz em `STATUS.md`. Marque um item apenas quando houver arquivo e evidência que o sustentem.

| Categoria confirmada | Pesquisa técnica | Código ilustrativo | Custos reproduzíveis | Síntese e fontes |
|---|---|---|---|---|
| NLP / análise de texto | Pendente de revisão do PDF existente | Pendente | Pendente de verificação | Pendente de revisão |
| Visão computacional | Pendente | Pendente | Pendente | Pendente |
| Fala para texto | Pendente | Pendente | Pendente | Pendente |

Esses estados descrevem o ponto de partida do roteiro. Ao retomar um projeto já iniciado, confira os arquivos e atualize os estados sem apagar progresso real.

## 6. Organização sugerida da pasta

Crie os arquivos conforme forem necessários, evitando arquivos vazios que pareçam entregas concluídas.

| Caminho | Finalidade |
|---|---|
| `ROTEIRO_ETAPA1.md` | Este roteiro. |
| `ROTEIRO_ETAPA2.md` | Roteiro da avaliação prática, para a sequência do projeto. |
| `STATUS.md` | Progresso, decisões, pendências e próxima ação. |
| `README.md` | Apresentação e navegação do projeto. |
| `documentos_base/` | Enunciado e pesquisa original preservados. |
| `etapa1/diagnostico.md` | Exigência × material existente × pendência. |
| `etapa1/categorias.md` | Seleção e justificativa das categorias. |
| `etapa1/nlp.md` | Capítulo de NLP revisado. |
| `etapa1/visao.md` | Capítulo de visão computacional. |
| `etapa1/fala.md` | Capítulo de fala para texto. |
| `exemplos/nlp/`, `exemplos/visao/`, `exemplos/fala/` | Exemplos Python separados por provedor. |
| `custos/premissas.csv` | Valores, unidades, regiões, datas e fontes dos cenários. |
| `custos/calcular_custos.py` | Fórmulas e geração das tabelas de custo. |
| `custos/resultados.csv` | Resultados calculados a partir das premissas. |
| `referencias/fontes.md` | Fontes e afirmações que sustentam. |
| `relatorio/relatorio_etapa1.md` | Texto consolidado e editável da entrega. |
| `relatorio/relatorio_etapa1.pdf` | PDF final, após revisão. |
| `.gitignore` | Exclusão de ambiente virtual, credenciais e arquivos temporários. |

Python é uma escolha prática do grupo, não uma linguagem imposta no enunciado. Se o grupo preferir planilha para os custos, ela pode substituir o script, desde que as fórmulas sejam verificáveis.

## 7. Regras de colaboração para a IA do VS Code

1. Responda em português e explique conceitos novos na primeira ocorrência. Exemplos: SDK é uma biblioteca que facilita chamadas ao serviço; franquia é o volume de uso gratuito previsto nas condições do provedor.
2. Leia os arquivos existentes antes de editar. Se os PDFs estiverem ausentes ou ilegíveis, informe exatamente qual conteúdo está faltando; avance apenas no que não depende dele.
3. Trabalhe em fases, com entregas concretas. Após cada fase, resuma o que foi produzido, como foi conferido e o que falta.
4. Faça as alterações locais necessárias quando houver ferramentas de edição. Se o chat não puder editar arquivos, entregue o conteúdo completo e indique o caminho de destino.
5. Use documentação oficial para afirmações técnicas e preços. Registre URL, data real de acesso, região e status de verificação.
6. Se não houver acesso à internet ou a uma tabela dinâmica, registre a limitação e peça somente a informação indispensável. Não invente dados, referências ou datas de consulta.
7. Identifique exemplos ilustrativos e dados hipotéticos. Não fabrique medições, execução de API ou resultados experimentais.
8. Evite dependências desnecessárias. Para os cálculos, prefira inicialmente a biblioteca padrão do Python; SDKs específicos podem ficar separados por categoria.
9. Quando precisar de comandos locais, priorize Windows/PowerShell. Explique o diretório em que o comando deve ser executado. Não altere políticas do sistema apenas para ativar um ambiente virtual; é possível usar diretamente seu executável Python.
10. Nunca grave credenciais no código, README ou registros. Os exemplos devem usar mecanismos de autenticação documentados e variáveis de ambiente quando apropriado.
11. Preparar arquivos locais não exige publicar imediatamente. Para a entrega, orientar a criação/publicação do repositório; pedir os dados necessários da conta/repositório e não inventar endereço do GitHub ou nomes dos integrantes.
12. Atualize `STATUS.md` ao final de cada fase para que outra sessão de IA possa continuar o trabalho.

## 8. Fases de execução

### Fase 1 — Ler os documentos e diagnosticar

**Objetivo:** identificar o que já está atendido e o que realmente precisa ser produzido.

**Ações:**

1. Ler o enunciado completo e o PDF de NLP.
2. Criar `etapa1/diagnostico.md`, com colunas: exigência; seção/página do enunciado; evidência no PDF de NLP; situação; ação necessária.
3. Usar as situações **atendido**, **parcial**, **ausente** e **a verificar**. A existência de uma tabela não significa que seus números já foram verificados.
4. Criar `STATUS.md` com as fases deste roteiro e a próxima ação.

**Critério de conclusão:** o diagnóstico reconhece explicitamente o que pode ser reaproveitado e identifica todas as entregas da Etapa 1.

### Fase 2 — Confirmar ofertas e critérios comuns nas três categorias

**Objetivo:** estabelecer uma comparação coerente.

**Ações:**

1. Pesquisar ofertas nas três nuvens para as três categorias já escolhidas: NLP, visão computacional e fala para texto.
2. Criar `etapa1/categorias.md`, explicando relevância, diversidade e operação comum de cada categoria.
3. Escolher modo de uso comparável: processamento síncrono, assíncrono ou em lote, conforme a tarefa. Explicar diferenças que impeçam equivalência perfeita.
4. Definir o mesmo roteiro de perguntas para cada capítulo: o que faz; como acessar; o que recebe; o que devolve; como autenticar; quais limites; quanto custa; para qual cenário é adequado.

**Critério de conclusão:** as três categorias escolhidas possuem ao menos dois provedores comparáveis cada; o terceiro é incluído quando equivalente e disponível. A tarefa não se encerra após pesquisar somente NLP.

### Fase 3 — Completar os capítulos e exemplos

**Objetivo:** transformar a pesquisa em material técnico que outro desenvolvedor consiga entender.

**Ações:**

1. Produzir primeiro `etapa1/nlp.md` reaproveitando o PDF, corrigindo nomenclatura e verificando afirmações.
2. Produzir `etapa1/visao.md` e `etapa1/fala.md` com a mesma estrutura.
3. Para cada provedor comparado, criar um exemplo pequeno da operação escolhida. Com três provedores nas três categorias, serão nove exemplos; o enunciado não fixa esse número.
4. Mostrar preparação do cliente, entrada, chamada e leitura da saída. Para processamento assíncrono, explicar envio, acompanhamento e obtenção do resultado.
5. Informar dependências, fonte, autenticação necessária e situação de validação de cada exemplo.

**Exemplo didático de entrada para NLP:** `O atendimento foi excelente.` Todos os serviços devem receber esse mesmo texto no exemplo comparativo.

**Critério de conclusão:** cada capítulo tem análise técnica, exemplo por provedor e fontes. O código é coerente com a operação documentada; nenhum exemplo é descrito como executado sem evidência.

### Fase 4 — Construir e conferir os custos

**Objetivo:** permitir que outra pessoa reproduza os valores do relatório.

**Ações:**

1. Verificar preços em fontes oficiais, incluindo unidade, mínimo, arredondamento, franquia, faixas, região e moeda.
2. Registrar essas informações em `custos/premissas.csv`, com campo `status_verificacao` e observações.
3. Para NLP, começar pela simulação existente de 100.000 documentos nos comprimentos de 100, 500, 1.200 e 4.000 caracteres, revisando a viabilidade técnica e a regra de cobrança.
4. Definir cargas equivalentes para imagem e áudio. Quantidades podem ser hipotéticas, desde que declaradas e iguais entre provedores.
5. Implementar as contas e gerar `custos/resultados.csv`. Separar cenários com e sem franquia quando ambos forem usados.
6. Conferir manualmente pelo menos um caso por regra de cobrança e os pontos em que muda o arredondamento ou a faixa.

**Exemplo puramente didático:** se uma tarifa hipotética cobra blocos de 1.000 caracteres, um texto de 1.200 caracteres usa dois blocos. Para 100 textos, são 200 blocos. O valor monetário depende do preço verificado. A regra real pode ser diferente por serviço e operação.

**Critério de conclusão:** tabelas do relatório e arquivo de resultados concordam; cada valor tem fonte e premissas. Preço indisponível aparece como pendência, sem cálculo apresentado como definitivo.

### Fase 5 — Escrever as sínteses e consolidar

**Objetivo:** explicar o significado dos resultados para quem escolherá um serviço.

**Ações:**

1. Escrever uma síntese por categoria, relacionando integração, limites, funcionalidades e custos.
2. Diferenciar conclusões documentais de resultados experimentais. Na Etapa 1, não afirmar qual API é mais precisa ou mais rápida sem evidência adequada.
3. Consolidar `relatorio/relatorio_etapa1.md` com introdução, seleção, três capítulos, síntese geral, limitações e referências.
4. Gerar PDF somente após conferir conteúdo, tabelas, referências e consistência das contas. Revisar visualmente quebras de página, fontes e cortes.

**Critério de conclusão:** o relatório apresenta comparações justificadas e permite rastrear cada número até o arquivo de cálculo e sua fonte.

### Fase 6 — Preparar a entrega no GitHub

**Objetivo:** tornar todos os artefatos acessíveis e compreensíveis.

**Ações:**

1. Escrever README com título, integrantes, objetivo, categorias, organização e links relativos para os arquivos.
2. Explicar como reproduzir os custos e como preparar os exemplos, distinguindo código ilustrativo de código executado.
3. Conferir links, arquivos necessários, dependências e ausência de segredos.
4. Preparar ou atualizar o repositório público indicado pelo grupo. Se a publicação depender da conta do aluno, fornecer instruções e manter essa tarefa pendente até ser realizada.

**Critério de conclusão:** relatório, exemplos, custos e referências estão no repositório público e são localizáveis pelo README. Se estiverem apenas no computador, a preparação local está concluída, mas a exigência de publicação ainda está pendente.

## 9. Modelo de capítulo por categoria

Use a estrutura abaixo em `nlp.md`, `visao.md` e `fala.md`:

1. Objetivo da categoria e caso de uso.
2. Serviços e operação comparável.
3. Tabela de funcionalidades, entradas, saídas, acesso, configuração e limites.
4. Exemplos de código e instruções mínimas.
5. Modelo de cobrança e condições.
6. Cenário de custo, fórmulas, premissas e resultados.
7. Síntese: vantagens, restrições e adequação por cenário.
8. Referências e pendências de verificação.

Evite comparar operações diferentes como se fossem iguais. Por exemplo, transcrição em lote e em tempo real podem ter condições e preços distintos.

## 10. Registro das fontes

Em `referencias/fontes.md`, registre para cada fonte:

- Identificador interno, como `NLP-AWS-01`.
- Provedor e serviço.
- Título da página e URL oficial.
- Data real de consulta.
- Informação sustentada: limite, operação, preço, idioma etc.
- Região ou indicação de que a tabela é global, somente quando a fonte confirmar.
- Estado: verificado; inacessível; informação não localizada; precisa de confirmação.

Se uma página mudar e contrariar a pesquisa inicial, registre o ajuste em `STATUS.md` e atualize texto, exemplo e cálculo afetados.

## 11. Modelo de acompanhamento em STATUS.md

O arquivo deve conter:

- **Objetivo atual:** finalizar a Etapa 1.
- **Fase em andamento:** nome e número.
- **Concluído:** arquivos e verificações efetivamente realizados.
- **Pendências:** descrição, motivo e dependência.
- **Decisões:** categorias, operações, regiões e cenários escolhidos, com justificativa.
- **Próxima ação concreta:** uma tarefa executável.
- **Última atualização:** data real.

Não marcar uma fase como concluída apenas porque seus arquivos foram criados. Aplicar os critérios de conclusão.

## 12. Conferência final da Etapa 1

- [ ] Os três provedores foram pesquisados.
- [ ] A seleção das categorias foi justificada e atende à orientação de diversidade.
- [ ] NLP, visão computacional e fala para texto têm capítulos completos; nenhum deles foi substituído por outra funcionalidade de NLP.
- [ ] Cada categoria compara pelo menos dois provedores; foram incluídos três quando equivalentes.
- [ ] O conteúdo útil da pesquisa de NLP foi aproveitado e suas pendências foram tratadas.
- [ ] Há comparação técnica e exemplos de código por categoria.
- [ ] As fontes dos exemplos adaptados e o estado de execução estão indicados.
- [ ] Preços possuem fonte, região, moeda, data e condições relevantes.
- [ ] Cenários usam cargas equivalentes e hipóteses explícitas.
- [ ] Os resultados de custo são reproduzíveis e concordam com o relatório.
- [ ] Cada categoria possui síntese técnica e econômica.
- [ ] Relatório e referências foram revisados, incluindo o PDF renderizado.
- [ ] README identifica integrantes e aponta para os artefatos.
- [ ] O repositório público contém as entregas exigidas, sem credenciais.

## 13. O que fica para a Etapa 2

O plano para a Etapa 2 está em `ROTEIRO_ETAPA2.md`: avaliar análise de sentimento em português, dentro de NLP, em pelo menos dois provedores estudados na Etapa 1. O professor permite escolher uma ou mais categorias para os experimentos; portanto, estudar três categorias na Etapa 1 não obriga a executar testes nas três.

Serão necessários programa executado, dados de teste, metodologia definida previamente, métricas, registros e análise dos resultados. Antes da execução, confirmar viabilidade das APIs, credenciais e orçamento. O planejamento e o código local podem avançar enquanto dependências externas são resolvidas.

Não incluir resultados inventados dessa etapa no relatório atual. Pode haver um pequeno parágrafo de encaminhamento, identificado como proposta futura.

## 14. Mensagem para iniciar o chat no VS Code

Copie e envie a mensagem abaixo, mencionando este arquivo pelo mecanismo disponível no seu chat:

> Leia integralmente `ROTEIRO_ETAPA1.md` e os PDFs em `documentos_base/`. As três categorias da Etapa 1 já foram escolhidas: NLP, visão computacional e fala para texto. Aproveite a pesquisa existente de NLP como um dos três capítulos. Comece pela Fase 1: crie o diagnóstico de exigências, identifique o que está atendido ou pendente e registre o andamento em `STATUS.md`. Explique didaticamente as decisões e faça as alterações locais necessárias. Siga as fases do roteiro, verificando cada entrega. Consulte fontes oficiais para informações técnicas e preços; quando faltar acesso ou informação, registre a limitação. Não invente referências, preços ou execução de APIs. O planejamento da avaliação prática está em `ROTEIRO_ETAPA2.md`; o foco atual é concluir a Etapa 1.

### Para retomar em outra sessão

> Leia `ROTEIRO_ETAPA1.md` e `STATUS.md`, confira os arquivos existentes e continue a partir da próxima ação registrada. Preserve o trabalho aproveitável e atualize o status após concluir a atividade.
