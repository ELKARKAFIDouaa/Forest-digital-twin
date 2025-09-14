// src/services/userAPI.ts
import { User, CreateUserData, UpdateUserData } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

// Mock users for dev/fallback
const mockUsers: User[] = [
  {
    id: '1',
    firstname: 'Alice',
    lastname: 'Dupont',
    email: 'alice@example.com',
    telephone: '0600000001',
    roles: ['admin'],
    permissions: [],
    createdAt: new Date(Date.now() - 86400000).toISOString(), // hier
  },
  {
    id: '2',
    firstname: 'Bob',
    lastname: 'Martin',
    email: 'bob@example.com',
    telephone: '0600000002',
    roles: ['agent'],
    permissions: [],
    createdAt: new Date().toISOString(),
  },
];

// Helper: headers with token if available
const getAuthHeaders = (): Record<string, string> => {
  const token = localStorage.getItem('token');
  return token
    ? { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` }
    : { 'Content-Type': 'application/json' };
};


// Normalize backend → frontend
const normalizeUserFromServer = (raw: any): User => ({
  id: raw.id?.toString(),
  email: raw.email,
  firstname: raw.firstname || raw.first_name || '',
  lastname: raw.lastname || raw.last_name || '',
  telephone: raw.telephone || '',
  roles: Array.isArray(raw.roles) ? raw.roles : raw.role ? [raw.role] : [],
  permissions: raw.permissions || [],
  createdAt: raw.created_at || new Date().toISOString(),
});

// ------------------- Users -------------------
export const getUsers = async (): Promise<User[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/admin/users`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) throw new Error('Failed to fetch users');
    const data = await response.json();
    return Array.isArray(data) ? data.map(normalizeUserFromServer) : [];
  } catch (error) {
    console.warn('Using mock users due to error:', error);
    return mockUsers;
  }
};

export const getUserById = async (id: string): Promise<User> => {
  try {
    const response = await fetch(`${API_BASE_URL}/admin/users/${id}`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) throw new Error('Failed to fetch user');
    return normalizeUserFromServer(await response.json());
  } catch (error) {
    const user = mockUsers.find(u => u.id === id);
    if (!user) throw new Error('User not found');
    console.warn('Using mock user due to error:', error);
    return user;
  }
};

export const createUser = async (userData: CreateUserData) => {
  try {
    const response = await fetch(`${API_BASE_URL}/admin/users/add`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(userData),
    });
    if (!response.ok) throw new Error('Failed to create user');
    return await response.json();
  } catch (error) {
    console.warn('Create failed, returning mock response:', error);
    return {
      success: true,
      message: 'Mock user created',
      id: Date.now().toString(),
      roles: [userData.role || 'agent'],
    };
  }
};

export const updateUser = async (id: string, updates: UpdateUserData) => {
  try {
    const response = await fetch(`${API_BASE_URL}/admin/users/${id}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(updates),
    });
    if (!response.ok) throw new Error('Failed to update user');
    return await response.json();
  } catch (error) {
    console.warn('Update failed, returning mock response:', error);
    const user = mockUsers.find(u => u.id === id);
    if (!user) throw new Error('User not found');
    return { ...user, ...updates };
  }
};

export const deleteUser = async (id: string) => {
  try {
    const response = await fetch(`${API_BASE_URL}/admin/users/${id}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });
    if (!response.ok) throw new Error('Failed to delete user');
    return await response.json();
  } catch (error) {
    console.warn('Delete failed, returning mock response:', error);
    return { success: true, message: 'Mock user deleted' };
  }
};

// ------------------- Roles -------------------
export const getRoles = async (): Promise<{ name: string; description?: string }[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/admin/roles`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) throw new Error('Failed to fetch roles');
    return await response.json();
  } catch (error) {
    console.warn('Using mock roles due to error:', error);
    return [
      { name: 'admin', description: 'Administrateur' },
      { name: 'agent', description: 'Agent' },
      { name: 'viewer', description: 'Observateur' },
    ];
  }
};

export const assignRole = async (userId: string, roleName: string) => {
  try {
    const response = await fetch(`${API_BASE_URL}/admin/assign-role`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ user_id: userId, role_name: roleName }),
    });
    if (!response.ok) throw new Error('Failed to assign role');
    return await response.json();
  } catch (error) {
    console.warn('Assign role failed, returning mock response:', error);
    return { success: true, message: 'Mock role assigned' };
  }
};

export const removeRole = async (userId: string, roleName: string) => {
  try {
    const response = await fetch(`${API_BASE_URL}/admin/remove-role`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ user_id: userId, role_name: roleName }),
    });
    if (!response.ok) throw new Error('Failed to remove role');
    return await response.json();
  } catch (error) {
    console.warn('Remove role failed, returning mock response:', error);
    return { success: true, message: 'Mock role removed' };
  }
};

export default {
  getUsers,
  getUserById,
  createUser,
  updateUser,
  deleteUser,
  getRoles,
  assignRole,
  removeRole,
};
