# Dicionário de Dados — ViolênciaDataPE

Este documento descreve as principais bases disponibilizadas no **ViolênciaDataPE**, dataset integrado sobre violência doméstica/familiar contra a mulher em Pernambuco.

O projeto integra dados do **SINAN/DataSUS**, **SDS-PE**, **IBGE** e **CNES**, processados em camadas de dados:

- **Silver**: bases tratadas, padronizadas e enriquecidas;
- **Gold**: base integrada e agregada para comparação entre SINAN e SDS;
- **Warehouse**: banco DuckDB contendo as tabelas analíticas.

> Observação: as bases Bronze preservam dados próximos à origem e podem conter estruturas específicas das fontes públicas originais. Este dicionário prioriza as bases tratadas e integradas disponibilizadas para análise e reuso.

---

## 1. Base `silver.sinan`

Arquivo principal:

```text
data/silver/sinan/base_sinan_tratada.parquet
```

Descrição: base tratada do SINAN, filtrada para registros de mulheres em Pernambuco, com variáveis categóricas traduzidas, idade padronizada, municípios enriquecidos pelo IBGE, unidades notificadoras enriquecidas pelo CNES e criação do recorte operacional `RECORTE_DOMESTICO_FAMILIAR`.

| Coluna | Tipo | Descrição |
|---|---|---|
| `ID_SINAN` | BIGINT | Identificador único artificial gerado pelo pipeline para cada registro tratado do SINAN. |
| `DT_NOTIFIC` | VARCHAR | Data de notificação do caso no SINAN. |
| `ESTADO_NOTIFICACAO` | VARCHAR | Unidade Federativa de notificação, traduzida a partir do código original. No recorte do projeto, corresponde a Pernambuco. |
| `NU_ANO` | BIGINT | Ano de referência do arquivo/notificação do SINAN. |
| `MUNICIPIO_NOTIFICACAO` | VARCHAR | Município onde a notificação foi registrada, padronizado a partir da base do IBGE. |
| `NOME_UNIDADE` | VARCHAR | Nome da unidade notificadora associada ao registro, enriquecido a partir da base CNES. |
| `DT_OCOR` | VARCHAR | Data de ocorrência da violência registrada na notificação. |
| `ANO_NASC` | BIGINT | Ano de nascimento da vítima. |
| `CODIGO_IDADE` | VARCHAR | Código original de idade do SINAN. O primeiro dígito indica a unidade de tempo e os demais indicam o valor da idade. |
| `IDADE_REAL` | VARCHAR | Idade interpretada de forma textual a partir de `CODIGO_IDADE`, preservando a unidade original quando necessário. |
| `IDADE_NUMERICA_EM_ANOS` | BIGINT | Idade padronizada em anos. Registros em horas, dias ou meses são convertidos para 0, representando vítimas com menos de um ano. |
| `FAIXA_ETARIA_SDS` | VARCHAR | Faixa etária harmonizada com a estrutura da SDS, utilizada no cruzamento agregado entre as bases. |
| `SEXO` | VARCHAR | Sexo da vítima. No recorte do projeto, a base Silver do SINAN mantém registros do sexo feminino (`F`). |
| `CS_RACA` | VARCHAR | Raça/cor da vítima após decodificação do código original do SINAN. |
| `ESCOLARIDADE` | VARCHAR | Escolaridade da vítima após decodificação do código original do SINAN. |
| `SG_UF` | VARCHAR | Unidade Federativa de residência da vítima. No recorte do projeto, corresponde a Pernambuco. |
| `MUNICIPIO_RESIDENCIA` | VARCHAR | Município de residência da vítima, padronizado com apoio da base do IBGE. |
| `MUNICIPIO_OCORRENCIA` | VARCHAR | Município onde ocorreu a violência, padronizado com apoio da base do IBGE. |
| `LOCAL_OCOR` | VARCHAR | Local de ocorrência da violência, como residência, via pública, escola, comércio/serviços, entre outros. |
| `RECORTE_DOMESTICO_FAMILIAR` | VARCHAR | Classificação operacional criada no pipeline. Recebe `SIM` quando o registro possui local residencial e/ou vínculo familiar, afetivo ou de cuidado com o provável autor; caso contrário, recebe `NAO`. |
| `ORIENT_SEX` | VARCHAR | Orientação sexual da vítima, traduzida a partir dos códigos originais do SINAN. |
| `IDENT_GEN` | VARCHAR | Identidade de gênero da vítima, traduzida a partir dos códigos originais do SINAN. |
| `DEF_TRANS` | VARCHAR | Indicador relacionado à presença de deficiência/transtorno registrada na notificação, conforme estrutura do SINAN. |
| `DEF_FISICA` | VARCHAR | Indicador de deficiência física. |
| `DEF_MENTAL` | VARCHAR | Indicador de deficiência mental. |
| `DEF_VISUAL` | VARCHAR | Indicador de deficiência visual. |
| `DEF_AUDITI` | VARCHAR | Indicador de deficiência auditiva. |
| `TRAN_MENT` | VARCHAR | Indicador de transtorno mental. |
| `VIOL_MOTIV` | VARCHAR | Motivação atribuída à violência, como sexismo, racismo, homofobia/lesbofobia/bifobia/transfobia, conflito geracional, entre outras categorias. |
| `VIOL_FISIC` | VARCHAR | Indicador de violência física. |
| `VIOL_PSICO` | VARCHAR | Indicador de violência psicológica/moral. |
| `VIOL_TORT` | VARCHAR | Indicador de tortura. |
| `VIOL_SEXU` | VARCHAR | Indicador de violência sexual. |
| `VIOL_TRAF` | VARCHAR | Indicador de tráfico de pessoas. |
| `VIOL_FINAN` | VARCHAR | Indicador de violência financeira/econômica. |
| `VIOL_NEGLI` | VARCHAR | Indicador de negligência/abandono. |
| `VIOL_INFAN` | VARCHAR | Indicador de intervenção legal/violência associada a esse campo na estrutura do SINAN. |
| `AG_FORCA` | VARCHAR | Indicador de agressão por força corporal/espancamento. |
| `AG_ENFOR` | VARCHAR | Indicador de agressão por enforcamento. |
| `AG_OBJETO` | VARCHAR | Indicador de agressão por objeto contundente. |
| `AG_CORTE` | VARCHAR | Indicador de agressão por objeto perfurocortante/cortante. |
| `AG_QUENTE` | VARCHAR | Indicador de agressão por substância ou objeto quente. |
| `AG_ENVEN` | VARCHAR | Indicador de agressão por envenenamento/intoxicação. |
| `AG_FOGO` | VARCHAR | Indicador de agressão por arma de fogo. |
| `AG_AMEACA` | VARCHAR | Indicador de agressão por ameaça. |
| `SEX_ASSEDI` | VARCHAR | Indicador de assédio sexual. |
| `SEX_ESTUPR` | VARCHAR | Indicador de estupro. |
| `SEX_PORNO` | VARCHAR | Indicador de pornografia infantil ou exposição associada à violência sexual, conforme estrutura do SINAN. |
| `SEX_EXPLO` | VARCHAR | Indicador de exploração sexual. |
| `NUM_ENVOLV` | VARCHAR | Número de envolvidos na ocorrência, conforme categorias do SINAN. |
| `AUTOR_SEXO` | VARCHAR | Sexo do provável autor da violência. |
| `CICL_VID` | VARCHAR | Ciclo de vida do provável autor, conforme categorias do SINAN. |
| `REL_PAI` | VARCHAR | Indicador de vínculo do provável autor como pai. |
| `REL_MAE` | VARCHAR | Indicador de vínculo do provável autor como mãe. |
| `REL_PAD` | VARCHAR | Indicador de vínculo do provável autor como padrasto. |
| `REL_MAD` | VARCHAR | Indicador de vínculo do provável autor como madrasta. |
| `REL_CONJ` | VARCHAR | Indicador de vínculo do provável autor como cônjuge. |
| `REL_EXCON` | VARCHAR | Indicador de vínculo do provável autor como ex-cônjuge. |
| `REL_NAMO` | VARCHAR | Indicador de vínculo do provável autor como namorado(a). |
| `REL_EXNAM` | VARCHAR | Indicador de vínculo do provável autor como ex-namorado(a). |
| `REL_IRMAO` | VARCHAR | Indicador de vínculo do provável autor como irmão/irmã. |
| `REL_FILHO` | VARCHAR | Indicador de vínculo do provável autor como filho(a). |
| `REL_CONHEC` | VARCHAR | Indicador de vínculo do provável autor como pessoa conhecida. |
| `REL_DESCO` | VARCHAR | Indicador de provável autor desconhecido. |
| `REL_PATRAO` | VARCHAR | Indicador de vínculo do provável autor como patrão/chefe. |
| `REL_INST` | VARCHAR | Indicador de vínculo institucional. |
| `REL_POL` | VARCHAR | Indicador de provável autor policial/agente da lei, conforme estrutura do SINAN. |
| `ENC_SAUDE` | VARCHAR | Indicador de encaminhamento para rede de saúde. |
| `ASSIST_SOC` | VARCHAR | Indicador de encaminhamento para assistência social. |
| `REDE_EDUCA` | VARCHAR | Indicador de encaminhamento para rede de educação. |
| `ATEND_MULH` | VARCHAR | Indicador de encaminhamento para serviço de atendimento à mulher. |
| `CONS_TUTEL` | VARCHAR | Indicador de encaminhamento para Conselho Tutelar. |
| `CONS_IDO` | VARCHAR | Indicador de encaminhamento para Conselho do Idoso. |
| `DIR_HUMAN` | VARCHAR | Indicador de encaminhamento para órgãos de direitos humanos. |
| `MPU` | VARCHAR | Indicador de encaminhamento ao Ministério Público. |
| `DELEG_CRIA` | VARCHAR | Indicador de encaminhamento para Delegacia de Proteção à Criança/Adolescente. |
| `DELEG_MULH` | VARCHAR | Indicador de encaminhamento para Delegacia da Mulher. |
| `INFAN_JUV` | VARCHAR | Indicador de encaminhamento para Vara/Justiça da Infância e Juventude ou serviço correlato. |
| `DEFEN_PUBL` | VARCHAR | Indicador de encaminhamento para Defensoria Pública. |
| `DELEG_IDOS` | VARCHAR | Indicador de encaminhamento para Delegacia do Idoso. |
| `REL_TRAB` | VARCHAR | Indicador de vínculo relacionado ao trabalho. |

### Valores comuns em colunas indicadoras do SINAN

As colunas indicadoras geralmente utilizam valores padronizados como:

```text
SIM
NAO
NAO SE APLICA
IGNORADO
DADO NÃO INFORMADO
```

---

## 2. Base `silver.sds`

Arquivo principal:

```text
data/silver/sds/base_sds_tratada.parquet
```

Descrição: base tratada da SDS-PE, com padronização de município, ano, sexo, faixa etária, total de vítimas e criação de indicadores compatíveis com os tipos de violência analisados no SINAN.

| Coluna | Tipo | Descrição |
|---|---|---|
| `ID_SDS` | BIGINT | Identificador único artificial gerado pelo pipeline para cada registro tratado da SDS. |
| `MUNICIPIO` | VARCHAR | Município associado ao registro da SDS, padronizado para integração com o SINAN. |
| `REGIAO_GEOGRAFICA` | VARCHAR | Região geográfica associada ao município no contexto da base da SDS. |
| `NATUREZA` | VARCHAR | Natureza da ocorrência registrada na SDS, utilizada para derivar indicadores de violência. |
| `DATA_FATO` | VARCHAR | Data do fato registrado na SDS. |
| `ANO` | BIGINT | Ano do fato, extraído ou padronizado a partir da data da ocorrência. |
| `SEXO` | VARCHAR | Sexo da vítima. No recorte utilizado para comparação, corresponde ao público feminino. |
| `FAIXA_ETARIA_SDS` | VARCHAR | Faixa etária conforme estrutura da SDS. Utilizada como chave de integração agregada com o SINAN. |
| `TOTAL_VITIMAS` | BIGINT | Total de vítimas associado ao registro da SDS. |
| `VIOL_FISIC` | BIGINT | Indicador derivado da natureza da ocorrência para violência física. |
| `VIOL_PSICO` | BIGINT | Indicador derivado da natureza da ocorrência para violência psicológica/moral. |
| `VIOL_TORT` | BIGINT | Indicador derivado da natureza da ocorrência para tortura. |
| `VIOL_SEXU` | BIGINT | Indicador derivado da natureza da ocorrência para violência sexual. |
| `VIOL_TRAF` | BIGINT | Indicador derivado da natureza da ocorrência para tráfico de pessoas. |
| `VIOL_FINAN` | BIGINT | Indicador derivado da natureza da ocorrência para violência financeira/patrimonial. |
| `VIOL_NEGLI` | BIGINT | Indicador derivado da natureza da ocorrência para negligência/abandono. |
| `VIOL_INFAN` | BIGINT | Indicador derivado da natureza da ocorrência para categoria compatível com o campo correspondente do SINAN. |
| `AG_FORCA` | BIGINT | Indicador derivado da natureza da ocorrência para agressão por força corporal/espancamento. |
| `AG_ENFOR` | BIGINT | Indicador derivado da natureza da ocorrência para enforcamento. |
| `AG_OBJETO` | BIGINT | Indicador derivado da natureza da ocorrência para agressão por objeto contundente. |
| `AG_CORTE` | BIGINT | Indicador derivado da natureza da ocorrência para agressão por objeto cortante/perfurocortante. |
| `AG_QUENTE` | BIGINT | Indicador derivado da natureza da ocorrência para agressão por substância ou objeto quente. |
| `AG_ENVEN` | BIGINT | Indicador derivado da natureza da ocorrência para envenenamento/intoxicação. |
| `AG_FOGO` | BIGINT | Indicador derivado da natureza da ocorrência para arma de fogo. |
| `AG_AMEACA` | BIGINT | Indicador derivado da natureza da ocorrência para ameaça. |
| `SEX_ASSEDI` | BIGINT | Indicador derivado da natureza da ocorrência para assédio sexual. |
| `SEX_ESTUPR` | BIGINT | Indicador derivado da natureza da ocorrência para estupro. |
| `SEX_PORNO` | BIGINT | Indicador derivado da natureza da ocorrência para pornografia/exposição associada à violência sexual. |
| `SEX_EXPLO` | BIGINT | Indicador derivado da natureza da ocorrência para exploração sexual. |

### Valores comuns em colunas indicadoras da SDS

As colunas derivadas da SDS geralmente funcionam como indicadores numéricos:

```text
0 = ausência da categoria no registro
1 = presença da categoria no registro
```

Em agregações, esses indicadores podem ser somados para representar o total de registros associados à categoria.

---

## 3. Base `silver.ibge`

Arquivo principal:

```text
data/silver/ibge/municipios_tratado.parquet
```

Descrição: base auxiliar de municípios utilizada para padronização e tradução dos códigos municipais do SINAN em nomes oficiais.

| Coluna | Tipo | Descrição |
|---|---|---|
| `codigo_uf` | BIGINT | Código da Unidade Federativa segundo o IBGE. Para Pernambuco, o código é 26. |
| `codigo_ibge` | BIGINT | Código oficial do município segundo o IBGE. |
| `ID_MUNICIP_SINAN` | VARCHAR | Código de município em formato compatível com o padrão usado pelo SINAN para cruzamento. |
| `NOME_MUNICIPIO` | VARCHAR | Nome oficial do município, padronizado para uso nas demais bases do projeto. |

---

## 4. Base `silver.cnes`

Arquivo principal:

```text
data/silver/cnes/unidades_tratadas.parquet
```

Descrição: base auxiliar de estabelecimentos de saúde utilizada para enriquecer os registros do SINAN com nomes das unidades notificadoras.

| Coluna | Tipo SQL | Descrição |
|---|---|---|
| `ID_UNIDADE` | VARCHAR | Identificador padronizado da unidade de saúde, compatível com o código de unidade presente no SINAN. |
| `NOME_UNIDADE` | VARCHAR | Nome da unidade de saúde utilizada para substituir/enriquecer o código da unidade notificadora no SINAN. |
| `CO_CNES` | VARCHAR | Código CNES do estabelecimento de saúde. |
| `CO_UNIDADE` | VARCHAR | Código da unidade conforme estrutura original do CNES. |
| `CO_UF` | VARCHAR | Código da Unidade Federativa do estabelecimento de saúde. |
| `CO_IBGE` | VARCHAR | Código IBGE do município do estabelecimento de saúde. |
| `TP_UNIDADE` | VARCHAR | Tipo de unidade de saúde, conforme classificação do CNES. |
| `NO_RAZAO_SOCIAL` | VARCHAR | Razão social do estabelecimento de saúde. |

---

## 5. Base `gold.sds_sinan`

Arquivo principal:

```text
data/gold/sds_sinan/sds_sinan_final.parquet
```

Descrição: tabela analítica final, construída por agregação e cruzamento entre SINAN e SDS. Como as bases não possuem chave individual comum, a integração é feita de forma agregada pelas chaves `MUNICIPIO`, `ANO`, `SEXO` e `FAIXA_ETARIA_SDS`.

| Coluna | Tipo | Descrição |
|---|---|---|
| `MUNICIPIO` | VARCHAR | Município utilizado como chave de integração entre SINAN e SDS. |
| `REGIAO_GEOGRAFICA` | VARCHAR | Região geográfica associada ao município, proveniente da SDS quando disponível. |
| `ANO` | BIGINT | Ano de referência da agregação. |
| `SEXO` | VARCHAR | Sexo da vítima no estrato agregado. |
| `FAIXA_ETARIA_SDS` | VARCHAR | Faixa etária harmonizada entre SINAN e SDS. |
| `TOTAL_REGISTROS_SINAN` | BIGINT | Total de notificações do SINAN no estrato agregado. |
| `TOTAL_REGISTROS_SDS` | BIGINT | Total de registros da SDS no estrato agregado. |
| `TOTAL_VITIMAS_SDS` | BIGINT | Total de vítimas registradas na SDS no estrato agregado. |
| `DIF_TOTAL_SDS_MENOS_SINAN` | BIGINT | Diferença entre `TOTAL_VITIMAS_SDS` e `TOTAL_REGISTROS_SINAN`. Valores positivos indicam maior volume na SDS; valores negativos indicam maior volume no SINAN. |
| `SINAN_VIOL_FISIC` | BIGINT | Total de registros de violência física no SINAN para o estrato agregado. |
| `SINAN_VIOL_PSICO` | BIGINT | Total de registros de violência psicológica/moral no SINAN para o estrato agregado. |
| `SINAN_VIOL_TORT` | BIGINT | Total de registros de tortura no SINAN para o estrato agregado. |
| `SINAN_VIOL_SEXU` | BIGINT | Total de registros de violência sexual no SINAN para o estrato agregado. |
| `SINAN_VIOL_TRAF` | BIGINT | Total de registros de tráfico de pessoas no SINAN para o estrato agregado. |
| `SINAN_VIOL_FINAN` | BIGINT | Total de registros de violência financeira/econômica no SINAN para o estrato agregado. |
| `SINAN_VIOL_NEGLI` | BIGINT | Total de registros de negligência/abandono no SINAN para o estrato agregado. |
| `SINAN_VIOL_INFAN` | BIGINT | Total de registros associados ao campo `VIOL_INFAN` no SINAN para o estrato agregado. |
| `SINAN_AG_FORCA` | BIGINT | Total de registros do SINAN com agressão por força corporal/espancamento no estrato. |
| `SINAN_AG_ENFOR` | BIGINT | Total de registros do SINAN com agressão por enforcamento no estrato. |
| `SINAN_AG_OBJETO` | BIGINT | Total de registros do SINAN com agressão por objeto contundente no estrato. |
| `SINAN_AG_CORTE` | BIGINT | Total de registros do SINAN com agressão por objeto cortante/perfurocortante no estrato. |
| `SINAN_AG_QUENTE` | BIGINT | Total de registros do SINAN com agressão por substância ou objeto quente no estrato. |
| `SINAN_AG_ENVEN` | BIGINT | Total de registros do SINAN com envenenamento/intoxicação no estrato. |
| `SINAN_AG_FOGO` | BIGINT | Total de registros do SINAN com agressão por arma de fogo no estrato. |
| `SINAN_AG_AMEACA` | BIGINT | Total de registros do SINAN com ameaça no estrato. |
| `SINAN_SEX_ASSEDI` | BIGINT | Total de registros do SINAN com assédio sexual no estrato. |
| `SINAN_SEX_ESTUPR` | BIGINT | Total de registros do SINAN com estupro no estrato. |
| `SINAN_SEX_PORNO` | BIGINT | Total de registros do SINAN com pornografia/exposição associada à violência sexual no estrato. |
| `SINAN_SEX_EXPLO` | BIGINT | Total de registros do SINAN com exploração sexual no estrato. |
| `SDS_VIOL_FISIC` | BIGINT | Total de registros compatíveis com violência física na SDS para o estrato agregado. |
| `SDS_VIOL_PSICO` | BIGINT | Total de registros compatíveis com violência psicológica/moral na SDS para o estrato agregado. |
| `SDS_VIOL_TORT` | BIGINT | Total de registros compatíveis com tortura na SDS para o estrato agregado. |
| `SDS_VIOL_SEXU` | BIGINT | Total de registros compatíveis com violência sexual na SDS para o estrato agregado. |
| `SDS_VIOL_TRAF` | BIGINT | Total de registros compatíveis com tráfico de pessoas na SDS para o estrato agregado. |
| `SDS_VIOL_FINAN` | BIGINT | Total de registros compatíveis com violência financeira/patrimonial na SDS para o estrato agregado. |
| `SDS_VIOL_NEGLI` | BIGINT | Total de registros compatíveis com negligência/abandono na SDS para o estrato agregado. |
| `SDS_VIOL_INFAN` | BIGINT | Total de registros compatíveis com o campo `VIOL_INFAN` na SDS para o estrato agregado. |
| `SDS_AG_FORCA` | BIGINT | Total de registros da SDS compatíveis com agressão por força corporal/espancamento no estrato. |
| `SDS_AG_ENFOR` | BIGINT | Total de registros da SDS compatíveis com enforcamento no estrato. |
| `SDS_AG_OBJETO` | BIGINT | Total de registros da SDS compatíveis com agressão por objeto contundente no estrato. |
| `SDS_AG_CORTE` | BIGINT | Total de registros da SDS compatíveis com agressão por objeto cortante/perfurocortante no estrato. |
| `SDS_AG_QUENTE` | BIGINT | Total de registros da SDS compatíveis com agressão por substância ou objeto quente no estrato. |
| `SDS_AG_ENVEN` | BIGINT | Total de registros da SDS compatíveis com envenenamento/intoxicação no estrato. |
| `SDS_AG_FOGO` | BIGINT | Total de registros da SDS compatíveis com arma de fogo no estrato. |
| `SDS_AG_AMEACA` | BIGINT | Total de registros da SDS compatíveis com ameaça no estrato. |
| `SDS_SEX_ASSEDI` | BIGINT | Total de registros da SDS compatíveis com assédio sexual no estrato. |
| `SDS_SEX_ESTUPR` | BIGINT | Total de registros da SDS compatíveis com estupro no estrato. |
| `SDS_SEX_PORNO` | BIGINT | Total de registros da SDS compatíveis com pornografia/exposição associada à violência sexual no estrato. |
| `SDS_SEX_EXPLO` | BIGINT | Total de registros da SDS compatíveis com exploração sexual no estrato. |

---

## 6. Observações metodológicas

### Integração entre SINAN e SDS

A integração entre SINAN e SDS é feita em nível agregado, pois as duas bases não possuem chave individual comum que permita identificar diretamente se uma ocorrência da SDS corresponde a uma notificação específica do SINAN.

As chaves de agregação utilizadas são:

```text
MUNICIPIO
ANO
SEXO
FAIXA_ETARIA_SDS
```

### Interpretação das diferenças entre as bases

Diferenças entre os totais da SDS e do SINAN devem ser interpretadas com cautela. As duas fontes possuem finalidades institucionais distintas:

- o SINAN registra notificações realizadas no âmbito da saúde;
- a SDS reúne registros administrativos e policiais.

Assim, discrepâncias entre os sistemas não indicam, isoladamente, erro em uma das bases. Elas devem ser lidas como evidências descritivas de diferenças de cobertura, fluxo de atendimento, critérios de registro e formas de captação da violência.

### Recorte doméstico/familiar

O campo `RECORTE_DOMESTICO_FAMILIAR` é uma classificação operacional criada no pipeline. Ele não substitui a definição jurídica completa de violência doméstica/familiar, mas aproxima registros compatíveis com esse fenômeno a partir de informações disponíveis no SINAN, especialmente:

- local de ocorrência residencial;
- vínculo familiar, afetivo ou de cuidado com o provável autor.

### Valores ausentes e ignorados

Durante o tratamento, valores vazios, inválidos, nulos ou sem utilidade analítica são padronizados como:

```text
DADO NÃO INFORMADO
```

Sempre que possível, categorias como `IGNORADO` e `NAO SE APLICA` são preservadas, pois representam respostas específicas presentes nos formulários originais.

---

## 7. Arquivos documentados

| Camada | Arquivo | Descrição |
|---|---|---|
| Silver | `data/silver/sinan/base_sinan_tratada.parquet` | Base tratada do SINAN. |
| Silver | `data/silver/sds/base_sds_tratada.parquet` | Base tratada da SDS. |
| Silver | `data/silver/ibge/municipios_tratado.parquet` | Base auxiliar tratada do IBGE. |
| Silver | `data/silver/cnes/unidades_tratadas.parquet` | Base auxiliar tratada do CNES. |
| Gold | `data/gold/sds_sinan/sds_sinan_final.parquet` | Base agregada integrada SINAN x SDS. |
| Warehouse | `data/warehouse/sinan_sds.duckdb` | Banco analítico local com as tabelas do projeto. |

---

## 8. Citação

Caso utilize este dataset, cite a versão publicada no Zenodo:

```text
ViolênciaDataPE: Dataset Integrado de Violência Doméstica/Familiar contra a Mulher em Pernambuco.
DOI: 10.5281/zenodo.21113070
```
