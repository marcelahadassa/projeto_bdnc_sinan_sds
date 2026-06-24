# %%
import pandas as pd
import numpy as np

# leitura da base do SDS
print("Carregando base bruta da SDS...")
df_sds = pd.read_excel('../data/raw/MICRO_DADOS_VIOL_DOM.xlsx')

# mapeando as colunas de interesse para o padrão do SINAN
print("Mapeando naturezas da ocorrência para os padrões do SINAN...")

colunas_violencia = ['VIOL_FISIC', 'VIOL_PSICO', 'VIOL_TORT', 'VIOL_SEXU', 
                     'VIOL_TRAF', 'VIOL_FINAN', 'VIOL_NEGLI', 'VIOL_INFAN']
colunas_agressao = ['AG_FORCA', 'AG_ENFOR', 'AG_OBJETO', 'AG_CORTE', 
                    'AG_QUENTE', 'AG_ENVEN', 'AG_FOGO', 'AG_AMEACA']
colunas_sexual = ['SEX_ASSEDI', 'SEX_ESTUPR', 'SEX_PORNO', 'SEX_EXPLO']

todas_colunas_sinan = colunas_violencia + colunas_agressao + colunas_sexual

crimes_fisicos = [
    'LESÃO CORPORAL POR VIOLÊNCIA DOMÉSTICA/FAMILIAR', 
    'VIAS DE FATOS POR VIOLÊNCIA DOMÉSTICA/FAMILIAR', 
    'MAUS TRATOS POR VIOLÊNCIA DOMÉSTICA/FAMILIAR'
]

crimes_psicologicos = [
    'AMEAÇA POR VIOLÊNCIA DOMÉSTICA/FAMILIAR', 'CALÚNIA POR VIOLÊNCIA DOMÉSTICA/FAMILIAR', 
    'DIFAMAÇÃO POR VIOLÊNCIA DOMÉSTICA/FAMILIAR', 'INJÚRIA POR VIOLÊNCIA DOMÉSTICA/FAMILIAR',
    'PERSEGUIÇÃO POR VIOLÊNCIA DOMÉSTICA/FAMILIAR', 'CONSTRANGIMENTO ILEGAL POR VIOLÊNCIA DOMÉSTICA/FAMILIAR',
    'PERTURBAÇÃO DO SOSSEGO POR VIOLÊNCIA DOMÉSTICA/FAMILIAR', 'CÁRCERE PRIVADO POR VIOLÊNCIA DOMÉSTICA/FAMILIAR'
]

crimes_sexuais = [
    'ESTUPRO POR VIOLÊNCIA DOMÉSTICA/FAMILIAR', 
    'ESTUPRO DE VULNERÁVEL POR VIOLÊNCIA DOMÉSTICA/FAMILIAR'
]

# inicialização com NAO
for coluna in todas_colunas_sinan:
    df_sds[coluna] = 'NAO'

# aplicação do mapeamento usando np.where
df_sds['VIOL_FISIC'] = np.where(df_sds['NATUREZA'].isin(crimes_fisicos), 'SIM', df_sds['VIOL_FISIC'])
df_sds['VIOL_PSICO'] = np.where(df_sds['NATUREZA'].isin(crimes_psicologicos), 'SIM', df_sds['VIOL_PSICO'])
df_sds['VIOL_SEXU']  = np.where(df_sds['NATUREZA'].isin(crimes_sexuais), 'SIM', df_sds['VIOL_SEXU'])
df_sds['VIOL_FINAN'] = np.where(df_sds['NATUREZA'] == 'DANO POR VIOLÊNCIA DOMÉSTICA/FAMILIAR', 'SIM', df_sds['VIOL_FINAN'])

df_sds['AG_AMEACA']  = np.where(df_sds['NATUREZA'] == 'AMEAÇA POR VIOLÊNCIA DOMÉSTICA/FAMILIAR', 'SIM', df_sds['AG_AMEACA'])
df_sds['SEX_ESTUPR'] = np.where(df_sds['NATUREZA'].isin(crimes_sexuais), 'SIM', df_sds['SEX_ESTUPR'])

# padronizando faixa etária e sexo

# remoção de prefixos numéricos como "1) ", "2) "
df_sds['FAIXA_ETARIA_SDS'] = df_sds['FAIXA_ETARIA_SDS'].str.replace(r'^\d+\)\s*', '', regex=True)

# primeira letra do sexo e converte para maiúscula (F)
df_sds['SEXO'] = df_sds['SEXO'].str[0].str.upper()

# deduplicação de registros exatos
linhas_iniciais = df_sds.shape[0]
quantidade_duplicatas = df_sds.duplicated().sum()

print(f"Registros antes da deduplicação: {linhas_iniciais}")
print(f"Linhas duplicadas encontradas: {quantidade_duplicatas}")

if quantidade_duplicatas > 0:
    df_sds = df_sds.drop_duplicates(ignore_index=True)
    linhas_removidas = linhas_iniciais - df_sds.shape[0]
    print(f"{linhas_removidas} registros duplicados foram removidos.")
else:
    print("Nenhuma duplicata encontrada.")

# verificação
print("\nAmostra dos dados finais:")
print(df_sds[['FAIXA_ETARIA_SDS', 'SEXO']].head())
print("\nValores únicos de Sexo:", df_sds['SEXO'].unique())
print("Valores únicos de Idade:", df_sds['FAIXA_ETARIA_SDS'].unique())
print(f"Total de registros finais: {df_sds.shape[0]}")

# criação do ID do SDS
print("\nGerando IDs numéricos únicos para a base limpa da SDS...")

# Insere a coluna ID_SDS na primeira posição
df_sds.insert(0, "ID_SDS", range(1, len(df_sds) + 1))

print(f"Primeiro ID gerado: {df_sds['ID_SDS'].iloc[0]}")
print(f"Último ID gerado: {df_sds['ID_SDS'].iloc[-1]}")

# type casting para garantir consistência de tipos de dados
print("\nAplicando tipagem estrita nas colunas antes de salvar...")

# tratamento de colunas de texto: converte para string e substitui 'nan' por None
colunas_texto = ['SEXO', 'FAIXA_ETARIA_SDS', 'NATUREZA', 'MUNICIPIO'] + todas_colunas_sinan
for col in colunas_texto:
    if col in df_sds.columns:
        df_sds[col] = df_sds[col].astype(str).replace('nan', None)

# para qualquer coluna de data existente na base, já formata para DATETIME
colunas_data_possiveis = ['DATA_FATO', 'DATA_BO', 'DATA_OCORRENCIA']
for col in colunas_data_possiveis:
    if col in df_sds.columns:
        df_sds[col] = pd.to_datetime(df_sds[col], errors='coerce')

# salvamento 
caminho_final = '../new_data/SDS_PRE_CRUZAMENTO.parquet'
print(f"\nSalvando base SDS preparada e tipada em: {caminho_final}...")

# salvamento do df_sds para parquet
df_sds.to_parquet(caminho_final, index=False)
# %%
