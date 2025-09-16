import React from 'react';

import { NavLink, useLocation, useNavigate } from 'react-router-dom';
import { Gauge, Activity, FileText, Users, Settings, TreePine, LogOut, LayoutDashboard, Cpu, Brain } from 'lucide-react';

import { useAuth } from '../../contexts/AuthContext';

const Sidebar: React.FC = () => {
  const location = useLocation();

  const navigate = useNavigate();
  const { logout, hasRole } = useAuth();
  interface SidebarItem {
  path: string;
  icon: React.ElementType;
  label: string;
}

// Navigation par défaut
let navigationItems: SidebarItem[] = [
  { path: '/digitalTwin', icon: TreePine, label: 'Digital Twin' },
  { path: '/dashboard', icon: LayoutDashboard, label: 'Tableau de bord' },
  { path: '/reports', icon: FileText, label: 'Rapports' },
  { path: '/alerts', icon: Activity, label: 'Alertes' },
  ];

  // ✅ Capteurs : admin + agent
if (hasRole("admin") || hasRole("agent")) {
  navigationItems = [
    ...navigationItems,
    { path: "/sensors", icon: Cpu, label: "Capteurs" },
  ];
}

// ✅ Options réservées admin uniquement
if (hasRole("admin")) {
  navigationItems = [
    ...navigationItems,
    { path: "/users", icon: Users, label: "Utilisateurs" },
    { path: "/roles", icon: Activity, label: "Rôles et permissions" },
    { path: "/settings", icon: Settings, label: "Paramètres" },
  ];
}
if (hasRole("chercheur")) {
  navigationItems = [
    ...navigationItems,
    {
      path: 'http://127.0.0.1:5001/',  
      icon: Cpu,                      
      label: 'Prédiction',
      
    }
  ];
}
  const handleLogout = () => {
    logout();          // clear session/auth
    navigate('/login'); // redirect to login page
  };

  

  return (
    <div className="w-64 bg-white border-r border-gray-200 flex flex-col h-full">
      {/* Logo */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <div className="mb-5">
            <img src="/logo.png" alt="Forest Digital Twin Logo" className="max-w-[100px]" />
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {navigationItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;

            return (
              <li key={item.path}>
                <NavLink
                  to={item.path}
                  className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                      : 'text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span className="font-medium">{item.label}</span>
                </NavLink>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Logout */}
      <div className="p-4 border-t border-gray-200">
        <button
          onClick={handleLogout}
          className="flex items-center space-x-3 px-4 py-3 w-full text-left text-gray-700 hover:bg-gray-50 rounded-lg transition-colors"
        >
          <LogOut className="w-5 h-5" />
          <span className="font-medium">Déconnexion</span>
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
