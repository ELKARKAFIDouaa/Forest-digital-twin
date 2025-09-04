import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { TreePine } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

const ForgotPasswordForm: React.FC = () => {
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isSubmitted, setIsSubmitted] = useState(false);
  const { resetPassword, isLoading } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (newPassword !== confirmPassword) {
      alert('Les mots de passe ne correspondent pas');
      return;
    }

    try {
      // TODO: This should handle password reset with token
      await resetPassword('user@email.com'); // This would normally come from URL params
      setIsSubmitted(true);
    } catch (error) {
      console.error('Password reset failed:', error);
    }
  };

  if (isSubmitted) {
    return (
      <div className="min-h-screen flex">
        {/* Left side - Branding */}
        <div className="flex-1 bg-emerald-600 flex flex-col justify-between p-12 text-white">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-white bg-opacity-20 rounded-lg flex items-center justify-center">
              <TreePine className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold">Forest</h1>
              <p className="text-sm opacity-90">Digital Twin</p>
            </div>
          </div>

          <div>
            <h2 className="text-4xl font-bold mb-4 leading-tight">
              Votre partenaire pour<br />
              la surveillance<br />
              environnementale.
            </h2>
          </div>

          <div>
            <p className="text-sm opacity-75">Having troubles? </p>
            <Link to="/help" className="text-sm underline hover:no-underline">
              Get Help
            </Link>
          </div>
        </div>

        {/* Right side - Success message */}
        <div className="flex-1 flex items-center justify-center p-12">
          <div className="w-full max-w-md text-center">
            <div className="mb-8">
              <div className="w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <TreePine className="w-8 h-8 text-emerald-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Mot de passe modifié
              </h2>
              <p className="text-gray-600">
                Votre mot de passe a été modifié avec succès.
              </p>
            </div>

            <Link
              to="/login"
              className="w-full bg-emerald-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-emerald-700 focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 transition-colors inline-block"
            >
              Retour à la connexion
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex">
      {/* Left side - Branding */}
      <div className="flex-1 bg-emerald-600 flex flex-col justify-between p-12 text-white">
        <div className="flex items-center space-x-3">
          <div className="w-12 h-12 bg-white bg-opacity-20 rounded-lg flex items-center justify-center">
            <TreePine className="w-8 h-8 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold">Forest</h1>
            <p className="text-sm opacity-90">Digital Twin</p>
          </div>
        </div>

        <div>
          <h2 className="text-4xl font-bold mb-4 leading-tight">
            Votre partenaire pour<br />
            la surveillance<br />
            environnementale.
          </h2>
        </div>

        <div>
          <p className="text-sm opacity-75">Having troubles? </p>
          <Link to="/help" className="text-sm underline hover:no-underline">
            Get Help
          </Link>
        </div>
      </div>

      {/* Right side - Reset form */}
      <div className="flex-1 flex items-center justify-center p-12">
        <div className="w-full max-w-md">
          <div className="text-right mb-8">
            <Link 
              to="/login" 
              className="text-sm text-gray-600 hover:text-gray-900"
            >
              Nouvel utilisateur ? Créer un compte
            </Link>
          </div>

          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Créer un nouveau mot de passe
            </h2>
            <p className="text-gray-600">
              Veuillez saisir un nouveau mot de passe.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* New Password */}
            <div>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Nouveau mot de passe"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            {/* Confirm Password */}
            <div>
              <input
                type={showPassword ? 'text' : 'password'}
                placeholder="Confirmer le nouveau mot de passe"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                required
              />
            </div>

            {/* Submit button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-emerald-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-emerald-700 focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isLoading ? 'Modification...' : 'Changer le mot de passe'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ForgotPasswordForm;