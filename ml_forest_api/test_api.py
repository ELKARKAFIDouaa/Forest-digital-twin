import requests
import json
import pandas as pd
import numpy as np
import os
from datetime import datetime

BASE_URL = 'http://localhost:5000'
TIMEOUT = 30

def print_section(title):
    print(f"\n{'='*50}")
    print(f"TEST: {title}")
    print('='*50)

def test_health_check():
    try:
        response = requests.get(f'{BASE_URL}/', timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            print(f"API active: {data['message']}")
            print(f"Modèles chargés: {data['models_loaded']}")
            return True
        else:
            print(f"Erreur {response.status_code}: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print("Impossible de se connecter à l'API")
        return False
    except Exception as e:
        print(f"Erreur: {str(e)}")
        return False

def test_models_info():
    try:
        response = requests.get(f'{BASE_URL}/models/info', timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()['data']
            print(f"Classification: {data['classification']['available']}")
            print(f"Timeseries: {data['timeseries']['available']}")
            
            if data['classification']['available']:
                print(f"Modèles: {len(data['classification']['models'])}")
                print(f"Meilleur: {data['classification']['best_model']}")
            
            if data['timeseries']['available']:
                print(f"Régions: {len(data['timeseries']['regions'])}")
            
            return True
        else:
            print(f"Erreur {response.status_code}")
            return False
    except Exception as e:
        print(f"Erreur: {str(e)}")
        return False

def test_features_schema():
    try:
        response = requests.get(f'{BASE_URL}/features/schema', timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()['data']
            print(f"Features attendues: {data['expected_features']}")
            
            schema = data['schema']
            for section_name, section in schema.items():
                print(f"{section['title']}: {len(section['fields'])} champs")
            
            return True
        else:
            print(f"Erreur {response.status_code}")
            return False
    except Exception as e:
        print(f"Erreur: {str(e)}")
        return False

def test_classification_predict():
    sample_data = {
        'NDVI_2024': 0.65,
        'NDVI_2023': 0.68,
        'NDVI_2022': 0.62,
        'NDVI_2021': 0.70,
        'NDVI_2020': 0.66,
        'EVI_2024': 0.45,
        'EVI_2023': 0.48,
        'EVI_2022': 0.42,
        'NDMI_2024': 0.45,
        'NDMI_2023': 0.48,
        'NDMI_2022': 0.42,
        'NBR_2024': 0.38,
        'NBR_2023': 0.41,
        'NBR_2022': 0.35,
        'elevation': 850.2,
        'slope': 12.5,
        'aspect': 180.0,
        'precipitation_sum_2024': 150.3,
        'precipitation_sum_2023': 140.5,
        'temperature_mean_2024': 22.5,
        'temperature_mean_2023': 21.8,
        'temperature_min_2024': 15.2,
        'temperature_max_2024': 29.8,
        'forest_health_composite': 0.72,
        'vegetation_vigor': 0.68,
        'water_stress_index': 0.35,
        'recovery_potential': 0.75,
        'LAI_2024': 2.1,
        'FAPAR_2024': 0.68,
        'GPP_2024': 1.5,
        'soil_moisture_2024': 0.45,
        'canopy_cover_2024': 0.78,
        'feature_32': 0.5,
        'feature_33': 0.6,
        'feature_34': 0.7,
        'feature_35': 0.8,
        'feature_36': 0.4,
        'feature_37': 0.3,
        'feature_38': 0.9,
        'feature_39': 0.2,
        'feature_40': 0.1,
        'feature_41': 0.5,
        'feature_42': 0.6,
        'feature_43': 0.7,
        'feature_44': 0.8,
        'feature_45': 0.4,
        'feature_46': 0.3,
        'feature_47': 0.9,
        'feature_48': 0.2,
        'feature_49': 0.1
    }
    
    try:
        response = requests.post(
            f'{BASE_URL}/classification/predict',
            json=sample_data,
            headers={'Content-Type': 'application/json'},
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()['data']
            pred = data['predictions'][0]
            print(f"Classe: {pred['class_name']}")
            print(f"Confiance: {pred['confidence']}%")
            print(f"Modèle: {data['model_used']}")
            return True
        else:
            print(f"Erreur {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"Erreur: {str(e)}")
        return False

def test_timeseries_predict():
    sample_data = {
        'region': 'COMBINED',
        'ndvi_values': [0.65, 0.68, 0.62, 0.70, 0.66, 0.63],
        'n_periods': 3
    }
    
    try:
        response = requests.post(
            f'{BASE_URL}/timeseries/predict',
            json=sample_data,
            headers={'Content-Type': 'application/json'},
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()['data']
            print(f"Région: {data['region']}")
            print(f"Modèle: {data['model_used']}")
            print(f"Méthode: {data['method_used']}")
            
            summary = data['summary']
            print(f"NDVI prédit: {summary['predicted_ndvi']}")
            print(f"Statut: {summary['health_status']}")
            print(f"Tendance: {summary['trend']} ({summary['variation_percent']:+.1f}%)")
            
            return True
        else:
            print(f"Erreur {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"Erreur: {str(e)}")
        return False

def test_csv_upload():
    test_data = {
        'NDVI_2024': [0.65, 0.60, 0.75],
        'NDVI_2023': [0.68, 0.63, 0.78],
        'NDVI_2022': [0.62, 0.58, 0.72],
        'NDVI_2021': [0.70, 0.65, 0.76],
        'NDVI_2020': [0.66, 0.61, 0.74],
        'EVI_2024': [0.45, 0.42, 0.48],
        'EVI_2023': [0.48, 0.44, 0.51],
        'EVI_2022': [0.42, 0.39, 0.45],
        'NDMI_2024': [0.45, 0.42, 0.48],
        'NDMI_2023': [0.48, 0.44, 0.51],
        'NDMI_2022': [0.42, 0.39, 0.45],
        'NBR_2024': [0.38, 0.35, 0.41],
        'NBR_2023': [0.41, 0.37, 0.44],
        'NBR_2022': [0.35, 0.32, 0.38],
        'elevation': [850.2, 1200.5, 450.0],
        'slope': [12.5, 18.3, 8.7],
        'aspect': [180.0, 225.0, 135.0],
        'precipitation_sum_2024': [150.3, 180.7, 120.4],
        'precipitation_sum_2023': [140.5, 170.2, 110.8],
        'temperature_mean_2024': [22.5, 18.2, 25.1],
        'temperature_mean_2023': [21.8, 17.5, 24.6]
    }
    
    df = pd.DataFrame(test_data)
    
    for i in range(22, 50):
        df[f'feature_{i}'] = np.random.uniform(0.1, 0.9, 3)
    
    csv_filename = 'test_data.csv'
    df.to_csv(csv_filename, index=False)
    
    try:
        with open(csv_filename, 'rb') as f:
            files = {'file': (csv_filename, f, 'text/csv')}
            data = {'type': 'classification'}
            
            response = requests.post(
                f'{BASE_URL}/upload/csv',
                files=files,
                data=data,
                timeout=TIMEOUT
            )
        
        if response.status_code == 200:
            data = response.json()['data']
            print(f"Fichier: {data['filename']}")
            print(f"Lignes: {data['total_rows']}")
            print(f"Réussites: {data['successful_predictions']}")
            print(f"Erreurs: {data['failed_predictions']}")
            
            if data['results']:
                result = data['results'][0]
                print(f"Premier résultat: {result['class_name']} ({result['confidence']}%)")
            
            return True
        else:
            print(f"Erreur {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"Erreur: {str(e)}")
        return False
    finally:
        if os.path.exists(csv_filename):
            os.remove(csv_filename)

def run_all_tests():
    print("TESTS API ML FORESTIÈRE")
    print(f"Début: {datetime.now().strftime('%H:%M:%S')}")
    print(f"URL: {BASE_URL}")
    
    tests = [
        ("Health Check", test_health_check),
        ("Modèles Info", test_models_info),
        ("Features Schema", test_features_schema),
        ("Classification", test_classification_predict),
        ("Timeseries", test_timeseries_predict),
        ("Upload CSV", test_csv_upload)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print_section(test_name)
        try:
            success = test_func()
            results.append((test_name, success))
            print(f"Résultat: {'PASSÉ' if success else 'ÉCHOUÉ'}")
        except Exception as e:
            print(f"Erreur: {str(e)}")
            results.append((test_name, False))
    
    print_section("RÉSUMÉ")
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"Tests passés: {passed}/{total}")
    
    for test_name, success in results:
        status = "PASSÉ" if success else "ÉCHOUÉ"
        print(f"{test_name}: {status}")
    
    if passed == total:
        print("\nTOUS LES TESTS SONT PASSÉS")
    else:
        print(f"\n{total - passed} test(s) ont échoué")
    
    print(f"\nTerminé: {datetime.now().strftime('%H:%M:%S')}")

if __name__ == '__main__':
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\nTests interrompus")
    except Exception as e:
        print(f"\n\nErreur: {str(e)}")