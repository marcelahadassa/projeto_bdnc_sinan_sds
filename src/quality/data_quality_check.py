# %%
# Importa sys para ajustar imports ao rodar pelo Dagster
import sys

# Importa Path para manipular caminhos
from pathlib import Path

# Importa DuckDB para consultar Parquets e o banco local
import duckdb

# Importa Dagster
import dagster as dg


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
ROOT_DIR = encontrar_raiz_projeto()

if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))


# %%
from src.config import (
    SINAN_BRONZE,
    SDS_BRONZE,
    IBGE_BRONZE,
    CNES_BRONZE,
    SINAN_SILVER,
    SDS_SILVER,
    IBGE_SILVER,
    CNES_SILVER,
    SDS_SINAN_GOLD,
    DUCKDB_PATH,
)


# %%
VALOR_NAO_INFORMADO = "DADO NÃO INFORMADO"


# %%
def caminho_sql(caminho):
    """
    Converte caminho para formato aceito pelo DuckDB SQL.
    Funciona com arquivo único e com glob, como VIOLBR*.parquet.
    """

    return str(Path(caminho).resolve()).replace("\\", "/").replace("'", "''")


# %%
def verificar_arquivo(caminho):
    """
    Verifica se um arquivo existe.
    """

    return caminho.exists()


# %%
def obter_colunas_parquet(conexao, caminho_ou_glob):
    """
    Obtém as colunas de um arquivo Parquet usando DuckDB.
    """

    colunas = conexao.execute(f"""
        SELECT *
        FROM read_parquet('{caminho_sql(caminho_ou_glob)}', union_by_name = true)
        LIMIT 0;
    """).fetchdf().columns.tolist()

    return colunas


# ============================================================
# CHECKS BRONZE - EXTRAÇÃO
# ============================================================

# %%
@dg.asset_check(
    asset=dg.AssetKey("bronze_extracao_sinan"),
    description="Verifica se os arquivos DBC do SINAN foram extraídos corretamente."
)
def check_bronze_sinan_dbc_extraidos():
    """
    Verifica se os arquivos DBC do SINAN existem e não estão vazios.
    """

    anos = list(range(14, 25))

    arquivos_esperados = [
    SINAN_BRONZE / "dbc" / f"VIOLBR{ano}.dbc"
    for ano in anos
    ]

    arquivos_faltantes = [
        str(arquivo)
        for arquivo in arquivos_esperados
        if not arquivo.exists()
    ]

    arquivos_vazios = [
        str(arquivo)
        for arquivo in arquivos_esperados
        if arquivo.exists() and arquivo.stat().st_size == 0
    ]

    passou = len(arquivos_faltantes) == 0 and len(arquivos_vazios) == 0

    return dg.AssetCheckResult(
        passed=passou,
        metadata={
            "total_arquivos_esperados": len(arquivos_esperados),
            "arquivos_faltantes": str(arquivos_faltantes),
            "arquivos_vazios": str(arquivos_vazios),
            "pasta_verificada": str(SINAN_BRONZE / "dbc"),
        },
    )


# ============================================================
# CHECKS BRONZE - PARQUET
# ============================================================

# %%
@dg.asset_check(
    asset=dg.AssetKey("bronze_sinan_parquet"),
    description="Verifica se os Parquets Bronze do SINAN possuem linhas e colunas obrigatórias."
)
def check_bronze_sinan_parquet_valido():
    """
    Verifica a estrutura inicial dos Parquets do SINAN.
    """

    caminho_glob = SINAN_BRONZE / "parquet" / "VIOLBR*.parquet"

    arquivos = sorted((SINAN_BRONZE / "parquet").glob("VIOLBR*.parquet"))

    if not arquivos:
        return dg.AssetCheckResult(
            passed=False,
            metadata={
                "erro": "Nenhum Parquet do SINAN encontrado",
                "caminho": str(caminho_glob),
            },
        )

    colunas_obrigatorias = [
        "DT_NOTIFIC",
        "SG_UF_NOT",
        "ID_MUNICIP",
        "ID_UNIDADE",
        "DT_OCOR",
        "NU_IDADE_N",
        "CS_SEXO",
        "CS_RACA",
        "CS_ESCOL_N",
        "SG_UF",
        "ID_MN_RESI",
        "ID_MN_OCOR",
        "VIOL_FISIC",
        "VIOL_PSICO",
        "VIOL_SEXU",
        "VIOL_FINAN",
    ]

    con = duckdb.connect(":memory:")

    total_linhas = con.execute(f"""
        SELECT COUNT(*)
        FROM read_parquet('{caminho_sql(caminho_glob)}', union_by_name = true);
    """).fetchone()[0]

    colunas_existentes = obter_colunas_parquet(con, caminho_glob)

    con.close()

    colunas_faltantes = [
        coluna for coluna in colunas_obrigatorias
        if coluna not in colunas_existentes
    ]

    passou = (
        len(arquivos) >= 11
        and total_linhas > 0
        and len(colunas_faltantes) == 0
    )

    return dg.AssetCheckResult(
        passed=passou,
        metadata={
            "total_arquivos_parquet": len(arquivos),
            "total_linhas_sinan_bronze": int(total_linhas),
            "total_colunas": len(colunas_existentes),
            "colunas_faltantes": str(colunas_faltantes),
        },
    )


# %%
@dg.asset_check(
    asset=dg.AssetKey("bronze_bases_parquet"),
    description="Verifica se a base SDS Bronze foi convertida corretamente."
)
def check_bronze_sds_parquet_valido():
    """
    Verifica estrutura inicial da SDS na camada Bronze.
    """

    caminho_sds = SDS_BRONZE / "parquet" / "sds_completo.parquet"

    if not caminho_sds.exists():
        return dg.AssetCheckResult(
            passed=False,
            metadata={
                "erro": "Parquet Bronze da SDS não encontrado",
                "caminho": str(caminho_sds),
            },
        )

    colunas_obrigatorias = [
        "MUNICÍPIO DO FATO",
        "REGIAO GEOGRÁFICA",
        "NATUREZA",
        "DATA DO FATO",
        "ANO",
        "SEXO",
        "IDADE SENASP",
        "TOTAL DE VÍTIMAS",
    ]

    con = duckdb.connect(":memory:")

    total_linhas = con.execute(f"""
        SELECT COUNT(*)
        FROM read_parquet('{caminho_sql(caminho_sds)}');
    """).fetchone()[0]

    total_periodo = con.execute(f"""
        SELECT COUNT(*)
        FROM read_parquet('{caminho_sql(caminho_sds)}')
        WHERE TRY_CAST(ANO AS INTEGER) BETWEEN 2014 AND 2024;
    """).fetchone()[0]

    total_feminino = con.execute(f"""
        SELECT COUNT(*)
        FROM read_parquet('{caminho_sql(caminho_sds)}')
        WHERE UPPER(TRIM(CAST(SEXO AS VARCHAR))) LIKE 'FEM%'
           OR UPPER(TRIM(CAST(SEXO AS VARCHAR))) = 'F';
    """).fetchone()[0]

    colunas_existentes = obter_colunas_parquet(con, caminho_sds)

    con.close()

    colunas_faltantes = [
        coluna for coluna in colunas_obrigatorias
        if coluna not in colunas_existentes
    ]

    passou = (
        total_linhas > 0
        and total_periodo > 0
        and total_feminino > 0
        and len(colunas_faltantes) == 0
    )

    return dg.AssetCheckResult(
        passed=passou,
        metadata={
            "total_linhas_sds_bronze": int(total_linhas),
            "total_linhas_2014_2024": int(total_periodo),
            "total_linhas_feminino": int(total_feminino),
            "colunas_faltantes": str(colunas_faltantes),
        },
    )


# %%
@dg.asset_check(
    asset=dg.AssetKey("bronze_bases_parquet"),
    description="Verifica se a base IBGE Bronze foi convertida corretamente."
)
def check_bronze_ibge_parquet_valido():
    """
    Verifica estrutura inicial da base IBGE na camada Bronze.
    """

    caminho_ibge = IBGE_BRONZE / "parquet" / "municipios_ibge.parquet"

    if not caminho_ibge.exists():
        return dg.AssetCheckResult(
            passed=False,
            metadata={
                "erro": "Parquet Bronze do IBGE não encontrado",
                "caminho": str(caminho_ibge),
            },
        )

    colunas_obrigatorias = [
        "codigo_ibge",
        "nome",
        "codigo_uf",
    ]

    con = duckdb.connect(":memory:")

    total_linhas = con.execute(f"""
        SELECT COUNT(*)
        FROM read_parquet('{caminho_sql(caminho_ibge)}');
    """).fetchone()[0]

    total_pe = con.execute(f"""
        SELECT COUNT(*)
        FROM read_parquet('{caminho_sql(caminho_ibge)}')
        WHERE TRY_CAST(codigo_uf AS INTEGER) = 26;
    """).fetchone()[0]

    colunas_existentes = obter_colunas_parquet(con, caminho_ibge)

    con.close()

    colunas_faltantes = [
        coluna for coluna in colunas_obrigatorias
        if coluna not in colunas_existentes
    ]

    passou = (
        total_linhas > 0
        and total_pe == 185
        and len(colunas_faltantes) == 0
    )

    return dg.AssetCheckResult(
        passed=passou,
        metadata={
            "total_linhas_ibge_bronze": int(total_linhas),
            "municipios_pernambuco": int(total_pe),
            "colunas_faltantes": str(colunas_faltantes),
        },
    )


# %%
@dg.asset_check(
    asset=dg.AssetKey("bronze_bases_parquet"),
    description="Verifica se a base CNES Bronze foi convertida corretamente."
)
def check_bronze_cnes_parquet_valido():
    """
    Verifica estrutura inicial da base CNES na camada Bronze.
    """

    caminho_cnes = CNES_BRONZE / "parquet" / "cnes_estabelecimentos.parquet"

    if not caminho_cnes.exists():
        return dg.AssetCheckResult(
            passed=False,
            metadata={
                "erro": "Parquet Bronze do CNES não encontrado",
                "caminho": str(caminho_cnes),
            },
        )

    colunas_obrigatorias = [
        "CO_CNES",
        "CO_UF",
        "CO_IBGE",
        "NO_FANTASIA",
        "NO_RAZAO_SOCIAL",
    ]

    con = duckdb.connect(":memory:")

    total_linhas = con.execute(f"""
        SELECT COUNT(*)
        FROM read_parquet('{caminho_sql(caminho_cnes)}');
    """).fetchone()[0]

    total_pe = con.execute(f"""
        SELECT COUNT(*)
        FROM read_parquet('{caminho_sql(caminho_cnes)}')
        WHERE TRY_CAST(CO_UF AS INTEGER) = 26;
    """).fetchone()[0]

    colunas_existentes = obter_colunas_parquet(con, caminho_cnes)

    con.close()

    colunas_faltantes = [
        coluna for coluna in colunas_obrigatorias
        if coluna not in colunas_existentes
    ]

    passou = (
        total_linhas > 0
        and total_pe > 0
        and len(colunas_faltantes) == 0
    )

    return dg.AssetCheckResult(
        passed=passou,
        metadata={
            "total_linhas_cnes_bronze": int(total_linhas),
            "total_unidades_pernambuco": int(total_pe),
            "colunas_faltantes": str(colunas_faltantes),
        },
    )


# ============================================================
# CHECKS SILVER
# ============================================================

# %%
@dg.asset_check(
    asset=dg.AssetKey("silver_ibge"),
    description="Verifica se a base IBGE Silver possui municípios tratados e Pernambuco completo."
)
def check_silver_ibge_valido():
    """
    Valida a base IBGE tratada.
    """

    caminho_ibge = IBGE_SILVER / "municipios_tratado.parquet"

    if not caminho_ibge.exists():
        return dg.AssetCheckResult(
            passed=False,
            metadata={
                "erro": "Arquivo Silver IBGE não encontrado",
                "caminho": str(caminho_ibge),
            },
        )

    colunas_obrigatorias = [
        "codigo_uf",
        "codigo_ibge",
        "ID_MUNICIP_SINAN",
        "NOME_MUNICIPIO",
    ]

    con = duckdb.connect(":memory:")

    total_linhas = con.execute(f"""
        SELECT COUNT(*)
        FROM read_parquet('{caminho_sql(caminho_ibge)}');
    """).fetchone()[0]

    total_pe = con.execute(f"""
        SELECT COUNT(*)
        FROM read_parquet('{caminho_sql(caminho_ibge)}')
        WHERE TRY_CAST(codigo_uf AS INTEGER) = 26;
    """).fetchone()[0]

    colunas_existentes = obter_colunas_parquet(con, caminho_ibge)

    con.close()

    colunas_faltantes = [
        coluna for coluna in colunas_obrigatorias
        if coluna not in colunas_existentes
    ]

    passou = (
        total_linhas > 0
        and total_pe == 185
        and len(colunas_faltantes) == 0
    )

    return dg.AssetCheckResult(
        passed=passou,
        metadata={
            "total_linhas_ibge_silver": int(total_linhas),
            "municipios_pernambuco": int(total_pe),
            "colunas_faltantes": str(colunas_faltantes),
        },
    )


# %%
@dg.asset_check(
    asset=dg.AssetKey("silver_cnes"),
    description="Verifica se a base CNES Silver possui unidades tratadas."
)
def check_silver_cnes_valido():
    """
    Valida a base CNES tratada.
    """

    caminho_cnes = CNES_SILVER / "unidades_tratadas.parquet"

    if not caminho_cnes.exists():
        return dg.AssetCheckResult(
            passed=False,
            metadata={
                "erro": "Arquivo Silver CNES não encontrado",
                "caminho": str(caminho_cnes),
            },
        )

    colunas_obrigatorias = [
        "ID_UNIDADE",
        "NOME_UNIDADE",
    ]

    con = duckdb.connect(":memory:")

    total_linhas = con.execute(f"""
        SELECT COUNT(*)
        FROM read_parquet('{caminho_sql(caminho_cnes)}');
    """).fetchone()[0]

    total_nome_nao_informado = con.execute(f"""
        SELECT COUNT(*)
        FROM read_parquet('{caminho_sql(caminho_cnes)}')
        WHERE NOME_UNIDADE IS NULL
           OR TRIM(CAST(NOME_UNIDADE AS VARCHAR)) = ''
           OR NOME_UNIDADE = '{VALOR_NAO_INFORMADO}';
    """).fetchone()[0]

    colunas_existentes = obter_colunas_parquet(con, caminho_cnes)

    con.close()

    colunas_faltantes = [
        coluna for coluna in colunas_obrigatorias
        if coluna not in colunas_existentes
    ]

    passou = (
        total_linhas > 0
        and len(colunas_faltantes) == 0
    )

    return dg.AssetCheckResult(
        passed=passou,
        metadata={
            "total_linhas_cnes_silver": int(total_linhas),
            "nomes_unidade_nao_informados": int(total_nome_nao_informado),
            "colunas_faltantes": str(colunas_faltantes),
        },
    )


# %%
@dg.asset_check(
    asset=dg.AssetKey("silver_sds"),
    description="Verifica se a base SDS Silver possui registros femininos, totais válidos e colunas tratadas."
)
def check_silver_sds_valido():
    """
    Valida a base SDS tratada.
    """

    caminho_sds = SDS_SILVER / "base_sds_tratada.parquet"

    if not caminho_sds.exists():
        return dg.AssetCheckResult(
            passed=False,
            metadata={
                "erro": "Arquivo Silver SDS não encontrado",
                "caminho": str(caminho_sds),
            },
        )

    colunas_obrigatorias = [
        "ID_SDS",
        "MUNICIPIO",
        "NATUREZA",
        "ANO",
        "SEXO",
        "FAIXA_ETARIA_SDS",
        "TOTAL_VITIMAS",
        "VIOL_FISIC",
        "VIOL_PSICO",
        "VIOL_SEXU",
        "VIOL_FINAN",
    ]

    con = duckdb.connect(":memory:")

    total_linhas = con.execute(f"""
        SELECT COUNT(*)
        FROM read_parquet('{caminho_sql(caminho_sds)}');
    """).fetchone()[0]

    total_sexo_diferente_f = con.execute(f"""
        SELECT COUNT(*)
        FROM read_parquet('{caminho_sql(caminho_sds)}')
        WHERE SEXO <> 'F';
    """).fetchone()[0]

    total_vitimas_invalidas = con.execute(f"""
        SELECT COUNT(*)
        FROM read_parquet('{caminho_sql(caminho_sds)}')
        WHERE TRY_CAST(TOTAL_VITIMAS AS BIGINT) IS NULL
           OR TRY_CAST(TOTAL_VITIMAS AS BIGINT) <= 0;
    """).fetchone()[0]

    total_faixa_nao_informada = con.execute(f"""
        SELECT COUNT(*)
        FROM read_parquet('{caminho_sql(caminho_sds)}')
        WHERE FAIXA_ETARIA_SDS = '{VALOR_NAO_INFORMADO}';
    """).fetchone()[0]

    colunas_existentes = obter_colunas_parquet(con, caminho_sds)

    con.close()

    colunas_faltantes = [
        coluna for coluna in colunas_obrigatorias
        if coluna not in colunas_existentes
    ]

    passou = (
        total_linhas > 0
        and total_sexo_diferente_f == 0
        and total_vitimas_invalidas == 0
        and len(colunas_faltantes) == 0
    )

    return dg.AssetCheckResult(
        passed=passou,
        metadata={
            "total_linhas_sds_silver": int(total_linhas),
            "linhas_sexo_diferente_f": int(total_sexo_diferente_f),
            "linhas_total_vitimas_invalidas": int(total_vitimas_invalidas),
            "linhas_faixa_etaria_nao_informada": int(total_faixa_nao_informada),
            "colunas_faltantes": str(colunas_faltantes),
        },
    )


# %%
@dg.asset_check(
    asset=dg.AssetKey("silver_sinan"),
    description="Verifica se a base SINAN Silver possui registros tratados, sexo feminino e colunas de cruzamento."
)
def check_silver_sinan_valido():
    """
    Valida a base SINAN tratada.
    """

    caminho_sinan = SINAN_SILVER / "base_sinan_tratada.parquet"

    if not caminho_sinan.exists():
        return dg.AssetCheckResult(
            passed=False,
            metadata={
                "erro": "Arquivo Silver SINAN não encontrado",
                "caminho": str(caminho_sinan),
            },
        )

    colunas_obrigatorias = [
        "ID_SINAN",
        "NU_ANO",
        "MUNICIPIO_OCORRENCIA",
        "SEXO",
        "IDADE_REAL",
        "IDADE_NUMERICA_EM_ANOS",
        "FAIXA_ETARIA_SDS",
        "VIOL_FISIC",
        "VIOL_PSICO",
        "VIOL_SEXU",
        "VIOL_FINAN",
    ]

    con = duckdb.connect(":memory:")

    total_linhas = con.execute(f"""
        SELECT COUNT(*)
        FROM read_parquet('{caminho_sql(caminho_sinan)}');
    """).fetchone()[0]

    total_sexo_diferente_f = con.execute(f"""
        SELECT COUNT(*)
        FROM read_parquet('{caminho_sql(caminho_sinan)}')
        WHERE SEXO <> 'F';
    """).fetchone()[0]

    total_idade_negativa = con.execute(f"""
        SELECT COUNT(*)
        FROM read_parquet('{caminho_sql(caminho_sinan)}')
        WHERE TRY_CAST(IDADE_NUMERICA_EM_ANOS AS BIGINT) < 0;
    """).fetchone()[0]

    total_faixa_nao_informada = con.execute(f"""
        SELECT COUNT(*)
        FROM read_parquet('{caminho_sql(caminho_sinan)}')
        WHERE FAIXA_ETARIA_SDS = '{VALOR_NAO_INFORMADO}';
    """).fetchone()[0]

    total_municipio_nao_informado = con.execute(f"""
        SELECT COUNT(*)
        FROM read_parquet('{caminho_sql(caminho_sinan)}')
        WHERE MUNICIPIO_OCORRENCIA = '{VALOR_NAO_INFORMADO}';
    """).fetchone()[0]

    colunas_existentes = obter_colunas_parquet(con, caminho_sinan)

    con.close()

    colunas_faltantes = [
        coluna for coluna in colunas_obrigatorias
        if coluna not in colunas_existentes
    ]

    passou = (
        total_linhas > 0
        and total_sexo_diferente_f == 0
        and total_idade_negativa == 0
        and len(colunas_faltantes) == 0
    )

    return dg.AssetCheckResult(
        passed=passou,
        metadata={
            "total_linhas_sinan_silver": int(total_linhas),
            "linhas_sexo_diferente_f": int(total_sexo_diferente_f),
            "linhas_idade_negativa": int(total_idade_negativa),
            "linhas_faixa_etaria_nao_informada": int(total_faixa_nao_informada),
            "linhas_municipio_ocorrencia_nao_informado": int(total_municipio_nao_informado),
            "colunas_faltantes": str(colunas_faltantes),
        },
    )


# ============================================================
# CHECKS GOLD
# ============================================================

# %%
@dg.asset_check(
    asset=dg.AssetKey("gold_sds_sinan"),
    description="Verifica se a base Gold foi gerada e possui linhas."
)
def check_gold_tem_linhas():
    """
    Confere se a base Gold existe e não está vazia.
    """

    caminho_gold = SDS_SINAN_GOLD / "sds_sinan_final.parquet"

    if not verificar_arquivo(caminho_gold):
        return dg.AssetCheckResult(
            passed=False,
            metadata={
                "erro": "Arquivo Gold não encontrado",
                "caminho": str(caminho_gold),
            },
        )

    con = duckdb.connect(":memory:")

    total_linhas = con.execute(f"""
        SELECT COUNT(*)
        FROM read_parquet('{caminho_sql(caminho_gold)}');
    """).fetchone()[0]

    con.close()

    return dg.AssetCheckResult(
        passed=total_linhas > 0,
        metadata={
            "total_linhas_gold": int(total_linhas),
            "arquivo": str(caminho_gold),
        },
    )


# %%
@dg.asset_check(
    asset=dg.AssetKey("gold_sds_sinan"),
    description="Verifica se as chaves principais da Gold não possuem nulos reais."
)
def check_gold_chaves_sem_nulos():
    """
    Confere se as chaves principais da Gold não possuem nulos reais.

    Observação:
    ANO é uma coluna numérica na Gold, então não deve ser comparada
    diretamente com o texto DADO NÃO INFORMADO.
    """

    caminho_gold = SDS_SINAN_GOLD / "sds_sinan_final.parquet"

    if not verificar_arquivo(caminho_gold):
        return dg.AssetCheckResult(
            passed=False,
            metadata={
                "erro": "Arquivo Gold não encontrado",
                "caminho": str(caminho_gold),
            },
        )

    con = duckdb.connect(":memory:")

    resultado = con.execute(f"""
        SELECT
            SUM(
                CASE
                    WHEN MUNICIPIO IS NULL
                      OR ANO IS NULL
                      OR SEXO IS NULL
                      OR FAIXA_ETARIA_SDS IS NULL
                      OR TRIM(CAST(MUNICIPIO AS VARCHAR)) = ''
                      OR TRIM(CAST(SEXO AS VARCHAR)) = ''
                      OR TRIM(CAST(FAIXA_ETARIA_SDS AS VARCHAR)) = ''
                    THEN 1
                    ELSE 0
                END
            ) AS total_chaves_nulas,

            SUM(
                CASE
                    WHEN CAST(MUNICIPIO AS VARCHAR) = '{VALOR_NAO_INFORMADO}'
                      OR CAST(SEXO AS VARCHAR) = '{VALOR_NAO_INFORMADO}'
                      OR CAST(FAIXA_ETARIA_SDS AS VARCHAR) = '{VALOR_NAO_INFORMADO}'
                    THEN 1
                    ELSE 0
                END
            ) AS total_chaves_nao_informadas
        FROM read_parquet('{caminho_sql(caminho_gold)}');
    """).fetchone()

    con.close()

    total_chaves_nulas = resultado[0] or 0
    total_chaves_nao_informadas = resultado[1] or 0

    return dg.AssetCheckResult(
        passed=total_chaves_nulas == 0,
        metadata={
            "total_chaves_nulas": int(total_chaves_nulas),
            "total_chaves_com_dado_nao_informado": int(total_chaves_nao_informadas),
        },
    )


# %%
@dg.asset_check(
    asset=dg.AssetKey("gold_sds_sinan"),
    description="Verifica se os totais principais da Gold não possuem valores negativos."
)
def check_gold_totais_nao_negativos():
    """
    Confere se os totais principais da Gold não possuem valores negativos.
    """

    caminho_gold = SDS_SINAN_GOLD / "sds_sinan_final.parquet"

    if not verificar_arquivo(caminho_gold):
        return dg.AssetCheckResult(
            passed=False,
            metadata={
                "erro": "Arquivo Gold não encontrado",
                "caminho": str(caminho_gold),
            },
        )

    con = duckdb.connect(":memory:")

    total_negativos = con.execute(f"""
        SELECT COUNT(*)
        FROM read_parquet('{caminho_sql(caminho_gold)}')
        WHERE TOTAL_REGISTROS_SINAN < 0
           OR TOTAL_REGISTROS_SDS < 0
           OR TOTAL_VITIMAS_SDS < 0;
    """).fetchone()[0]

    con.close()

    return dg.AssetCheckResult(
        passed=total_negativos == 0,
        metadata={
            "linhas_com_totais_negativos": int(total_negativos),
        },
    )


# %%
@dg.asset_check(
    asset=dg.AssetKey("gold_sds_sinan"),
    description="Verifica se os totais da Gold batem com as bases Silver."
)
def check_gold_totais_batem_com_silver():
    """
    Confere se os totais agregados da Gold batem com os totais das bases Silver.
    """

    caminho_gold = SDS_SINAN_GOLD / "sds_sinan_final.parquet"
    caminho_sinan = SINAN_SILVER / "base_sinan_tratada.parquet"
    caminho_sds = SDS_SILVER / "base_sds_tratada.parquet"

    arquivos = {
        "gold": caminho_gold,
        "sinan_silver": caminho_sinan,
        "sds_silver": caminho_sds,
    }

    for nome, caminho in arquivos.items():
        if not verificar_arquivo(caminho):
            return dg.AssetCheckResult(
                passed=False,
                metadata={
                    "erro": f"Arquivo não encontrado: {nome}",
                    "caminho": str(caminho),
                },
            )

    con = duckdb.connect(":memory:")

    total_sinan_silver = con.execute(f"""
        SELECT COUNT(*)
        FROM read_parquet('{caminho_sql(caminho_sinan)}');
    """).fetchone()[0]

    total_sds_registros_silver = con.execute(f"""
        SELECT COUNT(*)
        FROM read_parquet('{caminho_sql(caminho_sds)}');
    """).fetchone()[0]

    total_sds_vitimas_silver = con.execute(f"""
        SELECT COALESCE(SUM(TRY_CAST(TOTAL_VITIMAS AS BIGINT)), 0)
        FROM read_parquet('{caminho_sql(caminho_sds)}');
    """).fetchone()[0]

    totais_gold = con.execute(f"""
        SELECT
            COALESCE(SUM(TOTAL_REGISTROS_SINAN), 0) AS total_sinan_gold,
            COALESCE(SUM(TOTAL_REGISTROS_SDS), 0) AS total_sds_registros_gold,
            COALESCE(SUM(TOTAL_VITIMAS_SDS), 0) AS total_sds_vitimas_gold
        FROM read_parquet('{caminho_sql(caminho_gold)}');
    """).fetchone()

    con.close()

    total_sinan_gold = totais_gold[0]
    total_sds_registros_gold = totais_gold[1]
    total_sds_vitimas_gold = totais_gold[2]

    passou = (
        total_sinan_silver == total_sinan_gold
        and total_sds_registros_silver == total_sds_registros_gold
        and total_sds_vitimas_silver == total_sds_vitimas_gold
    )

    return dg.AssetCheckResult(
        passed=passou,
        metadata={
            "total_sinan_silver": int(total_sinan_silver),
            "total_sinan_gold": int(total_sinan_gold),
            "total_sds_registros_silver": int(total_sds_registros_silver),
            "total_sds_registros_gold": int(total_sds_registros_gold),
            "total_sds_vitimas_silver": int(total_sds_vitimas_silver),
            "total_sds_vitimas_gold": int(total_sds_vitimas_gold),
        },
    )


# ============================================================
# CHECKS DUCKDB
# ============================================================

# %%
@dg.asset_check(
    asset=dg.AssetKey("duckdb_warehouse"),
    description="Verifica se o banco DuckDB foi criado e contém as tabelas esperadas."
)
def check_duckdb_tabelas_existentes():
    """
    Confere se o banco DuckDB possui todas as tabelas esperadas.
    """

    if not verificar_arquivo(DUCKDB_PATH):
        return dg.AssetCheckResult(
            passed=False,
            metadata={
                "erro": "Banco DuckDB não encontrado",
                "caminho": str(DUCKDB_PATH),
            },
        )

    tabelas_esperadas = {
        ("bronze", "sinan"),
        ("bronze", "sds"),
        ("bronze", "ibge"),
        ("bronze", "cnes"),
        ("silver", "sinan"),
        ("silver", "sds"),
        ("silver", "ibge"),
        ("silver", "cnes"),
        ("gold", "sds_sinan"),
    }

    con = duckdb.connect(str(DUCKDB_PATH), read_only=True)

    tabelas_existentes = set(
        con.execute("""
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_schema IN ('bronze', 'silver', 'gold');
        """).fetchall()
    )

    con.close()

    tabelas_faltantes = sorted(tabelas_esperadas - tabelas_existentes)

    return dg.AssetCheckResult(
        passed=len(tabelas_faltantes) == 0,
        metadata={
            "total_tabelas_esperadas": len(tabelas_esperadas),
            "total_tabelas_encontradas": len(tabelas_existentes),
            "tabelas_faltantes": str(tabelas_faltantes),
        },
    )


# %%
@dg.asset_check(
    asset=dg.AssetKey("duckdb_warehouse"),
    description="Verifica se a tabela Gold no DuckDB bate com o arquivo Parquet Gold."
)
def check_duckdb_gold_bate_com_parquet():
    """
    Confere se a tabela gold.sds_sinan no DuckDB possui o mesmo total de linhas do Parquet Gold.
    """

    caminho_gold = SDS_SINAN_GOLD / "sds_sinan_final.parquet"

    if not verificar_arquivo(DUCKDB_PATH):
        return dg.AssetCheckResult(
            passed=False,
            metadata={
                "erro": "Banco DuckDB não encontrado",
                "caminho": str(DUCKDB_PATH),
            },
        )

    if not verificar_arquivo(caminho_gold):
        return dg.AssetCheckResult(
            passed=False,
            metadata={
                "erro": "Arquivo Gold Parquet não encontrado",
                "caminho": str(caminho_gold),
            },
        )

    con = duckdb.connect(str(DUCKDB_PATH), read_only=True)

    total_gold_duckdb = con.execute("""
        SELECT COUNT(*)
        FROM gold.sds_sinan;
    """).fetchone()[0]

    total_gold_parquet = con.execute(f"""
        SELECT COUNT(*)
        FROM read_parquet('{caminho_sql(caminho_gold)}');
    """).fetchone()[0]

    con.close()

    return dg.AssetCheckResult(
        passed=total_gold_duckdb == total_gold_parquet,
        metadata={
            "total_gold_duckdb": int(total_gold_duckdb),
            "total_gold_parquet": int(total_gold_parquet),
        },
    )