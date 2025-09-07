import pandas as pd
import numpy as np
import os
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class ForestDigitalTwinProcessor:
    """Processeur avancé pour les données Forest Digital Twin - Maroc"""
    
    def __init__(self, data_folder="data"):
        self.data_folder = Path(data_folder)
        self.datasets = {}
        self.region_configs = self._load_region_configurations()
        self.column_mapping = {}
        
        print("Forest Digital Twin Processor v2.0 initialisé")
        print(f"Dossier: {self.data_folder} | Régions: {len(self.region_configs)}")
        
    def inspect_data_structure(self):
        """Inspecter la structure des fichiers CSV"""
        print("\nInspection de la structure des données...")
        
        sample_files = ['samples_rif_2024.csv', 'samples_moyen_atlas_2024.csv', 'samples_mamora_2024.csv']
        
        for filename in sample_files:
            filepath = self.data_folder / filename
            if filepath.exists():
                print(f"\nAnalyse de {filename}:")
                try:
                    df = pd.read_csv(filepath, nrows=3)
                    print(f"   Colonnes ({len(df.columns)}): {list(df.columns)[:8]}...")
                    self._detect_coordinate_columns(df.columns)
                    return df.columns.tolist()
                except Exception as e:
                    print(f"   Erreur: {e}")
        
        print("Aucun fichier CSV trouvé")
        return []
    
    def _detect_coordinate_columns(self, columns):
        """Détecter et mapper les colonnes de coordonnées"""
        print("Détection coordonnées:")
        
        possible_coords = {
            'longitude': ['longitude', 'lon', 'x', 'lng', '.geo'],
            'latitude': ['latitude', 'lat', 'y', '.geo']
        }
        
        for standard_name, possible_names in possible_coords.items():
            found = False
            for col in columns:
                if any(possible in col.lower() for possible in possible_names):
                    self.column_mapping[standard_name] = col
                    print(f"     {standard_name} -> {col}")
                    found = True
                    break
            if not found:
                print(f"     {standard_name} non trouvé")
                self.column_mapping[standard_name] = None
        
    def _load_region_configurations(self):
        """Configuration des seuils d'alerte par région"""
        return {
            'rif': {
                'name': 'Chaîne du Rif',
                'ecosystem': 'Forêts méditerranéennes humides',
                'species': 'Chêne-liège, Pin maritime',
                'climate': 'Méditerranéen humide (600-1200mm/an)',
                'altitude_range': (200, 2000),
                'thresholds': {
                    'ndvi_critical': 0.5, 'ndmi_critical': 0.1, 'evi_critical': 0.3,
                    'health_excellent': 0.65, 'health_good': 0.5, 'health_moderate': 0.35,
                    'stress_severe': -0.1, 'stress_moderate': 0.05
                }
            },
            'moyen_atlas': {
                'name': 'Moyen Atlas',
                'ecosystem': 'Forêts de montagne continentales',
                'species': 'Cèdre de l\'Atlas, Chêne vert',
                'climate': 'Continental montagnard (400-800mm/an)',
                'altitude_range': (800, 3000),
                'thresholds': {
                    'ndvi_critical': 0.45, 'ndmi_critical': 0.05, 'evi_critical': 0.25,
                    'health_excellent': 0.6, 'health_good': 0.45, 'health_moderate': 0.3,
                    'stress_severe': -0.15, 'stress_moderate': 0.0
                }
            },
            'haut_atlas': {
                'name': 'Haut Atlas',
                'ecosystem': 'Forêts de haute montagne arides',
                'species': 'Thuya, Genévrier',
                'climate': 'Montagnard aride (200-600mm/an)',
                'altitude_range': (1000, 4000),
                'thresholds': {
                    'ndvi_critical': 0.4, 'ndmi_critical': 0.0, 'evi_critical': 0.2,
                    'health_excellent': 0.55, 'health_good': 0.4, 'health_moderate': 0.25,
                    'stress_severe': -0.2, 'stress_moderate': -0.05
                }
            },
            'mamora': {
                'name': 'Forêt de Mamora',
                'ecosystem': 'Forêt de plaine subéreuse',
                'species': 'Chêne-liège (monoculture)',
                'climate': 'Méditerranéen atlantique (400-600mm/an)',
                'altitude_range': (0, 200),
                'thresholds': {
                    'ndvi_critical': 0.4, 'ndmi_critical': 0.0, 'evi_critical': 0.2,
                    'health_excellent': 0.6, 'health_good': 0.4, 'health_moderate': 0.25,
                    'stress_severe': -0.1, 'stress_moderate': 0.0
                }
            },
            'argan': {
                'name': 'Écosystème Arganier',
                'ecosystem': 'Forêt aride endémique (UNESCO)',
                'species': 'Arganier (Argania spinosa)',
                'climate': 'Aride à semi-aride (150-400mm/an)',
                'altitude_range': (0, 1500),
                'thresholds': {
                    'ndvi_critical': 0.35, 'ndmi_critical': -0.1, 'evi_critical': 0.15,
                    'health_excellent': 0.5, 'health_good': 0.35, 'health_moderate': 0.2,
                    'stress_severe': -0.25, 'stress_moderate': -0.1
                }
            }
        }
    
    def load_all_data(self):
        """Charger tous les fichiers avec métadonnées"""
        print("\nChargement complet des données...")
        
        self.inspect_data_structure()
        self.load_sample_files()
        self.load_timeseries_files()
        self.create_master_dataset()
        self.add_available_derived_variables()
        
        print(f"\nChargement terminé : {len(self.datasets)} datasets créés")
        
    def load_sample_files(self):
        """Charger tous les fichiers samples"""
        print("\nChargement des fichiers samples...")
        
        sample_files = {
            'rif': 'samples_rif_2024.csv',
            'moyen_atlas': 'samples_moyen_atlas_2024.csv',
            'mamora': 'samples_mamora_2024.csv',
            'haut_atlas_ouest': 'samples_haut_atlas_ouest_2024.csv',
            'haut_atlas_est': 'samples_haut_atlas_est_2024.csv',
            'haut_atlas_nord': 'samples_haut_atlas_nord_2024.csv',
            'haut_atlas_sud': 'samples_haut_atlas_sud_2024.csv',
            'argan_nord_ouest': 'samples_argan_nord_ouest_2024.csv',
            'argan_nord_est': 'samples_argan_nord_est_2024.csv',
            'argan_sud_ouest': 'samples_argan_sud_ouest_2024.csv',
            'argan_sud_est': 'samples_argan_sud_est_2024.csv'
        }
        
        loaded_data = []
        
        for region_detail, filename in sample_files.items():
            filepath = self.data_folder / filename
            
            if filepath.exists():
                try:
                    df = pd.read_csv(filepath)
                    region_main = self._get_main_region(region_detail)
                    
                    df['region_detail'] = region_detail
                    df['region_main'] = region_main
                    df['data_type'] = 'sample'
                    df['file_source'] = filename
                    
                    if region_main in self.region_configs:
                        config = self.region_configs[region_main]
                        df['ecosystem_type'] = config['ecosystem']
                        df['dominant_species'] = config['species']
                        df['climate_type'] = config['climate']
                    
                    df = self._standardize_coordinate_columns(df)
                    loaded_data.append(df)
                    print(f"   {filename}: {len(df)} points ({region_main})")
                    
                except Exception as e:
                    print(f"   Erreur {filename}: {e}")
            else:
                print(f"   {filename}: Non trouvé")
        
        if loaded_data:
            self.datasets['samples_all'] = pd.concat(loaded_data, ignore_index=True)
            print(f"\nTotal samples: {len(self.datasets['samples_all'])} points")
            
            main_region_stats = self.datasets['samples_all']['region_main'].value_counts()
            for region, count in main_region_stats.items():
                print(f"     • {region}: {count} points")
        
        return loaded_data
    
    def _standardize_coordinate_columns(self, df):
        """Standardiser les noms des colonnes de coordonnées"""
        for col in df.columns:
            col_lower = col.lower()
            
            if any(x in col_lower for x in ['lon', 'x', 'lng']) and 'longitude' not in df.columns:
                df = df.rename(columns={col: 'longitude'})
            elif any(x in col_lower for x in ['lat', 'y']) and 'latitude' not in df.columns:
                df = df.rename(columns={col: 'latitude'})
        
        if '.geo' in df.columns and ('longitude' not in df.columns or 'latitude' not in df.columns):
            try:
                import json
                geo_sample = df['.geo'].iloc[0]
                if isinstance(geo_sample, str):
                    geo_data = json.loads(geo_sample)
                    if 'coordinates' in geo_data:
                        coords = geo_data['coordinates']
                        if len(coords) >= 2:
                            df['longitude'] = df['.geo'].apply(lambda x: json.loads(x)['coordinates'][0] if pd.notna(x) else None)
                            df['latitude'] = df['.geo'].apply(lambda x: json.loads(x)['coordinates'][1] if pd.notna(x) else None)
            except:
                pass
        
        return df
    
    def load_timeseries_files(self):
        """Charger les fichiers timeseries"""
        print("\nChargement des fichiers timeseries...")
        
        timeseries_files = {
            'rif': 'timeseries_samples_rif_2024.csv',
            'moyen_atlas': 'timeseries_samples_moyen_atlas_2024.csv',
            'mamora': 'timeseries_samples_mamora_2024.csv',
            'haut_atlas': 'timeseries_samples_haut_atlas_2024.csv',
            'argan': 'timeseries_samples_argan_2024.csv'
        }
        
        loaded_timeseries = []
        
        for region_name, filename in timeseries_files.items():
            filepath = self.data_folder / filename
            
            if filepath.exists():
                try:
                    df = pd.read_csv(filepath)
                    df['region_main'] = region_name
                    df['data_type'] = 'timeseries'
                    df['file_source'] = filename
                    df = self._standardize_coordinate_columns(df)
                    
                    loaded_timeseries.append(df)
                    print(f"   {filename}: {len(df)} points")
                    
                except Exception as e:
                    print(f"   Erreur {filename}: {e}")
            else:
                print(f"   {filename}: Non trouvé")
        
        if loaded_timeseries:
            self.datasets['timeseries_all'] = pd.concat(loaded_timeseries, ignore_index=True)
            print(f"\nTotal timeseries: {len(self.datasets['timeseries_all'])} points")
        
        return loaded_timeseries
    
    def _get_main_region(self, region_detail):
        """Mapper région détaillée vers région principale"""
        if 'haut_atlas' in region_detail:
            return 'haut_atlas'
        elif 'argan' in region_detail:
            return 'argan'
        else:
            return region_detail
    
    def create_master_dataset(self):
        """Créer le dataset maître avec fusion robuste"""
        print("\nCréation du dataset maître...")
        
        if 'samples_all' not in self.datasets:
            print("Charger d'abord les fichiers samples")
            return
        
        master = self.datasets['samples_all'].copy()
        
        if 'timeseries_all' in self.datasets:
            timeseries = self.datasets['timeseries_all']
            
            has_coords_master = 'longitude' in master.columns and 'latitude' in master.columns
            has_coords_timeseries = 'longitude' in timeseries.columns and 'latitude' in timeseries.columns
            
            if has_coords_master and has_coords_timeseries:
                print("   Fusion avec données temporelles (coordonnées)...")
                
                master['lat_round'] = master['latitude'].round(4)
                master['lon_round'] = master['longitude'].round(4)
                timeseries['lat_round'] = timeseries['latitude'].round(4)
                timeseries['lon_round'] = timeseries['longitude'].round(4)
                
                temporal_cols = ['NDVI_2020', 'NDVI_2021', 'NDVI_2022', 'NDVI_2023', 'NDVI_2024']
                available_temporal_cols = [col for col in temporal_cols if col in timeseries.columns]
                
                if available_temporal_cols:
                    timeseries_subset = timeseries[['region_main', 'lat_round', 'lon_round'] + available_temporal_cols]
                    
                    master = master.merge(
                        timeseries_subset,
                        on=['region_main', 'lat_round', 'lon_round'],
                        how='left',
                        suffixes=('', '_temporal')
                    )
                    
                    master = master.drop(['lat_round', 'lon_round'], axis=1)
                    print(f"   Fusion réussie: {len(available_temporal_cols)} variables temporelles")
                else:
                    print("   Aucune variable temporelle NDVI trouvée")
            else:
                print("   Fusion basée sur région uniquement...")
                
                temporal_cols = ['NDVI_2020', 'NDVI_2021', 'NDVI_2022', 'NDVI_2023', 'NDVI_2024']
                available_temporal_cols = [col for col in temporal_cols if col in timeseries.columns]
                
                if available_temporal_cols:
                    timeseries_regional = timeseries.groupby('region_main')[available_temporal_cols].mean().reset_index()
                    timeseries_regional.columns = ['region_main'] + [f'{col}_regional_avg' for col in available_temporal_cols]
                    
                    master = master.merge(timeseries_regional, on='region_main', how='left')
                    print(f"   Fusion régionale réussie")
        
        self.datasets['master'] = master
        print(f"\nDataset maître créé: {len(master)} points, {len(master.columns)} variables")
        
        return master
    
    def add_available_derived_variables(self):
        """Ajouter seulement les variables dérivées possibles"""
        print("\nAjout des variables dérivées...")
        
        if 'master' not in self.datasets:
            print("Créer d'abord le dataset maître")
            return
        
        df = self.datasets['master'].copy()
        initial_cols = len(df.columns)
        
        df = self._add_available_spectral_features(df)
        df = self._add_available_ecological_classifications(df)
        df = self._add_available_temporal_metrics(df)
        df = self._add_available_topographic_features(df)
        df = self._add_available_health_stress_indices(df)
        df = self._add_available_region_alerts(df)
        
        self.datasets['master'] = df
        added_vars = len(df.columns) - initial_cols
        print(f"\n{added_vars} variables dérivées ajoutées. Total: {len(df.columns)}")
        
        return df
    
    def _add_available_spectral_features(self, df):
        """Ajouter ratios spectraux seulement si bandes disponibles"""
        added = 0
        
        if all(col in df.columns for col in ['B8', 'B4']):
            df['B8_B4_ratio'] = df['B8'] / (df['B4'] + 0.001)
            added += 1
            
        if all(col in df.columns for col in ['B11', 'B8']):
            df['B11_B8_ratio'] = df['B11'] / (df['B8'] + 0.001)
            added += 1
            
        if all(col in df.columns for col in ['B12', 'B11']):
            df['B12_B11_ratio'] = df['B12'] / (df['B11'] + 0.001)
            added += 1
        
        if all(col in df.columns for col in ['B5', 'B4']):
            df['RedEdge_Red_ratio'] = df['B5'] / (df['B4'] + 0.001)
            added += 1
            
        if all(col in df.columns for col in ['B7', 'B6']):
            df['RedEdge_slope'] = (df['B7'] - df['B6']) / (783 - 740)
            added += 1
        
        if all(col in df.columns for col in ['B2', 'B3', 'B4']):
            df['visible_brightness'] = (df['B2'] + df['B3'] + df['B4']) / 3
            added += 1
            
        if added > 0:
            print(f"     {added} ratios spectraux ajoutés")
        
        return df
    
    def _add_available_ecological_classifications(self, df):
        """Classifications écologiques selon données disponibles"""
        added = 0
        
        if 'NDVI' in df.columns:
            df['health_category'] = pd.cut(
                df['NDVI'],
                bins=[-1, 0.2, 0.35, 0.5, 0.65, 1.0],
                labels=['Très Dégradé', 'Dégradé', 'Moyen', 'Bon', 'Excellent'],
                include_lowest=True
            )
            added += 1
        
        if 'NDMI' in df.columns:
            df['water_stress_level'] = pd.cut(
                df['NDMI'],
                bins=[-1, -0.2, 0, 0.2, 0.4, 1.0],
                labels=['Stress Extrême', 'Stress Sévère', 'Stress Modéré', 'Stress Faible', 'Pas de Stress'],
                include_lowest=True
            )
            added += 1
        
        if 'elevation' in df.columns:
            df['ecological_zone'] = pd.cut(
                df['elevation'],
                bins=[0, 800, 1500, 2500, 3200, 5000],
                labels=['Thermophile', 'Mésophile', 'Montagnard', 'Subalpin', 'Alpin'],
                include_lowest=True
            )
            added += 1
        
        if 'precipitation' in df.columns:
            df['bioclimate'] = pd.cut(
                df['precipitation'],
                bins=[0, 200, 400, 600, 800, 2000],
                labels=['Aride', 'Semi-aride', 'Sub-humide', 'Humide', 'Très humide'],
                include_lowest=True
            )
            added += 1
        
        if added > 0:
            print(f"     {added} classifications écologiques ajoutées")
        
        return df
    
    def _add_available_temporal_metrics(self, df):
        """Métriques temporelles selon données disponibles"""
        temporal_patterns = ['NDVI_202', '_regional_avg']
        temporal_cols = []
        
        for col in df.columns:
            if any(pattern in col for pattern in temporal_patterns) and 'NDVI' in col:
                temporal_cols.append(col)
        
        if len(temporal_cols) >= 3:
            print(f"     Calcul métriques temporelles sur {len(temporal_cols)} variables")
            
            if len(temporal_cols) >= 2:
                first_year = df[temporal_cols[0]]
                last_year = df[temporal_cols[-1]]
                df['ndvi_trend'] = (last_year - first_year) / (len(temporal_cols) - 1)
            
            df['ndvi_volatility'] = df[temporal_cols].std(axis=1)
            df['temporal_stability'] = 1 - (df['ndvi_volatility'] / (df[temporal_cols].mean(axis=1) + 0.001))
            
            print(f"     3 métriques temporelles ajoutées")
        else:
            print(f"     Métriques temporelles non calculées ({len(temporal_cols)} colonnes)")
        
        return df
    
    def _add_available_topographic_features(self, df):
        """Variables topographiques selon données disponibles"""
        added = 0
        
        if 'aspect' in df.columns and 'slope' in df.columns:
            df['northness'] = df['slope'] * np.cos(np.radians(df['aspect']))
            df['eastness'] = df['slope'] * np.sin(np.radians(df['aspect']))
            added += 2
            
            def classify_aspect(aspect):
                if pd.isna(aspect):
                    return 'Unknown'
                elif 315 <= aspect or aspect < 45:
                    return 'Nord'
                elif 45 <= aspect < 135:
                    return 'Est'
                elif 135 <= aspect < 225:
                    return 'Sud'
                else:
                    return 'Ouest'
            
            df['aspect_class'] = df['aspect'].apply(classify_aspect)
            added += 1
        
        if 'precipitation' in df.columns and 'slope' in df.columns:
            df['topographic_wetness_index'] = np.log((df['precipitation'] + 1) / (df['slope'] + 0.1))
            added += 1
        
        if added > 0:
            print(f"     {added} variables topographiques ajoutées")
        
        return df
    
    def _add_available_health_stress_indices(self, df):
        """Indices de santé et stress selon données disponibles"""
        added = 0
        
        if all(col in df.columns for col in ['NDVI', 'NDMI']):
            df['forest_health_score'] = (df['NDVI'] + df['NDMI']) / 2
            added += 1
        
        if all(col in df.columns for col in ['NDVI', 'EVI', 'NDMI']):
            df['vegetation_vigor_index'] = (df['NDVI'] + df['EVI'] + df['NDMI']) / 3
            added += 1
        
        if 'NDMI' in df.columns:
            df['stress_index'] = 1 - (df['NDMI'] + 1) / 2
            added += 1
        
        if all(col in df.columns for col in ['NDMI', 'NBR']):
            if 'temperature' in df.columns:
                df['fire_risk_index'] = ((1 - df['NDMI']) * (1 - df['NBR']) * 
                                       (df['temperature'] - 273.15) / 50).clip(0, 1)
            else:
                df['fire_risk_index'] = ((1 - df['NDMI']) * (1 - df['NBR'])).clip(0, 1)
            added += 1
        
        if added > 0:
            print(f"     {added} indices de santé/stress ajoutés")
        
        return df
    
    def _add_available_region_alerts(self, df):
        """Système d'alertes selon données et seuils disponibles"""
        if 'region_main' not in df.columns:
            print("Alertes non calculées: region_main manquante")
            return df
        
        df['alert_level'] = 'Normal'
        df['alert_color'] = 'Green'
        df['alert_priority'] = 0
        
        for region, config in self.region_configs.items():
            region_mask = df['region_main'] == region
            if not region_mask.any():
                continue
                
            thresholds = config['thresholds']
            critical_conditions = []
            
            if 'NDVI' in df.columns:
                critical_conditions.append(df.loc[region_mask, 'NDVI'] < thresholds['ndvi_critical'])
                
            if 'NDMI' in df.columns:
                critical_conditions.append(df.loc[region_mask, 'NDMI'] < thresholds['ndmi_critical'])
                
            if 'EVI' in df.columns:
                critical_conditions.append(df.loc[region_mask, 'EVI'] < thresholds['evi_critical'])
            
            if critical_conditions:
                critical_count = sum(cond.astype(int) for cond in critical_conditions)
                
                df.loc[region_mask & (critical_count == 0), ['alert_level', 'alert_color', 'alert_priority']] = ['Normal', 'Green', 0]
                df.loc[region_mask & (critical_count == 1), ['alert_level', 'alert_color', 'alert_priority']] = ['Attention', 'Yellow', 1]
                df.loc[region_mask & (critical_count == 2), ['alert_level', 'alert_color', 'alert_priority']] = ['Alerte', 'Orange', 2]
                df.loc[region_mask & (critical_count >= 3), ['alert_level', 'alert_color', 'alert_priority']] = ['Critique', 'Red', 3]
        
        print(f"Système d'alertes configuré pour {len(self.region_configs)} régions")
        return df
    
    def generate_alert_summary(self):
        """Générer un résumé des alertes par région"""
        if 'master' not in self.datasets:
            print("Dataset maître non disponible")
            return
        
        df = self.datasets['master']
        
        print("\nRESUME DES ALERTES PAR REGION")
        print("=" * 60)
        
        if 'alert_level' not in df.columns:
            print("Système d'alertes non disponible")
            
            if 'NDVI' in df.columns and 'region_main' in df.columns:
                print("\nResume basé sur NDVI:")
                for region in df['region_main'].unique():
                    if pd.isna(region):
                        continue
                    region_data = df[df['region_main'] == region]
                    config = self.region_configs.get(region, {})
                    print(f"\n{config.get('name', region).upper()}")
                    print(f"   Total: {len(region_data)} points")
                    ndvi_mean = region_data['NDVI'].mean()
                    print(f"   NDVI moyen: {ndvi_mean:.3f}")
                    excellent = len(region_data[region_data['NDVI'] > 0.6])
                    good = len(region_data[(region_data['NDVI'] > 0.4) & (region_data['NDVI'] <= 0.6)])
                    poor = len(region_data[region_data['NDVI'] <= 0.4])
                    total = len(region_data) if len(region_data) > 0 else 1
                    print(f"   Excellente (>0.6): {excellent} ({excellent/total*100:.1f}%)")
                    print(f"   Modérée (0.4-0.6): {good} ({good/total*100:.1f}%)")
                    print(f"   Dégradée (<0.4): {poor} ({poor/total*100:.1f}%)")
            return
        
        for region in df['region_main'].unique():
            if pd.isna(region):
                continue
            region_data = df[df['region_main'] == region]
            config = self.region_configs.get(region, {})
            print(f"\n{config.get('name', region).upper()}")
            print(f"   Total: {len(region_data)} points")
            alert_counts = region_data['alert_level'].value_counts()
            total_points = len(region_data)
            for level in ['Normal', 'Attention', 'Alerte', 'Critique']:
                count = alert_counts.get(level, 0)
                percentage = (count / total_points * 100) if total_points > 0 else 0
                print(f"   {level}: {count} ({percentage:.1f}%)")
            if 'NDVI' in region_data.columns:
                ndvi_mean = region_data['NDVI'].mean()
                print(f"   NDVI moyen: {ndvi_mean:.3f}")
    
    def save_processed_datasets(self, output_folder="processed_data"):
        """Sauvegarder tous les datasets traités"""
        print(f"\nSauvegarde dans {output_folder}/...")
        
        output_path = Path(output_folder)
        output_path.mkdir(exist_ok=True)
        saved_files = []
        
        if 'master' in self.datasets:
            master_file = output_path / "forest_digital_twin_master.csv"
            try:
                self.datasets['master'].to_csv(master_file, index=False)
                saved_files.append(master_file.name)
                print(f"   {master_file.name}: {len(self.datasets['master'])} lignes")
            except Exception as e:
                print(f"   Erreur master: {e}")
        
        if 'master' in self.datasets and 'region_main' in self.datasets['master'].columns:
            try:
                for region in self.datasets['master']['region_main'].unique():
                    if not pd.isna(region):
                        region_data = self.datasets['master'][self.datasets['master']['region_main'] == region]
                        region_file = output_path / f"forest_dt_{region}_complete.csv"
                        region_data.to_csv(region_file, index=False)
                        saved_files.append(region_file.name)
                        print(f"   {region_file.name}: {len(region_data)} lignes")
            except Exception as e:
                print(f"   ⚠️  Sauvegarde régions échouée: {e}")
        
        if 'samples_all' in self.datasets and 'master' not in self.datasets:
            simple_file = output_path / "forest_samples_combined.csv"
            try:
                self.datasets['samples_all'].to_csv(simple_file, index=False)
                saved_files.append(simple_file.name)
                print(f"   {simple_file.name}: {len(self.datasets['samples_all'])} lignes")
            except Exception as e:
                print(f"   Erreur simple: {e}")
        
        if 'timeseries_all' in self.datasets:
            timeseries_file = output_path / "forest_timeseries_combined.csv"
            try:
                self.datasets['timeseries_all'].to_csv(timeseries_file, index=False)
                saved_files.append(timeseries_file.name)
                print(f"   {timeseries_file.name}: {len(self.datasets['timeseries_all'])} lignes")
            except Exception as e:
                print(f"   Erreur timeseries: {e}")
        
        try:
            metadata_file = output_path / "dataset_metadata.txt"
            self._save_metadata(metadata_file)
            saved_files.append(metadata_file.name)
        except Exception as e:
            print(f"   Métadonnées non sauvegardées: {e}")
        
        print(f"\n{len(saved_files)} fichiers sauvegardés")
        return saved_files
    
    def _save_metadata(self, filepath):
        """Sauvegarder métadonnées du dataset"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("# FOREST DIGITAL TWIN - METADATA\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"Date: {pd.Timestamp.now()}\n")
            f.write(f"Version: 2.0\n\n")
            
            f.write("## DATASETS\n")
            for name, dataset in self.datasets.items():
                if isinstance(dataset, pd.DataFrame):
                    f.write(f"- {name}: {len(dataset)} lignes, {len(dataset.columns)} colonnes\n")
            
            f.write("\n## RÉGIONS\n")
            for region, config in self.region_configs.items():
                f.write(f"\n### {config['name']}\n")
                f.write(f"- Écosystème: {config['ecosystem']}\n")
                f.write(f"- Espèces: {config['species']}\n")
                f.write(f"- Climat: {config['climate']}\n")
            
            f.write("\n## VARIABLES\n")
            if 'master' in self.datasets:
                for col in sorted(self.datasets['master'].columns):
                    f.write(f"- {col}\n")

    def show_dataset_diagnostic(self):
        """Diagnostic complet du dataset"""
        print("\nDIAGNOSTIC COMPLET")
        print("=" * 50)
        
        if 'master' not in self.datasets:
            print("Dataset maître non disponible")
            return
        
        df = self.datasets['master']
        
        print(f"Dataset: {len(df):,} lignes × {len(df.columns)} colonnes")
        print(f"   Taille: {df.memory_usage(deep=True).sum() / 1024**2:.1f} MB")
        
        if 'region_main' in df.columns:
            print(f"\nRepartition regionale:")
            region_counts = df['region_main'].value_counts()
            for region, count in region_counts.items():
                print(f"   - {region}: {count:,} ({count/len(df)*100:.1f}%)")
        
        key_vars = ['NDVI', 'NDMI', 'EVI', 'NBR', 'elevation', 'temperature', 'precipitation']
        available = [var for var in key_vars if var in df.columns]
        missing = [var for var in key_vars if var not in df.columns]
        
        print(f"\nVariables clés:")
        print(f"   Disponibles ({len(available)}): {available}")
        if missing:
            print(f"   Manquantes ({len(missing)}): {missing}")
        
        total_cells = len(df) * len(df.columns)
        missing_cells = df.isnull().sum().sum()
        completeness = (1 - missing_cells / total_cells) * 100
        print(f"\nQualité: {completeness:.1f}% complétude")
    
    def diagnostic_mode(self):
        """Mode diagnostic en cas d'erreur"""
        print("\nMODE DIAGNOSTIC")
        print("=" * 50)
        
        sample_files = ['samples_rif_2024.csv', 'samples_moyen_atlas_2024.csv', 'samples_mamora_2024.csv']
        
        for filename in sample_files:
            filepath = self.data_folder / filename
            if filepath.exists():
                try:
                    df = pd.read_csv(filepath, nrows=5)
                    print(f"\n{filename}")
                    print(f"   Taille: {df.shape}")
                    print(f"   Colonnes: {list(df.columns)[:10]}{'...' if len(df.columns) > 10 else ''}")
                    if '.geo' in df.columns:
                        print("   Format .geo détecté")
                        
                    coords = [col for col in df.columns if any(x in col.lower() for x in ['lat', 'lon', 'x', 'y'])]
                    if coords:
                        print(f"   Coordonnées: {coords}")
                    
                    break
                    
                except Exception as e:
                    print(f"\n{filename}: {e}")
        
        print("\nSuggestions:")
        print("   1. Vérifiez noms fichiers")
        print("   2. Vérifiez dossier correct") 
        print("   3. Vérifiez encodage UTF-8")


def main():
    """Pipeline principal de traitement Forest Digital Twin"""
    print("FOREST DIGITAL TWIN - PIPELINE v2.0")
    print("=" * 60)
    
    processor = ForestDigitalTwinProcessor(data_folder=".")
    
    try:
        processor.load_all_data()
        processor.show_dataset_diagnostic()
        
        if 'master' in processor.datasets:
            processor.generate_alert_summary()
        
        processor.save_processed_datasets()
        
        print("\nPIPELINE TERMINÉ AVEC SUCCÈS!")
        
    except Exception as e:
        print(f"\nErreur pipeline: {e}")
        processor.diagnostic_mode()
    
    return processor

def quick_diagnostic():
    """Diagnostic rapide de la structure"""
    print("DIAGNOSTIC RAPIDE")
    print("=" * 30)
    
    processor = ForestDigitalTwinProcessor(data_folder=".")
    columns = processor.inspect_data_structure()
    
    if columns:
        print(f"\nStructure: {len(columns)} colonnes")
        
        spectral = [col for col in columns if col.startswith('B') and col[1:].isdigit()]
        vegetation = [col for col in columns if col in ['NDVI', 'EVI', 'NDMI', 'NBR', 'GNDVI', 'SAVI']]
        topo = [col for col in columns if col in ['elevation', 'slope', 'aspect']]
        climate = [col for col in columns if col in ['temperature', 'precipitation']]
        
        print("\nIdentifiees:")
        print(f"   Spectrales: {len(spectral)} {spectral[:5]}")
        print(f"   Vegetation: {len(vegetation)} {vegetation}")
        print(f"   Topo: {len(topo)} {topo}")
        print(f"   Climat: {len(climate)} {climate}")
        
        return True
    else:
        print("Aucune donnée détectée")
        return False

def test_data_loading():
    """Test rapide du chargement"""
    print("TEST CHARGEMENT")
    print("=" * 25)
    
    test_files = [
        'samples_rif_2024.csv',
        'samples_moyen_atlas_2024.csv',
        'samples_mamora_2024.csv',
        'samples_haut_atlas_ouest_2024.csv',
        'samples_argan_nord_ouest_2024.csv'
    ]
    
    loaded_count = 0
    total_points = 0
    
    for filename in test_files:
        if os.path.exists(filename):
            try:
                df = pd.read_csv(filename)
                print(f"{filename}: {len(df)} points")
                loaded_count += 1
                total_points += len(df)
            except Exception as e:
                print(f"{filename}: {e}")
        else:
            print(f"{filename}: Non trouvé")
    
    print(f"\nResume: {loaded_count}/{len(test_files)} fichiers, {total_points:,} points")
    
    if loaded_count > 0:
        print("Donnees accessibles")
        return True
    else:
        print("Aucun fichier chargé")
        return False

def simple_combine():
    """Combinaison simple sans variables dérivées"""
    print("COMBINAISON SIMPLE")
    print("=" * 30)
    
    sample_files = {
        'rif': 'samples_rif_2024.csv',
        'moyen_atlas': 'samples_moyen_atlas_2024.csv',
        'mamora': 'samples_mamora_2024.csv'
    }
    
    haut_atlas_files = {
        'haut_atlas_ouest': 'samples_haut_atlas_ouest_2024.csv',
        'haut_atlas_est': 'samples_haut_atlas_est_2024.csv',
        'haut_atlas_nord': 'samples_haut_atlas_nord_2024.csv',
        'haut_atlas_sud': 'samples_haut_atlas_sud_2024.csv'
    }
    
    argan_files = {
        'argan_nord_ouest': 'samples_argan_nord_ouest_2024.csv',
        'argan_nord_est': 'samples_argan_nord_est_2024.csv',
        'argan_sud_ouest': 'samples_argan_sud_ouest_2024.csv',
        'argan_sud_est': 'samples_argan_sud_est_2024.csv'
    }
    
    all_data = []
    
    for region, filename in sample_files.items():
        if os.path.exists(filename):
            try:
                df = pd.read_csv(filename)
                df['region'] = region
                df['region_type'] = 'simple'
                all_data.append(df)
                print(f"{region}: {len(df)} points")
            except Exception as e:
                print(f"{filename}: {e}")
    
    haut_atlas_data = []
    for sub_region, filename in haut_atlas_files.items():
        if os.path.exists(filename):
            try:
                df = pd.read_csv(filename)
                df['sub_region'] = sub_region
                haut_atlas_data.append(df)
                print(f"✅ {sub_region}: {len(df)} points")
            except Exception as e:
                print(f"❌ {filename}: {e}")
    
    if haut_atlas_data:
        haut_atlas_combined = pd.concat(haut_atlas_data, ignore_index=True)
        haut_atlas_combined['region'] = 'haut_atlas'
        haut_atlas_combined['region_type'] = 'combined'
        all_data.append(haut_atlas_combined)
        print(f"Haut Atlas: {len(haut_atlas_combined)} points")
    
    argan_data = []
    for sub_region, filename in argan_files.items():
        if os.path.exists(filename):
            try:
                df = pd.read_csv(filename)
                df['sub_region'] = sub_region
                argan_data.append(df)
                print(f"✅ {sub_region}: {len(df)} points")
            except Exception as e:
                print(f"❌ {filename}: {e}")
    
    if argan_data:
        argan_combined = pd.concat(argan_data, ignore_index=True)
        argan_combined['region'] = 'argan'
        argan_combined['region_type'] = 'combined'
        all_data.append(argan_combined)
        print(f"Argan: {len(argan_combined)} points")
    
    if all_data:
        morocco_complete = pd.concat(all_data, ignore_index=True)
        morocco_complete.to_csv('morocco_forest_complete_simple.csv', index=False)
        print(f"\nDataset créé: {len(morocco_complete)} points")
        print(f"Fichier: morocco_forest_complete_simple.csv")
        
        region_stats = morocco_complete['region'].value_counts()
        for region, count in region_stats.items():
            print(f"   • {region}: {count} points")
        
        key_vars = ['NDVI', 'NDMI', 'EVI', 'elevation', 'temperature']
        available_vars = [var for var in key_vars if var in morocco_complete.columns]
        print(f"\nVariables clés: {available_vars}")
        
        return morocco_complete
    else:
        print("Aucune donnée chargée")
        return None


if __name__ == "__main__":
    print("DEMARRAGE AUTOMATIQUE")
    print("=" * 30)
    
    if test_data_loading():
        print("\nLancement combinaison...")
        result = simple_combine()
        
        if result is not None:
            print("\nSUCCES! Lancez main() pour l'analyse complète")
        else:
            print("\nCombinaison partielle")
    else:
        print("\nAucune donnée. Vérifiez les fichiers CSV")