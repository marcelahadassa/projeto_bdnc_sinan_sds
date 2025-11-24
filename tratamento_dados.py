# %%
import pandas as pd

# %%
# carregando o arquivo csv
df = pd.read_csv("./planilhas/VIOLBR14.csv", index_col=False)

# %%
# renomeando as colunas para torná-las mais intuitivas
df_colunas_renomeadas = df.rename(columns={
   # "TP_UNI_EXT": "TP_UNI_NOTIFIC",
    # "CO_UNI_EXT": "COD_UNI_NOTIFIC",
    #"NM_UNI_EXT": "NOME_UNIDADE",
    "NU_IDADE_N": "CODIGO_IDADE",
    "ID_MN_RESI": "ID_MUNIC_RESI",
    "CS_SEXO": "SEXO",
    "SG_UF_NOT": "ESTADO_NOTIFICACAO", 
})

# %%
# colunas específicas e úteis para análise
colunas_filtradas = [
    "DT_NOTIFIC", "ESTADO_NOTIFICACAO", "NU_ANO", "ID_MUNICIP", "ID_UNIDADE", 
    "DT_OCOR", "ANO_NASC", "CODIGO_IDADE", "SEXO", "CS_RACA", 
    "SG_UF", "ID_MUNIC_RESI", "ID_MN_OCOR",
    "ID_MN_OCOR", "LOCAL_OCOR", "ORIENT_SEX", "IDENT_GEN", 
    "DEF_TRANS", "DEF_FISICA", "DEF_MENTAL", "DEF_VISUAL",
    "DEF_AUDITI", "TRAN_MENT", "VIOL_MOTIV", "VIOL_FISIC",
    "VIOL_PSICO", "VIOL_TORT", "VIOL_SEXU", "VIOL_TRAF",
    "VIOL_FINAN", "VIOL_NEGLI", "VIOL_INFAN", "AG_FORCA",
    "AG_ENFOR", "AG_OBJETO", "AG_CORTE", "AG_QUENTE",
    "AG_ENVEN", "AG_FOGO", "AG_AMEACA", "SEX_ASSEDI",
    "SEX_ESTUPR", "SEX_PORNO", "SEX_EXPLO", "NUM_ENVOLV", 
    "AUTOR_SEXO", "CICL_VID", "REL_PAI", "REL_MAE", "REL_PAD", "REL_MAD", 
    "REL_CONJ", "REL_EXCON", "REL_NAMO", "REL_EXNAM", "REL_IRMAO",
    "REL_FILHO", "REL_CONHEC", "REL_DESCO", "REL_DESCO", 
    "REL_PATRAO", "REL_INST", "REL_POL", "ENC_SAUDE", 
    "ASSIST_SOC", "REDE_EDUCA", "ATEND_MULH", "CONS_TUTEL", 
    "CONS_IDO", "DIR_HUMAN", "MPU", "DELEG_CRIA", "DELEG_MULH", 
    "INFAN_JUV", "DEFEN_PUBL", "DELEG_IDOS", "REL_TRAB",
]

# %%
# filtragem dos registros pelo sexo feminino
df_feminino_pe = df_colunas_renomeadas[
        (df_colunas_renomeadas["SEXO"] == "F") &
        (df_colunas_renomeadas["ESTADO_NOTIFICACAO"] == 26)
        ][colunas_filtradas]
# %%
# renomeando células relacionadas aos estados
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
df_feminino_pe["ESTADO_NOTIFICACAO"] = df_feminino_pe["ESTADO_NOTIFICACAO"].replace(uf_map)

# %%
# renomeando células relacionadas às raças
raca_map = {
    1.0: "BRANCA", 2.0: "PRETA", 3.0: "AMARELA",
    4.0: "PARDA", 5.0: "INDIGENA", 9.0: "IGNORADO"
}
df_feminino_pe["CS_RACA"] = df_feminino_pe["CS_RACA"].replace(raca_map)

# %%
# função para interpretar a idade de acordo com o código em CODIGO_IDADE
def interpretar_idade_formatada(idade_codificada):
    """
    Interpreta um código de idade e retorna uma string formatada.
    Ex: '4023' -> '23 anos', '3007' -> '7 meses'.
    """
    # Retorna None se o valor for nulo, vazio ou não numérico
    if pd.isnull(idade_codificada) or not str(idade_codificada).strip().isnumeric():
        return None

    idade_str = str(int(idade_codificada)) # Converte para int para remover ".0" e depois para string

    # O código deve ter pelo menos 2 dígitos (1 para unidade, 1+ para quantidade)
    if len(idade_str) < 2:
        return None

    try:
        unidade = int(idade_str[0])
        quantidade = int(idade_str[1:])

        if unidade == 1: # Horas
            return f"{quantidade} hora" if quantidade == 1 else f"{quantidade} horas"
        elif unidade == 2: # Dias
            return f"{quantidade} dia" if quantidade == 1 else f"{quantidade} dias"
        elif unidade == 3: # Meses
            return f"{quantidade} mês" if quantidade == 1 else f"{quantidade} meses"
        elif unidade == 4: # Anos
            return f"{quantidade} ano" if quantidade == 1 else f"{quantidade} anos"
        else:
            # Retorna None se a unidade for inválida (diferente de 1, 2, 3 ou 4)
            return None

    except (ValueError, IndexError):
        return None

# %%
df_feminino_pe["IDADE_REAL"] = df_feminino_pe["CODIGO_IDADE"].apply(interpretar_idade_formatada)

# %%
# descobre a posição da coluna CODIGO_IDADE
descobrir_col = df_feminino_pe.columns.get_loc("CODIGO_IDADE") + 1

# remove a coluna idade da posição antiga e a insere na posição desejada
rmv_coluna_idade = df_feminino_pe.pop("IDADE_REAL")
df_feminino_pe.insert(descobrir_col, "IDADE_REAL", rmv_coluna_idade)

# %%
# exibe as 50 primeiras linhas do dataframe
df_feminino_pe.head(50)
# %%
