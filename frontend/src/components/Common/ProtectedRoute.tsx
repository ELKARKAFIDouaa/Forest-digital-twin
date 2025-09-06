import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import LoadingSpinner from './LoadingSpinner';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole: string | string[]; // Accepte une chaîne ou un tableau de chaînes
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, requiredRole }) => {
  const { user, isLoading, hasRole } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  const hasRequiredRole = Array.isArray(requiredRole)
    ? requiredRole.some(role => hasRole(role))
    : hasRole(requiredRole);

  if (!hasRequiredRole) {
    console.warn(`Accès non autorisé. Rôle requis: ${requiredRole}, Rôles actuels: ${user.roles}`);
    return <Navigate to="/" state={{ from: location }} replace />;
  }

  return <>{children}</>;
};

export default ProtectedRoute;