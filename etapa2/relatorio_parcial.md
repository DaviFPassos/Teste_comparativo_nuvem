> **Nota da integração (18/10/2026) — leia antes do texto abaixo.**
> O texto a seguir é do Rafael e foi mantido **sem alterações**. Ao juntar o ramo `feat/azure-nlp-sentimento` ao `main`:
>
> - Esta é uma **verificação de infraestrutura com 5 frases**, não um resultado do experimento. Os números (acurácia 80%, latência média 990 ms) não entram nas métricas da Etapa 2 e não sustentam conclusões sobre a Azure — com 5 textos, um único erro muda a acurácia em 20 pontos.
> - Os dados foram movidos: o CSV para `etapa2/dados/fumaca_azure.csv` (o nome `teste.csv` fica reservado ao conjunto congelado) e o resultado, byte a byte, para `etapa2/demonstracoes/20261018T151637-azure-rafael/`.
> - Os scripts `executar.py`, `analisar.py` e `provedores/azure.py` deste ramo foram substituídos pela versão integrada, que roda Azure e Google pelo mesmo protocolo. O código original continua no histórico do git, no commit `82e25f9`.
> - Divergências com as decisões do grupo (`etapa2/metodologia.md`): o experimento compara **Azure e Google** — a AWS ficou fora por exigir plano pago —, e o conjunto de teste vem do B2W-Reviews01 anotado por dois integrantes.
> - Uma observação deste teste **confirma** um achado da demonstração com o Google: a primeira chamada (1.580 ms) é bem mais lenta que as demais (~843 ms). Isso reforça a proposta de chamada de aquecimento na metodologia.

---

# Relatório Parcial — Etapa 2 (Avaliação Prática)
**Provedor:** Microsoft Azure  
**Serviço:** Azure AI Language (Foundry Tools)  
**Funcionalidade:** Análise de Sentimento em Português (pt-BR)  
**Responsável:** Rafael Fonseca Pessoa

## 1. Metodologia de Execução
Para a avaliação prática, foi desenvolvido um pipeline em Python (gerenciado pelo `uv`) que consome a API do Azure AI Language. 
- **Entrada:** O script lê um arquivo CSV (`teste.csv`) contendo os textos e o gabarito humano (`rotulo_referencia`).
- **Chamada:** Cada texto é enviado individualmente para a API (requisição síncrona), configurado com o idioma `pt-br`. 
- **Rate Limit:** Foi implementado um intervalo de 1 segundo (`time.sleep(1)`) entre as chamadas para respeitar o limite do tier gratuito (F0).
- **Normalização:** As respostas da Azure (`positive`, `negative`, `neutral`, `mixed`) são mapeadas para o padrão do trabalho (`positivo`, `negativo`, `neutro`, `misto`).
- **Métricas:** O script mede o tempo exato de resposta (latência) em milissegundos usando `time.perf_counter()` e gera a matriz de confusão.

## 2. Resultados Obtidos (Amostra Inicial)
Execução realizada com um lote piloto de 5 textos para validação da infraestrutura.

- **Total de textos avaliados:** 5
- **Acurácia:** 80.00% (4/5 acertos)
- **Latência Média:** 990.39 ms (aproximadamente 1 segundo por requisição)

### Matriz de Confusão:
- Esperado: positivo | Previsto: positivo (2 vezes)
- Esperado: negativo | Previsto: negativo (1 vez)
- Esperado: neutro   | Previsto: neutro (1 vez)
- **Esperado: negativo | Previsto: neutro (1 vez)** *(Erro)*

## 3. Análise Preliminar
A infraestrutura de testes está 100% validada e pronta para receber o dataset completo do grupo (150 textos). 

**Sobre o erro observado:** O texto *"A comida estava fria e o garçom foi grosseiro"* foi classificado pela Azure como **neutro**, enquanto o gabarito apontava como **negativo**. Esse é um comportamento esperado e importante para o relatório final: a API pode falhar em captar insatisfações quando a negatividade é expressa por adjetivos descritivos (comida fria, garçom grosseiro) sem palavras de carga emocional explícita (como "odiei" ou "péssimo").

**Latência:** A média de ~990ms é um dado relevante para a comparação com AWS e Google, que possuem arquiteturas de inferência diferentes.

## 4. Próximos Passos
1. Substituir o `teste.csv` piloto pelo arquivo oficial contendo os 150 textos (50 positivos, 50 negativos, 50 neutros) definidos em conjunto com os colegas da AWS e Google.
2. Executar novamente o script (`uv run etapa2/src/executar.py`) e extrair as métricas finais.
3. Comparar a latência e a acurácia da Azure com os resultados dos outros provedores.
