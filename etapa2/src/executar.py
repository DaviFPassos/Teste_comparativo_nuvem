import csv
import json
import time
import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from provedores.azure import analisar_sentimento_azure

def main():
    caminho_csv = "etapa2/dados/teste.csv"
    resultados = []
    
    print(f"Lendo dados de: {caminho_csv}")
    
    with open(caminho_csv, mode="r", encoding="utf-8") as f:
        leitor = csv.DictReader(f)
        for linha in leitor:
            texto = linha["texto"]
            # Correção aqui: usamos aspas simples dentro das chaves
            print(f"Analisando ID {linha['id']}...")
            
            inicio = time.perf_counter()
            resposta = analisar_sentimento_azure(texto)
            fim = time.perf_counter()
            
            latencia = fim - inicio
            
            resultado_item = {
                "id": linha["id"],
                "texto": texto,
                "rotulo_referencia": linha["rotulo_referencia"],
                "provedor": "Azure",
                "resposta_original": resposta,
                "latencia_ms": round(latencia * 1000, 2),
                "timestamp": datetime.now().isoformat()
            }
            resultados.append(resultado_item)
            
            time.sleep(1) 
            
    os.makedirs("etapa2/resultados", exist_ok=True)
    # Outra correção aqui no strftime
    nome_arquivo = f"etapa2/resultados/azure_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=4)
        
    print(f"\n✅ Teste concluído! Resultados salvos em: {nome_arquivo}")

if __name__ == "__main__":
    main()
