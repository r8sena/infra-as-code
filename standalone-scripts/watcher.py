#!/usr/bin/python3

"""
Created on Fri Feb 03 12:59:22 2023
Changed on Fri Feb 03 12:59:22 2023

@author: r8sena@gmail.com
"""

import os
import sys
import scp
import time
import shutil
import hashlib
import paramiko
from scp import SCPClient
from collections import defaultdict
from smb.SMBConnection import SMBConnection

""" parameters:
"""

def notify():
    None

# Define progress callback that prints the current percentage completed for the file
def progress(filename, size, sent):
    sys.stdout.write("%s\'s progress: %.2f%%   \r" % (filename, float(sent)/float(size)*100) )

def createSSHClient(scp_host, scp_user, secret_key):

    try:
        ssh_client = paramiko.SSHClient()
        rsa_key = paramiko.RSAKey.from_private_key_file(secret_key, password=None)

        ssh_client.load_system_host_keys()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=scp_host,
                    port=22,
                    username=scp_user,
                    password=None,
                    pkey=rsa_key,
                    timeout=30,
                    allow_agent=False,
                    look_for_keys=False
                    )
        return ssh_client
    except paramiko.ssh_exception.BadHostKeyException as error:
        sys.exit('The server host key could not be verified: {}'.format(error))
    except paramiko.ssh_exception.AuthenticationException as error:
        sys.exit('Authentication failed: {}'.format(error))
    except paramiko.ssh_exception.SSHException as error:
        sys.exit('There was any other error connecting or establishing an SSH session: {}'.format(error))
    except paramiko.ssh_exception.PasswordRequiredException as error:
        sys.exit('The private key file is encrypted, and password is None: {}'.format(error))
    except IOError as error:
        sys.exit('There was an error reading the key: {}'.format(error))

def connectFSx():
    None

# copy files from a linux environment and send them to an aws FSx shared folder with md5 hash checking
def fileWatcher(scp_host, scp_user, secret_key, prefix, source_path, fsx_endpoint, fsx_share, fsx_folder_in, fsx_backup_folder):
    files = []
    md5 = defaultdict(list)
    find = "find {} -type f -iname {} -printf '%f\n'".format(source_path, prefix + "*.txt")
    ssh = createSSHClient(scp_host, scp_user, secret_key)
    stdin, stdout, stderr = ssh.exec_command(find)
    output = stdout.read().decode().strip()
    error = stderr.read().decode().strip()
    if output is not None:
        print("Found the following files to receive and copy: \n{}".format(output))
        files = list(output.split("\n"))
        for filename in files:
            time.sleep(10)
            check_hash_md5 = "md5sum {}{}".format(source_path, filename)
            stdin, stdout, stderr = ssh.exec_command(check_hash_md5)
            output = stdout.read().decode().strip()
            digest = list(output.split(" "))
            md5[filename].append(digest[0])
            scp_client = SCPClient(ssh.get_transport(), progress = progress)
            try:
                source = source_path + filename
                destination_path = fsx_share + fsx_folder_in
                scp_client.get(source, local_path=destination_path)
                scp_client.close()
            except scp.SCPException as error:
                sys.exit('No such file or directory: \n{}'.format(error))
    else:
        print("\nThere were not files to receive or copy at this moment: {} {}".format(output, error))
        #call function to send mail or teams notification
    time.sleep(5)
    for key, value in md5.items():
        filename = fsx_share + fsx_folder_in + key
        backup_filename = fsx_share + fsx_backup_folder + key
        print("\nThe md5 message digest for {} in source was {}".format(key, value[-1]))
        with open(filename, 'rb') as file_to_check:
            data = file_to_check.read()
            md5_returned = hashlib.md5(data).hexdigest()
            if md5_returned == value[-1]:
                print("MD5 checksum returned from {} is equal to {}".format(file_to_check, value[-1]))
                shutil.copyfile(filename, backup_filename)
                remove_source_file = "rm -fv {}{}".format(source_path, key)
                stdin, stdout, stderr = ssh.exec_command(remove_source_file)
                print("Source file {}{} in Connect Direct has been deleted after backup it.".format(source_path, key))
                output = stdout.read().decode().strip()
                print(output)
            else:
                print("MD5 checksum returned from {} is not equal to {}.".format(file_to_check, value[-1]))
                os.remove(file_to_check)
                print("File {} removed. We will try to copy it later.".format(file_to_check))
    ssh.close()

def main():

    # define your app properties
    scp_host = "kotlin-payroll-loan-service.local.dev.infra"
    source_path = "/home/file-watcher/banking/"
    fsx_endpoint = "amznfsxtestendpoint.local.corp"
    fsx_share = "/FILES/"
    fsx_folder_in = "source/"
    fsx_backup_folder = "backup/"
    scp_user = os.getenv('RD_FILE_WATCHER_USER')
    secret_key = os.getenv('RD_SCP_SECRET_KEY')
    prefix = "payroll-loan_test_file-"

    # call your main functions here
    fileWatcher(scp_host, 
                scp_user, 
                secret_key, 
                prefix, 
                source_path, 
                fsx_endpoint, 
                fsx_share, 
                fsx_folder_in, 
                fsx_backup_folder)

if __name__ == '__main__':
    main()