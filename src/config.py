# todos os arquivos usam os mesmos caminhos para evitar inconsistências, então eles são definidos aqui e importados nos outros arquivos

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = ROOT_DIR / "data"

BRONZE_DIR = DATA_DIR / "bronze"
SILVER_DIR = DATA_DIR / "silver"
GOLD_DIR = DATA_DIR / "gold"

SINAN_BRONZE = BRONZE_DIR / "sinan"
SDS_BRONZE = BRONZE_DIR / "sds"
CNES_BRONZE = BRONZE_DIR / "cnes"
IBGE_BRONZE = BRONZE_DIR / "ibge"

SINAN_SILVER = SILVER_DIR / "sinan"
SDS_SILVER = SILVER_DIR / "sds"
CNES_SILVER = SILVER_DIR / "cnes"
IBGE_SILVER = SILVER_DIR / "ibge"

SDS_SINAN_GOLD = GOLD_DIR / "sds_sinan"

# Pasta do banco local
WAREHOUSE_DIR = DATA_DIR / "warehouse"

# Caminho do banco DuckDB
DUCKDB_PATH = WAREHOUSE_DIR / "sinan_sds.duckdb"