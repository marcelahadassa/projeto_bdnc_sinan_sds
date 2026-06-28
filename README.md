# Pipeline SINAN/SDS-PE — Violência contra a mulher em Pernmabuco (2014-2024)

Este projeto constrói um pipeline de dados para extração, tratamento, validação, integração e armazenamento de bases relacionadas, principalmente, à violência doméstica e familiar em Pernambuco.

O fluxo utiliza dados do SINAN, SDS-PE, IBGE e CNES, organizados em camadas Bronze, Silver, Gold e Warehouse. A orquestração é feita com Dagster e o armazenamento final é realizado em DuckDB.

## Objetivo

Estruturar uma base integrada e reprodutível para análise comparativa entre notificações de violência registradas no SINAN e registros administrativos da SDS-PE.

A base final permite comparar registros por município, ano, sexo, faixa etária e tipo de violência.

## Arquitetura

```text
Bronze
├── Extração dos dados brutos
├── Conversão para Parquet
└── Validação inicial

Silver
├── Tratamento do SINAN
├── Tratamento da SDS
├── Tratamento do IBGE
└── Tratamento do CNES

Gold
└── Cruzamento agregado entre SINAN e SDS

Warehouse
└── Armazenamento em DuckDB
```

## Estrutura do projeto

```text
projeto_bdnc_sinan_sds/
├── data/
│   ├── bronze/
│   ├── silver/
│   ├── gold/
│   └── warehouse/
├── docs/
├── src/
│   ├── bronze/
│   ├── silver/
│   ├── gold/
│   ├── storage/
│   ├── quality/
│   ├── orchestration/
│   └── config.py
├── README.md
└── requirements.txt
```

## Instalação



```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
> **Importante:** O projeto foi desenvolvido e testado com Python 3.11.
> Versões mais recentes (como Python 3.13) podem apresentar incompatibilidades com algumas dependências, como a biblioteca `datasus_dbc`.

## Execução com Dagster

```bash
dagster dev -f src/orchestration/definitions.py
```

Acesse o link para a interface pelo terminal e, após abrir o site, clique em:

```text
Jobs → pipeline_completo_sinan_sds → Launch Run
```

## Consulta no DuckDB

O banco final é salvo em:

```text
data/warehouse/sinan_sds.duckdb
```

Consulta principal:

```sql
SELECT *
FROM gold.sds_sinan
LIMIT 10;
```

## Documentação no Dagster

Além dos arquivos de documentação do projeto, o Dagster também é utilizado como uma ferramenta de documentação técnica do pipeline.

Na interface do Dagster, cada etapa do fluxo é representada por um asset. Esses assets possuem descrições, grupos, dependências e metadados que ajudam a entender a função de cada parte do pipeline.

A documentação no Dagster inclui:

- descrição de cada asset;
- organização por camadas: Bronze, Silver, Gold e Warehouse;
- visualização da linhagem dos dados no Asset Graph;
- metadados das tabelas finais;
- schema esperado das bases tratadas;
- nome das colunas;
- tipo esperado de cada campo;
- descrição dos principais campos;
- quantidade de linhas materializadas;
- caminho dos arquivos gerados;
- histórico de execuções;
- checks de qualidade dos dados.

Com isso, o Dagster funciona como um catálogo técnico do projeto, permitindo acompanhar tanto a execução do pipeline quanto a estrutura esperada dos dados.

### Metadados documentados nos assets

Os principais metadados são adicionados aos assets das camadas Silver, Gold e Warehouse.

Na camada Silver, são documentadas as bases tratadas do SINAN e da SDS, incluindo campos como município, ano, sexo, faixa etária, total de vítimas e indicadores de violência.

Na camada Gold, é documentada a base final `gold.sds_sinan`, que consolida a comparação agregada entre SINAN e SDS por município, ano, sexo e faixa etária.

No Warehouse, é documentado o banco DuckDB, que armazena as tabelas das camadas Bronze, Silver e Gold.

### Diferença entre documentação e qualidade

A documentação descreve o que é esperado dos dados, como nomes de campos, tipos e significado das colunas.

Os checks de qualidade validam se os dados realmente cumprem essas regras durante a execução do pipeline.

```text
Documentação no Dagster → descreve a estrutura esperada
Asset Checks → validam a qualidade dos dados gerados
```

Essa combinação torna o pipeline mais fácil de entender, auditar e manter.

## Qualidade dos dados

A qualidade é monitorada por Asset Checks no Dagster, validando:

- arquivos brutos;
- arquivos Parquet;
- colunas obrigatórias;
- totais das camadas;
- consistência entre Gold e Silver;
- consistência entre Parquet Gold e DuckDB.

## Resultado final

Arquivo Gold:

```text
data/gold/sds_sinan/sds_sinan_final.parquet
```

Tabelas principais no DuckDB:

```text
gold.sds_sinan   → tabela final integrada entre SDS e SINAN
silver.sds       → tabela tratada da SDS
silver.sinan     → tabela tratada do SINAN
```
## Licença

Este projeto está licenciado sob a licença Creative Commons Attribution 4.0 International (CC BY 4.0).

Isso permite o compartilhamento e adaptação do material, desde que seja dado o devido crédito aos autores.

Mais informações: https://creativecommons.org/licenses/by/4.0/