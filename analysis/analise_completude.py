from pathlib import Path
import duckdb
import pandas as pd


# Caminho do banco DuckDB
DUCKDB_PATH = Path("data/warehouse/sinan_sds.duckdb")

# Pasta de saída da análise
OUTPUT_DIR = Path("analysis/completude_sinan")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# Valores considerados ausentes, ignorados ou não informados
VALORES_AUSENTES = {
    "",
    "IGNORADO",
    "IGNORADA",
    "NÃO INFORMADO",
    "NAO INFORMADO",
    "DADO NÃO INFORMADO",
    "DADO NAO INFORMADO",
    "NULL",
    "NAN",
    "NONE",
}


def normalizar_valor(valor):
    """Padroniza valores para comparação."""
    if pd.isna(valor):
        return ""

    return str(valor).strip().upper()


def eh_ausente(valor):
    """Verifica se o valor é ausente, ignorado ou não informado."""
    return normalizar_valor(valor) in VALORES_AUSENTES


def calcular_completude_coluna(df, coluna, nome_variavel):
    """Calcula completude de uma coluna simples."""
    total = len(df)

    total_ausente = df[coluna].apply(eh_ausente).sum()
    total_informado = total - total_ausente

    return {
        "variavel": nome_variavel,
        "total_registros": total,
        "total_ausente_ignorado_nao_informado": int(total_ausente),
        "total_informado": int(total_informado),
        "percentual_ausente_ignorado_nao_informado": round((total_ausente / total) * 100, 2),
        "percentual_completude": round((total_informado / total) * 100, 2),
    }


def calcular_completude_vinculo(df, colunas_vinculo):
    """
    Calcula completude do vínculo com o provável autor.

    Considera como vínculo informado quando pelo menos uma coluna REL_* possui valor SIM.
    """
    total = len(df)

    def possui_vinculo_informado(linha):
        for coluna in colunas_vinculo:
            valor = normalizar_valor(linha[coluna])
            if valor == "SIM":
                return True
        return False

    vinculo_informado = df[colunas_vinculo].apply(possui_vinculo_informado, axis=1)

    total_informado = vinculo_informado.sum()
    total_ausente = total - total_informado

    return {
        "variavel": "Vínculo com o provável autor",
        "total_registros": total,
        "total_ausente_ignorado_nao_informado": int(total_ausente),
        "total_informado": int(total_informado),
        "percentual_ausente_ignorado_nao_informado": round((total_ausente / total) * 100, 2),
        "percentual_completude": round((total_informado / total) * 100, 2),
    }


def main():
    # Conecta ao DuckDB
    con = duckdb.connect(str(DUCKDB_PATH))

    # Carrega a tabela Silver do SINAN
    df = con.execute("""
    SELECT *
    FROM silver.sinan
    WHERE UPPER(TRIM(RECORTE_DOMESTICO_FAMILIAR)) = 'SIM'
""").fetchdf()

    con.close()

    # Colunas simples para análise de completude
    variaveis_simples = {
        "CS_RACA": "Raça/cor",
        "ESCOLARIDADE": "Escolaridade",
        "FAIXA_ETARIA_SDS": "Faixa etária",
        "LOCAL_OCOR": "Local de ocorrência",
    }

    resultados = []

    # Calcula completude das variáveis simples
    for coluna, nome_variavel in variaveis_simples.items():
        resultados.append(calcular_completude_coluna(df, coluna, nome_variavel))

    # Colunas que representam vínculo com o provável autor
    colunas_vinculo = [
        "REL_PAI",
        "REL_MAE",
        "REL_PAD",
        "REL_MAD",
        "REL_CONJ",
        "REL_EXCON",
        "REL_NAMO",
        "REL_EXNAM",
        "REL_IRMAO",
        "REL_FILHO",
        "REL_CUIDA",
    ]

    # Mantém apenas colunas existentes na base
    colunas_vinculo = [col for col in colunas_vinculo if col in df.columns]

    resultados.append(calcular_completude_vinculo(df, colunas_vinculo))

    # Gera DataFrame final
    df_completude = pd.DataFrame(resultados)

    # Salva resultado em CSV
    caminho_saida = OUTPUT_DIR / "completude_variaveis_sinan.csv"
    df_completude.to_csv(caminho_saida, index=False, encoding="utf-8-sig")

    print("\nTabela de completude gerada:\n")
    print(df_completude.to_string(index=False))

    print(f"\nArquivo salvo em: {caminho_saida}")


if __name__ == "__main__":
    main()