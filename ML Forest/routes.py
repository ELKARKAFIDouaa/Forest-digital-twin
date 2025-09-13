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
    allowed_file, validate_features, validate_data_types,
    process_file, prepare_data, make_predictions,
    calculate_statistics, generate_recommendations
)

def register_routes(app):
    
    @app.route('/')
    def index():
        # Fix: Specify UTF-8 encoding when reading the HTML file
        with open('templates/index.html', 'r', encoding='utf-8') as f:
            return render_template_string(f.read())
    
    @app.route('/health', methods=['GET'])
    def health_check():
        model_data = get_model_data()
        all_features = get_all_features()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'model_loaded': model_data is not None,
            'model_name': model_data['best_model_name'] if model_data else None,
            'features_count': len(all_features) if all_features else 0
        })

    @app.route('/model/info', methods=['GET'])
    def model_info():
        model_data = get_model_data()
        all_features = get_all_features()
        selected_features = get_selected_features()
        
        if model_data is None:
            return jsonify({'success': False, 'message': 'Model not loaded'}), 500
        
        return jsonify({
            'success': True,
            'model_name': model_data['best_model_name'],
            'all_features': all_features,
            'selected_features': selected_features,
            'classes': model_data['label_encoder'].classes_.tolist(),
            'total_features_count': len(all_features),
            'selected_features_count': len(selected_features)
        })

    @app.route('/model/template', methods=['GET'])
    def get_template():
        model_data = get_model_data()
        all_features = get_all_features()
        
        if model_data is None:
            return jsonify({'success': False, 'message': 'Model not loaded'}), 500
        
        template_data = {feature: 0.0 for feature in all_features}
        
        return jsonify({
            'success': True,
            'all_features': all_features,
            'template': template_data
        })

    @app.route('/model/template/download', methods=['GET'])
    def download_template():
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

    @app.route('/predict/single', methods=['POST'])
    def predict_single():
        try:
            model_data = get_model_data()
            all_features = get_all_features()
            
            if model_data is None:
                return jsonify({'success': False, 'message': 'Model not loaded'}), 500
            
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'message': 'No data provided'}), 400
            
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
                'prediction': predictions[0],
                'model_used': model_data['best_model_name'],
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            app.logger.error(f"Single prediction error: {str(e)}")
            return jsonify({'success': False, 'message': str(e)}), 500

    @app.route('/predict/batch', methods=['POST'])
    def predict_batch():
        try:
            model_data = get_model_data()
            
            if model_data is None:
                return jsonify({'success': False, 'message': 'Model not loaded'}), 500
            
            data = request.get_json()
            if not data or 'data' not in data:
                return jsonify({'success': False, 'message': 'No data provided'}), 400
            
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
            recommendations = generate_recommendations(statistics)
            
            return jsonify({
                'success': True,
                'predictions': predictions,
                'statistics': statistics,
                'recommendations': recommendations,
                'model_used': model_data['best_model_name'],
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            app.logger.error(f"Batch prediction error: {str(e)}")
            return jsonify({'success': False, 'message': str(e)}), 500

    @app.route('/predict/file', methods=['POST'])
    def predict_file():
        try:
            model_data = get_model_data()
            
            if model_data is None:
                return jsonify({'success': False, 'message': 'Model not loaded'}), 500
            
            if 'file' not in request.files:
                return jsonify({'success': False, 'message': 'No file provided'}), 400
            
            file = request.files['file']
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
                recommendations = generate_recommendations(statistics)
                
                file_info = {
                    'filename': file.filename,
                    'rows': len(df),
                    'columns': len(df.columns),
                    'file_size': os.path.getsize(file_path)
                }
                
                return jsonify({
                    'success': True,
                    'predictions': predictions,
                    'statistics': statistics,
                    'recommendations': recommendations,
                    'file_info': file_info,
                    'model_used': model_data['best_model_name'],
                    'timestamp': datetime.now().isoformat()
                })
                
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
            all_features = get_all_features()
            
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
            
            if all_features:
                is_valid, missing_features, extra_features = validate_features(df)
                analysis['validation'] = {
                    'features_valid': is_valid,
                    'missing_features': missing_features,
                    'extra_features': extra_features
                }
            
            return jsonify({
                'success': True,
                'analysis': analysis,
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
                model_data = get_model_data()
                
                validation_results = {
                    'file_valid': True,
                    'rows': len(df),
                    'columns': len(df.columns),
                    'column_names': df.columns.tolist()
                }
                
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
            
            if export_format == 'csv':
                df = pd.DataFrame(predictions)
                csv_content = df.to_csv(index=False)
                
                return send_file(
                    io.BytesIO(csv_content.encode()),
                    mimetype='text/csv',
                    as_attachment=True,
                    download_name=f'forest_health_predictions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
                )
            
            elif export_format == 'json':
                json_content = json.dumps(predictions, indent=2)
                
                return send_file(
                    io.BytesIO(json_content.encode()),
                    mimetype='application/json',
                    as_attachment=True,
                    download_name=f'forest_health_predictions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
                )
            
            else:
                return jsonify({'success': False, 'message': 'Unsupported export format'}), 400
                
        except Exception as e:
            app.logger.error(f"Export error: {str(e)}")
            return jsonify({'success': False, 'message': str(e)}), 500