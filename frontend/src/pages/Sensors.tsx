import React, { useState, useEffect } from 'react';
import { Plus, Search, Filter, Edit, Trash } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Sensor } from '../types';
import * as sensorAPI from '../services/sensorAPI';
import LoadingSpinner from '../components/Common/LoadingSpinner';
import SensorCard from '../components/Sensors/SensorCard';

const Sensors: React.FC = () => {
  const [sensors, setSensors] = useState<Sensor[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const navigate = useNavigate();

  // ---------------- Fetch sensors ----------------
  useEffect(() => {
    const fetchSensors = async () => {
      try {
        setIsLoading(true);
        const sensorsData = await sensorAPI.getSensors();
        setSensors(sensorsData);
        setError(null);
      } catch (err: any) {
        setError('Erreur lors de la récupération des capteurs.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchSensors();
  }, []);

  // ---------------- Filters ----------------
  const filteredSensors = sensors.filter(sensor => {
    const matchesSearch =
      sensor.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (sensor.zone ?? '').toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || sensor.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  // ---------------- Handlers ----------------
  const handleDelete = async (sensorId: string) => {
    if (!window.confirm("Voulez-vous vraiment supprimer ce capteur ?")) return;
    try {
      await sensorAPI.deleteSensor(sensorId);
      setSensors(prev => prev.filter(s => s.id !== sensorId));
    } catch (err) {
      alert("Erreur lors de la suppression du capteur.");
    }
  };

  const handleEdit = (sensor: Sensor) => {
    navigate(`/sensors/edit/${sensor.id}`);
  };

  const handleSensorClick = (sensorId: string) => {
    navigate(`/sensors/${sensorId}`);
  };

  // ---------------- Render ----------------
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
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Capteurs</h1>
          <p className="text-gray-600 mt-2">
            Gérez et surveillez tous vos capteurs environnementaux
          </p>
        </div>
        <button
  onClick={() => navigate('/sensors/add')}
  className="bg-emerald-600 text-white px-4 py-2 rounded-lg hover:bg-emerald-700 transition-colors flex items-center space-x-2"
>
  <Plus className="w-5 h-5" />
  <span>Ajouter un capteur</span>
</button>

      </div>

      {/* Error message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
          {/* Search */}
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Rechercher des capteurs..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
            />
          </div>

          {/* Status filter */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Filter className="w-5 h-5 text-gray-400" />
              <span className="text-sm font-medium text-gray-700">Statut:</span>
            </div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
            >
              <option value="all">Tous</option>
              <option value="active">Actif</option>
              <option value="inactive">Inactif</option>
              <option value="maintenance">Maintenance</option>
            </select>
          </div>
        </div>
      </div>

      {/* Sensors grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredSensors.map((sensor) => (
          <div key={sensor.id} className="relative group">
            <SensorCard sensor={sensor} onClick={() => handleSensorClick(sensor.id)} />
            <div className="absolute top-2 right-2 hidden group-hover:flex space-x-2">
              <button
                onClick={() => handleEdit(sensor)}
                className="bg-white rounded-full p-2 shadow hover:bg-gray-100"
              >
                <Edit className="w-4 h-4 text-blue-500" />
              </button>
              <button
                onClick={() => handleDelete(sensor.id)}
                className="bg-white rounded-full p-2 shadow hover:bg-gray-100"
              >
                <Trash className="w-4 h-4 text-red-500" />
              </button>
            </div>
          </div>
        ))}
      </div>

      {filteredSensors.length === 0 && !isLoading && (
        <div className="text-center py-12">
          <p className="text-gray-500">
            {searchTerm || statusFilter !== 'all'
              ? "Aucun capteur ne correspond à vos critères de recherche"
              : "Aucun capteur n'est configuré pour le moment"}
          </p>
        </div>
      )}
    </div>
  );
};

export default Sensors;
