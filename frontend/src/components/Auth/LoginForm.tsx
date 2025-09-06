import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Eye, EyeOff, TreePine } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

const LoginForm: React.FC = () => {
  const [email, setEmail] = useState('Digitaltwin@email.com');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const { login, isLoading } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  setMessage(null); // Reset message
  try {
    const user = await login(email, password);
    setMessage("✅ Connexion réussie !");
    
    // Redirection basée sur le rôle
    setTimeout(() => {
      if (user.roles.includes('admin')) {
        navigate("/dashboard");
      } else if (user.roles.includes('user')) {
        navigate("/dashboarduser");
      } else {
        navigate("/");
      }
    }, 1500);
  } catch (error) {
    console.error("Login failed:", error);
    setMessage("❌ Email ou mot de passe incorrect.");
  }
};

  const handleGoogleLogin = () => {
    // TODO: Implement Google OAuth
    console.log('Google login clicked');
  };

  return (
    <div className="min-h-screen flex flex-col">
      <div className="flex flex-1">
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

        {/* Right side - Login form */}
        <div className="flex-1 flex items-center justify-center p-12">
          <div className="w-full max-w-md">
            <div className="text-right mb-8">
              <Link 
                to="/register" 
                className="text-sm text-gray-600 hover:text-gray-900"
              >
                Vous avez déjà un compte ?
              </Link>
            </div>

            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Connectez-vous à Digital Twin
              </h2>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Google Sign In */}
              <button
                type="button"
                onClick={handleGoogleLogin}
                className="w-full flex items-center justify-center space-x-3 px-4 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div className="w-5 h-5 bg-blue-500 rounded flex items-center justify-center">
                  <span className="text-white text-xs font-bold">G</span>
                </div>
                <span className="text-gray-700 font-medium">Se connecter avec Google</span>
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
                  Email address
                </label>
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                  required
                />
              </div>

              {/* Password */}
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                  Password
                </label>
                <div className="relative">
                  <input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
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

              {/* Remember me & Forgot password */}
              <div className="flex items-center justify-between">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    className="w-4 h-4 text-emerald-600 border-gray-300 rounded focus:ring-emerald-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">Se souvenir de moi</span>
                </label>
                <Link 
                  to="/forgot-password" 
                  className="text-sm text-emerald-600 hover:text-emerald-700"
                >
                  Mot de passe oublié?
                </Link>
              </div>

              {/* Submit button */}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-emerald-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-emerald-700 focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isLoading ? 'Connexion...' : 'Se connecter'}
              </button>
            </form>

            {/* Message affiché en bas */}
            {message && (
              <p className="mt-4 text-center text-sm font-medium 
                {message.startsWith('✅') ? 'text-green-600' : 'text-red-600'}">
                {message}
              </p>
            )}

            {/* Terms */}
            <div className="mt-6 flex items-start space-x-2">
              <input
                type="checkbox"
                id="terms"
                className="w-4 h-4 text-emerald-600 border-gray-300 rounded focus:ring-emerald-500 mt-0.5"
              />
              <label htmlFor="terms" className="text-xs text-gray-600 leading-relaxed">
                En cliquant sur Créer un compte, j'accepte d'avoir lu et accepte les{' '}
                <Link to="/terms" className="text-emerald-600 hover:underline">
                  Conditions d'utilisation
                </Link>{' '}
                et de{' '}
                <Link to="/privacy" className="text-emerald-600 hover:underline">
                  confidentialité
                </Link>
                .
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginForm;
