import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { LanguageProvider } from './context/LanguageContext';
import { SyncProvider } from './context/SyncContext';
import Sidebar from './components/Sidebar';
import Navbar from './components/Navbar';

// Public Pages
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';

// Farmer Pages
import FarmerDashboard from './pages/farmer/FarmerDashboard';
import MyAnimals from './pages/farmer/MyAnimals';
import AddAnimal from './pages/farmer/AddAnimal';
import AnimalPassport from './pages/farmer/AnimalPassport';
import ReportHealthIssue from './pages/farmer/ReportHealthIssue';
import UploadImage from './pages/farmer/UploadImage';
import AssessmentResult from './pages/farmer/AssessmentResult';
import FarmerAlerts from './pages/farmer/FarmerAlerts';

// Veterinarian Pages
import VetDashboard from './pages/vet/VetDashboard';
import HighRiskCases from './pages/vet/HighRiskCases';
import AnimalHealthHistory from './pages/vet/AnimalHealthHistory';
import ReviewAssessments from './pages/vet/ReviewAssessments';
import PotentialClusters from './pages/vet/PotentialClusters';

// Admin Pages
import AdminDashboard from './pages/admin/AdminDashboard';
import SurveillanceMapPage from './pages/admin/SurveillanceMapPage';
import ClusterManagement from './pages/admin/ClusterManagement';
import AdminAlerts from './pages/admin/AdminAlerts';

// Officer Dashboard (alias/compat)
import OfficerDashboard from './pages/officer/OfficerDashboard';

// Layout wrapper with role-based routing protection
const ProtectedRoute = ({ allowedRoles = [], children }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen bg-slate-50">
        <div className="w-10 h-10 border-4 border-emerald-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }
  
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  const userRole = (user.role || 'FARMER').toUpperCase();

  // Role validation check
  if (allowedRoles.length > 0 && !allowedRoles.includes(userRole)) {
    // Redirect unauthorized user to their role-appropriate home
    if (userRole === 'FARMER') return <Navigate to="/farmer/dashboard" replace />;
    if (userRole === 'VETERINARIAN') return <Navigate to="/veterinarian/dashboard" replace />;
    return <Navigate to="/admin/dashboard" replace />;
  }

  return (
    <div className="flex min-h-screen bg-slate-50 font-['Outfit',sans-serif]">
      <Sidebar />
      <div className="flex-1 flex flex-col h-screen overflow-hidden">
        <Navbar />
        <main className="flex-1 overflow-y-auto bg-slate-50/70">
          {children}
        </main>
      </div>
    </div>
  );
};

const AppRoutes = () => {
  const { user } = useAuth();

  const getHomeRedirect = () => {
    if (!user) return <LandingPage />;
    const role = (user.role || 'FARMER').toUpperCase();
    if (role === 'FARMER') return <Navigate to="/farmer/dashboard" replace />;
    if (role === 'VETERINARIAN') return <Navigate to="/veterinarian/dashboard" replace />;
    return <Navigate to="/admin/dashboard" replace />;
  };

  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/" element={getHomeRedirect()} />
      <Route path="/login" element={user ? getHomeRedirect() : <LoginPage />} />
      <Route path="/register" element={user ? getHomeRedirect() : <RegisterPage />} />

      {/* ========================================================================= */}
      {/* Farmer Protected Routes (Role: FARMER, VETERINARIAN, ADMIN)                */}
      {/* ========================================================================= */}
      <Route path="/farmer/dashboard" element={<ProtectedRoute allowedRoles={['FARMER', 'VETERINARIAN', 'ADMIN']}><FarmerDashboard /></ProtectedRoute>} />
      <Route path="/farmer/animals" element={<ProtectedRoute allowedRoles={['FARMER', 'VETERINARIAN', 'ADMIN']}><MyAnimals /></ProtectedRoute>} />
      <Route path="/farmer/animals/add" element={<ProtectedRoute allowedRoles={['FARMER', 'VETERINARIAN', 'ADMIN']}><AddAnimal /></ProtectedRoute>} />
      <Route path="/farmer/passport" element={<ProtectedRoute allowedRoles={['FARMER', 'VETERINARIAN', 'ADMIN']}><AnimalPassport /></ProtectedRoute>} />
      <Route path="/farmer/passport/:animal_id" element={<ProtectedRoute allowedRoles={['FARMER', 'VETERINARIAN', 'ADMIN']}><AnimalPassport /></ProtectedRoute>} />
      <Route path="/farmer/report" element={<ProtectedRoute allowedRoles={['FARMER', 'VETERINARIAN', 'ADMIN']}><ReportHealthIssue /></ProtectedRoute>} />
      <Route path="/farmer/health" element={<ProtectedRoute allowedRoles={['FARMER', 'VETERINARIAN', 'ADMIN']}><ReportHealthIssue /></ProtectedRoute>} />
      <Route path="/farmer/upload-image" element={<ProtectedRoute allowedRoles={['FARMER', 'VETERINARIAN', 'ADMIN']}><UploadImage /></ProtectedRoute>} />
      <Route path="/farmer/assessment" element={<ProtectedRoute allowedRoles={['FARMER', 'VETERINARIAN', 'ADMIN']}><AssessmentResult /></ProtectedRoute>} />
      <Route path="/farmer/assessment/:report_id" element={<ProtectedRoute allowedRoles={['FARMER', 'VETERINARIAN', 'ADMIN']}><AssessmentResult /></ProtectedRoute>} />
      <Route path="/farmer/alerts" element={<ProtectedRoute allowedRoles={['FARMER', 'VETERINARIAN', 'ADMIN']}><FarmerAlerts /></ProtectedRoute>} />
      <Route path="/farmer/vaccinations" element={<ProtectedRoute allowedRoles={['FARMER', 'VETERINARIAN', 'ADMIN']}><FarmerAlerts /></ProtectedRoute>} />

      {/* ========================================================================= */}
      {/* Veterinarian Protected Routes (Role: VETERINARIAN, ADMIN)                  */}
      {/* ========================================================================= */}
      <Route path="/veterinarian/dashboard" element={<ProtectedRoute allowedRoles={['VETERINARIAN', 'ADMIN']}><VetDashboard /></ProtectedRoute>} />
      <Route path="/veterinarian/cases" element={<ProtectedRoute allowedRoles={['VETERINARIAN', 'ADMIN']}><HighRiskCases /></ProtectedRoute>} />
      <Route path="/veterinarian/history" element={<ProtectedRoute allowedRoles={['VETERINARIAN', 'ADMIN']}><AnimalHealthHistory /></ProtectedRoute>} />
      <Route path="/veterinarian/history/:animal_id" element={<ProtectedRoute allowedRoles={['VETERINARIAN', 'ADMIN']}><AnimalHealthHistory /></ProtectedRoute>} />
      <Route path="/veterinarian/review" element={<ProtectedRoute allowedRoles={['VETERINARIAN', 'ADMIN']}><ReviewAssessments /></ProtectedRoute>} />
      <Route path="/veterinarian/review/:case_id" element={<ProtectedRoute allowedRoles={['VETERINARIAN', 'ADMIN']}><ReviewAssessments /></ProtectedRoute>} />
      <Route path="/veterinarian/clusters" element={<ProtectedRoute allowedRoles={['VETERINARIAN', 'ADMIN']}><PotentialClusters /></ProtectedRoute>} />
      <Route path="/veterinarian/map" element={<ProtectedRoute allowedRoles={['VETERINARIAN', 'ADMIN']}><SurveillanceMapPage /></ProtectedRoute>} />

      {/* ========================================================================= */}
      {/* Admin / District Officer Protected Routes (Role: ADMIN, OFFICER)           */}
      {/* ========================================================================= */}
      <Route path="/admin/dashboard" element={<ProtectedRoute allowedRoles={['ADMIN', 'OFFICER']}><AdminDashboard /></ProtectedRoute>} />
      <Route path="/admin/map" element={<ProtectedRoute allowedRoles={['ADMIN', 'OFFICER', 'VETERINARIAN']}><SurveillanceMapPage /></ProtectedRoute>} />
      <Route path="/admin/clusters" element={<ProtectedRoute allowedRoles={['ADMIN', 'OFFICER', 'VETERINARIAN']}><ClusterManagement /></ProtectedRoute>} />
      <Route path="/admin/alerts" element={<ProtectedRoute allowedRoles={['ADMIN', 'OFFICER']}><AdminAlerts /></ProtectedRoute>} />
      <Route path="/admin/users" element={<ProtectedRoute allowedRoles={['ADMIN']}><AdminDashboard /></ProtectedRoute>} />
      <Route path="/admin/config" element={<ProtectedRoute allowedRoles={['ADMIN']}><ClusterManagement /></ProtectedRoute>} />

      {/* Officer Alias Compatibility Routes */}
      <Route path="/officer/dashboard" element={<ProtectedRoute allowedRoles={['OFFICER', 'ADMIN']}><OfficerDashboard /></ProtectedRoute>} />
      <Route path="/officer/map" element={<ProtectedRoute allowedRoles={['OFFICER', 'ADMIN']}><SurveillanceMapPage /></ProtectedRoute>} />
      <Route path="/officer/trends" element={<ProtectedRoute allowedRoles={['OFFICER', 'ADMIN']}><AdminDashboard /></ProtectedRoute>} />

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
