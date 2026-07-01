from pathlib import Path
import duckdb
import pandas as pd


DUCKDB_PATH = Path("data/warehouse/sinan_sds.duckdb")
OUTPUT_DIR = Path("analysis/esquemas_tabelas")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


TABELAS = [
    ("silver", "sinan"),
    ("silver", "sds"),
    ("silver", "ibge"),
    ("silver", "cnes"),
    ("gold", "sds_sinan"),
]


def buscar_colunas(con, schema, tabela):
    """Retorna as colunas reais de uma tabela no DuckDB."""
    query = f"""
        SELECT
            table_schema,
            table_name,
            ordinal_position,
            column_name,
            data_type
        FROM information_schema.columns
        WHERE table_schema = '{schema}'
          AND table_name = '{tabela}'
        ORDER BY ordinal_position;
    """

    return con.execute(query).fetchdf()


def main():
    if not DUCKDB_PATH.exists():
        raise FileNotFoundError(
            f"Banco DuckDB não encontrado em: {DUCKDB_PATH}. "
            "Execute o pipeline antes de inspecionar os esquemas."
        )

    con = duckdb.connect(str(DUCKDB_PATH))

    todos_esquemas = []

    for schema, tabela in TABELAS:
        df_colunas = buscar_colunas(con, schema, tabela)

        if df_colunas.empty:
            print(f"\n⚠️ Tabela não encontrada: {schema}.{tabela}")
            continue

        nome_completo = f"{schema}.{tabela}"

        print("\n" + "=" * 80)
        print(f"ESQUEMA DA TABELA: {nome_completo}")
        print("=" * 80)
        print(df_colunas[["ordinal_position", "column_name", "data_type"]].to_string(index=False))

        # Salva CSV individual
        caminho_csv = OUTPUT_DIR / f"{schema}_{tabela}_colunas.csv"
        df_colunas.to_csv(caminho_csv, index=False, encoding="utf-8-sig")

        todos_esquemas.append(df_colunas)

    con.close()

    if todos_esquemas:
        df_final = pd.concat(todos_esquemas, ignore_index=True)

        # Salva CSV geral
        caminho_geral_csv = OUTPUT_DIR / "esquema_silver_gold_completo.csv"
        df_final.to_csv(caminho_geral_csv, index=False, encoding="utf-8-sig")

        # Salva Markdown geral para consultar/copiar no artigo
        caminho_md = OUTPUT_DIR / "esquema_silver_gold_completo.md"

        with open(caminho_md, "w", encoding="utf-8") as f:
            f.write("# Esquema das tabelas Silver e Gold\n\n")

            for schema, tabela in TABELAS:
                df_tabela = df_final[
                    (df_final["table_schema"] == schema)
                    & (df_final["table_name"] == tabela)
                ]

                if df_tabela.empty:
                    continue

                f.write(f"## {schema}.{tabela}\n\n")
                f.write("| Posição | Coluna | Tipo |\n")
                f.write("|---:|---|---|\n")

                for _, row in df_tabela.iterrows():
                    f.write(
                        f"| {row['ordinal_position']} | `{row['column_name']}` | `{row['data_type']}` |\n"
                    )

                f.write("\n")

        print("\nArquivos gerados:")
        print(f"- {caminho_geral_csv}")
        print(f"- {caminho_md}")
        print(f"- CSVs individuais em: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()