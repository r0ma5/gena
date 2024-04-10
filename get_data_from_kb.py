import boto3
import logging

logger = logging.getLogger()

# arn:aws:iam::088199345311:role/SandboxServiceRole
sts_client = boto3.client('sts')

try:
    response = sts_client.assume_role(
        RoleArn='arn:aws:iam::088199345311:role/SandboxServiceRole',
        RoleSessionName='br-session'
    )
except Exception as e:
    logger.error(e)
    raise e

br_client = boto3.client('bedrock-agent-runtime')

response = br_client.retrieve(
    knowledgeBaseId='5JDOP0XO5B',
    retrievalConfiguration={
        'vectorSearchConfiguration': {
            'numberOfResults': 50
#            'overrideSearchType': 'HYBRID'
        }
    },
    retrievalQuery={
        'text': 'htmlunit 3.8.0'
    }
)

print(response)
