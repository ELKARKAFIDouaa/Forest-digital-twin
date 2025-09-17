from flask import Flask
from flask_cors import CORS
import os
from logging.handlers import RotatingFileHandler
import logging

from routes import register_routes
from utils import load_model

app = Flask(__name__)
CORS(app)

# Utiliser des chemins relatifs au script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
MODEL_PATH = os.path.join(BASE_DIR, 'forest_model_complete.pkl')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
app.config['BASE_DIR'] = BASE_DIR  # Ajouter BASE_DIR à la config

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def setup_logging():
    logging.basicConfig(level=logging.INFO)
    log_path = os.path.join(BASE_DIR, 'api.log')
    handler = RotatingFileHandler(log_path, maxBytes=10000000, backupCount=3)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)

def create_app():
    setup_logging()
    
    # Vérifier si le modèle existe avant de le charger
    if os.path.exists(MODEL_PATH):
        app.logger.info(f"Loading model from: {MODEL_PATH}")
        load_model(MODEL_PATH, app.logger)
    else:
        app.logger.error(f"Model file not found at: {MODEL_PATH}")
        app.logger.info(f"Current working directory: {os.getcwd()}")
        app.logger.info(f"Script directory: {BASE_DIR}")
        app.logger.info(f"Files in script directory: {os.listdir(BASE_DIR)}")
    
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