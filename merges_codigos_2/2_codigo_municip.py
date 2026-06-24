# %%
import pandas as pd

#%%
# arquivos
df = pd.read_excel("../new_data/BASE_SINAN_TRATADA.xlsx")  
df_municipios = pd.read_csv("../data/raw/municipios.csv")

# %%
# tipos corretos
df_municipios["code_mni"] = df_municipios["code_mni"].astype(float)

cols = ["ID_MUNICIP", "ID_MUNIC_RESI", "ID_MN_OCOR"]
for col in cols:
    # usamos to_numeric para forçar a conversão e ignorar temporariamente os textos
    df[col] = pd.to_numeric(df[col], errors='coerce')

# %%
# função para substituir a coluna pelo nome
def substituir_codigo_por_nome(df, col, municipios):
    temp = df.merge(
        municipios,
        how="left",
        left_on=col,
        right_on="code_mni"
    )
    # substitui a coluna original pelo nome
    temp[col] = temp["name_muni"]
    # remove colunas auxiliares
    temp = temp.drop(columns=["code_mni", "name_muni"])
    return temp 

# %%
# aplicar para cada coluna
for col in cols:
    df = substituir_codigo_por_nome(df, col, df_municipios)
    # devolvemos o texto padrão para onde não houve cruzamento (os antigos nulos/textos)
    df[col] = df[col].fillna("DADO NÃO INFORMADO")

# %%
df.head(20)

# %%
df.to_excel("../new_data/BASE_SINAN_TRATADA_MUNICIP.xlsx", index=False)
# %%