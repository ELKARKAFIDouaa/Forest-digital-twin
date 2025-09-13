import pandas as pd
import numpy as np
import joblib
import os
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta

model_data = None
all_features = None
selected_features = None

def load_model(model_path: str, logger):
    global model_data, all_features, selected_features
    try:
        if os.path.exists(model_path):
            model_data = joblib.load(model_path)
            all_features = model_data['all_features']
            selected_features = model_data['selected_features']
            logger.info(f"Model loaded: {model_data['best_model_name']}")
    except Exception as e:
        logger.error(f"Model loading error: {str(e)}")
        model_data = None

def get_model_data():
    return model_data

def get_all_features():
    return all_features

def get_selected_features():
    return selected_features

def allowed_file(filename: str) -> bool:
    ALLOWED_EXTENSIONS = {'txt', 'csv', 'xlsx', 'xls'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_features(data: pd.DataFrame) -> Tuple[bool, List[str], List[str]]:
    if model_data is None or all_features is None:
        return False, [], []
    
    data_columns = set(data.columns.str.strip().str.lower())
    all_features_lower = set([f.lower() for f in all_features])
    
    missing_features = list(all_features_lower - data_columns)
    extra_features = list(data_columns - all_features_lower)
    
    missing_features_original = []
    for missing in missing_features:
        for feat in all_features:
            if feat.lower() == missing:
                missing_features_original.append(feat)
                break
    
    return len(missing_features) == 0, missing_features_original, list(extra_features)

def validate_data_types(data: pd.DataFrame) -> Tuple[bool, List[str]]:
    invalid_columns = []
    
    if model_data is None or all_features is None:
        return False, ["Model not loaded"]
    
    for col in data.columns:
        if col.lower() in [f.lower() for f in all_features]:
            try:
                pd.to_numeric(data[col], errors='raise')
            except (ValueError, TypeError):
                invalid_columns.append(col)
    
    return len(invalid_columns) == 0, invalid_columns

def process_file(file_path: str, file_extension: str) -> pd.DataFrame:
    if file_extension == 'csv':
        data = pd.read_csv(file_path)
    elif file_extension in ['xlsx', 'xls']:
        data = pd.read_excel(file_path)
    elif file_extension == 'txt':
        for delimiter in [',', '\t', ';']:
            try:
                data = pd.read_csv(file_path, delimiter=delimiter)
                if len(data.columns) > 1:
                    break
            except:
                continue
        else:
            raise ValueError("Cannot determine delimiter")
    else:
        raise ValueError("Unsupported file format")
    
    data.columns = data.columns.str.strip()
    return data

def prepare_data(data: pd.DataFrame) -> np.ndarray:
    if model_data is None:
        raise Exception("Model not loaded")
    
    if all_features is None:
        raise Exception("Features not loaded")
    
    # Créer une copie pour éviter les modifications sur l'original
    data_processed = data.copy()
    
    for req_feat in all_features:
        matching_cols = [col for col in data_processed.columns if col.lower() == req_feat.lower()]
        if matching_cols:
            col_name = matching_cols[0]
            data_processed[req_feat] = pd.to_numeric(data_processed[col_name], errors='coerce')
        else:
            raise Exception(f"Required feature not found: {req_feat}")
    
    # Vérifier les valeurs manquantes
    if data_processed[all_features].isnull().any().any():
        null_columns = data_processed[all_features].columns[data_processed[all_features].isnull().any()].tolist()
        raise Exception(f"Missing values in columns: {null_columns}")
    
    # Ordonner les colonnes selon all_features
    data_ordered = data_processed[all_features]
    
    # Appliquer la sélection de features si disponible
    if 'feature_selector' in model_data and model_data['feature_selector'] is not None:
        data_selected = model_data['feature_selector'].transform(data_ordered)
    else:
        data_selected = data_ordered
    
    # Appliquer le scaler si disponible
    if 'scaler' in model_data and model_data['scaler'] is not None:
        data_scaled = model_data['scaler'].transform(data_selected)
    else:
        data_scaled = data_selected
    
    return data_scaled

def make_predictions(data_scaled: np.ndarray) -> List[Dict]:
    if model_data is None:
        raise Exception("Model not loaded")
    
    model = model_data['model']
    
    # Vérifier si le modèle a la méthode predict_proba
    if hasattr(model, 'predict_proba'):
        predictions = model.predict(data_scaled)
        probabilities = model.predict_proba(data_scaled)
    else:
        # Pour les modèles qui n'ont pas predict_proba
        predictions = model.predict(data_scaled)
        probabilities = np.zeros((len(predictions), len(model_data['label_encoder'].classes_)))
        for i, pred in enumerate(predictions):
            class_idx = np.where(model_data['label_encoder'].classes_ == pred)[0][0]
            probabilities[i, class_idx] = 1.0
    
    predicted_classes = model_data['label_encoder'].inverse_transform(predictions)
    all_classes = model_data['label_encoder'].classes_
    
    results = []
    for i in range(len(predictions)):
        class_probabilities = {
            str(class_name): float(prob) 
            for class_name, prob in zip(all_classes, probabilities[i])
        }
        
        results.append({
            'row_id': i,
            'predicted_class': str(predicted_classes[i]),
            'confidence': float(np.max(probabilities[i])),
            'probabilities': class_probabilities
        })
    
    return results

def calculate_statistics(predictions: List[Dict]) -> Dict:
    class_counts = {}
    confidences = []
    
    for pred in predictions:
        class_name = pred['predicted_class']
        class_counts[class_name] = class_counts.get(class_name, 0) + 1
        confidences.append(pred['confidence'])
    
    return {
        'total_rows': len(predictions),
        'class_distribution': class_counts,
        'average_confidence': float(np.mean(confidences)) if confidences else 0.0,
        'min_confidence': float(np.min(confidences)) if confidences else 0.0,
        'max_confidence': float(np.max(confidences)) if confidences else 0.0,
        'std_confidence': float(np.std(confidences)) if confidences else 0.0
    }

def generate_recommendations(statistics: Dict) -> List[str]:
    recommendations = []
    
    if not statistics or 'class_distribution' not in statistics or 'total_rows' not in statistics:
        return ["No valid statistics available for recommendations"]
    
    class_dist = statistics['class_distribution']
    total = statistics['total_rows']
    
    if total == 0:
        return ["No predictions available for recommendations"]
    
    critical_pct = (class_dist.get('Critical', 0) / total) * 100
    poor_pct = (class_dist.get('Poor', 0) / total) * 100
    good_pct = (class_dist.get('Good', 0) + class_dist.get('Excellent', 0)) / total * 100
    
    if critical_pct > 20:
        recommendations.append("URGENT: Over 20% critical areas - immediate intervention required")
    elif poor_pct > 30:
        recommendations.append("WARNING: Over 30% poor health areas - enhanced management needed")
    elif good_pct > 60:
        recommendations.append("GOOD: Majority of areas in good health - maintain current practices")
    else:
        recommendations.append("MIXED: Variable health conditions - differentiated management recommended")
    
    if 'average_confidence' in statistics and statistics['average_confidence'] < 0.7:
        recommendations.append("Low prediction confidence - consider additional data collection")
    
    return recommendations 