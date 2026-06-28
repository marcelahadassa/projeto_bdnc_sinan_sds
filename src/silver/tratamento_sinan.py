# %%
# Importa sys para ajustar imports quando rodar por célula no VS Code
import sys

# Importa Path para manipular caminhos de arquivos
from pathlib import Path

# Importa Number para identificar valores numéricos
from numbers import Number

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
from src.config import SINAN_BRONZE, SINAN_SILVER, IBGE_SILVER, CNES_SILVER


# %%
# Valor padrão usado para células sem informação útil
VALOR_NAO_INFORMADO = "DADO NÃO INFORMADO"

# Lista de valores considerados inválidos ou sem utilidade analítica
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

    # Normaliza o texto para separar letras e acentos
    texto_normalizado = unicodedata.normalize("NFKD", texto)

    # Remove os caracteres de acentuação
    texto_sem_acentos = "".join(
        caractere for caractere in texto_normalizado
        if not unicodedata.combining(caractere)
    )

    # Retorna o texto sem acento
    return texto_sem_acentos


# %%
def extrair_ano_arquivo(caminho_arquivo):
    """
    Extrai o ano completo a partir do nome do arquivo.
    Exemplo: VIOLBR14.parquet -> 2014
    """

    # Pega o nome do arquivo sem extensão
    nome = caminho_arquivo.stem.upper()

    # Remove o prefixo VIOLBR e fica apenas com o ano curto
    ano_curto = int(nome.replace("VIOLBR", ""))

    # Converte o ano curto para ano completo
    return 2000 + ano_curto


# %%
def normalizar_valor_invalido(valor, zero_valido=False):
    """
    Padroniza qualquer valor inválido como DADO NÃO INFORMADO.
    Permite manter zero quando ele for um valor válido.
    """

    # Trata nulos reais do pandas/numpy
    if pd.isna(valor):
        return VALOR_NAO_INFORMADO

    # Trata zeros numéricos
    if isinstance(valor, Number) and valor == 0:

        # Mantém zero quando permitido
        if zero_valido:
            return "0"

        # Caso contrário, zero vira dado não informado
        return VALOR_NAO_INFORMADO

    # Converte para texto para tratar variações como 'nan', 'NULL', '0.0'
    valor_texto = str(valor).strip()

    # Remove .0 de números que vieram como float textual
    if valor_texto.endswith(".0"):
        valor_texto_sem_decimal = valor_texto[:-2]
    else:
        valor_texto_sem_decimal = valor_texto

    # Mantém zero textual quando permitido
    if zero_valido and valor_texto_sem_decimal in {"0", "00", "000", "0000"}:
        return "0"

    # Verifica se o texto é inválido
    if valor_texto in VALORES_INVALIDOS_TEXTO:
        return VALOR_NAO_INFORMADO

    # Verifica se o texto sem .0 é inválido
    if valor_texto_sem_decimal in VALORES_INVALIDOS_TEXTO:
        return VALOR_NAO_INFORMADO

    # Retorna o valor original quando ele é válido
    return valor


# %%
def normalizar_dataframe_final(df, colunas_excecao=None, colunas_zero_valido=None):
    """
    Aplica a padronização final de valores inválidos em todo o DataFrame.
    Permite manter zero em colunas específicas.
    """

    # Define colunas que não devem ser alteradas
    if colunas_excecao is None:
        colunas_excecao = []

    # Define colunas onde zero é um valor válido
    if colunas_zero_valido is None:
        colunas_zero_valido = []

    # Percorre todas as colunas
    for coluna in df.columns:

        # Pula colunas de exceção
        if coluna in colunas_excecao:
            continue

        # Verifica se zero é válido para esta coluna
        zero_valido = coluna in colunas_zero_valido

        # Aplica a padronização de valores inválidos
        df[coluna] = df[coluna].apply(
            lambda valor: normalizar_valor_invalido(
                valor,
                zero_valido=zero_valido
            )
        )

        # Converte para string para evitar mistura de tipos no Parquet
        df[coluna] = df[coluna].astype(str)

        # Define inválidos que serão substituídos
        valores_invalidos = set(VALORES_INVALIDOS_TEXTO)

        # Se zero for válido, não substitui zeros textuais
        if zero_valido:
            valores_invalidos = valores_invalidos - {"0", "0.0", "00", "000", "0000"}

        # Garante novamente a troca de textos inválidos após conversão
        df[coluna] = df[coluna].replace(
            list(valores_invalidos),
            VALOR_NAO_INFORMADO
        )

    # Retorna o DataFrame normalizado
    return df


# %%
def carregar_sinan_bronze():
    """
    Lê todos os arquivos Parquet do SINAN na camada bronze
    e concatena em um único DataFrame.
    """

    # Define a pasta onde estão os Parquets brutos do SINAN
    pasta_sinan = SINAN_BRONZE / "parquet"

    # Busca todos os arquivos anuais do SINAN
    arquivos = sorted(pasta_sinan.glob("VIOLBR*.parquet"))

    # Interrompe se nenhum arquivo for encontrado
    if not arquivos:
        raise FileNotFoundError(f"Nenhum arquivo Parquet encontrado em: {pasta_sinan}")

    # Lista para armazenar os DataFrames de cada ano
    lista_dfs = []

    # Percorre cada arquivo anual
    for arquivo in arquivos:

        # Mostra qual arquivo está sendo lido
        print(f"Carregando: {arquivo.name}", flush=True)

        # Lê o arquivo Parquet
        df_temp = pd.read_parquet(arquivo)

        # Extrai o ano a partir do nome do arquivo
        ano_completo = extrair_ano_arquivo(arquivo)

        # Garante a coluna NU_ANO preenchida corretamente
        df_temp["NU_ANO"] = ano_completo

        # Adiciona o DataFrame na lista
        lista_dfs.append(df_temp)

    # Junta todos os anos em uma única base
    df = pd.concat(lista_dfs, ignore_index=True)

    # Exibe o tamanho da base consolidada
    print(
        f"\nBase SINAN bronze consolidada: {df.shape[0]} linhas e {df.shape[1]} colunas.",
        flush=True
    )

    # Retorna a base consolidada
    return df


# %%
def aplicar_mapa_coluna(df, coluna, mapa):
    """
    Aplica um dicionário de tradução em uma coluna.
    Valores inválidos viram DADO NÃO INFORMADO.
    """

    # Só aplica se a coluna existir
    if coluna in df.columns:

        # Normaliza inválidos antes do mapeamento
        df[coluna] = df[coluna].apply(normalizar_valor_invalido)

        # Converte os códigos para numérico de forma segura
        codigos = pd.to_numeric(df[coluna], errors="coerce")

        # Aplica o mapa
        valores_mapeados = codigos.map(mapa)

        # Mantém valores já válidos quando não houver correspondência no mapa
        df[coluna] = valores_mapeados.fillna(df[coluna])

        # Normaliza novamente após o mapeamento
        df[coluna] = df[coluna].apply(normalizar_valor_invalido)

    # Retorna o DataFrame atualizado
    return df


# %%
def interpretar_idade_formatada(idade_codificada):
    """
    Interpreta o código de idade do SINAN.
    Exemplo: 4023 -> 23 anos
    """

    # Trata valores inválidos
    if normalizar_valor_invalido(idade_codificada) == VALOR_NAO_INFORMADO:
        return VALOR_NAO_INFORMADO

    # Tenta converter o código para inteiro
    try:
        idade_int = int(float(idade_codificada))
    except (ValueError, TypeError):
        return VALOR_NAO_INFORMADO

    # Trata zero como não informado
    if idade_int == 0:
        return VALOR_NAO_INFORMADO

    # Converte para string para separar unidade e quantidade
    idade_str = str(idade_int)

    # Garante que o código tenha ao menos dois dígitos
    if len(idade_str) < 2:
        return VALOR_NAO_INFORMADO

    # Interpreta a unidade de tempo
    try:
        unidade = int(idade_str[0])
        quantidade = int(idade_str[1:])

        # Unidade 1 representa horas
        if unidade == 1:
            return f"{quantidade} hora" if quantidade == 1 else f"{quantidade} horas"

        # Unidade 2 representa dias
        if unidade == 2:
            return f"{quantidade} dia" if quantidade == 1 else f"{quantidade} dias"

        # Unidade 3 representa meses
        if unidade == 3:
            return f"{quantidade} mês" if quantidade == 1 else f"{quantidade} meses"

        # Unidade 4 representa anos
        if unidade == 4:
            return f"{quantidade} ano" if quantidade == 1 else f"{quantidade} anos"

        # Outras unidades são tratadas como não informadas
        return VALOR_NAO_INFORMADO

    except (ValueError, IndexError):
        return VALOR_NAO_INFORMADO


# %%
def padronizar_codigo_municipio_sinan(valor):
    """
    Padroniza o código de município do SINAN para cruzar com o IBGE.
    """

    # Trata valores inválidos
    if normalizar_valor_invalido(valor) == VALOR_NAO_INFORMADO:
        return VALOR_NAO_INFORMADO

    # Tenta converter para inteiro
    try:
        codigo_int = int(float(valor))
        codigo_texto = str(codigo_int)
    except (ValueError, TypeError):
        codigo_texto = str(valor).strip()

    # Remove .0 caso venha como texto
    if codigo_texto.endswith(".0"):
        codigo_texto = codigo_texto[:-2]

    # Trata valores inválidos após conversão
    if codigo_texto in VALORES_INVALIDOS_TEXTO:
        return VALOR_NAO_INFORMADO

    # Se vier com 7 dígitos do IBGE, usa os 6 primeiros
    if len(codigo_texto) >= 7:
        codigo_texto = codigo_texto[:6]

    # Se tiver menos de 6 dígitos, considera inválido
    if len(codigo_texto) < 6:
        return VALOR_NAO_INFORMADO

    # Retorna o código compatível com o SINAN
    return codigo_texto


# %%
def substituir_codigos_municipios(df):
    """
    Substitui os códigos de município do SINAN pelos nomes dos municípios
    usando a base tratada do IBGE.
    """

    # Caminho da base IBGE tratada
    caminho_ibge = IBGE_SILVER / "municipios_tratado.parquet"

    # Verifica se a base IBGE tratada existe
    if not caminho_ibge.exists():
        raise FileNotFoundError(f"Base IBGE tratada não encontrada: {caminho_ibge}")

    # Lê a base tratada do IBGE
    df_ibge = pd.read_parquet(caminho_ibge)

    # Verifica se as colunas necessárias existem no IBGE tratado
    colunas_ibge = ["ID_MUNICIP_SINAN", "NOME_MUNICIPIO"]
    colunas_ausentes = [
        coluna for coluna in colunas_ibge
        if coluna not in df_ibge.columns
    ]

    # Interrompe se faltar coluna no IBGE
    if colunas_ausentes:
        raise ValueError(f"Colunas ausentes no IBGE tratado: {colunas_ausentes}")

    # Cria dicionário código SINAN -> nome do município
    mapa_municipios = dict(
        zip(
            df_ibge["ID_MUNICIP_SINAN"].astype(str),
            df_ibge["NOME_MUNICIPIO"].astype(str)
        )
    )

    # Colunas de município que serão substituídas
    colunas_municipio = [
        "ID_MUNICIP",
        "ID_MUNIC_RESI",
        "ID_MN_OCOR"
    ]

    # Substitui os códigos pelos nomes
    for coluna in colunas_municipio:

        # Só aplica se a coluna existir
        if coluna in df.columns:

            # Padroniza os códigos antes do mapeamento
            codigos_padronizados = df[coluna].apply(padronizar_codigo_municipio_sinan)

            # Substitui o código pelo nome do município
            df[coluna] = codigos_padronizados.map(mapa_municipios)

            # Onde não encontrou município, coloca dado não informado
            df[coluna] = df[coluna].fillna(VALOR_NAO_INFORMADO)

    # Renomeia as colunas para refletir que agora possuem nomes
    df = df.rename(columns={
        "ID_MUNICIP": "MUNICIPIO_NOTIFICACAO",
        "ID_MUNIC_RESI": "MUNICIPIO_RESIDENCIA",
        "ID_MN_OCOR": "MUNICIPIO_OCORRENCIA"
    })

    # Retorna DataFrame atualizado
    return df


# %%
def padronizar_codigo_unidade_sinan(valor):
    """
    Padroniza o código da unidade do SINAN para cruzar com o CNES.
    Exemplo: 0000019, 19.0 ou 19 -> 19
    """

    # Trata valores inválidos
    if normalizar_valor_invalido(valor) == VALOR_NAO_INFORMADO:
        return VALOR_NAO_INFORMADO

    # Tenta converter para inteiro
    try:
        codigo_int = int(float(valor))
    except (ValueError, TypeError):
        return VALOR_NAO_INFORMADO

    # Trata zero como inválido
    if codigo_int == 0:
        return VALOR_NAO_INFORMADO

    # Retorna como texto sem zeros à esquerda
    return str(codigo_int)


# %%
def substituir_codigos_unidades(df):
    """
    Substitui o ID_UNIDADE do SINAN pelo nome da unidade
    usando a base tratada do CNES.
    """

    # Caminho da base CNES tratada
    caminho_cnes = CNES_SILVER / "unidades_tratadas.parquet"

    # Verifica se a base CNES tratada existe
    if not caminho_cnes.exists():
        raise FileNotFoundError(f"Base CNES tratada não encontrada: {caminho_cnes}")

    # Lê a base tratada do CNES
    df_cnes = pd.read_parquet(caminho_cnes)

    # Verifica se as colunas necessárias existem no CNES tratado
    colunas_cnes = ["ID_UNIDADE", "NOME_UNIDADE"]
    colunas_ausentes = [
        coluna for coluna in colunas_cnes
        if coluna not in df_cnes.columns
    ]

    # Interrompe se faltar coluna no CNES
    if colunas_ausentes:
        raise ValueError(f"Colunas ausentes no CNES tratado: {colunas_ausentes}")

    # Cria dicionário ID_UNIDADE -> nome da unidade
    mapa_unidades = dict(
        zip(
            df_cnes["ID_UNIDADE"].astype(str),
            df_cnes["NOME_UNIDADE"].astype(str)
        )
    )

    # Só aplica se a coluna ID_UNIDADE existir
    if "ID_UNIDADE" in df.columns:

        # Padroniza os códigos antes do mapeamento
        codigos_padronizados = df["ID_UNIDADE"].apply(padronizar_codigo_unidade_sinan)

        # Substitui o código pelo nome da unidade
        df["ID_UNIDADE"] = codigos_padronizados.map(mapa_unidades)

        # Onde não encontrou unidade, coloca dado não informado
        df["ID_UNIDADE"] = df["ID_UNIDADE"].fillna(VALOR_NAO_INFORMADO)

        # Renomeia a coluna para refletir que agora contém nomes
        df = df.rename(columns={
            "ID_UNIDADE": "NOME_UNIDADE"
        })

    # Retorna DataFrame atualizado
    return df


# %%
def extrair_idade_numerica_em_anos(idade_real):
    """
    Extrai idade numérica em anos.
    Horas, dias e meses entram como 0, pois representam menor de 1 ano.
    """

    # Trata valores inválidos
    if normalizar_valor_invalido(idade_real) == VALOR_NAO_INFORMADO:
        return pd.NA

    # Padroniza texto sem acentos
    texto = remover_acentos(str(idade_real).strip().lower())

    # Extrai o número do texto
    numero = pd.Series([texto]).str.extract(r"(\d+)").iloc[0, 0]

    # Trata quando não encontra número
    if pd.isna(numero):
        return pd.NA

    # Converte para inteiro
    try:
        numero = int(float(numero))
    except (ValueError, TypeError):
        return pd.NA

    # Idades em horas, dias ou meses entram como 0 ano
    if ("hora" in texto) or ("dia" in texto) or ("mes" in texto):
        return 0

    # Idades em anos usam o próprio número
    if "ano" in texto:
        return numero

    # Caso o texto venha apenas numérico, usa o número
    return numero


# %%
def criar_faixa_etaria_sds_sinan(df):
    """
    Cria IDADE_NUMERICA_EM_ANOS e FAIXA_ETARIA_SDS no SINAN.
    """

    # Cria idade numérica em anos a partir da idade real
    df["IDADE_NUMERICA_EM_ANOS"] = df["IDADE_REAL"].apply(extrair_idade_numerica_em_anos)

    # Define os limites usados na SDS
    limites = [-1, 11, 17, 24, 29, 34, 64, 130]

    # Define os nomes das faixas usadas na SDS
    nomes_faixas = [
        "00-11",
        "12-17",
        "18-24",
        "25-29",
        "30-34",
        "35-64",
        "65 OU MAIS"
    ]

    # Converte idade para numérico
    idade_num = pd.to_numeric(df["IDADE_NUMERICA_EM_ANOS"], errors="coerce")

    # Cria a faixa etária compatível com a SDS
    df["FAIXA_ETARIA_SDS"] = pd.cut(
        idade_num,
        bins=limites,
        labels=nomes_faixas
    )

    # Trata faixas ausentes
    df["FAIXA_ETARIA_SDS"] = (
        df["FAIXA_ETARIA_SDS"]
        .astype("object")
        .where(df["FAIXA_ETARIA_SDS"].notna(), VALOR_NAO_INFORMADO)
    )

    # Posiciona IDADE_NUMERICA_EM_ANOS e FAIXA_ETARIA_SDS logo após IDADE_REAL
    if "IDADE_REAL" in df.columns:

        # Pega a posição da idade real
        posicao_idade = df.columns.get_loc("IDADE_REAL")

        # Remove temporariamente as colunas criadas
        coluna_idade_numerica = df.pop("IDADE_NUMERICA_EM_ANOS")
        coluna_faixa_etaria = df.pop("FAIXA_ETARIA_SDS")

        # Insere as colunas na posição correta
        df.insert(posicao_idade + 1, "IDADE_NUMERICA_EM_ANOS", coluna_idade_numerica)
        df.insert(posicao_idade + 2, "FAIXA_ETARIA_SDS", coluna_faixa_etaria)

    # Retorna DataFrame atualizado
    return df


# %%
def padronizar_municipios_para_cruzamento(df):
    """
    Padroniza nomes de municípios para cruzar com a SDS.
    Remove acentos, coloca em maiúsculo e remove espaços extras.
    """

    # Colunas de município já substituídas pelo nome
    colunas_municipios = [
        "MUNICIPIO_NOTIFICACAO",
        "MUNICIPIO_RESIDENCIA",
        "MUNICIPIO_OCORRENCIA"
    ]

    # Percorre cada coluna de município
    for coluna in colunas_municipios:

        # Só aplica se a coluna existir
        if coluna in df.columns:

            # Padroniza município
            df[coluna] = (
                df[coluna]
                .apply(normalizar_valor_invalido)
                .astype(str)
                .str.strip()
                .str.upper()
                .apply(remover_acentos)
            )

            # Garante tratamento de inválidos após padronização
            df[coluna] = df[coluna].replace(
                list(VALORES_INVALIDOS_TEXTO),
                VALOR_NAO_INFORMADO
            )

    # Retorna DataFrame atualizado
    return df


# %%
def preparar_sinan_para_cruzamento(df):
    """
    Aplica as transformações necessárias para cruzar SINAN com SDS.
    """

    # Cria idade numérica em anos e faixa etária compatível com SDS
    print("Criando IDADE_NUMERICA_EM_ANOS e FAIXA_ETARIA_SDS...", flush=True)
    df = criar_faixa_etaria_sds_sinan(df)

    # Padroniza os municípios para o mesmo padrão da SDS
    print("Padronizando municípios para cruzamento com SDS...", flush=True)
    df = padronizar_municipios_para_cruzamento(df)

    # Retorna DataFrame preparado
    return df


# %%
def tratar_sinan():
    """
    Executa o tratamento principal do SINAN e salva a base na camada silver.
    """

    # Cria a pasta silver do SINAN caso ainda não exista
    SINAN_SILVER.mkdir(parents=True, exist_ok=True)

    # Carrega os arquivos Parquet da camada bronze
    df = carregar_sinan_bronze()

    # Renomeia colunas para nomes mais claros
    df = df.rename(columns={
        "NU_IDADE_N": "CODIGO_IDADE",
        "ID_MN_RESI": "ID_MUNIC_RESI",
        "CS_SEXO": "SEXO",
        "SG_UF_NOT": "ESTADO_NOTIFICACAO",
        "CS_ESCOL_N": "ESCOLARIDADE",
    })

    # Define as colunas úteis para a análise
    colunas_filtradas = [
        "DT_NOTIFIC", "ESTADO_NOTIFICACAO", "NU_ANO", "ID_MUNICIP", "ID_UNIDADE",
        "DT_OCOR", "ANO_NASC", "CODIGO_IDADE", "SEXO", "CS_RACA", "ESCOLARIDADE",
        "SG_UF", "ID_MUNIC_RESI", "ID_MN_OCOR", "LOCAL_OCOR", "ORIENT_SEX", "IDENT_GEN",
        "DEF_TRANS", "DEF_FISICA", "DEF_MENTAL", "DEF_VISUAL",
        "DEF_AUDITI", "TRAN_MENT", "VIOL_MOTIV", "VIOL_FISIC",
        "VIOL_PSICO", "VIOL_TORT", "VIOL_SEXU", "VIOL_TRAF",
        "VIOL_FINAN", "VIOL_NEGLI", "VIOL_INFAN", "AG_FORCA",
        "AG_ENFOR", "AG_OBJETO", "AG_CORTE", "AG_QUENTE",
        "AG_ENVEN", "AG_FOGO", "AG_AMEACA", "SEX_ASSEDI",
        "SEX_ESTUPR", "SEX_PORNO", "SEX_EXPLO", "NUM_ENVOLV",
        "AUTOR_SEXO", "CICL_VID", "REL_PAI", "REL_MAE", "REL_PAD", "REL_MAD",
        "REL_CONJ", "REL_EXCON", "REL_NAMO", "REL_EXNAM", "REL_IRMAO",
        "REL_FILHO", "REL_CONHEC", "REL_DESCO",
        "REL_PATRAO", "REL_INST", "REL_POL", "ENC_SAUDE",
        "ASSIST_SOC", "REDE_EDUCA", "ATEND_MULH", "CONS_TUTEL",
        "CONS_IDO", "DIR_HUMAN", "MPU", "DELEG_CRIA", "DELEG_MULH",
        "INFAN_JUV", "DEFEN_PUBL", "DELEG_IDOS", "REL_TRAB",
    ]

    # Verifica se todas as colunas necessárias existem
    colunas_ausentes = [coluna for coluna in colunas_filtradas if coluna not in df.columns]

    # Interrompe se houver colunas ausentes
    if colunas_ausentes:
        raise ValueError(f"Colunas ausentes no SINAN: {colunas_ausentes}")

    # Converte UF de notificação para número
    estado_notificacao_num = pd.to_numeric(df["ESTADO_NOTIFICACAO"], errors="coerce")

    # Converte UF de residência para número
    sg_uf_num = pd.to_numeric(df["SG_UF"], errors="coerce")

    # Padroniza sexo para evitar problemas de caixa e espaços
    sexo_padronizado = df["SEXO"].astype(str).str.upper().str.strip()

    # Filtra registros de Pernambuco e sexo feminino
    df_sinan = df[
        (estado_notificacao_num == 26) &
        (sg_uf_num == 26) &
        (sexo_padronizado == "F")
    ][colunas_filtradas].copy()

    # Mostra o total após filtro
    print(f"Registros após filtro PE + sexo feminino: {df_sinan.shape[0]}", flush=True)

    # Mapa de UFs
    uf_map = {
        12: "ACRE", 27: "ALAGOAS", 16: "AMAPA", 13: "AMAZONAS",
        29: "BAHIA", 23: "CEARA", 53: "DF",
        32: "ESPIRITO SANTO", 52: "GOIAS", 21: "MARANHAO",
        51: "MATO GROSSO", 50: "MATO GROSSO DO SUL", 31: "MINAS GERAIS",
        15: "PARA", 25: "PARAIBA", 41: "PARANA",
        26: "PERNAMBUCO", 22: "PIAUI", 24: "RIO GRANDE DO NORTE",
        43: "RIO GRANDE DO SUL", 33: "RIO DE JANEIRO", 11: "RONDONIA",
        14: "RORAIMA", 42: "SANTA CATARINA", 35: "SAO PAULO",
        28: "SERGIPE", 17: "TOCANTINS"
    }

    # Mapa de raça/cor
    raca_map = {
        1: "BRANCA", 2: "PRETA", 3: "AMARELA",
        4: "PARDA", 5: "INDIGENA", 9: "IGNORADO"
    }

    # Mapa do local de ocorrência
    local_ocor_map = {
        1: "RESIDENCIA", 2: "HABITACAO COLETIVA", 3: "ESCOLA",
        4: "LOCAL DE PRATICA ESPORTIVA", 5: "BAR OU SIMILAR",
        6: "VIA PUBLICA", 7: "COMERCIO/SERVICOS",
        8: "INDUSTRIAS/CONSTRUCAO", 9: "OUTRO", 99: "IGNORADO"
    }

    # Mapa de orientação sexual
    orient_sex_map = {
        1: "HETEROSSEXUAL", 2: "HOMOSSEXUAL", 3: "BISSEXUAL",
        8: "NAO SE APLICA", 9: "IGNORADO"
    }

    # Mapa de escolaridade
    escolaridade_map = {
        0: VALOR_NAO_INFORMADO,
        1: "1ª a 4ª série incompleta do EF",
        2: "4ª série completa do EF (antigo 1° grau)",
        3: "5ª a 8ª série incompleta do EF (antigo ginásio ou 1° grau)",
        4: "Ensino fundamental completo (antigo ginásio ou 1° grau)",
        5: "Ensino médio incompleto (antigo colegial ou 2° grau)",
        6: "Ensino médio completo (antigo colegial ou 2° grau)",
        7: "Educação superior incompleta",
        8: "Educação superior completa",
        9: "Ignorado",
        10: "Não se aplica",
        43: "Analfabeto"
    }

    # Mapa de motivação da violência
    viol_motivo_map = {
        1: "SEXISMO", 2: "HOMOFOBIA/LESBOFOBIA/BIFOBIA/TRANSFOBIA",
        3: "RACISMO", 4: "INTOLERANCIA RELIGIOSA", 5: "XENOFOBIA",
        6: "CONFLITO GERACIONAL", 7: "SITUACAO DE RUA",
        8: "DEFICIENCIA", 9: "OUTROS", 88: "NAO SE APLICA",
        99: "IGNORADO"
    }

    # Mapa do número de envolvidos
    num_envolv_map = {
        1: "UM", 2: "DOIS OU MAIS", 9: "IGNORADO"
    }

    # Mapa de identidade de gênero
    ident_gen_map = {
        1: "TRAVESTI", 2: "TRANSEXUAL MULHER", 3: "TRANSEXUAL HOMEM",
        8: "NAO SE APLICA", 9: "IGNORADO"
    }

    # Mapa de sexo do autor
    autor_sexo_map = {
        1: "MASCULINO", 2: "FEMININO", 3: "AMBOS DOS SEXOS", 9: "IGNORADO"
    }

    # Mapa de ciclo de vida
    ciclo_vida_map = {
        1: "CRIANCA", 2: "ADOLESCENTE", 3: "JOVEM",
        4: "PESSOA ADULTA", 5: "PESSOA IDOSA", 9: "IGNORADO"
    }

    # Aplica os mapas principais
    df_sinan = aplicar_mapa_coluna(df_sinan, "ESTADO_NOTIFICACAO", uf_map)
    df_sinan = aplicar_mapa_coluna(df_sinan, "SG_UF", uf_map)
    df_sinan = aplicar_mapa_coluna(df_sinan, "CS_RACA", raca_map)
    df_sinan = aplicar_mapa_coluna(df_sinan, "LOCAL_OCOR", local_ocor_map)
    df_sinan = aplicar_mapa_coluna(df_sinan, "ORIENT_SEX", orient_sex_map)
    df_sinan = aplicar_mapa_coluna(df_sinan, "ESCOLARIDADE", escolaridade_map)
    df_sinan = aplicar_mapa_coluna(df_sinan, "VIOL_MOTIV", viol_motivo_map)
    df_sinan = aplicar_mapa_coluna(df_sinan, "NUM_ENVOLV", num_envolv_map)
    df_sinan = aplicar_mapa_coluna(df_sinan, "IDENT_GEN", ident_gen_map)
    df_sinan = aplicar_mapa_coluna(df_sinan, "AUTOR_SEXO", autor_sexo_map)
    df_sinan = aplicar_mapa_coluna(df_sinan, "CICL_VID", ciclo_vida_map)

    # Colunas com respostas SIM/NAO/IGNORADO
    colunas_resposta_geral = [
        "DEF_TRANS", "DEF_FISICA", "DEF_MENTAL", "VIOL_FISIC", "VIOL_PSICO",
        "VIOL_TORT", "VIOL_SEXU", "VIOL_TRAF", "VIOL_FINAN", "VIOL_NEGLI",
        "VIOL_INFAN", "REL_PAI", "REL_MAE", "REL_PAD", "REL_MAD", "REL_CONJ",
        "REL_EXCON", "REL_NAMO", "REL_EXNAM", "REL_IRMAO", "REL_FILHO",
        "REL_CONHEC", "REL_DESCO", "REL_PATRAO", "REL_INST", "REL_POL",
        "ENC_SAUDE", "ASSIST_SOC", "REDE_EDUCA", "ATEND_MULH", "CONS_TUTEL",
        "CONS_IDO", "DIR_HUMAN", "MPU", "DELEG_IDOS", "REL_TRAB",
        "AG_FORCA", "AG_ENFOR", "AG_OBJETO", "AG_CORTE", "AG_QUENTE",
        "AG_ENVEN", "AG_FOGO", "AG_AMEACA", "DELEG_MULH", "DELEG_CRIA",
        "INFAN_JUV", "DEFEN_PUBL", "DEF_VISUAL", "DEF_AUDITI", "TRAN_MENT"
    ]

    # Mapa geral de respostas
    resposta_geral_map = {
        1: "SIM", 2: "NAO", 8: "NAO SE APLICA", 9: "IGNORADO"
    }

    # Aplica o mapa geral
    for coluna in colunas_resposta_geral:
        df_sinan = aplicar_mapa_coluna(df_sinan, coluna, resposta_geral_map)

    # Colunas específicas de violência sexual
    colunas_sexuais = ["SEX_ASSEDI", "SEX_ESTUPR", "SEX_PORNO", "SEX_EXPLO"]

    # Aplica o mapa nas colunas sexuais
    for coluna in colunas_sexuais:
        df_sinan = aplicar_mapa_coluna(df_sinan, coluna, resposta_geral_map)

    # Cria a coluna de idade interpretada
    print("Aplicando interpretação da idade...", flush=True)
    df_sinan["IDADE_REAL"] = df_sinan["CODIGO_IDADE"].apply(interpretar_idade_formatada)

    # Posiciona IDADE_REAL logo após CODIGO_IDADE
    posicao_idade = df_sinan.columns.get_loc("CODIGO_IDADE") + 1
    coluna_idade_real = df_sinan.pop("IDADE_REAL")
    df_sinan.insert(posicao_idade, "IDADE_REAL", coluna_idade_real)

    # Conta duplicatas antes da remoção
    linhas_iniciais = df_sinan.shape[0]
    quantidade_duplicatas = df_sinan.duplicated().sum()

    # Exibe diagnóstico de duplicatas
    print(f"\nTotal antes da deduplicação: {linhas_iniciais}", flush=True)
    print(f"Duplicatas encontradas: {quantidade_duplicatas}", flush=True)

    # Remove duplicatas exatas
    if quantidade_duplicatas > 0:
        df_sinan = df_sinan.drop_duplicates(ignore_index=True)
        print(f"Duplicatas removidas: {linhas_iniciais - df_sinan.shape[0]}", flush=True)
    else:
        print("Nenhuma duplicata exata encontrada.", flush=True)

    # Cria ID único do SINAN na primeira coluna
    df_sinan.insert(0, "ID_SINAN", range(1, len(df_sinan) + 1))

    # Substitui códigos de município pelos nomes usando o IBGE tratado
    print("Substituindo códigos de município pelos nomes...", flush=True)
    df_sinan = substituir_codigos_municipios(df_sinan)

    # Substitui código da unidade pelo nome da unidade usando o CNES tratado
    print("Substituindo código da unidade pelo nome da unidade...", flush=True)
    df_sinan = substituir_codigos_unidades(df_sinan)

    # Prepara campos necessários para cruzamento com SDS
    df_sinan = preparar_sinan_para_cruzamento(df_sinan)

    # Padroniza valores inválidos em todas as colunas finais
    df_sinan = normalizar_dataframe_final(
        df_sinan,
        colunas_excecao=["ID_SINAN"],
        colunas_zero_valido=["IDADE_NUMERICA_EM_ANOS"]
    )

    # Garante tipos numéricos reais na base Silver do SINAN
    # Mantém como texto apenas códigos, categorias e descrições
    colunas_inteiras = [
        "ID_SINAN",
        "NU_ANO",
        "ANO_NASC",
        "IDADE_NUMERICA_EM_ANOS",
    ]

    for coluna in colunas_inteiras:
        if coluna in df_sinan.columns:
            df_sinan[coluna] = pd.to_numeric(
                df_sinan[coluna],
                errors="coerce"
            ).astype("Int64")

    # Define o caminho de saída
    caminho_saida = SINAN_SILVER / "base_sinan_tratada.parquet"

    # Salva a base tratada em Parquet
    df_sinan.to_parquet(
        caminho_saida,
        index=False,
        engine="pyarrow",
        compression="snappy"
    )

    # Exibe resumo final
    print(f"\nBase SINAN tratada salva em: {caminho_saida}", flush=True)
    print(f"Total final: {df_sinan.shape[0]} linhas e {df_sinan.shape[1]} colunas.", flush=True)

    # Retorna o caminho do arquivo salvo
    return caminho_saida


# %%
# Permite executar o arquivo diretamente pelo terminal
if __name__ == "__main__":
    tratar_sinan()