import React, { useState, useEffect } from 'react';
import EnvironmentalChart from '../components/Dashboard/EnvironmentalChart';
import LoadingSpinner from '../components/Common/LoadingSpinner';
import * as dashboardAPI from '../services/dashboardAPI';

const REFRESH_INTERVAL = 5000; // 5 secondes

const Dashboard: React.FC = () => {
  const [environmentalData, setEnvironmentalData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchData = async () => {
    try {
      const envData = await dashboardAPI.getEnvironmentalData();
      setEnvironmentalData(envData);
    } catch (error) {
      console.error('Échec du chargement des données environnementales:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData(); // premier fetch
    const interval = setInterval(fetchData, REFRESH_INTERVAL); // mises à jour en temps réel
    return () => clearInterval(interval);
  }, []);

  if (isLoading) return <LoadingSpinner size="lg" />;

  return (
    <div className="space-y-6">
      {/* Barre supérieure */}
      <h1 className="text-3xl font-bold">Tableau de bord - Données environnementales</h1>

      {/* Graphiques */}
      {environmentalData && (
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          <EnvironmentalChart title="Température" data={environmentalData.temperature} unit="°C" color="red" />
          <EnvironmentalChart title="Humidité" data={environmentalData.humidity} unit="%" color="blue" />
          <EnvironmentalChart title="Qualité de l'air" data={environmentalData.airQuality} unit="AQI" color="green" />
          <EnvironmentalChart title="Pluviométrie" data={environmentalData.rainfall} unit="mm" color="yellow" />
          <EnvironmentalChart title="Vitesse du vent" data={environmentalData.windSpeed} unit="km/h" color="purple" />
          <EnvironmentalChart title="Humidité du sol" data={environmentalData.soilHumidity} unit="%" color="blue" />
          <EnvironmentalChart title="pH du sol" data={environmentalData.soilPH} unit="" color="green" />
        </div>
      )}
    </div>
  );
};

export default Dashboard;
