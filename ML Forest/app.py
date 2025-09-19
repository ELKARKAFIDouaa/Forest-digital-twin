from flask import Flask
from flask_cors import CORS
import os
from logging.handlers import RotatingFileHandler
import logging
import sys

from routes import register_routes
from utils import load_model, load_arima_models

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
    # Configure logging with proper encoding
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )
    
    # Set up file logging with UTF-8 encoding
    log_path = os.path.join(BASE_DIR, 'api.log')
    file_handler = RotatingFileHandler(
        log_path, 
        maxBytes=10000000, 
        backupCount=3,
        encoding='utf-8'
    )
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    app.logger.addHandler(file_handler)
    
    # Set console output encoding for Windows
    if sys.platform.startswith('win'):
        try:
            # Try to set UTF-8 encoding for console
            sys.stdout.reconfigure(encoding='utf-8')
        except:
            pass

def create_app():
    setup_logging()
    
    app.logger.info("=" * 50)
    app.logger.info("APPLICATION STARTUP - MULTI-YEAR NDVI PREDICTOR")
    app.logger.info("=" * 50)
    app.logger.info(f"Base directory: {BASE_DIR}")
    app.logger.info(f"Current working directory: {os.getcwd()}")
    
    # Lister tous les fichiers dans le répertoire
    try:
        all_files = os.listdir(BASE_DIR)
        pkl_files = [f for f in all_files if f.endswith('.pkl')]
        app.logger.info(f"PKL files found ({len(pkl_files)}): {pkl_files}")
    except Exception as e:
        app.logger.error(f"Error listing directory: {str(e)}")
    
    # Charger le modèle de classification forestière
    app.logger.info("-" * 30)
    app.logger.info("LOADING CLASSIFICATION MODEL")
    app.logger.info("-" * 30)
    
    if os.path.exists(MODEL_PATH):
        app.logger.info(f"Loading classification model from: {MODEL_PATH}")
        load_model(MODEL_PATH, app.logger)
    else:
        app.logger.error(f"Classification model file not found at: {MODEL_PATH}")
    
    # Charger les modèles ARIMA pour NDVI multi-années
    app.logger.info("-" * 30)
    app.logger.info("LOADING MULTI-YEAR NDVI/ARIMA MODELS")
    app.logger.info("-" * 30)
    
    load_arima_models(BASE_DIR, app.logger)
    
    # Vérifier le statut final des modèles
    app.logger.info("-" * 30)
    app.logger.info("FINAL MODEL STATUS")
    app.logger.info("-" * 30)
    
    from utils import get_model_data, get_arima_config
    
    classification_loaded = get_model_data() is not None
    ndvi_loaded = get_arima_config() is not None
    
    # Use ASCII characters instead of Unicode to avoid encoding issues
    app.logger.info(f"Classification model: {'LOADED' if classification_loaded else 'FAILED'}")
    app.logger.info(f"Multi-year NDVI/ARIMA model: {'LOADED' if ndvi_loaded else 'FAILED'}")
    
    if not classification_loaded:
        app.logger.warning("Classification model not available - some features will be disabled")
    
    if not ndvi_loaded:
        app.logger.warning("NDVI model not available - multi-year predictions will use fallback mode")
    else:
        app.logger.info("Multi-year NDVI predictions available (1-4 years: 2025-2028)")
    
    # Enregistrer les routes
    register_routes(app)
    
    @app.errorhandler(413)
    def too_large(e):
        return {'success': False, 'message': 'File too large (max 50MB)'}, 413

    @app.errorhandler(500)
    def internal_error(e):
        app.logger.error(f"Internal error: {str(e)}")
        return {'success': False, 'message': 'Internal server error'}, 500
    
    app.logger.info("=" * 50)
    app.logger.info("MULTI-YEAR FOREST HEALTH PREDICTOR READY")
    app.logger.info("Features: Classification + NDVI Multi-Year (1-4 years)")
    app.logger.info("=" * 50)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=False, host='0.0.0.0', port=5001)