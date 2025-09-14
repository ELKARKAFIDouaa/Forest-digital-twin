import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { User, UpdateUserData } from '../types';
import * as userAPI from '../services/userAPI';
import LoadingSpinner from '../components/Common/LoadingSpinner';

const EditUser: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<UpdateUserData>({
    firstname: '',
    lastname: '',
    email: '',
    telephone: '',
    password: '',
    role: '',
  });

  useEffect(() => {
    const fetchUser = async () => {
      try {
        if (!id) throw new Error("ID utilisateur manquant");
        const userData = await userAPI.getUserById(id);
        setUser(userData);
        setFormData({
          firstname: userData.firstname,
          lastname: userData.lastname,
          email: userData.email,
          telephone: userData.telephone,
          password: '',
          role: userData.roles[0] || '',
        });
      } catch (err: any) {
        setError("Erreur lors du chargement de l'utilisateur.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchUser();
  }, [id]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;
    try {
      await userAPI.updateUser(user.id, formData);
      alert("Utilisateur mis à jour avec succès !");
      navigate('/users'); // retour vers la liste
    } catch (err) {
      alert("Erreur lors de la mise à jour.");
    }
  };

  if (isLoading) return <div className="flex justify-center py-12"><LoadingSpinner size="lg" /></div>;
  if (error) return <div className="text-center py-12 text-red-600">{error}</div>;
  if (!user) return null;

  return (
    <div className="max-w-2xl mx-auto bg-white p-8 rounded-xl shadow-sm mt-8">
      <h1 className="text-2xl font-bold mb-6">Modifier l'utilisateur</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Prénom</label>
          <input
            type="text"
            name="firstname"
            value={formData.firstname}
            onChange={handleChange}
            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-emerald-500 focus:border-emerald-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Nom</label>
          <input
            type="text"
            name="lastname"
            value={formData.lastname}
            onChange={handleChange}
            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-emerald-500 focus:border-emerald-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Email</label>
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-emerald-500 focus:border-emerald-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Téléphone</label>
          <input
            type="text"
            name="telephone"
            value={formData.telephone}
            onChange={handleChange}
            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-emerald-500 focus:border-emerald-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Mot de passe</label>
          <input
            type="password"
            name="password"
            placeholder="Laisser vide pour ne pas changer"
            value={formData.password}
            onChange={handleChange}
            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-emerald-500 focus:border-emerald-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Rôle</label>
          <select
            name="role"
            value={formData.role}
            onChange={handleChange}
            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-emerald-500 focus:border-emerald-500"
          >
            <option value="admin">Administrateur</option>
            <option value="agent">Agent</option>
            <option value="viewer">Observateur</option>
            <option value="user">Utilisateur</option>
          </select>
        </div>

        <button
          type="submit"
          className="bg-emerald-600 text-white px-4 py-2 rounded-lg hover:bg-emerald-700 transition-colors"
        >
          Enregistrer
        </button>
      </form>
    </div>
  );
};

export default EditUser;
