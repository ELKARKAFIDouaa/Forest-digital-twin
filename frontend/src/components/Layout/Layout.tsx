import React, { ReactNode } from 'react';
import Sidebar from './Sidebar';
import Header from './Header';
import { useAuth } from '../../contexts/AuthContext';

interface LayoutProps {
  children: ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { hasRole } = useAuth();

  const canSeeSidebar =
    hasRole('admin') || hasRole('agent') || hasRole('chercheur');

  return (
    <div className="flex h-screen bg-gray-50">
      {canSeeSidebar && <Sidebar />} {/* Sidebar visible pour admin, agent, chercheur */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;
