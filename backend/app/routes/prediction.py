from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
import requests
import json

ml_bp = Blueprint('ml', __name__)

# Configuration - URL de votre API ML
ML_API_URL = "http://localhost:5001"  # ou l'URL où tourne ml_forest_api

@ml_bp.route('/api/ml/classification/predict', methods=['POST'])
@jwt_required()
def ml_classification_predict():
    try:
        # Récupérer les données de la requête
        data = request.get_json()
        
        # Appeler l'API ML
        response = requests.post(
            f"{ML_API_URL}/classification/predict",
            json=data,
            timeout=30
        )
        
        # Retourner la réponse de l'API ML
        return jsonify(response.json()), response.status_code
        
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"ML API error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Internal error: {str(e)}"}), 500

@ml_bp.route('/api/ml/timeseries/predict', methods=['POST'])
@jwt_required()
def ml_timeseries_predict():
    try:
        data = request.get_json()
        response = requests.post(
            f"{ML_API_URL}/timeseries/predict",
            json=data,
            timeout=30
        )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ml_bp.route('/api/ml/models/info')
@jwt_required()
def ml_models_info():
    try:
        response = requests.get(f"{ML_API_URL}/models/info", timeout=10)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500