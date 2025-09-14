import React, { useState, useEffect } from 'react';
import { Search, Filter, Trash, Edit } from 'lucide-react';
import * as roleAPI from '../services/roleAPI';
import { useAuth } from '../contexts/AuthContext';
import LoadingSpinner from '../components/Common/LoadingSpinner';

interface Role {
  name: string;
  description?: string;
  permissions?: string[]; // <-- ajouté
}

const Roles: React.FC = () => {
  const [roles, setRoles] = useState<Role[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [error, setError] = useState<string | null>(null);

  const [editingRole, setEditingRole] = useState<Role | null>(null); // rôle en édition
  const [editName, setEditName] = useState('');
  const [editDescription, setEditDescription] = useState('');
  const [editPermissions, setEditPermissions] = useState<string>('');

  const { hasRole } = useAuth();

  useEffect(() => {
    const fetchRoles = async () => {
      try {
        if (!hasRole('admin')) {
          setError("Accès non autorisé.");
          return;
        }
        const rolesData = await roleAPI.getRoles();
        setRoles(rolesData);
      } catch (err: any) {
        setError(err.message || 'Erreur lors de la récupération des rôles.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchRoles();
  }, [hasRole]);

  const filteredRoles = roles.filter(role =>
    role.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    role.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // ---------------- Edit ----------------
  const startEdit = (role: Role) => {
    setEditingRole(role);
    setEditName(role.name);
    setEditDescription(role.description || '');
    setEditPermissions(role.permissions?.join(', ') || '');
  };

  const saveEdit = async () => {
    if (!editingRole) return;

    try {
      const updatedRole = {
        name: editName,
        description: editDescription,
        permissions: editPermissions.split(',').map(p => p.trim())
      };
      await roleAPI.updateRole(editingRole.name, updatedRole);
      // Mettre à jour localement
      setRoles(prev => prev.map(r => r.name === editingRole.name ? { ...r, ...updatedRole } : r));
      setEditingRole(null);
    } catch (err: any) {
      alert(err.message || 'Erreur lors de la mise à jour du rôle.');
    }
  };

  // ---------------- Delete ----------------
  const deleteRole = async (roleName: string) => {
  if (!window.confirm(`Voulez-vous vraiment supprimer le rôle ${roleName} ?`)) return;
  try {
    await roleAPI.deleteRole(roleName);
    setRoles(prev => prev.filter(r => r.name !== roleName));
  } catch (err: any) {
    alert(err.message || 'Erreur lors de la suppression du rôle.');
  }
};


  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12 text-red-600">
        {error}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Rôles</h1>
          <p className="text-gray-600 mt-2">Gérez les rôles et leurs permissions</p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="relative max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Rechercher des rôles..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
          />
        </div>
      </div>

      {/* Roles table */}
      <div className="overflow-x-auto bg-white rounded-xl border border-gray-200 shadow-sm">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-600">Nom</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-600">Description</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-600">Permissions</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-600">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
  {filteredRoles.map((role) => (
    <tr key={role.name} className="hover:bg-gray-50">
      <td className="px-6 py-4 whitespace-nowrap">{role.name}</td>
      <td className="px-6 py-4 whitespace-nowrap text-gray-600">{role.description}</td>
      <td className="px-6 py-4 whitespace-nowrap">
        <div className="flex flex-wrap gap-1">
          {role.permissions && role.permissions.length > 0 ? (
            role.permissions.map((perm) => (
              <span
                key={perm}
                className="px-2 py-1 bg-emerald-100 text-emerald-800 text-xs rounded-full"
              >
                {perm}
              </span>
            ))
          ) : (
            <span className="text-gray-400 text-xs">Aucune</span>
          )}
        </div>
      </td>
      <td className="px-6 py-4 whitespace-nowrap flex space-x-3">
        <button
          className="text-blue-500 hover:text-blue-700"
          onClick={() => alert(`Edition du rôle ${role.name} pas encore implémentée`)}
        >
          Edit
        </button>
        <button
          className="text-red-500 hover:text-red-700"
          onClick={() => alert(`Suppression du rôle ${role.name} pas encore implémentée`)}
        >
          <Trash className="w-5 h-5" />
        </button>
      </td>
    </tr>
  ))}
</tbody>

        </table>

        {filteredRoles.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500">Aucun rôle trouvé avec les filtres actuels.</p>
          </div>
        )}
      </div>

      {/* Edit modal */}
      {editingRole && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md space-y-4">
            <h2 className="text-xl font-bold text-gray-900">Modifier le rôle</h2>
            <input
              type="text"
              value={editName}
              onChange={e => setEditName(e.target.value)}
              placeholder="Nom"
              className="w-full border border-gray-300 rounded-lg px-3 py-2"
            />
            <input
              type="text"
              value={editDescription}
              onChange={e => setEditDescription(e.target.value)}
              placeholder="Description"
              className="w-full border border-gray-300 rounded-lg px-3 py-2"
            />
            <input
              type="text"
              value={editPermissions}
              onChange={e => setEditPermissions(e.target.value)}
              placeholder="Permissions (séparées par des virgules)"
              className="w-full border border-gray-300 rounded-lg px-3 py-2"
            />
            <div className="flex justify-end space-x-3 mt-4">
              <button
                className="px-4 py-2 rounded-lg border border-gray-300 hover:bg-gray-50"
                onClick={() => setEditingRole(null)}
              >
                Annuler
              </button>
              <button
                className="px-4 py-2 rounded-lg bg-emerald-600 text-white hover:bg-emerald-700"
                onClick={saveEdit}
              >
                Enregistrer
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Roles;
