import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Search, Filter, Plus, Edit, Trash } from "lucide-react";
import SensorCard from "../components/Sensors/SensorCard";
import { Sensor } from "../types";
import * as sensorsAPI from "../services/sensorAPI";
import { useAuth } from "../contexts/AuthContext";

const Sensors: React.FC = () => {
  const [sensors, setSensors] = useState<Sensor[]>([]);
  const [filteredSensors, setFilteredSensors] = useState<Sensor[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const navigate = useNavigate();
  const { hasRole } = useAuth();

  useEffect(() => {
    const fetchSensors = async () => {
      setIsLoading(true);
      try {
        const data = await sensorsAPI.getSensors();
        setSensors(data);
        setFilteredSensors(data);
      } catch (err) {
        setError("Impossible de charger les capteurs");
      } finally {
        setIsLoading(false);
      }
    };
    fetchSensors();
  }, []);

  useEffect(() => {
    let filtered = [...sensors];
    if (searchTerm) {
      filtered = filtered.filter((s) =>
        s.name.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    if (statusFilter !== "all") {
      filtered = filtered.filter((s) => s.status === statusFilter);
    }
    setFilteredSensors(filtered);
  }, [searchTerm, statusFilter, sensors]);

  const handleSensorClick = (id: string) => {
    navigate(`/sensors/${id}`);
  };

  const handleEdit = (sensor: Sensor) => {
    navigate(`/sensors/${sensor.id}/edit`);
  };

  const handleDelete = async (id: string) => {
    if (window.confirm("Voulez-vous vraiment supprimer ce capteur ?")) {
      try {
        await sensorsAPI.deleteSensor(id);
        setSensors(sensors.filter((s) => s.id !== id));
      } catch {
        setError("Échec de suppression du capteur");
      }
    }
  };

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

        {/* Ajouter → réservé à l’admin */}
        {hasRole("admin") && (
          <button
            onClick={() => navigate("/sensors/add")}
            className="bg-emerald-600 text-white px-4 py-2 rounded-lg hover:bg-emerald-700 transition-colors flex items-center space-x-2"
          >
            <Plus className="w-5 h-5" />
            <span>Ajouter un capteur</span>
          </button>
        )}
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
          <SensorCard
            key={sensor.id}
            sensor={sensor}
            onClick={() => handleSensorClick(sensor.id)}
            // Admin uniquement pour Edit / Delete
            onEdit={hasRole("admin") ? () => handleEdit(sensor) : undefined}
            onDelete={hasRole("admin") ? () => handleDelete(sensor.id) : undefined}
          />
        ))}
      </div>

      {filteredSensors.length === 0 && !isLoading && (
        <div className="text-center py-12">
          <p className="text-gray-500">
            {searchTerm || statusFilter !== "all"
              ? "Aucun capteur ne correspond à vos critères de recherche"
              : "Aucun capteur n'est configuré pour le moment"}
          </p>
        </div>
      )}
    </div>
  );
};

export default Sensors;
