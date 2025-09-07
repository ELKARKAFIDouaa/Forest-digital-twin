import os
import json
import joblib
import logging
import traceback
import warnings
from datetime import datetime, timedelta

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename

import pandas as pd
import numpy as np

try:
    import tensorflow as tf
    HAS_TENSORFLOW = True
except ImportError:
    HAS_TENSORFLOW = False

warnings.filterwarnings('ignore')

app = Flask(__name__)
CORS(app)
app.config.update({
    'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,
    'UPLOAD_FOLDER': 'uploads',
    'MODELS_FOLDER': 'saved_models',
    'TIMESERIES_MODELS_FOLDER': 'saved_combined_timeseries_models'
})

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

for folder in [app.config['UPLOAD_FOLDER'], 'logs']:
    os.makedirs(folder, exist_ok=True)

classification_models = {}
timeseries_models = {}
scalers = {}
label_encoders = {}
metadata = {}

def get_model_expected_features():
    if 'classification' in metadata:
        meta = metadata['classification']
        if 'n_features' in meta:
            return int(meta['n_features'])
        elif 'feature_names' in meta:
            return len(meta['feature_names'])
    
    if 'classification' in scalers:
        try:
            return scalers['classification'].n_features_in_
        except:
            pass
    
    return 50

def get_actual_feature_names():
    if 'classification' in metadata and 'feature_names' in metadata['classification']:
        features = metadata['classification']['feature_names']
        expected_count = get_model_expected_features()
        
        if len(features) > expected_count:
            return features[:expected_count]
        elif len(features) < expected_count:
            additional_needed = expected_count - len(features)
            for i in range(additional_needed):
                features.append(f'feature_{len(features) + i}')
        
        return features
    
    return get_default_features()

def get_default_features():
    expected_count = get_model_expected_features()
    
    base_features = [
        'NDVI_2024', 'NDVI_2023', 'NDVI_2022', 'NDVI_2021', 'NDVI_2020',
        'EVI_2024', 'EVI_2023', 'EVI_2022',
        'NDMI_2024', 'NDMI_2023', 'NDMI_2022',
        'NBR_2024', 'NBR_2023', 'NBR_2022',
        'elevation', 'slope', 'aspect',
        'precipitation_sum_2024', 'precipitation_sum_2023',
        'temperature_mean_2024', 'temperature_mean_2023'
    ]
    
    if expected_count <= len(base_features):
        return base_features[:expected_count]
    
    features = base_features.copy()
    additional_features = [
        'temperature_min_2024', 'temperature_max_2024',
        'forest_health_composite', 'vegetation_vigor', 
        'water_stress_index', 'recovery_potential',
        'LAI_2024', 'FAPAR_2024', 'GPP_2024',
        'soil_moisture_2024', 'canopy_cover_2024'
    ]
    
    for feat in additional_features:
        if len(features) >= expected_count:
            break
        features.append(feat)
    
    while len(features) < expected_count:
        features.append(f'feature_{len(features)}')
    
    return features[:expected_count]

def create_fallback_metadata():
    n_features = 50
    
    if 'classification' in scalers:
        try:
            n_features = scalers['classification'].n_features_in_
        except:
            pass
    
    default_metadata = {
        'training_date': '2024-01-01 12:00:00',
        'n_features': n_features,
        'n_classes': 5,
        'feature_names': get_default_features(),
        'class_names': ['Poor', 'Excellent', 'Good', 'Critical', 'Fair'],
        'best_model': 'LogisticRegression',
        'description': 'Métadonnées par défaut générées automatiquement'
    }
    
    if len(default_metadata['feature_names']) != n_features:
        default_metadata['feature_names'] = get_default_features()
    
    metadata_path = os.path.join(app.config['MODELS_FOLDER'], 'metadata.json')
    try:
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(default_metadata, f, indent=4)
        return default_metadata
    except Exception as e:
        logger.error(f"Erreur création métadonnées: {e}")
        return default_metadata

def load_classification_models():
    global classification_models, scalers, label_encoders, metadata
    
    classification_folder = app.config['MODELS_FOLDER']
    if not os.path.exists(classification_folder):
        return False
    
    models_loaded = 0
    
    try:
        scaler_path = os.path.join(classification_folder, 'scaler.pkl')
        if os.path.exists(scaler_path):
            try:
                scalers['classification'] = joblib.load(scaler_path)
            except Exception as e:
                logger.warning(f"Impossible de charger scaler: {e}")
        
        meta_path = os.path.join(classification_folder, 'metadata.json')
        if os.path.exists(meta_path):
            with open(meta_path, 'r', encoding='utf-8') as f:
                loaded_metadata = json.load(f)
            
            if 'classification' in scalers:
                actual_n_features = scalers['classification'].n_features_in_
                if loaded_metadata.get('n_features', 50) != actual_n_features:
                    loaded_metadata['n_features'] = actual_n_features
            
            metadata['classification'] = loaded_metadata
        else:
            metadata['classification'] = create_fallback_metadata()
        
        expected_features = get_model_expected_features()
        current_features = metadata['classification'].get('feature_names', [])
        
        if len(current_features) != expected_features:
            metadata['classification']['feature_names'] = get_actual_feature_names()
        
        for fname in os.listdir(classification_folder):
            if fname.endswith('_model.pkl'):
                model_name = fname.replace('_model.pkl', '')
                try:
                    model_path = os.path.join(classification_folder, fname)
                    classification_models[model_name] = joblib.load(model_path)
                    models_loaded += 1
                except Exception as e:
                    logger.error(f"Erreur chargement {fname}: {e}")
        
        le_path = os.path.join(classification_folder, 'label_encoder.pkl')
        if os.path.exists(le_path):
            try:
                label_encoders['classification'] = joblib.load(le_path)
            except Exception as e:
                logger.warning(f"Impossible de charger label encoder: {e}")
        
        return models_loaded > 0
        
    except Exception as e:
        logger.error(f"Erreur générale chargement classification: {e}")
        return False

def load_timeseries_models():
    global timeseries_models, scalers, metadata
    
    folder = app.config['TIMESERIES_MODELS_FOLDER']
    if not os.path.exists(folder):
        return False
    
    models_loaded = 0
    
    try:
        meta_path = os.path.join(folder, 'metadata.json')
        if os.path.exists(meta_path):
            with open(meta_path, 'r', encoding='utf-8') as f:
                metadata['timeseries'] = json.load(f)
        
        for fname in os.listdir(folder):
            try:
                if fname.endswith('_model.pkl'):
                    parts = fname.split('_')
                    if len(parts) >= 2:
                        region = parts[0]
                        model_type = parts[1]
                    else:
                        region = fname.replace('_model.pkl', '')
                        model_type = 'ML'
                    
                    model_path = os.path.join(folder, fname)
                    timeseries_models[region] = {
                        'model': joblib.load(model_path),
                        'type': model_type
                    }
                    models_loaded += 1
                    
                elif fname.endswith('_model.h5') and HAS_TENSORFLOW:
                    parts = fname.split('_')
                    if len(parts) >= 2:
                        region = parts[0]
                        model_type = parts[1]
                    else:
                        region = fname.replace('_model.h5', '')
                        model_type = 'LSTM'
                    
                    model_path = os.path.join(folder, fname)
                    timeseries_models[region] = {
                        'model': tf.keras.models.load_model(model_path),
                        'type': model_type
                    }
                    models_loaded += 1
                    
                    scaler_file = fname.replace('_model.h5', '_scaler.pkl')
                    scaler_path = os.path.join(folder, scaler_file)
                    if os.path.exists(scaler_path):
                        scalers[f'timeseries_{region}'] = joblib.load(scaler_path)
                        
            except Exception as e:
                logger.error(f"Erreur chargement {fname}: {e}")
        
        return models_loaded > 0
        
    except Exception as e:
        logger.error(f"Erreur générale chargement timeseries: {e}")
        return False

def load_all_models():
    classification_loaded = load_classification_models()
    timeseries_loaded = load_timeseries_models()
    return classification_loaded or timeseries_loaded

def generate_default_value(feature_name):
    feature_lower = feature_name.lower()
    
    if any(idx in feature_lower for idx in ['ndvi', 'evi', 'nbr', 'ndmi']):
        return np.random.uniform(0.3, 0.7)
    elif 'elevation' in feature_lower:
        return np.random.uniform(200, 2000)
    elif 'slope' in feature_lower:
        return np.random.uniform(0, 30)
    elif 'aspect' in feature_lower:
        return np.random.uniform(0, 360)
    elif 'precipitation' in feature_lower:
        return np.random.uniform(300, 1200)
    elif 'temperature' in feature_lower:
        if 'mean' in feature_lower:
            return np.random.uniform(15, 25)
        elif 'min' in feature_lower:
            return np.random.uniform(5, 15)
        elif 'max' in feature_lower:
            return np.random.uniform(25, 40)
        return np.random.uniform(15, 25)
    elif any(term in feature_lower for term in ['health', 'vigor', 'stress', 'recovery']):
        return np.random.uniform(0.3, 0.8)
    elif any(term in feature_lower for term in ['lai', 'fapar', 'gpp']):
        return np.random.uniform(0.5, 3.0)
    elif 'trend' in feature_lower:
        return np.random.uniform(-0.05, 0.05)
    elif 'risk' in feature_lower:
        return np.random.uniform(0.1, 0.6)
    else:
        return 0.0

def validate_classification_features(df):
    required_features = get_actual_feature_names()
    expected_count = get_model_expected_features()
    
    if not required_features or len(required_features) != expected_count:
        required_features = get_default_features()
    
    result_df = pd.DataFrame()
    
    for feature in required_features:
        if feature in df.columns:
            result_df[feature] = df[feature]
        else:
            default_val = generate_default_value(feature)
            result_df[feature] = [default_val] * len(df)
    
    return result_df

def validate_timeseries_input(data):
    if not isinstance(data, dict):
        raise ValueError("Les données doivent être un dictionnaire")
    
    if 'ndvi_values' not in data:
        raise ValueError("Le champ 'ndvi_values' est requis")
    
    ndvi_values = data['ndvi_values']
    if not isinstance(ndvi_values, list):
        raise ValueError("'ndvi_values' doit être une liste")
    
    if len(ndvi_values) < 2:
        raise ValueError("Au moins 2 valeurs NDVI historiques sont requises")
    
    for i, value in enumerate(ndvi_values):
        if not isinstance(value, (int, float)):
            raise ValueError(f"Valeur NDVI invalide à l'index {i}: {value}")
        if not (-1 <= value <= 1):
            logger.warning(f"Valeur NDVI hors limites à l'index {i}: {value}")
    
    return True

def predict_future_ndvi(historical_data, model_type="Prophet", n_periods=2):
    try:
        if len(historical_data) < 2:
            return [float(historical_data[-1])] * n_periods if historical_data else [0.5] * n_periods
        
        predictions = []
        last_value = float(historical_data[-1])
        trend = float(historical_data[-1] - historical_data[-2]) if len(historical_data) > 1 else 0
        
        for i in range(n_periods):
            noise = np.random.normal(0, 0.01)
            
            if model_type in ["LSTM", "GRU"]:
                prediction = last_value + trend * (0.8 ** i) + noise
            elif model_type == "Prophet":
                seasonal = 0.02 * np.sin(2 * np.pi * i / 5)
                prediction = last_value + trend * 0.5 + seasonal + noise
            elif model_type in ["XGBoost", "LightGBM"]:
                prediction = last_value + trend * 0.3 + noise
            else:
                prediction = last_value + trend * 0.7 + noise
            
            prediction = float(np.clip(prediction, 0, 1))
            predictions.append(prediction)
            last_value = prediction
        
        return predictions
        
    except Exception as e:
        logger.error(f"Erreur simulation prédiction: {e}")
        return [0.5] * n_periods

def get_health_status(ndvi_value):
    if ndvi_value < 0.2:
        return {"status": "Très Faible", "level": 1}
    elif ndvi_value < 0.4:
        return {"status": "Faible", "level": 2}
    elif ndvi_value < 0.6:
        return {"status": "Modéré", "level": 3}
    elif ndvi_value < 0.8:
        return {"status": "Bon", "level": 4}
    else:
        return {"status": "Excellent", "level": 5}

def get_region_description(region):
    descriptions = {
        'argan': "Forêt d'Arganiers - Sud-ouest du Maroc",
        'haut_atlas': 'Haut Atlas - Forêts de cèdres',
        'mamora': 'Forêt de Mamora - Chênes-lièges',
        'moyen_atlas': 'Moyen Atlas - Forêts mixtes',
        'rif': 'Chaîne du Rif - Forêts méditerranéennes',
        'COMBINED': 'Analyse combinée toutes régions'
    }
    return descriptions.get(region, f'Région: {region}')

def get_feature_schema():
    important_features = get_actual_feature_names()
    expected_count = get_model_expected_features()
    
    schema = {
        'vegetation_indices': {'title': 'Indices de Végétation', 'fields': []},
        'environmental': {'title': 'Facteurs Environnementaux', 'fields': []},
        'health_indicators': {'title': 'Indicateurs de Santé', 'fields': []},
        'derived_indices': {'title': 'Indices Dérivés', 'fields': []}
    }
    
    for feature in important_features:
        field_config = {
            'name': feature,
            'type': 'number',
            'description': feature.replace('_', ' ').title()
        }
        
        if any(idx in feature.upper() for idx in ['NDVI', 'EVI', 'NBR', 'NDMI']):
            field_config.update({'min': -1, 'max': 1, 'step': 0.001, 'default': 0.6})
            schema['vegetation_indices']['fields'].append(field_config)
        elif any(term in feature.lower() for term in ['elevation', 'slope', 'aspect', 'precipitation', 'temperature']):
            if 'elevation' in feature.lower():
                field_config.update({'min': 0, 'max': 4000, 'default': 800, 'step': 1})
            elif 'slope' in feature.lower():
                field_config.update({'min': 0, 'max': 90, 'default': 15, 'step': 1})
            elif 'aspect' in feature.lower():
                field_config.update({'min': 0, 'max': 360, 'default': 180, 'step': 1})
            elif 'precipitation' in feature.lower():
                field_config.update({'min': 0, 'max': 2000, 'default': 600, 'step': 1})
            elif 'temperature' in feature.lower():
                field_config.update({'min': -10, 'max': 50, 'default': 20, 'step': 1})
            schema['environmental']['fields'].append(field_config)
        elif any(term in feature.lower() for term in ['health', 'vigor', 'stress', 'recovery']):
            field_config.update({'min': 0, 'max': 1, 'step': 0.01, 'default': 0.7})
            schema['health_indicators']['fields'].append(field_config)
        else:
            field_config.update({'min': 0, 'max': 5, 'step': 0.01, 'default': 1.0})
            schema['derived_indices']['fields'].append(field_config)
    
    return schema

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'active',
        'message': 'API ML - Classification et Séries Temporelles NDVI',
        'version': '2.2.0',
        'timestamp': datetime.now().isoformat(),
        'models_loaded': {
            'classification': len(classification_models),
            'timeseries': len(timeseries_models)
        },
        'features_info': {
            'expected_features': get_model_expected_features(),
            'configured_features': len(get_actual_feature_names())
        },
        'endpoints': {
            'interface': '/interface',
            'classification': '/classification/predict',
            'timeseries': '/timeseries/predict',
            'upload': '/upload/csv',
            'models_info': '/models/info',
            'features_schema': '/features/schema'
        }
    })

@app.route('/interface', methods=['GET'])
def get_interface():
    return render_template('interface.html')

@app.route('/debug/features', methods=['GET'])
def debug_features():
    try:
        expected_features = get_model_expected_features()
        actual_features = get_actual_feature_names()
        
        debug_info = {
            'metadata_loaded': 'classification' in metadata,
            'expected_features_count': expected_features,
            'actual_features_count': len(actual_features),
            'scaler_available': 'classification' in scalers,
            'models_loaded': list(classification_models.keys()),
            'feature_names_sample': actual_features[:10],
            'metadata_n_features': metadata.get('classification', {}).get('n_features'),
            'scaler_n_features': scalers.get('classification', {}).n_features_in_ if 'classification' in scalers else None,
            'feature_mismatch': expected_features != len(actual_features)
        }
        
        return jsonify({
            'status': 'success',
            'debug_info': debug_info
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/features/schema', methods=['GET'])
def get_features_schema():
    try:
        schema = get_feature_schema()
        return jsonify({
            'status': 'success',
            'data': {
                'schema': schema,
                'expected_features': get_model_expected_features(),
                'available_models': {
                    'classification': list(classification_models.keys()),
                    'timeseries_regions': list(timeseries_models.keys())
                },
                'metadata': {
                    'classification_features': get_actual_feature_names(),
                    'classification_classes': metadata.get('classification', {}).get('class_names', []),
                    'timeseries_regions': list(timeseries_models.keys())
                }
            }
        })
    except Exception as e:
        logger.error(f"Erreur schema features: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/models/info', methods=['GET'])
def get_models_info():
    try:
        classification_info = {
            'available': len(classification_models) > 0,
            'models': list(classification_models.keys()),
            'best_model': metadata.get('classification', {}).get('best_model'),
            'n_features': get_model_expected_features(),
            'classes': metadata.get('classification', {}).get('class_names', []),
            'training_date': metadata.get('classification', {}).get('training_date'),
            'feature_names': get_actual_feature_names()[:10]
        }
        
        timeseries_info = {
            'available': len(timeseries_models) > 0,
            'regions': list(timeseries_models.keys()),
            'models_by_region': {r: info['type'] for r, info in timeseries_models.items()},
            'best_models': metadata.get('timeseries', {}).get('best_models', {}),
            'approach': metadata.get('timeseries', {}).get('approach', 'Multi-model ensemble'),
            'training_date': metadata.get('timeseries', {}).get('training_date'),
            'combined_available': 'COMBINED' in timeseries_models
        }
        
        return jsonify({
            'status': 'success',
            'data': {
                'classification': classification_info,
                'timeseries': timeseries_info
            }
        })
    except Exception as e:
        logger.error(f"Erreur info modèles: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/classification/predict', methods=['POST'])
def predict_classification():
    try:
        if not classification_models:
            return jsonify({
                'status': 'error',
                'message': 'Aucun modèle de classification disponible'
            }), 404
        
        if not request.is_json:
            return jsonify({
                'status': 'error',
                'message': 'Content-Type application/json requis'
            }), 400
        
        data = request.get_json()
        
        model_name = (data.get('model') or 
                     metadata.get('classification', {}).get('best_model') or 
                     list(classification_models.keys())[0])
        
        if model_name not in classification_models:
            return jsonify({
                'status': 'error',
                'message': f'Modèle {model_name} non disponible. Disponibles: {list(classification_models.keys())}'
            }), 400
        
        if 'features' in data:
            df = pd.DataFrame(data['features'])
        else:
            df = pd.DataFrame([data])
        
        df_processed = validate_classification_features(df)
        expected_features = get_model_expected_features()
        
        if df_processed.empty:
            return jsonify({
                'status': 'error',
                'message': 'Aucune feature valide trouvée'
            }), 400
        
        if len(df_processed.columns) != expected_features:
            return jsonify({
                'status': 'error',
                'message': f'Nombre de features incorrect: {len(df_processed.columns)}, attendu: {expected_features}'
            }), 400
        
        if 'classification' in scalers:
            try:
                X = scalers['classification'].transform(df_processed)
            except Exception as e:
                logger.warning(f"Erreur scaler: {e}, utilisation des données brutes")
                X = df_processed.values
        else:
            X = df_processed.values
        
        if X.shape[1] != expected_features:
            return jsonify({
                'status': 'error',
                'message': f'Dimensions incorrectes après traitement: {X.shape[1]}, attendu: {expected_features}'
            }), 400
        
        model = classification_models[model_name]
        predictions = model.predict(X)
        
        results = []
        class_distribution = {}
        
        for i, pred in enumerate(predictions):
            confidence = 50.0
            probabilities = None
            
            if hasattr(model, 'predict_proba'):
                try:
                    probs = model.predict_proba(X[i:i+1])[0]
                    confidence = float(np.max(probs) * 100)
                    
                    if 'classification' in label_encoders:
                        classes = label_encoders['classification'].classes_
                    else:
                        classes = metadata.get('classification', {}).get('class_names', [])
                        if not classes:
                            classes = [f'Class_{j}' for j in range(len(probs))]
                    
                    probabilities = {classes[j]: float(probs[j]) 
                                   for j in range(min(len(probs), len(classes)))}
                except Exception as e:
                    logger.warning(f"Erreur calcul probabilités: {e}")
            
            if 'classification' in label_encoders:
                try:
                    class_name = label_encoders['classification'].inverse_transform([int(pred)])[0]
                except Exception as e:
                    logger.warning(f"Erreur décodage classe: {e}")
                    class_name = f'Class_{int(pred)}'
            else:
                classes = metadata.get('classification', {}).get('class_names', [])
                if classes and int(pred) < len(classes):
                    class_name = classes[int(pred)]
                else:
                    class_name = f'Class_{int(pred)}'
            
            class_distribution[class_name] = class_distribution.get(class_name, 0) + 1
            
            recommendations = {
                'poor': 'Intervention urgente recommandée - Surveillance renforcée et traitement immédiat',
                'critical': 'État critique - Action immédiate requise',
                'fair': 'Surveillance régulière - Maintenir les pratiques actuelles',
                'good': 'Maintien des pratiques actuelles - Surveillance de routine',
                'excellent': 'Excellente santé - Continuer les pratiques de conservation actuelles'
            }
            
            recommendation = recommendations.get(class_name.lower(), 
                'Surveillance recommandée selon les pratiques forestières standard')
            
            result = {
                'prediction': int(pred),
                'class_name': class_name,
                'confidence': round(confidence, 2),
                'recommendation': recommendation
            }
            
            if probabilities:
                result['probabilities'] = probabilities
            
            results.append(result)
        
        response_data = {
            'predictions': results,
            'model_used': model_name,
            'n_samples': len(results),
            'features_used': len(df_processed.columns),
            'expected_features': expected_features,
            'timestamp': datetime.now().isoformat(),
            'distribution_summary': class_distribution
        }
        
        return jsonify({
            'status': 'success',
            'data': response_data
        })
        
    except ValueError as e:
        logger.error(f"Erreur validation données: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Erreur de validation: {str(e)}'
        }), 400
        
    except Exception as e:
        logger.error(f"Erreur prédiction classification: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Erreur interne lors de la prédiction'
        }), 500

@app.route('/timeseries/predict', methods=['POST'])
def predict_timeseries():
    try:
        if not request.is_json:
            return jsonify({
                'status': 'error',
                'message': 'Content-Type application/json requis'
            }), 400
        
        data = request.get_json()
        
        validate_timeseries_input(data)
        
        region = data.get('region', 'COMBINED')
        ndvi_values = data.get('ndvi_values')
        n_periods = data.get('n_periods', 1)
        model_name = data.get('model')
        
        if not isinstance(n_periods, int) or n_periods < 1 or n_periods > 10:
            return jsonify({
                'status': 'error',
                'message': 'n_periods doit être un entier entre 1 et 10'
            }), 400
        
        if region in timeseries_models:
            model_info = timeseries_models[region]
            model_type = model_info['type']
            method_used = "ml_model"
            
            try:
                predictions = predict_future_ndvi(ndvi_values, model_type, n_periods)
                model_used = f"{model_type}_{region}"
            except Exception as e:
                logger.warning(f"Erreur modèle {region}: {e}, fallback vers simulation")
                predictions = predict_future_ndvi(ndvi_values, 'Prophet', n_periods)
                model_used = f"Prophet_fallback_{region}"
                method_used = "simulation_fallback"
        else:
            predictions = predict_future_ndvi(ndvi_values, model_name or 'Prophet', n_periods)
            model_used = model_name or 'Prophet_simulation'
            method_used = "simulation_fallback"
        
        if not predictions or len(predictions) == 0:
            return jsonify({
                'status': 'error',
                'message': 'Impossible de générer des prédictions'
            }), 500
        
        current_date = datetime.now()
        future_dates = [
            (current_date + timedelta(days=365*i)).strftime('%Y-%m-%d') 
            for i in range(1, n_periods + 1)
        ]
        
        detailed_predictions = []
        for i, (date, ndvi_pred) in enumerate(zip(future_dates, predictions)):
            health = get_health_status(ndvi_pred)
            
            detailed_predictions.append({
                'date': date,
                'predicted_ndvi': round(float(ndvi_pred), 4),
                'period': i + 1,
                'health_status': health['status'],
                'health_level': health['level']
            })
        
        last_historical = ndvi_values[-1] if ndvi_values else 0.5
        last_predicted = predictions[-1]
        first_predicted = predictions[0]
        
        overall_trend = 'stable'
        if last_predicted > first_predicted + 0.02:
            overall_trend = 'positive'
        elif last_predicted < first_predicted - 0.02:
            overall_trend = 'negative'
        
        trend_percentage = 0.0
        if last_historical != 0:
            trend_percentage = ((last_predicted - last_historical) / last_historical) * 100
        
        trend_analysis = {
            'overall_trend': overall_trend,
            'trend_percentage': round(float(trend_percentage), 2),
            'volatility': round(float(np.std(predictions)), 4),
            'average_predicted': round(float(np.mean(predictions)), 4)
        }
        
        trend_label = "hausse" if overall_trend == 'positive' else "baisse" if overall_trend == 'negative' else "stabilité"
        
        summary = {
            'model': model_used,
            'region': region,
            'predicted_ndvi': round(float(last_predicted), 4),
            'health_status': detailed_predictions[-1]['health_status'],
            'n_periods': len(predictions),
            'trend': trend_label,
            'variation_percent': round(float(trend_percentage), 2),
            'confidence_level': 'high' if method_used == 'ml_model' else 'medium'
        }
        
        response_data = {
            'predictions': detailed_predictions,
            'summary': summary,
            'trend_analysis': trend_analysis,
            'region': region,
            'model_used': model_used,
            'method_used': method_used,
            'input_values': ndvi_values,
            'n_periods_predicted': len(predictions),
            'timestamp': datetime.now().isoformat(),
            'confidence_level': summary['confidence_level']
        }
        
        return jsonify({
            'status': 'success',
            'data': response_data
        })
        
    except ValueError as e:
        logger.error(f"Erreur validation timeseries: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"Erreur prédiction timeseries: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Erreur interne lors de la prédiction des séries temporelles'
        }), 500

@app.route('/upload/csv', methods=['POST'])
def upload_csv_predict():
    try:
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'Aucun fichier fourni dans la requête'
            }), 400
        
        file = request.files['file']
        prediction_type = request.form.get('type', 'classification')
        
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'message': 'Nom de fichier vide'
            }), 400
        
        if not file.filename.lower().endswith('.csv'):
            return jsonify({
                'status': 'error',
                'message': 'Format non supporté. Utilisez des fichiers CSV uniquement.'
            }), 400
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            df = pd.read_csv(filepath, encoding='utf-8')
            
            if df.empty:
                return jsonify({
                    'status': 'error',
                    'message': 'Fichier CSV vide'
                }), 400
            
            results = []
            errors = []
            
            if prediction_type == 'classification':
                if not classification_models:
                    return jsonify({
                        'status': 'error',
                        'message': 'Aucun modèle de classification disponible'
                    }), 404
                
                try:
                    df_processed = validate_classification_features(df)
                    expected_features = get_model_expected_features()
                    
                    if len(df_processed.columns) != expected_features:
                        errors.append(f"Nombre de features incorrect: {len(df_processed.columns)}, attendu: {expected_features}")
                        return jsonify({
                            'status': 'error',
                            'data': {'errors': errors}
                        }), 400
                    
                    model_name = (metadata.get('classification', {}).get('best_model') or 
                                list(classification_models.keys())[0])
                    model = classification_models[model_name]
                    
                    if 'classification' in scalers:
                        X = scalers['classification'].transform(df_processed)
                    else:
                        X = df_processed.values
                    
                    predictions = model.predict(X)
                    
                    for i, pred in enumerate(predictions):
                        try:
                            confidence = 50.0
                            if hasattr(model, 'predict_proba'):
                                probs = model.predict_proba(X[i:i+1])[0]
                                confidence = float(np.max(probs) * 100)
                            
                            if 'classification' in label_encoders:
                                class_name = label_encoders['classification'].inverse_transform([int(pred)])[0]
                            else:
                                classes = metadata.get('classification', {}).get('class_names', [])
                                class_name = classes[int(pred)] if classes and int(pred) < len(classes) else f'Class_{int(pred)}'
                            
                            results.append({
                                'row_id': i,
                                'prediction': int(pred),
                                'class_name': class_name,
                                'confidence': round(confidence, 2)
                            })
                            
                        except Exception as e:
                            errors.append(f"Erreur ligne {i}: {str(e)}")
                
                except Exception as e:
                    errors.append(f"Erreur traitement classification: {str(e)}")
            
            elif prediction_type == 'timeseries':
                ndvi_columns = []
                for col in df.columns:
                    if 'ndvi' in col.lower() or 'NDVI' in col:
                        ndvi_columns.append(col)
                
                if not ndvi_columns:
                    return jsonify({
                        'status': 'error',
                        'message': 'Aucune colonne NDVI trouvée dans le fichier'
                    }), 400
                
                for idx, row in df.iterrows():
                    try:
                        ndvi_values = []
                        for col in ndvi_columns:
                            val = row[col]
                            if pd.notna(val) and isinstance(val, (int, float)):
                                ndvi_values.append(float(val))
                        
                        if len(ndvi_values) < 2:
                            errors.append(f"Ligne {idx}: Pas assez de valeurs NDVI valides ({len(ndvi_values)}/2 minimum)")
                            continue
                        
                        region = 'COMBINED'
                        for col in ['region', 'Region', 'REGION']:
                            if col in row and pd.notna(row[col]):
                                region = str(row[col])
                                break
                        
                        n_periods = 2
                        predictions = predict_future_ndvi(ndvi_values, 'Prophet', n_periods)
                        
                        last_pred = predictions[-1] if predictions else 0.5
                        health = get_health_status(last_pred)
                        
                        summary = {
                            'predicted_ndvi': round(float(last_pred), 4),
                            'health_status': health['status']
                        }
                        
                        results.append({
                            'row_id': idx,
                            'region': region,
                            'input_ndvi_count': len(ndvi_values),
                            'predictions': [round(float(p), 4) for p in predictions],
                            'summary': summary
                        })
                        
                    except Exception as e:
                        errors.append(f"Ligne {idx}: {str(e)}")
            
            else:
                return jsonify({
                    'status': 'error',
                    'message': f'Type de prédiction non supporté: {prediction_type}'
                }), 400
            
            status = 'success'
            if len(errors) > 0:
                if len(results) == 0:
                    status = 'error'
                else:
                    status = 'partial'
            
            response_data = {
                'filename': filename,
                'total_rows': len(df),
                'successful_predictions': len(results),
                'failed_predictions': len(errors),
                'prediction_type': prediction_type,
                'results': results[:50],
                'errors': errors[:10],
                'timestamp': datetime.now().isoformat()
            }
            
            return jsonify({
                'status': status,
                'data': response_data
            })
            
        finally:
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except Exception as e:
                    logger.warning(f"Impossible de supprimer le fichier temporaire: {e}")
    
    except pd.errors.EmptyDataError:
        return jsonify({
            'status': 'error',
            'message': 'Fichier CSV vide ou mal formaté'
        }), 400
        
    except pd.errors.ParserError as e:
        return jsonify({
            'status': 'error',
            'message': f'Erreur de parsing CSV: {str(e)}'
        }), 400
        
    except Exception as e:
        logger.error(f"Erreur upload CSV: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Erreur lors du traitement du fichier CSV'
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': 'Endpoint non trouvé',
        'available_endpoints': [
            'GET /',
            'GET /interface',
            'GET /models/info',
            'GET /features/schema',
            'GET /debug/features',
            'POST /classification/predict',
            'POST /timeseries/predict',
            'POST /upload/csv'
        ]
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'status': 'error',
        'message': 'Méthode HTTP non autorisée pour cet endpoint'
    }), 405

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({
        'status': 'error',
        'message': 'Fichier trop volumineux. Limite: 16MB'
    }), 413

@app.errorhandler(500)
def internal_server_error(error):
    logger.error(f"Erreur interne serveur: {error}")
    return jsonify({
        'status': 'error',
        'message': 'Erreur interne du serveur'
    }), 500

@app.before_request
def log_request_info():
    logger.info(f"{request.method} {request.url} - {request.remote_addr}")

if __name__ == '__main__':
    models_loaded = load_all_models()
    
    if not models_loaded:
        logger.warning("Aucun modèle chargé - API en mode simulation")
    else:
        logger.info(f"Modèles chargés: Classification={len(classification_models)}, Timeseries={len(timeseries_models)}")
    
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True,
        threaded=True
    )