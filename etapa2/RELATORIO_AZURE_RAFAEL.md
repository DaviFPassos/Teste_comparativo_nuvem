# Relatório de Progresso — Integração Azure

**Responsável:** Rafael Fonseca Pessoa  
**Provedor:** Microsoft Azure (Azure AI Language)  
**Data:** 19/10/2026

## 1. O que foi feito
- **Configuração da Conta:** Criação do recurso (Language in Foundry Tools) na região East US, utilizando o tier gratuito **F0**.
- **Integração com a Arquitetura do Grupo:** O código inicial da Azure foi adaptado para a nova estrutura orientada a objetos criada pelo Davi (`etapa2/src/provedores/azure.py`).
- **Validação do Ambiente:** O arquivo `.env` foi configurado localmente (ignorado pelo Git por segurança) e a chave foi validada.
- **Testes de Front-end:** O painel (`etapa2/painel/servidor.py`) foi executado com sucesso. A Azure foi reconhecida como **ATIVA**, e a interface respondeu corretamente (exibindo classe, confianças e latência em tempo real).

## 2. Resultados da Demonstração (Validação Técnica)
Para garantir que toda a pipeline (executor -> API -> análise -> gráficos) funciona, foi rodada uma demonstração com 8 frases (`demonstracao.csv`).

- **Execução ID:** `20261019T132214Z-demonstracao-r1` *(evidências commitadas na pasta demonstracoes)*
- **Acurácia:** 66,7% (4 acertos de 6 textos válidos) *- Nota: a amostra de 8 frases é pequena e não representa o experimento final.*
- **Latência Mediana:** 224 ms (p95: 262 ms)
- **Previsões `misto`:** 0
- **Custo Estimado:** US$ 0,00 (consumo dentro da franquia F0).
- **Artefatos Gerados:** Tabelas em CSV/JSON e gráficos (`qualidade.png`, `matriz_confusao.png`, `latencia.png`) salvos na pasta de demonstrações.

## 3. Status Atual e Próximos Passos
✅ **Configuração e demonstração validadas.**  
⏳ **Aguardando:** O piloto e o experimento final (dataset de 300 textos) **NÃO** foram executados ainda, seguindo as regras da metodologia.

**O que falta para o grupo:**
1. Realizar a anotação manual do gabarito (preencher as planilhas A e B).
2. Consolidar o arquivo final (`teste.csv`).
3. Rodar o piloto e a coleta real na Azure e no Google para gerar os gráficos comparativos finais.
