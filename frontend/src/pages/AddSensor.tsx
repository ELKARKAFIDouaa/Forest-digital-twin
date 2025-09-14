import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import * as sensorAPI from '../services/sensorAPI';
import LoadingSpinner from '../components/Common/LoadingSpinner';
import { Sensor } from '../types';
import { Plus } from 'lucide-react';

const AddSensor: React.FC = () => {
  const navigate = useNavigate();

  // Champs du formulaire
  const [name, setName] = useState('');
  const [category, setCategory] = useState('');
  const [type, setType] = useState('');
  const [unit, setUnit] = useState('');
  const [zone, setZone] = useState('');
  const [latitude, setLatitude] = useState<string>('');
  const [longitude, setLongitude] = useState<string>('');
  const [status, setStatus] = useState<'active' | 'inactive' | 'maintenance'>('active');
  const [minValue, setMinValue] = useState<string>('');
  const [maxValue, setMaxValue] = useState<string>('');

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validation simple
    if (!name || !category || !type || !unit) {
      setError('Veuillez remplir tous les champs obligatoires.');
      return;
    }

    // Création de l'objet Sensor compatible avec l'API
    const newSensor: Partial<Sensor> = {
  name,
  category,
  type,
  unit,
  zone,
  status,
  batteryLevel: 100,
  location: {
    lat: latitude ? parseFloat(latitude) : 0,
    lng: longitude ? parseFloat(longitude) : 0,
    zone,
  },
  lastReading: null,
  min_value: minValue ? parseFloat(minValue) : undefined,
  max_value: maxValue ? parseFloat(maxValue) : undefined,
};

    try {
      setIsLoading(true);
      await sensorAPI.createSensor(newSensor);
      navigate('/sensors'); // retour à la liste après ajout
    } catch (err: any) {
      console.error(err);
      setError('Erreur lors de la création du capteur.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto py-8 space-y-6">
      <div className="flex items-center space-x-3">
        <Plus className="w-6 h-6 text-emerald-600" />
        <h1 className="text-2xl font-bold text-gray-900">Ajouter un capteur</h1>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Nom *</label>
            <input type="text" value={name} onChange={e => setName(e.target.value)}
              className="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Catégorie *</label>
            <input type="text" value={category} onChange={e => setCategory(e.target.value)}
              className="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Type *</label>
            <input type="text" value={type} onChange={e => setType(e.target.value)}
              className="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Unité *</label>
            <input type="text" value={unit} onChange={e => setUnit(e.target.value)}
              className="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Zone</label>
            <input type="text" value={zone} onChange={e => setZone(e.target.value)}
              className="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Statut</label>
            <select value={status} onChange={e => setStatus(e.target.value as 'active' | 'inactive' | 'maintenance')}
              className="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500">
              <option value="active">Actif</option>
              <option value="inactive">Inactif</option>
              <option value="maintenance">Maintenance</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Latitude</label>
            <input type="number" value={latitude} onChange={e => setLatitude(e.target.value)}
              className="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Longitude</label>
            <input type="number" value={longitude} onChange={e => setLongitude(e.target.value)}
              className="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Valeur min</label>
            <input type="number" value={minValue} onChange={e => setMinValue(e.target.value)}
              className="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Valeur max</label>
            <input type="number" value={maxValue} onChange={e => setMaxValue(e.target.value)}
              className="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500" />
          </div>
        </div>

        <div className="flex justify-end space-x-3 mt-4">
          <button type="button" onClick={() => navigate('/sensors')}
            className="px-4 py-2 rounded-lg border border-gray-300 hover:bg-gray-50">Annuler</button>
          <button type="submit" className="px-4 py-2 rounded-lg bg-emerald-600 text-white hover:bg-emerald-700">
            {isLoading ? <LoadingSpinner size="sm" /> : 'Ajouter'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default AddSensor;
