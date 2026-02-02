import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext';
import Layout from './components/Layout';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import DevelopmentPlansPage from './pages/DevelopmentPlansPage';
import LearningPathsPage from './pages/LearningPathsPage';
import MyBioPage from './pages/MyBioPage';
import MentorValidationPage from './pages/MentorValidationPage';
import TeamManagementPage from './pages/TeamManagementPage';
import PathCreationPage from './pages/PathCreationPage';
import UserManagementPage from './pages/UserManagementPage';
import LoadingSpinner from './components/LoadingSpinner';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

function PublicRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
}

export default function App() {
  return (
    <Routes>
      {/* Public routes */}
      <Route
        path="/login"
        element={
          <PublicRoute>
            <LoginPage />
          </PublicRoute>
        }
      />
      <Route
        path="/register"
        element={
          <PublicRoute>
            <RegisterPage />
          </PublicRoute>
        }
      />

      {/* Protected routes with layout */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="development-plans" element={<DevelopmentPlansPage />} />
        <Route path="learning-paths" element={<LearningPathsPage />} />
        <Route path="my-bio" element={<MyBioPage />} />
        <Route path="mentor-validation" element={<MentorValidationPage />} />
        <Route path="team-management" element={<TeamManagementPage />} />
        <Route path="path-creation" element={<PathCreationPage />} />
        <Route path="user-management" element={<UserManagementPage />} />
      </Route>

      {/* 404 */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}
