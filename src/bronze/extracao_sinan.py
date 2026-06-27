import os
from ftplib import FTP


def extrair_dados_sinan():
    """
    Ingestão da Camada Bronze: Conecta via FTP anônimo ao DATASUS,
    busca os arquivos de violência e salva localmente.
    """
    ftp_host = "ftp.datasus.gov.br"
    ftp_usuario = "anonymous"
    ftp_senha = ""
    pasta_remota = "/dissemin/publicos/SINAN/DADOS/FINAIS/"

    # Destino exato na sua nova arquitetura de pastas
    pasta_destino_local = "data/bronze/sinan/dbc"
    os.makedirs(pasta_destino_local, exist_ok=True)

    # Otimização: Gera a lista exata dos arquivos necessários (2014 a 2024)
    # Isso evita travar o script processando milhares de arquivos não relacionados.
    anos = range(14, 25)
    arquivos_alvo = [f"VIOLBR{ano}.dbc" for ano in anos]

    print("Iniciando conexão com o servidor FTP do DATASUS...")

    try:
        with FTP(ftp_host) as ftp:
            ftp.login(user=ftp_usuario, passwd=ftp_senha)
            ftp.cwd(pasta_remota)
            print(f"Diretório acessado: {pasta_remota}")

            # Lista o que existe no servidor para validação
            arquivos_no_servidor = ftp.nlst()

            for arquivo in arquivos_alvo:
                if arquivo in arquivos_no_servidor:
                    caminho_local = os.path.join(pasta_destino_local, arquivo)

                    # Idempotência: só baixa se não existir na pasta local
                    if not os.path.exists(caminho_local):
                        print(f"Baixando {arquivo} para {caminho_local}...")
                        with open(caminho_local, "wb") as f_local:
                            ftp.retrbinary(f"RETR {arquivo}", f_local.write)
                    else:
                        print(f"Arquivo {arquivo} já existe na Bronze. Download ignorado.")
                else:
                    print(f"AVISO: {arquivo} não encontrado no servidor FTP do DATASUS.")

        print("Extração da camada Bronze do SINAN finalizada com sucesso!")

    except Exception as e:
        print(f"Erro crítico durante a extração FTP: {e}")
        raise


if __name__ == "__main__":
    extrair_dados_sinan()
