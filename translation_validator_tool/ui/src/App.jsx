import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// Pages
import LoginPage from './pages/LoginPage';
import ValidatorPage from './pages/ValidatorPage';
import HistoryPage from './pages/HistoryPage';
import RegisterPage from './pages/RegisterPage';
import AdminUsers from './pages/AdminUsers';
import AdminTranslations from './pages/AdminTranslations';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

const AdminRoute = ({ children }) => {
  const { isAuthenticated, loading, user } = useAuth();

  if (loading) return <div className="min-h-screen bg-gray-50 flex items-center justify-center"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div></div>;

  if (!isAuthenticated) return <Navigate to="/login" replace />;

  if (!user?.is_superuser) return <Navigate to="/validator" replace />;

  return children;
};

// App Component
const App = () => {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <ToastContainer position="top-right" autoClose={5000} />
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route 
              path="/validator" 
              element={
                <ProtectedRoute>
                  <ValidatorPage />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/history" 
              element={
                <ProtectedRoute>
                  <HistoryPage />
                </ProtectedRoute>
              } 
            />
            <Route
              path="/admin/users"
              element={
                <AdminRoute>
                  <AdminUsers />
                </AdminRoute>
              }
            />
            <Route
              path="/admin/translations"
              element={
                <AdminRoute>
                  <AdminTranslations />
                </AdminRoute>
              }
            />
            <Route path="/" element={<Navigate to="/validator" replace />} />
            <Route path="*" element={<Navigate to="/validator" replace />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
};

export default App;