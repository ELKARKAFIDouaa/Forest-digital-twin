import React from 'react';
import { Battery, MapPin, Activity, AlertTriangle, Edit, Trash } from 'lucide-react';
import { Sensor } from '../../types';

interface SensorCardProps {
  sensor: Sensor;
  onClick?: () => void;
  onEdit?: () => void;
  onDelete?: () => void;
}

const SensorCard: React.FC<SensorCardProps> = ({ sensor, onClick, onEdit, onDelete }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-emerald-100 text-emerald-800 border-emerald-200';
      case 'inactive':
        return 'bg-gray-100 text-gray-800 border-gray-200';
      case 'maintenance':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getQualityColor = (quality: string) => {
    switch (quality) {
      case 'good':
        return 'text-emerald-600';
      case 'warning':
        return 'text-yellow-600';
      case 'critical':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  const getBatteryColor = (level: number) => {
    if (level > 50) return 'text-emerald-600';
    if (level > 20) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="relative bg-white rounded-xl border border-gray-200 p-6 hover:shadow-lg transition-all cursor-pointer group" onClick={onClick}>
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-1">{sensor.name}</h3>
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <MapPin className="w-4 h-4" />
            <span>{sensor.zone ?? '—'}</span>
          </div>
        </div>
        <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(sensor.status)}`}>
          {sensor.status}
        </span>
      </div>

      {/* Last reading */}
      <div className="mb-4">
        <div className="flex items-center space-x-2 mb-2">
          <Activity className={`w-4 h-4 ${getQualityColor(sensor.lastReading?.quality ?? 'good')}`} />
          <span className="text-sm text-gray-600">Dernière lecture</span>
        </div>
        <div className="flex items-baseline space-x-2">
          <span className="text-2xl font-bold text-gray-900">{sensor.lastReading?.value ?? '--'}</span>
          <span className="text-sm text-gray-600">{sensor.lastReading?.unit ?? ''}</span>
        </div>
        <p className="text-xs text-gray-500 mt-1">
          {sensor.lastReading?.timestamp
            ? new Date(sensor.lastReading.timestamp).toLocaleString('fr-FR')
            : 'Aucune donnée'}
        </p>
      </div>

      {/* Battery */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Battery className={`w-4 h-4 ${getBatteryColor(sensor.batteryLevel ?? 100)}`} />
          <span className="text-sm text-gray-600">Batterie</span>
        </div>
        <span className={`text-sm font-medium ${getBatteryColor(sensor.batteryLevel ?? 100)}`}>
          {sensor.batteryLevel ?? 100}%
        </span>
      </div>

      {/* Low battery warning */}
      {sensor.batteryLevel !== undefined && sensor.batteryLevel < 30 && (
        <div className="mt-3 flex items-center space-x-2 text-yellow-600 bg-yellow-50 px-3 py-2 rounded-lg">
          <AlertTriangle className="w-4 h-4" />
          <span className="text-sm">Batterie faible</span>
        </div>
      )}

      {/* Edit/Delete overlay on hover */}
      <div className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 flex space-x-2 transition-opacity">
        {onEdit && (
          <button
            onClick={(e) => { e.stopPropagation(); onEdit(); }}
            className="p-1 rounded bg-blue-100 text-blue-600 hover:bg-blue-200"
          >
            <Edit className="w-4 h-4" />
          </button>
        )}
        {onDelete && (
          <button
            onClick={(e) => { e.stopPropagation(); onDelete(); }}
            className="p-1 rounded bg-red-100 text-red-600 hover:bg-red-200"
          >
            <Trash className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  );
};

export default SensorCard;
