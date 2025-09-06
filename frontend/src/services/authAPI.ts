import { User, RegisterData } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

export const login = async (email: string, password: string): Promise<User> => {
  console.log('🔐 Attempting login to:', `${API_BASE_URL}/auth/login`);
  
  try {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    console.log('📡 Login response status:', response.status);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ Login error response:', errorText);
      throw new Error(errorText || 'Login failed');
    }

    const data = await response.json();
    console.log('✅ Login success data:', data);

    const token = data.access_token;
    if (!token) {
      throw new Error('No token received from server');
    }

    localStorage.setItem('token', token);

    // ✅ Correction: Utilisez la structure correcte
    return {
      id: data.user.id,
      email: data.user.email,
      firstname: data.user.firstname,
      lastname: data.user.lastname,
      telephone: data.user.telephone || '',
      roles: [data.user.role], // Convertir en tableau
      permissions: ['standard'],
      createdAt: data.user.created_at || new Date().toISOString(),
    };
  } catch (error) {
    console.error('💥 Login fetch error:', error);
    throw error;
  }
};

export const register = async (userData: RegisterData): Promise<User> => {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || error.error || 'Registration failed');
    }

    const data = await response.json();
    const token = data.access_token;

    if (token) {
      localStorage.setItem('token', token);
    }

    // ✅ Correction: Utilisez la structure correcte
    return {
      id: data.user.id,
      email: data.user.email,
      firstname: data.user.firstname,
      lastname: data.user.lastname,
      telephone: data.user.telephone || '',
      roles: [data.user.role], // Convertir en tableau
      permissions: ['standard'],
      createdAt: data.user.created_at || new Date().toISOString(),
    };
  } catch (error) {
    console.error('Registration error:', error);
    throw error;
  }
};

export const getCurrentUser = async (): Promise<User> => {
  const token = localStorage.getItem('token');
  
  if (!token) {
    throw new Error('No authentication token found');
  }

  try {
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      if (response.status === 401 || response.status === 403) {
        localStorage.removeItem('token');
        throw new Error('Session expired');
      }
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    
    // ✅ Correction: Utilisez la structure correcte
    return {
      id: data.id,
      email: data.email,
      firstname: data.firstname || '',
      lastname: data.lastname || '',
      telephone: data.telephone || '',
      roles: [data.role], // Convertir en tableau
      permissions: ['standard'],
      createdAt: data.created_at || new Date().toISOString(),
    };
  } catch (error) {
    console.error('Error fetching current user:', error);
    throw error;
  }
};

export const logout = async (): Promise<void> => {
  await fetch(`${API_BASE_URL}/auth/logout`, {
    method: 'POST',
  });
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

