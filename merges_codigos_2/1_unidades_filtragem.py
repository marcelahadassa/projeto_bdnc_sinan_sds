# %%
import pandas as pd
# %%
# arquivo do cnes
df_cnes = pd.read_excel("tbEstabelecimento202510.xlsx")

# %%
colunas_uteis = [
    "CO_CNES",
    "NO_FANTASIA",
    "NO_RAZAO_SOCIAL",
    "CO_MUNICIPIO_GESTOR",
    "TP_UNIDADE",
    "CO_TIPO_ESTABELECIMENTO"
]

df_cnes = df_cnes[colunas_uteis]

# %%
# filtragem pra garantir que CO_MUNICIPIO_GESTOR começa com 26 (codigo de PE) e é string pra filtrar
df_cnes["CO_MUNICIPIO_GESTOR"] = df_cnes["CO_MUNICIPIO_GESTOR"].astype(str)

df_cnes = df_cnes[df_cnes["CO_MUNICIPIO_GESTOR"].str.startswith("26")]

print("Total de unidades apenas em Pernambuco:", len(df_cnes))

# %%
 # padronização
df_cnes["CO_CNES"] = df_cnes["CO_CNES"].astype(float)
# %%
df_cnes = df_cnes.rename(columns={
    "CO_CNES": "ID_UNIDADE",
    "NO_FANTASIA": "UNIDADE_NOME_FANTASIA",
    "NO_RAZAO_SOCIAL": "UNIDADE_RAZAO_SOCIAL"
})

df_cnes.head()
# %%
df_cnes.to_excel("estabelecimentos_PE_filtrados.xlsx", index=False)