from flask import request, jsonify, send_file, render_template_string
from werkzeug.utils import secure_filename
from datetime import datetime
import pandas as pd
import numpy as np
import os
import io
import json

from utils import (
    get_model_data, get_all_features, get_selected_features,
    get_arima_config, get_best_model_info,
    allowed_file, validate_features, validate_data_types,
    validate_ndvi_data, process_file, prepare_data, 
    make_predictions, predict_ndvi_arima, predict_ndvi_batch,
    predict_ndvi_arima_multi_year, predict_ndvi_batch_multi_year,
    calculate_statistics, generate_recommendations,
    calculate_statistics_multi_year, generate_recommendations_multi_year
)

def register_routes(app):
    
    @app.route('/')
    def index():
        try:
            with open('templates/index.html', 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            with open('templates/index.html', 'r', encoding='latin1') as f:
                return f.read()
        except FileNotFoundError:
            return "Index file not found", 404
    
    @app.route('/health', methods=['GET'])
    def health_check():
        model_data = get_model_data()
        all_features = get_all_features()
        arima_config = get_arima_config()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'classification_model_loaded': model_data is not None,
            'arima_model_loaded': arima_config is not None,
            'model_name': model_data['best_model_name'] if model_data else None,
            'features_count': len(all_features) if all_features else 0,
            'available_models': {
                'classification': model_data is not None,
                'ndvi_timeseries': arima_config is not None
            }
        })

    @app.route('/model/info', methods=['GET'])
    def model_info():
        model_type = request.args.get('type', 'classification')
        
        if model_type == 'classification':
            model_data = get_model_data()
            all_features = get_all_features()
            selected_features = get_selected_features()
            
            if model_data is None:
                return jsonify({'success': False, 'message': 'Classification model not loaded'}), 500
            
            return jsonify({
                'success': True,
                'model_type': 'classification',
                'model_name': model_data['best_model_name'],
                'all_features': all_features,
                'selected_features': selected_features,
                'classes': model_data['label_encoder'].classes_.tolist(),
                'total_features_count': len(all_features),
                'selected_features_count': len(selected_features)
            })
        
        elif model_type == 'ndvi':
            arima_config = get_arima_config()
            best_info = get_best_model_info()
            
            if arima_config is None:
                return jsonify({'success': False, 'message': 'NDVI model not loaded'}), 500
            
            return jsonify({
                'success': True,
                'model_type': 'ndvi_timeseries',
                'model_name': 'ARIMA',
                'required_features': ['NDVI_2020', 'NDVI_2021', 'NDVI_2022', 'NDVI_2023', 'NDVI_2024'],
                'prediction_target': 'NDVI_2025_to_2028',
                'max_years_ahead': 4,
                'model_config': {
                    'order': arima_config.get('order', [1, 1, 1]),
                    'rmse': arima_config.get('rmse', 0.0192),
                    'mae': arima_config.get('mae', 0.0149)
                },
                'best_model_info': best_info if best_info else {}
            })
        
        else:
            return jsonify({'success': False, 'message': 'Invalid model type'}), 400

    @app.route('/model/template', methods=['GET'])
    def get_template():
        model_type = request.args.get('type', 'classification')
        
        if model_type == 'classification':
            model_data = get_model_data()
            all_features = get_all_features()
            
            if model_data is None:
                return jsonify({'success': False, 'message': 'Model not loaded'}), 500
            
            template_data = {feature: 0.0 for feature in all_features}
            
            return jsonify({
                'success': True,
                'model_type': 'classification',
                'all_features': all_features,
                'template': template_data
            })
        
        elif model_type == 'ndvi':
            template_data = {
                'NDVI_2020': 0.3,
                'NDVI_2021': 0.32,
                'NDVI_2022': 0.31,
                'NDVI_2023': 0.33,
                'NDVI_2024': 0.34
            }
            
            return jsonify({
                'success': True,
                'model_type': 'ndvi',
                'template': template_data,
                'description': 'Historical NDVI values from 2020 to 2024 for predicting up to 4 years ahead (2025-2028)',
                'max_years_ahead': 4
            })
        
        else:
            return jsonify({'success': False, 'message': 'Invalid model type'}), 400

    @app.route('/model/template/download', methods=['GET'])
    def download_template():
        model_type = request.args.get('type', 'classification')
        
        if model_type == 'classification':
            model_data = get_model_data()
            all_features = get_all_features()
            
            if model_data is None:
                return jsonify({'success': False, 'message': 'Model not loaded'}), 500
            
            csv_content = ','.join(all_features) + '\n'
            example_data = [str(np.random.uniform(0, 1)) for _ in all_features]
            csv_content += ','.join(example_data)
            
            return send_file(
                io.BytesIO(csv_content.encode()),
                mimetype='text/csv',
                as_attachment=True,
                download_name='forest_health_template.csv'
            )
        
        elif model_type == 'ndvi':
            csv_content = 'NDVI_2020,NDVI_2021,NDVI_2022,NDVI_2023,NDVI_2024\n'
            csv_content += '0.3,0.32,0.31,0.33,0.34\n'
            csv_content += '0.25,0.26,0.24,0.27,0.28\n'
            csv_content += '0.4,0.42,0.41,0.43,0.44\n'
            
            return send_file(
                io.BytesIO(csv_content.encode()),
                mimetype='text/csv',
                as_attachment=True,
                download_name='ndvi_timeseries_template.csv'
            )
        
        else:
            return jsonify({'success': False, 'message': 'Invalid model type'}), 400

    @app.route('/predict/single', methods=['POST'])
    def predict_single():
        try:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'message': 'No data provided'}), 400
            
            model_type = data.get('model_type', 'classification')
            
            if model_type == 'classification':
                model_data = get_model_data()
                all_features = get_all_features()
                
                if model_data is None:
                    return jsonify({'success': False, 'message': 'Model not loaded'}), 500
                
                df = pd.DataFrame([data])
                is_valid, missing_features, extra_features = validate_features(df)
                
                if not is_valid:
                    return jsonify({
                        'success': False,
                        'message': 'Missing features',
                        'missing_features': missing_features,
                        'required_features': all_features
                    }), 400
                
                types_valid, invalid_columns = validate_data_types(df)
                if not types_valid:
                    return jsonify({
                        'success': False,
                        'message': 'Invalid data types',
                        'invalid_columns': invalid_columns
                    }), 400
                
                data_scaled = prepare_data(df)
                predictions = make_predictions(data_scaled)
                
                return jsonify({
                    'success': True,
                    'model_type': 'classification',
                    'prediction': predictions[0],
                    'model_used': model_data['best_model_name'],
                    'timestamp': datetime.now().isoformat()
                })
            
            elif model_type == 'ndvi':
                arima_config = get_arima_config()
                
                if arima_config is None:
                    return jsonify({'success': False, 'message': 'ARIMA model not loaded'}), 500
                
                # Support pour years_ahead (1 à 4 années)
                years_ahead = data.get('years_ahead', 1)
                if years_ahead < 1 or years_ahead > 4:
                    return jsonify({
                        'success': False, 
                        'message': 'years_ahead must be between 1 and 4'
                    }), 400
                
                result = predict_ndvi_arima_multi_year(data, years_ahead)
                
                return jsonify({
                    'success': True,
                    'model_type': 'ndvi',
                    'years_ahead': years_ahead,
                    'prediction': result,
                    'model_used': 'ARIMA',
                    'timestamp': datetime.now().isoformat()
                })
            
            else:
                return jsonify({'success': False, 'message': 'Invalid model type'}), 400
                
        except Exception as e:
            app.logger.error(f"Single prediction error: {str(e)}")
            return jsonify({'success': False, 'message': str(e)}), 500

    @app.route('/predict/batch', methods=['POST'])
    def predict_batch():
        try:
            data = request.get_json()
            if not data or 'data' not in data:
                return jsonify({'success': False, 'message': 'No data provided'}), 400
            
            model_type = data.get('model_type', 'classification')
            
            if model_type == 'classification':
                model_data = get_model_data()
                
                if model_data is None:
                    return jsonify({'success': False, 'message': 'Model not loaded'}), 500
                
                df = pd.DataFrame(data['data'])
                is_valid, missing_features, extra_features = validate_features(df)
                
                if not is_valid:
                    return jsonify({
                        'success': False,
                        'message': 'Missing features',
                        'missing_features': missing_features
                    }), 400
                
                data_scaled = prepare_data(df)
                predictions = make_predictions(data_scaled)
                statistics = calculate_statistics(predictions)
                recommendations = generate_recommendations(statistics, 'classification')
                
                return jsonify({
                    'success': True,
                    'model_type': 'classification',
                    'predictions': predictions,
                    'statistics': statistics,
                    'recommendations': recommendations,
                    'model_used': model_data['best_model_name'],
                    'timestamp': datetime.now().isoformat()
                })
            
            elif model_type == 'ndvi':
                df = pd.DataFrame(data['data'])
                is_valid, missing_cols = validate_ndvi_data(df)
                
                if not is_valid:
                    return jsonify({
                        'success': False,
                        'message': 'Missing NDVI columns',
                        'missing_columns': missing_cols
                    }), 400
                
                # Support pour years_ahead
                years_ahead = data.get('years_ahead', 1)
                if years_ahead < 1 or years_ahead > 4:
                    return jsonify({
                        'success': False, 
                        'message': 'years_ahead must be between 1 and 4'
                    }), 400
                
                predictions = predict_ndvi_batch_multi_year(df, years_ahead)
                statistics = calculate_statistics_multi_year(predictions)
                recommendations = generate_recommendations_multi_year(statistics)
                
                return jsonify({
                    'success': True,
                    'model_type': 'ndvi',
                    'years_ahead': years_ahead,
                    'predictions': predictions,
                    'statistics': statistics,
                    'recommendations': recommendations,
                    'model_used': 'ARIMA',
                    'timestamp': datetime.now().isoformat()
                })
            
            else:
                return jsonify({'success': False, 'message': 'Invalid model type'}), 400
                
        except Exception as e:
            app.logger.error(f"Batch prediction error: {str(e)}")
            return jsonify({'success': False, 'message': str(e)}), 500

    @app.route('/predict/file', methods=['POST'])
    def predict_file():
        try:
            if 'file' not in request.files:
                return jsonify({'success': False, 'message': 'No file provided'}), 400
            
            file = request.files['file']
            model_type = request.form.get('model_type', 'classification')
            
            if file.filename == '' or not allowed_file(file.filename):
                return jsonify({'success': False, 'message': 'Invalid file'}), 400
            
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            try:
                file_extension = filename.rsplit('.', 1)[1].lower()
                df = process_file(file_path, file_extension)
                
                if model_type == 'classification':
                    model_data = get_model_data()
                    
                    if model_data is None:
                        return jsonify({'success': False, 'message': 'Model not loaded'}), 500
                    
                    is_valid, missing_features, extra_features = validate_features(df)
                    if not is_valid:
                        return jsonify({
                            'success': False,
                            'message': 'Missing required features',
                            'missing_features': missing_features,
                            'found_features': df.columns.tolist()
                        }), 400
                    
                    types_valid, invalid_columns = validate_data_types(df)
                    if not types_valid:
                        return jsonify({
                            'success': False,
                            'message': 'Invalid data types',
                            'invalid_columns': invalid_columns
                        }), 400
                    
                    data_scaled = prepare_data(df)
                    predictions = make_predictions(data_scaled)
                    statistics = calculate_statistics(predictions)
                    recommendations = generate_recommendations(statistics, 'classification')
                    
                    file_info = {
                        'filename': file.filename,
                        'rows': len(df),
                        'columns': len(df.columns),
                        'file_size': os.path.getsize(file_path)
                    }
                    
                    return jsonify({
                        'success': True,
                        'model_type': 'classification',
                        'predictions': predictions,
                        'statistics': statistics,
                        'recommendations': recommendations,
                        'file_info': file_info,
                        'model_used': model_data['best_model_name'],
                        'timestamp': datetime.now().isoformat()
                    })
                
                elif model_type == 'ndvi':
                    is_valid, missing_cols = validate_ndvi_data(df)
                    
                    if not is_valid:
                        return jsonify({
                            'success': False,
                            'message': 'Missing NDVI columns',
                            'missing_columns': missing_cols,
                            'found_columns': df.columns.tolist()
                        }), 400
                    
                    # Support pour years_ahead dans les fichiers
                    years_ahead = int(request.form.get('years_ahead', 1))
                    if years_ahead < 1 or years_ahead > 4:
                        return jsonify({
                            'success': False, 
                            'message': 'years_ahead must be between 1 and 4'
                        }), 400
                    
                    predictions = predict_ndvi_batch_multi_year(df, years_ahead)
                    statistics = calculate_statistics_multi_year(predictions)
                    recommendations = generate_recommendations_multi_year(statistics)
                    
                    file_info = {
                        'filename': file.filename,
                        'rows': len(df),
                        'columns': len(df.columns),
                        'file_size': os.path.getsize(file_path)
                    }
                    
                    return jsonify({
                        'success': True,
                        'model_type': 'ndvi',
                        'years_ahead': years_ahead,
                        'predictions': predictions,
                        'statistics': statistics,
                        'recommendations': recommendations,
                        'file_info': file_info,
                        'model_used': 'ARIMA',
                        'timestamp': datetime.now().isoformat()
                    })
                
                else:
                    return jsonify({'success': False, 'message': 'Invalid model type'}), 400
                    
            finally:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    
        except Exception as e:
            app.logger.error(f"File prediction error: {str(e)}")
            return jsonify({'success': False, 'message': str(e)}), 500

    @app.route('/analyze/data', methods=['POST'])
    def analyze_data():
        try:
            data = request.get_json()
            if not data or 'data' not in data:
                return jsonify({'success': False, 'message': 'No data provided'}), 400
            
            df = pd.DataFrame(data['data'])
            model_type = data.get('model_type', 'classification')
            
            analysis = {
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': df.columns.tolist(),
                'data_types': df.dtypes.astype(str).to_dict(),
                'missing_values': df.isnull().sum().to_dict(),
                'numeric_summary': {}
            }
            
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                analysis['numeric_summary'][col] = {
                    'mean': float(df[col].mean()),
                    'std': float(df[col].std()),
                    'min': float(df[col].min()),
                    'max': float(df[col].max()),
                    'median': float(df[col].median())
                }
            
            if model_type == 'classification':
                all_features = get_all_features()
                if all_features:
                    is_valid, missing_features, extra_features = validate_features(df)
                    analysis['validation'] = {
                        'features_valid': is_valid,
                        'missing_features': missing_features,
                        'extra_features': extra_features
                    }
            elif model_type == 'ndvi':
                is_valid, missing_cols = validate_ndvi_data(df)
                analysis['validation'] = {
                    'features_valid': is_valid,
                    'missing_columns': missing_cols
                }
            
            return jsonify({
                'success': True,
                'analysis': analysis,
                'model_type': model_type,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            app.logger.error(f"Data analysis error: {str(e)}")
            return jsonify({'success': False, 'message': str(e)}), 500

    @app.route('/validate/file', methods=['POST'])
    def validate_file():
        try:
            if 'file' not in request.files:
                return jsonify({'success': False, 'message': 'No file provided'}), 400
            
            file = request.files['file']
            model_type = request.form.get('model_type', 'classification')
            
            if not allowed_file(file.filename):
                return jsonify({'success': False, 'message': 'Invalid file type'}), 400
            
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            try:
                file_extension = filename.rsplit('.', 1)[1].lower()
                df = process_file(file_path, file_extension)
                
                validation_results = {
                    'file_valid': True,
                    'rows': len(df),
                    'columns': len(df.columns),
                    'column_names': df.columns.tolist(),
                    'model_type': model_type
                }
                
                if model_type == 'classification':
                    model_data = get_model_data()
                    if model_data:
                        is_valid, missing_features, extra_features = validate_features(df)
                        types_valid, invalid_columns = validate_data_types(df)
                        
                        validation_results.update({
                            'features_valid': is_valid,
                            'types_valid': types_valid,
                            'missing_features': missing_features,
                            'extra_features': extra_features,
                            'invalid_columns': invalid_columns,
                            'ready_for_prediction': is_valid and types_valid
                        })
                elif model_type == 'ndvi':
                    is_valid, missing_cols = validate_ndvi_data(df)
                    validation_results.update({
                        'features_valid': is_valid,
                        'missing_columns': missing_cols,
                        'ready_for_prediction': is_valid,
                        'max_years_ahead': 4
                    })
                
                return jsonify({
                    'success': True,
                    'validation': validation_results,
                    'timestamp': datetime.now().isoformat()
                })
                
            finally:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    
        except Exception as e:
            app.logger.error(f"File validation error: {str(e)}")
            return jsonify({'success': False, 'message': str(e)}), 500

    @app.route('/export/results', methods=['POST'])
    def export_results():
        try:
            data = request.get_json()
            if not data or 'predictions' not in data:
                return jsonify({'success': False, 'message': 'No predictions provided'}), 400
            
            predictions = data['predictions']
            export_format = data.get('format', 'csv').lower()
            model_type = data.get('model_type', 'classification')
            years_ahead = data.get('years_ahead', 1)
            
            if export_format == 'csv':
                if model_type == 'ndvi':
                    # Format spécifique pour NDVI multi-années
                    export_data = []
                    for pred in predictions:
                        if pred.get('success', False):
                            row = {
                                'row_id': pred.get('row_id', ''),
                                'years_predicted': pred.get('years_predicted', years_ahead)
                            }
                            
                            # Ajouter les valeurs historiques
                            if 'historical_values' in pred:
                                row.update(pred['historical_values'])
                            
                            # Ajouter les prédictions par année
                            if 'predictions_by_year' in pred:
                                for year, year_data in pred['predictions_by_year'].items():
                                    row[f'NDVI_{year}_prediction'] = year_data['prediction']
                                    row[f'NDVI_{year}_health_status'] = year_data['health_status']
                                    row[f'NDVI_{year}_confidence_lower'] = year_data['confidence_interval']['lower']
                                    row[f'NDVI_{year}_confidence_upper'] = year_data['confidence_interval']['upper']
                            
                            # Compatibilité avec format single year
                            elif 'prediction_2025' in pred:
                                row['NDVI_2025_prediction'] = pred['prediction_2025']
                                row['NDVI_2025_health_status'] = pred.get('health_status', '')
                                if 'confidence_interval' in pred:
                                    row['NDVI_2025_confidence_lower'] = pred['confidence_interval']['lower']
                                    row['NDVI_2025_confidence_upper'] = pred['confidence_interval']['upper']
                            
                            # Informations générales
                            row['trend'] = pred.get('trend', '')
                            row['overall_health_status'] = pred.get('overall_health_status', pred.get('health_status', ''))
                            row['average_prediction'] = pred.get('average_prediction', pred.get('prediction_2025', ''))
                            
                            export_data.append(row)
                    
                    df = pd.DataFrame(export_data)
                else:
                    # Format pour classification
                    df = pd.DataFrame(predictions)
                
                csv_content = df.to_csv(index=False)
                
                filename = f'{model_type}_predictions'
                if model_type == 'ndvi' and years_ahead > 1:
                    filename += f'_{years_ahead}years'
                filename += f'_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
                
                return send_file(
                    io.BytesIO(csv_content.encode()),
                    mimetype='text/csv',
                    as_attachment=True,
                    download_name=filename
                )
            
            elif export_format == 'json':
                export_data = {
                    'metadata': {
                        'model_type': model_type,
                        'years_ahead': years_ahead if model_type == 'ndvi' else 1,
                        'export_timestamp': datetime.now().isoformat(),
                        'total_predictions': len(predictions)
                    },
                    'predictions': predictions
                }
                
                json_content = json.dumps(export_data, indent=2)
                
                filename = f'{model_type}_predictions'
                if model_type == 'ndvi' and years_ahead > 1:
                    filename += f'_{years_ahead}years'
                filename += f'_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
                
                return send_file(
                    io.BytesIO(json_content.encode()),
                    mimetype='application/json',
                    as_attachment=True,
                    download_name=filename
                )
            
            else:
                return jsonify({'success': False, 'message': 'Unsupported export format'}), 400
                
        except Exception as e:
            app.logger.error(f"Export error: {str(e)}")
            return jsonify({'success': False, 'message': str(e)}), 500