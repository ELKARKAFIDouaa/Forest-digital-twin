import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Eye, EyeOff } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

const RegisterForm: React.FC = () => {
  const [formData, setFormData] = useState({
    email: '',
    firstname: '',
    lastname: '',
    telephone: '',
    password: '',
    confirmPassword: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [acceptTerms, setAcceptTerms] = useState(false);
  const { register, isLoading } = useAuth();
  const navigate = useNavigate(); // 👉 pour redirection
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.password !== formData.confirmPassword) {
      alert('Les mots de passe ne correspondent pas');
      return;
    }
    if (!acceptTerms) {
      alert("Veuillez accepter les conditions d'utilisation");
      return;
    }

    try {
      await register({
        email: formData.email,
        firstname: formData.firstname,
        lastname: formData.lastname,
        telephone: formData.telephone,
        password: formData.password,
      });

      // Si tout est OK
      setSuccessMessage('Compte créé avec succès ! Redirection vers la connexion...');
      
      // Redirection après 2 secondes
      setTimeout(() => {
        navigate('/login');
      }, 2000);
      
    } catch (error) {
      console.error('Registration failed:', error);
      alert("Erreur lors de l'inscription, veuillez réessayer.");
    }
  };

  const handleGoogleSignup = () => {
    console.log('Google signup clicked');
  };

  return (
    <div className="min-h-screen flex">
      {/* Left side - Branding */}
      <div className="flex-1 bg-[#68B85B] flex flex-col justify-between p-12 text-white">
        <div className="flex items-center space-x-3">
          <div className="mb-5">
            <img src="/logo.png" alt="Forest Digital Twin Logo" className="max-w-[150px]" />
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

      {/* Right side - Register form */}
      <div className="flex-1 flex items-center justify-center p-12">
        <div className="w-full max-w-md">
          <div className="text-right mb-8">
            <Link 
              to="/login" 
              className="text-sm text-gray-600 hover:text-gray-900"
            >
              Déjà inscrit ? Se connecter
            </Link>
          </div>

          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Inscrivez-vous à Digital Twin
            </h2>
          </div>

          {/* ✅ Message de succès */}
          {successMessage && (
            <div className="mb-4 p-3 bg-green-100 text-green-700 rounded-lg text-center">
              {successMessage}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Google Sign Up */}
            <button
              type="button"
              onClick={handleGoogleSignup}
              className="w-full flex items-center justify-center space-x-3 px-4 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div className="w-5 h-5 bg-blue-500 rounded flex items-center justify-center">
                <span className="text-white text-xs font-bold">G</span>
              </div>
              <span className="text-gray-700 font-medium">Sign in with Google</span>
            </button>

            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">ou</span>
              </div>
            </div>

            {/* Email */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Email
              </label>
              <input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                required
              />
            </div>

            {/* Name fields */}
            <div className="grid grid-cols-2 gap-4">
              <input
                type="text"
                placeholder="Prénom"
                value={formData.firstname}
                onChange={(e) => setFormData({ ...formData, firstname: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                required
              />
              <input
                type="text"
                placeholder="Nom"
                value={formData.lastname}
                onChange={(e) => setFormData({ ...formData, lastname: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                required
              />
            </div>

            {/* Telephone */}
            <div>
              <label htmlFor="telephone" className="block text-sm font-medium text-gray-700 mb-2">
                Téléphone
              </label>
              <input
                id="telephone"
                type="tel"
                value={formData.telephone}
                onChange={(e) => setFormData({ ...formData, telephone: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                required
              />
            </div>

            {/* Password */}
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                placeholder="Mot de passe"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
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

            {/* Confirm Password */}
            <div>
              <input
                type="password"
                placeholder="Confirmer le mot de passe"
                value={formData.confirmPassword}
                onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                required
              />
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-emerald-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-emerald-700 focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isLoading ? 'Inscription...' : "S'inscrire"}
            </button>
          </form>

          {/* Terms */}
          <div className="mt-6 flex items-start space-x-2">
            <input
              type="checkbox"
              id="terms"
              checked={acceptTerms}
              onChange={(e) => setAcceptTerms(e.target.checked)}
              className="w-4 h-4 text-emerald-600 border-gray-300 rounded focus:ring-emerald-500 mt-0.5"
            />
            <label htmlFor="terms" className="text-xs text-gray-600 leading-relaxed">
              En cliquant sur Créer un compte, j'accepte les{' '}
              <Link to="/terms" className="text-emerald-600 hover:underline">
                Conditions d'utilisation
              </Link>{' '}
              et la{' '}
              <Link to="/privacy" className="text-emerald-600 hover:underline">
                Politique de confidentialité
              </Link>.
            </label>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegisterForm;
