import { User, RegisterData } from '../types';

// Use Vite environment variables
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

// Simulated API calls - replace with actual Flask backend endpoints
export const login = async (email: string, password: string): Promise<User> => {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    throw new Error('Login failed');
  }

  return {
    id: '1',
    email,
    firstName: 'John',
    lastName: 'Doe',
    role: 'admin',
    createdAt: new Date().toISOString(),
  };
};

export const register = async (userData: RegisterData): Promise<User> => {
  const response = await fetch(`${API_BASE_URL}/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(userData),
  });

  if (!response.ok) {
    throw new Error('Registration failed');
  }

  return {
    id: '1',
    email: userData.email,
    firstName: userData.firstName,
    lastName: userData.lastName,
    role: 'user',
    createdAt: new Date().toISOString(),
  };
};

export const logout = async (): Promise<void> => {
  await fetch(`${API_BASE_URL}/auth/logout`, {
    method: 'POST',
  });
};

export const getCurrentUser = async (): Promise<User> => {
  const response = await fetch(`${API_BASE_URL}/auth/me`, {
    headers: {
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
  });

  if (!response.ok) {
    throw new Error('Not authenticated');
  }

  return response.json();
};

export const resetPassword = async (email: string): Promise<void> => {
  await fetch(`${API_BASE_URL}/auth/reset-password`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email }),
  });
};
