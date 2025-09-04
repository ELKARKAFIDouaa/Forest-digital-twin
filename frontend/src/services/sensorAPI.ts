import { Sensor, SensorReading } from '../types';

// Use Vite env variables
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

// Mock data for development
const mockSensors: Sensor[] = [
  {
    id: '1',
    name: 'Temperature Sensor A1',
    type: 'temperature',
    location: { lat: 45.5017, lng: -73.5673, zone: 'Zone Nord' },
    status: 'active',
    batteryLevel: 85,
    lastReading: {
      id: '1',
      sensorId: '1',
      value: 22.5,
      unit: '°C',
      timestamp: new Date().toISOString(),
      quality: 'good',
    },
  },
  {
    id: '2',
    name: 'Humidity Sensor B2',
    type: 'humidity',
    location: { lat: 45.5087, lng: -73.5540, zone: 'Zone Sud' },
    status: 'active',
    batteryLevel: 92,
    lastReading: {
      id: '2',
      sensorId: '2',
      value: 68,
      unit: '%',
      timestamp: new Date().toISOString(),
      quality: 'good',
    },
  },
  {
    id: '3',
    name: 'Air Quality Monitor C1',
    type: 'air_quality',
    location: { lat: 45.5125, lng: -73.5607, zone: 'Zone Est' },
    status: 'maintenance',
    batteryLevel: 23,
    lastReading: {
      id: '3',
      sensorId: '3',
      value: 156,
      unit: 'AQI',
      timestamp: new Date(Date.now() - 3600000).toISOString(),
      quality: 'warning',
    },
  },
];

export const getSensors = async (): Promise<Sensor[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/sensors`);
    if (!response.ok) throw new Error('Failed to fetch sensors');
    return await response.json();
  } catch (error) {
    console.warn('Using mock sensors due to error:', error);
    return mockSensors;
  }
};

export const getSensorById = async (id: string): Promise<Sensor> => {
  try {
    const response = await fetch(`${API_BASE_URL}/sensors/${id}`);
    if (!response.ok) throw new Error('Failed to fetch sensor');
    return await response.json();
  } catch (error) {
    const sensor = mockSensors.find(s => s.id === id);
    if (!sensor) throw new Error('Sensor not found');
    console.warn('Using mock sensor due to error:', error);
    return sensor;
  }
};

export const getSensorReadings = async (sensorId: string, limit = 100): Promise<SensorReading[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/sensors/${sensorId}/readings?limit=${limit}`);
    if (!response.ok) throw new Error('Failed to fetch readings');
    return await response.json();
  } catch (error) {
    console.warn('Using mock readings due to error:', error);
    return Array.from({ length: 24 }, (_, i) => ({
      id: `reading-${i}`,
      sensorId,
      value: +(Math.random() * 100).toFixed(1),
      unit: '°C',
      timestamp: new Date(Date.now() - i * 3600000).toISOString(),
      quality: Math.random() > 0.8 ? 'warning' : 'good',
    }));
  }
};

export const updateSensor = async (id: string, updates: Partial<Sensor>): Promise<Sensor> => {
  try {
    const response = await fetch(`${API_BASE_URL}/sensors/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates),
    });

    if (!response.ok) throw new Error('Failed to update sensor');
    return await response.json();
  } catch (error) {
    console.warn('Update failed, returning mock sensor:', error);
    const sensor = mockSensors.find(s => s.id === id);
    if (!sensor) throw new Error('Sensor not found');
    return { ...sensor, ...updates };
  }
};
