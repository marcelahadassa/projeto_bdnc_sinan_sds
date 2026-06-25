# %%
import pandas as pd
import numpy as np
import unicodedata

#%%
# leitura da base do SINAN
df_sinan = pd.read_parquet('../new_data/BASE_COMPLETA_SINAN_UNIDADES.parquet')

# criação da faixa etária se baseando na base do SDS (para padronização de cruzamento)
#%%
# extração da parte numérica da coluna IDADE_REAL e conversão para float
df_sinan['IDADE_NUMERICA'] = df_sinan['IDADE_REAL'].str.extract(r'(\d+)').astype(float)

# limites e nomes das faixas etárias do SDS
limites = [-1, 11, 17, 24, 29, 34, 64, 130] 
nomes_faixas = ['00-11', '12-17', '18-24', '25-29', '30-34', '35-64', '65 OU MAIS']

# corte das idades em faixas etárias usando pd.cut
df_sinan['FAIXA_ETARIA_SDS'] = pd.cut(df_sinan['IDADE_NUMERICA'], bins=limites, labels=nomes_faixas)

# dados nulos ou que não se encaixam em nenhuma faixa recebem o rótulo (vazio)
df_sinan['FAIXA_ETARIA_SDS'] = df_sinan['FAIXA_ETARIA_SDS'].astype(str).replace('nan', '(vazio)')

# encontra a posição da coluna IDADE_REAL para inserir a nova coluna logo após ela
posicao_idade_real = df_sinan.columns.get_loc('IDADE_REAL')

# a coluna nova é extraída para ser inserida na posição correta posteriormente
coluna_faixa_etaria = df_sinan.pop('FAIXA_ETARIA_SDS')

# inserção da coluna FAIXA_ETARIA_SDS na posição correta (logo após IDADE_REAL)
df_sinan.insert(posicao_idade_real + 1, 'FAIXA_ETARIA_SDS', coluna_faixa_etaria)

# padronização de nomes de municípios (remoção de acentos, conversão para maiúsculas e remoção de espaços extras)
#%%
# função para remover acentos e caracteres especiais
def remover_acentos(texto):
    if texto is None or not isinstance(texto, str):
        return texto
    # normaliza o texto para decompor os caracteres acentuados em seus componentes básicos
    nfkd_form = unicodedata.normalize('NFKD', texto)
    # filtra apenas os caracteres que não são marcas de acentuação
    return "".join([char for char in nfkd_form if not unicodedata.combining(char)])

# colunas que precisam de padronização de municípios
colunas_municipios = ['ID_MUNICIP', 'ID_MUNIC_RESI', 'ID_MN_OCOR']

for col in colunas_municipios:
    if col in df_sinan.columns:
        # aplicação da função de remoção de acentos, conversão para maiúsculas e remoção de espaços extras
        df_sinan[col] = df_sinan[col].apply(remover_acentos).str.upper().str.strip()

# type casting para garantir consistência de tipos de dados
#%%
# conversão de data para datetime
colunas_de_data = ['DT_NOTIFIC', 'DT_OCOR']
for col in colunas_de_data:
    if col in df_sinan.columns:
        df_sinan[col] = pd.to_datetime(df_sinan[col], errors='coerce')

# conversão para int 
colunas_inteiras = ['NU_ANO', 'ANO_NASC', 'CODIGO_IDADE']
for col in colunas_inteiras:
    if col in df_sinan.columns:
        df_sinan[col] = pd.to_numeric(df_sinan[col], errors='coerce').astype('Int64')

# garante que o codigo do ibge seja tratado como string, preservando zeros à esquerda
colunas_texto = ['ID_MUNICIP', 'ID_UNIDADE', 'SEXO', 'CS_RACA', 'ESTADO_NOTIFICACAO']
for col in colunas_texto:
    if col in df_sinan.columns:
        df_sinan[col] = df_sinan[col].astype(str).replace('nan', None)

#%%
df_sinan.head(10)

#%%
# salvamento
caminho_final = '../new_data/BASE_SINAN_COMPLETA_PRE_CRUZAMENTO.parquet'

# salvamento do df_sinan em parquet
df_sinan.to_parquet(caminho_final, index=False)
# %%