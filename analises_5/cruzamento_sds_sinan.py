#%%
import pandas as pd

#%%
# 1. Carregar as bases finais (Camada Silver) já tratadas
# Certifique-se de que o caminho das pastas está correto para o seu computador
df_sds = pd.read_excel('../new_data/SDS_TRATADO2.xlsx')
df_sinan = pd.read_excel('../new_data/SINAN_ATUALIZADA_PRE_CRUZAMENTO2.xlsx')

#%%
# 2. Padronização Rigorosa de Tipos de Dados
# Isso previne o erro "int64 vs object" forçando todas as chaves a serem Texto (String)
print("Padronizando chaves de cruzamento...")
df_sds['ANO'] = df_sds['ANO'].astype(str)
df_sinan['NU_ANO'] = df_sinan['NU_ANO'].astype(str)

df_sds['SEXO'] = df_sds['SEXO'].astype(str)
df_sinan['SEXO'] = df_sinan['SEXO'].astype(str)

df_sds['FAIXA_ETARIA_SDS'] = df_sds['FAIXA_ETARIA_SDS'].astype(str)
df_sinan['FAIXA_ETARIA_SDS'] = df_sinan['FAIXA_ETARIA_SDS'].astype(str)

df_sds['ID_MUNICIP'] = df_sds['ID_MUNICIP'].astype(str)
df_sinan['ID_MUNICIP'] = df_sinan['ID_MUNICIP'].astype(str)

#%%
# 3. Agrupamento das Bases
print("Agrupando e contabilizando os casos...")

# SDS: Usamos .sum() porque 1 linha = 1 Boletim de Ocorrência (que pode ter várias vítimas)
sds_agrupado = df_sds.groupby(
    ['ID_MUNICIP', 'ANO', 'SEXO', 'FAIXA_ETARIA_SDS']
)['TOTAL DE VÍTIMAS'].sum().reset_index(name='TOTAL_CASOS_SDS')

# SINAN: Usamos .size() porque 1 linha = 1 Paciente atendido
sinan_agrupado = df_sinan.groupby(
    ['ID_MUNICIP', 'NU_ANO', 'SEXO', 'FAIXA_ETARIA_SDS']
).size().reset_index(name='TOTAL_CASOS_SINAN')

#%%
# 4. O Grande Cruzamento (Merge)
print("Realizando a junção (Outer Merge)...")
df_cruzado = pd.merge(
    sds_agrupado,
    sinan_agrupado,
    left_on=['ID_MUNICIP', 'ANO', 'SEXO', 'FAIXA_ETARIA_SDS'],
    right_on=['ID_MUNICIP', 'NU_ANO', 'SEXO', 'FAIXA_ETARIA_SDS'],
    how='outer'
)

#%%
# 5. Tratamento de Nulos Pós-Cruzamento
print("Realizando limpeza final...")

# Onde não houve registro (NaN), transformamos em zero casos (0)
df_cruzado['TOTAL_CASOS_SDS'] = df_cruzado['TOTAL_CASOS_SDS'].fillna(0).astype(int)
df_cruzado['TOTAL_CASOS_SINAN'] = df_cruzado['TOTAL_CASOS_SINAN'].fillna(0).astype(int)

# Dica de Ouro: Se a linha veio só do SINAN, a coluna 'ANO' da SDS estará vazia.
# Preenchemos os vazios da coluna ANO com os dados da coluna NU_ANO para não perder a data.
df_cruzado['ANO'] = df_cruzado['ANO'].fillna(df_cruzado['NU_ANO'])

# Agora podemos deletar a coluna duplicada com segurança
df_cruzado = df_cruzado.drop(columns=['NU_ANO'])

#%%
print(df_cruzado.head(10))
#%%
# 6. Exportação da Tabela Ouro
caminho_saida = '../new_data/tabela_cruzada_sds_sinan.csv'
df_cruzado.to_csv(caminho_saida, index=False, sep=';', encoding='latin1')


# %%
#%%
# 1. Padronizar os vazios da Idade
df_cruzado['FAIXA_ETARIA_SDS'] = df_cruzado['FAIXA_ETARIA_SDS'].replace(
    ['nan', 'NaN', '<NA>', '(vazio)', 'None', ''], 'Não Informado'
)

#%%
# 2. O TRATAMENTO DE CHOQUE: 
# Arrancamos qualquer menção prévia à palavra "anos" e usamos .strip() para matar os espaços invisíveis
df_cruzado['FAIXA_ETARIA_SDS'] = df_cruzado['FAIXA_ETARIA_SDS'].str.replace('anos', '', case=False).str.strip()

#%%
# 3. Agora que sabemos que a base está limpa (só os números), adicionamos o " anos" com segurança
df_cruzado['FAIXA_ETARIA_SDS'] = df_cruzado['FAIXA_ETARIA_SDS'].apply(
    lambda x: str(x) + ' anos' if str(x) not in ['Não Informado', '65 OU MAIS'] else str(x)
)

#%%
# 4. Salvar direto em Excel para preservar a formatação
#caminho_saida_excel = '../new_data/tabela_final_sds_sinan.xlsx'

# Usamos o to_excel. (Se der erro de módulo, rode 'pip install openpyxl' no terminal)
#df_cruzado.to_excel(caminho_saida_excel, index=False)

#print("Tabela corrigida (Tratamento de Choque) e salva perfeitamente em formato Excel!")
# %%
df_conv1 = pd.read_excel('../new_data/SINAN_ATUALIZADA_PRE_CRUZAMENTO2.xlsx')
df_conv2 = pd.read_excel('../new_data/SDS_TRATADO2.xlsx')
df_conv3 = pd.read_excel('../new_data/tabela_final_sds_sinan.xlsx')

#%%
df_conv1['ESCOLARIDADE'] = df_conv1['ESCOLARIDADE'].astype(str)

#%%
df_conv1.to_parquet('../new_data/SINAN_FINAL.parquet', index=False)
df_conv2.to_parquet('../new_data/SDS_FINAL.parquet', index=False)
df_conv3.to_parquet('../new_data/SDS_SINAN_FINAL.parquet', index=False)
# %%
