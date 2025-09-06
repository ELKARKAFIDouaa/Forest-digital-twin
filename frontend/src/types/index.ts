// Core types for the Digital Twin application
export interface User {
  id: string;
  email: string;
  firstname: string;
  lastname: string;
  telephone: string;
  roles: string[];
  permissions: string[];
  avatar?: string;
  createdAt: string;
  token?: string;
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

export interface RegisterData {
  telephone: string;
  email: string;
  firstname: string;
  lastname: string;
  password: string;
}
export interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<User>;
  logout: () => Promise<void>;
  register: (userData: RegisterData) => Promise<User>;
  resetPassword: (email: string) => Promise<void>;
  isLoading: boolean;
  hasRole: (role: string) => boolean;
  hasPermission: (permission: string) => boolean;
}