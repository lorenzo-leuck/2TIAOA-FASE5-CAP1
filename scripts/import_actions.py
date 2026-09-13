#!/usr/bin/env python3
"""Import the CardioIA Actions workspace through the documented V2 API."""

import json
import os
import sys

from dotenv import load_dotenv
from ibm_cloud_sdk_core.authenticators import BasicAuthenticator, IAMAuthenticator
from ibm_watson import AssistantV2


def required(name):
    value = os.getenv(name)
    if not value:
        print(f'Erro: {name} não está configurado no .env.', file=sys.stderr)
        sys.exit(1)
    return value


def main():
    root = os.path.dirname(os.path.dirname(__file__))
    load_dotenv(os.path.join(root, '.env'))
    api_key = os.getenv('ASSISTANT_IAM_APIKEY') or required('ASSISTANT_APIKEY')
    assistant_id = required('ASSISTANT_ID')
    skill_id = required('ASSISTANT_ACTION_SKILL_ID')
    service_url = required('ASSISTANT_URL')

    if os.getenv('ASSISTANT_AUTH_TYPE', 'iam').lower() == 'basic':
        authenticator = BasicAuthenticator(required('ASSISTANT_USERNAME'), api_key)
    else:
        authenticator = IAMAuthenticator(api_key)

    with open(os.path.join(root, 'config', 'actions.json'), encoding='utf-8') as file:
        workspace = json.load(file)['workspace']
    for action in workspace.get('actions', []):
        action.setdefault('type', 'standard')
        action.setdefault('variables', [])
        known_variables = {item.get('variable') for item in action['variables']}
        for step in action.get('steps', []):
            step.setdefault('type', 'standard')
            variable = step.get('variable')
            if variable and variable not in known_variables:
                action['variables'].append({
                    'variable': variable,
                    'data_type': 'any',
                })
                known_variables.add(variable)

    assistant = AssistantV2(version='2021-11-27', authenticator=authenticator)
    assistant.set_service_url(service_url)
    result = assistant.update_skill(
        assistant_id=assistant_id,
        skill_id=skill_id,
        workspace=workspace,
    ).get_result()
    print(f"Importação enviada. Status: {result.get('status', 'processing')}")


if __name__ == '__main__':
    main()
