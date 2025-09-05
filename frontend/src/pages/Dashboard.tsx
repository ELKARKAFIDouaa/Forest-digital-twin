import React, { useState, useEffect } from 'react';
import { DashboardStats } from '../types';
import StatsCard from '../components/Dashboard/StatsCard';
import EnvironmentalChart from '../components/Dashboard/EnvironmentalChart';
import LoadingSpinner from '../components/Common/LoadingSpinner';
import * as dashboardAPI from '../services/dashboardAPI';
import { TrendingUp, TrendingDown, AlertCircle, Activity } from 'lucide-react';

const REFRESH_INTERVAL = 5000; // 5 seconds

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [environmentalData, setEnvironmentalData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchData = async () => {
    try {
      const [statsData, envData] = await Promise.all([
        dashboardAPI.getDashboardStats(),
        dashboardAPI.getEnvironmentalData(),
      ]);
      setStats(statsData);
      setEnvironmentalData(envData);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData(); // initial fetch
    const interval = setInterval(fetchData, REFRESH_INTERVAL); // real-time updates
    return () => clearInterval(interval);
  }, []);

  if (isLoading) return <LoadingSpinner size="lg" />;

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Tableau de bord</h1>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatsCard title="Capteurs totaux" value={stats.totalSensors} icon={Activity} color="blue" />
          <StatsCard title="Capteurs actifs" value={stats.activeSensors} icon={TrendingUp} color="green" />
          <StatsCard title="Alertes critiques" value={stats.criticalAlerts} icon={AlertCircle} color="red" />
          <StatsCard title="Points de données" value={stats.dataPoints.toLocaleString()} icon={TrendingUp} color="purple" />
</div>
        
      )}

      {/* Environmental Charts */}
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
