import os
import zipfile
import requests

URL = "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/CNES/cnes_estabelecimentos_csv.zip"
PASTA_DESTINO = "data/bronze/cnes"
NOME_ZIP = "cnes_estabelecimentos_csv.zip"


def extrair_cnes():
    os.makedirs(PASTA_DESTINO, exist_ok=True)

    caminho_zip = os.path.join(PASTA_DESTINO, NOME_ZIP)

    print("Baixando CNES Estabelecimentos...")

    with requests.get(URL, stream=True, timeout=120) as r:
        r.raise_for_status()

        with open(caminho_zip, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)

    print("Download concluído. Extraindo...")

    with zipfile.ZipFile(caminho_zip, "r") as zip_ref:
        zip_ref.extractall(PASTA_DESTINO)

    print("Extração concluída!")

    return PASTA_DESTINO


if __name__ == "__main__":
    extrair_cnes()