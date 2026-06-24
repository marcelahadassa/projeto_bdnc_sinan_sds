# %%
import pandas as pd

# %%
# lista vazia para guardar os dados
lista_dfs = []

# loop que vai do número 14 até o 24 (anos das planilhas)
for ano in range(14, 25):
    caminho = f"../data/raw/VIOLBR{ano}.csv"
    print(f"Carregando: {caminho}...")
    
    # leitura dos arquivos
    df_temp = pd.read_csv(caminho, index_col=False, low_memory=False)
    
    # a coluna com o ano de 2020 estava vazia e precisou ser preenchida com o ano correto
    ano_completo = 2000 + ano
    df_temp["NU_ANO"] = ano_completo
    
    # 4. Adiciona esse DataFrame na nossa lista
    lista_dfs.append(df_temp)

# criação do df
df = pd.concat(lista_dfs, ignore_index=True)

print(f"\ndf final tem {len(df)} linhas.")

# %%
# renomeando as colunas
df_colunas_renomeadas = df.rename(columns={
    "NU_IDADE_N": "CODIGO_IDADE",
    "ID_MN_RESI": "ID_MUNIC_RESI",
    "CS_SEXO": "SEXO",
    "SG_UF_NOT": "ESTADO_NOTIFICACAO", 
    "CS_ESCOL_N": "ESCOLARIDADE",
})

# %%
# TRADUÇÕES

# colunas específicas e úteis para análise
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

# %%
# filtragem dos registros pelo estado e sexo
df_feminino_pe = df_colunas_renomeadas[
        (df_colunas_renomeadas["ESTADO_NOTIFICACAO"] == 26) & 
        (df_colunas_renomeadas["SG_UF"] == 26) & 
        (df_colunas_renomeadas["SEXO"] == "F")
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
df_feminino_pe["SG_UF"] = df_feminino_pe["SG_UF"].replace(uf_map)
# %%
# renomeando células relacionadas às raças
raca_map = {
    1.0: "BRANCA", 2.0: "PRETA", 3.0: "AMARELA",
    4.0: "PARDA", 5.0: "INDIGENA", 9.0: "IGNORADO"
}
df_feminino_pe["CS_RACA"] = df_feminino_pe["CS_RACA"].replace(raca_map)

# %%
local_ocor_map = {
    1: "RESIDENCIA", 2: "HABITACAO COLETIVA", 3: "ESCOLA",
    4: "LOCAL DE PRATICA ESPORTIVA", 5: "BAR OU SIMILAR", 6: "VIA PUBLICA",
    7: "COMERCIO/SERVICOS", 8: "INDUSTRIAS/CONSTRUCAO", 9: "OUTRO", 
    99: "IGNORADO"
}
df_feminino_pe["LOCAL_OCOR"] = df_feminino_pe["LOCAL_OCOR"].replace(local_ocor_map)

# %%
orient_sex_map = {
    1: "HETEROSSEXUAL", 2: "HOMOSSEXUAL", 3: "BISSEXUAL",
    8: "NAO SE APLICA", 9: "IGNORADO"
}

df_feminino_pe["ORIENT_SEX"] = df_feminino_pe["ORIENT_SEX"].replace(orient_sex_map)

#%%
escolaridade_map = {
    0: 'DADO NÃO INFORMADO',
    0.0: 'DADO NÃO INFORMADO',
    1: '1ª a 4ª série incompleta do EF',
    2: '4ª série completa do EF (antigo 1° grau)',
    3: '5ª a 8ª série incompleta do EF (antigo ginásio ou 1° grau)',
    4: 'Ensino fundamental completo (antigo ginásio ou 1° grau)',
    5: 'Ensino médio incompleto (antigo colegial ou 2° grau)',
    6: 'Ensino médio completo (antigo colegial ou 2° grau)',
    7: 'Educação superior incompleta',
    8: 'Educação superior completa',
    9: 'Ignorado',
    10: 'Não se aplica',
    43: 'Analfabeto'
}

df_feminino_pe["ESCOLARIDADE"] = df_feminino_pe["ESCOLARIDADE"].replace(escolaridade_map)

# %%
viol_motivo_map = {
    1: "SEXISMO", 2: "HOMOFOBIA/LESBOFOBIA/BIFOBIA/TRANSFOBIA", 3: "RACISMO",
    4: "INTOLERANCIA RELIGIOSA", 5: "XENOFOBIA", 6: "CONFLITO GERACIONAL", 
    7: "SITUACAO DE RUA", 8: "DEFICIENCIA", 9: "OUTROS", 88: "NAO SE APLICA",
    99: "IGNORADO"
}

df_feminino_pe["VIOL_MOTIV"] = df_feminino_pe["VIOL_MOTIV"].replace(viol_motivo_map)


# %%
num_envolv_map = {
    1: "UM", 2: "DOIS OU MAIS", 9: "IGNORADO"
}
df_feminino_pe["NUM_ENVOLV"] = df_feminino_pe["NUM_ENVOLV"].replace(num_envolv_map)

# %%
identi_gen_map = {
    1: "TRAVESTI", 2: "TRANSEXUAL MULHER", 3: "TRANSEXUAL HOMEM", 8: "NAO SE APLICA", 9: "IGNORADO"
}
df_feminino_pe["IDENT_GEN"] = df_feminino_pe["IDENT_GEN"].replace(identi_gen_map)

# %%
autor_sexo_map = {
    1: "MASCULINO", 2: "FEMININO", 3: "AMBOS DOS SEXOS", 9: "IGNORADO"
}
df_feminino_pe["AUTOR_SEXO"] = df_feminino_pe["AUTOR_SEXO"].replace(autor_sexo_map)

# %%
ciclo_vida_map = {
    1: "CRIANCA", 2: "ADOLESCENTE", 3: "JOVEM", 4: "PESSOA ADULTA",
    5: "PESSOA IDOSA", 9: "IGNORADO"
}
df_feminino_pe["CICL_VID"] = df_feminino_pe["CICL_VID"].replace(ciclo_vida_map)


# %%
colunas1 = [
    "DEF_TRANS", "DEF_FISICA", "DEF_MENTAL", "VIOL_FISIC", "VIOL_PSICO", 
    "VIOL_TORT", "VIOL_SEXU", "VIOL_TRAF", "VIOL_FINAN", "VIOL_NEGLI", 
    "VIOL_INFAN", "REL_PAI", "REL_MAE", "REL_PAD", "REL_MAD", "REL_CONJ", 
    "REL_EXCON", "REL_NAMO", "REL_EXNAM", "REL_IRMAO", "REL_FILHO", "REL_CONHEC", 
    "REL_DESCO", "REL_PATRAO", "REL_INST", "REL_POL", "ENC_SAUDE", 
    "ASSIST_SOC", "REDE_EDUCA", "ATEND_MULH", "CONS_TUTEL", "CONS_IDO", 
    "DIR_HUMAN", "MPU", "DELEG_IDOS", "REL_TRAB", "AG_FORCA", 
    "AG_ENFOR", "AG_OBJETO", "AG_CORTE", "AG_QUENTE", "AG_ENVEN", 
    "AG_FOGO", "AG_AMEACA", "DELEG_MULH", "DELEG_CRIA", "INFAN_JUV", "DEFEN_PUBL",
    "DEF_VISUAL", "DEF_AUDITI", "TRAN_MENT"
]
map_geral1 = {
    1: "SIM", 2: "NAO", 8: "NAO SE APLICA", 9: "IGNORADO"
}

df_feminino_pe[colunas1] = df_feminino_pe[colunas1].replace(map_geral1)
# %%

map_geral2 = {
    1: "SIM", 2: "NAO", 8: "NAO SE APLICA", 9: "IGNORADO"
}
colunas_sexuais = ["SEX_ASSEDI", "SEX_ESTUPR", "SEX_PORNO", "SEX_EXPLO"]
df_feminino_pe[colunas_sexuais] = df_feminino_pe[colunas_sexuais].replace(map_geral2)


# %%
def interpretar_idade_formatada(idade_codificada):
    """
    Interpreta um código de idade e retorna uma string formatada.
    Ex: 4023 -> '23 anos', 3007 -> '7 meses'.
    Trata o valor 0 ou nulos como None (campo vazio).
    """
    # 1. Checa se é nulo nativo do Pandas (NaN, NaT, None)
    if pd.isna(idade_codificada):
        return "DADO NÃO INFORMADO"

    # 2. Conversão segura para inteiro (limpa floats tipo 4023.0 e strings com espaços)
    try:
        idade_int = int(float(idade_codificada))
    except (ValueError, TypeError):
        return "DADO NÃO INFORMADO"

    # NOVA CONDIÇÃO: Se o código de idade for igual a 0, trata como nulo
    if idade_int == 0:
        return "DADO NÃO INFORMADO"

    # Converte para string para analisar os dígitos de unidade e quantidade
    idade_str = str(idade_int)

    # O código deve ter pelo menos 2 dígitos (1 para unidade, 1+ para quantidade)
    if len(idade_str) < 2:
        return "DADO NÃO INFORMADO"

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
            # Unidades fora do padrão (ex: 5, 6...) também viram nulo
            return "DADO NÃO INFORMADO"

    except (ValueError, IndexError):
        return "DADO NÃO INFORMADO"

# %%
print("Aplicando a interpretation de idade com tratamento de zeros...")
df_feminino_pe["IDADE_REAL"] = df_feminino_pe["CODIGO_IDADE"].apply(interpretar_idade_formatada)

# %%
# Reposicionando a coluna logo após a coluna original CODIGO_IDADE
descobrir_col = df_feminino_pe.columns.get_loc("CODIGO_IDADE") + 1

rmv_coluna_idade = df_feminino_pe.pop("IDADE_REAL")
df_feminino_pe.insert(descobrir_col, "IDADE_REAL", rmv_coluna_idade)

# %%
# verificação de qualidade: checagem e remoção de duplicatas exatas
linhas_iniciais = df_feminino_pe.shape[0]
quantidade_duplicatas = df_feminino_pe.duplicated().sum()

print(f"\nTotal de registros antes da deduplicação: {linhas_iniciais}")
print(f"Linhas duplicadas encontradas: {quantidade_duplicatas}")

if quantidade_duplicatas > 0:
    df_feminino_pe = df_feminino_pe.drop_duplicates(ignore_index=True)
    linhas_removidas = linhas_iniciais - df_feminino_pe.shape[0]
    print(f"Sucesso! {linhas_removidas} registros duplicados foram removidos.")
else:
    print("Nenhuma duplicata exata encontrada.")

# %%
# criação do ID único (chave artificial SINAN)
print("\nGerando IDs numéricos únicos para a base limpa do SINAN...")
df_feminino_pe.insert(0, "ID_SINAN", range(1, len(df_feminino_pe) + 1))

# %%
# preenchendo todos os valores nulos/vazios restantes no dataframe com "DADO NÃO INFORMADO"
df_feminino_pe = df_feminino_pe.fillna("DADO NÃO INFORMADO")

# %%
df_feminino_pe.head(10)
# %%
df_feminino_pe.to_excel("../new_data/BASE_SINAN_TRATADA_teste.xlsx", index=False)
# %%
contagem_linhas1 = df_feminino_pe.shape[0]
print(contagem_linhas1)
# %%