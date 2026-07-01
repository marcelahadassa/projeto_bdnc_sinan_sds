# %%
# Importa subprocess para executar módulos Python do projeto
import subprocess

# Importa sys para usar o Python do ambiente atual
import sys

# Importa Path para manipular caminhos
from pathlib import Path

# Importa DuckDB para calcular métricas dos arquivos gerados
import duckdb

# Importa Dagster
import dagster as dg


# %%
# Importa checks de qualidade dos dados
from src.quality.data_quality_check import (
    check_bronze_sinan_dbc_extraidos,
    check_bronze_sinan_parquet_valido,
    check_bronze_sds_parquet_valido,
    check_bronze_ibge_parquet_valido,
    check_bronze_cnes_parquet_valido,
    check_silver_ibge_valido,
    check_silver_cnes_valido,
    check_silver_sds_valido,
    check_silver_sinan_valido,
    check_gold_tem_linhas,
    check_gold_chaves_sem_nulos,
    check_gold_totais_nao_negativos,
    check_gold_totais_batem_com_silver,
    check_duckdb_tabelas_existentes,
    check_duckdb_gold_bate_com_parquet,
)

# Importa metadados documentais dos assets
from src.orchestration.asset_metadata import (
    SILVER_SINAN_METADATA,
    SILVER_SDS_METADATA,
    SILVER_IBGE_METADATA,
    SILVER_CNES_METADATA,
    GOLD_SDS_SINAN_METADATA,
    DUCKDB_WAREHOUSE_METADATA,
)


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
def executar_modulo_python(nome_modulo):
    """
    Executa um módulo Python do projeto.
    Exemplo: src.bronze.extracao_sinan
    """

    raiz_projeto = encontrar_raiz_projeto()

    comando = [
        sys.executable,
        "-u",
        "-m",
        nome_modulo,
    ]

    resultado = subprocess.run(
        comando,
        cwd=raiz_projeto,
        capture_output=True,
        text=True,
    )

    if resultado.returncode != 0:
        raise RuntimeError(
            f"Erro ao executar {nome_modulo}\n\n"
            f"STDOUT:\n{resultado.stdout}\n\n"
            f"STDERR:\n{resultado.stderr}"
        )

    return resultado.stdout


# %%
def contar_linhas_parquet(caminho):
    """
    Conta linhas de um arquivo Parquet usando DuckDB.
    """

    caminho_sql = str(caminho.resolve()).replace("\\", "/").replace("'", "''")

    con = duckdb.connect(":memory:")

    total = con.execute(f"""
        SELECT COUNT(*)
        FROM read_parquet('{caminho_sql}');
    """).fetchone()[0]

    con.close()

    return int(total)


# ============================================================
# BRONZE - EXTRAÇÕES
# ============================================================

# %%
@dg.asset(
    group_name="bronze",
    description="Extrai os dados brutos do SINAN."
)
def bronze_extracao_sinan(context: dg.AssetExecutionContext):
    saida = executar_modulo_python("src.bronze.extracao_sinan")
    context.log.info(saida)
    return "extracao_sinan_concluida"


# %%
@dg.asset(
    group_name="bronze",
    description="Extrai os dados brutos da SDS."
)
def bronze_extracao_sds(context: dg.AssetExecutionContext):
    saida = executar_modulo_python("src.bronze.extracao_sds")
    context.log.info(saida)
    return "extracao_sds_concluida"


# %%
@dg.asset(
    group_name="bronze",
    description="Extrai os dados brutos do IBGE."
)
def bronze_extracao_ibge(context: dg.AssetExecutionContext):
    saida = executar_modulo_python("src.bronze.extracao_ibge")
    context.log.info(saida)
    return "extracao_ibge_concluida"


# %%
@dg.asset(
    group_name="bronze",
    description="Extrai os dados brutos do CNES."
)
def bronze_extracao_cnes(context: dg.AssetExecutionContext):
    saida = executar_modulo_python("src.bronze.extracao_cnes")
    context.log.info(saida)
    return "extracao_cnes_concluida"


# ============================================================
# BRONZE - CONVERSÕES PARA PARQUET
# ============================================================

# %%
@dg.asset(
    deps=[bronze_extracao_sinan],
    group_name="bronze",
    description="Converte os arquivos DBC do SINAN para Parquet."
)
def bronze_sinan_parquet(context: dg.AssetExecutionContext):
    saida = executar_modulo_python("src.bronze.sinan_dbc_parquet")
    context.log.info(saida)
    return "sinan_parquet_concluido"


# %%
@dg.asset(
    deps=[
        bronze_extracao_sds,
        bronze_extracao_ibge,
        bronze_extracao_cnes,
    ],
    group_name="bronze",
    description="Converte as bases SDS, IBGE e CNES para Parquet."
)
def bronze_bases_parquet(context: dg.AssetExecutionContext):
    saida = executar_modulo_python("src.bronze.bases_parquet")
    context.log.info(saida)
    return "bases_parquet_concluido"


# %%
@dg.asset(
    deps=[
        bronze_sinan_parquet,
        bronze_bases_parquet,
    ],
    group_name="bronze",
    description="Valida os arquivos Parquet gerados na camada Bronze."
)
def bronze_validacao(context: dg.AssetExecutionContext):
    saida = executar_modulo_python("src.bronze.validacao")
    context.log.info(saida)
    return "validacao_bronze_concluida"


# ============================================================
# SILVER
# ============================================================

# %%
@dg.asset(
    deps=[bronze_validacao],
    group_name="silver",
    description="Trata a base IBGE e gera municípios padronizados.",
    metadata=SILVER_IBGE_METADATA,
)
def silver_ibge(context: dg.AssetExecutionContext):
    saida = executar_modulo_python("src.silver.tratamento_ibge")
    context.log.info(saida)
    return "silver_ibge_concluido"


# %%
@dg.asset(
    deps=[bronze_validacao],
    group_name="silver",
    description="Trata a base CNES e gera unidades padronizadas.",
    metadata=SILVER_CNES_METADATA,
)
def silver_cnes(context: dg.AssetExecutionContext):
    saida = executar_modulo_python("src.silver.tratamento_cnes")
    context.log.info(saida)
    return "silver_cnes_concluido"


# %%
@dg.asset(
    deps=[bronze_validacao],
    group_name="silver",
    description="Trata a base SDS e cria colunas compatíveis com o SINAN.",
    metadata=SILVER_SDS_METADATA,
)
def silver_sds(context: dg.AssetExecutionContext):
    saida = executar_modulo_python("src.silver.tratamento_sds")
    context.log.info(saida)

    caminho_sds = (
        encontrar_raiz_projeto()
        / "data"
        / "silver"
        / "sds"
        / "base_sds_tratada.parquet"
    )

    total_linhas = contar_linhas_parquet(caminho_sds)

    return dg.MaterializeResult(
        metadata={
            "dagster/row_count": total_linhas,
            "dagster/uri": caminho_sds.as_uri(),
            "arquivo": str(caminho_sds),
        }
    )


# %%
@dg.asset(
    deps=[
        silver_ibge,
        silver_cnes,
    ],
    group_name="silver",
    description="Trata a base SINAN usando IBGE e CNES tratados.",
    metadata=SILVER_SINAN_METADATA,
)
def silver_sinan(context: dg.AssetExecutionContext):
    saida = executar_modulo_python("src.silver.tratamento_sinan")
    context.log.info(saida)

    caminho_sinan = (
        encontrar_raiz_projeto()
        / "data"
        / "silver"
        / "sinan"
        / "base_sinan_tratada.parquet"
    )

    total_linhas = contar_linhas_parquet(caminho_sinan)

    return dg.MaterializeResult(
        metadata={
            "dagster/row_count": total_linhas,
            "dagster/uri": caminho_sinan.as_uri(),
            "arquivo": str(caminho_sinan),
        }
    )


# ============================================================
# GOLD
# ============================================================

# %%
@dg.asset(
    deps=[
        silver_sinan,
        silver_sds,
    ],
    group_name="gold",
    description="Gera a base Gold cruzada entre SDS e SINAN.",
    metadata=GOLD_SDS_SINAN_METADATA,
)
def gold_sds_sinan(context: dg.AssetExecutionContext):
    """
    Executa o cruzamento Gold entre SDS e SINAN.
    """

    saida = executar_modulo_python("src.gold.sds_sinan")
    context.log.info(saida)

    caminho_gold = (
        encontrar_raiz_projeto()
        / "data"
        / "gold"
        / "sds_sinan"
        / "sds_sinan_final.parquet"
    )

    total_linhas = contar_linhas_parquet(caminho_gold)

    return dg.MaterializeResult(
        metadata={
            "dagster/row_count": total_linhas,
            "dagster/uri": caminho_gold.as_uri(),
            "arquivo": str(caminho_gold),
        }
    )


# ============================================================
# WAREHOUSE
# ============================================================

# %%
@dg.asset(
    deps=[
        gold_sds_sinan,
    ],
    group_name="warehouse",
    description="Carrega as camadas Bronze, Silver e Gold no banco DuckDB.",
    metadata=DUCKDB_WAREHOUSE_METADATA,
)
def duckdb_warehouse(context: dg.AssetExecutionContext):
    """
    Carrega os dados finais no DuckDB.
    """

    saida = executar_modulo_python("src.storage.duckdb_loader")
    context.log.info(saida)

    caminho_duckdb = (
        encontrar_raiz_projeto()
        / "data"
        / "warehouse"
        / "sinan_sds.duckdb"
    )

    return dg.MaterializeResult(
        metadata={
            "dagster/uri": caminho_duckdb.as_uri(),
            "arquivo": str(caminho_duckdb),
            "tipo_armazenamento": "DuckDB",
        }
    )


# ============================================================
# JOB
# ============================================================

# %%
pipeline_completo_job = dg.define_asset_job(
    name="pipeline_completo_sinan_sds",
    selection=dg.AssetSelection.all(),
)


# %%
defs = dg.Definitions(
    assets=[
        # Bronze - extrações
        bronze_extracao_sinan,
        bronze_extracao_sds,
        bronze_extracao_ibge,
        bronze_extracao_cnes,

        # Bronze - conversões
        bronze_sinan_parquet,
        bronze_bases_parquet,
        bronze_validacao,

        # Silver
        silver_ibge,
        silver_cnes,
        silver_sds,
        silver_sinan,

        # Gold
        gold_sds_sinan,

        # Warehouse
        duckdb_warehouse,
    ],
    asset_checks=[
        # Bronze
        check_bronze_sinan_dbc_extraidos,
        check_bronze_sinan_parquet_valido,
        check_bronze_sds_parquet_valido,
        check_bronze_ibge_parquet_valido,
        check_bronze_cnes_parquet_valido,

        # Silver
        check_silver_ibge_valido,
        check_silver_cnes_valido,
        check_silver_sds_valido,
        check_silver_sinan_valido,

        # Gold
        check_gold_tem_linhas,
        check_gold_chaves_sem_nulos,
        check_gold_totais_nao_negativos,
        check_gold_totais_batem_com_silver,

        # DuckDB
        check_duckdb_tabelas_existentes,
        check_duckdb_gold_bate_com_parquet,
    ],
    jobs=[
        pipeline_completo_job,
    ],
)