import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/Common/ProtectedRoute';
import Layout from './components/Layout/Layout';
import LoginForm from './components/Auth/LoginForm';
import RegisterForm from './components/Auth/RegisterForm';
import ForgotPasswordForm from './components/Auth/ForgotPasswordForm';
import Dashboard from './pages/Dashboard';
import DashboardUser from './pages/Dashboarduser';
import Sensors from './pages/Sensors';
import Reports from './pages/Reports';
import Users from './pages/Users';
import Roles from './pages/Roles';
import EditUser from './pages/EditUser';
import UserForm from './pages/UserForm'
import Settings from './pages/Settings';
import DigitalTwin from './pages/Digitaltwin';
import Home from './pages/Home';
import AddSensor from './pages/AddSensor';
function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Page d’accueil */}
          <Route path="/" element={<Home />} />

          {/* Public routes */}
          <Route path="/login" element={<LoginForm />} />
          <Route path="/register" element={<RegisterForm />} />
          <Route path="/forgot-password" element={<ForgotPasswordForm />} />

          {/* Protected routes */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute requiredRole="admin">
                <Layout>
                  <Dashboard />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboarduser"
            element={
              <ProtectedRoute requiredRole="user">
                <Layout>
                  <DashboardUser />
                </Layout>
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/digitaltwin"
            element={
              <ProtectedRoute requiredRole={["admin", "user"]}>
                <Layout>
                  <DigitalTwin />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/sensors"
            element={
              <ProtectedRoute requiredRole="admin">
                <Layout>
                  <Sensors />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/sensors/add"
            element={
              <ProtectedRoute requiredRole="admin">
                <Layout>
                  <AddSensor />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/reports"
            element={
              <ProtectedRoute requiredRole="admin">
                <Layout>
                  <Reports />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/users"
            element={
              <ProtectedRoute requiredRole="admin">
                <Layout>
                  <Users />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
          path="/users/edit/:id"
          element={
              <ProtectedRoute requiredRole="admin">
              <Layout>
                 <EditUser />
              </Layout>
              </ProtectedRoute>
          }
/>
<Route
          path="/users/add"
          element={
              <ProtectedRoute requiredRole="admin">
              <Layout>
                 <UserForm/>
              </Layout>
              </ProtectedRoute>
          }
/>
<Route
          path="/roles"
          element={
              <ProtectedRoute requiredRole="admin">
              <Layout>
                 <Roles/>
              </Layout>
              </ProtectedRoute>
          }
/>

          <Route
            path="/settings"
            element={
              <ProtectedRoute requiredRole={["admin", "user"]}>
                <Layout>
                  <Settings />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Redirection par défaut */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;