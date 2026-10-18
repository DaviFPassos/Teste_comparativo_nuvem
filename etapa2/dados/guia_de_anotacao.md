# Guia de anotação do gabarito — Etapa 2

**Para quem vai anotar.** Este guia define o rótulo que cada texto deve receber. O seu rótulo é o **gabarito**: é contra ele que as respostas da Azure e do Google serão medidas. Por isso ele precisa ser feito **sem consultar as APIs** e **sem consultar o colega**.

## Antes de começar

1. Abra a **sua** planilha: `etapa2/dados/anotacao/planilha_A.csv` ou `planilha_B.csv`.
   - **Excel:** *Dados → De Texto/CSV*, origem **UTF-8**, delimitador **vírgula**. Ao salvar, mantenha **CSV UTF-8**. (Se o Excel salvar com ponto e vírgula, não tem problema: o script aceita os dois.)
   - **Google Planilhas ou LibreOffice:** importar o CSV direto.
2. Escreva seu nome em `etapa2/dados/anotacao/anotadores.json`, no campo da sua letra.
3. Preencha **só** as colunas `rotulo` e, se quiser, `observacao`. Não altere `id` nem `texto`.

São 330 textos curtos (mediana de 100 caracteres). Faça em mais de uma sessão se cansar — rótulo dado com pressa vira ruído no gabarito.

## Os cinco rótulos

Escreva exatamente uma destas palavras, em minúsculas e sem acento:

| Rótulo | Quando usar |
|---|---|
| `positivo` | O texto expressa **avaliação favorável predominante**. Pode haver uma ressalva pequena, desde que a opinião geral seja claramente boa. |
| `negativo` | O texto expressa **avaliação desfavorável predominante**. Pode haver um elogio pequeno, desde que a opinião geral seja claramente ruim. |
| `neutro` | O texto **comunica informação sem avaliação predominante**: descreve, relata, pergunta ou informa, sem dizer se gostou ou não. |
| `misto` | O texto **combina avaliações favoráveis e desfavoráveis sem que uma predomine**, ou não permite uma decisão consistente com as regras acima. |
| `invalido` | Não é uma avaliação legível em português: outro idioma, sequência de letras sem sentido, texto só com símbolos. |

## Regras de decisão

**1. Julgue o texto, não a nota.** Você não vê as estrelas, e é de propósito. Avaliação de 4 estrelas pode ter texto negativo, e vice-versa — o próprio artigo do dataset mostra isso.

**2. Predominância decide entre `positivo`/`negativo` e `misto`.** Pergunte: *se eu tivesse que resumir em uma palavra se a pessoa ficou satisfeita, conseguiria sem hesitar?*
- Consegue, e a resposta é "sim" → `positivo`.
- Consegue, e a resposta é "não" → `negativo`.
- Não consegue, porque os dois lados pesam parecido → `misto`.

**3. Produto e loja contam igualmente.** Reclamar da entrega, do atendimento ou da troca é avaliação desfavorável, mesmo que o produto em si não seja comentado. Se o produto é elogiado e a entrega criticada com peso parecido, é `misto`.

**4. Expectativa e recomendação são avaliação.** "Recomendo", "não comprem", "superou as expectativas", "me arrependi" contam como opinião.

**5. Ironia: rotule o sentido pretendido.** "Ótimo, chegou quebrado" é `negativo`. Se você não tem certeza de que é ironia, use `misto` e explique em `observacao`.

**6. `neutro` é raro em avaliação de produto — e tudo bem.** Não force um texto para `neutro` só para equilibrar as classes. Um texto que diz "Chegou no prazo, funciona" está avaliando (favoravelmente), não só informando.

**7. Erros de digitação e gírias não importam.** Rotule pelo que a pessoa quis dizer.

**8. Na dúvida, escreva em `observacao`.** Uma frase curta sobre o porquê ajuda muito na discussão das divergências.

## Exemplos ilustrativos

Estes exemplos foram **escritos para este guia** e não fazem parte do conjunto de teste:

| Texto | Rótulo | Por quê |
|---|---|---|
| "Produto excelente, chegou antes do prazo. Recomendo." | `positivo` | Favorável, sem ressalva |
| "Bom, mas a tampa é meio frágil." | `positivo` | Favorável predominante; a ressalva é menor (regra 2) |
| "A cor é bonita, mas parou de funcionar em uma semana." | `negativo` | Defeito pesa mais que a cor |
| "Produto ótimo, porém a entrega atrasou 20 dias e ninguém respondeu." | `misto` | Elogio ao produto e crítica à loja com peso parecido (regra 3) |
| "Comprei para dar de presente para minha mãe." | `neutro` | Relata, não avalia |
| "O fone tem cabo de 1,2 m e vem com três tamanhos de borracha." | `neutro` | Descreve, não avalia |
| "Ótimo, veio faltando peça." | `negativo` | Ironia (regra 5) |
| "asdkjh qwe poiu" | `invalido` | Sem sentido |

## Depois de terminar

1. Salve a planilha e avise o grupo. **Não abra a planilha do colega** antes que os dois terminem.
2. Alguém roda `uv run etapa2/src/anotacao.py consolidar`. Ele calcula a concordância entre vocês (kappa de Cohen) e gera `etapa2/dados/anotacao/divergencias.csv`.
3. Os dois **juntos** discutem cada divergência e preenchem `rotulo_final` e `justificativa`. Ninguém consulta API nessa etapa.
4. Roda-se `consolidar` de novo e depois `montar`, que congela `piloto.csv`, `teste.csv` e `exploratorio_misto.csv`.

## Uma diferença que vale saber (não muda como você anota)

A regra deste guia para `misto` é **humana**: depende de predominância. A Azure usa uma regra **mecânica**: devolve `mixed` sempre que o documento tem ao menos uma sentença positiva e uma negativa. Então "Bom, mas a tampa é meio frágil" é `positivo` para nós e pode ser `mixed` para a Azure. Isso não é erro de anotação — é uma diferença de definição que a análise vai medir. Anote pelo guia, não tentando prever a API.
