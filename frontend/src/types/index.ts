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
// Représentation d'un rôle
export interface RoleData {
  name: string;             
  description?: string;     
  permissions?: string[];   
}

// Payload pour créer un rôle
export interface CreateRoleData {
  name: string;
  description?: string;
  permissions?: string[];
}

// Payload pour mise à jour d’un rôle
export interface UpdateRoleData {
  name?: string;
  description?: string;
  permissions?: string[];
}


export interface CreateSensorData {
  name: string;
  category: string;
  type: string;
  unit: string;
  status?: string;
  batteryLevel?: number;
  latitude: number;
  longitude: number;
  zone: string;
  min_value?: number;
  max_value?: number;
  interface?: string;
  reference?: string;
}

export interface UpdateSensorData {
  name?: string;
  category?: string;
  type?: string;
  unit?: string;
  status?: string;
  batteryLevel?: number;
  latitude?: number;
  longitude?: number;
  zone?: string;
  min_value?: number;
  max_value?: number;
  interface?: string;
  reference?: string;
}


export interface SensorReading {
  id: string;
  sensorId: string;
  name?: string;        // nom du capteur (optionnel)
  value: number;
  unit: string;
  timestamp: string;
  quality?: 'good' | 'warning' | 'critical'; // calculée ou renvoyée par backend
}

export interface Sensor {
  zone: string;
  id: string;
  name: string;
  category: string;
  type: string;
  unit: string;
  interface?: string;
  reference?: string;
  status: 'active' | 'inactive' | 'maintenance';
  batteryLevel: number;
  location: {
    lat: number;
    lng: number;
    zone: string;
  };
  lastReading: SensorReading | null;
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
// Payload pour la création d'un utilisateur
export interface CreateUserData {
  email: string;
  firstname: string;
  lastname: string;
  telephone: string;
  password: string;
  role: string;        
  avatar?: string;         
}

// Payload pour la mise à jour d'un utilisateur
export interface UpdateUserData {
  email?: string;
  firstname?: string;
  lastname?: string;
  telephone?: string;
  password?: string;       // pour reset le mot de passe
  role?: string;
  avatar?: string;
}

// Réponse générique du backend pour les actions de type POST/PUT/DELETE
export interface ApiResponse {
  success: boolean;
  message?: string;
  id?: string | number;    // ex: id de l’utilisateur créé
}
