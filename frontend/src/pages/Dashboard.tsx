import React, { useState, useEffect } from 'react';
import { Activity, Thermometer, Droplets, Wind, AlertTriangle } from 'lucide-react';
import StatsCard from '../components/Dashboard/StatsCard';
import EnvironmentalChart from '../components/Dashboard/EnvironmentalChart';
import { DashboardStats } from '../types';
import * as dashboardAPI from '../services/dashboardAPI';
import LoadingSpinner from '../components/Common/LoadingSpinner';

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [environmentalData, setEnvironmentalData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
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

    fetchData();
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Tableau de bord</h1>
        <p className="text-gray-600 mt-2">
          Vue d'ensemble de votre système de surveillance environnementale
        </p>
      </div>

      {/* Stats cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatsCard
            title="Capteurs totaux"
            value={stats.totalSensors}
            change={{ value: 12, type: 'increase' }}
            icon={Activity}
            color="blue"
          />
          <StatsCard
            title="Capteurs actifs"
            value={stats.activeSensors}
            change={{ value: 5, type: 'increase' }}
            icon={Activity}
            color="green"
          />
          <StatsCard
            title="Alertes critiques"
            value={stats.criticalAlerts}
            change={{ value: 8, type: 'decrease' }}
            icon={AlertTriangle}
            color="red"
          />
          <StatsCard
            title="Points de données"
            value={stats.dataPoints.toLocaleString()}
            change={{ value: 23, type: 'increase' }}
            icon={Activity}
            color="purple"
          />
        </div>
      )}

      {/* Environmental charts */}
      {environmentalData && (
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          <EnvironmentalChart
            title="Température"
            data={environmentalData.temperature}
            color="#10b981"
            unit="°C"
          />
          <EnvironmentalChart
            title="Humidité"
            data={environmentalData.humidity}
            color="#3b82f6"
            unit="%"
          />
          <EnvironmentalChart
            title="Qualité de l'air"
            data={environmentalData.airQuality}
            color="#f59e0b"
            unit="AQI"
          />
        </div>
      )}

      {/* Recent alerts */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Alertes récentes</h3>
        <div className="space-y-3">
          {[
            {
              id: 1,
              message: 'Capteur de température A1 - Valeur élevée détectée',
              time: '2 minutes ago',
              severity: 'warning',
            },
            {
              id: 2,
              message: 'Capteur d\'humidité B2 - Batterie faible',
              time: '15 minutes ago',
              severity: 'info',
            },
            {
              id: 3,
              message: 'Capteur de qualité d\'air C1 - Maintenance requise',
              time: '1 hour ago',
              severity: 'critical',
            },
          ].map((alert) => (
            <div key={alert.id} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
              <div className={`w-2 h-2 rounded-full ${
                alert.severity === 'critical' ? 'bg-red-500' :
                alert.severity === 'warning' ? 'bg-yellow-500' : 'bg-blue-500'
              }`} />
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">{alert.message}</p>
                <p className="text-xs text-gray-500">{alert.time}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;