# Projet ML Flask API

## Description
Ce projet implémente une solution complète de machine learning avec une API Flask pour l'analyse de données géospatiales collectées depuis Google Earth Engine. Le système inclut des modèles de classification et d'analyse de séries temporelles avec une interface web pour la visualisation des résultats.

## Structure du Projet

```
ml_flask_api/
├── app.py                    # API Flask principale
├── test_api.py              # Tests de l'API
├── interface.html           # Interface de visualisation web
└── Data And Model/
    ├── Documentation_Data.pdf    # Documentation des données GEE
    ├── Des Fichers CSVs            # Données collectées depuis Google Earth Engine
    └── Prediction Model.ipynb         # Implémentation des modèles ML
```

## Composants Principaux

### Data And Model/
Ce dossier contient tous les éléments liés aux données et aux modèles :

- **Données** : Collectées depuis Google Earth Engine
- **Documentation** : Le fichier `Documentation_Data.pdf` contient toutes les informations détaillées sur les données utilisées
- **Notebook** : Implémentation des modèles de machine learning
  - Modèles de classification
  - Modèles d'analyse de séries temporelles

### API Flask (app.py)
L'API principale qui permet l'intégration des modèles dans l'application :

- **Fonctionnalité** : Intégration des modèles ML dans l'application principale
- **Options de chargement des données** :
  - Chargement manuel des données pré-traitées
  - Upload et traitement de fichiers CSV
- **Endpoints** : API RESTful pour l'interaction avec les modèles

### Tests (test_api.py)
Script de test pour valider le fonctionnement de l'API.

**Important** : L'API (`app.py`) doit être en cours d'exécution avant de lancer les tests.

### Interface (interface.html)
Interface web pour visualiser les résultats de l'API de manière interactive.

## Installation et Utilisation


### Lancement du Projet

1. **Démarrer l'API** :
   ```bash
   python app.py
   ```

2. **Tester l'API** (dans un nouveau terminal) :
   ```bash
   python test_api.py
   ```

3. **Accéder à l'interface** :
   Ouvrir `interface.html` dans un navigateur web

## Endpoints API

### Endpoints Principaux

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/` | GET | État de santé de l'API et informations générales |
| `/interface` | GET | Interface web pour visualiser les résultats |
| `/classification/predict` | POST | Prédiction de classification (santé forestière) |
| `/timeseries/predict` | POST | Prédiction de séries temporelles (NDVI futur) |
| `/upload/csv` | POST | Upload et traitement de fichiers CSV |

### Endpoints d'Information

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/models/info` | GET | Informations sur les modèles chargés |
| `/features/schema` | GET | Schéma des features attendues |
| `/debug/features` | GET | Informations de debug sur les features |

## Tests et Exemples d'Utilisation

### 1. Test Automatisé
Le fichier `test_api.py` contient les tests unitaires pour valider le fonctionnement de l'API.

```bash
# Assurez-vous que app.py est en cours d'exécution
python test_api.py
```

### 2. Tests Manuels avec cURL

#### Vérifier l'état de l'API
```bash
curl -X GET http://127.0.0.1:5000/
```

#### Test de Classification
```bash
curl -X POST http://127.0.0.1:5000/classification/predict \
  -H "Content-Type: application/json" \
  -d '{
    "NDVI_2024": 0.65,
    "NDVI_2023": 0.62,
    "EVI_2024": 0.58,
    "elevation": 800,
    "slope": 15,
    "precipitation_sum_2024": 600,
    "temperature_mean_2024": 20
  }'
```

#### Test de Série Temporelle
```bash
curl -X POST http://127.0.0.1:5000/timeseries/predict \
  -H "Content-Type: application/json" \
  -d '{
    "ndvi_values": [0.45, 0.52, 0.58, 0.62, 0.65],
    "region": "argan",
    "n_periods": 2
  }'
```

#### Informations sur les Modèles
```bash
curl -X GET http://127.0.0.1:5000/models/info
```

#### Schéma des Features
```bash
curl -X GET http://127.0.0.1:5000/features/schema
```

### 3. Test Upload CSV

#### Préparer un fichier CSV de test
Créez un fichier `test_classification.csv` :
```csv
NDVI_2024,NDVI_2023,EVI_2024,elevation,slope,precipitation_sum_2024,temperature_mean_2024
0.65,0.62,0.58,800,15,600,20
0.45,0.48,0.42,1200,25,800,18
0.75,0.72,0.68,600,10,900,22
```

#### Upload et Test
```bash
curl -X POST http://127.0.0.1:5000/upload/csv \
  -F "file=@test_classification.csv" \
  -F "type=classification"
```

### 4. Interface Web
Accédez à l'interface interactive via votre navigateur :
```
http://127.0.0.1:5000/interface
```

### URLs de Test Rapide

Une fois l'API lancée (`python app.py`), testez ces URLs dans votre navigateur :

- **État de l'API** : http://127.0.0.1:5000/
- **Interface Web** : http://127.0.0.1:5000/interface
- **Info Modèles** : http://127.0.0.1:5000/models/info
- **Schéma Features** : http://127.0.0.1:5000/features/schema
- **Debug Features** : http://127.0.0.1:5000/debug/features

**Important** : L'API doit être en cours d'exécution (`python app.py`) avant de lancer les tests.

## Données

### Source
Toutes les données proviennent de **Google Earth Engine** et sont optimisées pour :
- L'analyse de classification
- L'analyse de séries temporelles

### Documentation
Pour des informations complètes sur les données (métadonnées, format, structure), consultez le fichier `Documentation_Data.pdf` dans le dossier `Data And Model/`.

## Modèles Implémentés

Le notebook dans `Data And Model/` contient l'implémentation de :

1. **Modèles de Classification** : Pour la catégorisation des données géospatiales
2. **Modèles de Séries Temporelles** : Pour l'analyse des tendances temporelles

## Chargement des Données

L'API supporte deux méthodes de chargement :

### Option 1 : Chargement Manuel
Utilisation directe des données pré-traitées depuis Google Earth Engine.

### Option 2 : Upload CSV
Upload de nouveaux fichiers CSV via l'interface pour un traitement personnalisé.

## Workflow Recommandé

1. Consulter `Documentation_Data.pdf` pour comprendre les données
2. Explorer le notebook dans `Data And Model/` pour comprendre les modèles
3. Lancer `app.py` pour démarrer l'API
4. Utiliser `test_api.py` pour valider le fonctionnement
5. Utiliser `interface.html` pour visualiser les résultats

## Configuration

### Dossiers
- `uploads/` : Fichiers CSV temporaires
- `saved_models/` : Modèles de classification sauvegardés
- `saved_combined_timeseries_models/` : Modèles de séries temporelles
- `logs/` : Fichiers de logs

### Paramètres API
- **Port** : 5000
- **Host** : 127.0.0.1
- **Limite upload** : 16MB
- **Format logs** : Fichier `api.log` + console

## Gestion des Erreurs

L'API gère automatiquement :
- Fichiers CSV malformés
- Données manquantes
- Erreurs de modèles
- Limites de taille de fichier
- Endpoints inexistants

## Support

- **Documentation des données** : `Data And Model/Documentation_Data.pdf`
- **Implémentation des modèles** : Notebook dans `Data And Model/`
- **Tests** : Utiliser `test_api.py` pour validation
- **Logs** : Consulter `api.log` pour le débogage

---

**Note** : Ce projet utilise des données provenant de Google Earth Engine. Assurez-vous d'avoir les autorisations nécessaires pour leur utilisation.