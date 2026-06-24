#%%
import pandas as pd
import matplotlib.pyplot as plt

print("Buscando dados no BigQuery e preparando painel (Incluindo Ignorados)...")

# ==========================================
# 1. EXTRAÇÃO
# ==========================================
query = """
SELECT 
    TRIM(UPPER(CAST(ID_MUNICIP AS STRING))) AS ID_MUNICIP,
    TRIM(UPPER(CAST(CS_RACA AS STRING))) AS CS_RACA,
    COUNT(*) AS Total_Casos
FROM `sinan-sds-ic.dados_sinan_sds_pe.sinan_tratado`
WHERE CS_RACA IS NOT NULL 
GROUP BY 1, 2
"""
df_raw = pd.read_gbq(query, project_id='sinan-sds-ic', location='southamerica-east1')

# ==========================================
# 2. PADRONIZAÇÃO (O SEGREDO ESTÁ AQUI)
# ==========================================
# Em vez de excluir, nós transformamos tudo que é "sujeira" em "IGNORADA"
termos_vazios = ['IGNORADO', 'NAN', 'NÃO INFORMADO', 'NAO INFORMADO']
df_raw['CS_RACA'] = df_raw['CS_RACA'].replace(termos_vazios, 'IGNORADA')

if len(df_raw) > 0:
    # Seleciona os Top 15 Municípios pelo volume TOTAL (agora contando com os ignorados)
    top_15 = df_raw.groupby('ID_MUNICIP')['Total_Casos'].sum().nlargest(15).index
    df_final = df_raw[df_raw['ID_MUNICIP'].isin(top_15)]

    # ==========================================
    # 3. PREPARAÇÃO DAS MATRIZES
    # ==========================================
    matriz_absoluta = df_final.pivot_table(
        index='ID_MUNICIP', columns='CS_RACA', values='Total_Casos', aggfunc='sum', fill_value=0
    )
    
    # Ordenar os municípios pelo volume total
    matriz_absoluta['Total_Geral'] = matriz_absoluta.sum(axis=1)
    matriz_absoluta = matriz_absoluta.sort_values(by='Total_Geral', ascending=True)
    matriz_absoluta = matriz_absoluta.drop(columns='Total_Geral')

    # Transforma em Porcentagem
    matriz_pct = matriz_absoluta.div(matriz_absoluta.sum(axis=1), axis=0) * 100
    matriz_pct = matriz_pct.astype(float)

    # ==========================================
    # 4. DEFINIÇÃO DE CORES
    # ==========================================
    mapa_cores = {
        'AMARELA': '#F4D03F',   
        'BRANCA': '#5DADE2',    
        'INDIGENA': '#58D68D',  
        'PARDA': '#E67E22',     
        'PRETA': '#8E44AD',     
        'IGNORADA': '#BDC3C7'  # Adicionamos o Cinza para os dados faltantes
    }
    
    cores_lista = [mapa_cores.get(raca, '#95A5A6') for raca in matriz_absoluta.columns]

    # ==========================================
    # 5. DESENHANDO O PAINEL
    # ==========================================
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8), sharey=True)

    # GRÁFICO ESQUERDO
    matriz_absoluta.plot(
        kind='barh', stacked=True, ax=ax1, color=cores_lista, edgecolor='white', width=0.8
    )
    ax1.set_title('Volume Absoluto (Total de Vítimas)', fontsize=14, pad=15)
    ax1.set_xlabel('Número de Notificações', fontsize=12)
    ax1.set_ylabel('Município', fontsize=12)
    ax1.legend().remove()
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)

    # GRÁFICO DIREITO
    matriz_pct.plot(
        kind='barh', stacked=True, ax=ax2, color=cores_lista, edgecolor='white', width=0.8
    )
    ax2.set_title('Composição Racial e Dados Faltantes (Proporção 100%)', fontsize=14, pad=15)
    ax2.set_xlabel('Proporção dentro do Município (%)', fontsize=12)
    ax2.set_ylabel('')
    
    # Legenda fora do gráfico
    ax2.legend(title='Raça/Cor Autodeclarada', bbox_to_anchor=(1.05, 1), loc='upper left')
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)

    plt.suptitle('Qualidade do Preenchimento Racial no SINAN por Município (Top 15 PE)', fontsize=18, y=1.02)
    plt.tight_layout()
    plt.savefig('painel_duplo_com_ignorados.png', dpi=300, bbox_inches='tight')
    print("\n✅ Painel duplo gerado com sucesso!")
    
    plt.show()
else:
    print("\n🚨 ALERTA: O DataFrame ficou vazio.")
# %%