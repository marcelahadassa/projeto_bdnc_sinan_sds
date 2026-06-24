# %%
import pandas as pd
from dbfread import DBF
import glob

# %%
# configurações de exibição 
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

# %%
# Caminho padrão para os arquivos .dbf (padrão do DataSUS)
caminho_padrao = '../data/raw/dbf_files/VIOLBR*.dbf'
arquivos_dbf = glob.glob(caminho_padrao)

# ordena a lista para ele processar do menor ano para o maior (ex: 14, 15... 24)
arquivos_dbf.sort()

print(f"Foram encontrados {len(arquivos_dbf)} arquivos .dbf para conversão.\n")

# %%
# loop para cada arquivo .dbf encontrado, convertendo para .csv
for arquivo_dbf in arquivos_dbf:
    
    # cria o nome do arquivo de saída apenas trocando a extensão de .dbf para .csv
    arquivo_csv = arquivo_dbf.replace('.dbf', '.csv')
    
    print(f"Lendo e convertendo: {arquivo_dbf}...")
    
    # leitura do arquivo .dbf 
    # (iso-8859-1 é praticamente igual ao latin1, mas é o formato oficial do DataSUS)
    tabela = DBF(arquivo_dbf, encoding='iso-8859-1')
    df = pd.DataFrame(iter(tabela))
    
    # um novo arquivo csv é gerado e salvo
    df.to_csv(arquivo_csv, index=False)
    print(f"Salvo como: {arquivo_csv}\n")

print("Conversão feita.")
# %%