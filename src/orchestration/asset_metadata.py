# %%
# Importa Dagster
import dagster as dg


# ============================================================
# METADATA - SILVER SINAN
# ============================================================

SILVER_SINAN_METADATA = {
    "dagster/table_name": "silver.sinan",
    "camada": "silver",
    "descricao": (
        "Base SINAN tratada, filtrada para Pernambuco e sexo feminino, "
        "com códigos categóricos traduzidos, idade tratada, enriquecimento "
        "com IBGE/CNES e criação do recorte doméstico/familiar."
    ),
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
                "ESTADO_NOTIFICACAO",
                "VARCHAR",
                description="Unidade federativa onde a notificação foi registrada."
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
                "ANO_NASC",
                "BIGINT",
                description="Ano de nascimento da vítima, quando informado."
            ),
            dg.TableColumn(
                "CODIGO_IDADE",
                "VARCHAR",
                description="Código original de idade do SINAN. O primeiro dígito indica a unidade de tempo."
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
                "CS_RACA",
                "VARCHAR",
                description="Raça/cor da vítima após decodificação do código original do SINAN."
            ),
            dg.TableColumn(
                "ESCOLARIDADE",
                "VARCHAR",
                description="Escolaridade da vítima após decodificação do código original do SINAN."
            ),
            dg.TableColumn(
                "SG_UF",
                "VARCHAR",
                description="Unidade federativa de residência ou referência do registro, conforme campo original tratado."
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
                "LOCAL_OCOR",
                "VARCHAR",
                description="Local de ocorrência da violência após decodificação."
            ),
            dg.TableColumn(
                "RECORTE_DOMESTICO_FAMILIAR",
                "VARCHAR",
                description=(
                    "Indica se o registro foi classificado no recorte doméstico/familiar. "
                    "O recorte considera local residencial e/ou vínculo familiar, afetivo ou de cuidado."
                )
            ),
            dg.TableColumn(
                "ORIENT_SEX",
                "VARCHAR",
                description="Orientação sexual da vítima, quando informada."
            ),
            dg.TableColumn(
                "IDENT_GEN",
                "VARCHAR",
                description="Identidade de gênero da vítima, quando informada."
            ),
            dg.TableColumn(
                "DEF_TRANS",
                "VARCHAR",
                description="Indicador de transtorno ou deficiência conforme campo tratado do SINAN."
            ),
            dg.TableColumn(
                "DEF_FISICA",
                "VARCHAR",
                description="Indicador de deficiência física."
            ),
            dg.TableColumn(
                "DEF_MENTAL",
                "VARCHAR",
                description="Indicador de deficiência intelectual ou mental."
            ),
            dg.TableColumn(
                "DEF_VISUAL",
                "VARCHAR",
                description="Indicador de deficiência visual."
            ),
            dg.TableColumn(
                "DEF_AUDITI",
                "VARCHAR",
                description="Indicador de deficiência auditiva."
            ),
            dg.TableColumn(
                "TRAN_MENT",
                "VARCHAR",
                description="Indicador de transtorno mental."
            ),
            dg.TableColumn(
                "VIOL_MOTIV",
                "VARCHAR",
                description="Motivação da violência após decodificação."
            ),
            dg.TableColumn(
                "VIOL_FISIC",
                "VARCHAR",
                description="Indicador de violência física."
            ),
            dg.TableColumn(
                "VIOL_PSICO",
                "VARCHAR",
                description="Indicador de violência psicológica ou moral."
            ),
            dg.TableColumn(
                "VIOL_TORT",
                "VARCHAR",
                description="Indicador de tortura."
            ),
            dg.TableColumn(
                "VIOL_SEXU",
                "VARCHAR",
                description="Indicador de violência sexual."
            ),
            dg.TableColumn(
                "VIOL_TRAF",
                "VARCHAR",
                description="Indicador de tráfico de seres humanos."
            ),
            dg.TableColumn(
                "VIOL_FINAN",
                "VARCHAR",
                description="Indicador de violência financeira, econômica ou patrimonial."
            ),
            dg.TableColumn(
                "VIOL_NEGLI",
                "VARCHAR",
                description="Indicador de negligência ou abandono."
            ),
            dg.TableColumn(
                "VIOL_INFAN",
                "VARCHAR",
                description="Indicador de violência relacionada à intervenção legal ou outra categoria tratada conforme dicionário do SINAN."
            ),
            dg.TableColumn(
                "AG_FORCA",
                "VARCHAR",
                description="Indicador de agressão por força corporal ou espancamento."
            ),
            dg.TableColumn(
                "AG_ENFOR",
                "VARCHAR",
                description="Indicador de agressão por enforcamento."
            ),
            dg.TableColumn(
                "AG_OBJETO",
                "VARCHAR",
                description="Indicador de agressão com objeto contundente."
            ),
            dg.TableColumn(
                "AG_CORTE",
                "VARCHAR",
                description="Indicador de agressão com objeto perfurocortante."
            ),
            dg.TableColumn(
                "AG_QUENTE",
                "VARCHAR",
                description="Indicador de agressão por substância ou objeto quente."
            ),
            dg.TableColumn(
                "AG_ENVEN",
                "VARCHAR",
                description="Indicador de agressão por envenenamento ou intoxicação."
            ),
            dg.TableColumn(
                "AG_FOGO",
                "VARCHAR",
                description="Indicador de agressão por arma de fogo."
            ),
            dg.TableColumn(
                "AG_AMEACA",
                "VARCHAR",
                description="Indicador de ameaça."
            ),
            dg.TableColumn(
                "SEX_ASSEDI",
                "VARCHAR",
                description="Indicador de assédio sexual."
            ),
            dg.TableColumn(
                "SEX_ESTUPR",
                "VARCHAR",
                description="Indicador de estupro."
            ),
            dg.TableColumn(
                "SEX_PORNO",
                "VARCHAR",
                description="Indicador de pornografia infantil ou exploração sexual relacionada ao campo tratado."
            ),
            dg.TableColumn(
                "SEX_EXPLO",
                "VARCHAR",
                description="Indicador de exploração sexual."
            ),
            dg.TableColumn(
                "NUM_ENVOLV",
                "VARCHAR",
                description="Número de prováveis autores envolvidos, conforme registro tratado."
            ),
            dg.TableColumn(
                "AUTOR_SEXO",
                "VARCHAR",
                description="Sexo do provável autor da agressão."
            ),
            dg.TableColumn(
                "CICL_VID",
                "VARCHAR",
                description="Ciclo de vida da vítima conforme classificação tratada."
            ),
            dg.TableColumn(
                "REL_PAI",
                "VARCHAR",
                description="Indicador de vínculo do provável autor como pai."
            ),
            dg.TableColumn(
                "REL_MAE",
                "VARCHAR",
                description="Indicador de vínculo do provável autor como mãe."
            ),
            dg.TableColumn(
                "REL_PAD",
                "VARCHAR",
                description="Indicador de vínculo do provável autor como padrasto."
            ),
            dg.TableColumn(
                "REL_MAD",
                "VARCHAR",
                description="Indicador de vínculo do provável autor como madrasta."
            ),
            dg.TableColumn(
                "REL_CONJ",
                "VARCHAR",
                description="Indicador de vínculo do provável autor como cônjuge."
            ),
            dg.TableColumn(
                "REL_EXCON",
                "VARCHAR",
                description="Indicador de vínculo do provável autor como ex-cônjuge."
            ),
            dg.TableColumn(
                "REL_NAMO",
                "VARCHAR",
                description="Indicador de vínculo do provável autor como namorado."
            ),
            dg.TableColumn(
                "REL_EXNAM",
                "VARCHAR",
                description="Indicador de vínculo do provável autor como ex-namorado."
            ),
            dg.TableColumn(
                "REL_IRMAO",
                "VARCHAR",
                description="Indicador de vínculo do provável autor como irmão ou irmã."
            ),
            dg.TableColumn(
                "REL_FILHO",
                "VARCHAR",
                description="Indicador de vínculo do provável autor como filho ou filha."
            ),
            dg.TableColumn(
                "REL_CONHEC",
                "VARCHAR",
                description="Indicador de vínculo do provável autor como conhecido."
            ),
            dg.TableColumn(
                "REL_DESCO",
                "VARCHAR",
                description="Indicador de provável autor desconhecido."
            ),
            dg.TableColumn(
                "REL_PATRAO",
                "VARCHAR",
                description="Indicador de vínculo do provável autor como patrão ou chefe."
            ),
            dg.TableColumn(
                "REL_INST",
                "VARCHAR",
                description="Indicador de relação institucional com o provável autor."
            ),
            dg.TableColumn(
                "REL_POL",
                "VARCHAR",
                description="Indicador de provável autor policial ou agente da lei, conforme campo tratado."
            ),
            dg.TableColumn(
                "ENC_SAUDE",
                "VARCHAR",
                description="Indicador de encaminhamento para a rede de saúde."
            ),
            dg.TableColumn(
                "ASSIST_SOC",
                "VARCHAR",
                description="Indicador de encaminhamento para assistência social."
            ),
            dg.TableColumn(
                "REDE_EDUCA",
                "VARCHAR",
                description="Indicador de encaminhamento para a rede de educação."
            ),
            dg.TableColumn(
                "ATEND_MULH",
                "VARCHAR",
                description="Indicador de encaminhamento para atendimento à mulher."
            ),
            dg.TableColumn(
                "CONS_TUTEL",
                "VARCHAR",
                description="Indicador de encaminhamento ao Conselho Tutelar."
            ),
            dg.TableColumn(
                "CONS_IDO",
                "VARCHAR",
                description="Indicador de encaminhamento ao Conselho do Idoso."
            ),
            dg.TableColumn(
                "DIR_HUMAN",
                "VARCHAR",
                description="Indicador de encaminhamento para órgãos de direitos humanos."
            ),
            dg.TableColumn(
                "MPU",
                "VARCHAR",
                description="Indicador de encaminhamento ao Ministério Público."
            ),
            dg.TableColumn(
                "DELEG_CRIA",
                "VARCHAR",
                description="Indicador de encaminhamento à delegacia de proteção à criança ou adolescente."
            ),
            dg.TableColumn(
                "DELEG_MULH",
                "VARCHAR",
                description="Indicador de encaminhamento à Delegacia da Mulher."
            ),
            dg.TableColumn(
                "INFAN_JUV",
                "VARCHAR",
                description="Indicador de encaminhamento para serviço ou órgão da infância e juventude."
            ),
            dg.TableColumn(
                "DEFEN_PUBL",
                "VARCHAR",
                description="Indicador de encaminhamento à Defensoria Pública."
            ),
            dg.TableColumn(
                "DELEG_IDOS",
                "VARCHAR",
                description="Indicador de encaminhamento à delegacia ou serviço de proteção ao idoso."
            ),
            dg.TableColumn(
                "REL_TRAB",
                "VARCHAR",
                description="Indicador de vínculo ou relação de trabalho com o provável autor."
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
    "descricao": (
        "Base SDS tratada e compatibilizada com as colunas principais do SINAN, "
        "com padronização de município, ano, sexo, faixa etária, total de vítimas "
        "e indicadores derivados da natureza da ocorrência."
    ),
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
                "VIOL_TORT",
                "VARCHAR",
                description="Indicador de tortura criado a partir da coluna NATUREZA."
            ),
            dg.TableColumn(
                "VIOL_SEXU",
                "VARCHAR",
                description="Indicador de violência sexual criado a partir da coluna NATUREZA."
            ),
            dg.TableColumn(
                "VIOL_TRAF",
                "VARCHAR",
                description="Indicador de tráfico de seres humanos criado a partir da coluna NATUREZA."
            ),
            dg.TableColumn(
                "VIOL_FINAN",
                "VARCHAR",
                description="Indicador de violência financeira/patrimonial criado a partir da coluna NATUREZA."
            ),
            dg.TableColumn(
                "VIOL_NEGLI",
                "VARCHAR",
                description="Indicador de negligência/abandono criado a partir da coluna NATUREZA."
            ),
            dg.TableColumn(
                "VIOL_INFAN",
                "VARCHAR",
                description="Indicador de violência relacionada à variável tratada VIOL_INFAN criado a partir da coluna NATUREZA."
            ),
            dg.TableColumn(
                "AG_FORCA",
                "VARCHAR",
                description="Indicador de agressão por força corporal ou espancamento criado a partir da coluna NATUREZA."
            ),
            dg.TableColumn(
                "AG_ENFOR",
                "VARCHAR",
                description="Indicador de agressão por enforcamento criado a partir da coluna NATUREZA."
            ),
            dg.TableColumn(
                "AG_OBJETO",
                "VARCHAR",
                description="Indicador de agressão com objeto contundente criado a partir da coluna NATUREZA."
            ),
            dg.TableColumn(
                "AG_CORTE",
                "VARCHAR",
                description="Indicador de agressão com objeto perfurocortante criado a partir da coluna NATUREZA."
            ),
            dg.TableColumn(
                "AG_QUENTE",
                "VARCHAR",
                description="Indicador de agressão por substância ou objeto quente criado a partir da coluna NATUREZA."
            ),
            dg.TableColumn(
                "AG_ENVEN",
                "VARCHAR",
                description="Indicador de agressão por envenenamento ou intoxicação criado a partir da coluna NATUREZA."
            ),
            dg.TableColumn(
                "AG_FOGO",
                "VARCHAR",
                description="Indicador de agressão por arma de fogo criado a partir da coluna NATUREZA."
            ),
            dg.TableColumn(
                "AG_AMEACA",
                "VARCHAR",
                description="Indicador de ameaça criado a partir da coluna NATUREZA."
            ),
            dg.TableColumn(
                "SEX_ASSEDI",
                "VARCHAR",
                description="Indicador de assédio sexual criado a partir da coluna NATUREZA."
            ),
            dg.TableColumn(
                "SEX_ESTUPR",
                "VARCHAR",
                description="Indicador de estupro criado a partir da coluna NATUREZA."
            ),
            dg.TableColumn(
                "SEX_PORNO",
                "VARCHAR",
                description="Indicador relacionado à pornografia ou exploração sexual criado a partir da coluna NATUREZA."
            ),
            dg.TableColumn(
                "SEX_EXPLO",
                "VARCHAR",
                description="Indicador de exploração sexual criado a partir da coluna NATUREZA."
            ),
        ]
    ),
}


# ============================================================
# METADATA - SILVER IBGE
# ============================================================

SILVER_IBGE_METADATA = {
    "dagster/table_name": "silver.ibge",
    "camada": "silver",
    "descricao": "Base auxiliar do IBGE tratada, contendo códigos e nomes dos municípios de Pernambuco.",
    "dagster/column_schema": dg.TableSchema(
        columns=[
            dg.TableColumn(
                "codigo_uf",
                "BIGINT",
                description="Código da unidade federativa segundo o IBGE."
            ),
            dg.TableColumn(
                "codigo_ibge",
                "BIGINT",
                description="Código completo do município segundo o IBGE."
            ),
            dg.TableColumn(
                "ID_MUNICIP_SINAN",
                "VARCHAR",
                description="Código municipal compatibilizado para cruzamento com o SINAN."
            ),
            dg.TableColumn(
                "NOME_MUNICIPIO",
                "VARCHAR",
                description="Nome oficial do município segundo o IBGE."
            ),
        ]
    ),
}


# ============================================================
# METADATA - SILVER CNES
# ============================================================

SILVER_CNES_METADATA = {
    "dagster/table_name": "silver.cnes",
    "camada": "silver",
    "descricao": "Base auxiliar do CNES tratada, contendo estabelecimentos de saúde de Pernambuco.",
    "dagster/column_schema": dg.TableSchema(
        columns=[
            dg.TableColumn(
                "ID_UNIDADE",
                "VARCHAR",
                description="Identificador da unidade de saúde compatibilizado para cruzamento com o SINAN."
            ),
            dg.TableColumn(
                "NOME_UNIDADE",
                "VARCHAR",
                description="Nome fantasia da unidade de saúde."
            ),
            dg.TableColumn(
                "CO_CNES",
                "VARCHAR",
                description="Código CNES do estabelecimento de saúde."
            ),
            dg.TableColumn(
                "CO_UNIDADE",
                "VARCHAR",
                description="Código da unidade de saúde conforme cadastro original."
            ),
            dg.TableColumn(
                "CO_UF",
                "VARCHAR",
                description="Código da unidade federativa."
            ),
            dg.TableColumn(
                "CO_IBGE",
                "VARCHAR",
                description="Código IBGE do município da unidade de saúde."
            ),
            dg.TableColumn(
                "TP_UNIDADE",
                "VARCHAR",
                description="Tipo da unidade de saúde conforme classificação do CNES."
            ),
            dg.TableColumn(
                "NO_RAZAO_SOCIAL",
                "VARCHAR",
                description="Razão social do estabelecimento de saúde."
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
    "descricao": (
        "Base final agregada que cruza registros do SINAN com registros da SDS "
        "por município, ano, sexo e faixa etária."
    ),
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
                "SINAN_VIOL_PSICO",
                "BIGINT",
                description="Total de registros do SINAN classificados como violência psicológica."
            ),
            dg.TableColumn(
                "SINAN_VIOL_TORT",
                "BIGINT",
                description="Total de registros do SINAN classificados como tortura."
            ),
            dg.TableColumn(
                "SINAN_VIOL_SEXU",
                "BIGINT",
                description="Total de registros do SINAN classificados como violência sexual."
            ),
            dg.TableColumn(
                "SINAN_VIOL_TRAF",
                "BIGINT",
                description="Total de registros do SINAN classificados como tráfico de seres humanos."
            ),
            dg.TableColumn(
                "SINAN_VIOL_FINAN",
                "BIGINT",
                description="Total de registros do SINAN classificados como violência financeira/patrimonial."
            ),
            dg.TableColumn(
                "SINAN_VIOL_NEGLI",
                "BIGINT",
                description="Total de registros do SINAN classificados como negligência ou abandono."
            ),
            dg.TableColumn(
                "SINAN_VIOL_INFAN",
                "BIGINT",
                description="Total de registros do SINAN classificados conforme a variável tratada VIOL_INFAN."
            ),
            dg.TableColumn(
                "SINAN_AG_FORCA",
                "BIGINT",
                description="Total de registros do SINAN com agressão por força corporal ou espancamento."
            ),
            dg.TableColumn(
                "SINAN_AG_ENFOR",
                "BIGINT",
                description="Total de registros do SINAN com agressão por enforcamento."
            ),
            dg.TableColumn(
                "SINAN_AG_OBJETO",
                "BIGINT",
                description="Total de registros do SINAN com agressão por objeto contundente."
            ),
            dg.TableColumn(
                "SINAN_AG_CORTE",
                "BIGINT",
                description="Total de registros do SINAN com agressão por objeto perfurocortante."
            ),
            dg.TableColumn(
                "SINAN_AG_QUENTE",
                "BIGINT",
                description="Total de registros do SINAN com agressão por substância ou objeto quente."
            ),
            dg.TableColumn(
                "SINAN_AG_ENVEN",
                "BIGINT",
                description="Total de registros do SINAN com agressão por envenenamento ou intoxicação."
            ),
            dg.TableColumn(
                "SINAN_AG_FOGO",
                "BIGINT",
                description="Total de registros do SINAN com agressão por arma de fogo."
            ),
            dg.TableColumn(
                "SINAN_AG_AMEACA",
                "BIGINT",
                description="Total de registros do SINAN com ameaça."
            ),
            dg.TableColumn(
                "SINAN_SEX_ASSEDI",
                "BIGINT",
                description="Total de registros do SINAN com assédio sexual."
            ),
            dg.TableColumn(
                "SINAN_SEX_ESTUPR",
                "BIGINT",
                description="Total de registros do SINAN com estupro."
            ),
            dg.TableColumn(
                "SINAN_SEX_PORNO",
                "BIGINT",
                description="Total de registros do SINAN relacionados à pornografia ou exploração sexual conforme campo tratado."
            ),
            dg.TableColumn(
                "SINAN_SEX_EXPLO",
                "BIGINT",
                description="Total de registros do SINAN com exploração sexual."
            ),
            dg.TableColumn(
                "SDS_VIOL_FISIC",
                "BIGINT",
                description="Total de vítimas da SDS associadas à violência física."
            ),
            dg.TableColumn(
                "SDS_VIOL_PSICO",
                "BIGINT",
                description="Total de vítimas da SDS associadas à violência psicológica."
            ),
            dg.TableColumn(
                "SDS_VIOL_TORT",
                "BIGINT",
                description="Total de vítimas da SDS associadas à tortura."
            ),
            dg.TableColumn(
                "SDS_VIOL_SEXU",
                "BIGINT",
                description="Total de vítimas da SDS associadas à violência sexual."
            ),
            dg.TableColumn(
                "SDS_VIOL_TRAF",
                "BIGINT",
                description="Total de vítimas da SDS associadas ao tráfico de seres humanos."
            ),
            dg.TableColumn(
                "SDS_VIOL_FINAN",
                "BIGINT",
                description="Total de vítimas da SDS associadas à violência financeira/patrimonial."
            ),
            dg.TableColumn(
                "SDS_VIOL_NEGLI",
                "BIGINT",
                description="Total de vítimas da SDS associadas à negligência ou abandono."
            ),
            dg.TableColumn(
                "SDS_VIOL_INFAN",
                "BIGINT",
                description="Total de vítimas da SDS associadas à variável tratada VIOL_INFAN."
            ),
            dg.TableColumn(
                "SDS_AG_FORCA",
                "BIGINT",
                description="Total de vítimas da SDS associadas à agressão por força corporal ou espancamento."
            ),
            dg.TableColumn(
                "SDS_AG_ENFOR",
                "BIGINT",
                description="Total de vítimas da SDS associadas à agressão por enforcamento."
            ),
            dg.TableColumn(
                "SDS_AG_OBJETO",
                "BIGINT",
                description="Total de vítimas da SDS associadas à agressão por objeto contundente."
            ),
            dg.TableColumn(
                "SDS_AG_CORTE",
                "BIGINT",
                description="Total de vítimas da SDS associadas à agressão por objeto perfurocortante."
            ),
            dg.TableColumn(
                "SDS_AG_QUENTE",
                "BIGINT",
                description="Total de vítimas da SDS associadas à agressão por substância ou objeto quente."
            ),
            dg.TableColumn(
                "SDS_AG_ENVEN",
                "BIGINT",
                description="Total de vítimas da SDS associadas à agressão por envenenamento ou intoxicação."
            ),
            dg.TableColumn(
                "SDS_AG_FOGO",
                "BIGINT",
                description="Total de vítimas da SDS associadas à agressão por arma de fogo."
            ),
            dg.TableColumn(
                "SDS_AG_AMEACA",
                "BIGINT",
                description="Total de vítimas da SDS associadas à ameaça."
            ),
            dg.TableColumn(
                "SDS_SEX_ASSEDI",
                "BIGINT",
                description="Total de vítimas da SDS associadas ao assédio sexual."
            ),
            dg.TableColumn(
                "SDS_SEX_ESTUPR",
                "BIGINT",
                description="Total de vítimas da SDS associadas ao estupro."
            ),
            dg.TableColumn(
                "SDS_SEX_PORNO",
                "BIGINT",
                description="Total de vítimas da SDS associadas à pornografia."
            ),
            dg.TableColumn(
                "SDS_SEX_EXPLO",
                "BIGINT",
                description="Total de vítimas da SDS associadas à exploração sexual."
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
