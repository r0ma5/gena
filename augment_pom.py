import boto3
import logging
import argparse
import xml.etree.ElementTree as ET

logger = logging.getLogger()

# arn:aws:iam::088199345311:role/SandboxServiceRole

br_client = boto3.client('bedrock-agent-runtime')

if __name__ == '__main__':

    parser = argparse.ArgumentParser('Augment pom.xml with Gen AI')
    parser.add_argument('pomfile', default='pom.xml', help='pom file to augment')
    parser.add_argument('--prompt', default='prompt.txt', help='model prompt file')
    parser.add_argument('--kbid', default='2AEDVV6ZHM', help='knowledge base ID from the AWS account')
    parser.add_argument('--model', default='anthropic.claude-v2:1', help='model to call')
    parser.add_argument('--numberOfResults', default=20, type=int, help='model to call')
    args = parser.parse_args()

    if args.prompt:
        try:
            with open(args.prompt, 'r') as prompt_file:
                prompt = prompt_file.read()
        except Exception as e:
            logger.error(e)
            raise e
    if args.pomfile:
        try:
            pomTree = ET.parse(args.pomfile).getroot()
#            for e in pomTree:
#                print(e)
            ns = {'huh': "http://maven.apache.org/POM/4.0.0"}
#            ET.register_namespace('huh', 'http://maven.apache.org/POM/4.0.0')
            pom_dependencies = pomTree.find('dependencies')
            if not pom_dependencies:
                logger.warning('No dependencies found in pom, exiting');
                exit(1)
            print(ET.tostring(pom_dependencies).decode('utf-8'))
        except Exception as e:
            logger.error(e)
            raise e

    response = br_client.retrieve_and_generate(
        input={
            'text': str(ET.tostring(pom_dependencies))
        },
        retrieveAndGenerateConfiguration={
           'type': 'KNOWLEDGE_BASE',
           'knowledgeBaseConfiguration': {
                'knowledgeBaseId': args.kbid,
                'modelArn': 'arn:aws:bedrock:us-east-1::foundation-model/{m}'.format(m=args.model),
                'generationConfiguration': {
                    'promptTemplate': {
                     'textPromptTemplate': prompt
                    }
                },
                'retrievalConfiguration': {
                    'vectorSearchConfiguration': {
                     'numberOfResults': args.numberOfResults
                    }
                }
            }
        }
    )

    print(response)


