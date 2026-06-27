import os
import requests

def extrair_ibge():
    # URL do CSV oficial que contém os códigos de municípios (TSE/IBGE)
    # Dica: Verifique se o link direto ao CSV no dados.gov.br não expira. 
    # Se expirar, salve o link permanente do recurso.
    url = "https://raw.githubusercontent.com/kelvins/municipios-brasileiros/main/csv/municipios.csv"
    pasta_destino = "data/bronze/ibge"
    os.makedirs(pasta_destino, exist_ok=True)
    caminho_arquivo = os.path.join(pasta_destino, "municipios_ibge.csv")

    if not os.path.exists(caminho_arquivo):
        print("Baixando base mestra de municípios (IBGE)...")
        response = requests.get(url)
        with open(caminho_arquivo, "wb") as f:
            f.write(response.content)
        print("Base IBGE baixada com sucesso!")
    else:
        print("Base IBGE já existe localmente. Pulando download.")

if __name__ == "__main__":
    extrair_ibge()