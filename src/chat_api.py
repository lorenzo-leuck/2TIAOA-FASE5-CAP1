import re
import logging

from flask import Blueprint, jsonify, request

logger = logging.getLogger(__name__)


def parse_pressure(message):
    match = re.search(r'\b(\d{2,3})\s*(?:por|/|x)\s*(\d{2,3})\b', message.lower())
    if not match:
        return None
    return int(match.group(1)), int(match.group(2))


def first_intent(response):
    intents = response.get('intents', response.get('output', {}).get('intents', []))
    if not intents:
        return '', 0
    return intents[0].get('intent', ''), intents[0].get('confidence', 0)


def history_text(rows):
    if not rows:
        return 'Ainda não há medições registradas nesta sessão.'
    measurements = [
        f"{row['sistolica']} por {row['diastolica']} mmHg ({row['timestamp']})"
        for row in rows
    ]
    return 'Medições registradas nesta sessão:\n' + '\n'.join(f'- {item}' for item in measurements)


def pressure_interpretation(systolic, diastolic):
    if systolic < 90 or diastolic < 60:
        classification = 'abaixo do esperado'
        guidance = 'Se esse valor se repetir ou vier acompanhado de tontura, desmaio ou fraqueza, procure orientação profissional.'
    elif systolic >= 140 or diastolic >= 90:
        classification = 'elevada'
        guidance = 'Repita a medição em repouso e procure orientação profissional se os valores continuarem elevados.'
    else:
        classification = 'dentro de uma faixa geralmente adequada'
        guidance = 'Continue acompanhando as medições em repouso e registre os resultados.'
    return classification, guidance


def create_chat_api(watson, db, table_name):
    bp = Blueprint('chat', __name__, url_prefix='/api')

    @bp.post('/session')
    def create_session():
        try:
            return jsonify({'session_id': watson.create_session()}), 201
        except Exception:
            logger.exception('Falha ao criar sessão no Watson Assistant')
            return jsonify({'error': 'Não foi possível iniciar a sessão do assistente.'}), 503

    @bp.post('/chat')
    def chat():
        data = request.get_json(silent=True) or {}
        message = data.get('message', '').strip()
        session_id = data.get('session_id')

        if not message:
            return jsonify({'error': 'A mensagem é obrigatória.'}), 400
        if len(message) > 500:
            return jsonify({'error': 'A mensagem deve ter no máximo 500 caracteres.'}), 400
        if not session_id:
            return jsonify({'error': 'session_id é obrigatório.'}), 400

        try:
            response = watson.send_message(session_id, message)
            text = watson.text_from_response(response)
            intent, confidence = first_intent(response)
            if confidence < 0.70:
                intent = ''
                text = ''
            result = {
                'response': text,
                'session_id': session_id,
                'intents': response.get('intents', response.get('output', {}).get('intents', [])),
                'entities': response.get('entities', response.get('output', {}).get('entities', [])),
            }

            pressure = parse_pressure(message)
            if pressure:
                systolic, diastolic = pressure
                if 60 <= systolic <= 300 and 40 <= diastolic <= 250 and systolic > diastolic:
                    result['measurement_id'] = db.insert(table_name, {
                        'session_id': session_id[:100],
                        'sistolica': systolic,
                        'diastolica': diastolic,
                        'source': 'watson-chat',
                    })
                    classification, guidance = pressure_interpretation(systolic, diastolic)
                    result['response'] = (
                        f'Sua pressão foi de {systolic} por {diastolic} mmHg. '
                        f'Esse valor está {classification} para muitos adultos em repouso. '
                        f'{guidance} Uma única medição não confirma um diagnóstico.'
                    )
                else:
                    result['response'] = 'Os valores parecem inconsistentes. Informe a sistólica por diastólica, por exemplo: 120 por 80.'
            elif re.search(r'\b(press[aã]o|medir|medição|medicao)\b', message.lower()) and re.search(r'\b\d{2,3}\b', message):
                result['response'] = 'Recebi apenas um valor. Informe a pressão completa no formato sistólica por diastólica, por exemplo: 120 por 80.'

            if not result['response']:
                if intent == 'cardioia_orientacao_intent':
                    result['response'] = (
                        'Pressão alta é quando a pressão do sangue nas artérias permanece elevada. '
                        'Uma única medição não confirma um diagnóstico; procure orientação de um profissional de saúde.'
                    )
                elif intent == 'cardioia_historico_intent':
                    result['response'] = history_text(db.fetch_where(table_name, 'session_id = ?', [session_id]))
                elif intent == 'cardioia_registrar_medicao_intent':
                    result['response'] = 'Informe a pressão completa no formato sistólica por diastólica, por exemplo: 120 por 80.'
                elif intent == 'cardioia_urgencia_intent':
                    result['response'] = 'Se os sintomas forem intensos ou persistentes, procure atendimento de emergência imediatamente. Não espere uma resposta do chatbot.'
                else:
                    result['response'] = 'Posso ajudar a registrar uma medição, consultar o histórico ou explicar o acompanhamento da pressão. Tente reformular sua mensagem.'
            return jsonify(result)
        except Exception as exc:
            logger.exception('Falha ao enviar mensagem ao Watson Assistant')
            return jsonify({
                'error': 'O assistente está temporariamente indisponível.',
                'details': str(exc),
            }), 503

    @bp.post('/measurements')
    def insert_measurement():
        data = request.get_json(silent=True) or {}
        session_id = data.get('session_id')
        try:
            systolic = int(data['systolic'])
            diastolic = int(data['diastolic'])
        except (KeyError, TypeError, ValueError):
            return jsonify({'error': 'Informe valores numéricos para sistólica e diastólica.'}), 400

        if not session_id or not 40 <= diastolic <= 250 or not 60 <= systolic <= 300:
            return jsonify({'error': 'Valores de pressão fora dos limites aceitos.'}), 400
        if diastolic >= systolic:
            return jsonify({'error': 'A sistólica deve ser maior que a diastólica.'}), 400

        row_id = db.insert(table_name, {
            'session_id': session_id[:100],
            'sistolica': systolic,
            'diastolica': diastolic,
            'source': 'react-native',
        })
        return jsonify({'id': row_id, 'message': 'Medição registrada.'}), 201

    @bp.get('/measurements')
    def get_measurements():
        session_id = request.args.get('session_id', '')
        if not session_id:
            return jsonify({'error': 'session_id é obrigatório.'}), 400
        rows = db.fetch_where(table_name, 'session_id = ?', [session_id])
        return jsonify(rows), 200

    return bp
