#!/usr/bin/python3

"""
Created on Fri May 13 12:59:22 2022
Changed on Wed Ago 03 23:03:00 2022

@author: r8sena@gmail.com
"""

import os
import sys
import time
import datetime
from decouple import Config, RepositoryEnv

""" parameters:
    - request_url: service endpoint for https requests
    - token: a service shared secret
    - method: base path or uri to request
    - file_path: path to a text or csv file to read as input
"""

def inserir_base_positiva(request_url, token, file_path, output):
    curl_cmd = "/usr/bin/curl -ki --location --request POST '{}/eligibility/allow' \
            --header 'Authorization: {}' --form 'file=@{}' > {}".format(request_url, token, file_path, output)
    os.system(curl_cmd)
    time.sleep(10)
    try:
        with open(output, 'r') as file:
            line = file.readlines()[0]
            print(line)
            http_code = line.split()[1]
            if http_code == '201':
                print("{} - Carga de base positiva realizada com sucesso - HTTP response code 201.".format(datetime.datetime.today()))
            elif http_code == '200':
                print("{} - Carga de base positiva realizada com sucesso - HTTP response code 200.".format(datetime.datetime.today()))
            else:
                print("{} - A carga de base positiva falhou.".format(datetime.datetime.today()))
                sys.exit("HTTP response code", http_code)
    except FileNotFoundError as file_not_found:
        print("{} - {}".format(datetime.datetime.today(), file_not_found))
        print("{} - File {} not found.".format(datetime.datetime.today(), file_path))
    except PermissionError as permission:
        print("{} - {}".format(datetime.datetime.today(), permission))

def inserir_base_negativa(request_url, token, file_path, output):
    curl_cmd = "/usr/bin/curl -ki --location --request POST '{}/eligibility/deny' \
            --header 'Authorization: {}' --form 'file=@{}' > {}".format(request_url, token, file_path, output)
    os.system(curl_cmd)
    time.sleep(10)
    try:
        with open(output, 'r') as file:
            line = file.readlines()[0]
            print(line)
            http_code = line.split()[1]
            if http_code == '201':
                print("{} - Carga de base negativa realizada com sucesso - HTTP response code 201.".format(datetime.datetime.today()))
            elif http_code == '200':
                print("{} - Carga de base negativa realizada com sucesso - HTTP response code 200.".format(datetime.datetime.today()))
            else:
                print("{} - A carga de base negativa falhou.".format(datetime.datetime.today()))
                sys.exit("HTTP response code", http_code)
    except FileNotFoundError as file_not_found:
        print("{} - {}".format(datetime.datetime.today(), file_not_found))
        print("{} - File {} not found.".format(datetime.datetime.today(), file_path))
    except PermissionError as permission:
        print("{} - {}".format(datetime.datetime.today(), permission))

def main():

    # define your app properties here
    ENV_FILE = os.environ.get("ENV_FILE", "/opt/rundeck/squad/app/.env")
    config = Config(RepositoryEnv(ENV_FILE))
    request_url = config('ENDPOINT')
    token = config('SERVICE_SHARED_SECRET')
    method = os.getenv('RD_OPTION_STATUS')
    file_path = os.getenv('RD_FILE_ARQ')
    output = '/opt/rundeck/squad/app/output.txt'

    try:
        with open(file_path, 'r') as file:
            file.read()
    except FileNotFoundError as file_not_found:
        print("{} - {}".format(datetime.datetime.today(), file_not_found))
        print("{} - File {} not found.".format(datetime.datetime.today(), file_path))
    except PermissionError as permission:
        print("{} - {}".format(datetime.datetime.today(), permission))
    except TypeError as type_error:
        sys.exit(type_error, "Escolha um arquivo CSV válido para realizar a carga.")
    else:

        # call your functions here
        if method == 'ALLOW':
            print("{} - Opção escolhida: ALLOW. Liberando elegíveis.".format(datetime.datetime.today()))
            inserir_base_positiva(request_url, token, file_path, output)
        elif method == 'DENY':
            print("{} - Opção escolhida: DENY. Bloqueando elegíveis.".format(datetime.datetime.today()))
            inserir_base_negativa(request_url, token, file_path, output)
        elif method == 'NONE':
            print("{} - Selecione uma opção de carga válida:".format(datetime.datetime.today()))
            sys.exit("ALLOW para inserir BASE POSITIVA ou DENY para BASE NEGATIVA de clientes.")
        else:
            sys.exit("Method or URI not found.")

if __name__ == '__main__':
    main()