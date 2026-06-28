import os
import requests

def baixar_sds():
    url = "https://www.sds.pe.gov.br/images/indicadores/violecia-domestica/MICRODADOS_DE_VIOL%C3%8ANCIA_DOM%C3%89STICA_JAN_2015_A_ABR_2026.xlsx"
    pasta_destino = "data/bronze/sds"
    os.makedirs(pasta_destino, exist_ok=True)
    caminho_arquivo = os.path.join(pasta_destino, "sds_completo.xlsx")

    print("Baixando dados da SDS diretamente da fonte...")
    
    # O 'stream=True' é importante para arquivos grandes (não trava a memória)
    response = requests.get(url, stream=True)
    
    if response.status_code == 200:
        with open(caminho_arquivo, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print("Download da SDS concluído com sucesso!")
    else:
        print(f"Erro ao baixar: Status {response.status_code}")
        raise Exception("Falha na conexão com o portal da SDS.")

if __name__ == "__main__":
    baixar_sds()