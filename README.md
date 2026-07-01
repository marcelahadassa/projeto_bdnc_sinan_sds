# Pipeline SINAN/SDS-PE — Violência contra a mulher em Pernambuco (2014-2024)

Este projeto constrói um pipeline de dados para extração, tratamento, validação, integração, análise e armazenamento de bases relacionadas à violência contra a mulher em Pernambuco, com foco no recorte doméstico/familiar.

O fluxo utiliza dados do SINAN, SDS-PE, IBGE e CNES, organizados em camadas Bronze, Silver, Gold e Warehouse. A orquestração é feita com Dagster, os dados são armazenados em formato Parquet e o armazenamento analítico final é realizado em DuckDB.

## Objetivo

Estruturar uma base integrada, documentada e reprodutível para análise comparativa entre notificações de violência registradas no SINAN e registros administrativos da SDS-PE.

A base final permite comparar registros por município, ano, sexo, faixa etária e tipo de violência, além de apoiar análises exploratórias sobre violência doméstica/familiar contra a mulher em Pernambuco.

## Fontes de dados

O projeto utiliza quatro fontes públicas principais:

- **SINAN/DataSUS**: notificações de violência interpessoal/autoprovocada, série `VIOLBR14` a `VIOLBR24`, considerando registros de mulheres em Pernambuco no período de 2014 a 2024.
- **SDS-PE**: registros administrativos e policiais relacionados à violência doméstica/familiar contra a mulher em Pernambuco, utilizados na comparação entre 2015 e 2024.
- **IBGE**: base auxiliar de municípios, utilizada para padronização geográfica.
- **CNES**: base auxiliar de estabelecimentos de saúde, utilizada para enriquecer os registros do SINAN com informações sobre unidades notificadoras.

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

Analysis
└── Geração de tabelas, gráficos e textos-base
```

## Estrutura do projeto

```text
projeto_bdnc_sinan_sds/
├── analysis/
│   ├── analise_completude.py
│   ├── analise_discrepancia_gold.py
│   ├── analise_sinan_recorte_domestico.py
│   └── analises_schemas.py
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
├── requirements.txt
├── CITATION.cff
├── LICENSE
└── .zenodo.json
```

## Instalação

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

> **Importante:** O projeto foi desenvolvido e testado com Python 3.11. Versões mais recentes, como Python 3.13, podem apresentar incompatibilidades com algumas dependências, como a biblioteca `datasus_dbc`.

## Execução com Dagster

Para iniciar a interface do Dagster, execute:

```bash
dagster dev -f src/orchestration/definitions.py
```

Em seguida, acesse o link exibido no terminal e execute o pipeline completo em:

```text
Jobs → pipeline_completo_sinan_sds → Launch Run
```

Também é possível materializar assets específicos pela interface do Dagster, conforme a necessidade de reprocessamento.

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

Tabelas principais no DuckDB:

```text
gold.sds_sinan   → tabela final integrada entre SDS e SINAN
silver.sds       → tabela tratada da SDS
silver.sinan     → tabela tratada do SINAN
silver.ibge      → base auxiliar tratada de municípios
silver.cnes      → base auxiliar tratada de unidades de saúde
```

## Documentação no Dagster

Além dos arquivos de documentação do projeto, o Dagster também é utilizado como ferramenta de documentação técnica do pipeline.

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

Na camada Silver, são documentadas as bases tratadas do SINAN, SDS, IBGE e CNES. Esses metadados incluem informações sobre campos como município, ano, sexo, faixa etária, total de vítimas, indicadores de violência, unidades notificadoras e códigos geográficos.

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

- existência dos arquivos brutos;
- conversão correta para Parquet;
- presença de colunas obrigatórias;
- validade das bases tratadas nas camadas Silver;
- existência de linhas na camada Gold;
- ausência de nulos reais nas chaves principais da Gold;
- ausência de totais negativos;
- consistência entre Gold e Silver;
- consistência entre Parquet Gold e DuckDB.

No tratamento do SINAN, também é realizada a remoção de duplicatas exatas após o filtro de escopo. Na versão atual, foram identificadas e removidas 130 duplicatas, resultando em 138.076 registros na base `silver.sinan`.

## Análises

Além do pipeline principal, o projeto inclui scripts de análise na pasta `analysis/`. Esses scripts utilizam as bases tratadas e integradas geradas pelo pipeline para produzir tabelas, gráficos e textos-base utilizados na exploração dos dados e na construção do artigo.

As análises devem ser executadas após a materialização completa do pipeline no Dagster, pois dependem dos arquivos Parquet tratados e/ou do banco DuckDB gerado na camada Warehouse.

Entre as análises desenvolvidas, destacam-se:

- análise dos schemas das tabelas geradas;
- análise de completude das principais variáveis do SINAN no recorte doméstico/familiar;
- análise territorial do recorte doméstico/familiar por município;
- comparação entre volume absoluto e percentual de notificações no recorte doméstico/familiar;
- análise das diferenças entre SINAN e SDS por tipo de violência.

Exemplos de execução:

```bash
python analysis/analises_schemas.py
python analysis/analise_completude.py
python analysis/analise_sinan_recorte_domestico.py
python analysis/analise_discrepancia_gold.py
```

Os resultados gerados pelos scripts podem incluir arquivos `.csv`, gráficos `.png` e textos auxiliares em `.md`, organizados para apoiar a interpretação dos dados e a documentação dos resultados.

> Os nomes dos scripts podem variar conforme a versão do projeto. Todos devem ser executados a partir da raiz do repositório.

## Resultado final

Arquivo Gold:

```text
data/gold/sds_sinan/sds_sinan_final.parquet
```

Arquivos Silver principais:

```text
data/silver/sinan/base_sinan_tratada.parquet
data/silver/sds/base_sds_tratada.parquet
data/silver/ibge/municipios_tratado.parquet
data/silver/cnes/unidades_tratadas.parquet
```

Banco analítico:

```text
data/warehouse/sinan_sds.duckdb
```

Volumetria da versão atual:

```text
silver.sinan      → 138.076 registros
silver.sds        → 338.489 registros
gold.sds_sinan    → 14.116 combinações agregadas
```

## Disponibilização no Zenodo

A versão estável do projeto será disponibilizada no Zenodo, com DOI permanente, permitindo a citação e o reuso acadêmico do dataset e do código associado.

A publicação no Zenodo inclui:

- código-fonte do pipeline;
- arquivos Parquet tratados das camadas Silver e Gold;
- banco analítico DuckDB;
- scripts de análise;
- resultados agregados das análises;
- documentação do projeto;
- dicionário de dados;
- arquivo de citação;
- licença de uso.

Arquivos principais disponibilizados:

```text
data/silver/sinan/base_sinan_tratada.parquet
data/silver/sds/base_sds_tratada.parquet
data/silver/ibge/municipios_tratado.parquet
data/silver/cnes/unidades_tratadas.parquet
data/gold/sds_sinan/sds_sinan_final.parquet
data/warehouse/sinan_sds.duckdb
```

```text
DOI: 10.5281/zenodo.21113070
```

A versão publicada no Zenodo corresponde ao release estável do projeto. Assim, alterações posteriores no código, nos dados ou nas análises devem ser documentadas em uma nova versão.

## Citação

Caso utilize este projeto, cite a versão publicada no Zenodo e o repositório associado.

```text
Hadassa, M.; Aurelio, L.; Vasconcelos, M.; Accioly, S.; Neves, G. ViolênciaDataPE: Dataset Integrado de Violência Doméstica/Familiar contra a Mulher em Pernambuco. Versão 1.0.0.
```

## Cuidados com dados sensíveis

As bases utilizadas são públicas e não incluem identificadores diretos como nome, CPF ou endereço completo. Ainda assim, por se tratar de dados relacionados à violência contra a mulher, o uso do dataset deve respeitar princípios éticos, evitando tentativas de reidentificação, exposição de grupos pequenos ou interpretações que possam estigmatizar municípios, vítimas ou serviços.

## Licença

Este projeto está licenciado sob a licença Creative Commons Attribution 4.0 International (CC BY 4.0).

Isso permite o compartilhamento e adaptação do material, desde que seja dado o devido crédito aos autores.

Mais informações: https://creativecommons.org/licenses/by/4.0/
