import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getSensorById, updateSensor } from "../services/sensorAPI";
import { Sensor, UpdateSensorData } from "../types";

const EditSensor: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [sensor, setSensor] = useState<Sensor | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    const fetchSensor = async () => {
      try {
        const data = await getSensorById(id);
        setSensor(data);
      } catch {
        setError("Impossible de charger le capteur");
      } finally {
        setLoading(false);
      }
    };
    fetchSensor();
  }, [id]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    if (!sensor) return;
    setSensor({
      ...sensor,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!id || !sensor) return;

    try {
      const updates: UpdateSensorData = {
        name: sensor.name,
        category: sensor.category,
        type: sensor.type,
        unit: sensor.unit,
        status: sensor.status,
        batteryLevel: sensor.batteryLevel,
        zone: sensor.zone,
        latitude: sensor.location.lat,
        longitude: sensor.location.lng,
      };
      await updateSensor(id, updates);
      navigate("/sensors");
    } catch {
      setError("Erreur lors de la mise à jour du capteur");
    }
  };

  if (loading) return <p className="text-center">Chargement...</p>;
  if (error) return <p className="text-red-600">{error}</p>;
  if (!sensor) return <p className="text-gray-500">Capteur introuvable</p>;

  return (
    <div className="max-w-2xl mx-auto bg-white rounded-xl shadow p-6">
      <h1 className="text-2xl font-bold mb-4">Modifier le capteur</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Nom */}
        <div>
          <label className="block text-sm font-medium">Nom</label>
          <input
            type="text"
            name="name"
            value={sensor.name}
            onChange={handleChange}
            className="w-full border px-3 py-2 rounded-lg"
          />
        </div>

        {/* Catégorie */}
        <div>
          <label className="block text-sm font-medium">Catégorie</label>
          <input
            type="text"
            name="category"
            value={sensor.category}
            onChange={handleChange}
            className="w-full border px-3 py-2 rounded-lg"
          />
        </div>

        {/* Type */}
        <div>
          <label className="block text-sm font-medium">Type</label>
          <input
            type="text"
            name="type"
            value={sensor.type}
            onChange={handleChange}
            className="w-full border px-3 py-2 rounded-lg"
          />
        </div>

        {/* Statut */}
        <div>
          <label className="block text-sm font-medium">Statut</label>
          <select
            name="status"
            value={sensor.status}
            onChange={handleChange}
            className="w-full border px-3 py-2 rounded-lg"
          >
            <option value="active">Actif</option>
            <option value="inactive">Inactif</option>
            <option value="maintenance">Maintenance</option>
          </select>
        </div>

        {/* Batterie */}
        <div>
          <label className="block text-sm font-medium">Batterie (%)</label>
          <input
            type="number"
            name="batteryLevel"
            value={sensor.batteryLevel}
            onChange={(e) =>
              setSensor({ ...sensor, batteryLevel: Number(e.target.value) })
            }
            className="w-full border px-3 py-2 rounded-lg"
          />
        </div>

        {/* Zone */}
        <div>
          <label className="block text-sm font-medium">Zone</label>
          <input
            type="text"
            name="zone"
            value={sensor.zone}
            onChange={handleChange}
            className="w-full border px-3 py-2 rounded-lg"
          />
        </div>

        {/* Latitude */}
        <div>
          <label className="block text-sm font-medium">Latitude</label>
          <input
            type="number"
            step="any"
            value={sensor.location.lat}
            onChange={(e) =>
              setSensor({
                ...sensor,
                location: { ...sensor.location, lat: Number(e.target.value) },
              })
            }
            className="w-full border px-3 py-2 rounded-lg"
          />
        </div>

        {/* Longitude */}
        <div>
          <label className="block text-sm font-medium">Longitude</label>
          <input
            type="number"
            step="any"
            value={sensor.location.lng}
            onChange={(e) =>
              setSensor({
                ...sensor,
                location: { ...sensor.location, lng: Number(e.target.value) },
              })
            }
            className="w-full border px-3 py-2 rounded-lg"
          />
        </div>

        <div className="flex justify-end space-x-4">
          <button
            type="button"
            onClick={() => navigate("/sensors")}
            className="px-4 py-2 rounded-lg border"
          >
            Annuler
          </button>
          <button
            type="submit"
            className="bg-emerald-600 text-white px-4 py-2 rounded-lg hover:bg-emerald-700"
          >
            Sauvegarder
          </button>
        </div>
      </form>
    </div>
  );
};

export default EditSensor;
