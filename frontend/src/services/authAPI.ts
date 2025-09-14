import { User, RegisterData } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const handleResponse = async (response: Response) => {
  const contentType = response.headers.get('Content-Type');
  let data: any = {};
  if (contentType && contentType.includes('application/json')) {
    data = await response.json();
  } else {
    const text = await response.text();
    throw new Error(text || 'Unexpected response from server');
  }

  if (!response.ok) {
    const errorMsg = data.error || data.message || 'Request failed';
    throw new Error(errorMsg);
  }

  return data;
};

export const login = async (email: string, password: string): Promise<User> => {
  console.log('🔐 Attempting login to:', `${API_BASE_URL}/auth/login`);
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });

  const data = await handleResponse(response);
  if (!data.access_token) throw new Error('No token received from server');

  localStorage.setItem('token', data.access_token);

  return {
    id: data.user.id,
    email: data.user.email,
    firstname: data.user.firstname,
    lastname: data.user.lastname,
    telephone: data.user.telephone || '',
    roles: [data.user.role],
    permissions: ['standard'],
    createdAt: data.user.created_at || new Date().toISOString(),
  };
};

export const register = async (userData: RegisterData): Promise<User> => {
  const response = await fetch(`${API_BASE_URL}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(userData),
  });

  const data = await handleResponse(response);

  if (!data.access_token) throw new Error('No token received from server');
  localStorage.setItem('token', data.access_token);

  return {
    id: data.user.id,
    email: data.user.email,
    firstname: data.user.firstname,
    lastname: data.user.lastname,
    telephone: data.user.telephone || '',
    roles: [data.user.role],
    permissions: ['standard'],
    createdAt: data.user.created_at || new Date().toISOString(),
  };
};

export const getCurrentUser = async (): Promise<User> => {
  const token = localStorage.getItem('token');
  if (!token) throw new Error('No authentication token found');

  const response = await fetch(`${API_BASE_URL}/auth/me`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  const data = await handleResponse(response);

  return {
    id: data.id,
    email: data.email,
    firstname: data.firstname || '',
    lastname: data.lastname || '',
    telephone: data.telephone || '',
    roles: [data.role],
    permissions: ['standard'],
    createdAt: data.created_at || new Date().toISOString(),
  };
};

export const logout = (): void => {
  localStorage.removeItem('token');
  // Optionnel : Appeler un endpoint backend pour invalider le token
};

export const resetPassword = async (email: string): Promise<void> => {
  const response = await fetch(`${API_BASE_URL}/auth/reset-password`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email }),
  });

  await handleResponse(response);
};
