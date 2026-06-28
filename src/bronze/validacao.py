# %%
# Importa Path para trabalhar com caminhos de arquivos
from pathlib import Path

# Importa pandas para testar a leitura dos arquivos Parquet
import pandas as pd

# %%
# Define a raiz do projeto
ROOT_DIR = Path(__file__).resolve().parents[2]

# Define a pasta bronze
BRONZE_DIR = ROOT_DIR / "data" / "bronze"


# %%
def validar_arquivo_parquet(caminho_arquivo):
    """
    Valida se um arquivo Parquet existe, abre corretamente e possui linhas.
    """

    # Verifica se o arquivo existe
    if not caminho_arquivo.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_arquivo}")

    # Lê o arquivo Parquet
    df = pd.read_parquet(caminho_arquivo)

    # Verifica se o arquivo tem linhas
    if df.empty:
        raise ValueError(f"Arquivo vazio: {caminho_arquivo}")

    # Exibe informações básicas
    print(f"OK: {caminho_arquivo.name}")
    print(f"Linhas: {df.shape[0]} | Colunas: {df.shape[1]}")
    print("-" * 50)

    # Retorna o DataFrame apenas se for necessário inspecionar depois
    return df


# %%
def validar_bronze():
    """
    Valida os arquivos principais da camada bronze.
    """

    print("Validando camada bronze...\n")

    # Valida os Parquets do SINAN
    pasta_sinan = BRONZE_DIR / "sinan" / "parquet"
    arquivos_sinan = sorted(pasta_sinan.glob("VIOLBR*.parquet"))

    # Confere se os 11 arquivos do SINAN foram gerados
    if len(arquivos_sinan) != 11:
        raise ValueError(f"Esperados 11 arquivos SINAN, encontrados: {len(arquivos_sinan)}")

    # Valida cada arquivo anual do SINAN
    for arquivo in arquivos_sinan:
        validar_arquivo_parquet(arquivo)

    # Valida SDS
    validar_arquivo_parquet(
        BRONZE_DIR / "sds" / "parquet" / "sds_completo.parquet"
    )

    # Valida IBGE
    validar_arquivo_parquet(
        BRONZE_DIR / "ibge" / "parquet" / "municipios_ibge.parquet"
    )

    # Valida CNES
    validar_arquivo_parquet(
        BRONZE_DIR / "cnes" / "parquet" / "cnes_estabelecimentos.parquet"
    )

    print("\nCamada bronze validada com sucesso!")


# %%
# Permite executar o arquivo diretamente pelo terminal
if __name__ == "__main__":
    validar_bronze()
#%%