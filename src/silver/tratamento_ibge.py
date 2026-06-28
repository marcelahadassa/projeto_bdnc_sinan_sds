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
from src.config import IBGE_BRONZE, IBGE_SILVER


# %%
# Valor padrão para dados ausentes ou inválidos
VALOR_NAO_INFORMADO = "DADO NÃO INFORMADO"


# %%
def padronizar_nome_municipio(nome):
    """
    Padroniza o nome do município para texto em maiúsculo.
    """

    # Trata valores nulos
    if pd.isna(nome):
        return VALOR_NAO_INFORMADO

    # Converte para texto, remove espaços e coloca em maiúsculo
    nome_padronizado = str(nome).strip().upper()

    # Trata textos vazios ou inválidos
    if nome_padronizado in ["", "NAN", "NONE", "NULL", "0", "0.0"]:
        return VALOR_NAO_INFORMADO

    # Retorna o nome padronizado
    return nome_padronizado


# %%
def criar_codigo_sinan(codigo_ibge):
    """
    Cria o código de município compatível com o SINAN.
    O IBGE vem com 7 dígitos e o SINAN costuma usar os 6 primeiros.
    Exemplo: 2611606 -> 261160
    """

    # Trata valores nulos
    if pd.isna(codigo_ibge):
        return VALOR_NAO_INFORMADO

    # Tenta converter para inteiro
    try:
        codigo_int = int(float(codigo_ibge))
    except (ValueError, TypeError):
        return VALOR_NAO_INFORMADO

    # Trata zero como dado não informado
    if codigo_int == 0:
        return VALOR_NAO_INFORMADO

    # Converte para texto
    codigo_texto = str(codigo_int)

    # Garante que o código tenha pelo menos 6 dígitos
    if len(codigo_texto) < 6:
        return VALOR_NAO_INFORMADO

    # Retorna os 6 primeiros dígitos usados no SINAN
    return codigo_texto[:6]


# %%
def tratar_ibge():
    """
    Trata a base de municípios do IBGE e salva na camada silver.
    """

    # Cria a pasta silver do IBGE caso ainda não exista
    IBGE_SILVER.mkdir(parents=True, exist_ok=True)

    # Define o caminho de entrada
    caminho_entrada = IBGE_BRONZE / "parquet" / "municipios_ibge.parquet"

    # Verifica se o arquivo existe
    if not caminho_entrada.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_entrada}")

    # Lê o Parquet da camada bronze
    df = pd.read_parquet(caminho_entrada)

    # Exibe o tamanho inicial
    print(f"Base IBGE bronze: {df.shape[0]} linhas e {df.shape[1]} colunas.", flush=True)

    # Define as colunas necessárias
    colunas_necessarias = ["codigo_uf", "codigo_ibge", "nome"]

    # Verifica se as colunas existem
    colunas_ausentes = [
        coluna for coluna in colunas_necessarias
        if coluna not in df.columns
    ]

    # Interrompe se faltar alguma coluna
    if colunas_ausentes:
        raise ValueError(f"Colunas ausentes no IBGE: {colunas_ausentes}")

    # Mantém apenas as colunas úteis
    df_ibge = df[colunas_necessarias].copy()

    # Converte UF para inteiro de forma segura
    df_ibge["codigo_uf"] = pd.to_numeric(
        df_ibge["codigo_uf"],
        errors="coerce"
    ).astype("Int64")

    # Converte código IBGE para inteiro de forma segura
    df_ibge["codigo_ibge"] = pd.to_numeric(
        df_ibge["codigo_ibge"],
        errors="coerce"
    ).astype("Int64")

    # Cria o código compatível com o SINAN
    df_ibge["ID_MUNICIP_SINAN"] = df_ibge["codigo_ibge"].apply(criar_codigo_sinan)

    # Padroniza o nome do município
    df_ibge["NOME_MUNICIPIO"] = df_ibge["nome"].apply(padronizar_nome_municipio)

    # Remove a coluna nome original após padronização
    df_ibge = df_ibge.drop(columns=["nome"])

    # Reordena as colunas finais
    df_ibge = df_ibge[
        [
            "codigo_uf",
            "codigo_ibge",
            "ID_MUNICIP_SINAN",
            "NOME_MUNICIPIO"
        ]
    ]

    # Remove registros sem código SINAN válido
    df_ibge = df_ibge[
        df_ibge["ID_MUNICIP_SINAN"] != VALOR_NAO_INFORMADO
    ].copy()

    # Remove registros sem nome válido
    df_ibge = df_ibge[
        df_ibge["NOME_MUNICIPIO"] != VALOR_NAO_INFORMADO
    ].copy()

    # Remove possíveis duplicatas pelo código compatível com o SINAN
    df_ibge = df_ibge.drop_duplicates(
        subset=["ID_MUNICIP_SINAN"],
        keep="first",
        ignore_index=True
    )

    # Define o caminho de saída
    caminho_saida = IBGE_SILVER / "municipios_tratado.parquet"

    # Salva a base tratada em Parquet
    df_ibge.to_parquet(
        caminho_saida,
        index=False,
        engine="pyarrow",
        compression="snappy"
    )

    # Exibe resumo final
    print(f"\nBase IBGE tratada salva em: {caminho_saida}", flush=True)
    print(f"Total final: {df_ibge.shape[0]} linhas e {df_ibge.shape[1]} colunas.", flush=True)

    # Mostra quantos municípios de Pernambuco ficaram na base
    total_pe = df_ibge[df_ibge["codigo_uf"] == 26].shape[0]
    print(f"Municípios de Pernambuco na base: {total_pe}", flush=True)

    # Retorna o caminho salvo
    return caminho_saida


# %%
# Permite executar o arquivo diretamente pelo terminal
if __name__ == "__main__":
    tratar_ibge()