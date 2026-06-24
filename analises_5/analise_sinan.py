#%%
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configuração de estilo para artigo acadêmico (fundo branco, sem grades pesadas)
sns.set_theme(style="white", rc={"axes.edgecolor": "black", "xtick.color": "black", "ytick.color": "black"})

#%%
# 1. Carregando a sua Tabela Ouro
df = pd.read_excel('../planilhas_parquet/tabela_cruzada_sds_sinan.xlsx')

#%%
# 2. Descobrindo o Total de Notificações do Estado inteiro
total_notificacoes = df['TOTAL_CASOS_SINAN'].sum()
print(f"TOTAL GERAL DE NOTIFICAÇÕES (SINAN): {total_notificacoes}")

#%%
# 3. Agrupando para ver quantos casos cada Município teve no total (somando todos os anos e idades)
ranking_municipios = df.groupby('ID_MUNICIP')['TOTAL_CASOS_SINAN'].sum().reset_index()

#%%
# 4. Calculando a Porcentagem (%) de cada município
ranking_municipios['PORCENTAGEM (%)'] = (ranking_municipios['TOTAL_CASOS_SINAN'] / total_notificacoes) * 100

#%%
# 5. Ordenando do maior para o menor (do município com mais casos para o com menos)
ranking_municipios = ranking_municipios.sort_values(by='TOTAL_CASOS_SINAN', ascending=False)

#%% 
# Arredondando a porcentagem para 2 casas decimais (para ficar com visual de painel)
ranking_municipios['PORCENTAGEM (%)'] = ranking_municipios['PORCENTAGEM (%)'].round(2)

print("\n--- TOP MUNICÍPIOS COM MAIS NOTIFICAÇÕES ---")
print(ranking_municipios.head(10).to_string(index=False))

#%%
# Carregando a tabela cruzada
df_cruzado = pd.read_excel('../planilhas_parquet/tabela_cruzada_sds_sinan.xlsx')

#%%
# 1. Totais Gerais do Estado
total_sds = df_cruzado['TOTAL_CASOS_SDS'].sum()
total_sinan = df_cruzado['TOTAL_CASOS_SINAN'].sum()

# A CONTA NOVA: Quantos BOs existem que não viraram ficha no hospital?
gap_saude = total_sds - total_sinan 

# Qual a taxa de sucesso do hospital?
taxa_notificacao_saude = (total_sinan / total_sds) * 100

print(f"\n--- PANORAMA DA SUBNOTIFICAÇÃO NA SAÚDE (PERNAMBUCO) ---")
print(f"Total de Registros na Polícia (SDS): {total_sds}")
print(f"Total de Notificações na Saúde (SINAN): {total_sinan}")
print(f"Diferença (Casos Invisíveis para a Saúde): {gap_saude} casos")
print(f"A Saúde preenche a notificação em apenas {taxa_notificacao_saude:.2f}% dos casos conhecidos pela polícia.")

#%%
# 2. Municípios com maior falha na Saúde
df_cruzado['GAP_SAUDE'] = df_cruzado['TOTAL_CASOS_SDS'] - df_cruzado['TOTAL_CASOS_SINAN']
ranking_gap = df_cruzado.groupby('ID_MUNICIP')['GAP_SAUDE'].sum().sort_values(ascending=False)

print("\n--- MUNICÍPIOS COM MAIOR SUBNOTIFICAÇÃO HOSPITALAR ---")
print(ranking_gap.head(5))

# =====================================================================
# SESSÃO DE GRÁFICOS (PRETO E BRANCO - PADRÃO ARTIGO)
# =====================================================================

#%% GRÁFICO 1: Comparação SDS x SINAN (O Abismo)
plt.figure(figsize=(8, 6))
cores_barras = ['#333333', '#999999'] # Cinza escuro e cinza claro
barras = plt.bar(['Polícia (SDS)', 'Saúde (SINAN)'], [total_sds, total_sinan], color=cores_barras, edgecolor='black', width=0.6)

plt.title('Comparação de Registros de Violência Doméstica (2014-2024)', fontsize=12, weight='bold', pad=15)
plt.ylabel('Número de Ocorrências', fontsize=11)

# Adicionando os rótulos numéricos em cima de cada barra
for barra in barras:
    yval = barra.get_height()
    plt.text(barra.get_x() + barra.get_width()/2, yval + 5000, f'{int(yval):,}'.replace(',', '.'), ha='center', va='bottom', fontsize=11)

plt.tight_layout()
# plt.savefig('grafico_1_abismo_sds_sinan.png', dpi=300) # dpi=300 é exigência de artigos
plt.show()

#%% GRÁFICO 2: Top 10 Municípios Notificadores na Saúde
top10_sinan = ranking_municipios.head(10)

plt.figure(figsize=(10, 6))
barras_h = sns.barplot(x='TOTAL_CASOS_SINAN', y='ID_MUNICIP', data=top10_sinan, color='#777777', edgecolor='black')

plt.title('Top 10 Municípios com Mais Notificações na Saúde (SINAN)', fontsize=12, weight='bold', pad=15)
plt.xlabel('Total de Casos Notificados', fontsize=11)
plt.ylabel('Município', fontsize=11)

# Adicionando os valores na ponta das barras
for index, value in enumerate(top10_sinan['TOTAL_CASOS_SINAN']):
    plt.text(value + 100, index, f'{int(value)}', va='center', fontsize=10, color='black')

plt.tight_layout()
# plt.savefig('grafico_2_top10_sinan.png', dpi=300)
plt.show()

#%% GRÁFICO 3: O "Ranking da Omissão" (Top 5 Municípios GAP_SAUDE)
top5_gap = ranking_gap.head(5).reset_index()

plt.figure(figsize=(10, 5))
# Usando um cinza bem escuro quase preto para dar sensação de gravidade
barras_gap = sns.barplot(x='GAP_SAUDE', y='ID_MUNICIP', data=top5_gap, color='#222222', edgecolor='black')

plt.title('Top 5 Municípios com Maior Déficit de Notificações na Saúde', fontsize=12, weight='bold', pad=15)
plt.xlabel('Déficit Absoluto (Casos Invisíveis)', fontsize=11)
plt.ylabel('Município', fontsize=11)

# Adicionando os valores na ponta das barras
for index, value in enumerate(top5_gap['GAP_SAUDE']):
    plt.text(value + 1000, index, f'{int(value)}', va='center', fontsize=10, color='black')

plt.tight_layout()
# plt.savefig('grafico_3_top5_gap.png', dpi=300)
plt.show()

#%%