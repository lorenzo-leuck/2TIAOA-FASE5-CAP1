import os

from ibm_cloud_sdk_core.authenticators import BasicAuthenticator, IAMAuthenticator
from ibm_watson import AssistantV2


class WatsonAssistantService:
    """Small adapter around the Watson Assistant V2 runtime API."""

    def __init__(self):
        auth_type = os.getenv('ASSISTANT_AUTH_TYPE', 'iam').lower()
        api_key = os.getenv('ASSISTANT_IAM_APIKEY') or os.getenv('ASSISTANT_APIKEY')
        service_url = os.getenv('ASSISTANT_URL')
        self.assistant_id = (
            os.getenv('ASSISTANT_ID')
            or os.getenv('ASSISTANT_ASSISTANT_ID')
            or os.getenv('WATSON_ASSISTANT_ID')
        )
        self.environment_id = (
            os.getenv('ASSISTANT_ENVIRONMENT_ID')
            or os.getenv('ASSISTANT_DRAFT_ENVIRONMENT_ID')
            or 'draft'
        )
        if not api_key or not service_url or not self.assistant_id:
            raise RuntimeError(
                'Configure ASSISTANT_IAM_APIKEY (ou ASSISTANT_APIKEY), '
                'ASSISTANT_URL e ASSISTANT_ID no .env.'
            )

        if auth_type == 'basic':
            username = os.getenv('ASSISTANT_USERNAME')
            if not username:
                raise RuntimeError('ASSISTANT_USERNAME é obrigatório para autenticação basic.')
            authenticator = BasicAuthenticator(username, api_key)
        else:
            authenticator = IAMAuthenticator(api_key)

        self.client = AssistantV2(version='2021-06-14', authenticator=authenticator)
        self.client.set_service_url(service_url)
        self.client.set_http_config({'timeout': 120})

    def create_session(self):
        response = self.client.create_session(
            assistant_id=self.assistant_id,
            environment_id=self.environment_id,
        ).get_result()
        return response['session_id']

    def send_message(self, session_id, message):
        return self.client.message(
            assistant_id=self.assistant_id,
            environment_id=self.environment_id,
            session_id=session_id,
            user_id=f'cardioia-{session_id}',
            input={
                'message_type': 'text',
                'text': message,
            },
        ).get_result()

    @staticmethod
    def text_from_response(response):
        generic = response.get('output', {}).get('generic', [])
        generic_text = '\n'.join(
            item.get('text', '') for item in generic if item.get('response_type') == 'text'
        ).strip()
        if generic_text:
            return generic_text
        return '\n'.join(response.get('output', {}).get('text', [])).strip()
