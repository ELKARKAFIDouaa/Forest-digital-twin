import pandas as pd
import numpy as np
import joblib
import os
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from statsmodels.tsa.arima.model import ARIMA
import warnings
warnings.filterwarnings('ignore')

# Variables globales pour le modèle de classification
model_data = None
all_features = None
selected_features = None

# Variables globales pour le modèle de série temporelle
arima_config = None
scaler_X = None
scaler_y = None
best_model_info = None

def load_model(model_path: str, logger):
    """Charger le modèle de classification forestière"""
    global model_data, all_features, selected_features
    try:
        if os.path.exists(model_path):
            model_data = joblib.load(model_path)
            all_features = model_data['all_features']
            selected_features = model_data['selected_features']
            logger.info(f"Classification model loaded: {model_data['best_model_name']} with {len(all_features)} features")
        else:
            logger.error(f"Model file not found: {model_path}")
    except Exception as e:
        logger.error(f"Model loading error: {str(e)}")
        model_data = None

def load_arima_models(base_dir: str, logger):
    """Charger les modèles ARIMA et les scalers"""
    global arima_config, scaler_X, scaler_y, best_model_info
    
    try:
        # Charger la configuration ARIMA
        arima_path = os.path.join(base_dir, 'best_ndvi_model_arima.pkl')
        if os.path.exists(arima_path):
            arima_config = joblib.load(arima_path)
            logger.info(f"ARIMA config loaded: {arima_config}")
            
            # Ajouter les métriques manquantes depuis best_model_info.pkl si disponible
            model_info_path = os.path.join(base_dir, 'best_model_info.pkl')
            if os.path.exists(model_info_path):
                model_info = joblib.load(model_info_path)
                if isinstance(model_info, dict):
                    arima_config['rmse'] = model_info.get('rmse', 0.0192)
                    arima_config['mae'] = model_info.get('mae', 0.0149)
                    logger.info(f"Added metrics from model info: RMSE={arima_config['rmse']}, MAE={arima_config['mae']}")
            
            # Valeurs par défaut si pas dans model_info
            if 'rmse' not in arima_config:
                arima_config['rmse'] = 0.0192
            if 'mae' not in arima_config:
                arima_config['mae'] = 0.0149
        else:
            logger.warning(f"ARIMA config file not found: {arima_path}")
        
        # Charger Scaler X
        scaler_x_path = os.path.join(base_dir, 'scaler_X.pkl')
        if os.path.exists(scaler_x_path):
            scaler_X = joblib.load(scaler_x_path)
            logger.info("Scaler X loaded")
        
        # Charger Scaler Y
        scaler_y_path = os.path.join(base_dir, 'scaler_y.pkl')
        if os.path.exists(scaler_y_path):
            scaler_y = joblib.load(scaler_y_path)
            logger.info("Scaler Y loaded")
        
        # Charger les informations du modèle
        model_info_path = os.path.join(base_dir, 'best_model_info.pkl')
        if os.path.exists(model_info_path):
            best_model_info = joblib.load(model_info_path)
            logger.info(f"Model info loaded: {best_model_info}")
        
        if arima_config is not None:
            logger.info("NDVI models loading completed successfully")
        else:
            logger.error("ARIMA config not loaded - creating fallback")
            arima_config = {
                'model_type': 'ARIMA',
                'order': (1, 1, 1),
                'rmse': 0.0192,
                'mae': 0.0149
            }
            
    except Exception as e:
        logger.error(f"ARIMA models loading error: {str(e)}")
        # Créer une configuration de fallback
        arima_config = {
            'model_type': 'ARIMA',
            'order': (1, 1, 1),
            'rmse': 0.0192,
            'mae': 0.0149
        }

def get_model_data():
    return model_data

def get_all_features():
    return all_features

def get_selected_features():
    return selected_features

def get_arima_config():
    return arima_config

def get_best_model_info():
    return best_model_info

def allowed_file(filename: str) -> bool:
    ALLOWED_EXTENSIONS = {'txt', 'csv', 'xlsx', 'xls'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_features(data: pd.DataFrame) -> Tuple[bool, List[str], List[str]]:
    if model_data is None or all_features is None:
        return False, ["Model or features not loaded"], []
    
    # Clean and normalize column names
    data_columns = set([col.strip() for col in data.columns])
    data_columns_lower = set([col.lower() for col in data_columns])
    all_features_lower = set([f.lower() for f in all_features])
    
    missing_features = list(all_features_lower - data_columns_lower)
    extra_features = list(data_columns_lower - all_features_lower)
    
    # Map back to original case for missing features
    missing_features_original = []
    for missing in missing_features:
        for feat in all_features:
            if feat.lower() == missing:
                missing_features_original.append(feat)
                break
    
    return len(missing_features) == 0, missing_features_original, list(extra_features)

def validate_ndvi_data(data: pd.DataFrame) -> Tuple[bool, List[str]]:
    """Valider les données pour le modèle de série temporelle NDVI"""
    required_cols = ['NDVI_2020', 'NDVI_2021', 'NDVI_2022', 'NDVI_2023', 'NDVI_2024']
    
    missing_cols = []
    for col in required_cols:
        if col not in data.columns:
            missing_cols.append(col)
    
    return len(missing_cols) == 0, missing_cols

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
    """Préparer les données pour le modèle de classification"""
    if model_data is None:
        raise Exception("Model not loaded")
    
    if all_features is None:
        raise Exception("Features not loaded")
    
    data_processed = data.copy()
    
    for req_feat in all_features:
        matching_cols = [col for col in data_processed.columns if col.lower() == req_feat.lower()]
        if matching_cols:
            col_name = matching_cols[0]
            data_processed[req_feat] = pd.to_numeric(data_processed[col_name], errors='coerce')
        else:
            raise Exception(f"Required feature not found: {req_feat}")
    
    if data_processed[all_features].isnull().any().any():
        null_columns = data_processed[all_features].columns[data_processed[all_features].isnull().any()].tolist()
        raise Exception(f"Missing values in columns: {null_columns}")
    
    data_ordered = data_processed[all_features]
    
    if 'feature_selector' in model_data and model_data['feature_selector'] is not None:
        data_selected = model_data['feature_selector'].transform(data_ordered)
    else:
        data_selected = data_ordered
    
    if 'scaler' in model_data and model_data['scaler'] is not None:
        data_scaled = model_data['scaler'].transform(data_selected)
    else:
        data_scaled = data_selected
    
    return data_scaled

def make_predictions(data_scaled: np.ndarray) -> List[Dict]:
    """Faire des prédictions avec le modèle de classification"""
    if model_data is None:
        raise Exception("Model not loaded")
    
    model = model_data['model']
    
    if hasattr(model, 'predict_proba'):
        predictions = model.predict(data_scaled)
        probabilities = model.predict_proba(data_scaled)
    else:
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

def predict_ndvi_arima(historical_data: Dict) -> Dict:
    """Prédire NDVI pour 2025 avec ARIMA - version legacy pour compatibilité"""
    return predict_ndvi_arima_multi_year(historical_data, 1)

def predict_ndvi_arima_multi_year(historical_data: Dict, years_ahead: int = 1) -> Dict:
    """Prédire NDVI pour plusieurs années (1 à 4)"""
    if arima_config is None:
        raise Exception("ARIMA model not loaded")
    
    if years_ahead < 1 or years_ahead > 4:
        raise ValueError("years_ahead must be between 1 and 4")
    
    # Récupérer les valeurs NDVI historiques
    years = [2020, 2021, 2022, 2023, 2024]
    ndvi_values = []
    
    for year in years:
        key = f'NDVI_{year}'
        if key in historical_data:
            value = float(historical_data[key])
            if not (0 <= value <= 1):
                raise ValueError(f"Invalid NDVI value for {year}: {value} (must be between 0 and 1)")
            ndvi_values.append(value)
        else:
            raise ValueError(f"Missing {key} in data")
    
    try:
        # Créer et ajuster le modèle ARIMA
        order = arima_config.get('order', (1, 1, 1))
        
        if len(ndvi_values) < 3:
            raise ValueError("Need at least 3 historical values for ARIMA prediction")
        
        model = ARIMA(ndvi_values, order=order)
        fitted_model = model.fit()
        
        # Prédire pour plusieurs années
        forecast_result = fitted_model.forecast(steps=years_ahead)
        conf_int = fitted_model.get_forecast(steps=years_ahead).conf_int()
        
        # Préparer les prédictions par année
        predictions_by_year = {}
        future_years = list(range(2025, 2025 + years_ahead))
        
        for i, year in enumerate(future_years):
            if hasattr(forecast_result, 'iloc'):
                prediction = float(forecast_result.iloc[i])
                lower_bound = max(0.0, float(conf_int.iloc[i, 0]))
                upper_bound = min(1.0, float(conf_int.iloc[i, 1]))
            else:
                prediction = float(forecast_result[i])
                lower_bound = max(0.0, float(conf_int[i, 0]))
                upper_bound = min(1.0, float(conf_int[i, 1]))
            
            # S'assurer que la prédiction est dans une plage raisonnable
            prediction = max(0.0, min(1.0, prediction))
            
            predictions_by_year[str(year)] = {
                'prediction': prediction,
                'confidence_interval': {
                    'lower': lower_bound,
                    'upper': upper_bound
                },
                'health_status': get_ndvi_health_status(prediction)
            }
        
        # Analyser la tendance globale
        trend = "stable"
        if years_ahead > 1:
            first_prediction = predictions_by_year[str(future_years[0])]['prediction']
            last_prediction = predictions_by_year[str(future_years[-1])]['prediction']
            change = last_prediction - first_prediction
            
            if change > 0.05:
                trend = "amélioration progressive"
            elif change < -0.05:
                trend = "dégradation progressive"
        else:
            # Tendance basée sur l'historique pour une seule année
            if len(ndvi_values) > 1:
                recent_change = ndvi_values[-1] - ndvi_values[-2]
                if recent_change > 0.05:
                    trend = "amélioration"
                elif recent_change < -0.05:
                    trend = "dégradation"
        
        # Calculer la moyenne des prédictions
        avg_prediction = np.mean([pred['prediction'] for pred in predictions_by_year.values()])
        
        # Pour la compatibilité avec l'ancien format (1 année)
        if years_ahead == 1:
            year_2025 = predictions_by_year['2025']
            return {
                'success': True,
                'prediction_2025': year_2025['prediction'],
                'historical_values': {f'{year}': val for year, val in zip(years, ndvi_values)},
                'trend': trend,
                'confidence_interval': year_2025['confidence_interval'],
                'model_info': {
                    'type': 'ARIMA',
                    'order': order,
                    'rmse': arima_config.get('rmse', 0.0192),
                    'mae': arima_config.get('mae', 0.0149),
                    'aic': float(fitted_model.aic) if hasattr(fitted_model, 'aic') else None
                },
                'health_status': year_2025['health_status']
            }
        else:
            # Format multi-années
            return {
                'success': True,
                'years_predicted': years_ahead,
                'predictions_by_year': predictions_by_year,
                'historical_values': {f'{year}': val for year, val in zip(years, ndvi_values)},
                'trend': trend,
                'average_prediction': float(avg_prediction),
                'model_info': {
                    'type': 'ARIMA',
                    'order': order,
                    'rmse': arima_config.get('rmse', 0.0192),
                    'mae': arima_config.get('mae', 0.0149),
                    'aic': float(fitted_model.aic) if hasattr(fitted_model, 'aic') else None
                },
                'overall_health_status': get_ndvi_health_status(avg_prediction)
            }
        
    except Exception as e:
        raise Exception(f"Multi-year ARIMA prediction error: {str(e)}")

def predict_ndvi_batch(data: pd.DataFrame) -> List[Dict]:
    """Prédire NDVI pour plusieurs points - version legacy"""
    return predict_ndvi_batch_multi_year(data, 1)

def predict_ndvi_batch_multi_year(data: pd.DataFrame, years_ahead: int = 1) -> List[Dict]:
    """Prédire NDVI pour plusieurs points et plusieurs années"""
    predictions = []
    
    for idx, row in data.iterrows():
        try:
            historical_data = row.to_dict()
            result = predict_ndvi_arima_multi_year(historical_data, years_ahead)
            result['row_id'] = idx
            predictions.append(result)
        except Exception as e:
            predictions.append({
                'row_id': idx,
                'success': False,
                'error': str(e)
            })
    
    return predictions

def get_ndvi_health_status(ndvi_value: float) -> str:
    """Déterminer le statut de santé basé sur la valeur NDVI"""
    if ndvi_value < 0.1:
        return "Critical"
    elif ndvi_value < 0.2:
        return "Poor"
    elif ndvi_value < 0.3:
        return "Fair"
    elif ndvi_value < 0.4:
        return "Good"
    else:
        return "Excellent"

def calculate_statistics(predictions: List[Dict]) -> Dict:
    """Calculer les statistiques pour les prédictions - version legacy"""
    class_counts = {}
    confidences = []
    
    for pred in predictions:
        if 'predicted_class' in pred:  # Classification model
            class_name = pred['predicted_class']
            class_counts[class_name] = class_counts.get(class_name, 0) + 1
            confidences.append(pred['confidence'])
        elif 'prediction_2025' in pred:  # NDVI model single year
            health_status = pred.get('health_status', 'Unknown')
            class_counts[health_status] = class_counts.get(health_status, 0) + 1
            if 'confidence_interval' in pred:
                ci = pred['confidence_interval']
                confidence = 1.0 - (ci['upper'] - ci['lower']) / 2.0
                confidences.append(min(max(confidence, 0.0), 1.0))
    
    return {
        'total_rows': len(predictions),
        'class_distribution': class_counts,
        'average_confidence': float(np.mean(confidences)) if confidences else 0.0,
        'min_confidence': float(np.min(confidences)) if confidences else 0.0,
        'max_confidence': float(np.max(confidences)) if confidences else 0.0,
        'std_confidence': float(np.std(confidences)) if confidences else 0.0
    }

def calculate_statistics_multi_year(predictions: List[Dict]) -> Dict:
    """Calculer les statistiques pour les prédictions multi-années"""
    if not predictions:
        return {}
    
    # Statistiques par année
    years_stats = {}
    total_predictions = len([p for p in predictions if p.get('success', False)])
    
    if total_predictions == 0:
        return {'total_rows': len(predictions), 'successful_predictions': 0}
    
    # Collecter toutes les années prédites
    all_years = set()
    for pred in predictions:
        if pred.get('success', False):
            if 'predictions_by_year' in pred:
                all_years.update(pred['predictions_by_year'].keys())
            elif 'prediction_2025' in pred:  # Compatibilité avec format single year
                all_years.add('2025')
    
    for year in sorted(all_years):
        year_values = []
        year_health_status = {}
        
        for pred in predictions:
            if pred.get('success', False):
                year_data = None
                if 'predictions_by_year' in pred:
                    year_data = pred['predictions_by_year'].get(year)
                elif year == '2025' and 'prediction_2025' in pred:  # Compatibilité
                    year_data = {
                        'prediction': pred['prediction_2025'],
                        'health_status': pred.get('health_status', 'Unknown')
                    }
                
                if year_data:
                    year_values.append(year_data['prediction'])
                    health_status = year_data['health_status']
                    year_health_status[health_status] = year_health_status.get(health_status, 0) + 1
        
        if year_values:
            years_stats[year] = {
                'average_ndvi': float(np.mean(year_values)),
                'min_ndvi': float(np.min(year_values)),
                'max_ndvi': float(np.max(year_values)),
                'std_ndvi': float(np.std(year_values)),
                'class_distribution': year_health_status
            }
    
    # Statistiques globales
    all_predictions = []
    overall_health_status = {}
    
    for pred in predictions:
        if pred.get('success', False):
            if 'average_prediction' in pred:
                all_predictions.append(pred['average_prediction'])
            elif 'prediction_2025' in pred:  # Compatibilité
                all_predictions.append(pred['prediction_2025'])
            
            if 'overall_health_status' in pred:
                status = pred['overall_health_status']
                overall_health_status[status] = overall_health_status.get(status, 0) + 1
            elif 'health_status' in pred:  # Compatibilité
                status = pred['health_status']
                overall_health_status[status] = overall_health_status.get(status, 0) + 1
    
    return {
        'total_rows': len(predictions),
        'successful_predictions': total_predictions,
        'years_predicted': list(sorted(all_years)) if all_years else [],
        'years_statistics': years_stats,
        'overall_statistics': {
            'average_ndvi': float(np.mean(all_predictions)) if all_predictions else 0.0,
            'min_ndvi': float(np.min(all_predictions)) if all_predictions else 0.0,
            'max_ndvi': float(np.max(all_predictions)) if all_predictions else 0.0,
            'std_ndvi': float(np.std(all_predictions)) if all_predictions else 0.0,
            'class_distribution': overall_health_status
        }
    }

def generate_recommendations(statistics: Dict, model_type: str = 'classification') -> List[str]:
    """Générer des recommandations basées sur les statistiques - version legacy"""
    recommendations = []
    
    if not statistics or 'class_distribution' not in statistics or 'total_rows' not in statistics:
        return ["No valid statistics available for recommendations"]
    
    class_dist = statistics['class_distribution']
    total = statistics['total_rows']
    
    if total == 0:
        return ["No predictions available for recommendations"]
    
    if model_type == 'ndvi':
        critical_pct = (class_dist.get('Critical', 0) / total) * 100
        poor_pct = (class_dist.get('Poor', 0) / total) * 100
        good_pct = (class_dist.get('Good', 0) + class_dist.get('Excellent', 0)) / total * 100
        
        if critical_pct > 20:
            recommendations.append("URGENT: Plus de 20% des zones avec NDVI critique (<0.1) - intervention immédiate requise")
        elif poor_pct > 30:
            recommendations.append("ATTENTION: Plus de 30% des zones avec NDVI faible (0.1-0.2)")
        elif good_pct > 60:
            recommendations.append("BON: Majorité des zones avec NDVI sain (>0.3)")
    else:
        critical_pct = (class_dist.get('Critical', 0) / total) * 100
        poor_pct = (class_dist.get('Poor', 0) / total) * 100
        good_pct = (class_dist.get('Good', 0) + class_dist.get('Excellent', 0)) / total * 100
        
        if critical_pct > 20:
            recommendations.append("URGENT: Over 20% critical areas - immediate intervention required")
        elif poor_pct > 30:
            recommendations.append("WARNING: Over 30% poor health areas - enhanced management needed")
        elif good_pct > 60:
            recommendations.append("GOOD: Majority of areas in good health - maintain current practices")
    
    return recommendations

def generate_recommendations_multi_year(statistics: Dict) -> List[str]:
    """Générer des recommandations pour les prédictions multi-années"""
    recommendations = []
    
    if not statistics or 'years_statistics' not in statistics:
        return ["No valid statistics available for recommendations"]
    
    years_stats = statistics['years_statistics']
    overall_stats = statistics.get('overall_statistics', {})
    
    if not years_stats:
        return ["No year-specific predictions available"]
    
    # Analyser l'évolution temporelle
    years = sorted(years_stats.keys())
    if len(years) > 1:
        first_year_avg = years_stats[years[0]]['average_ndvi']
        last_year_avg = years_stats[years[-1]]['average_ndvi']
        trend_change = last_year_avg - first_year_avg
        
        if trend_change > 0.05:
            recommendations.append(f"TENDANCE POSITIVE: Amélioration prévue du NDVI de {first_year_avg:.3f} en {years[0]} à {last_year_avg:.3f} en {years[-1]}")
            recommendations.append("Maintenir les pratiques actuelles de gestion qui favorisent cette amélioration")
        elif trend_change < -0.05:
            recommendations.append(f"ALERTE TENDANCE: Dégradation prévue du NDVI de {first_year_avg:.3f} en {years[0]} à {last_year_avg:.3f} en {years[-1]}")
            recommendations.append("Intervention recommandée pour inverser la tendance négative")
        else:
            recommendations.append(f"STABILITÉ: NDVI prévu stable autour de {np.mean([years_stats[y]['average_ndvi'] for y in years]):.3f}")
    
    # Analyse par année
    for year in years:
        year_data = years_stats[year]
        class_dist = year_data.get('class_distribution', {})
        total = sum(class_dist.values())
        
        if total > 0:
            critical_pct = (class_dist.get('Critical', 0) / total) * 100
            poor_pct = (class_dist.get('Poor', 0) / total) * 100
            
            if critical_pct > 20:
                recommendations.append(f"URGENT {year}: {critical_pct:.1f}% zones critiques - intervention immédiate requise")
            elif poor_pct > 30:
                recommendations.append(f"ATTENTION {year}: {poor_pct:.1f}% zones en mauvaise santé - surveillance renforcée")
    
    # Recommandations globales
    if overall_stats:
        avg_ndvi = overall_stats.get('average_ndvi', 0)
        if avg_ndvi < 0.2:
            recommendations.append("STRATÉGIE GLOBALE: NDVI moyen faible - programme de reforestation à grande échelle recommandé")
        elif avg_ndvi > 0.4:
            recommendations.append("STRATÉGIE GLOBALE: NDVI moyen excellent - continuer les pratiques de conservation actuelles")
    
    recommendations.append(f"Période de prédiction: {len(years)} année(s) ({', '.join(years)})")
    
    return recommendations