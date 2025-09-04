import { DashboardStats } from '../types';

// Use Vite env variables
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

export const getDashboardStats = async (): Promise<DashboardStats> => {
  try {
    const response = await fetch(`${API_BASE_URL}/dashboard/stats`);
    if (!response.ok) throw new Error('Failed to fetch dashboard stats');
    return await response.json();
  } catch (error) {
    // Mock data for development or fallback
    console.warn('Using mock dashboard stats due to error:', error);
    return {
      totalSensors: 24,
      activeSensors: 22,
      criticalAlerts: 3,
      dataPoints: 15847,
      lastUpdate: new Date().toISOString(),
    };
  }
};

export const getEnvironmentalData = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/dashboard/environmental`);
    if (!response.ok) throw new Error('Failed to fetch environmental data');
    return await response.json();
  } catch (error) {
    // Mock environmental data
    console.warn('Using mock environmental data due to error:', error);
    return {
      temperature: Array.from({ length: 24 }, (_, i) => ({
        time: `${i}:00`,
        value: +(20 + Math.random() * 10).toFixed(1),
      })),
      humidity: Array.from({ length: 24 }, (_, i) => ({
        time: `${i}:00`,
        value: +(60 + Math.random() * 20).toFixed(1),
      })),
      airQuality: Array.from({ length: 24 }, (_, i) => ({
        time: `${i}:00`,
        value: +(50 + Math.random() * 100).toFixed(0),
      })),
    };
  }
};
