# %%
# Importa sys para ajustar imports quando rodar por célula no VS Code
import sys

# Importa Path para manipular caminhos de arquivos
from pathlib import Path

# Importa pandas para manipulação dos dados
import pandas as pd


# %%
def encontrar_raiz_projeto():
    """
    Localiza a raiz do projeto procurando pela pasta src/config.py.
    """

    # Começa a busca a partir da pasta atual
    caminho_atual = Path.cwd().resolve()

    # Percorre a pasta atual e as pastas superiores
    for pasta in [caminho_atual, *caminho_atual.parents]:

        # Verifica se encontrou o arquivo de configuração
        if (pasta / "src" / "config.py").exists():
            return pasta

    # Interrompe se a raiz não for encontrada
    raise FileNotFoundError("Não foi possível encontrar a raiz do projeto com src/config.py")


# Encontra a raiz do projeto
ROOT_DIR = encontrar_raiz_projeto()

# Adiciona a raiz ao path para permitir imports do pacote src
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))


# %%
# Importa os caminhos padronizados do projeto
from src.config import SINAN_SILVER, SDS_SILVER, SDS_SINAN_GOLD


# %%
# Valor padrão usado para células sem informação útil
VALOR_NAO_INFORMADO = "DADO NÃO INFORMADO"

# Colunas de indicadores equivalentes entre SINAN e SDS
COLUNAS_INDICADORES = [
    "VIOL_FISIC",
    "VIOL_PSICO",
    "VIOL_TORT",
    "VIOL_SEXU",
    "VIOL_TRAF",
    "VIOL_FINAN",
    "VIOL_NEGLI",
    "VIOL_INFAN",
    "AG_FORCA",
    "AG_ENFOR",
    "AG_OBJETO",
    "AG_CORTE",
    "AG_QUENTE",
    "AG_ENVEN",
    "AG_FOGO",
    "AG_AMEACA",
    "SEX_ASSEDI",
    "SEX_ESTUPR",
    "SEX_PORNO",
    "SEX_EXPLO",
]


# %%
def normalizar_chave(valor):
    """
    Padroniza valores usados como chave de cruzamento.
    """

    # Trata nulos reais
    if pd.isna(valor):
        return VALOR_NAO_INFORMADO

    # Converte para texto e remove espaços
    texto = str(valor).strip().upper()

    # Trata valores inválidos
    if texto in ["", "NAN", "NONE", "NULL", "NAT", "<NA>"]:
        return VALOR_NAO_INFORMADO

    # Retorna texto padronizado
    return texto


# %%
def preparar_indicador_sim_nao(df, coluna):
    """
    Converte indicador SIM/NAO em 1/0.
    """

    # Se a coluna não existir, cria como zero
    if coluna not in df.columns:
        return pd.Series(0, index=df.index)

    # Padroniza valores e marca SIM como 1
    return (
        df[coluna]
        .astype(str)
        .str.upper()
        .str.strip()
        .eq("SIM")
        .astype(int)
    )


# %%
def carregar_bases_silver():
    """
    Carrega as bases SINAN e SDS tratadas na camada silver.
    """

    # Caminho da base SINAN tratada
    caminho_sinan = SINAN_SILVER / "base_sinan_tratada.parquet"

    # Caminho da base SDS tratada
    caminho_sds = SDS_SILVER / "base_sds_tratada.parquet"

    # Verifica se o SINAN existe
    if not caminho_sinan.exists():
        raise FileNotFoundError(f"Base SINAN tratada não encontrada: {caminho_sinan}")

    # Verifica se a SDS existe
    if not caminho_sds.exists():
        raise FileNotFoundError(f"Base SDS tratada não encontrada: {caminho_sds}")

    # Lê SINAN
    df_sinan = pd.read_parquet(caminho_sinan)

    # Lê SDS
    df_sds = pd.read_parquet(caminho_sds)

    # Exibe tamanhos
    print(f"SINAN silver: {df_sinan.shape[0]} linhas e {df_sinan.shape[1]} colunas.", flush=True)
    print(f"SDS silver: {df_sds.shape[0]} linhas e {df_sds.shape[1]} colunas.", flush=True)

    # Retorna as bases
    return df_sinan, df_sds


# %%
def preparar_sinan_para_gold(df_sinan):
    """
    Prepara e agrega a base SINAN para cruzamento com SDS.
    """

    # Define colunas necessárias
    colunas_necessarias = [
        "ID_SINAN",
        "MUNICIPIO_OCORRENCIA",
        "NU_ANO",
        "SEXO",
        "FAIXA_ETARIA_SDS",
    ]

    # Verifica colunas ausentes
    colunas_ausentes = [
        coluna for coluna in colunas_necessarias
        if coluna not in df_sinan.columns
    ]

    # Interrompe se faltar alguma coluna
    if colunas_ausentes:
        raise ValueError(f"Colunas ausentes no SINAN silver: {colunas_ausentes}")

    # Cria base auxiliar
    df = df_sinan.copy()

    # Padroniza chaves para cruzamento
    df["MUNICIPIO"] = df["MUNICIPIO_OCORRENCIA"].apply(normalizar_chave)
    df["ANO"] = df["NU_ANO"].apply(normalizar_chave)
    df["SEXO"] = df["SEXO"].apply(normalizar_chave)
    df["FAIXA_ETARIA_SDS"] = df["FAIXA_ETARIA_SDS"].apply(normalizar_chave)

    # Cria colunas numéricas dos indicadores
    for coluna in COLUNAS_INDICADORES:
        df[f"SINAN_{coluna}"] = preparar_indicador_sim_nao(df, coluna)

    # Chaves do agrupamento
    chaves = [
        "MUNICIPIO",
        "ANO",
        "SEXO",
        "FAIXA_ETARIA_SDS",
    ]

    # Define agregações
    agregacoes = {
        "ID_SINAN": "count",
    }

    # Adiciona agregações dos indicadores
    for coluna in COLUNAS_INDICADORES:
        agregacoes[f"SINAN_{coluna}"] = "sum"

    # Agrupa SINAN
    df_sinan_agg = (
        df
        .groupby(chaves, dropna=False)
        .agg(agregacoes)
        .reset_index()
    )

    # Renomeia total principal
    df_sinan_agg = df_sinan_agg.rename(columns={
        "ID_SINAN": "TOTAL_REGISTROS_SINAN"
    })

    # Exibe resumo
    print(
        f"SINAN agregado: {df_sinan_agg.shape[0]} linhas e {df_sinan_agg.shape[1]} colunas.",
        flush=True
    )

    # Retorna SINAN agregado
    return df_sinan_agg


# %%
def preparar_sds_para_gold(df_sds):
    """
    Prepara e agrega a base SDS para cruzamento com SINAN.
    """

    # Define colunas necessárias
    colunas_necessarias = [
        "ID_SDS",
        "MUNICIPIO",
        "REGIAO_GEOGRAFICA",
        "ANO",
        "SEXO",
        "FAIXA_ETARIA_SDS",
        "TOTAL_VITIMAS",
    ]

    # Verifica colunas ausentes
    colunas_ausentes = [
        coluna for coluna in colunas_necessarias
        if coluna not in df_sds.columns
    ]

    # Interrompe se faltar alguma coluna
    if colunas_ausentes:
        raise ValueError(f"Colunas ausentes na SDS silver: {colunas_ausentes}")

    # Cria base auxiliar
    df = df_sds.copy()

    # Padroniza chaves para cruzamento
    df["MUNICIPIO"] = df["MUNICIPIO"].apply(normalizar_chave)
    df["ANO"] = df["ANO"].apply(normalizar_chave)
    df["SEXO"] = df["SEXO"].apply(normalizar_chave)
    df["FAIXA_ETARIA_SDS"] = df["FAIXA_ETARIA_SDS"].apply(normalizar_chave)
    df["REGIAO_GEOGRAFICA"] = df["REGIAO_GEOGRAFICA"].apply(normalizar_chave)

    # Converte total de vítimas para número
    df["TOTAL_VITIMAS_NUM"] = pd.to_numeric(
        df["TOTAL_VITIMAS"],
        errors="coerce"
    ).fillna(0).astype(int)

    # Cria colunas ponderadas por TOTAL_VITIMAS
    for coluna in COLUNAS_INDICADORES:

        # Cria indicador 1/0
        indicador = preparar_indicador_sim_nao(df, coluna)

        # Soma vítimas associadas àquele tipo de violência
        df[f"SDS_{coluna}"] = indicador * df["TOTAL_VITIMAS_NUM"]

    # Chaves do agrupamento
    chaves = [
        "MUNICIPIO",
        "ANO",
        "SEXO",
        "FAIXA_ETARIA_SDS",
    ]

    # Define agregações
    agregacoes = {
        "ID_SDS": "count",
        "TOTAL_VITIMAS_NUM": "sum",
        "REGIAO_GEOGRAFICA": "first",
    }

    # Adiciona agregações dos indicadores
    for coluna in COLUNAS_INDICADORES:
        agregacoes[f"SDS_{coluna}"] = "sum"

    # Agrupa SDS
    df_sds_agg = (
        df
        .groupby(chaves, dropna=False)
        .agg(agregacoes)
        .reset_index()
    )

    # Renomeia colunas principais
    df_sds_agg = df_sds_agg.rename(columns={
        "ID_SDS": "TOTAL_REGISTROS_SDS",
        "TOTAL_VITIMAS_NUM": "TOTAL_VITIMAS_SDS",
    })

    # Exibe resumo
    print(
        f"SDS agregada: {df_sds_agg.shape[0]} linhas e {df_sds_agg.shape[1]} colunas.",
        flush=True
    )

    # Retorna SDS agregada
    return df_sds_agg


# %%
def cruzar_sds_sinan(df_sinan_agg, df_sds_agg):
    """
    Cruza SINAN e SDS agregados.
    """

    # Chaves de cruzamento
    chaves = [
        "MUNICIPIO",
        "ANO",
        "SEXO",
        "FAIXA_ETARIA_SDS",
    ]

    # Faz o merge externo para manter registros presentes em apenas uma base
    df_gold = df_sinan_agg.merge(
        df_sds_agg,
        on=chaves,
        how="outer"
    )

    # Colunas numéricas que devem receber zero quando ausentes
    colunas_numericas = [
        coluna for coluna in df_gold.columns
        if coluna.startswith("SINAN_")
        or coluna.startswith("SDS_")
        or coluna.startswith("TOTAL_")
    ]

    # Preenche ausências numéricas com zero
    for coluna in colunas_numericas:
        df_gold[coluna] = pd.to_numeric(df_gold[coluna], errors="coerce").fillna(0).astype(int)

    # Preenche região ausente
    if "REGIAO_GEOGRAFICA" in df_gold.columns:
        df_gold["REGIAO_GEOGRAFICA"] = df_gold["REGIAO_GEOGRAFICA"].fillna(VALOR_NAO_INFORMADO)

    # Cria diferença entre as bases
    df_gold["DIF_TOTAL_SDS_MENOS_SINAN"] = (
        df_gold["TOTAL_VITIMAS_SDS"] - df_gold["TOTAL_REGISTROS_SINAN"]
    )

    # Reordena colunas principais
    colunas_principais = [
        "MUNICIPIO",
        "REGIAO_GEOGRAFICA",
        "ANO",
        "SEXO",
        "FAIXA_ETARIA_SDS",
        "TOTAL_REGISTROS_SINAN",
        "TOTAL_REGISTROS_SDS",
        "TOTAL_VITIMAS_SDS",
        "DIF_TOTAL_SDS_MENOS_SINAN",
    ]

    # Mantém apenas colunas principais existentes
    colunas_principais = [
        coluna for coluna in colunas_principais
        if coluna in df_gold.columns
    ]

    # Demais colunas
    outras_colunas = [
        coluna for coluna in df_gold.columns
        if coluna not in colunas_principais
    ]

    # Reordena DataFrame
    df_gold = df_gold[colunas_principais + outras_colunas]

    # Exibe resumo
    print(
        f"Base Gold SDS + SINAN: {df_gold.shape[0]} linhas e {df_gold.shape[1]} colunas.",
        flush=True
    )

    # Retorna base final
    return df_gold


# %%
def gerar_gold_sds_sinan():
    """
    Gera a base Gold cruzada entre SDS e SINAN.
    """

    # Cria pasta gold caso ainda não exista
    SDS_SINAN_GOLD.mkdir(parents=True, exist_ok=True)

    # Carrega as bases silver
    df_sinan, df_sds = carregar_bases_silver()

    # Agrega SINAN
    df_sinan_agg = preparar_sinan_para_gold(df_sinan)

    # Agrega SDS
    df_sds_agg = preparar_sds_para_gold(df_sds)

    # Cruza bases agregadas
    df_gold = cruzar_sds_sinan(df_sinan_agg, df_sds_agg)

    # Define caminho de saída
    caminho_saida = SDS_SINAN_GOLD / "sds_sinan_final.parquet"

    # Salva em Parquet
    df_gold.to_parquet(
        caminho_saida,
        index=False,
        engine="pyarrow",
        compression="snappy"
    )

    # Exibe confirmação
    print(f"\nBase Gold salva em: {caminho_saida}", flush=True)

    # Retorna caminho salvo
    return caminho_saida


# %%
# Permite executar o arquivo diretamente pelo terminal
if __name__ == "__main__":
    gerar_gold_sds_sinan()