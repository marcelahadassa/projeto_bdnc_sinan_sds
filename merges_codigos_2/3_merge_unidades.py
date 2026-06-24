# %%
import pandas as pd

#%%
# arquivos
df_viol = pd.read_excel("../new_data/BASE_SINAN_TRATADA_MUNICIP.xlsx")
df_cnes = pd.read_excel("../data/raw/estabelecimentos_PE_filtrados.xlsx")

# %%
# padronização de tipos
# usamos to_numeric para forçar a conversão e ignorar temporariamente os textos
df_viol["ID_UNIDADE"] = pd.to_numeric(df_viol["ID_UNIDADE"], errors='coerce')
df_cnes["ID_UNIDADE"] = pd.to_numeric(df_cnes["ID_UNIDADE"], errors='coerce')

# %%
# merge pelo nome da unidade
df_merge = df_viol.merge(
    df_cnes,
    on="ID_UNIDADE",
    how="left"
)

# %%
# criação de nova coluna pra checagem
# já aplicamos o fillna para restaurar o padrão onde não houve cruzamento
df_merge["NOME_UNIDADE"] = df_merge["UNIDADE_NOME_FANTASIA"].fillna("DADO NÃO INFORMADO")

# substituir o conteúdo de id_unidade por unidade_nome_fantasia
df_merge["ID_UNIDADE"] = df_merge["UNIDADE_NOME_FANTASIA"].fillna("DADO NÃO INFORMADO")

# %%
# remoção de colunas que não são necessárias
colunas_para_remover = [
    "UNIDADE_RAZAO_SOCIAL",
    "CO_MUNICIPIO_GESTOR",
    "TP_UNIDADE",
    "CO_TIPO_ESTABELECIMENTO"
]

df_merge = df_merge.drop(columns=colunas_para_remover, errors="ignore")

# %%
df_merge.head(10)

# %%
df_merge.to_excel("../new_data/BASE_TRATADA_SINAN_UNIDADES.xlsx", index=False)
# %%