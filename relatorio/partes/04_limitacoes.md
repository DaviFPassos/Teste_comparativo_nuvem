## 7. Limitações

Registradas para delimitar o alcance das conclusões:

**1. Nenhum exemplo de código foi executado.** A seção 3 do enunciado permite isso nesta etapa. Consequentemente, não há neste relatório qualquer medição de latência, taxa de acerto, taxa de erro ou comportamento em produção.

**2. As conclusões valem para a data e a região declaradas.** Preços de nuvem mudam. Todos os valores são de **US East, em USD, consultados em 23/09/2026**, com a fonte de cada um registrada em `custos/premissas.csv`. Uma consulta futura pode divergir, e a reprodução dos cálculos exige reverificar as premissas.

**3. As cargas dos cenários são hipotéticas.** 100.000 documentos, 100.000 imagens e 10.000 minutos de áudio são quantidades escolhidas pelo grupo para permitir comparação, não estimativas de uso real de nenhuma aplicação. O que garante a validade da comparação não é a quantidade em si, mas o fato de ser **idêntica entre provedores**.

**4. Os resultados não se generalizam para outros volumes sem recálculo.** As faixas de preço têm degraus em pontos diferentes em cada provedor. A ordem observada em 100.000 imagens pode se inverter em 10 milhões.

**5. Comparou-se uma operação por categoria.** Sentimento de documento, detecção de rótulos e transcrição em lote. Cada serviço oferece dezenas de outras operações, com preços e limites próprios, que não foram analisadas.

**6. Informações não localizadas ficaram como pendência.** Especificamente:

| Pendência | Onde |
|---|---|
| Tamanho máximo de arquivo, duração máxima de áudio e número de jobs simultâneos do Amazon Transcribe | Página de cotas não acessível na consulta |
| Franquia gratuita da tabela Recognition da Cloud Speech-to-Text **V2** | Não localizada; a faixa de 60 minutos consta das tabelas da V1 |
| Valor padrão de `MinConfidence` do `DetectLabels` | Não localizado; o exemplo de código fixa o parâmetro explicitamente |
| Limite de tags por imagem no Azure Image Analysis | Não localizado nas páginas consultadas |

Nenhuma dessas lacunas foi preenchida por estimativa.

**7. A distinção `pt-BR` da Azure não foi testada.** A documentação registra que a Azure distingue português do Brasil de português de Portugal, e que AWS e Google não. **Ela não afirma que isso produza melhor resultado em textos brasileiros**, e este relatório não o afirma. É uma hipótese verificável na Etapa 2.
