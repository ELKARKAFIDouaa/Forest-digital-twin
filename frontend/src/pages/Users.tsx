import React, { useState, useEffect } from 'react';
import { Plus, Search, Filter, Edit, Trash } from 'lucide-react';
import { User } from '../types';
import * as userAPI from '../services/userAPI';
import { useAuth } from '../contexts/AuthContext';
import LoadingSpinner from '../components/Common/LoadingSpinner';
import { useNavigate } from 'react-router-dom';

const Users: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState<string>('all');
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const { hasRole } = useAuth();

  // ---------------- Fetch users ----------------
  useEffect(() => {
    const fetchUsers = async () => {
      try {
        if (!hasRole('admin')) {
          setError("Accès non autorisé.");
          return;
        }
        const usersData = await userAPI.getUsers();
        setUsers(usersData);
      } catch (err: any) {
        setError(err.response?.data?.error || 'Erreur lors de la récupération des utilisateurs.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchUsers();
  }, [hasRole]);

  // ---------------- Filters ----------------
  const filteredUsers = users.filter(user => {
    const matchesSearch =
      user.firstname.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.lastname.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRole = roleFilter === 'all' || user.roles.includes(roleFilter);
    return matchesSearch && matchesRole;
  });

  // ---------------- Handlers ----------------
  const handleDelete = async (userId: string) => {
    if (!window.confirm("Voulez-vous vraiment supprimer cet utilisateur ?")) return;
    try {
      await userAPI.deleteUser(userId);
      setUsers(prev => prev.filter(u => u.id !== userId));
    } catch (err) {
      alert("Erreur lors de la suppression.");
    }
  };

  const handleEdit = (user: User) => {
    navigate(`/users/edit/${user.id}`);
  };

  // ---------------- Render ----------------
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
          <h1 className="text-3xl font-bold text-gray-900">Utilisateurs</h1>
          <p className="text-gray-600 mt-2">
            Gérez les utilisateurs et leurs permissions d'accès
          </p>
        </div>
        <button
          onClick={() => navigate('/users/add')}
          className="bg-emerald-600 text-white px-4 py-2 rounded-lg hover:bg-emerald-700 transition-colors flex items-center space-x-2"
        >
          <Plus className="w-5 h-5" />
          <span>Inviter un utilisateur</span>
        </button>
      </div>

      {/* Filters */}
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

      {/* Users table */}
      <div className="overflow-x-auto bg-white rounded-xl border border-gray-200 shadow-sm">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-600">Prénom</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-600">Nom</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-600">Email</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-600">Téléphone</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-600">Rôle</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-600">Date création</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-600">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {filteredUsers.map((user) => (
              <tr key={user.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">{user.firstname}</td>
                <td className="px-6 py-4 whitespace-nowrap">{user.lastname}</td>
                <td className="px-6 py-4 whitespace-nowrap text-gray-600">{user.email}</td>
                <td className="px-6 py-4 whitespace-nowrap">{user.telephone}</td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {user.roles.length > 0 ? user.roles.join(', ') : 'Viewer'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {new Date(user.createdAt).toLocaleDateString('fr-FR')}
                </td>
                <td className="px-6 py-4 whitespace-nowrap flex space-x-3">
                  <button
                    onClick={() => handleEdit(user)}
                    className="text-blue-500 hover:text-blue-700"
                  >
                    <Edit className="w-5 h-5" />
                  </button>
                  <button
                    onClick={() => handleDelete(user.id)}
                    className="text-red-500 hover:text-red-700"
                  >
                    <Trash className="w-5 h-5" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {filteredUsers.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500">
              Aucun utilisateur trouvé avec les filtres actuels.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Users;
