# %%
# Importa sys para ajustar imports quando rodar por célula no VS Code
import sys

# Importa Path para manipular caminhos de arquivos
from pathlib import Path

# Importa unicodedata para remover acentos
import unicodedata

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
from src.config import SDS_BRONZE, SDS_SILVER


# %%
# Valor padrão usado para células sem informação útil
VALOR_NAO_INFORMADO = "DADO NÃO INFORMADO"

# Recorte temporal compatível com o SINAN
ANO_INICIO = 2014
ANO_FIM = 2024

# Valores considerados inválidos
VALORES_INVALIDOS_TEXTO = {
    "",
    " ",
    "0",
    "0.0",
    "00",
    "000",
    "0000",
    "nan",
    "NaN",
    "NAN",
    "none",
    "None",
    "NONE",
    "null",
    "Null",
    "NULL",
    "nat",
    "NaT",
    "NAT",
    "<NA>",
    "NA",
    "N/A",
    "na",
    "n/a",
    "DADO NAO INFORMADO",
    "DADO NÃO INFORMADO",
}


# %%
def remover_acentos(texto):
    """
    Remove acentos de um texto.
    """

    # Converte para texto
    texto = str(texto)

    # Normaliza o texto
    texto_normalizado = unicodedata.normalize("NFKD", texto)

    # Remove caracteres de acento
    texto_sem_acentos = "".join(
        caractere for caractere in texto_normalizado
        if not unicodedata.combining(caractere)
    )

    # Retorna texto sem acentos
    return texto_sem_acentos


# %%
def normalizar_valor_invalido(valor):
    """
    Padroniza qualquer valor inválido como DADO NÃO INFORMADO.
    """

    # Trata nulos reais do pandas
    if pd.isna(valor):
        return VALOR_NAO_INFORMADO

    # Trata zero numérico como ausência de informação
    if isinstance(valor, (int, float)) and valor == 0:
        return VALOR_NAO_INFORMADO

    # Converte para texto e remove espaços
    valor_texto = str(valor).strip()

    # Remove .0 de valores textuais
    if valor_texto.endswith(".0"):
        valor_texto_sem_decimal = valor_texto[:-2]
    else:
        valor_texto_sem_decimal = valor_texto

    # Verifica valor inválido
    if valor_texto in VALORES_INVALIDOS_TEXTO:
        return VALOR_NAO_INFORMADO

    # Verifica valor sem decimal
    if valor_texto_sem_decimal in VALORES_INVALIDOS_TEXTO:
        return VALOR_NAO_INFORMADO

    # Retorna valor válido
    return valor


# %%
def padronizar_texto(valor, remover_acentuacao=True):
    """
    Padroniza texto em maiúsculo, sem espaços extras e, por padrão, sem acentos.
    """

    # Trata valores inválidos
    valor = normalizar_valor_invalido(valor)

    # Retorna padrão se for inválido
    if valor == VALOR_NAO_INFORMADO:
        return VALOR_NAO_INFORMADO

    # Converte para texto e padroniza
    texto = str(valor).strip().upper()

    # Remove acentos quando necessário
    if remover_acentuacao:
        texto = remover_acentos(texto)

    # Trata valores inválidos após conversão
    if texto in VALORES_INVALIDOS_TEXTO:
        return VALOR_NAO_INFORMADO

    # Retorna texto padronizado
    return texto


# %%
def normalizar_dataframe_final(df, colunas_excecao=None):
    """
    Aplica a padronização final de valores inválidos em todo o DataFrame.
    """

    # Define colunas que não devem ser alteradas
    if colunas_excecao is None:
        colunas_excecao = []

    # Percorre todas as colunas
    for coluna in df.columns:

        # Pula exceções
        if coluna in colunas_excecao:
            continue

        # Aplica tratamento de inválidos
        df[coluna] = df[coluna].apply(normalizar_valor_invalido)

        # Converte para string para evitar erro no Parquet
        df[coluna] = df[coluna].astype(str)

        # Garante troca de inválidos textuais
        df[coluna] = df[coluna].replace(
            list(VALORES_INVALIDOS_TEXTO),
            VALOR_NAO_INFORMADO
        )

    # Retorna DataFrame tratado
    return df


# %%
def padronizar_sexo_sds(valor):
    """
    Padroniza o sexo da SDS para F ou M.
    """

    # Padroniza texto
    sexo = padronizar_texto(valor)

    # Retorna padrão se inválido
    if sexo == VALOR_NAO_INFORMADO:
        return VALOR_NAO_INFORMADO

    # Feminino
    if sexo.startswith("F"):
        return "F"

    # Masculino
    if sexo.startswith("M"):
        return "M"

    # Caso não reconheça
    return VALOR_NAO_INFORMADO


# %%
def padronizar_faixa_etaria_sds(valor):
    """
    Remove prefixos da faixa etária da SDS.
    Exemplo: 1) 00-11 -> 00-11
    """

    # Padroniza texto
    faixa = padronizar_texto(valor)

    # Retorna padrão se inválido
    if faixa == VALOR_NAO_INFORMADO:
        return VALOR_NAO_INFORMADO

    # Remove prefixo numérico como "1)"
    if ")" in faixa:
        faixa = faixa.split(")", 1)[1].strip()

    # Padroniza variações
    faixa = faixa.replace("65 E MAIS", "65 OU MAIS")

    # Faixas esperadas
    faixas_validas = {
        "00-11",
        "12-17",
        "18-24",
        "25-29",
        "30-34",
        "35-64",
        "65 OU MAIS",
    }

    # Retorna faixa válida
    if faixa in faixas_validas:
        return faixa

    # Caso contrário, retorna padrão
    return VALOR_NAO_INFORMADO


# %%
def padronizar_data(valor):
    """
    Padroniza data no formato YYYY-MM-DD.
    """

    # Converte para datetime
    data = pd.to_datetime(valor, errors="coerce")

    # Trata data inválida
    if pd.isna(data):
        return VALOR_NAO_INFORMADO

    # Retorna data formatada
    return data.strftime("%Y-%m-%d")


# %%
def padronizar_total_vitimas(valor):
    """
    Padroniza o total de vítimas.
    """

    # Trata inválidos
    if normalizar_valor_invalido(valor) == VALOR_NAO_INFORMADO:
        return VALOR_NAO_INFORMADO

    # Tenta converter para inteiro
    try:
        total = int(float(valor))
    except (ValueError, TypeError):
        return VALOR_NAO_INFORMADO

    # Total menor ou igual a zero não é útil
    if total <= 0:
        return VALOR_NAO_INFORMADO

    # Retorna como texto
    return str(total)


# %%
def criar_colunas_sinan_por_natureza(df):
    """
    Cria colunas equivalentes ao SINAN a partir da coluna NATUREZA da SDS.
    """

    # Colunas de violência do SINAN
    colunas_violencia = [
        "VIOL_FISIC",
        "VIOL_PSICO",
        "VIOL_TORT",
        "VIOL_SEXU",
        "VIOL_TRAF",
        "VIOL_FINAN",
        "VIOL_NEGLI",
        "VIOL_INFAN",
    ]

    # Colunas de agressão do SINAN
    colunas_agressao = [
        "AG_FORCA",
        "AG_ENFOR",
        "AG_OBJETO",
        "AG_CORTE",
        "AG_QUENTE",
        "AG_ENVEN",
        "AG_FOGO",
        "AG_AMEACA",
    ]

    # Colunas de violência sexual do SINAN
    colunas_sexual = [
        "SEX_ASSEDI",
        "SEX_ESTUPR",
        "SEX_PORNO",
        "SEX_EXPLO",
    ]

    # Junta todas as colunas
    todas_colunas_sinan = colunas_violencia + colunas_agressao + colunas_sexual

    # Inicializa todas como NAO
    for coluna in todas_colunas_sinan:
        df[coluna] = "NAO"

    # Cria versão da natureza sem acento para comparação
    natureza_busca = df["NATUREZA"].apply(lambda valor: padronizar_texto(valor, remover_acentuacao=True))

    # Crimes físicos usados no código antigo
    crimes_fisicos = {
        "LESAO CORPORAL POR VIOLENCIA DOMESTICA/FAMILIAR",
        "VIAS DE FATOS POR VIOLENCIA DOMESTICA/FAMILIAR",
        "MAUS TRATOS POR VIOLENCIA DOMESTICA/FAMILIAR",
    }

    # Crimes psicológicos usados no código antigo
    crimes_psicologicos = {
        "AMEACA POR VIOLENCIA DOMESTICA/FAMILIAR",
        "CALUNIA POR VIOLENCIA DOMESTICA/FAMILIAR",
        "DIFAMACAO POR VIOLENCIA DOMESTICA/FAMILIAR",
        "INJURIA POR VIOLENCIA DOMESTICA/FAMILIAR",
        "PERSEGUICAO POR VIOLENCIA DOMESTICA/FAMILIAR",
        "CONSTRANGIMENTO ILEGAL POR VIOLENCIA DOMESTICA/FAMILIAR",
        "PERTURBACAO DO SOSSEGO POR VIOLENCIA DOMESTICA/FAMILIAR",
        "CARCERE PRIVADO POR VIOLENCIA DOMESTICA/FAMILIAR",
    }

    # Crimes sexuais usados no código antigo
    crimes_sexuais = {
        "ESTUPRO POR VIOLENCIA DOMESTICA/FAMILIAR",
        "ESTUPRO DE VULNERAVEL POR VIOLENCIA DOMESTICA/FAMILIAR",
    }

    # Máscara de violência física
    mask_fisica = (
        natureza_busca.isin(crimes_fisicos) |
        natureza_busca.str.contains("LESAO CORPORAL", na=False) |
        natureza_busca.str.contains("VIAS DE FATO", na=False) |
        natureza_busca.str.contains("MAUS TRATOS", na=False)
    )

    # Máscara de violência psicológica
    mask_psico = (
        natureza_busca.isin(crimes_psicologicos) |
        natureza_busca.str.contains("AMEACA", na=False) |
        natureza_busca.str.contains("CALUNIA", na=False) |
        natureza_busca.str.contains("DIFAMACAO", na=False) |
        natureza_busca.str.contains("INJURIA", na=False) |
        natureza_busca.str.contains("PERSEGUICAO", na=False) |
        natureza_busca.str.contains("CONSTRANGIMENTO", na=False) |
        natureza_busca.str.contains("PERTURBACAO", na=False) |
        natureza_busca.str.contains("CARCERE PRIVADO", na=False)
    )

    # Máscara de violência sexual
    mask_sexual = (
        natureza_busca.isin(crimes_sexuais) |
        natureza_busca.str.contains("ESTUPRO", na=False)
    )

    # Máscara de violência financeira/patrimonial
    mask_financeira = (
        natureza_busca.eq("DANO POR VIOLENCIA DOMESTICA/FAMILIAR") |
        natureza_busca.str.contains("DANO", na=False)
    )

    # Marca violência física
    df.loc[mask_fisica, "VIOL_FISIC"] = "SIM"

    # Marca violência psicológica
    df.loc[mask_psico, "VIOL_PSICO"] = "SIM"

    # Marca violência sexual
    df.loc[mask_sexual, "VIOL_SEXU"] = "SIM"

    # Marca violência financeira
    df.loc[mask_financeira, "VIOL_FINAN"] = "SIM"

    # Marca ameaça
    df.loc[natureza_busca.str.contains("AMEACA", na=False), "AG_AMEACA"] = "SIM"

    # Marca estupro
    df.loc[mask_sexual, "SEX_ESTUPR"] = "SIM"

    # Retorna o DataFrame e a lista de colunas criadas
    return df, todas_colunas_sinan


# %%
def tratar_sds():
    """
    Trata a base SDS e salva na camada silver.
    """

    # Cria a pasta silver da SDS caso ainda não exista
    SDS_SILVER.mkdir(parents=True, exist_ok=True)

    # Define o caminho de entrada
    caminho_entrada = SDS_BRONZE / "parquet" / "sds_completo.parquet"

    # Verifica se o arquivo existe
    if not caminho_entrada.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_entrada}")

    # Lê a base SDS bronze
    df = pd.read_parquet(caminho_entrada)

    # Exibe tamanho inicial
    print(f"Base SDS bronze: {df.shape[0]} linhas e {df.shape[1]} colunas.", flush=True)

    # Renomeia colunas para o padrão do projeto
    df = df.rename(columns={
        "MUNICÍPIO DO FATO": "MUNICIPIO",
        "REGIAO GEOGRÁFICA": "REGIAO_GEOGRAFICA",
        "NATUREZA": "NATUREZA",
        "DATA DO FATO": "DATA_FATO",
        "ANO": "ANO",
        "SEXO": "SEXO",
        "IDADE SENASP": "FAIXA_ETARIA_SDS",
        "TOTAL DE VÍTIMAS": "TOTAL_VITIMAS",
    })

    # Define colunas necessárias
    colunas_necessarias = [
        "MUNICIPIO",
        "REGIAO_GEOGRAFICA",
        "NATUREZA",
        "DATA_FATO",
        "ANO",
        "SEXO",
        "FAIXA_ETARIA_SDS",
        "TOTAL_VITIMAS",
    ]

    # Verifica colunas ausentes
    colunas_ausentes = [
        coluna for coluna in colunas_necessarias
        if coluna not in df.columns
    ]

    # Interrompe se faltar alguma coluna
    if colunas_ausentes:
        raise ValueError(f"Colunas ausentes na SDS: {colunas_ausentes}")

    # Mantém apenas as colunas úteis
    df_sds = df[colunas_necessarias].copy()

    # Cria coluna auxiliar de ano numérico
    df_sds["ANO_NUM"] = pd.to_numeric(df_sds["ANO"], errors="coerce")

    # Filtra o mesmo recorte temporal do SINAN
    df_sds = df_sds[
        (df_sds["ANO_NUM"] >= ANO_INICIO) &
        (df_sds["ANO_NUM"] <= ANO_FIM)
    ].copy()

    # Exibe total após filtro temporal
    print(
        f"Registros após filtro temporal {ANO_INICIO}-{ANO_FIM}: {df_sds.shape[0]}",
        flush=True
    )

    # Padroniza sexo para F/M
    df_sds["SEXO"] = df_sds["SEXO"].apply(padronizar_sexo_sds)

    # Filtra apenas sexo feminino
    df_sds = df_sds[
        df_sds["SEXO"] == "F"
    ].copy()

    # Exibe total após filtro de sexo
    print(
        f"Registros após filtro {ANO_INICIO}-{ANO_FIM} + sexo feminino: {df_sds.shape[0]}",
        flush=True
    )

    # Padroniza município sem acentos para facilitar merge com SINAN
    df_sds["MUNICIPIO"] = df_sds["MUNICIPIO"].apply(
        lambda valor: padronizar_texto(valor, remover_acentuacao=True)
    )

    # Padroniza região geográfica
    df_sds["REGIAO_GEOGRAFICA"] = df_sds["REGIAO_GEOGRAFICA"].apply(
        lambda valor: padronizar_texto(valor, remover_acentuacao=True)
    )

    # Padroniza natureza
    df_sds["NATUREZA"] = df_sds["NATUREZA"].apply(
        lambda valor: padronizar_texto(valor, remover_acentuacao=True)
    )

    # Padroniza data do fato
    df_sds["DATA_FATO"] = df_sds["DATA_FATO"].apply(padronizar_data)

    # Padroniza ano
    df_sds["ANO"] = df_sds["ANO_NUM"].astype("Int64").astype(str)
    df_sds["ANO"] = df_sds["ANO"].replace(
        ["<NA>", "nan", "NaN", "None"],
        VALOR_NAO_INFORMADO
    )

    # Remove coluna auxiliar
    df_sds = df_sds.drop(columns=["ANO_NUM"])

    # Padroniza faixa etária SDS
    df_sds["FAIXA_ETARIA_SDS"] = df_sds["FAIXA_ETARIA_SDS"].apply(padronizar_faixa_etaria_sds)

    # Padroniza total de vítimas
    df_sds["TOTAL_VITIMAS"] = df_sds["TOTAL_VITIMAS"].apply(padronizar_total_vitimas)

    # Cria colunas equivalentes ao SINAN a partir da natureza
    df_sds, todas_colunas_sinan = criar_colunas_sinan_por_natureza(df_sds)

    # Reordena colunas finais
    df_sds = df_sds[
        [
            "MUNICIPIO",
            "REGIAO_GEOGRAFICA",
            "NATUREZA",
            "DATA_FATO",
            "ANO",
            "SEXO",
            "FAIXA_ETARIA_SDS",
            "TOTAL_VITIMAS",
        ] + todas_colunas_sinan
    ]

    # Conta duplicatas antes da remoção
    linhas_iniciais = df_sds.shape[0]
    quantidade_duplicatas = df_sds.duplicated().sum()

    # Exibe diagnóstico de duplicatas
    print(f"\nTotal antes da deduplicação: {linhas_iniciais}", flush=True)
    print(f"Duplicatas encontradas: {quantidade_duplicatas}", flush=True)

    # Remove duplicatas exatas
    if quantidade_duplicatas > 0:
        df_sds = df_sds.drop_duplicates(ignore_index=True)
        print(f"Duplicatas removidas: {linhas_iniciais - df_sds.shape[0]}", flush=True)
    else:
        print("Nenhuma duplicata exata encontrada.", flush=True)

    # Cria ID único da SDS
    df_sds.insert(0, "ID_SDS", range(1, len(df_sds) + 1))

    # Padroniza valores inválidos em todas as colunas finais
    df_sds = normalizar_dataframe_final(
        df_sds,
        colunas_excecao=["ID_SDS"]
    )

    # Define o caminho de saída
    caminho_saida = SDS_SILVER / "base_sds_tratada.parquet"

    # Salva a base tratada em Parquet
    df_sds.to_parquet(
        caminho_saida,
        index=False,
        engine="pyarrow",
        compression="snappy"
    )

    # Exibe resumo final
    print(f"\nBase SDS tratada salva em: {caminho_saida}", flush=True)
    print(f"Total final: {df_sds.shape[0]} linhas e {df_sds.shape[1]} colunas.", flush=True)

    # Mostra conferência rápida
    print("\nValores únicos de SEXO:", df_sds["SEXO"].unique(), flush=True)
    print("Valores únicos de FAIXA_ETARIA_SDS:", df_sds["FAIXA_ETARIA_SDS"].unique(), flush=True)

    # Retorna caminho salvo
    return caminho_saida


# %%
# Permite executar o arquivo diretamente pelo terminal
if __name__ == "__main__":
    tratar_sds()