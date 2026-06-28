# %%
"""
Análise descritiva da base Silver SINAN considerando o recorte doméstico/familiar.

Este script utiliza a tabela silver.sinan no DuckDB para analisar os registros do
SINAN por ano e município, considerando a coluna RECORTE_DOMESTICO_FAMILIAR.

A coluna RECORTE_DOMESTICO_FAMILIAR foi criada como um recorte operacional para
aproximar casos de violência doméstica/familiar, considerando local residencial
e/ou vínculo familiar, afetivo ou de cuidado com o provável autor.

Saídas geradas em:
analysis/sinan_recorte_domestico/
"""

# %%
import sys
from pathlib import Path

import duckdb
import pandas as pd
import matplotlib.pyplot as plt


# %%
def encontrar_raiz_projeto():
    """
    Localiza a raiz do projeto procurando pela pasta src/config.py.
    """

    caminho_atual = Path.cwd().resolve()

    for pasta in [caminho_atual, *caminho_atual.parents]:
        if (pasta / "src" / "config.py").exists():
            return pasta

    raise FileNotFoundError("Não foi possível encontrar a raiz do projeto com src/config.py")


ROOT_DIR = encontrar_raiz_projeto()

if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))


# %%
from src.config import DUCKDB_PATH


# %%
PASTA_RESULTADOS = ROOT_DIR / "analysis" / "sinan_recorte_domestico"
PASTA_RESULTADOS.mkdir(parents=True, exist_ok=True)


# %%
def executar_consulta(sql):
    """
    Executa uma consulta SQL no DuckDB do projeto e retorna um DataFrame.
    """

    con = duckdb.connect(str(DUCKDB_PATH), read_only=True)

    df = con.execute(sql).fetchdf()

    con.close()

    return df


# %%
def salvar_csv(df, nome_arquivo):
    """
    Salva um DataFrame em CSV dentro da pasta de resultados.
    """

    caminho = PASTA_RESULTADOS / nome_arquivo

    df.to_csv(
        caminho,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"Arquivo salvo: {caminho}")

    return caminho


# %%
def salvar_grafico(nome_arquivo):
    """
    Salva o gráfico atual em PNG.
    """

    caminho = PASTA_RESULTADOS / nome_arquivo

    plt.tight_layout()
    plt.savefig(caminho, dpi=300)
    plt.show()

    print(f"Gráfico salvo: {caminho}")

    return caminho


# ============================================================
# 1. RESUMO GERAL DO RECORTE DOMÉSTICO/FAMILIAR
# ============================================================

# %%
sql_resumo_geral = """
SELECT
    COUNT(*) AS total_notificacoes_sinan,

    SUM(
        CASE
            WHEN RECORTE_DOMESTICO_FAMILIAR = 'SIM' THEN 1
            ELSE 0
        END
    ) AS total_recorte_domestico_familiar,

    SUM(
        CASE
            WHEN RECORTE_DOMESTICO_FAMILIAR = 'NAO' THEN 1
            ELSE 0
        END
    ) AS total_fora_recorte,

    ROUND(
        100.0 * SUM(
            CASE
                WHEN RECORTE_DOMESTICO_FAMILIAR = 'SIM' THEN 1
                ELSE 0
            END
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS percentual_recorte_domestico_familiar

FROM silver.sinan;
"""

df_resumo_geral = executar_consulta(sql_resumo_geral)

print("\nResumo geral do recorte doméstico/familiar no SINAN:")
print(df_resumo_geral)

salvar_csv(df_resumo_geral, "01_resumo_geral_recorte_domestico.csv")


# ============================================================
# 2. ANÁLISE DESCRITIVA POR ANO
# ============================================================

# %%
sql_por_ano = """
SELECT
    NU_ANO AS ano,

    COUNT(*) AS total_notificacoes_sinan,

    SUM(
        CASE
            WHEN RECORTE_DOMESTICO_FAMILIAR = 'SIM' THEN 1
            ELSE 0
        END
    ) AS total_recorte_domestico_familiar,

    SUM(
        CASE
            WHEN RECORTE_DOMESTICO_FAMILIAR = 'NAO' THEN 1
            ELSE 0
        END
    ) AS total_fora_recorte,

    ROUND(
        100.0 * SUM(
            CASE
                WHEN RECORTE_DOMESTICO_FAMILIAR = 'SIM' THEN 1
                ELSE 0
            END
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS percentual_recorte_domestico_familiar,

    SUM(
        CASE
            WHEN RECORTE_DOMESTICO_FAMILIAR = 'SIM'
             AND VIOL_FISIC = 'SIM'
            THEN 1
            ELSE 0
        END
    ) AS total_violencia_fisica_recorte,

    SUM(
        CASE
            WHEN RECORTE_DOMESTICO_FAMILIAR = 'SIM'
             AND VIOL_PSICO = 'SIM'
            THEN 1
            ELSE 0
        END
    ) AS total_violencia_psicologica_recorte,

    SUM(
        CASE
            WHEN RECORTE_DOMESTICO_FAMILIAR = 'SIM'
             AND VIOL_SEXU = 'SIM'
            THEN 1
            ELSE 0
        END
    ) AS total_violencia_sexual_recorte,

    SUM(
        CASE
            WHEN RECORTE_DOMESTICO_FAMILIAR = 'SIM'
             AND VIOL_FINAN = 'SIM'
            THEN 1
            ELSE 0
        END
    ) AS total_violencia_financeira_recorte

FROM silver.sinan
GROUP BY NU_ANO
ORDER BY NU_ANO;
"""

df_por_ano = executar_consulta(sql_por_ano)

print("\nAnálise do recorte doméstico/familiar por ano:")
print(df_por_ano)

salvar_csv(df_por_ano, "02_recorte_domestico_por_ano.csv")


# %%
plt.figure(figsize=(9, 5))
plt.plot(
    df_por_ano["ano"],
    df_por_ano["total_notificacoes_sinan"],
    marker="o",
    label="Total SINAN"
)
plt.plot(
    df_por_ano["ano"],
    df_por_ano["total_recorte_domestico_familiar"],
    marker="o",
    label="Recorte doméstico/familiar"
)
plt.title("Notificações do SINAN e recorte doméstico/familiar por ano")
plt.xlabel("Ano")
plt.ylabel("Total de notificações")
plt.legend()
plt.grid(True)
salvar_grafico("grafico_01_total_e_recorte_por_ano.png")


# %%
plt.figure(figsize=(9, 5))
plt.bar(
    df_por_ano["ano"],
    df_por_ano["percentual_recorte_domestico_familiar"]
)
plt.title("Percentual do recorte doméstico/familiar por ano")
plt.xlabel("Ano")
plt.ylabel("% do total de notificações do SINAN")
plt.grid(axis="y")
salvar_grafico("grafico_02_percentual_recorte_por_ano.png")


# ============================================================
# 3. ESTATÍSTICAS DESCRITIVAS DO RECORTE POR ANO
# ============================================================

# %%
df_descritivas_ano = df_por_ano[
    [
        "total_notificacoes_sinan",
        "total_recorte_domestico_familiar",
        "percentual_recorte_domestico_familiar",
        "total_violencia_fisica_recorte",
        "total_violencia_psicologica_recorte",
        "total_violencia_sexual_recorte",
        "total_violencia_financeira_recorte",
    ]
].describe(percentiles=[0.25, 0.5, 0.75]).reset_index()

print("\nEstatísticas descritivas por ano:")
print(df_descritivas_ano)

salvar_csv(df_descritivas_ano, "03_estatisticas_descritivas_por_ano.csv")


# ============================================================
# 4. ANÁLISE DESCRITIVA POR MUNICÍPIO
# ============================================================

# %%
sql_por_municipio = """
SELECT
    MUNICIPIO_OCORRENCIA AS municipio,

    COUNT(*) AS total_notificacoes_sinan,

    SUM(
        CASE
            WHEN RECORTE_DOMESTICO_FAMILIAR = 'SIM' THEN 1
            ELSE 0
        END
    ) AS total_recorte_domestico_familiar,

    SUM(
        CASE
            WHEN RECORTE_DOMESTICO_FAMILIAR = 'NAO' THEN 1
            ELSE 0
        END
    ) AS total_fora_recorte,

    ROUND(
        100.0 * SUM(
            CASE
                WHEN RECORTE_DOMESTICO_FAMILIAR = 'SIM' THEN 1
                ELSE 0
            END
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS percentual_recorte_domestico_familiar,

    SUM(
        CASE
            WHEN RECORTE_DOMESTICO_FAMILIAR = 'SIM'
             AND VIOL_FISIC = 'SIM'
            THEN 1
            ELSE 0
        END
    ) AS total_violencia_fisica_recorte,

    SUM(
        CASE
            WHEN RECORTE_DOMESTICO_FAMILIAR = 'SIM'
             AND VIOL_PSICO = 'SIM'
            THEN 1
            ELSE 0
        END
    ) AS total_violencia_psicologica_recorte,

    SUM(
        CASE
            WHEN RECORTE_DOMESTICO_FAMILIAR = 'SIM'
             AND VIOL_SEXU = 'SIM'
            THEN 1
            ELSE 0
        END
    ) AS total_violencia_sexual_recorte,

    SUM(
        CASE
            WHEN RECORTE_DOMESTICO_FAMILIAR = 'SIM'
             AND VIOL_FINAN = 'SIM'
            THEN 1
            ELSE 0
        END
    ) AS total_violencia_financeira_recorte

FROM silver.sinan
GROUP BY MUNICIPIO_OCORRENCIA
ORDER BY total_recorte_domestico_familiar DESC;
"""

df_por_municipio = executar_consulta(sql_por_municipio)

print("\nAnálise do recorte doméstico/familiar por município:")
print(df_por_municipio)

salvar_csv(df_por_municipio, "04_recorte_domestico_por_municipio.csv")


# %%
df_descritivas_municipio = df_por_municipio[
    [
        "total_notificacoes_sinan",
        "total_recorte_domestico_familiar",
        "percentual_recorte_domestico_familiar",
        "total_violencia_fisica_recorte",
        "total_violencia_psicologica_recorte",
        "total_violencia_sexual_recorte",
        "total_violencia_financeira_recorte",
    ]
].describe(percentiles=[0.25, 0.5, 0.75]).reset_index()

print("\nEstatísticas descritivas por município:")
print(df_descritivas_municipio)

salvar_csv(df_descritivas_municipio, "05_estatisticas_descritivas_por_municipio.csv")


# ============================================================
# 5. TOP MUNICÍPIOS COM MAIOR VOLUME DO RECORTE
# ============================================================

# %%
df_top_municipios_volume = df_por_municipio.head(20).copy()

print("\nTop 20 municípios com maior volume do recorte doméstico/familiar:")
print(df_top_municipios_volume)

salvar_csv(df_top_municipios_volume, "06_top_20_municipios_maior_volume_recorte.csv")


# %%
plt.figure(figsize=(10, 6))
plt.barh(
    df_top_municipios_volume["municipio"],
    df_top_municipios_volume["total_recorte_domestico_familiar"]
)
plt.title("Top 20 municípios com maior volume do recorte doméstico/familiar")
plt.xlabel("Total de notificações no recorte")
plt.ylabel("Município")
plt.gca().invert_yaxis()
plt.grid(axis="x")
salvar_grafico("grafico_03_top_20_municipios_volume_recorte.png")


# ============================================================
# 6. MUNICÍPIOS COM MAIOR PERCENTUAL DO RECORTE
# ============================================================

# %%
# Filtro mínimo para evitar destacar municípios com poucos registros totais.
# Ajuste este valor, se necessário.
MINIMO_NOTIFICACOES_MUNICIPIO = 100

df_top_municipios_percentual = (
    df_por_municipio[
        df_por_municipio["total_notificacoes_sinan"] >= MINIMO_NOTIFICACOES_MUNICIPIO
    ]
    .sort_values(
        by="percentual_recorte_domestico_familiar",
        ascending=False
    )
    .head(20)
    .copy()
)

print("\nTop 20 municípios com maior percentual do recorte doméstico/familiar:")
print(df_top_municipios_percentual)

salvar_csv(df_top_municipios_percentual, "07_top_20_municipios_maior_percentual_recorte.csv")


# %%
plt.figure(figsize=(10, 6))
plt.barh(
    df_top_municipios_percentual["municipio"],
    df_top_municipios_percentual["percentual_recorte_domestico_familiar"]
)
plt.title("Top 20 municípios com maior percentual do recorte doméstico/familiar")
plt.xlabel("% do total de notificações do município")
plt.ylabel("Município")
plt.gca().invert_yaxis()
plt.grid(axis="x")
salvar_grafico("grafico_04_top_20_municipios_percentual_recorte.png")


# ============================================================
# 7. ANÁLISE MUNICÍPIO x ANO
# ============================================================

# %%
sql_municipio_ano = """
SELECT
    MUNICIPIO_OCORRENCIA AS municipio,
    NU_ANO AS ano,

    COUNT(*) AS total_notificacoes_sinan,

    SUM(
        CASE
            WHEN RECORTE_DOMESTICO_FAMILIAR = 'SIM' THEN 1
            ELSE 0
        END
    ) AS total_recorte_domestico_familiar,

    ROUND(
        100.0 * SUM(
            CASE
                WHEN RECORTE_DOMESTICO_FAMILIAR = 'SIM' THEN 1
                ELSE 0
            END
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS percentual_recorte_domestico_familiar

FROM silver.sinan
GROUP BY
    MUNICIPIO_OCORRENCIA,
    NU_ANO
ORDER BY
    MUNICIPIO_OCORRENCIA,
    NU_ANO;
"""

df_municipio_ano = executar_consulta(sql_municipio_ano)

print("\nAnálise município x ano:")
print(df_municipio_ano)

salvar_csv(df_municipio_ano, "08_recorte_domestico_municipio_ano.csv")


# %%
municipios_top_5 = (
    df_por_municipio
    .head(5)["municipio"]
    .tolist()
)

df_top_5_serie = df_municipio_ano[
    df_municipio_ano["municipio"].isin(municipios_top_5)
].copy()

plt.figure(figsize=(10, 6))

for municipio in municipios_top_5:
    df_temp = df_top_5_serie[
        df_top_5_serie["municipio"] == municipio
    ].sort_values("ano")

    plt.plot(
        df_temp["ano"],
        df_temp["total_recorte_domestico_familiar"],
        marker="o",
        label=municipio
    )

plt.title("Evolução anual do recorte nos 5 municípios com maior volume")
plt.xlabel("Ano")
plt.ylabel("Total de notificações no recorte")
plt.legend()
plt.grid(True)
salvar_grafico("grafico_05_evolucao_top_5_municipios.png")


# ============================================================
# 8. RECIFE COMO RECORTE ILUSTRATIVO
# ============================================================

# %%
sql_recife = """
SELECT
    NU_ANO AS ano,

    COUNT(*) AS total_notificacoes_sinan,

    SUM(
        CASE
            WHEN RECORTE_DOMESTICO_FAMILIAR = 'SIM' THEN 1
            ELSE 0
        END
    ) AS total_recorte_domestico_familiar,

    ROUND(
        100.0 * SUM(
            CASE
                WHEN RECORTE_DOMESTICO_FAMILIAR = 'SIM' THEN 1
                ELSE 0
            END
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS percentual_recorte_domestico_familiar,

    SUM(
        CASE
            WHEN RECORTE_DOMESTICO_FAMILIAR = 'SIM'
             AND VIOL_FISIC = 'SIM'
            THEN 1
            ELSE 0
        END
    ) AS total_violencia_fisica_recorte,

    SUM(
        CASE
            WHEN RECORTE_DOMESTICO_FAMILIAR = 'SIM'
             AND VIOL_PSICO = 'SIM'
            THEN 1
            ELSE 0
        END
    ) AS total_violencia_psicologica_recorte,

    SUM(
        CASE
            WHEN RECORTE_DOMESTICO_FAMILIAR = 'SIM'
             AND VIOL_SEXU = 'SIM'
            THEN 1
            ELSE 0
        END
    ) AS total_violencia_sexual_recorte,

    SUM(
        CASE
            WHEN RECORTE_DOMESTICO_FAMILIAR = 'SIM'
             AND VIOL_FINAN = 'SIM'
            THEN 1
            ELSE 0
        END
    ) AS total_violencia_financeira_recorte

FROM silver.sinan
WHERE MUNICIPIO_OCORRENCIA = 'RECIFE'
GROUP BY NU_ANO
ORDER BY NU_ANO;
"""

df_recife = executar_consulta(sql_recife)

print("\nRecorte doméstico/familiar em Recife por ano:")
print(df_recife)

salvar_csv(df_recife, "09_recife_recorte_domestico_por_ano.csv")


# %%
plt.figure(figsize=(9, 5))
plt.plot(
    df_recife["ano"],
    df_recife["total_notificacoes_sinan"],
    marker="o",
    label="Total SINAN"
)
plt.plot(
    df_recife["ano"],
    df_recife["total_recorte_domestico_familiar"],
    marker="o",
    label="Recorte doméstico/familiar"
)
plt.title("Recife: notificações do SINAN e recorte doméstico/familiar por ano")
plt.xlabel("Ano")
plt.ylabel("Total de notificações")
plt.legend()
plt.grid(True)
salvar_grafico("grafico_06_recife_total_e_recorte_por_ano.png")


# ============================================================
# 9. TEXTO-BASE PARA INTERPRETAÇÃO NO ARTIGO
# ============================================================

# %%
total_notificacoes = int(df_resumo_geral.loc[0, "total_notificacoes_sinan"])
total_recorte = int(df_resumo_geral.loc[0, "total_recorte_domestico_familiar"])
total_fora_recorte = int(df_resumo_geral.loc[0, "total_fora_recorte"])
percentual_recorte = float(df_resumo_geral.loc[0, "percentual_recorte_domestico_familiar"])

ano_maior_volume = df_por_ano.sort_values(
    by="total_recorte_domestico_familiar",
    ascending=False
).iloc[0]

municipio_maior_volume = df_por_municipio.sort_values(
    by="total_recorte_domestico_familiar",
    ascending=False
).iloc[0]

texto_interpretacao = f"""
# Análise descritiva do recorte doméstico/familiar no SINAN

A análise da tabela `silver.sinan` permitiu observar a distribuição das
notificações do SINAN considerando a coluna `RECORTE_DOMESTICO_FAMILIAR`,
criada como um recorte operacional para aproximar casos de violência
doméstica/familiar contra mulheres.

No conjunto analisado, foram identificadas {total_notificacoes:,} notificações
do SINAN. Desse total, {total_recorte:,} notificações foram classificadas dentro
do recorte doméstico/familiar, enquanto {total_fora_recorte:,} ficaram fora do
recorte. Assim, o recorte doméstico/familiar correspondeu a {percentual_recorte:.2f}%
das notificações analisadas.

Na análise temporal, o ano com maior volume de notificações dentro do recorte foi
{int(ano_maior_volume["ano"])}, com {int(ano_maior_volume["total_recorte_domestico_familiar"]):,}
notificações. Esse resultado permite observar a evolução anual dos registros e
identificar possíveis variações no volume de notificações ao longo do tempo.

Na análise territorial, o município com maior volume de notificações dentro do
recorte foi {municipio_maior_volume["municipio"]}, com
{int(municipio_maior_volume["total_recorte_domestico_familiar"]):,} notificações.
A análise por município permite identificar a concentração espacial dos registros
e destacar localidades com maior volume absoluto de notificações.

Esses resultados não devem ser interpretados como a totalidade jurídica dos casos
de violência doméstica e familiar, mas como uma aproximação metodológica baseada
em informações disponíveis no SINAN, especialmente local de ocorrência e vínculo
com o provável autor.
"""

caminho_texto = PASTA_RESULTADOS / "10_texto_base_interpretacao_artigo.md"

caminho_texto.write_text(texto_interpretacao, encoding="utf-8")

print(f"Texto-base salvo em: {caminho_texto}")
print(texto_interpretacao)
