from flask import Flask
from flask_cors import CORS
import os
from logging.handlers import RotatingFileHandler
import logging

from routes import register_routes
from utils import load_model

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
MODEL_PATH = 'forest_model_complete.pkl'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def setup_logging():
    logging.basicConfig(level=logging.INFO)
    handler = RotatingFileHandler('api.log', maxBytes=10000000, backupCount=3)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)

def create_app():
    setup_logging()
    load_model(MODEL_PATH, app.logger)
    register_routes(app)
    
    @app.errorhandler(413)
    def too_large(e):
        return {'success': False, 'message': 'File too large (max 50MB)'}, 413

    @app.errorhandler(500)
    def internal_error(e):
        app.logger.error(f"Internal error: {str(e)}")
        return {'success': False, 'message': 'Internal server error'}, 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=False, host='0.0.0.0', port=5001)