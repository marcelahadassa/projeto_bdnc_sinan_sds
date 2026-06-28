# %%
# Importa sys para ajustar imports ao rodar por módulo
import sys

# Importa Path para manipular caminhos
from pathlib import Path

# Importa DuckDB
import duckdb


# %%
def encontrar_raiz_projeto():
    """
    Localiza a raiz do projeto procurando pela pasta src/config.py.
    """

    caminho_atual = Path.cwd().resolve()

    for pasta in [caminho_atual, *caminho_atual.parents]:
        if (pasta / "src" / "config.py").exists():
            return pasta

    raise FileNotFoundError("Não foi possível encontrar a raiz do projeto com src/config.py")


# %%
# Encontra a raiz do projeto
ROOT_DIR = encontrar_raiz_projeto()

# Adiciona a raiz ao path
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))


# %%
# Importa caminhos do projeto
from src.config import (
    DUCKDB_PATH,
    WAREHOUSE_DIR,
    SINAN_BRONZE,
    SDS_BRONZE,
    IBGE_BRONZE,
    CNES_BRONZE,
    SINAN_SILVER,
    SDS_SILVER,
    IBGE_SILVER,
    CNES_SILVER,
    SDS_SINAN_GOLD,
)


# %%
def caminho_para_sql(caminho):
    """
    Converte caminho do Windows para formato aceito pelo DuckDB SQL.
    """

    return str(caminho).replace("\\", "/").replace("'", "''")


# %%
def verificar_arquivo(caminho):
    """
    Verifica se um arquivo existe.
    """

    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")


# %%
def verificar_glob(padrao):
    """
    Verifica se existe pelo menos um arquivo no padrão informado.
    """

    arquivos = list(Path(padrao).parent.glob(Path(padrao).name))

    if not arquivos:
        raise FileNotFoundError(f"Nenhum arquivo encontrado no padrão: {padrao}")

    return arquivos


# %%
def criar_schema(conexao, nome_schema):
    """
    Cria schema no DuckDB caso ainda não exista.
    """

    conexao.execute(f"CREATE SCHEMA IF NOT EXISTS {nome_schema};")


# %%
def criar_tabela_por_parquet(conexao, schema, tabela, caminho_ou_glob):
    """
    Cria ou substitui uma tabela no DuckDB a partir de arquivo Parquet.
    """

    caminho_sql = caminho_para_sql(caminho_ou_glob)

    print(f"Criando tabela {schema}.{tabela}...")

    conexao.execute(f"""
        CREATE OR REPLACE TABLE {schema}.{tabela} AS
        SELECT *
        FROM read_parquet('{caminho_sql}', union_by_name = true);
    """)

    total = conexao.execute(
        f"SELECT COUNT(*) FROM {schema}.{tabela};"
    ).fetchone()[0]

    print(f"Tabela {schema}.{tabela} criada com {total} linhas.")


# %%
def carregar_bronze(conexao):
    """
    Carrega as tabelas Bronze no DuckDB.
    """

    print("\nCarregando camada Bronze...")

    # SINAN possui vários arquivos anuais
    caminho_sinan_bronze = SINAN_BRONZE / "parquet" / "VIOLBR*.parquet"
    verificar_glob(caminho_sinan_bronze)

    # Bases auxiliares
    caminho_sds_bronze = SDS_BRONZE / "parquet" / "sds_completo.parquet"
    caminho_ibge_bronze = IBGE_BRONZE / "parquet" / "municipios_ibge.parquet"
    caminho_cnes_bronze = CNES_BRONZE / "parquet" / "cnes_estabelecimentos.parquet"

    verificar_arquivo(caminho_sds_bronze)
    verificar_arquivo(caminho_ibge_bronze)
    verificar_arquivo(caminho_cnes_bronze)

    criar_tabela_por_parquet(conexao, "bronze", "sinan", caminho_sinan_bronze)
    criar_tabela_por_parquet(conexao, "bronze", "sds", caminho_sds_bronze)
    criar_tabela_por_parquet(conexao, "bronze", "ibge", caminho_ibge_bronze)
    criar_tabela_por_parquet(conexao, "bronze", "cnes", caminho_cnes_bronze)


# %%
def carregar_silver(conexao):
    """
    Carrega as tabelas Silver no DuckDB.
    """

    print("\nCarregando camada Silver...")

    caminho_sinan_silver = SINAN_SILVER / "base_sinan_tratada.parquet"
    caminho_sds_silver = SDS_SILVER / "base_sds_tratada.parquet"
    caminho_ibge_silver = IBGE_SILVER / "municipios_tratado.parquet"
    caminho_cnes_silver = CNES_SILVER / "unidades_tratadas.parquet"

    verificar_arquivo(caminho_sinan_silver)
    verificar_arquivo(caminho_sds_silver)
    verificar_arquivo(caminho_ibge_silver)
    verificar_arquivo(caminho_cnes_silver)

    criar_tabela_por_parquet(conexao, "silver", "sinan", caminho_sinan_silver)
    criar_tabela_por_parquet(conexao, "silver", "sds", caminho_sds_silver)
    criar_tabela_por_parquet(conexao, "silver", "ibge", caminho_ibge_silver)
    criar_tabela_por_parquet(conexao, "silver", "cnes", caminho_cnes_silver)


# %%
def carregar_gold(conexao):
    """
    Carrega as tabelas Gold no DuckDB.
    """

    print("\nCarregando camada Gold...")

    caminho_gold = SDS_SINAN_GOLD / "sds_sinan_final.parquet"

    verificar_arquivo(caminho_gold)

    criar_tabela_por_parquet(conexao, "gold", "sds_sinan", caminho_gold)


# %%
def mostrar_resumo(conexao):
    """
    Exibe resumo das tabelas criadas no DuckDB.
    """

    print("\nResumo das tabelas no DuckDB:")

    tabelas = conexao.execute("""
        SELECT 
            table_schema,
            table_name
        FROM information_schema.tables
        WHERE table_schema IN ('bronze', 'silver', 'gold')
        ORDER BY table_schema, table_name;
    """).fetchall()

    for schema, tabela in tabelas:
        total = conexao.execute(
            f"SELECT COUNT(*) FROM {schema}.{tabela};"
        ).fetchone()[0]

        print(f"{schema}.{tabela}: {total} linhas")


# %%
def carregar_dados_duckdb():
    """
    Cria o banco DuckDB e carrega as camadas Bronze, Silver e Gold.
    """

    # Cria pasta do warehouse
    WAREHOUSE_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Criando/atualizando banco DuckDB em: {DUCKDB_PATH}")

    # Conecta ao banco
    conexao = duckdb.connect(str(DUCKDB_PATH))

    try:
        # Cria schemas
        criar_schema(conexao, "bronze")
        criar_schema(conexao, "silver")
        criar_schema(conexao, "gold")

        # Carrega tabelas
        carregar_bronze(conexao)
        carregar_silver(conexao)
        carregar_gold(conexao)

        # Mostra resumo
        mostrar_resumo(conexao)

    finally:
        # Fecha conexão
        conexao.close()

    print("\nDuckDB carregado com sucesso!")

    return DUCKDB_PATH


# %%
if __name__ == "__main__":
    carregar_dados_duckdb()