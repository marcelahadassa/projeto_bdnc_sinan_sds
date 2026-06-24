#%%
# ==========================================
# 1. IMPORTAÇÕES E CARREGAMENTO
# ==========================================
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

print("Carregando base do SINAN...")
df_sinan = pd.read_parquet('../planilhas_parquet/sinan_final.parquet')

#%%
# ==========================================
# 2. PREPARAÇÃO DOS DADOS: GERAL
# ==========================================
# Lista exata das suas colunas de violência
colunas_violencia = [
    'VIOL_FISIC', 'VIOL_PSICO', 'VIOL_TORT', 'VIOL_SEXU', 
    'VIOL_TRAF', 'VIOL_FINAN', 'VIOL_NEGLI', 'VIOL_INFAN'
]

# Dicionário para deixar os nomes bonitos no relatório
nomes_violencia = {
    'VIOL_FISIC': 'Física', 'VIOL_PSICO': 'Psicológica', 'VIOL_TORT': 'Tortura', 
    'VIOL_SEXU': 'Sexual', 'VIOL_TRAF': 'Tráfico Humano', 'VIOL_FINAN': 'Financeira', 
    'VIOL_NEGLI': 'Negligência', 'VIOL_INFAN': 'Trabalho Infantil'
}

# Total geral de pacientes no SINAN
total_pacientes = len(df_sinan)
resultados_violencia = []

print("Analisando tipos de violência...")

# Loop Inteligente para o primeiro gráfico
for col in colunas_violencia:
    if col in df_sinan.columns:
        # Converte pra texto, joga pra maiúsculo, tira espaço e compara com 'SIM'
        qtd_sim = (df_sinan[col].astype(str).str.upper().str.strip() == 'SIM').sum()
        porcentagem = (qtd_sim / total_pacientes) * 100
        
        resultados_violencia.append({
            'Tipo de Violência': nomes_violencia[col],
            'Qtd Casos (Sim)': int(qtd_sim),
            'Porcentagem (%)': round(porcentagem, 2)
        })

# Transformando em uma tabela bonita e ordenando do maior pro menor
df_resumo_violencia = pd.DataFrame(resultados_violencia)
df_resumo_violencia = df_resumo_violencia.sort_values(by='Qtd Casos (Sim)', ascending=False)

print(f"\nTOTAL DE PACIENTES ANALISADOS: {total_pacientes}\n")
print("=== RANKING DOS TIPOS DE VIOLÊNCIA SOFRIDA ===")
print(df_resumo_violencia.to_string(index=False))

#%%
# ==========================================
# 3. GRÁFICO 1: BARRAS HORIZONTAIS (GERAL) - TONS DE CINZA
# ==========================================
sns.set_theme(style="whitegrid") # Fundo branco com linhas discretas
plt.figure(figsize=(10, 6))

# Criando as barras dinâmicas em tons de cinza
ax = sns.barplot(
    x='Porcentagem (%)', 
    y='Tipo de Violência', 
    data=df_resumo_violencia, 
    color="#444444", # Substituímos o palette="mako" por um cinza escuro sólido
    edgecolor="black" # Adiciona uma borda preta fina para dar mais contraste
)

# Colocando os números na frente das barras
for p in ax.patches:
    width = p.get_width()
    ax.annotate(f'{width:.2f}%',
                (width, p.get_y() + p.get_height() / 2.),
                ha='left', va='center',
                xytext=(5, 0),
                textcoords='offset points',
                fontsize=11, color='#333333', fontweight='bold')

# Formatando títulos e margens
plt.title('Proporção dos Tipos de Violência Notificados (SINAN)', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Frequência Relativa (%)', fontsize=12, labelpad=10)
plt.ylabel('') # Eixo Y vazio para deixar o gráfico mais limpo

# Limite dinâmico: acha a maior porcentagem e soma 10 para o texto caber
limite_maximo = df_resumo_violencia['Porcentagem (%)'].max() + 10
plt.xlim(0, limite_maximo) 

plt.tight_layout()
#plt.savefig('grafico_tipos_violencia_pb.png', dpi=300, bbox_inches='tight')
print("\nGráfico de barras P&B gerado com sucesso! ('grafico_tipos_violencia_pb.png')")

#%%
# ==========================================
# 4. PREPARAÇÃO E GRÁFICO (MAPA DE CALOR)
# ==========================================
print("\nIniciando cruzamento por Faixa Etária...")

coluna_idade = 'FAIXA_ETARIA_SDS' 
ordem_idades = [
    '0-11 anos', '12-17 anos', '18-24 anos', 
    '25-29 anos', '30-34 anos', '35-64 anos', '65 OU MAIS'
]

dados_cruzados = []

# Loop de cruzamento
for col in colunas_violencia:
    if col in df_sinan.columns and coluna_idade in df_sinan.columns:
        df_sim = df_sinan[df_sinan[col].astype(str).str.upper().str.strip() == 'SIM']
        contagem = df_sim[coluna_idade].value_counts().to_dict()
        
        for idade, qtd in contagem.items():
            dados_cruzados.append({
                'Tipo de Violência': nomes_violencia[col],
                'Faixa Etária': idade,
                'Qtd Casos': qtd
            })

# Cria a Matriz
# ==========================================
df_cruzado = pd.DataFrame(dados_cruzados)
df_matriz = df_cruzado.pivot(index='Tipo de Violência', columns='Faixa Etária', values='Qtd Casos').fillna(0)

# 1. Pegamos todas as faixas etárias que REALMENTE vieram do banco de dados
colunas_reais = list(df_matriz.columns)

# 2. Imprimimos no terminal para você ver como elas estão escritas de verdade lá no Parquet
print("\n⚠️ NOMES REAIS DAS FAIXAS ETÁRIAS NA BASE:", colunas_reais)

# 3. Organizamos a ordem: o que bater com a sua lista fica no começo, o que for diferente vai pro final (mas NÃO some!)
colunas_ordenadas = [idade for idade in ordem_idades if idade in colunas_reais]
colunas_restantes = [idade for idade in colunas_reais if idade not in colunas_ordenadas]

# Atualiza a matriz sem perder ninguém
df_matriz = df_matriz[colunas_ordenadas + colunas_restantes]

# Desenha o Gráfico
plt.figure(figsize=(12, 8))
ax_heat = sns.heatmap(
    df_matriz, 
    annot=True,        
    fmt=".0f",         
    cmap="YlOrRd",     
    linewidths=.5,     
    cbar_kws={'label': 'Número de Casos'} 
)

plt.title('Concentração de Tipos de Violência por Faixa Etária (SINAN)', fontsize=15, fontweight='bold', pad=20)
plt.xlabel('Faixa Etária', fontsize=12, fontweight='bold', labelpad=10)
plt.ylabel('Tipo de Violência', fontsize=12, fontweight='bold', labelpad=10)
plt.xticks(rotation=45, ha='right')

plt.tight_layout()
#plt.savefig('heatmap_violencia_idade.png', dpi=300, bbox_inches='tight')
print("\n✅ Mapa de Calor gerado com sucesso! ('heatmap_violencia_idade.png')")
#%%