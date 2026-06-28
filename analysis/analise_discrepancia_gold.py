# %%
"""
Análise descritiva da discrepância entre SDS e SINAN na camada Gold.

Este script usa a tabela gold.sds_sinan do DuckDB para produzir tabelas e gráficos
que ajudam a identificar diferenças de captação entre os registros da SDS e as
notificações do SINAN.

Importante:
A comparação entre SDS e SINAN considera apenas o período de 2015 a 2024,
pois a base SDS utilizada no projeto inicia em 2015. O ano de 2014 é excluído
da análise comparativa para evitar distorção, já que nesse ano há registros do
SINAN, mas não há registros equivalentes da SDS na base integrada.

Saídas geradas em:
analysis/discrepancia_gold/
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
# Período usado na comparação entre SDS e SINAN.
# A SDS começa em 2015, por isso 2014 fica fora da análise de discrepância.
ANO_INICIO = 2015
ANO_FIM = 2024


# %%
PASTA_RESULTADOS = ROOT_DIR / "analysis" / "discrepancia_gold"
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


# %%
def consulta_gold_filtrada():
    """
    Retorna a subconsulta padrão da Gold no período comparável entre SDS e SINAN.
    """

    return f"""
        SELECT *
        FROM gold.sds_sinan
        WHERE ANO BETWEEN {ANO_INICIO} AND {ANO_FIM}
    """


# ============================================================
# 1. RESUMO GERAL DA DISCREPÂNCIA
# ============================================================

# %%
sql_resumo_geral = f"""
WITH gold_filtrada AS (
    {consulta_gold_filtrada()}
)

SELECT
    COUNT(*) AS total_estratos,

    SUM(TOTAL_REGISTROS_SINAN) AS total_registros_sinan,
    SUM(TOTAL_REGISTROS_SDS) AS total_registros_sds,
    SUM(TOTAL_VITIMAS_SDS) AS total_vitimas_sds,

    SUM(DIF_TOTAL_SDS_MENOS_SINAN) AS diferenca_total_sds_menos_sinan,

    ROUND(
        SUM(TOTAL_VITIMAS_SDS) * 1.0
        / NULLIF(SUM(TOTAL_REGISTROS_SINAN), 0),
        4
    ) AS razao_geral_sds_sinan,

    ROUND(
        100.0 * SUM(DIF_TOTAL_SDS_MENOS_SINAN)
        / NULLIF(SUM(TOTAL_VITIMAS_SDS), 0),
        2
    ) AS percentual_diferenca_sobre_sds,

    SUM(
        CASE
            WHEN TOTAL_VITIMAS_SDS > TOTAL_REGISTROS_SINAN THEN 1
            ELSE 0
        END
    ) AS estratos_sds_maior_que_sinan,

    SUM(
        CASE
            WHEN TOTAL_VITIMAS_SDS < TOTAL_REGISTROS_SINAN THEN 1
            ELSE 0
        END
    ) AS estratos_sinan_maior_que_sds,

    SUM(
        CASE
            WHEN TOTAL_VITIMAS_SDS = TOTAL_REGISTROS_SINAN THEN 1
            ELSE 0
        END
    ) AS estratos_com_mesmo_total

FROM gold_filtrada;
"""

df_resumo_geral = executar_consulta(sql_resumo_geral)

print(f"\nResumo geral da discrepância ({ANO_INICIO}-{ANO_FIM}):")
print(df_resumo_geral)

salvar_csv(df_resumo_geral, "01_resumo_geral_discrepancia_2015_2024.csv")


# ============================================================
# 2. ESTATÍSTICAS DESCRITIVAS POR ESTRATO
# ============================================================

# %%
sql_estratos = f"""
WITH gold_filtrada AS (
    {consulta_gold_filtrada()}
)

SELECT
    MUNICIPIO,
    ANO,
    SEXO,
    FAIXA_ETARIA_SDS,
    TOTAL_REGISTROS_SINAN,
    TOTAL_REGISTROS_SDS,
    TOTAL_VITIMAS_SDS,
    DIF_TOTAL_SDS_MENOS_SINAN,

    TOTAL_VITIMAS_SDS * 1.0
    / NULLIF(TOTAL_REGISTROS_SINAN, 0) AS RAZAO_SDS_SINAN,

    100.0 * DIF_TOTAL_SDS_MENOS_SINAN
    / NULLIF(TOTAL_VITIMAS_SDS, 0) AS PERCENTUAL_DIFERENCA_SOBRE_SDS

FROM gold_filtrada
WHERE TOTAL_REGISTROS_SINAN > 0
   OR TOTAL_VITIMAS_SDS > 0;
"""

df_estratos = executar_consulta(sql_estratos)

df_descritivas = df_estratos[
    [
        "DIF_TOTAL_SDS_MENOS_SINAN",
        "RAZAO_SDS_SINAN",
        "PERCENTUAL_DIFERENCA_SOBRE_SDS",
    ]
].describe(percentiles=[0.25, 0.5, 0.75]).reset_index()

print("\nEstatísticas descritivas por estrato:")
print(df_descritivas)

salvar_csv(df_estratos, "02_estratos_com_metricas_discrepancia_2015_2024.csv")
salvar_csv(df_descritivas, "03_estatisticas_descritivas_estratos_2015_2024.csv")


# ============================================================
# 3. DISCREPÂNCIA POR ANO
# ============================================================

# %%
sql_discrepancia_por_ano = f"""
WITH gold_filtrada AS (
    {consulta_gold_filtrada()}
)

SELECT
    ANO,

    SUM(TOTAL_REGISTROS_SINAN) AS total_registros_sinan,
    SUM(TOTAL_REGISTROS_SDS) AS total_registros_sds,
    SUM(TOTAL_VITIMAS_SDS) AS total_vitimas_sds,

    SUM(DIF_TOTAL_SDS_MENOS_SINAN) AS diferenca_sds_menos_sinan,

    ROUND(
        SUM(TOTAL_VITIMAS_SDS) * 1.0
        / NULLIF(SUM(TOTAL_REGISTROS_SINAN), 0),
        4
    ) AS razao_sds_sinan,

    ROUND(
        100.0 * SUM(DIF_TOTAL_SDS_MENOS_SINAN)
        / NULLIF(SUM(TOTAL_VITIMAS_SDS), 0),
        2
    ) AS percentual_diferenca_sobre_sds

FROM gold_filtrada
GROUP BY ANO
ORDER BY ANO;
"""

df_por_ano = executar_consulta(sql_discrepancia_por_ano)

print("\nDiscrepância por ano:")
print(df_por_ano)

salvar_csv(df_por_ano, "04_discrepancia_por_ano_2015_2024.csv")


# %%
plt.figure(figsize=(9, 5))
plt.plot(df_por_ano["ANO"], df_por_ano["total_registros_sinan"], marker="o", label="SINAN")
plt.plot(df_por_ano["ANO"], df_por_ano["total_vitimas_sds"], marker="o", label="SDS")
plt.title(f"Comparação anual entre SINAN e SDS ({ANO_INICIO}-{ANO_FIM})")
plt.xlabel("Ano")
plt.ylabel("Total de registros/vítimas")
plt.legend()
plt.grid(True)
salvar_grafico("grafico_01_comparacao_anual_sinan_sds_2015_2024.png")


# %%
plt.figure(figsize=(9, 5))
plt.bar(df_por_ano["ANO"], df_por_ano["diferenca_sds_menos_sinan"])
plt.title(f"Diferença anual entre SDS e SINAN ({ANO_INICIO}-{ANO_FIM})")
plt.xlabel("Ano")
plt.ylabel("SDS - SINAN")
plt.grid(axis="y")
salvar_grafico("grafico_02_diferenca_anual_sds_menos_sinan_2015_2024.png")


# ============================================================
# 4. DISCREPÂNCIA POR FAIXA ETÁRIA
# ============================================================

# %%
sql_discrepancia_por_faixa = f"""
WITH gold_filtrada AS (
    {consulta_gold_filtrada()}
)

SELECT
    FAIXA_ETARIA_SDS,

    SUM(TOTAL_REGISTROS_SINAN) AS total_registros_sinan,
    SUM(TOTAL_REGISTROS_SDS) AS total_registros_sds,
    SUM(TOTAL_VITIMAS_SDS) AS total_vitimas_sds,

    SUM(DIF_TOTAL_SDS_MENOS_SINAN) AS diferenca_sds_menos_sinan,

    ROUND(
        SUM(TOTAL_VITIMAS_SDS) * 1.0
        / NULLIF(SUM(TOTAL_REGISTROS_SINAN), 0),
        4
    ) AS razao_sds_sinan,

    ROUND(
        100.0 * SUM(DIF_TOTAL_SDS_MENOS_SINAN)
        / NULLIF(SUM(TOTAL_VITIMAS_SDS), 0),
        2
    ) AS percentual_diferenca_sobre_sds

FROM gold_filtrada
GROUP BY FAIXA_ETARIA_SDS
ORDER BY
    CASE FAIXA_ETARIA_SDS
        WHEN '00-11' THEN 1
        WHEN '12-17' THEN 2
        WHEN '18-24' THEN 3
        WHEN '25-29' THEN 4
        WHEN '30-34' THEN 5
        WHEN '35-64' THEN 6
        WHEN '65 OU MAIS' THEN 7
        ELSE 8
    END;
"""

df_por_faixa = executar_consulta(sql_discrepancia_por_faixa)

print("\nDiscrepância por faixa etária:")
print(df_por_faixa)

salvar_csv(df_por_faixa, "05_discrepancia_por_faixa_etaria_2015_2024.csv")


# %%
plt.figure(figsize=(9, 5))
plt.bar(df_por_faixa["FAIXA_ETARIA_SDS"], df_por_faixa["diferenca_sds_menos_sinan"])
plt.title(f"Diferença entre SDS e SINAN por faixa etária ({ANO_INICIO}-{ANO_FIM})")
plt.xlabel("Faixa etária")
plt.ylabel("SDS - SINAN")
plt.xticks(rotation=45)
plt.grid(axis="y")
salvar_grafico("grafico_03_diferenca_por_faixa_etaria_2015_2024.png")


# ============================================================
# 5. MUNICÍPIOS COM MAIOR DISCREPÂNCIA
# ============================================================

# %%
sql_top_municipios = f"""
WITH gold_filtrada AS (
    {consulta_gold_filtrada()}
)

SELECT
    MUNICIPIO,

    SUM(TOTAL_REGISTROS_SINAN) AS total_registros_sinan,
    SUM(TOTAL_REGISTROS_SDS) AS total_registros_sds,
    SUM(TOTAL_VITIMAS_SDS) AS total_vitimas_sds,

    SUM(DIF_TOTAL_SDS_MENOS_SINAN) AS diferenca_sds_menos_sinan,

    ROUND(
        SUM(TOTAL_VITIMAS_SDS) * 1.0
        / NULLIF(SUM(TOTAL_REGISTROS_SINAN), 0),
        4
    ) AS razao_sds_sinan,

    ROUND(
        100.0 * SUM(DIF_TOTAL_SDS_MENOS_SINAN)
        / NULLIF(SUM(TOTAL_VITIMAS_SDS), 0),
        2
    ) AS percentual_diferenca_sobre_sds

FROM gold_filtrada
GROUP BY MUNICIPIO
ORDER BY diferenca_sds_menos_sinan DESC
LIMIT 20;
"""

df_top_municipios = executar_consulta(sql_top_municipios)

print("\nTop municípios com maior diferença SDS - SINAN:")
print(df_top_municipios)

salvar_csv(df_top_municipios, "06_top_20_municipios_maior_discrepancia_2015_2024.csv")


# %%
plt.figure(figsize=(10, 6))
plt.barh(df_top_municipios["MUNICIPIO"], df_top_municipios["diferenca_sds_menos_sinan"])
plt.title(f"Top 20 municípios com maior diferença SDS - SINAN ({ANO_INICIO}-{ANO_FIM})")
plt.xlabel("SDS - SINAN")
plt.ylabel("Município")
plt.gca().invert_yaxis()
plt.grid(axis="x")
salvar_grafico("grafico_04_top_20_municipios_discrepancia_2015_2024.png")


# ============================================================
# 6. DISCREPÂNCIA POR TIPO DE VIOLÊNCIA
# ============================================================

# %%
sql_tipos_violencia = f"""
WITH gold_filtrada AS (
    {consulta_gold_filtrada()}
)

SELECT
    'VIOL_FISIC' AS tipo_violencia,
    SUM(SINAN_VIOL_FISIC) AS total_sinan,
    SUM(SDS_VIOL_FISIC) AS total_sds,
    SUM(SDS_VIOL_FISIC) - SUM(SINAN_VIOL_FISIC) AS diferenca_sds_menos_sinan,
    ROUND(SUM(SDS_VIOL_FISIC) * 1.0 / NULLIF(SUM(SINAN_VIOL_FISIC), 0), 4) AS razao_sds_sinan
FROM gold_filtrada

UNION ALL

SELECT
    'VIOL_PSICO' AS tipo_violencia,
    SUM(SINAN_VIOL_PSICO) AS total_sinan,
    SUM(SDS_VIOL_PSICO) AS total_sds,
    SUM(SDS_VIOL_PSICO) - SUM(SINAN_VIOL_PSICO) AS diferenca_sds_menos_sinan,
    ROUND(SUM(SDS_VIOL_PSICO) * 1.0 / NULLIF(SUM(SINAN_VIOL_PSICO), 0), 4) AS razao_sds_sinan
FROM gold_filtrada

UNION ALL

SELECT
    'VIOL_SEXU' AS tipo_violencia,
    SUM(SINAN_VIOL_SEXU) AS total_sinan,
    SUM(SDS_VIOL_SEXU) AS total_sds,
    SUM(SDS_VIOL_SEXU) - SUM(SINAN_VIOL_SEXU) AS diferenca_sds_menos_sinan,
    ROUND(SUM(SDS_VIOL_SEXU) * 1.0 / NULLIF(SUM(SINAN_VIOL_SEXU), 0), 4) AS razao_sds_sinan
FROM gold_filtrada

UNION ALL

SELECT
    'VIOL_FINAN' AS tipo_violencia,
    SUM(SINAN_VIOL_FINAN) AS total_sinan,
    SUM(SDS_VIOL_FINAN) AS total_sds,
    SUM(SDS_VIOL_FINAN) - SUM(SINAN_VIOL_FINAN) AS diferenca_sds_menos_sinan,
    ROUND(SUM(SDS_VIOL_FINAN) * 1.0 / NULLIF(SUM(SINAN_VIOL_FINAN), 0), 4) AS razao_sds_sinan
FROM gold_filtrada

ORDER BY diferenca_sds_menos_sinan DESC;
"""

df_tipos_violencia = executar_consulta(sql_tipos_violencia)

print("\nDiscrepância por tipo de violência:")
print(df_tipos_violencia)

salvar_csv(df_tipos_violencia, "07_discrepancia_por_tipo_violencia_2015_2024.csv")


# %%
plt.figure(figsize=(8, 5))
plt.bar(df_tipos_violencia["tipo_violencia"], df_tipos_violencia["diferenca_sds_menos_sinan"])
plt.title(f"Diferença SDS - SINAN por tipo de violência ({ANO_INICIO}-{ANO_FIM})")
plt.xlabel("Tipo de violência")
plt.ylabel("SDS - SINAN")
plt.xticks(rotation=45)
plt.grid(axis="y")
salvar_grafico("grafico_05_discrepancia_por_tipo_violencia_2015_2024.png")


# ============================================================
# 7. RECIFE COMO RECORTE ILUSTRATIVO
# ============================================================

# %%
sql_recife = f"""
WITH gold_filtrada AS (
    {consulta_gold_filtrada()}
)

SELECT
    ANO,
    FAIXA_ETARIA_SDS,

    SUM(TOTAL_REGISTROS_SINAN) AS total_registros_sinan,
    SUM(TOTAL_REGISTROS_SDS) AS total_registros_sds,
    SUM(TOTAL_VITIMAS_SDS) AS total_vitimas_sds,

    SUM(DIF_TOTAL_SDS_MENOS_SINAN) AS diferenca_sds_menos_sinan,

    ROUND(
        SUM(TOTAL_VITIMAS_SDS) * 1.0
        / NULLIF(SUM(TOTAL_REGISTROS_SINAN), 0),
        4
    ) AS razao_sds_sinan,

    ROUND(
        100.0 * SUM(DIF_TOTAL_SDS_MENOS_SINAN)
        / NULLIF(SUM(TOTAL_VITIMAS_SDS), 0),
        2
    ) AS percentual_diferenca_sobre_sds

FROM gold_filtrada
WHERE MUNICIPIO = 'RECIFE'
  AND SEXO = 'F'
GROUP BY
    ANO,
    FAIXA_ETARIA_SDS
ORDER BY
    ANO,
    CASE FAIXA_ETARIA_SDS
        WHEN '00-11' THEN 1
        WHEN '12-17' THEN 2
        WHEN '18-24' THEN 3
        WHEN '25-29' THEN 4
        WHEN '30-34' THEN 5
        WHEN '35-64' THEN 6
        WHEN '65 OU MAIS' THEN 7
        ELSE 8
    END;
"""

df_recife = executar_consulta(sql_recife)

print("\nDiscrepância em Recife por ano e faixa etária:")
print(df_recife)

salvar_csv(df_recife, "08_recife_discrepancia_por_ano_faixa_2015_2024.csv")


# %%
df_recife_ano = (
    df_recife
    .groupby("ANO", as_index=False)[
        [
            "total_registros_sinan",
            "total_vitimas_sds",
            "diferenca_sds_menos_sinan",
        ]
    ]
    .sum()
)

plt.figure(figsize=(9, 5))
plt.plot(df_recife_ano["ANO"], df_recife_ano["total_registros_sinan"], marker="o", label="SINAN")
plt.plot(df_recife_ano["ANO"], df_recife_ano["total_vitimas_sds"], marker="o", label="SDS")
plt.title(f"Comparação anual entre SINAN e SDS em Recife ({ANO_INICIO}-{ANO_FIM})")
plt.xlabel("Ano")
plt.ylabel("Total de registros/vítimas")
plt.legend()
plt.grid(True)
salvar_grafico("grafico_06_recife_comparacao_anual_sinan_sds_2015_2024.png")


# ============================================================
# 8. TEXTO-BASE PARA INTERPRETAÇÃO NO ARTIGO
# ============================================================

# %%
total_sinan = int(df_resumo_geral.loc[0, "total_registros_sinan"])
total_sds = int(df_resumo_geral.loc[0, "total_vitimas_sds"])
diferenca_total = int(df_resumo_geral.loc[0, "diferenca_total_sds_menos_sinan"])
razao_geral = float(df_resumo_geral.loc[0, "razao_geral_sds_sinan"])
percentual = float(df_resumo_geral.loc[0, "percentual_diferenca_sobre_sds"])
total_estratos = int(df_resumo_geral.loc[0, "total_estratos"])
estratos_sds_maior = int(df_resumo_geral.loc[0, "estratos_sds_maior_que_sinan"])
estratos_sinan_maior = int(df_resumo_geral.loc[0, "estratos_sinan_maior_que_sds"])
estratos_iguais = int(df_resumo_geral.loc[0, "estratos_com_mesmo_total"])

texto_interpretacao = f"""
# Análise descritiva da discrepância entre SDS e SINAN

A análise da tabela Gold `gold.sds_sinan` permitiu comparar, de forma agregada,
os registros do SINAN e da SDS por município, ano, sexo e faixa etária.

Para evitar distorções na comparação, considerou-se apenas o período de
{ANO_INICIO} a {ANO_FIM}, pois a base SDS utilizada no projeto inicia em 2015.
O ano de 2014 foi excluído da análise comparativa porque possui registros do
SINAN, mas não possui registros equivalentes da SDS na base integrada.

No conjunto analisado, o SINAN apresentou {total_sinan:,} registros, enquanto
a SDS apresentou {total_sds:,} vítimas registradas. A diferença absoluta entre
as bases foi de {diferenca_total:,} registros/vítimas a mais na SDS em relação
ao SINAN.

A razão geral SDS/SINAN foi de {razao_geral:.2f}, indicando quantas vítimas
registradas na SDS existem para cada registro notificado no SINAN. Além disso,
o percentual de diferença em relação ao total da SDS foi de {percentual:.2f}%.

A comparação foi realizada em {total_estratos:,} estratos analíticos definidos
por município, ano, sexo e faixa etária. Em {estratos_sds_maior:,} estratos,
a SDS apresentou total superior ao SINAN; em {estratos_sinan_maior:,} estratos,
o SINAN apresentou total superior à SDS; e em {estratos_iguais:,} estratos os
totais foram iguais.

Esses resultados indicam discrepância expressiva entre as bases analisadas.
Como SINAN e SDS são sistemas distintos, com finalidades e fluxos de registro
diferentes, essa diferença deve ser interpretada como evidência descritiva de
diferença de captação entre os sistemas, compatível com a hipótese de possível
subnotificação nas notificações de saúde.
"""

caminho_texto = PASTA_RESULTADOS / "09_texto_base_interpretacao_artigo_2015_2024.md"

caminho_texto.write_text(texto_interpretacao, encoding="utf-8")

print(f"Texto-base salvo em: {caminho_texto}")
print(texto_interpretacao)
