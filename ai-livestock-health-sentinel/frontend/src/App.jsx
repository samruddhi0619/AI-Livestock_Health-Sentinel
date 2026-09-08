import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { LanguageProvider } from './context/LanguageContext';
import { SyncProvider } from './context/SyncContext';
import Sidebar from './components/Sidebar';
import Navbar from './components/Navbar';
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import FarmerDashboard from './pages/farmer/FarmerDashboard';
import VetDashboard from './pages/vet/VetDashboard';
import OfficerDashboard from './pages/officer/OfficerDashboard';
import AdminDashboard from './pages/admin/AdminDashboard';

// Layout wrapper for authenticated users
const AuthenticatedLayout = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}><div className="spinner" /></div>;
  }
  
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="app-container">
      <Sidebar />
      <div className="main-content">
        <Navbar />
        <div style={{ flex: 1, overflowY: 'auto' }}>
          {children}
        </div>
      </div>
    </div>
  );
};

const AppRoutes = () => {
  const { user } = useAuth();

  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/" element={user ? <Navigate to={`/${user.role.toLowerCase()}/dashboard`} replace /> : <LandingPage />} />
      <Route path="/login" element={user ? <Navigate to={`/${user.role.toLowerCase()}/dashboard`} replace /> : <LoginPage />} />
      <Route path="/register" element={user ? <Navigate to={`/${user.role.toLowerCase()}/dashboard`} replace /> : <RegisterPage />} />

      {/* Authenticated Dashboard Routes */}
      <Route path="/farmer/dashboard" element={<AuthenticatedLayout><FarmerDashboard /></AuthenticatedLayout>} />
      
      {/* Redundancy support for other requested farmer routes */}
      <Route path="/farmer/animals" element={<AuthenticatedLayout><FarmerDashboard /></AuthenticatedLayout>} />
      <Route path="/farmer/health" element={<AuthenticatedLayout><FarmerDashboard /></AuthenticatedLayout>} />
      <Route path="/farmer/vaccinations" element={<AuthenticatedLayout><FarmerDashboard /></AuthenticatedLayout>} />

      <Route path="/veterinarian/dashboard" element={<AuthenticatedLayout><VetDashboard /></AuthenticatedLayout>} />
      <Route path="/veterinarian/cases" element={<AuthenticatedLayout><VetDashboard /></AuthenticatedLayout>} />
      <Route path="/veterinarian/map" element={<AuthenticatedLayout><VetDashboard /></AuthenticatedLayout>} />

      <Route path="/officer/dashboard" element={<AuthenticatedLayout><OfficerDashboard /></AuthenticatedLayout>} />
      <Route path="/officer/map" element={<AuthenticatedLayout><OfficerDashboard /></AuthenticatedLayout>} />
      <Route path="/officer/trends" element={<AuthenticatedLayout><OfficerDashboard /></AuthenticatedLayout>} />

      <Route path="/admin/dashboard" element={<AuthenticatedLayout><AdminDashboard /></AuthenticatedLayout>} />
      <Route path="/admin/users" element={<AuthenticatedLayout><AdminDashboard /></AuthenticatedLayout>} />
      <Route path="/admin/config" element={<AuthenticatedLayout><AdminDashboard /></AuthenticatedLayout>} />
      <Route path="/admin/audit" element={<AuthenticatedLayout><AdminDashboard /></AuthenticatedLayout>} />

      {/* Catch-all */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

const App = () => {
  return (
    <Router>
      <LanguageProvider>
        <AuthProvider>
          <SyncProvider>
            <AppRoutes />
          </SyncProvider>
        </AuthProvider>
      </LanguageProvider>
    </Router>
  );
};

export default App;
