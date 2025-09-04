// Core types for the Digital Twin application
export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  role: 'admin' | 'user' | 'viewer';
  avatar?: string;
  createdAt: string;
}

export interface Sensor {
  id: string;
  name: string;
  type: 'temperature' | 'humidity' | 'air_quality' | 'soil_moisture' | 'light';
  location: {
    lat: number;
    lng: number;
    zone: string;
  };
  status: 'active' | 'inactive' | 'maintenance';
  lastReading: SensorReading;
  batteryLevel: number;
}

export interface SensorReading {
  id: string;
  sensorId: string;
  value: number;
  unit: string;
  timestamp: string;
  quality: 'good' | 'warning' | 'critical';
}

export interface Report {
  id: string;
  title: string;
  type: 'environmental' | 'maintenance' | 'analysis';
  generatedAt: string;
  generatedBy: string;
  status: 'draft' | 'published' | 'archived';
  summary: string;
  downloadUrl?: string;
}

export interface DashboardStats {
  totalSensors: number;
  activeSensors: number;
  criticalAlerts: number;
  dataPoints: number;
  lastUpdate: string;
}

export interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  register: (userData: RegisterData) => Promise<void>;
  resetPassword: (email: string) => Promise<void>;
  isLoading: boolean;
}

export interface RegisterData {
  email: string;
  firstName: string;
  lastName: string;
  password: string;
}