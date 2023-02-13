#!/usr/bin/python3

"""
Created on Sat Nov 13 12:59:22 2021
Changed on Mon Apr 29 13:38:00 2022

@author: r8sena@gmail.com
"""
import os
import logging
import datetime
import paramiko
from datetime import date
from decouple import config

""" parameters:
"""

def log(log_file):
    clean_logs = "rm -rfv {}_*".format(log_file)
    os.system(clean_logs)
    logging.basicConfig(filename="{}_{}.log".format(log_file, date.today()), level=logging.INFO)

def sftp(sftp_host, sftp_username, sftp_password, sftp_port, sftp_file, abr_temp_dir, log_file):
    log(log_file)
    if os.path.exists(abr_temp_dir):
        clean_files = "rm -rfv {}/*".format(abr_temp_dir)
        os.system(clean_files)
        mkdir_cmd = "mkdir -p {}{}".format(abr_temp_dir, date.today())
        logging.info("{} - Creating temp dir {}{}".format(datetime.datetime.today(), abr_temp_dir, date.today()))
        os.system(mkdir_cmd)
        transport = paramiko.Transport((sftp_host,sftp_port))
        transport.connect(None,sftp_username,sftp_password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        remote_path = 'saida/' + sftp_file + '.enc.zip'
        local_path = "{}{}/{}.enc.zip".format(abr_temp_dir, date.today(), sftp_file)
        logging.info("{} - Downloading {} to {}".format(datetime.datetime.today(), remote_path, local_path))
        sftp.get(remote_path, local_path)
        sftp.close()
        transport.close()

def decrypt(abr_temp_dir, sftp_file, log_file, bundle_key, decrypted_key):
    log(log_file)
    if os.path.exists(abr_temp_dir):
        extract_dir = "{}{}".format(abr_temp_dir, date.today())
        unzip_bundle = "unzip {}/{}.enc.zip -d {}".format(extract_dir, sftp_file, extract_dir)
        decrypt_random_key = "openssl rsautl -decrypt -inkey {} -in {}/{}.random.key -out {}/{}".format(bundle_key, extract_dir, sftp_file, extract_dir, decrypted_key)
        decrypt_csv_file = "openssl enc -d -aes-256-cbc -in {}/{}.enc -out {}/{}.zip -pass file:{}/{}".format(extract_dir, sftp_file, extract_dir, sftp_file, extract_dir, decrypted_key)
        unzip_csv = "unzip {}/{}.zip -d {}".format(extract_dir, sftp_file, extract_dir)
        os.system(unzip_bundle)
        os.system(decrypt_random_key)
        os.system(decrypt_csv_file)
        os.system(unzip_csv)

def main():

    # define your environment and global variables here
    sftp_host = config('SFTP_HOST')
    sftp_username = config('SFTP_USERNAME')
    sftp_password = config('SFTP_PASSWORD')
    sftp_port = 22
    sftp_file = 'list2_payroll-loan.csv'
    decrypted_key = 'list2_decrypted_random.key'
    abr_temp_dir = config('TELCO_FILES')
    log_file = '/opt/rundeck/payroll-loan/do_not_call-me/logs/SFTP'
    bundle_key = config('BUNDLE_KEY')

    # call your main functions here
    sftp(sftp_host, sftp_username, sftp_password, sftp_port, sftp_file, abr_temp_dir, log_file)
    decrypt(abr_temp_dir, sftp_file, log_file, bundle_key, decrypted_key)

if __name__ == '__main__':
    main()