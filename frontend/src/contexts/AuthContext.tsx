
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, RegisterData, AuthContextType  } from '../types';
import * as authAPI from '../services/authAPI';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const userData = await authAPI.getCurrentUser();
        setUser(userData);
      } catch (error) {
        console.log('No active session');
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = async (email: string, password: string) => {
  setIsLoading(true);
  try {
    const userData = await authAPI.login(email, password);
    setUser(userData);
    return userData; // ← Ajoutez ce return
  } catch (error) {
    console.error('Login error:', error);
    throw error; // ← Propagez l'erreur
  } finally {
    setIsLoading(false);
  }
};

  const hasRole = (role: string) => {
    return Array.isArray(user?.roles) ? user.roles.includes(role) : user?.roles === role;
  };

  const hasPermission = (permission: string) => {
    if (!user?.permissions) return false;
    if (Array.isArray(user.permissions)) {
      return user.permissions.includes(permission);
    } else if (typeof user.permissions === 'string') {
      return user.permissions === 'all' || user.permissions === permission;
    }
    return false;
  };

  const logout = async () => {
    try {
      await authAPI.logout();
      setUser(null);
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const register = async (userData: RegisterData): Promise<User> => {
    setIsLoading(true);
    try {
      const newUser = await authAPI.register(userData);
      setUser(newUser);
      return newUser; // ← Ajoutez ce return
    } catch (error) {
      console.error('Registration error:', error);
      throw error; // ← Propagez l'erreur
    } finally {
      setIsLoading(false);
    }
  };

  const resetPassword = async (email: string) => {
    await authAPI.resetPassword(email);
  };

  const value: AuthContextType = {
    user,
    login,
    logout,
    register,
    resetPassword,
    isLoading,
    hasRole,
    hasPermission,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};