import {RoleData} from '../types';
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

// Helper: headers with token if available
const getAuthHeaders = (): Record<string, string> => {
  const token = localStorage.getItem('token');
  return token
    ? { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` }
    : { 'Content-Type': 'application/json' };
};

// ------------------- Roles -------------------
export const getRoles = async (): Promise<{ name: string; description?: string; permissions?: string[] }[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/admin/roles`, { headers: getAuthHeaders() });
    if (!response.ok) throw new Error('Failed to fetch roles');
    return await response.json();
  } catch (error) {
    console.warn('Using mock roles due to error:', error);
    return [
      { name: 'admin', description: 'Administrateur', permissions: ["manage_users", "manage_roles", "view_dashboard", "manage_iot"] },
      { name: 'forest_agent', description: 'Agent forestier', permissions: ["view_dashboard", "manage_iot", "view_reports"] },
      { name: 'researcher', description: 'Chercheur', permissions: ["view_dashboard", "view_reports", "run_predictions"] },
      { name: 'viewer', description: 'Observateur', permissions: ["view_dashboard"] },
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
export const deleteRole = async (roleName: string) => {
  try {
    const response = await fetch(`${API_BASE_URL}/admin/delete-role`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ role_name: roleName }),
    });
    if (!response.ok) throw new Error("Échec de la suppression du rôle");
    return await response.json();
  } catch (error) {
    console.warn("Delete role failed:", error);
    throw error;
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

export const updateRole = async (roleName: string, updatedData: RoleData) => {
  try {
    const response = await fetch(`${API_BASE_URL}/admin/update-role`, {
      method: 'POST', // ou PUT selon ton backend
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
      body: JSON.stringify({ role_name: roleName, ...updatedData }),
    });

    if (!response.ok) {
      throw new Error('Échec de la mise à jour du rôle');
    }
    return await response.json();
  } catch (error) {
    console.warn('Update role failed:', error);
    return { success: false, message: 'Erreur lors de la mise à jour du rôle' };
  }
};

export default {
  getRoles,
  assignRole,
  removeRole,
  updateRole,
};
