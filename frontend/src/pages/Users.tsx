import React, { useState, useEffect } from 'react';
import { Plus, Search, Filter, Mail, Shield } from 'lucide-react';
import axios from 'axios';
import { User } from '../types';
import { useAuth } from '../contexts/AuthContext';

const Users: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState<string>('all');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { hasRole, user: currentUser } = useAuth();

  const token = localStorage.getItem('token');

  // ---------------- Récupérer les utilisateurs ----------------
  const fetchUsers = async () => {
  if (!token) {
    console.log('No token found');
    return setError('Aucun token trouvé');
  }
  try {
    setIsLoading(true);
    console.log('Fetching users with token:', token);
    
    const response = await axios.get('/api/admin/users', { 
      headers: { Authorization: `Bearer ${token}` } 
    });
    
    console.log('API Response status:', response.status);
    console.log('API Response data:', response.data);
    console.log('Is array:', Array.isArray(response.data));
    console.log('Array length:', Array.isArray(response.data) ? response.data.length : 'Not array');
    
    setUsers(Array.isArray(response.data) ? response.data : []);
    const usersArray = Array.isArray(response.data) ? response.data : [];
    setUsers(usersArray);
  } catch (err: any) {
    console.error('Fetch users error details:', err);
    console.error('Error response:', err.response);
    setError(err.response?.data?.error || err.response?.data?.message || 'Erreur lors de la récupération des utilisateurs.');
    setUsers([]);
  } finally { 
    setIsLoading(false); 
  }
};
  useEffect(() => {
  console.log('User has admin role:', hasRole('admin'));
  console.log('Current user:', currentUser);
  
  if (hasRole('admin')) {
    fetchUsers();
  } else {
    setIsLoading(false);
    setError('Accès non autorisé.');
  }
}, [hasRole]);

  // ---------------- Filtrage et couleur des rôles ----------------
  const filteredUsers = users.filter(user => {
    const matchesSearch =
      user.firstname.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.lastname.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRole = roleFilter === 'all' || user.roles.includes(roleFilter);
    return matchesSearch && matchesRole;
  });

  const getRoleColor = (role: string) => {
  switch (role) {
    case 'admin': return 'bg-red-100 text-red-800';
    case 'user': return 'bg-blue-100 text-blue-800';
    case 'agent': return 'bg-green-100 text-green-800';
    case 'viewer': return 'bg-gray-100 text-gray-800';
    default: return 'bg-gray-100 text-gray-800';
  }
};
  // ---------------- Assigner / Supprimer un rôle ----------------
  const assignRole = async (userId: string, roleName: string) => {
  if (!token) return;
  try {
    await axios.post('/api/admin/assign-role', { user_id: userId, role_name: roleName }, { headers: { Authorization: `Bearer ${token}` } });
    fetchUsers();
  } catch (err: any) {
    setError(err.response?.data?.message || 'Erreur lors de l’assignation du rôle.');
  }
};

const removeRole = async (userId: string, roleName: string) => {
  if (!token) return;
  try {
    await axios.post('/api/admin/remove-role', { user_id: userId, role_name: roleName }, { headers: { Authorization: `Bearer ${token}` } });
    fetchUsers();
  } catch (err: any) {
    setError(err.response?.data?.message || 'Erreur lors de la suppression du rôle.');
  }
};

  // ---------------- Ajouter un utilisateur ----------------
  const createUser = async (userData: {
    email: string;
    firstname: string;
    lastname: string;
    telephone: string;
    password: string;
    role: string;
  }) => {
    if (!token) return;
    try {
      await axios.post('/api/admin/users', userData, { headers: { Authorization: `Bearer ${token}` } });
      fetchUsers();
    } catch (err: any) {
      setError(err.response?.data?.message || 'Erreur lors de la création de l’utilisateur.');
    }
  };

  // ---------------- Render ----------------
  if (isLoading) return <div className="text-center py-12">Chargement...</div>;
  if (error) return <div className="text-center py-12 text-red-600">{error}</div>;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Utilisateurs</h1>
          <p className="text-gray-600 mt-2">Gérez les utilisateurs et leurs permissions d'accès</p>
        </div>
        <button
          onClick={() =>
            createUser({
              email: 'new.user@forestdt.com',
              firstname: 'New',
              lastname: 'User',
              telephone: '1234567890',
              password: 'password123',
              role: 'user',
            })
          }
          className="bg-emerald-600 text-white px-4 py-2 rounded-lg hover:bg-emerald-700 transition-colors flex items-center space-x-2"
        >
          <Plus className="w-5 h-5" />
          <span>Inviter un utilisateur</span>
        </button>
      </div>

      {/* Filtres */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Rechercher des utilisateurs..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
            />
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Filter className="w-5 h-5 text-gray-400" />
              <span className="text-sm font-medium text-gray-700">Rôle:</span>
            </div>
            <select
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
            >
              <option value="all">Tous</option>
              <option value="admin">Administrateur</option>
              <option value="user">Utilisateur</option>
              <option value="agent">Agent</option>
              <option value="viewer">Observateur</option>
            </select>
          </div>
        </div>
      </div>

      {/* Table des utilisateurs */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left py-4 px-6 font-medium text-gray-900">Utilisateur</th>
                <th className="text-left py-4 px-6 font-medium text-gray-900">Rôles</th>
                <th className="text-left py-4 px-6 font-medium text-gray-900">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredUsers.map((user) => (
                <tr key={user.id} className="hover:bg-gray-50">
                  <td className="py-4 px-6 flex items-center space-x-3">
                    <div className="w-10 h-10 bg-emerald-100 rounded-full flex items-center justify-center">
                      <span className="text-emerald-600 font-medium">
                        {user.firstname[0]}
                        {user.lastname[0]}
                      </span>
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">
                        {user.firstname} {user.lastname}
                      </p>
                      <p className="text-sm text-gray-600 flex items-center">
                        <Mail className="w-4 h-4 mr-1" />
                        {user.email}
                      </p>
                    </div>
                  </td>
                  <td className="py-4 px-6">
                    {user.roles.map((role) => (
                      <span
                        key={role}
                        className={`px-3 py-1 rounded-full text-xs font-medium ${getRoleColor(role)} mr-2`}
                      >
                        <Shield className="w-3 h-3 inline mr-1" />
                        {role}
                      </span>
                    ))}
                  </td>
                  <td className="py-4 px-6">
                    <select
                      onChange={(e) => {
                        const roleName = e.target.value;
                        if (roleName) assignRole(user.id, roleName);
                      }}
                      className="border border-gray-300 rounded-lg px-3 py-1"
                    >
                      <option value="">Assigner un rôle</option>
                      <option value="admin">Administrateur</option>
                      <option value="user">Utilisateur</option>
                      <option value="agent">Agent</option>
                      <option value="viewer">Observateur</option>
                    </select>
                    {user.roles.length > 0 && (
                      <button
                        onClick={() => removeRole(user.id, user.roles[0])}
                        className="ml-2 text-red-600 hover:text-red-800"
                      >
                        Supprimer le rôle
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {filteredUsers.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500">Aucun utilisateur trouvé avec les filtres actuels.</p>
        </div>
      )}
    </div>
  );
};

export default Users;
