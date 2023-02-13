#!/usr/bin/python3

"""
Created on Fri May 13 12:59:22 2022
Changed on Tue Jul 19 16:30:00 2022

@author: r8sena@gmail.com
"""

import os
import boto3
import botocore
import logging
import datetime
from datetime import date
from decouple import Config, RepositoryEnv

""" parameters:
    - prefix: pattern to match in s3 bucket which depends on how object files are saved into bucket
    - mount_point: local path to folder where finding files for processing
    - bucket: s3 bucket with target contents
    - s3_client: initialized s3 client object
    - log_file: local path and filename to daily logs
    - shared_folder: a FSx shared folder endpoint
"""

def log(log_file):
    logging.basicConfig(filename="{}_{}.log".format(log_file, date.today()), level=logging.INFO)

def fsx(shared_folder, mount_point, mount_options, log_file):
    if os.path.exists(mount_point):
        mount_cmd = "sudo mount -t cifs {} {} --verbose -o {}".format(shared_folder, mount_point, mount_options)
        os.system(mount_cmd)
        exit()

# copy files from a FSx shared folder and send them to a s3 bucket folder
def send(shared_folder, mount_point, mount_options, log_file, bucket, s3_client):
    log(log_file)
    if os.path.exists(os.path.join(mount_point) + "/send"):
       for root, dirs, files in os.walk(os.path.join(mount_point) + "/send"):
          for f in files:
             file_name = os.path.join(root, f)
             object_name = "send/" + f
             try:
                s3_client.upload_file(file_name, bucket, object_name)
                logging.info("{} - Uploaded {} to s3://{}/{}".format(datetime.datetime.today(), file_name, bucket, object_name))
                print("{} - Uploaded {} to s3://{}/{}".format(datetime.datetime.today(), file_name, bucket, object_name))
                mv_cmd = "mv -v {} {}".format(os.path.join(root, f), os.path.join(mount_point) + "/backup")
                os.system(mv_cmd)
             except botocore.exceptions.ClientError as error:
                raise error
             except botocore.exceptions.ParamValidationError as error:
                raise ValueError('The parameters you provided are incorrect: {}'.format(error))
    else:
        print("{} - Directory {} not found.".format(datetime.datetime.today(), os.path.join(mount_point) + "/send"))
        fsx(shared_folder, mount_point, mount_options, log_file)

# copy invoice files from a s3 bucket folder and send them to a FSx shared folder
def receive_invoice(shared_folder, mount_point, mount_options, log_file, bucket, prefix_cob, s3_client):
    keys = []
    log(log_file)
    response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix_cob)
    contents = response.get('Contents')
    if contents is not None:
       for obj in response['Contents']:
           k = obj.get('Key')
           keys.append(k)
       for k in keys:
           dest_pathname = os.path.join(mount_point, k)
           try:
               s3_client.download_file(bucket, k, dest_pathname)
               logging.info("{} - Downloded s3://{}/{} to {}".format(datetime.datetime.today(), bucket, k, dest_pathname))
               print("{} - Downloded s3://{}/{} to {}".format(datetime.datetime.today(), bucket, k, dest_pathname))
               s3_client.delete_object(Bucket=bucket, Key=k)
               logging.info("{} - Removed s3://{}/{} file after downloading it".format(datetime.datetime.today(), bucket, k))
               print("{} - Removed s3://{}/{} file after downloading it".format(datetime.datetime.today(), bucket, k))
           except botocore.exceptions.ClientError as error:
               raise error
           except botocore.exceptions.ParamValidationError as error:
               raise ValueError('The parameters you provided are incorrect: {}'.format(error))
    else:
        print("{} - There's no file s3://{}/{} to download".format(datetime.datetime.today(), bucket, prefix_cob))
        logging.info("{} - There's no file s3://{}/{} to download".format(datetime.datetime.today(), bucket, prefix_cob))

# copy statement files from a s3 bucket folder and send them to a FSx shared folder
def receive_statement(shared_folder, mount_point, mount_options, log_file, bucket, prefix_ext, s3_client):
    keys = []
    log(log_file)
    response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix_ext)
    contents = response.get('Contents')
    if contents is not None:
       for obj in response['Contents']:
           k = obj.get('Key')
           keys.append(k)
       for k in keys:
           dest_filename = k.replace('receive', 'statement')
           dest_pathname = (os.path.join(mount_point) + "/receive/" + (dest_filename))
           try:
               s3_client.download_file(bucket, k, dest_pathname)
               logging.info("{} - Downloded s3://{}/{} to {}".format(datetime.datetime.today(), bucket, k, dest_pathname))
               print("{} - Downloded s3://{}/{} to {}".format(datetime.datetime.today(), bucket, k, dest_pathname))
               s3_client.delete_object(Bucket=bucket, Key=k)
               logging.info("{} - Removed s3://{}/{} file after downloading it".format(datetime.datetime.today(), bucket, k))
               print("{} - Removed s3://{}/{} file after downloading it".format(datetime.datetime.today(), bucket, k))
           except botocore.exceptions.ClientError as error:
               raise error
           except botocore.exceptions.ParamValidationError as error:
               raise ValueError('The parameters you provided are incorrect: {}'.format(error))
    else:
        print("{} - There's no file s3://{}/{} to download".format(datetime.datetime.today(), bucket, prefix_ext))
        logging.info("{} - There's no file s3://{}/{} to download".format(datetime.datetime.today(), bucket, prefix_ext))

def main():

    # define your authentication properties
    ENV_FILE = os.environ.get("ENV_FILE", "/opt/rundeck/squad/loan/.env")
    config = Config(RepositoryEnv(ENV_FILE))
    ACCESS_KEY = config('AWS_ACCESS_KEY_ID')
    SECRET_KEY = config('AWS_SECRET_ACCESS_KEY')
    SESSION_TOKEN = config('AWS_SESSION_TOKEN')
    session = boto3.Session(
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        aws_session_token=SESSION_TOKEN
    )
    s3_client = session.client('s3')

    # define your app properties
    shared_folder = config('ENDPOINT')
    mount_point = '/mnt/loan/debts'
    mount_options = config('OPTIONS')
    log_file = '/opt/rundeck/squad/loan/logs/Sync'
    bucket = 'test-bucket-payroll-loan'
    prefix_cob = "receive/ABC"
    prefix_ext = "receive/DEF"

    # call your main functions here
    send(shared_folder, mount_point, mount_options, log_file, bucket, s3_client)
    receive_invoice(shared_folder, mount_point, mount_options, log_file, bucket, prefix_cob, s3_client)
    receive_statement(shared_folder, mount_point, mount_options, log_file, bucket, prefix_ext, s3_client)

if __name__ == '__main__':
    main()