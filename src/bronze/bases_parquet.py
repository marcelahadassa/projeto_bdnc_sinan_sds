# %%
# Importa Path para trabalhar com caminhos de arquivos
from pathlib import Path

# Importa pandas para leitura e escrita dos dados
import pandas as pd


# %%
# Define a raiz do projeto
ROOT_DIR = Path(__file__).resolve().parents[2]

# Define a pasta principal da camada bronze
BRONZE_DIR = ROOT_DIR / "data" / "bronze"


# %%
def converter_sds_para_parquet():
    """
    Converte a base original da SDS de Excel para Parquet.
    """

    # Caminho do arquivo Excel original da SDS
    caminho_entrada = BRONZE_DIR / "sds" / "sds_completo.xlsx"

    # Pasta onde o Parquet será salvo
    pasta_saida = BRONZE_DIR / "sds" / "parquet"

    # Cria a pasta de saída se ela não existir
    pasta_saida.mkdir(parents=True, exist_ok=True)

    # Caminho final do arquivo Parquet
    caminho_saida = pasta_saida / "sds_completo.parquet"

    # Lê o arquivo Excel
    df = pd.read_excel(caminho_entrada)

    # Salva em Parquet
    df.to_parquet(
        caminho_saida,
        index=False,
        engine="pyarrow",
        compression="snappy"
    )

    # Exibe confirmação
    print(f"SDS convertida: {caminho_saida}", flush=True)
    print(f"Linhas: {df.shape[0]} | Colunas: {df.shape[1]}", flush=True)

    # Retorna o caminho gerado
    return caminho_saida


# %%
def converter_ibge_para_parquet():
    """
    Converte a base de municípios do IBGE de CSV para Parquet.
    """

    # Caminho do arquivo CSV original do IBGE
    caminho_entrada = BRONZE_DIR / "ibge" / "municipios_ibge.csv"

    # Pasta onde o Parquet será salvo
    pasta_saida = BRONZE_DIR / "ibge" / "parquet"

    # Cria a pasta de saída se ela não existir
    pasta_saida.mkdir(parents=True, exist_ok=True)

    # Caminho final do arquivo Parquet
    caminho_saida = pasta_saida / "municipios_ibge.parquet"

    # Lê o CSV do IBGE
    df = pd.read_csv(caminho_entrada)

    # Salva em Parquet
    df.to_parquet(
        caminho_saida,
        index=False,
        engine="pyarrow",
        compression="snappy"
    )

    # Exibe confirmação
    print(f"IBGE convertido: {caminho_saida}", flush=True)
    print(f"Linhas: {df.shape[0]} | Colunas: {df.shape[1]}", flush=True)

    # Retorna o caminho gerado
    return caminho_saida


# %%
def converter_cnes_para_parquet():
    """
    Converte o CSV extraído do CNES para Parquet.
    """

    # Pasta onde está o CSV extraído do ZIP do CNES
    pasta_cnes = BRONZE_DIR / "cnes"

    # Busca arquivos CSV dentro da pasta do CNES
    arquivos_csv = sorted(pasta_cnes.glob("*.csv"))

    # Interrompe se nenhum CSV for encontrado
    if not arquivos_csv:
        raise FileNotFoundError(f"Nenhum CSV do CNES encontrado em: {pasta_cnes}")

    # Usa o primeiro CSV encontrado
    caminho_entrada = arquivos_csv[0]

    # Pasta onde o Parquet será salvo
    pasta_saida = pasta_cnes / "parquet"

    # Cria a pasta de saída se ela não existir
    pasta_saida.mkdir(parents=True, exist_ok=True)

    # Caminho final do arquivo Parquet
    caminho_saida = pasta_saida / "cnes_estabelecimentos.parquet"

    # Tenta ler o CSV com separador ponto e vírgula
    try:
        df = pd.read_csv(
            caminho_entrada,
            sep=";",
            dtype=str,
            encoding="utf-8",
            low_memory=False
        )

    # Se der erro de encoding, tenta com latin1
    except UnicodeDecodeError:
        df = pd.read_csv(
            caminho_entrada,
            sep=";",
            dtype=str,
            encoding="latin1",
            low_memory=False
        )

    # Se o CSV ficou com uma única coluna, tenta ler com vírgula
    if df.shape[1] == 1:
        df = pd.read_csv(
            caminho_entrada,
            sep=",",
            dtype=str,
            encoding="utf-8",
            low_memory=False
        )

    # Salva em Parquet
    df.to_parquet(
        caminho_saida,
        index=False,
        engine="pyarrow",
        compression="snappy"
    )

    # Exibe confirmação
    print(f"CNES convertido: {caminho_saida}", flush=True)
    print(f"Linhas: {df.shape[0]} | Colunas: {df.shape[1]}", flush=True)

    # Retorna o caminho gerado
    return caminho_saida


# %%
def converter_bases_bronze_para_parquet():
    """
    Executa a conversão das bases auxiliares para Parquet.
    """

    # Converte SDS para Parquet
    converter_sds_para_parquet()

    # Converte IBGE para Parquet
    converter_ibge_para_parquet()

    # Converte CNES para Parquet
    converter_cnes_para_parquet()

    # Mensagem final
    print("\nConversão das bases bronze finalizada.", flush=True)


# %%
# Permite executar o arquivo diretamente pelo terminal
if __name__ == "__main__":
    converter_bases_bronze_para_parquet()

#%%