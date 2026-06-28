# %%
# Importa Dagster
import dagster as dg


# ============================================================
# METADATA - SILVER SINAN
# ============================================================

SILVER_SINAN_METADATA = {
    "dagster/table_name": "silver.sinan",
    "camada": "silver",
    "descricao": "Base SINAN tratada, filtrada para Pernambuco e sexo feminino.",
    "dagster/column_schema": dg.TableSchema(
        columns=[
            dg.TableColumn(
                "ID_SINAN",
                "BIGINT",
                description="Identificador único criado para cada registro tratado do SINAN."
            ),
            dg.TableColumn(
                "DT_NOTIFIC",
                "VARCHAR",
                description="Data de notificação do caso."
            ),
            dg.TableColumn(
                "NU_ANO",
                "BIGINT",
                description="Ano do registro do SINAN."
            ),
            dg.TableColumn(
                "MUNICIPIO_NOTIFICACAO",
                "VARCHAR",
                description="Município onde a notificação foi registrada."
            ),
            dg.TableColumn(
                "NOME_UNIDADE",
                "VARCHAR",
                description="Nome da unidade de saúde, obtido a partir da base CNES."
            ),
            dg.TableColumn(
                "DT_OCOR",
                "VARCHAR",
                description="Data de ocorrência do fato."
            ),
            dg.TableColumn(
                "IDADE_REAL",
                "VARCHAR",
                description="Idade interpretada a partir do código original do SINAN."
            ),
            dg.TableColumn(
                "IDADE_NUMERICA_EM_ANOS",
                "BIGINT",
                description="Idade convertida para anos. Horas, dias e meses são representados como 0."
            ),
            dg.TableColumn(
                "FAIXA_ETARIA_SDS",
                "VARCHAR",
                description="Faixa etária compatível com a classificação utilizada pela SDS."
            ),
            dg.TableColumn(
                "SEXO",
                "VARCHAR",
                description="Sexo da vítima. Nesta base, esperado como F."
            ),
            dg.TableColumn(
                "MUNICIPIO_RESIDENCIA",
                "VARCHAR",
                description="Município de residência da vítima."
            ),
            dg.TableColumn(
                "MUNICIPIO_OCORRENCIA",
                "VARCHAR",
                description="Município onde ocorreu o fato."
            ),
            dg.TableColumn(
                "VIOL_FISIC",
                "VARCHAR",
                description="Indicador de violência física. Valores esperados: SIM, NAO, IGNORADO, NAO SE APLICA ou DADO NÃO INFORMADO."
            ),
            dg.TableColumn(
                "VIOL_PSICO",
                "VARCHAR",
                description="Indicador de violência psicológica."
            ),
            dg.TableColumn(
                "VIOL_SEXU",
                "VARCHAR",
                description="Indicador de violência sexual."
            ),
            dg.TableColumn(
                "VIOL_FINAN",
                "VARCHAR",
                description="Indicador de violência financeira ou patrimonial."
            ),
        ]
    ),
}


# ============================================================
# METADATA - SILVER SDS
# ============================================================

SILVER_SDS_METADATA = {
    "dagster/table_name": "silver.sds",
    "camada": "silver",
    "descricao": "Base SDS tratada e compatibilizada com as colunas principais do SINAN.",
    "dagster/column_schema": dg.TableSchema(
        columns=[
            dg.TableColumn(
                "ID_SDS",
                "BIGINT",
                description="Identificador único criado para cada registro tratado da SDS."
            ),
            dg.TableColumn(
                "MUNICIPIO",
                "VARCHAR",
                description="Município do fato, padronizado para cruzamento."
            ),
            dg.TableColumn(
                "REGIAO_GEOGRAFICA",
                "VARCHAR",
                description="Região geográfica do município."
            ),
            dg.TableColumn(
                "NATUREZA",
                "VARCHAR",
                description="Natureza do registro policial/administrativo."
            ),
            dg.TableColumn(
                "DATA_FATO",
                "VARCHAR",
                description="Data do fato."
            ),
            dg.TableColumn(
                "ANO",
                "BIGINT",
                description="Ano do fato."
            ),
            dg.TableColumn(
                "SEXO",
                "VARCHAR",
                description="Sexo da vítima. Nesta base tratada, esperado como F."
            ),
            dg.TableColumn(
                "FAIXA_ETARIA_SDS",
                "VARCHAR",
                description="Faixa etária original da SDS, padronizada."
            ),
            dg.TableColumn(
                "TOTAL_VITIMAS",
                "BIGINT",
                description="Total de vítimas representadas pelo registro."
            ),
            dg.TableColumn(
                "VIOL_FISIC",
                "VARCHAR",
                description="Indicador de violência física criado a partir da coluna NATUREZA."
            ),
            dg.TableColumn(
                "VIOL_PSICO",
                "VARCHAR",
                description="Indicador de violência psicológica criado a partir da coluna NATUREZA."
            ),
            dg.TableColumn(
                "VIOL_SEXU",
                "VARCHAR",
                description="Indicador de violência sexual criado a partir da coluna NATUREZA."
            ),
            dg.TableColumn(
                "VIOL_FINAN",
                "VARCHAR",
                description="Indicador de violência financeira/patrimonial criado a partir da coluna NATUREZA."
            ),
        ]
    ),
}


# ============================================================
# METADATA - GOLD SDS + SINAN
# ============================================================

GOLD_SDS_SINAN_METADATA = {
    "dagster/table_name": "gold.sds_sinan",
    "camada": "gold",
    "descricao": "Base final agregada que cruza registros do SINAN com registros da SDS por município, ano, sexo e faixa etária.",
    "dagster/column_schema": dg.TableSchema(
        columns=[
            dg.TableColumn(
                "MUNICIPIO",
                "VARCHAR",
                description="Município usado como chave de cruzamento entre SDS e SINAN."
            ),
            dg.TableColumn(
                "REGIAO_GEOGRAFICA",
                "VARCHAR",
                description="Região geográfica do município, quando disponível na SDS."
            ),
            dg.TableColumn(
                "ANO",
                "BIGINT",
                description="Ano de referência da agregação."
            ),
            dg.TableColumn(
                "SEXO",
                "VARCHAR",
                description="Sexo padronizado. Esperado: F."
            ),
            dg.TableColumn(
                "FAIXA_ETARIA_SDS",
                "VARCHAR",
                description="Faixa etária padronizada para cruzamento entre SDS e SINAN."
            ),
            dg.TableColumn(
                "TOTAL_REGISTROS_SINAN",
                "BIGINT",
                description="Total de registros do SINAN agregados na chave."
            ),
            dg.TableColumn(
                "TOTAL_REGISTROS_SDS",
                "BIGINT",
                description="Total de registros da SDS agregados na chave."
            ),
            dg.TableColumn(
                "TOTAL_VITIMAS_SDS",
                "BIGINT",
                description="Total de vítimas da SDS agregadas na chave."
            ),
            dg.TableColumn(
                "DIF_TOTAL_SDS_MENOS_SINAN",
                "BIGINT",
                description="Diferença entre o total de vítimas da SDS e o total de registros do SINAN."
            ),
            dg.TableColumn(
                "SINAN_VIOL_FISIC",
                "BIGINT",
                description="Total de registros do SINAN classificados como violência física."
            ),
            dg.TableColumn(
                "SDS_VIOL_FISIC",
                "BIGINT",
                description="Total de vítimas da SDS associadas à violência física."
            ),
            dg.TableColumn(
                "SINAN_VIOL_PSICO",
                "BIGINT",
                description="Total de registros do SINAN classificados como violência psicológica."
            ),
            dg.TableColumn(
                "SDS_VIOL_PSICO",
                "BIGINT",
                description="Total de vítimas da SDS associadas à violência psicológica."
            ),
            dg.TableColumn(
                "SINAN_VIOL_SEXU",
                "BIGINT",
                description="Total de registros do SINAN classificados como violência sexual."
            ),
            dg.TableColumn(
                "SDS_VIOL_SEXU",
                "BIGINT",
                description="Total de vítimas da SDS associadas à violência sexual."
            ),
            dg.TableColumn(
                "SINAN_VIOL_FINAN",
                "BIGINT",
                description="Total de registros do SINAN classificados como violência financeira/patrimonial."
            ),
            dg.TableColumn(
                "SDS_VIOL_FINAN",
                "BIGINT",
                description="Total de vítimas da SDS associadas à violência financeira/patrimonial."
            ),
        ]
    ),
}


# ============================================================
# METADATA - DUCKDB
# ============================================================

DUCKDB_WAREHOUSE_METADATA = {
    "dagster/table_name": "data/warehouse/sinan_sds.duckdb",
    "camada": "warehouse",
    "descricao": "Banco DuckDB local contendo as tabelas Bronze, Silver e Gold do projeto.",
}