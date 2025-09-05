// src/services/dashboardAPI.ts
import { DashboardStats } from '../types';

// Helper to generate random values
const random = (min: number, max: number, decimals = 0) =>
  +(Math.random() * (max - min) + min).toFixed(decimals);

// Dashboard stats
export const getDashboardStats = async (): Promise<DashboardStats> => ({
  totalSensors: 24,
  activeSensors: random(20, 24),
  criticalAlerts: random(0, 5),
  dataPoints: random(15000, 16000),
  lastUpdate: new Date().toISOString(),
});

// Environmental data
export const getEnvironmentalData = async () => ({
  temperature: Array.from({ length: 24 }, (_, i) => ({ time: `${i}:00`, value: random(20, 30, 1) })),
  humidity: Array.from({ length: 24 }, (_, i) => ({ time: `${i}:00`, value: random(60, 80, 1) })),
  airQuality: Array.from({ length: 24 }, (_, i) => ({ time: `${i}:00`, value: random(50, 150) })),
  rainfall: Array.from({ length: 24 }, (_, i) => ({ time: `${i}:00`, value: random(0, 10, 1) })),
  windSpeed: Array.from({ length: 24 }, (_, i) => ({ time: `${i}:00`, value: random(0, 15, 1) })),
  soilHumidity: Array.from({ length: 24 }, (_, i) => ({ time: `${i}:00`, value: random(30, 70, 1) })),
  soilPH: Array.from({ length: 24 }, (_, i) => ({ time: `${i}:00`, value: random(5, 8, 2) })),
});

// Other metrics (vegetation, fauna, plant, fire, human, sound, GPS)
export const getVegetationData = async () => ({ NDVI: Array.from({ length: 24 }, (_, i) => ({ time: `${i}:00`, value: random(0, 1, 2) })) });
export const getPlantData = async () => ({ growth: Array.from({ length: 24 }, (_, i) => ({ time: `${i}:00`, value: random(0, 100) })) });
export const getFaunaData = async () => ({ sightings: Array.from({ length: 24 }, (_, i) => ({ time: `${i}:00`, value: random(0, 10) })) });
export const getFireData = async () => ({ fireAlerts: Array.from({ length: 24 }, (_, i) => ({ time: `${i}:00`, value: random(0, 5) })) });
export const getHumanData = async () => ({ activity: Array.from({ length: 24 }, (_, i) => ({ time: `${i}:00`, value: random(0, 20) })) });
export const getSoundData = async () => ({ decibel: Array.from({ length: 24 }, (_, i) => ({ time: `${i}:00`, value: random(30, 100, 1) })) });
export const getGPSData = async () => ({
  latitude: Array.from({ length: 24 }, () => random(30, 35, 5)),
  longitude: Array.from({ length: 24 }, () => random(10, 15, 5)),
});
