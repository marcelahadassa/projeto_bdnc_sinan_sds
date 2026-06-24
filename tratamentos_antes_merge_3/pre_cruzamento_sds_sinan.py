#%%
import pandas as pd

#%%
# leitura das bases de dados
df_sinan = pd.read_parquet('../new_data//BASE_SINAN_TRATADA_PRE_CRUZAMENTO.parquet')
df_sds = pd.read_parquet('../new_data/SDS_PRE_CRUZAMENTO.parquet')

#%%
# conversão para datetime da coluna de data de ocorrência na planilha do SDS)
df_sinan['DT_OCOR'] = pd.to_datetime(df_sinan['DT_OCOR'], errors='coerce')
df_sds['DT_OCOR'] = pd.to_datetime(df_sds['DT_OCOR'], errors='coerce')

# conversão para datetime da data de notificação no SINAN
df_sinan['DT_NOTIFIC'] = pd.to_datetime(df_sinan['DT_NOTIFIC'], errors='coerce')

# map para tradução dos dias da semana
dias_pt = {
    'Monday': 'Segunda', 'Tuesday': 'Terça', 'Wednesday': 'Quarta', 
    'Thursday': 'Quinta', 'Friday': 'Sexta', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
}

#%%
# colunas de sazonalidade e tempo de resposta para o SINAN (pode ser util em analises futuras)
df_sinan['MES_OCORRENCIA'] = df_sinan['DT_OCOR'].dt.month
df_sinan['DIA_SEMANA'] = df_sinan['DT_OCOR'].dt.day_name().map(dias_pt)

# dias entre a data de ocorrência e a data de notificação
df_sinan['DIAS_ATRASO_BUSCA_AJUDA'] = (df_sinan['DT_NOTIFIC'] - df_sinan['DT_OCOR']).dt.days

#%%
# colunas de sazonalidade e tempo de resposta para o SDS (pode ser util em analises futuras)
df_sds['MES_OCORRENCIA'] = df_sds['DT_OCOR'].dt.month
df_sds['DIA_SEMANA'] = df_sds['DT_OCOR'].dt.day_name().map(dias_pt)

#%%
# verificação
print("\nAmostra SINAN (Sazonalidade e Tempo de Resposta):")
print(df_sinan[['DT_OCOR', 'DT_NOTIFIC', 'DIAS_ATRASO_BUSCA_AJUDA', 'DIA_SEMANA']].head())

print("\nAmostra SDS (Sazonalidade):")
print(df_sds[['DT_OCOR', 'MES_OCORRENCIA', 'DIA_SEMANA']].head())

# %%
# agrupamento da base do SDS somando o total de vítimas por município, ano, sexo e faixa etária
sds_agrupado = df_sds.groupby(
    ['ID_MUNICIP', 'ANO', 'SEXO', 'FAIXA_ETARIA_SDS']
)['TOTAL DE VÍTIMAS'].sum().reset_index(name='TOTAL_CASOS_SDS')

#%%
# agrupamento da base do SINAN
sinan_agrupado = df_sinan.groupby(
    ['ID_MUNICIP', 'NU_ANO', 'SEXO', 'FAIXA_ETARIA_SDS']
).size().reset_index(name='TOTAL_CASOS_SINAN')
#%%
# salvamento em parquet
df_sinan.to_parquet('../new_data/BASE_SINAN_TRATADA_FINAL.parquet', index=False)
df_sds.to_parquet('../new_data/BASE_SDS_TRATADA_FINAL.parquet', index=False)
#%%