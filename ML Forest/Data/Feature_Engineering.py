import pandas as pd
import numpy as np
import warnings
from sklearn.preprocessing import StandardScaler, MinMaxScaler, PolynomialFeatures
from sklearn.decomposition import PCA
from scipy import stats
from scipy.spatial.distance import pdist, squareform
import math

warnings.filterwarnings('ignore')

class ForestFeatureEngineer:
    """Création de nouvelles features pour Forest Digital Twin Dataset"""
    
    def __init__(self, df):
        self.df = df.copy()
        self.original_shape = df.shape
        self.new_features = []
        self.feature_categories = {
            'spectral': [],
            'temporal': [],
            'topographic': [],
            'ecological': [],
            'composite': [],
            'geospatial': [],
            'interaction': [],
            'ml_ready': []
        }
        
        print("Feature Engineer initialisé")
        print(f"Dataset initial: {self.df.shape[0]:,} points × {self.df.shape[1]} features")

    # ============= ÉTAPE 1: FEATURES SPECTRALES =============
    def create_spectral_features(self):
        """ÉTAPE 1: Création de features spectrales avancées"""
        print("\n" + "="*70)
        print("ETAPE 1: CREATION DE FEATURES SPECTRALES")
        print("="*70)
        
        initial_count = len(self.df.columns)
        
        # 1.1 Ratios spectraux de base
        self._create_basic_spectral_ratios()
        
        # 1.2 Indices Red Edge avancés
        self._create_red_edge_features()
        
        # 1.3 Indices de texture spectrale
        self._create_spectral_texture_features()
        
        # 1.4 Transformations spectrales
        self._create_spectral_transformations()
        
        # 1.5 Indices custom pour forêts
        self._create_forest_specific_indices()
        
        final_count = len(self.df.columns)
        created = final_count - initial_count
        print(f"\n{created} features spectrales créées")
        
        return created

    def _create_basic_spectral_ratios(self):
        """Ratios spectraux fondamentaux"""
        print("\n1.1 Ratios spectraux de base:")
        
        spectral_ratios = [
            ('B8', 'B4', 'NIR_Red_ratio', 'Ratio Proche IR / Rouge'),
            ('B11', 'B8', 'SWIR1_NIR_ratio', 'Ratio SWIR1 / NIR'),
            ('B12', 'B11', 'SWIR2_SWIR1_ratio', 'Ratio SWIR2 / SWIR1'),
            ('B8', 'B3', 'NIR_Green_ratio', 'Ratio NIR / Vert'),
            ('B4', 'B3', 'Red_Green_ratio', 'Ratio Rouge / Vert'),
            ('B5', 'B4', 'RedEdge_Red_ratio', 'Ratio Red Edge / Rouge'),
            ('B6', 'B5', 'RedEdge2_RedEdge1_ratio', 'Ratio Red Edge interne'),
            ('B8A', 'B8', 'NIR_Narrow_Wide_ratio', 'Ratio NIR étroit/large')
        ]
        
        created = 0
        for band1, band2, feature_name, description in spectral_ratios:
            if band1 in self.df.columns and band2 in self.df.columns:
                self.df[feature_name] = self.df[band1] / (self.df[band2] + 0.0001)
                self.feature_categories['spectral'].append(feature_name)
                self.new_features.append(feature_name)
                created += 1
                print(f"   {feature_name}: {description}")
        
        print(f"   Créés: {created}/8 ratios")

    def _create_red_edge_features(self):
        """Features Red Edge avancées pour détection stress précoce"""
        print("\n1.2 Features Red Edge avancées:")
        
        created = 0
        
        # Red Edge Position (REP)
        if all(band in self.df.columns for band in ['B5', 'B6', 'B7']):
            # Position du Red Edge (approximation linéaire)
            self.df['red_edge_position'] = 705 + 35 * ((self.df['B7'] - self.df['B5']) / 
                                                      (self.df['B6'] - self.df['B5'] + 0.0001))
            
            # Amplitude Red Edge
            self.df['red_edge_amplitude'] = self.df['B6'] - (self.df['B4'] + self.df['B7']) / 2
            
            # Pente Red Edge
            self.df['red_edge_slope'] = (self.df['B7'] - self.df['B5']) / (783 - 705)
            
            # Asymétrie Red Edge
            self.df['red_edge_asymmetry'] = (self.df['B6'] - self.df['B5']) / (self.df['B7'] - self.df['B6'] + 0.0001)
            
            created += 4
            for feature in ['red_edge_position', 'red_edge_amplitude', 'red_edge_slope', 'red_edge_asymmetry']:
                self.feature_categories['spectral'].append(feature)
                self.new_features.append(feature)
            
            print("   Red Edge features: position, amplitude, pente, asymétrie")
        
        # Normalized Red Edge indices
        if all(band in self.df.columns for band in ['B5', 'B6', 'B8A']):
            # IRECI (Inverted Red Edge Chlorophyll Index)
            self.df['IRECI'] = (self.df['B7'] - self.df['B4']) / (self.df['B5'] / self.df['B6'])
            
            # S2REP (Sentinel-2 Red Edge Position)
            self.df['S2REP'] = 705 + 35 * ((((self.df['B4'] + self.df['B7']) / 2) - self.df['B5']) / 
                                          (self.df['B6'] - self.df['B5'] + 0.0001))
            
            created += 2
            for feature in ['IRECI', 'S2REP']:
                self.feature_categories['spectral'].append(feature)
                self.new_features.append(feature)
            
            print("   Indices Red Edge normalisés: IRECI, S2REP")
        
        print(f"   Créés: {created} features Red Edge")

    def _create_spectral_texture_features(self):
        """Features de texture spectrale"""
        print("\n1.3 Features de texture spectrale:")
        
        created = 0
        
        # Brightness, Greenness, Wetness (Tasseled Cap-like)
        if all(band in self.df.columns for band in ['B2', 'B3', 'B4', 'B8', 'B11', 'B12']):
            # Brightness (luminosité)
            self.df['brightness'] = (0.3037 * self.df['B2'] + 0.2793 * self.df['B3'] + 
                                   0.4743 * self.df['B4'] + 0.5585 * self.df['B8'] + 
                                   0.5082 * self.df['B11'] + 0.1863 * self.df['B12'])
            
            # Greenness (verdeur)
            self.df['greenness'] = (-0.2848 * self.df['B2'] - 0.2435 * self.df['B3'] - 
                                  0.5436 * self.df['B4'] + 0.7243 * self.df['B8'] + 
                                  0.0840 * self.df['B11'] - 0.1800 * self.df['B12'])
            
            # Wetness (humidité)
            self.df['wetness'] = (0.1509 * self.df['B2'] + 0.1973 * self.df['B3'] + 
                                0.3279 * self.df['B4'] + 0.3406 * self.df['B8'] - 
                                0.7112 * self.df['B11'] - 0.4572 * self.df['B12'])
            
            created += 3
            for feature in ['brightness', 'greenness', 'wetness']:
                self.feature_categories['spectral'].append(feature)
                self.new_features.append(feature)
            
            print("   Tasseled Cap: brightness, greenness, wetness")
        
        # Indices de diversité spectrale
        visible_bands = [col for col in ['B2', 'B3', 'B4'] if col in self.df.columns]
        if len(visible_bands) >= 2:
            # Diversité dans le visible
            visible_data = self.df[visible_bands]
            self.df['visible_diversity'] = visible_data.std(axis=1) / (visible_data.mean(axis=1) + 0.0001)
            
            created += 1
            self.feature_categories['spectral'].append('visible_diversity')
            self.new_features.append('visible_diversity')
            print("   Diversité spectrale visible")
        
        # Contraste spectral
        if all(band in self.df.columns for band in ['B2', 'B12']):
            self.df['spectral_contrast'] = (self.df['B12'] - self.df['B2']) / (self.df['B12'] + self.df['B2'] + 0.0001)
            created += 1
            self.feature_categories['spectral'].append('spectral_contrast')
            self.new_features.append('spectral_contrast')
            print("   Contraste spectral B12-B2")
        
        print(f"   Créés: {created} features de texture")

    def _create_spectral_transformations(self):
        """Transformations mathématiques des bandes"""
        print("\n1.4 Transformations spectrales:")
        
        created = 0
        spectral_bands = [col for col in self.df.columns if col.startswith('B') and len(col) <= 4]
        
        if len(spectral_bands) >= 3:
            # PCA des bandes spectrales
            spectral_data = self.df[spectral_bands].fillna(self.df[spectral_bands].mean())
            
            if spectral_data.shape[1] >= 3:
                pca = PCA(n_components=3)
                pca_result = pca.fit_transform(spectral_data)
                
                self.df['spectral_PC1'] = pca_result[:, 0]
                self.df['spectral_PC2'] = pca_result[:, 1] 
                self.df['spectral_PC3'] = pca_result[:, 2]
                
                # Variance expliquée
                explained_var = pca.explained_variance_ratio_
                
                created += 3
                for i, feature in enumerate(['spectral_PC1', 'spectral_PC2', 'spectral_PC3']):
                    self.feature_categories['spectral'].append(feature)
                    self.new_features.append(feature)
                
                print(f"   PCA spectrale: PC1 ({explained_var[0]:.1%}), PC2 ({explained_var[1]:.1%}), PC3 ({explained_var[2]:.1%})")
        
        # Transformations logarithmiques pour bandes SWIR
        swir_bands = ['B11', 'B12']
        for band in swir_bands:
            if band in self.df.columns:
                log_feature = f'{band}_log'
                self.df[log_feature] = np.log1p(self.df[band])  # log(1+x) pour éviter log(0)
                created += 1
                self.feature_categories['spectral'].append(log_feature)
                self.new_features.append(log_feature)
                print(f"   Transformation log: {log_feature}")
        
        print(f"   Créés: {created} transformations")

    def _create_forest_specific_indices(self):
        """Indices spécialisés pour les forêts"""
        print("\n1.5 Indices forestiers spécialisés:")
        
        created = 0
        
        # Forest Canopy Density Index
        if all(band in self.df.columns for band in ['B8', 'B4', 'B11']):
            self.df['forest_canopy_density'] = ((self.df['B8'] - self.df['B4']) / 
                                               (self.df['B8'] + self.df['B4'] + 0.0001)) * \
                                              (1 - self.df['B11'] / (self.df['B8'] + 0.0001))
            created += 1
            self.feature_categories['spectral'].append('forest_canopy_density')
            self.new_features.append('forest_canopy_density')
            print("   Forest Canopy Density Index")
        
        # Leaf Area Index approximation
        if 'NDVI' in self.df.columns:
            # LAI approximation basée sur NDVI
            self.df['LAI_approx'] = 3.618 * (self.df['NDVI'] ** 2.169)
            self.df['LAI_approx'] = self.df['LAI_approx'].clip(0, 8)  # LAI réaliste 0-8
            
            created += 1
            self.feature_categories['spectral'].append('LAI_approx')
            self.new_features.append('LAI_approx')
            print("   Leaf Area Index approximation")
        
        # Canopy Water Content
        if all(band in self.df.columns for band in ['B8A', 'B11']):
            self.df['canopy_water_content'] = (self.df['B8A'] - self.df['B11']) / (self.df['B8A'] + self.df['B11'] + 0.0001)
            created += 1
            self.feature_categories['spectral'].append('canopy_water_content')
            self.new_features.append('canopy_water_content')
            print("   Canopy Water Content")
        
        # Anthocyanin Reflectance Index (stress automnal)
        if all(band in self.df.columns for band in ['B3', 'B5']):
            self.df['anthocyanin_index'] = (1 / self.df['B3']) - (1 / self.df['B5'])
            created += 1
            self.feature_categories['spectral'].append('anthocyanin_index')
            self.new_features.append('anthocyanin_index')
            print("   Anthocyanin Reflectance Index")
        
        print(f"   Créés: {created} indices forestiers")

    # ============= ÉTAPE 2: FEATURES TEMPORELLES =============
    def create_temporal_features(self):
        """ÉTAPE 2: Création de features temporelles"""
        print("\n" + "="*70)
        print("ETAPE 2: CREATION DE FEATURES TEMPORELLES")
        print("="*70)
        
        initial_count = len(self.df.columns)
        
        # 2.1 Détection des séries temporelles
        temporal_cols = self._detect_temporal_columns()
        
        if not temporal_cols:
            print("Aucune série temporelle détectée")
            return 0
        
        print(f"Séries temporelles détectées: {len(temporal_cols)}")
        for col in temporal_cols:
            print(f"   • {col}")
        
        # 2.2 Features de tendance
        self._create_trend_features(temporal_cols)
        
        # 2.3 Features de variabilité
        self._create_variability_features(temporal_cols)
        
        # 2.4 Features de saisonnalité
        self._create_seasonality_features(temporal_cols)
        
        # 2.5 Features d'événements
        self._create_event_features(temporal_cols)
        
        # 2.6 Features de résilience
        self._create_resilience_features(temporal_cols)
        
        final_count = len(self.df.columns)
        created = final_count - initial_count
        print(f"\n{created} features temporelles créées")
        
        return created

    def _detect_temporal_columns(self):
        """Détecter les colonnes temporelles NDVI"""
        temporal_patterns = ['ndvi_202', 'NDVI_202', '_regional_avg']
        temporal_cols = []
        
        for col in self.df.columns:
            if any(pattern in col for pattern in temporal_patterns):
                temporal_cols.append(col)
        
        # Trier par année
        temporal_cols.sort(key=lambda x: ''.join([c for c in x if c.isdigit()]))
        return temporal_cols

    def _create_trend_features(self, temporal_cols):
        """Features de tendance temporelle"""
        print("\n2.1 Features de tendance:")
        
        if len(temporal_cols) < 2:
            print("   Pas assez de données pour calculer les tendances")
            return
        
        created = 0
        
        # Tendance linéaire globale
        first_year = self.df[temporal_cols[0]]
        last_year = self.df[temporal_cols[-1]]
        n_years = len(temporal_cols)
        
        self.df['ndvi_linear_trend'] = (last_year - first_year) / (n_years - 1)
        
        # Tendance en pourcentage
        self.df['ndvi_trend_percent'] = ((last_year - first_year) / (first_year + 0.0001)) * 100
        
        # Direction de la tendance
        self.df['trend_direction'] = np.where(self.df['ndvi_linear_trend'] > 0.01, 'Positive',
                                    np.where(self.df['ndvi_linear_trend'] < -0.01, 'Negative', 'Stable'))
        
        created += 3
        for feature in ['ndvi_linear_trend', 'ndvi_trend_percent', 'trend_direction']:
            self.feature_categories['temporal'].append(feature)
            self.new_features.append(feature)
        
        # Régression linéaire robuste
        if len(temporal_cols) >= 3:
            years = np.arange(len(temporal_cols))
            
            def calculate_slope(row):
                values = row[temporal_cols].values
                if np.isnan(values).sum() < len(values) * 0.5:  # Moins de 50% de NaN
                    valid_idx = ~np.isnan(values)
                    if valid_idx.sum() >= 2:
                        slope, _, _, _, _ = stats.linregress(years[valid_idx], values[valid_idx])
                        return slope
                return np.nan
            
            self.df['ndvi_robust_slope'] = self.df.apply(calculate_slope, axis=1)
            
            # R² de la tendance
            def calculate_r2(row):
                values = row[temporal_cols].values
                if np.isnan(values).sum() < len(values) * 0.5:
                    valid_idx = ~np.isnan(values)
                    if valid_idx.sum() >= 2:
                        _, _, r_value, _, _ = stats.linregress(years[valid_idx], values[valid_idx])
                        return r_value ** 2
                return np.nan
            
            self.df['ndvi_trend_r2'] = self.df.apply(calculate_r2, axis=1)
            
            created += 2
            for feature in ['ndvi_robust_slope', 'ndvi_trend_r2']:
                self.feature_categories['temporal'].append(feature)
                self.new_features.append(feature)
        
        print(f"   Créées: {created} features de tendance")

    def _create_variability_features(self, temporal_cols):
        """Features de variabilité temporelle"""
        print("\n2.2 Features de variabilité:")
        
        created = 0
        
        # Variabilité de base
        temporal_data = self.df[temporal_cols]
        
        # Écart-type temporel
        self.df['ndvi_temporal_std'] = temporal_data.std(axis=1)
        
        # Coefficient de variation
        self.df['ndvi_temporal_cv'] = temporal_data.std(axis=1) / (temporal_data.mean(axis=1) + 0.0001)
        
        # Range (étendue)
        self.df['ndvi_temporal_range'] = temporal_data.max(axis=1) - temporal_data.min(axis=1)
        
        # Stabilité (inverse de la variabilité)
        self.df['ndvi_stability'] = 1 / (1 + self.df['ndvi_temporal_cv'])
        
        created += 4
        for feature in ['ndvi_temporal_std', 'ndvi_temporal_cv', 'ndvi_temporal_range', 'ndvi_stability']:
            self.feature_categories['temporal'].append(feature)
            self.new_features.append(feature)
        
        # Variabilité avancée
        if len(temporal_cols) >= 3:
            # Nombre de changements de direction
            def count_direction_changes(row):
                values = row[temporal_cols].values
                if np.isnan(values).sum() < len(values) * 0.5:
                    valid_values = values[~np.isnan(values)]
                    if len(valid_values) >= 3:
                        diffs = np.diff(valid_values)
                        signs = np.sign(diffs)
                        changes = np.sum(np.diff(signs) != 0)
                        return changes
                return np.nan
            
            self.df['ndvi_direction_changes'] = self.df.apply(count_direction_changes, axis=1)
            
            # Persistance (autocorrélation lag-1)
            def calculate_persistence(row):
                values = row[temporal_cols].values
                valid_values = values[~np.isnan(values)]
                if len(valid_values) >= 3:
                    return np.corrcoef(valid_values[:-1], valid_values[1:])[0, 1]
                return np.nan
            
            self.df['ndvi_persistence'] = self.df.apply(calculate_persistence, axis=1)
            
            created += 2
            for feature in ['ndvi_direction_changes', 'ndvi_persistence']:
                self.feature_categories['temporal'].append(feature)
                self.new_features.append(feature)
        
        print(f"   Créées: {created} features de variabilité")

    def _create_seasonality_features(self, temporal_cols):
        """Features de saisonnalité (si applicable)"""
        print("\n2.3 Features de saisonnalité:")
        
        # Pour les données annuelles, on peut chercher des patterns
        if len(temporal_cols) >= 4:
            created = 0
            
            # Amplitude saisonnière approximative
            temporal_data = self.df[temporal_cols]
            
            # Maximum et minimum dans la série
            self.df['ndvi_seasonal_max'] = temporal_data.max(axis=1)
            self.df['ndvi_seasonal_min'] = temporal_data.min(axis=1)
            self.df['ndvi_seasonal_amplitude'] = self.df['ndvi_seasonal_max'] - self.df['ndvi_seasonal_min']
            
            # Position du maximum (quelle année)
            self.df['ndvi_max_position'] = temporal_data.idxmax(axis=1).map(
                {col: i for i, col in enumerate(temporal_cols)}
            )
            
            # Position du minimum
            self.df['ndvi_min_position'] = temporal_data.idxmin(axis=1).map(
                {col: i for i, col in enumerate(temporal_cols)}
            )
            
            created += 5
            for feature in ['ndvi_seasonal_max', 'ndvi_seasonal_min', 'ndvi_seasonal_amplitude', 
                          'ndvi_max_position', 'ndvi_min_position']:
                self.feature_categories['temporal'].append(feature)
                self.new_features.append(feature)
            
            print(f"   Créées: {created} features de saisonnalité")
        else:
            print("   Pas assez de données pour saisonnalité")

    def _create_event_features(self, temporal_cols):
        """Features d'événements spécifiques (sécheresse, etc.)"""
        print("\n2.4 Features d'événements:")
        
        created = 0
        
        # Identifier années spécifiques si disponibles
        drought_years = ['2022']  # Année de sécheresse connue
        recovery_years = ['2023', '2024']
        
        for year in drought_years:
            drought_col = None
            for col in temporal_cols:
                if year in col:
                    drought_col = col
                    break
            
            if drought_col:
                # Impact de la sécheresse (par rapport à la moyenne des autres années)
                other_cols = [col for col in temporal_cols if col != drought_col]
                if other_cols:
                    other_mean = self.df[other_cols].mean(axis=1)
                    self.df[f'drought_{year}_impact'] = (other_mean - self.df[drought_col]) / (other_mean + 0.0001)
                    
                    created += 1
                    self.feature_categories['temporal'].append(f'drought_{year}_impact')
                    self.new_features.append(f'drought_{year}_impact')
                    print(f"   Impact sécheresse {year}")
        
        # Récupération post-événement
        for year in recovery_years:
            recovery_col = None
            for col in temporal_cols:
                if year in col:
                    recovery_col = col
                    break
            
            if recovery_col:
                # Trouver l'année précédente
                current_idx = temporal_cols.index(recovery_col)
                if current_idx > 0:
                    previous_col = temporal_cols[current_idx - 1]
                    self.df[f'recovery_{year}'] = (self.df[recovery_col] - self.df[previous_col]) / (self.df[previous_col] + 0.0001)
                    
                    created += 1
                    self.feature_categories['temporal'].append(f'recovery_{year}')
                    self.new_features.append(f'recovery_{year}')
                    print(f"   Récupération {year}")
        
        # Chutes brutales (drops)
        if len(temporal_cols) >= 2:
            temporal_data = self.df[temporal_cols]
            diffs = temporal_data.diff(axis=1)
            
            # Plus grande chute
            self.df['max_ndvi_drop'] = diffs.min(axis=1)
            
            # Plus grande hausse
            self.df['max_ndvi_rise'] = diffs.max(axis=1)
            
            # Nombre de chutes significatives (>0.1)
            self.df['significant_drops'] = (diffs < -0.1).sum(axis=1)
            
            created += 3
            for feature in ['max_ndvi_drop', 'max_ndvi_rise', 'significant_drops']:
                self.feature_categories['temporal'].append(feature)
                self.new_features.append(feature)
        
        print(f"   Créées: {created} features d'événements")

    def _create_resilience_features(self, temporal_cols):
        """Features de résilience forestière"""
        print("\n2.5 Features de résilience:")
        
        created = 0
        
        if len(temporal_cols) >= 3:
            temporal_data = self.df[temporal_cols]
            
            # Temps de récupération après chute
            def calculate_recovery_time(row):
                values = row[temporal_cols].values
                if np.isnan(values).sum() < len(values) * 0.5:
                    valid_values = values[~np.isnan(values)]
                    if len(valid_values) >= 3:
                        # Trouver la plus grande chute
                        diffs = np.diff(valid_values)
                        if len(diffs) > 0:
                            min_diff_idx = np.argmin(diffs)
                            if diffs[min_diff_idx] < -0.05:  # Chute significative
                                # Chercher temps de récupération
                                drop_value = valid_values[min_diff_idx + 1]
                                pre_drop_value = valid_values[min_diff_idx]
                                
                                recovery_time = 0
                                for i in range(min_diff_idx + 2, len(valid_values)):
                                    recovery_time += 1
                                    if valid_values[i] >= pre_drop_value * 0.95:  # 95% de récupération
                                        return recovery_time
                                return len(valid_values) - min_diff_idx - 2  # Pas encore récupéré
                return np.nan
            
            self.df['recovery_time'] = self.df.apply(calculate_recovery_time, axis=1)
            
            # Résilience index (capacité à maintenir des valeurs élevées)
            baseline = temporal_data.quantile(0.8, axis=1)  # 80e percentile comme baseline
            drops_below_baseline = (temporal_data.T < baseline).T.sum(axis=1)
            self.df['resilience_index'] = 1 - (drops_below_baseline / len(temporal_cols))
            
            # Adaptabilité (capacité à s'améliorer après stress)
            mid_point = len(temporal_cols) // 2
            first_half_mean = temporal_data.iloc[:, :mid_point].mean(axis=1)
            second_half_mean = temporal_data.iloc[:, mid_point:].mean(axis=1)
            self.df['adaptability'] = (second_half_mean - first_half_mean) / (first_half_mean + 0.0001)
            
            created += 3
            for feature in ['recovery_time', 'resilience_index', 'adaptability']:
                self.feature_categories['temporal'].append(feature)
                self.new_features.append(feature)
        
        print(f"   Créées: {created} features de résilience")

    # ============= ÉTAPE 3: FEATURES TOPOGRAPHIQUES =============
    def create_topographic_features(self):
        """ÉTAPE 3: Création de features topographiques avancées"""
        print("\n" + "="*70)
        print("ETAPE 3: CREATION DE FEATURES TOPOGRAPHIQUES")
        print("="*70)
        
        initial_count = len(self.df.columns)
        
        # 3.1 Features d'exposition
        self._create_exposure_features()
        
        # 3.2 Features de terrain
        self._create_terrain_features()
        
        # 3.3 Features hydrologiques
        self._create_hydrological_features()
        
        # 3.4 Features climatiques dérivées
        self._create_climate_derived_features()
        
        final_count = len(self.df.columns)
        created = final_count - initial_count
        print(f"\n{created} features topographiques créées")
        
        return created

    def _create_exposure_features(self):
        """Features d'exposition solaire et aux vents"""
        print("\n3.1 Features d'exposition:")
        
        created = 0
        
        if 'aspect' in self.df.columns and 'slope' in self.df.columns:
            # Exposition directionnelle
            self.df['northness'] = np.cos(np.radians(self.df['aspect'])) * np.sin(np.radians(self.df['slope']))
            self.df['eastness'] = np.sin(np.radians(self.df['aspect'])) * np.sin(np.radians(self.df['slope']))
            
            # Exposition solaire (simplified)
            # Favorise les pentes sud avec inclinaison modérée
            self.df['solar_exposure'] = np.cos(np.radians(self.df['aspect'] - 180)) * \
                                      np.sin(np.radians(self.df['slope'])) * \
                                      np.cos(np.radians(self.df['slope']))
            
            # Protection contre le vent (pentes nord)
            self.df['wind_protection'] = -np.cos(np.radians(self.df['aspect'])) * np.sin(np.radians(self.df['slope']))
            
            created += 4
            for feature in ['northness', 'eastness', 'solar_exposure', 'wind_protection']:
                self.feature_categories['topographic'].append(feature)
                self.new_features.append(feature)
            
            # Classifications d'exposition
            def classify_exposure(row):
                if pd.isna(row['aspect']):
                    return 'Unknown'
                aspect = row['aspect']
                slope = row['slope']
                
                if slope < 5:
                    return 'Flat'
                elif 135 <= aspect <= 225:  # Sud
                    return 'South_facing'
                elif 315 <= aspect or aspect <= 45:  # Nord
                    return 'North_facing'
                elif 45 < aspect < 135:  # Est
                    return 'East_facing'
                else:  # Ouest
                    return 'West_facing'
            
            self.df['exposure_class'] = self.df.apply(classify_exposure, axis=1)
            created += 1
            self.feature_categories['topographic'].append('exposure_class')
            self.new_features.append('exposure_class')
            
            print("   Exposition: northness, eastness, solaire, vent, classes")
        
        print(f"   Créées: {created} features d'exposition")

    def _create_terrain_features(self):
        """Features de caractérisation du terrain"""
        print("\n3.2 Features de terrain:")
        
        created = 0
        
        if 'elevation' in self.df.columns:
            # Classification altitudinale écologique
            def classify_elevation_zone(elevation):
                if pd.isna(elevation):
                    return 'Unknown'
                elif elevation < 500:
                    return 'Lowland'
                elif elevation < 1000:
                    return 'Colline'
                elif elevation < 1500:
                    return 'Montane_Low'
                elif elevation < 2500:
                    return 'Montane_High'
                else:
                    return 'Alpine'
            
            self.df['elevation_zone'] = self.df['elevation'].apply(classify_elevation_zone)
            
            # Élévation relative (si coordonnées disponibles pour calculs de voisinage)
            if 'latitude' in self.df.columns and 'longitude' in self.df.columns:
                # Élévation relative dans un rayon (approximation simple)
                elevation_mean = self.df['elevation'].mean()
                self.df['elevation_relative'] = self.df['elevation'] - elevation_mean
            
            created += 1
            self.feature_categories['topographic'].append('elevation_zone')
            self.new_features.append('elevation_zone')
            
            if 'elevation_relative' in self.df.columns:
                created += 1
                self.feature_categories['topographic'].append('elevation_relative')
                self.new_features.append('elevation_relative')
        
        if 'slope' in self.df.columns:
            # Classification de pente
            def classify_slope(slope):
                if pd.isna(slope):
                    return 'Unknown'
                elif slope < 2:
                    return 'Very_Gentle'
                elif slope < 5:
                    return 'Gentle'
                elif slope < 15:
                    return 'Moderate'
                elif slope < 30:
                    return 'Steep'
                else:
                    return 'Very_Steep'
            
            self.df['slope_class'] = self.df['slope'].apply(classify_slope)
            
            # Rugosité du terrain (slope comme proxy)
            self.df['terrain_roughness'] = np.log1p(self.df['slope'])
            
            created += 2
            for feature in ['slope_class', 'terrain_roughness']:
                self.feature_categories['topographic'].append(feature)
                self.new_features.append(feature)
        
        print(f"   Terrain: zones d'élévation, classes de pente, rugosité")
        print(f"   Créées: {created} features de terrain")

    def _create_hydrological_features(self):
        """Features hydrologiques dérivées"""
        print("\n3.3 Features hydrologiques:")
        
        created = 0
        
        # Topographic Wetness Index
        if 'slope' in self.df.columns and 'precipitation' in self.df.columns:
            # TWI = ln(a/tan(slope)) où a est l'aire de drainage (approximée par précipitations)
            drainage_area = self.df['precipitation'] / 1000  # Normalisation
            slope_rad = np.radians(self.df['slope'] + 0.1)  # Éviter division par 0
            
            self.df['topographic_wetness_index'] = np.log(drainage_area / np.tan(slope_rad))
            
            created += 1
            self.feature_categories['topographic'].append('topographic_wetness_index')
            self.new_features.append('topographic_wetness_index')
            print("   Topographic Wetness Index")
        
        # Position topographique
        if 'elevation' in self.df.columns and 'slope' in self.df.columns:
            # Position relative: crête, mi-pente, vallée
            def classify_topo_position(row):
                elevation = row['elevation']
                slope = row['slope']
                
                if pd.isna(elevation) or pd.isna(slope):
                    return 'Unknown'
                
                # Approximation basée sur élévation relative et pente
                elevation_percentile = stats.percentileofscore(self.df['elevation'].dropna(), elevation)
                
                if slope < 3:
                    if elevation_percentile > 70:
                        return 'Plateau'
                    else:
                        return 'Valley_Floor'
                elif slope < 15:
                    return 'Mid_Slope'
                else:
                    if elevation_percentile > 70:
                        return 'Ridge'
                    else:
                        return 'Steep_Slope'
            
            self.df['topographic_position'] = self.df.apply(classify_topo_position, axis=1)
            
            created += 1
            self.feature_categories['topographic'].append('topographic_position')
            self.new_features.append('topographic_position')
            print("   Position topographique")
        
        print(f"   Créées: {created} features hydrologiques")

    def _create_climate_derived_features(self):
        """Features climatiques dérivées de la topographie"""
        print("\n3.4 Features climatiques dérivées:")
        
        created = 0
        
        if 'elevation' in self.df.columns and 'temperature' in self.df.columns:
            # Gradient thermique altitudinal (approximation)
            # Généralement -0.6°C par 100m
            expected_temp_drop = (self.df['elevation'] / 100) * 0.6
            reference_temp = self.df['temperature'].mean()
            expected_temp = reference_temp - expected_temp_drop
            
            # Anomalie thermique (différence entre observé et attendu)
            self.df['temperature_anomaly'] = self.df['temperature'] - expected_temp
            
            created += 1
            self.feature_categories['topographic'].append('temperature_anomaly')
            self.new_features.append('temperature_anomaly')
            print("   Anomalie thermique altitudinale")
        
        if 'elevation' in self.df.columns and 'precipitation' in self.df.columns:
            # Efficacité précipitations par altitude
            self.df['precipitation_efficiency'] = self.df['precipitation'] / (1 + self.df['elevation'] / 1000)
            
            created += 1
            self.feature_categories['topographic'].append('precipitation_efficiency')
            self.new_features.append('precipitation_efficiency')
            print("   Efficacité précipitations")
        
        # Continentalité (distance à l'océan - pour le Maroc)
        if 'longitude' in self.df.columns and 'latitude' in self.df.columns:
            # Approximation: distance à la côte atlantique (longitude ~-6 à -9)
            atlantic_longitude = -6  # Côte atlantique moyenne Maroc
            self.df['continentality'] = np.abs(self.df['longitude'] - atlantic_longitude)
            
            # Distance à la Méditerranée (latitude ~35-36)
            mediterranean_latitude = 35.5
            self.df['distance_to_mediterranean'] = np.abs(self.df['latitude'] - mediterranean_latitude)
            
            created += 2
            for feature in ['continentality', 'distance_to_mediterranean']:
                self.feature_categories['topographic'].append(feature)
                self.new_features.append(feature)
            
            print("   Continentalité et distance aux mers")
        
        print(f"   Créées: {created} features climatiques dérivées")

    # ============= ÉTAPE 4: FEATURES ÉCOLOGIQUES =============
    def create_ecological_features(self):
        """ÉTAPE 4: Création de features écologiques et de santé"""
        print("\n" + "="*70)
        print("ETAPE 4: CREATION DE FEATURES ÉCOLOGIQUES")
        print("="*70)
        
        initial_count = len(self.df.columns)
        
        # 4.1 Indices de santé composite
        self._create_health_indices()
        
        # 4.2 Indices de stress
        self._create_stress_indices()
        
        # 4.3 Potentiel écologique
        self._create_ecological_potential()
        
        # 4.4 Classifications écologiques
        self._create_ecological_classifications()
        
        final_count = len(self.df.columns)
        created = final_count - initial_count
        print(f"\n{created} features écologiques créées")
        
        return created

    def _create_health_indices(self):
        """Indices composites de santé forestière"""
        print("\n4.1 Indices de santé composite:")
        
        created = 0
        
        # Forest Health Score composite
        health_components = []
        weights = {}
        
        if 'NDVI' in self.df.columns:
            health_components.append('NDVI')
            weights['NDVI'] = 0.4
        
        if 'NDMI' in self.df.columns:
            health_components.append('NDMI')
            weights['NDMI'] = 0.3
        
        if 'EVI' in self.df.columns:
            health_components.append('EVI')
            weights['EVI'] = 0.3
        
        if len(health_components) >= 2:
            # Normaliser les composants
            health_data = self.df[health_components].copy()
            
            # Score pondéré
            weighted_score = 0
            total_weight = 0
            
            for component in health_components:
                # Normalisation min-max
                min_val = health_data[component].quantile(0.05)
                max_val = health_data[component].quantile(0.95)
                normalized = (health_data[component] - min_val) / (max_val - min_val)
                normalized = normalized.clip(0, 1)
                
                weighted_score += normalized * weights[component]
                total_weight += weights[component]
            
            self.df['forest_health_composite'] = weighted_score / total_weight
            
            created += 1
            self.feature_categories['ecological'].append('forest_health_composite')
            self.new_features.append('forest_health_composite')
            print("   Forest Health Composite Score")
        
        # Vegetation Vigor Index
        if all(col in self.df.columns for col in ['NDVI', 'EVI']):
            self.df['vegetation_vigor'] = (self.df['NDVI'] * 0.6 + self.df['EVI'] * 0.4)
            
            created += 1
            self.feature_categories['ecological'].append('vegetation_vigor')
            self.new_features.append('vegetation_vigor')
            print("   Vegetation Vigor Index")
        
        # Canopy Condition Index
        if 'LAI_approx' in self.df.columns and 'NDVI' in self.df.columns:
            # Relation LAI-NDVI comme indicateur de condition
            expected_lai = 3.618 * (self.df['NDVI'] ** 2.169)
            self.df['canopy_condition'] = self.df['LAI_approx'] / (expected_lai + 0.0001)
            
            created += 1
            self.feature_categories['ecological'].append('canopy_condition')
            self.new_features.append('canopy_condition')
            print("   Canopy Condition Index")
        
        print(f"   Créées: {created} indices de santé")

    def _create_stress_indices(self):
        """Indices de stress forestier"""
        print("\n4.2 Indices de stress:")
        
        created = 0
        
        # Water Stress Index
        if 'NDMI' in self.df.columns:
            # Inverser NDMI pour avoir un indice de stress (plus élevé = plus de stress)
            self.df['water_stress_index'] = 1 - ((self.df['NDMI'] + 1) / 2)
            
            created += 1
            self.feature_categories['ecological'].append('water_stress_index')
            self.new_features.append('water_stress_index')
            print("   Water Stress Index")
        
        # Temperature Stress
        if 'temperature' in self.df.columns:
            # Stress thermique basé sur les extrêmes
            temp_mean = self.df['temperature'].mean()
            temp_std = self.df['temperature'].std()
            
            # Z-score de température
            temp_z = np.abs((self.df['temperature'] - temp_mean) / temp_std)
            self.df['temperature_stress'] = np.where(temp_z > 2, temp_z / 3, temp_z / 6)
            
            created += 1
            self.feature_categories['ecological'].append('temperature_stress')
            self.new_features.append('temperature_stress')
            print("   Temperature Stress Index")
        
        # Drought Stress (si données temporelles)
        if 'ndvi_temporal_std' in self.df.columns and 'ndvi_linear_trend' in self.df.columns:
            # Combinaison de tendance négative et variabilité élevée
            trend_stress = np.where(self.df['ndvi_linear_trend'] < 0, 
                                  np.abs(self.df['ndvi_linear_trend']), 0)
            variability_stress = self.df['ndvi_temporal_std'] / (self.df['ndvi_temporal_std'].max() + 0.0001)
            
            self.df['drought_stress_composite'] = (trend_stress * 0.6 + variability_stress * 0.4)
            
            created += 1
            self.feature_categories['ecological'].append('drought_stress_composite')
            self.new_features.append('drought_stress_composite')
            print("   Drought Stress Composite")
        
        # Fire Risk Index
        if all(col in self.df.columns for col in ['NDMI', 'temperature']):
            # Combiner faible humidité et haute température
            water_stress = 1 - ((self.df['NDMI'] + 1) / 2)
            temp_normalized = (self.df['temperature'] - self.df['temperature'].min()) / \
                            (self.df['temperature'].max() - self.df['temperature'].min())
            
            self.df['fire_risk_index'] = (water_stress * 0.6 + temp_normalized * 0.4)
            
            if 'slope' in self.df.columns:
                # Ajouter facteur de pente (pentes raides = propagation rapide)
                slope_normalized = self.df['slope'] / (self.df['slope'].max() + 0.0001)
                self.df['fire_risk_index'] = (self.df['fire_risk_index'] * 0.8 + slope_normalized * 0.2)
            
            created += 1
            self.feature_categories['ecological'].append('fire_risk_index')
            self.new_features.append('fire_risk_index')
            print("   Fire Risk Index")
        
        print(f"   Créées: {created} indices de stress")

    def _create_ecological_potential(self):
        """Potentiel et capacité écologique"""
        print("\n4.3 Potentiel écologique:")
        
        created = 0
        
        # Carrying Capacity Index
        if all(col in self.df.columns for col in ['precipitation', 'temperature', 'elevation']):
            # Capacité de charge basée sur facteurs climatiques
            precip_normalized = self.df['precipitation'] / 1000  # mm to m
            temp_suitability = 1 - np.abs(self.df['temperature'] - 288.15) / 20  # Optimum ~15°C
            elev_suitability = np.exp(-self.df['elevation'] / 3000)  # Décroissance exponentielle
            
            self.df['carrying_capacity'] = (precip_normalized * 0.4 + 
                                          temp_suitability * 0.4 + 
                                          elev_suitability * 0.2)
            
            created += 1
            self.feature_categories['ecological'].append('carrying_capacity')
            self.new_features.append('carrying_capacity')
            print("   Carrying Capacity Index")
        
        # Growth Potential
        if 'NDVI' in self.df.columns and 'carrying_capacity' in self.df.columns:
            # Potentiel de croissance = capacité - état actuel
            ndvi_normalized = (self.df['NDVI'] - self.df['NDVI'].min()) / \
                            (self.df['NDVI'].max() - self.df['NDVI'].min())
            
            self.df['growth_potential'] = self.df['carrying_capacity'] - ndvi_normalized
            
            created += 1
            self.feature_categories['ecological'].append('growth_potential')
            self.new_features.append('growth_potential')
            print("   Growth Potential Index")
        
        # Recovery Potential
        if all(col in self.df.columns for col in ['forest_health_composite', 'water_stress_index']):
            # Potentiel de récupération = santé de base - stress
            self.df['recovery_potential'] = self.df['forest_health_composite'] - self.df['water_stress_index']
            
            created += 1
            self.feature_categories['ecological'].append('recovery_potential')
            self.new_features.append('recovery_potential')
            print("   Recovery Potential Index")
        
        # Biodiversity Potential (proxy)
        if all(col in self.df.columns for col in ['elevation', 'precipitation']):
            # Diversité potentielle basée sur hétérogénéité environnementale
            elev_diversity = 1 - np.abs(self.df['elevation'] - self.df['elevation'].mean()) / \
                           (self.df['elevation'].std() + 0.0001)
            precip_diversity = self.df['precipitation'] / (self.df['precipitation'].max() + 0.0001)
            
            self.df['biodiversity_potential'] = (elev_diversity * 0.5 + precip_diversity * 0.5)
            
            created += 1
            self.feature_categories['ecological'].append('biodiversity_potential')
            self.new_features.append('biodiversity_potential')
            print("   Biodiversity Potential Index")
        
        print(f"   Créées: {created} indices de potentiel")

    def _create_ecological_classifications(self):
        """Classifications écologiques avancées"""
        print("\n4.4 Classifications écologiques:")
        
        created = 0
        
        # Classification de santé multi-critères
        if 'forest_health_composite' in self.df.columns:
            def classify_health_detailed(health_score):
                if pd.isna(health_score):
                    return 'Unknown'
                elif health_score >= 0.8:
                    return 'Excellent'
                elif health_score >= 0.6:
                    return 'Good'
                elif health_score >= 0.4:
                    return 'Fair'
                elif health_score >= 0.2:
                    return 'Poor'
                else:
                    return 'Critical'
            
            self.df['health_class_detailed'] = self.df['forest_health_composite'].apply(classify_health_detailed)
            
            created += 1
            self.feature_categories['ecological'].append('health_class_detailed')
            self.new_features.append('health_class_detailed')
            print("   Classification santé détaillée")
        
        # Classification de risque
        risk_factors = ['water_stress_index', 'fire_risk_index', 'temperature_stress']
        available_risk = [factor for factor in risk_factors if factor in self.df.columns]
        
        if len(available_risk) >= 2:
            # Score de risque composite
            risk_data = self.df[available_risk]
            self.df['risk_composite'] = risk_data.mean(axis=1)
            
            def classify_risk(risk_score):
                if pd.isna(risk_score):
                    return 'Unknown'
                elif risk_score <= 0.2:
                    return 'Low_Risk'
                elif risk_score <= 0.4:
                    return 'Moderate_Risk'
                elif risk_score <= 0.6:
                    return 'High_Risk'
                else:
                    return 'Critical_Risk'
            
            self.df['risk_class'] = self.df['risk_composite'].apply(classify_risk)
            
            created += 2
            for feature in ['risk_composite', 'risk_class']:
                self.feature_categories['ecological'].append(feature)
                self.new_features.append(feature)
            
            print("   Classification de risque composite")
        
        # Classification de priorité de gestion
        if all(col in self.df.columns for col in ['forest_health_composite', 'risk_composite']):
            def classify_management_priority(row):
                health = row['forest_health_composite']
                risk = row['risk_composite']
                
                if pd.isna(health) or pd.isna(risk):
                    return 'Unknown'
                
                if health < 0.3 and risk > 0.6:
                    return 'Urgent_Intervention'
                elif health < 0.5 and risk > 0.4:
                    return 'High_Priority'
                elif health < 0.7 or risk > 0.3:
                    return 'Moderate_Priority'
                else:
                    return 'Low_Priority'
            
            self.df['management_priority'] = self.df.apply(classify_management_priority, axis=1)
            
            created += 1
            self.feature_categories['ecological'].append('management_priority')
            self.new_features.append('management_priority')
            print("   Classification priorité de gestion")
        
        print(f"   Créées: {created} classifications")

    # ============= ÉTAPE 5: FEATURES D'INTERACTION =============
    def create_interaction_features(self):
        """ÉTAPE 5: Création de features d'interaction"""
        print("\n" + "="*70)
        print("ETAPE 5: CREATION DE FEATURES D'INTERACTION")
        print("="*70)
        
        initial_count = len(self.df.columns)
        
        # 5.1 Interactions climat-topographie
        self._create_climate_topo_interactions()
        
        # 5.2 Interactions végétation-environnement
        self._create_vegetation_environment_interactions()
        
        # 5.3 Interactions temporelles
        self._create_temporal_interactions()
        
        # 5.4 Ratios et produits significatifs
        self._create_significant_ratios()
        
        final_count = len(self.df.columns)
        created = final_count - initial_count
        print(f"\n{created} features d'interaction créées")
        
        return created

    def _create_climate_topo_interactions(self):
        """Interactions climat-topographie"""
        print("\n5.1 Interactions climat-topographie:")
        
        created = 0
        
        # Interaction température-altitude
        if all(col in self.df.columns for col in ['temperature', 'elevation']):
            self.df['temp_elevation_interaction'] = self.df['temperature'] * np.log1p(self.df['elevation'])
            
            # Gradient thermique local
            expected_temp = self.df['temperature'].mean() - (self.df['elevation'] / 100) * 0.006
            self.df['temp_elevation_anomaly'] = self.df['temperature'] - expected_temp
            
            created += 2
            for feature in ['temp_elevation_interaction', 'temp_elevation_anomaly']:
                self.feature_categories['interaction'].append(feature)
                self.new_features.append(feature)
            
            print("   Interactions température-élévation")
        
        # Interaction précipitation-pente
        if all(col in self.df.columns for col in ['precipitation', 'slope']):
            # Efficacité des précipitations selon la pente
            self.df['precip_slope_interaction'] = self.df['precipitation'] / (1 + self.df['slope'] / 10)
            
            created += 1
            self.feature_categories['interaction'].append('precip_slope_interaction')
            self.new_features.append('precip_slope_interaction')
            print("   Interaction précipitation-pente")
        
        # Interaction exposition-climat
        if all(col in self.df.columns for col in ['solar_exposure', 'temperature', 'precipitation']):
            # Stress climatique pondéré par exposition
            self.df['climate_exposure_stress'] = (self.df['temperature'] / 288.15) * \
                                               np.abs(self.df['solar_exposure']) / \
                                               (self.df['precipitation'] / 500 + 0.1)
            
            created += 1
            self.feature_categories['interaction'].append('climate_exposure_stress')
            self.new_features.append('climate_exposure_stress')
            print("   Stress climatique-exposition")
        
        print(f"   Créées: {created} interactions climat-topo")

    def _create_vegetation_environment_interactions(self):
        """Interactions végétation-environnement"""
        print("\n5.2 Interactions végétation-environnement:")
        
        created = 0
        
        # NDVI-Climat
        if all(col in self.df.columns for col in ['NDVI', 'temperature', 'precipitation']):
            # Efficacité de la végétation selon le climat
            self.df['ndvi_climate_efficiency'] = self.df['NDVI'] / \
                                               (self.df['temperature'] - 273.15 + 1) * \
                                               (self.df['precipitation'] / 1000)
            
            # Potentiel climatique vs réalisation
            climate_potential = (self.df['precipitation'] / 1000) * \
                              np.exp(-(self.df['temperature'] - 288.15)**2 / 100)
            self.df['ndvi_climate_realization'] = self.df['NDVI'] / (climate_potential + 0.001)
            
            created += 2
            for feature in ['ndvi_climate_efficiency', 'ndvi_climate_realization']:
                self.feature_categories['interaction'].append(feature)
                self.new_features.append(feature)
            
            print("   Interactions NDVI-climat")
        
        # Végétation-Topographie
        if all(col in self.df.columns for col in ['NDVI', 'elevation', 'slope']):
            # NDVI ajusté par contraintes topographiques
            topo_constraint = 1 / (1 + self.df['elevation'] / 2000 + self.df['slope'] / 30)
            self.df['ndvi_topo_adjusted'] = self.df['NDVI'] / topo_constraint
            
            # Productivité par unité d'altitude
            self.df['productivity_per_elevation'] = self.df['NDVI'] / (self.df['elevation'] / 1000 + 0.1)
            
            created += 2
            for feature in ['ndvi_topo_adjusted', 'productivity_per_elevation']:
                self.feature_categories['interaction'].append(feature)
                self.new_features.append(feature)
            
            print("   Interactions végétation-topographie")
        
        # Stress hydrique-Demande évaporative
        if all(col in self.df.columns for col in ['NDMI', 'temperature', 'solar_exposure']):
            # Demande évaporative approximée
            evaporative_demand = (self.df['temperature'] - 273.15) * (1 + np.abs(self.df['solar_exposure']))
            self.df['water_stress_evaporative'] = (1 - (self.df['NDMI'] + 1) / 2) * evaporative_demand / 30
            
            created += 1
            self.feature_categories['interaction'].append('water_stress_evaporative')
            self.new_features.append('water_stress_evaporative')
            print("   Stress hydrique-demande évaporative")
        
        print(f"   Créées: {created} interactions végétation-environnement")

    def _create_temporal_interactions(self):
        """Interactions temporelles"""
        print("\n5.3 Interactions temporelles:")
        
        created = 0
        
        # Tendance vs Stress actuel
        if all(col in self.df.columns for col in ['ndvi_linear_trend', 'water_stress_index']):
            # Capacité à maintenir la tendance malgré le stress
            self.df['trend_stress_interaction'] = self.df['ndvi_linear_trend'] / (1 + self.df['water_stress_index'])
            
            created += 1
            self.feature_categories['interaction'].append('trend_stress_interaction')
            self.new_features.append('trend_stress_interaction')
            print("   Interaction tendance-stress")
        
        # Variabilité vs Résilience
        if all(col in self.df.columns for col in ['ndvi_temporal_cv', 'recovery_potential']):
            # Rapport variabilité/capacité de récupération
            self.df['variability_resilience_ratio'] = self.df['ndvi_temporal_cv'] / \
                                                     (self.df['recovery_potential'] + 0.001)
            
            created += 1
            self.feature_categories['interaction'].append('variability_resilience_ratio')
            self.new_features.append('variability_resilience_ratio')
            print("   Ratio variabilité-résilience")
        
        # Adaptation vs Contraintes environnementales
        if all(col in self.df.columns for col in ['adaptability', 'climate_exposure_stress']):
            self.df['adaptation_constraint_balance'] = self.df['adaptability'] / \
                                                      (1 + self.df['climate_exposure_stress'])
            
            created += 1
            self.feature_categories['interaction'].append('adaptation_constraint_balance')
            self.new_features.append('adaptation_constraint_balance')
            print("   Balance adaptation-contraintes")
        
        print(f"   Créées: {created} interactions temporelles")

    def _create_significant_ratios(self):
        """Ratios et produits écologiquement significatifs"""
        print("\n5.4 Ratios significatifs:")
        
        created = 0
        
        # Ratio Productivité/Stress
        if all(col in self.df.columns for col in ['vegetation_vigor', 'water_stress_index']):
            self.df['productivity_stress_ratio'] = self.df['vegetation_vigor'] / \
                                                  (self.df['water_stress_index'] + 0.001)
            
            created += 1
            self.feature_categories['interaction'].append('productivity_stress_ratio')
            self.new_features.append('productivity_stress_ratio')
            print("   Ratio productivité/stress")
        
        # Ratio Santé/Risque
        if all(col in self.df.columns for col in ['forest_health_composite', 'risk_composite']):
            self.df['health_risk_ratio'] = self.df['forest_health_composite'] / \
                                          (self.df['risk_composite'] + 0.001)
            
            created += 1
            self.feature_categories['interaction'].append('health_risk_ratio')
            self.new_features.append('health_risk_ratio')
            print("   Ratio santé/risque")
        
        # Efficiency Index (production par unité de ressource)
        if all(col in self.df.columns for col in ['NDVI', 'precipitation', 'temperature']):
            # Efficacité de conversion climat → biomasse
            climate_input = (self.df['precipitation'] / 1000) * \
                          np.exp(-(self.df['temperature'] - 288.15)**2 / 200)
            self.df['climate_conversion_efficiency'] = self.df['NDVI'] / (climate_input + 0.001)
            
            created += 1
            self.feature_categories['interaction'].append('climate_conversion_efficiency')
            self.new_features.append('climate_conversion_efficiency')
            print("   Efficacité conversion climatique")
        
        print(f"   Créées: {created} ratios significatifs")

    # ============= ÉTAPE 6: FEATURES MACHINE LEARNING =============
    def create_ml_features(self):
        """ÉTAPE 6: Préparation features pour Machine Learning"""
        print("\n" + "="*70)
        print("ETAPE 6: FEATURES MACHINE LEARNING")
        print("="*70)
        
        initial_count = len(self.df.columns)
        
        # 6.1 Normalisation et scaling
        self._create_normalized_features()
        
        # 6.2 Features polynomiales
        self._create_polynomial_features()
        
        # 6.3 Binning et discrétisation
        self._create_binned_features()
        
        # 6.4 Encoding des variables catégorielles
        self._encode_categorical_features()
        
        final_count = len(self.df.columns)
        created = final_count - initial_count
        print(f"\n{created} features ML créées")
        
        return created

    def _create_normalized_features(self):
        """Features normalisées pour ML"""
        print("\n6.1 Normalisation features:")
        
        created = 0
        key_features = ['NDVI', 'NDMI', 'EVI', 'forest_health_composite', 'water_stress_index']
        available_features = [f for f in key_features if f in self.df.columns]
        
        if available_features:
            scaler = StandardScaler()
            normalized_data = scaler.fit_transform(self.df[available_features].fillna(0))
            
            for i, feature in enumerate(available_features):
                normalized_name = f'{feature}_standardized'
                self.df[normalized_name] = normalized_data[:, i]
                
                self.feature_categories['ml_ready'].append(normalized_name)
                self.new_features.append(normalized_name)
                created += 1
            
            print(f"   Standardisation: {len(available_features)} features")
        
        # Min-Max scaling pour features spécifiques
        minmax_features = ['fire_risk_index', 'recovery_potential', 'growth_potential']
        available_minmax = [f for f in minmax_features if f in self.df.columns]
        
        if available_minmax:
            minmax_scaler = MinMaxScaler()
            minmax_data = minmax_scaler.fit_transform(self.df[available_minmax].fillna(0))
            
            for i, feature in enumerate(available_minmax):
                minmax_name = f'{feature}_minmax'
                self.df[minmax_name] = minmax_data[:, i]
                
                self.feature_categories['ml_ready'].append(minmax_name)
                self.new_features.append(minmax_name)
                created += 1
            
            print(f"   Min-Max scaling: {len(available_minmax)} features")
        
        print(f"   Créées: {created} features normalisées")

    def _create_polynomial_features(self):
        """Features polynomiales pour capturer non-linéarités"""
        print("\n6.2 Features polynomiales:")
        
        created = 0
        
        # Sélectionner features importantes pour interactions polynomiales
        poly_features = ['NDVI', 'NDMI', 'temperature', 'precipitation']
        available_poly = [f for f in poly_features if f in self.df.columns]
        
        if len(available_poly) >= 2:
            # Limiter à 3 features max pour éviter explosion dimensionnelle
            selected_features = available_poly[:3]
            
            poly_data = self.df[selected_features].fillna(self.df[selected_features].mean())
            
            # Créer features quadratiques uniquement
            for feature in selected_features:
                quad_name = f'{feature}_squared'
                self.df[quad_name] = poly_data[feature] ** 2
                
                self.feature_categories['ml_ready'].append(quad_name)
                self.new_features.append(quad_name)
                created += 1
            
            # Créer quelques interactions croisées importantes
            if 'NDVI' in selected_features and 'precipitation' in selected_features:
                self.df['NDVI_precipitation_product'] = poly_data['NDVI'] * poly_data['precipitation']
                self.feature_categories['ml_ready'].append('NDVI_precipitation_product')
                self.new_features.append('NDVI_precipitation_product')
                created += 1
            
            if 'NDMI' in selected_features and 'temperature' in selected_features:
                self.df['NDMI_temperature_product'] = poly_data['NDMI'] * poly_data['temperature']
                self.feature_categories['ml_ready'].append('NDMI_temperature_product')
                self.new_features.append('NDMI_temperature_product')
                created += 1
            
            print(f"   Features polynomiales: {len(selected_features)} quadratiques + interactions")
        
        print(f"   Créées: {created} features polynomiales")

    def _create_binned_features(self):
        """Discrétisation de variables continues"""
        print("\n6.3 Binning features:")
        
        created = 0
        
        # Binning features importantes
        binning_config = {
            'elevation': {'bins': 5, 'labels': ['Very_Low', 'Low', 'Medium', 'High', 'Very_High']},
            'temperature': {'bins': 4, 'labels': ['Cold', 'Cool', 'Warm', 'Hot']},
            'precipitation': {'bins': 4, 'labels': ['Arid', 'Semi_Arid', 'Humid', 'Very_Humid']},
            'NDVI': {'bins': 5, 'labels': ['Very_Poor', 'Poor', 'Fair', 'Good', 'Excellent']}
        }
        
        for feature, config in binning_config.items():
            if feature in self.df.columns:
                binned_name = f'{feature}_binned'
                self.df[binned_name] = pd.cut(self.df[feature], 
                                            bins=config['bins'], 
                                            labels=config['labels'],
                                            include_lowest=True)
                
                self.feature_categories['ml_ready'].append(binned_name)
                self.new_features.append(binned_name)
                created += 1
                print(f"   Binning: {feature} → {config['bins']} bins")
        
        print(f"   Créées: {created} features binnées")

    def _encode_categorical_features(self):
        """Encoding des variables catégorielles"""
        print("\n6.4 Encoding catégoriel:")
        
        created = 0
        
        # Features catégorielles à encoder
        categorical_features = [
            'region_main', 'exposure_class', 'slope_class', 'elevation_zone',
            'health_class_detailed', 'risk_class', 'management_priority'
        ]
        
        available_categorical = [f for f in categorical_features if f in self.df.columns]
        
        for feature in available_categorical:
            # One-hot encoding pour features avec peu de catégories
            unique_count = self.df[feature].nunique()
            
            if unique_count <= 6:  # One-hot si peu de catégories
                dummies = pd.get_dummies(self.df[feature], prefix=f'{feature}_is', dummy_na=True)
                
                for dummy_col in dummies.columns:
                    self.df[dummy_col] = dummies[dummy_col]
                    self.feature_categories['ml_ready'].append(dummy_col)
                    self.new_features.append(dummy_col)
                    created += 1
                
                print(f"   One-hot: {feature} → {len(dummies.columns)} dummies")
            
            else:  # Label encoding si beaucoup de catégories
                from sklearn.preprocessing import LabelEncoder
                le = LabelEncoder()
                encoded_name = f'{feature}_encoded'
                self.df[encoded_name] = le.fit_transform(self.df[feature].astype(str))
                
                self.feature_categories['ml_ready'].append(encoded_name)
                self.new_features.append(encoded_name)
                created += 1
                
                print(f"   Label encoding: {feature}")
        
        print(f"   Créées: {created} features encodées")

    # ============= MÉTHODES UTILITAIRES =============
    def generate_feature_summary(self):
        """Générer un résumé des features créées"""
        print("\n" + "="*70)
        print("RESUME DE FEATURE ENGINEERING")
        print("="*70)
        
        print(f"\nBILAN GLOBAL:")
        print(f"   • Features initiales: {self.original_shape[1]}")
        print(f"   • Features créées: {len(self.new_features)}")
        print(f"   • Features finales: {self.df.shape[1]}")
        print(f"   • Augmentation: {(len(self.new_features)/self.original_shape[1]*100):.1f}%")
        
        print(f"\nFEATURES PAR CATEGORIE:")
        total_new = 0
        for category, features in self.feature_categories.items():
            if features:
                print(f"   • {category.replace('_', ' ').title()}: {len(features)} features")
                total_new += len(features)
                
                if len(features) <= 3:
                    print(f"     - {', '.join(features)}")
                else:
                    print(f"     - {', '.join(features[:3])}... (+{len(features)-3})")
        
        print(f"\nFEATURES ML-READY:")
        ml_features = self.feature_categories['ml_ready']
        print(f"   • Total: {len(ml_features)} features prêtes pour ML")
        
        print(f"\nQUALITE DES NOUVELLES FEATURES:")
        if self.new_features:
            new_features_data = self.df[self.new_features]
            missing_pct = new_features_data.isnull().sum().sum() / (len(new_features_data) * len(self.new_features)) * 100
            print(f"   • Complétude: {100-missing_pct:.1f}%")
            print(f"   • Features sans valeurs manquantes: {len([f for f in self.new_features if self.df[f].isnull().sum() == 0])}")
        
        print(f"\nRECOMMANDATIONS:")
        if len(self.new_features) > 100:
            print("   Considérer une sélection de features (trop nombreuses)")
        if len(ml_features) > 0:
            print("   Features prêtes pour entraînement ML")
        if len(self.feature_categories['temporal']) > 0:
            print("   Features temporelles disponibles pour analyse de tendances")
        if len(self.feature_categories['ecological']) > 0:
            print("   Features écologiques pour évaluation santé forestière")
        
        return {
            'original_features': self.original_shape[1],
            'new_features': len(self.new_features),
            'total_features': self.df.shape[1],
            'categories': {cat: len(feats) for cat, feats in self.feature_categories.items() if feats},
            'ml_ready_count': len(ml_features)
        }

    def save_engineered_dataset(self, output_file='forest_features_engineered.csv'):
        """Sauvegarder le dataset avec nouvelles features"""
        self.df.to_csv(output_file, index=False)
        print(f"\nDataset avec features sauvegardé: {output_file}")
        
        # Sauvegarder la liste des nouvelles features
        feature_list_file = output_file.replace('.csv', '_feature_list.txt')
        with open(feature_list_file, 'w') as f:
            f.write("NOUVELLES FEATURES CRÉEES\n")
            f.write("="*50 + "\n\n")
            
            for category, features in self.feature_categories.items():
                if features:
                    f.write(f"{category.replace('_', ' ').title()}:\n")
                    for feature in features:
                        f.write(f"  - {feature}\n")
                    f.write("\n")
        
        print(f"Liste des features sauvegardée: {feature_list_file}")
        
        return output_file

# ============= FONCTIONS PRINCIPALES =============

def full_feature_engineering_pipeline(data_file):
    """Pipeline complet de feature engineering"""
    print("PIPELINE FEATURE ENGINEERING FOREST DIGITAL TWIN")
    print("=" * 60)
    
    # Charger données
    try:
        df = pd.read_csv(data_file)
        print(f"Dataset chargé: {df.shape[0]:,} points × {df.shape[1]} features")
    except Exception as e:
        print(f"Erreur chargement: {e}")
        return None
    
    # Initialiser Feature Engineer
    engineer = ForestFeatureEngineer(df)
    
    # Exécuter toutes les étapes
    results = {}
    
    print("\nLancement feature engineering complet...")
    
    results['spectral'] = engineer.create_spectral_features()
    results['temporal'] = engineer.create_temporal_features()
    results['topographic'] = engineer.create_topographic_features()
    results['ecological'] = engineer.create_ecological_features()
    results['interaction'] = engineer.create_interaction_features()
    results['ml'] = engineer.create_ml_features()
    
    # Résumé
    summary = engineer.generate_feature_summary()
    
    # Sauvegarde
    output_file = engineer.save_engineered_dataset()
    
    return {
        'engineer': engineer,
        'results': results,
        'summary': summary,
        'output_file': output_file,
        'final_dataset': engineer.df
    }

def custom_feature_engineering(data_file, steps=None):
    """Feature engineering personnalisé"""
    if steps is None:
        steps = ['spectral', 'temporal', 'topographic', 'ecological']
    
    print("FEATURE ENGINEERING PERSONNALISE")
    print(f"Étapes sélectionnées: {steps}")
    print("=" * 40)
    
    df = pd.read_csv(data_file)
    engineer = ForestFeatureEngineer(df)
    
    results = {}
    
    if 'spectral' in steps:
        results['spectral'] = engineer.create_spectral_features()
    
    if 'temporal' in steps:
        results['temporal'] = engineer.create_temporal_features()
    
    if 'topographic' in steps:
        results['topographic'] = engineer.create_topographic_features()
    
    if 'ecological' in steps:
        results['ecological'] = engineer.create_ecological_features()
    
    if 'interaction' in steps:
        results['interaction'] = engineer.create_interaction_features()
    
    if 'ml' in steps:
        results['ml'] = engineer.create_ml_features()
    
    summary = engineer.generate_feature_summary()
    
    return engineer, results, summary


if __name__ == "__main__":
    import os
    
    test_files = [
        'forest_digital_twin_master.csv',
        'morocco_forest_complete_simple.csv',
        'processed_data/forest_digital_twin_master.csv'
    ]
    
    for file in test_files:
        if os.path.exists(file):
            print(f"Dataset trouvé: {file}")
            results = full_feature_engineering_pipeline(file)
            break
    else:
        print("Aucun dataset trouvé. Utilisez:")
        print(">>> full_feature_engineering_pipeline('votre_fichier.csv')")