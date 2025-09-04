import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/Common/ProtectedRoute';
import Layout from './components/Layout/Layout';
import LoginForm from './components/Auth/LoginForm';
import RegisterForm from './components/Auth/RegisterForm';
import ForgotPasswordForm from './components/Auth/ForgotPasswordForm';
import Dashboard from './pages/Dashboard';
import Sensors from './pages/Sensors';
import Reports from './pages/Reports';
import Users from './pages/Users';
import Settings from './pages/Settings';
import DigitalTwin from './pages/DigitalTwin';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<LoginForm />} />
          <Route path="/register" element={<RegisterForm />} />
          <Route path="/forgot-password" element={<ForgotPasswordForm />} />
          
          {/* Protected routes */}
          <Route path="/dashboard" element={
            
              <Layout>
                <Dashboard />
              </Layout>
            
          } />
          <Route path="/digitaltwin" element={
            
              <Layout>
                <DigitalTwin />
              </Layout>
            
          } />
          
          <Route path="/sensors" element={
            
              <Layout>
                <Sensors />
              </Layout>
            
          } />
          <Route path="/reports" element={
            
              <Layout>
                <Reports />
              </Layout>
            
          } />
          <Route path="/users" element={
            
              <Layout>
                <Users />
              </Layout>
            
          } />
          <Route path="/settings" element={
            
              <Layout>
                <Settings />
              </Layout>
            
          } />
          
          {/* Default redirect */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;