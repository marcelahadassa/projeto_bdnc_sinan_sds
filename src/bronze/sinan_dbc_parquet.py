# Importa Path para trabalhar com caminhos de forma segura
from pathlib import Path

# Importa pandas para criar DataFrames e salvar em Parquet
import pandas as pd

# Importa DBF para ler arquivos .dbf
from dbfread import DBF

# Importa datasus_dbc para descompactar .dbc em .dbf
import datasus_dbc


# Define a raiz do projeto, subindo duas pastas a partir deste arquivo
ROOT_DIR = Path(__file__).resolve().parents[2]

# Pasta onde estão os arquivos .dbc baixados do DataSUS
PASTA_DBC = ROOT_DIR / "data" / "bronze" / "sinan" / "dbc"

# Pasta intermediária onde os arquivos .dbf serão salvos
PASTA_DBF = ROOT_DIR / "data" / "bronze" / "sinan" / "dbf"

# Pasta final onde os arquivos .parquet serão salvos
PASTA_PARQUET = ROOT_DIR / "data" / "bronze" / "sinan" / "parquet"


def converter_dbc_para_parquet(sobrescrever: bool = False):
    """
    Converte arquivos .dbc do SINAN para .parquet,
    usando .dbf apenas como etapa intermediária.

    Parâmetro:
        sobrescrever: se True, recria os arquivos mesmo que já existam.
    """

    # Mensagem inicial da execução
    print("Iniciando conversão DBC -> DBF -> Parquet...", flush=True)

    # Cria as pastas de saída caso elas ainda não existam
    PASTA_DBF.mkdir(parents=True, exist_ok=True)
    PASTA_PARQUET.mkdir(parents=True, exist_ok=True)

    # Busca arquivos .dbc e .DBC, evitando duplicatas no Windows
    arquivos_dbc = sorted(
        {
            arquivo.resolve(): arquivo
            for padrao in ("*.dbc", "*.DBC")
            for arquivo in PASTA_DBC.glob(padrao)
        }.values(),
        key=lambda arquivo: arquivo.name.lower()
    )

    # Interrompe a execução se nenhum arquivo for encontrado
    if not arquivos_dbc:
        raise FileNotFoundError(f"Nenhum arquivo .dbc encontrado em: {PASTA_DBC}")

    # Exibe a quantidade de arquivos encontrados
    print(f"Foram encontrados {len(arquivos_dbc)} arquivos .dbc.", flush=True)

    # Lista para guardar os caminhos dos Parquets gerados
    arquivos_convertidos = []

    # Percorre cada arquivo .dbc encontrado
    for caminho_dbc in arquivos_dbc:

        # Define o caminho do DBF intermediário
        caminho_dbf = PASTA_DBF / f"{caminho_dbc.stem}.dbf"

        # Define o caminho do Parquet final
        caminho_parquet = PASTA_PARQUET / f"{caminho_dbc.stem}.parquet"

        # Pula a conversão se o Parquet já existir e sobrescrever for False
        if caminho_parquet.exists() and not sobrescrever:
            print(f"Parquet já existe. Pulando: {caminho_parquet.name}", flush=True)
            arquivos_convertidos.append(caminho_parquet)
            continue

        # Exibe o arquivo atual
        print(f"\nProcessando: {caminho_dbc.name}", flush=True)

        # Mostra o tamanho do arquivo DBC em MB
        tamanho_mb = caminho_dbc.stat().st_size / 1024 / 1024
        print(f"Tamanho DBC: {tamanho_mb:.2f} MB", flush=True)

        # Descompacta o arquivo .dbc para .dbf
        print("Convertendo DBC para DBF...", flush=True)
        datasus_dbc.decompress(str(caminho_dbc), str(caminho_dbf))

        # Lê o DBF usando a codificação comum dos arquivos DataSUS
        print("Lendo DBF com dbfread...", flush=True)
        tabela = DBF(str(caminho_dbf), encoding="iso-8859-1")

        # Converte os registros do DBF para DataFrame
        df = pd.DataFrame(iter(tabela))

        # Exibe o tamanho do DataFrame carregado
        print(f"Linhas: {df.shape[0]} | Colunas: {df.shape[1]}", flush=True)

        # Salva o DataFrame em Parquet com compressão
        print("Salvando em Parquet...", flush=True)
        df.to_parquet(
            caminho_parquet,
            index=False,
            engine="pyarrow",
            compression="snappy"
        )

        # Confirma o arquivo gerado
        print(f"Salvo em: {caminho_parquet}", flush=True)

        # Adiciona o arquivo gerado à lista final
        arquivos_convertidos.append(caminho_parquet)

    # Mensagem final
    print("\nConversão finalizada.", flush=True)

    # Retorna os caminhos dos arquivos Parquet criados
    return arquivos_convertidos


# Permite executar o arquivo diretamente pelo terminal
if __name__ == "__main__":
    converter_dbc_para_parquet()

