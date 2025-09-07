
# RAPPORT D'ANALYSE - MODÉLISATION NDVI COMBINÉE
## Date: 2025-09-01 21:12:29

### 🌍 DONNÉES ANALYSÉES
- **Régions individuelles**: 5
- **Locations totales**: 2397
- **Observations totales**: 11985
- **Période**: 2020-2024

### 🏆 MEILLEURS MODÈLES PAR RÉGION
- **argan**: Prophet (RMSE: 0.0096, R²: nan)
- **haut**: ExpSmoothing (RMSE: 0.0009, R²: nan)
- **mamora**: ARIMA (RMSE: 0.0144, R²: nan)
- **moyen**: ExpSmoothing (RMSE: 0.0007, R²: nan)
- **rif**: SARIMA (RMSE: 0.0038, R²: nan)
- **COMBINED**: Prophet (RMSE: 0.0031, R²: nan)

### 🌍 MODÈLE COMBINÉ (TOUTES RÉGIONS)
- **Meilleur modèle**: Prophet
- **Performance**:
  - MAE: 0.0031
  - MSE: 0.0000
  - RMSE: 0.0031
  - R2: nan
  - MAPE: 1.2192

### 📊 CLASSEMENT GLOBAL DES MODÈLES
1. **SARIMA** - RMSE moyen: 0.0088
2. **ARIMA** - RMSE moyen: 0.0101
3. **ExpSmoothing** - RMSE moyen: 0.0146
4. **Prophet** - RMSE moyen: 0.0687

### 💡 RECOMMANDATIONS
1. **Pour une approche globale**: Utiliser le modèle Prophet
2. **Pour une approche régionale**: Adapter selon la région spécifique
3. **Surveillance continue**: Réévaluer les modèles avec de nouvelles données

### 📁 FICHIERS GÉNÉRÉS
- `results_summary_combined.csv`: Résultats détaillés
- `combined_model_results.csv`: Résultats spécifiques au modèle combiné
- `*.png`: Visualisations
- `saved_combined_timeseries_models/`: Modèles entraînés
