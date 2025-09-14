import { Sensor, SensorReading, CreateSensorData, UpdateSensorData } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

// Mock sensors for dev/fallback
const mockSensors: Sensor[] = [
  {
    id: '1',
    name: 'Capteur Température',
    category: 'environmental',
    type: 'temperature',
    unit: '°C',
    status: 'active',
    batteryLevel: 85,
    location: {
      lat: 48.8566,
      lng: 2.3522,
      zone: 'Forêt Nord'
    },
    lastReading: {
      id: '101',
      sensorId: '1',
      name: 'Température',
      value: 22.5,
      unit: '°C',
      timestamp: new Date().toISOString(),
      quality: 'good'
    }
  },
  {
    id: '2',
    name: 'Capteur Humidité',
    category: 'environmental',
    type: 'humidity',
    unit: '%',
    status: 'active',
    batteryLevel: 90,
    location: {
      lat: 48.8606,
      lng: 2.3526,
      zone: 'Forêt Sud'
    },
    lastReading: {
      id: '102',
      sensorId: '2',
      name: 'Humidité',
      value: 65.2,
      unit: '%',
      timestamp: new Date().toISOString(),
      quality: 'good'
    }
  }
];

// Helper: headers with token if available
const getAuthHeaders = (): Record<string, string> => {
  const token = localStorage.getItem('token');
  return token
    ? { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` }
    : { 'Content-Type': 'application/json' };
};

// Normalize backend → frontend
const normalizeSensorFromServer = (raw: any): Sensor => ({
  id: raw.id?.toString(),
  name: raw.name,
  category: raw.category || 'environmental',
  type: raw.type,
  unit: raw.unit,
  interface: raw.interface || undefined,
  reference: raw.reference || undefined,
  status: raw.status || 'active',
  batteryLevel: raw.battery_level ?? 100,
  location: {
    lat: raw.latitude ?? 0,
    lng: raw.longitude ?? 0,
    zone: raw.zone || 'Inconnue',
  },
  lastReading: raw.lastReading
    ? {
        id: raw.lastReading.id?.toString(),
        sensorId: raw.lastReading.sensor_id?.toString(),
        name: raw.lastReading.name,
        value: raw.lastReading.value,
        unit: raw.lastReading.unit,
        timestamp: raw.lastReading.timestamp,
        quality: raw.lastReading.quality || 'good',
      }
    : {
        id: null,
        sensorId: raw.id?.toString(),
        name: raw.type,
        value: null, // pas encore de lecture
        unit: raw.unit,
        timestamp: null,
        quality: 'good',
      },
});

// Normalize for readings
const normalizeReadingFromServer = (raw: any): SensorReading => ({
  id: raw.id?.toString(),
  sensorId: raw.sensor_id?.toString(),
  name: raw.name,
  value: raw.value,
  unit: raw.unit,
  timestamp: raw.timestamp,
  quality: raw.quality || 'good',
});

// ------------------- Sensors -------------------
export const getSensors = async (): Promise<Sensor[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/sensors/`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) throw new Error('Failed to fetch sensors');
    const data = await response.json();
    return Array.isArray(data) ? data.map(normalizeSensorFromServer) : [];
  } catch (error) {
    console.warn('Using mock sensors due to error:', error);
    return mockSensors;
  }
};

export const getSensorById = async (id: string): Promise<Sensor> => {
  try {
    const response = await fetch(`${API_BASE_URL}/sensors/${id}`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) throw new Error('Failed to fetch sensor');
    return normalizeSensorFromServer(await response.json());
  } catch (error) {
    const sensor = mockSensors.find(s => s.id === id);
    if (!sensor) throw new Error('Sensor not found');
    console.warn('Using mock sensor due to error:', error);
    return sensor;
  }
};

export const createSensor = async (sensorData: CreateSensorData) => {
  try {
    const response = await fetch(`${API_BASE_URL}/sensors/`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(sensorData),
    });
    if (!response.ok) throw new Error('Failed to create sensor');
    return await response.json();
  } catch (error) {
    console.warn('Create failed, returning mock response:', error);
    return {
      success: true,
      message: 'Mock sensor created',
      id: Date.now().toString(),
    };
  }
};

export const updateSensor = async (id: string, updates: UpdateSensorData) => {
  try {
    const response = await fetch(`${API_BASE_URL}/sensors/${id}`, {
      method: 'PATCH',
      headers: getAuthHeaders(),
      body: JSON.stringify(updates),
    });
    if (!response.ok) throw new Error('Failed to update sensor');
    return await response.json();
  } catch (error) {
    console.warn('Update failed, returning mock response:', error);
    const sensor = mockSensors.find(s => s.id === id);
    if (!sensor) throw new Error('Sensor not found');
    return { ...sensor, ...updates };
  }
};

export const deleteSensor = async (id: string) => {
  try {
    const response = await fetch(`${API_BASE_URL}/sensors/${id}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });
    if (!response.ok) throw new Error('Failed to delete sensor');
    return await response.json();
  } catch (error) {
    console.warn('Delete failed, returning mock response:', error);
    return { success: true, message: 'Mock sensor deleted' };
  }
};

// ------------------- Readings -------------------
export const getSensorReadings = async (
  sensorId: string,
  limit = 100
): Promise<SensorReading[]> => {
  try {
    const response = await fetch(
      `${API_BASE_URL}/sensors/${sensorId}/readings?limit=${limit}`,
      { headers: getAuthHeaders() }
    );
    if (!response.ok) throw new Error('Failed to fetch readings');
    const data = await response.json();
    return Array.isArray(data) ? data.map(normalizeReadingFromServer) : [];
  } catch (error) {
    console.warn('Using mock readings due to error:', error);
    // Retourner des lectures mockées pour le capteur
    return [
      {
        id: 'mock1',
        sensorId,
        name: 'Mock Reading',
        value: 25.0,
        unit: '°C',
        timestamp: new Date().toISOString(),
        quality: 'good'
      }
    ];
  }
};

export const createReading = async (sensorId: string, readingData: { value: number }) => {
  try {
    const response = await fetch(`${API_BASE_URL}/sensors/${sensorId}/data`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(readingData),
    });
    if (!response.ok) throw new Error('Failed to create reading');
    return await response.json();
  } catch (error) {
    console.warn('Create reading failed, returning mock response:', error);
    return {
      success: true,
      message: 'Mock reading created',
      id: Date.now().toString(),
    };
  }
};

export default {
  getSensors,
  getSensorById,
  createSensor,
  updateSensor,
  deleteSensor,
  getSensorReadings,
  createReading,
};