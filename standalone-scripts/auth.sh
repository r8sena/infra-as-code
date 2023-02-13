#!/bin/bash

ROLE_ARN=arn:aws:iam::999999999999:role/CrossOrgTest
ENV_REGION=sa-east-1
export AWS_DEFAULT_REGION=sa-east-1
credentials=$(aws sts assume-role --role-arn $ROLE_ARN --role-session-name test --region $ENV_REGION)

cat << EOF > /opt/test/squad/app/.env
ENDPOINT = '//fsx-endpoint-url/ARQUIVOS'
OPTIONS = 'uid=test,gid=test,credentials=/opt/test/squad/app/.secret'
AWS_SECRET_ACCESS_KEY = '$(echo $credentials | awk -F 'SecretAccessKey' '{print $2}' | awk '{print $2}' | tr -d ' ,"')'
AWS_SESSION_TOKEN = '$(echo $credentials | awk -F 'SessionToken' '{print $2}' | awk '{print $2}' | tr -d ' ,"')'
AWS_ACCESS_KEY_ID = '$(echo $credentials | awk -F 'AccessKeyId' '{print $2}' | awk '{print $2}' | tr -d ' ,"')'
EOF