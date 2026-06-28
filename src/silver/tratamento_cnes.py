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
from src.config import CNES_BRONZE, CNES_SILVER


# %%
# Valor padrão para dados ausentes ou inválidos
VALOR_NAO_INFORMADO = "DADO NÃO INFORMADO"

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
def normalizar_valor_invalido(valor):
    """
    Padroniza valores vazios ou inválidos como DADO NÃO INFORMADO.
    """

    # Trata nulos reais do pandas
    if pd.isna(valor):
        return VALOR_NAO_INFORMADO

    # Trata zero numérico como inválido
    if isinstance(valor, (int, float)) and valor == 0:
        return VALOR_NAO_INFORMADO

    # Converte para texto e remove espaços
    valor_texto = str(valor).strip()

    # Remove .0 de textos numéricos
    if valor_texto.endswith(".0"):
        valor_texto_sem_decimal = valor_texto[:-2]
    else:
        valor_texto_sem_decimal = valor_texto

    # Verifica se o valor é inválido
    if valor_texto in VALORES_INVALIDOS_TEXTO:
        return VALOR_NAO_INFORMADO

    # Verifica se o valor sem .0 é inválido
    if valor_texto_sem_decimal in VALORES_INVALIDOS_TEXTO:
        return VALOR_NAO_INFORMADO

    # Retorna o valor original se for válido
    return valor_texto


# %%
def padronizar_codigo_cnes(valor):
    """
    Padroniza o código CNES para cruzar com o ID_UNIDADE do SINAN.
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
def padronizar_texto(valor):
    """
    Padroniza textos para maiúsculo e remove espaços extras.
    """

    # Trata valores inválidos
    valor = normalizar_valor_invalido(valor)

    # Retorna padrão se for inválido
    if valor == VALOR_NAO_INFORMADO:
        return VALOR_NAO_INFORMADO

    # Padroniza texto
    return str(valor).strip().upper()


# %%
def escolher_nome_unidade(linha):
    """
    Escolhe o melhor nome da unidade.
    Prioriza NO_FANTASIA e usa NO_RAZAO_SOCIAL como alternativa.
    """

    # Padroniza o nome fantasia
    nome_fantasia = padronizar_texto(linha.get("NO_FANTASIA"))

    # Se o nome fantasia for válido, usa ele
    if nome_fantasia != VALOR_NAO_INFORMADO:
        return nome_fantasia

    # Caso contrário, usa a razão social
    razao_social = padronizar_texto(linha.get("NO_RAZAO_SOCIAL"))

    # Retorna razão social ou dado não informado
    return razao_social


# %%
def tratar_cnes():
    """
    Trata a base CNES e salva uma base auxiliar para cruzar com o SINAN.
    """

    # Cria a pasta silver do CNES caso ainda não exista
    CNES_SILVER.mkdir(parents=True, exist_ok=True)

    # Define o caminho de entrada
    caminho_entrada = CNES_BRONZE / "parquet" / "cnes_estabelecimentos.parquet"

    # Verifica se o arquivo existe
    if not caminho_entrada.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_entrada}")

    # Lê a base CNES bronze
    df = pd.read_parquet(caminho_entrada)

    # Exibe tamanho inicial
    print(f"Base CNES bronze: {df.shape[0]} linhas e {df.shape[1]} colunas.", flush=True)

    # Define as colunas necessárias
    colunas_necessarias = [
        "CO_CNES",
        "CO_UNIDADE",
        "CO_UF",
        "CO_IBGE",
        "NO_FANTASIA",
        "NO_RAZAO_SOCIAL",
        "TP_UNIDADE"
    ]

    # Verifica colunas ausentes
    colunas_ausentes = [
        coluna for coluna in colunas_necessarias
        if coluna not in df.columns
    ]

    # Interrompe se faltar alguma coluna
    if colunas_ausentes:
        raise ValueError(f"Colunas ausentes no CNES: {colunas_ausentes}")

    # Mantém apenas as colunas úteis
    df_cnes = df[colunas_necessarias].copy()

    # Filtra apenas Pernambuco
    df_cnes = df_cnes[
        pd.to_numeric(df_cnes["CO_UF"], errors="coerce") == 26
    ].copy()

    # Cria o ID_UNIDADE compatível com o SINAN
    df_cnes["ID_UNIDADE"] = df_cnes["CO_CNES"].apply(padronizar_codigo_cnes)

    # Cria o nome final da unidade
    df_cnes["NOME_UNIDADE"] = df_cnes.apply(escolher_nome_unidade, axis=1)

    # Padroniza os demais campos úteis
    df_cnes["CO_CNES"] = df_cnes["CO_CNES"].apply(padronizar_codigo_cnes)
    df_cnes["CO_UNIDADE"] = df_cnes["CO_UNIDADE"].apply(normalizar_valor_invalido).astype(str)
    df_cnes["CO_UF"] = df_cnes["CO_UF"].apply(normalizar_valor_invalido).astype(str)
    df_cnes["CO_IBGE"] = df_cnes["CO_IBGE"].apply(normalizar_valor_invalido).astype(str)
    df_cnes["TP_UNIDADE"] = df_cnes["TP_UNIDADE"].apply(normalizar_valor_invalido).astype(str)
    df_cnes["NO_RAZAO_SOCIAL"] = df_cnes["NO_RAZAO_SOCIAL"].apply(padronizar_texto)

    # Mantém apenas registros com ID_UNIDADE válido
    df_cnes = df_cnes[
        df_cnes["ID_UNIDADE"] != VALOR_NAO_INFORMADO
    ].copy()

    # Mantém apenas registros com nome válido
    df_cnes = df_cnes[
        df_cnes["NOME_UNIDADE"] != VALOR_NAO_INFORMADO
    ].copy()

    # Remove duplicatas pelo ID_UNIDADE
    df_cnes = df_cnes.drop_duplicates(
        subset=["ID_UNIDADE"],
        keep="first",
        ignore_index=True
    )

    # Seleciona e ordena as colunas finais
    df_cnes = df_cnes[
        [
            "ID_UNIDADE",
            "NOME_UNIDADE",
            "CO_CNES",
            "CO_UNIDADE",
            "CO_UF",
            "CO_IBGE",
            "TP_UNIDADE",
            "NO_RAZAO_SOCIAL"
        ]
    ]

    # Define o caminho de saída
    caminho_saida = CNES_SILVER / "unidades_tratadas.parquet"

    # Salva a base tratada
    df_cnes.to_parquet(
        caminho_saida,
        index=False,
        engine="pyarrow",
        compression="snappy"
    )

    # Exibe resumo final
    print(f"\nBase CNES tratada salva em: {caminho_saida}", flush=True)
    print(f"Total final: {df_cnes.shape[0]} linhas e {df_cnes.shape[1]} colunas.", flush=True)

    # Retorna o caminho salvo
    return caminho_saida


# %%
# Permite executar o arquivo diretamente pelo terminal
if __name__ == "__main__":
    tratar_cnes()