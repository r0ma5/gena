import boto3
import logging
import argparse
import xml.etree.ElementTree as ET

logger = logging.getLogger()

# arn:aws:iam::088199345311:role/SandboxServiceRole
# anthropic.claude-v2
# anthropic.claude-v2:1
# anthropic.claude-3-sonnet-20240229-v1:0
# anthropic.claude-3-haiku-20240307-v1:0


def start_bold(text):
    return '\033[1m{t}'.format(t=text)


def stop_bold(text):
    return '{t}\033[0m'.format(t=text)


br_client = boto3.client('bedrock-agent-runtime')

if __name__ == '__main__':

    parser = argparse.ArgumentParser('Augment pom.xml with Gen AI')
    parser.add_argument('pomfile', default='pom.xml', help='pom file to augment')
    parser.add_argument('--prompt', default='prompt.txt', help='model prompt file')
    parser.add_argument('--kbid', default='QJH6PFQD9K', help='knowledge base ID from the AWS account')
    parser.add_argument('--model', default='anthropic.claude-v2:1', help='model to call')
    parser.add_argument('--numberOfResults', default=5, type=int, help='number of results from KB')
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
#            print(ET.tostring(pom_dependencies).decode('utf-8'))
        except Exception as e:
            logger.error(e)
            raise e
    for d in pom_dependencies.findall('dependency'):
        print('---')
        ET.indent(d)
        input = "Evaluate vulnerability for the following dependency:\n {d}\n replace version with the safer alternative if found.".format(d=ET.tostring(d).decode('utf-8').strip())
        print(input)
        print('---')

        response = br_client.retrieve_and_generate(
            input={
                'text': input
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
        print(response.get('output').get('text')
              .replace('<dependency>', start_bold('<dependency>'))
              .replace('</dependency>', stop_bold('</dependency>')))



