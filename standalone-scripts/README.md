fsx-to-s3.py
fsx-to-s3-again.py
s3-to-fsx.py
============

Modulo para sincronizar arquivos entre shared folders AWS FSx e AWS buckets S3.

Requirements
------------

Python 3 e libs boto3, botocore, logging, datetime e decouple.
Instalacao do pacote cifs-utils no Amazon Linux 2.
Configuracao de .secrets necessarias ao mount point cifs.

Variables
--------------

    - bucket: nome do bucket na AWS.
    - prefix: string para prefixo dentro do bucket, pode ser uma pasta ou uma pasta mais inicio de nome de um arquivo.
    - s3_client: inicializacao do objeto s3 client.
    - session: criacao da sessao do s3 client autenticando via profile_name.
    - shared_folder: endpoint FSx mais nome da pasta compartilhada. Ex.: \\FSx_DNS_name\shared_folder
    - mount_point: path local para montagem da shared folder FSx no Amazon Linux 2.
    - mount_options: parametros para o ponto de montagem.
    - log_file: path local e nome do arquivo para logs do script.


Dependencies
------------

Python3 libs boto3, botocore, logging, datetime e decouple.
Lib cifs-utils em Amazon Linux 2.

How to use
----------

    - Criar um diretorio e salvar o consigSync.py no mesmo. Ex.: /opt/rundeck/squad/payroll-loan/fsx-to-s3.py
    - Utilizar auth.sh no mesmo diretorio do consigSync.py para obter credenciais AWS.
    - Utilizar API Vault para criar o arquivo .env com as variaveis e secrets necessarias.
    - Criar o schedule para executar o script.
