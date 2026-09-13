import os
import logging
from flask import Flask
from flask_cors import CORS

from db import Database
from chat_api import create_chat_api
from watson_service import WatsonAssistantService
from dotenv import load_dotenv

# ============================================
# CONFIGURATION TEMPLATE
# ============================================
TABLE_NAME = 'medicoes_pressao'
TABLE_SCHEMA = {
    'session_id': 'TEXT NOT NULL',
    'sistolica': 'INTEGER NOT NULL',
    'diastolica': 'INTEGER NOT NULL',
    'source': 'TEXT',
}
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 5000


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
    # Init database
    db = Database('cardioia.db')
    db.init_table(TABLE_NAME, TABLE_SCHEMA)
    print(f'[server] Table "{TABLE_NAME}" ready.')

    # Create Flask app + APIs
    app = Flask(__name__)
    CORS(app, resources={r'/api/*': {'origins': '*'}})
    watson = WatsonAssistantService()
    app.register_blueprint(create_chat_api(watson, db, TABLE_NAME))

    print(f'[server] API: http://localhost:{SERVER_PORT}/')
    app.run(host=SERVER_HOST, port=SERVER_PORT, debug=False)
