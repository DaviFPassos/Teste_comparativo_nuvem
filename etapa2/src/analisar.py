import json
import glob
import os

def main():
    # Pega o arquivo JSON mais recente gerado
    lista_arquivos = glob.glob("etapa2/resultados/*.json")
    if not lista_arquivos:
        print("Nenhum resultado encontrado. Rode o executar.py primeiro.")
        return
        
    arquivo_recente = max(lista_arquivos, key=os.path.getctime)
    print(f"Analisando o arquivo: {arquivo_recente}\n")
    
    with open(arquivo_recente, "r", encoding="utf-8") as f:
        dados = json.load(f)
        
    acertos = 0
    total = len(dados)
    latencia_total = 0
    matriz = {} # Para contar os acertos e erros
    
    # Dicionário para traduzir a resposta da Azure para o padrão do trabalho
    traduzir = {
        "positive": "positivo",
        "negative": "negativo",
        "neutral": "neutro",
        "mixed": "misto"
    }
    
    for item in dados:
        latencia_total += item["latencia_ms"]
        
        esperado = item["rotulo_referencia"]
        
        # Pega o que a Azure respondeu
        resp_original = item["resposta_original"]
        if resp_original.get("sucesso"):
            previsto = traduzir.get(resp_original["sentimento"], "desconhecido")
        else:
            previsto = "erro"
            
        # Contabiliza acerto (Considerando apenas o plano de 3 classes)
        if esperado == previsto:
            acertos += 1
            
        # Contabiliza matriz de confusão
        chave = f"Esperado: {esperado.ljust(8)} | Previsto: {previsto}"
        matriz[chave] = matriz.get(chave, 0) + 1

    # Cálculos finais
    acuracia = (acertos / total) * 100 if total > 0 else 0
    latencia_media = latencia_total / total if total > 0 else 0
    
    print("-" * 40)
    print("📊 RESULTADOS DA AVALIAÇÃO - AZURE")
    print("-" * 40)
    print(f"Total de textos avaliados: {total}")
    print(f"Acurácia: {acuracia:.2f}% ({acertos}/{total} acertos)")
    print(f"Latência Média: {latencia_media:.2f} ms")
    print("-" * 40)
    print("Matriz de Confusão:")
    for k, v in matriz.items():
        print(f"  {k}: {v} vezes")
    print("-" * 40)

if __name__ == "__main__":
    main()
