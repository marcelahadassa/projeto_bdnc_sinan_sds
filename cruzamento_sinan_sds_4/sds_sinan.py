# %%
import pandas as pd

# leitura das bases 
df_sinan_raw = pd.read_parquet("../new_data/BASE_SINAN_FINAL.parquet")
df_sds_raw = pd.read_parquet("../new_data/BASE_SDS_FINAL.parquet")

# padronização das colunas de município, ano, sexo e faixa etária para garantir que o merge funcione corretamente
#%%
# garantia que os nomes dos municípios estejam iguais, sem espaços e em caixa alta
df_sinan_raw["ID_MUNICIP"] = df_sinan_raw["ID_MUNICIP"].astype(str).str.upper().str.strip()
df_sds_raw["ID_MUNICIP"] = df_sds_raw["ID_MUNICIP"].astype(str).str.upper().str.strip()

# alinhando a coluna de ano para float64, garantindo que não haja problemas de tipo no merge
# coluna ANO unificada 
df_sinan_raw["ANO"] = df_sinan_raw["NU_ANO"].astype("float64") 
df_sds_raw["ANO"] = df_sds_raw["ANO"].astype("float64")

# alinhando sexo
df_sinan_raw["SEXO"] = df_sinan_raw["SEXO"].astype(str).str.upper().str.strip()
df_sds_raw["SEXO"] = df_sds_raw["SEXO"].astype(str).str.upper().str.strip()

# alinhando faixa etaria
df_sinan_raw["FAIXA_ETARIA_SDS"] = df_sinan_raw["FAIXA_ETARIA_SDS"].astype(str).str.upper().str.strip()
df_sds_raw["FAIXA_ETARIA_SDS"] = df_sds_raw["FAIXA_ETARIA_SDS"].astype(str).str.upper().str.strip()

# padronizando valores de faixa etária para "DADO NÃO INFORMADO" quando estiverem vazios ou com valores nulos
df_sinan_raw["FAIXA_ETARIA_SDS"] = df_sinan_raw["FAIXA_ETARIA_SDS"].replace(["", "NAN", "NULL", "NONE", "(VAZIO)"], "DADO NAO INFORMADO")
df_sds_raw["FAIXA_ETARIA_SDS"] = df_sds_raw["FAIXA_ETARIA_SDS"].replace(["", "NAN", "NULL", "NONE", "(VAZIO)"], "DADO NAO INFORMADO")

#%%
# chaves para o merge
chaves_grupo = ["ID_MUNICIP", "ANO", "SEXO", "FAIXA_ETARIA_SDS"]

# agrupando e contando volumes do SDS
df_sds_grouped = (
    df_sds_raw.groupby(chaves_grupo, dropna=False)
    .size()
    .reset_index(name="TOTAL_CASOS_SDS")
)

# agrupando e contando volumes do SINAN
df_sinan_grouped = (
    df_sinan_raw.groupby(chaves_grupo, dropna=False)
    .size()
    .reset_index(name="TOTAL_CASOS_SINAN")
)

# merge das duas bases agrupadas para criar a tabela final
#%%
# uso do outer merge (full join) para garantir que grupos que só existem na SDS 
# ou só existem no SINAN apareçam na tabela final
df_final = pd.merge(
    df_sds_grouped,
    df_sinan_grouped,
    on=chaves_grupo,
    how="outer"
)

# preenchendo com 0 onde um sistema não teve notificações para o grupo do outro
df_final["TOTAL_CASOS_SDS"] = df_final["TOTAL_CASOS_SDS"].fillna(0).astype("int64")
df_final["TOTAL_CASOS_SINAN"] = df_final["TOTAL_CASOS_SINAN"].fillna(0).astype("int64")

#%%
# reordenando as colunas para a saída final
ordem_colunas = [
    "ID_MUNICIP", "ANO", "SEXO", "FAIXA_ETARIA_SDS", 
    "TOTAL_CASOS_SDS", "TOTAL_CASOS_SINAN"
]
df_final = df_final[ordem_colunas]

# %%
# salvamento em parquet
caminho_saida = "../new_data/SDS_SINAN_FINAL.parquet"

df_final.to_parquet(caminho_saida, index=False)

# verificação
print(f"Total de combinações únicas/linhas: {df_final.shape[0]}")
print(f"Total de Casos SDS computados: {df_final['TOTAL_CASOS_SDS'].sum()}")
print(f"Total de Casos SINAN computados: {df_final['TOTAL_CASOS_SINAN'].sum()}")
print(f"Salvo com sucesso em: {caminho_saida}")
# %%