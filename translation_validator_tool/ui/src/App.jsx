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
import AdminUsersList from './pages/AdminUsersList';
 {/*import AdminTranslations from './pages/AdminTranslations';*/}
import AdminAnnotations from './pages/AdminAnnotations';
import TranslatorAnnotationsPage from './pages/TranslatorAnnotationsPage';


const getUserRole = (user) => {
  if (!user) return null;
  if (user.role) return user.role;
  return user.is_superuser ? 'admin' : 'validador';
};

const AdminRoute = ({ children }) => {
  const { isAuthenticated, loading, user } = useAuth();

  if (loading) return <div className="min-h-screen bg-gray-50 flex items-center justify-center"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div></div>;

  if (!isAuthenticated) return <Navigate to="/login" replace />;

  const isAdmin = getUserRole(user) === 'admin';
  if (!isAdmin) return <Navigate to="/" replace />;

  return children;
};

const ValidatorRoute = ({ children }) => {
  const { isAuthenticated, loading, user } = useAuth();

  if (loading) return <div className="min-h-screen bg-gray-50 flex items-center justify-center"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div></div>;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (getUserRole(user) !== 'validador') return <Navigate to="/" replace />;

  return children;
};

const TranslatorRoute = ({ children }) => {
  const { isAuthenticated, loading, user } = useAuth();

  if (loading) return <div className="min-h-screen bg-gray-50 flex items-center justify-center"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div></div>;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (getUserRole(user) !== 'traductor') return <Navigate to="/" replace />;

  return children;
};

const HistoryRoute = ({ children }) => {
  const { isAuthenticated, loading, user } = useAuth();

  if (loading) return <div className="min-h-screen bg-gray-50 flex items-center justify-center"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div></div>;
  if (!isAuthenticated) return <Navigate to="/login" replace />;

  const role = getUserRole(user);
  if (role !== 'validador' && role !== 'traductor') return <Navigate to="/" replace />;

  return children;
};

const HomeRedirect = () => {
  const { isAuthenticated, loading, user } = useAuth();

  if (loading) return <div className="min-h-screen bg-gray-50 flex items-center justify-center"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div></div>;
  if (!isAuthenticated) return <Navigate to="/login" replace />;

  const role = getUserRole(user);
  if (role === 'admin') return <Navigate to="/admin/users" replace />;
  if (role === 'traductor') return <Navigate to="/translator-annotations" replace />;
  return <Navigate to="/validator" replace />;
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
                <ValidatorRoute>
                  <ValidatorPage />
                </ValidatorRoute>
              } 
            />
            <Route
              path="/translator-annotations"
              element={
                <TranslatorRoute>
                  <TranslatorAnnotationsPage />
                </TranslatorRoute>
              }
            />
            <Route 
              path="/history" 
              element={
                <HistoryRoute>
                  <HistoryPage />
                </HistoryRoute>
              } 
            />
            <Route
              path="/admin/users"
              element={
                <AdminRoute>
                  <AdminUsersList />
                </AdminRoute>
              }
            />
            <Route
              path="/admin/pending"
              element={
                <AdminRoute>
                  <AdminUsers />
                </AdminRoute>
              }
            />
            {/*<Route
              path="/admin/translations"
              element={
                <AdminRoute>
                  <AdminTranslations />
                </AdminRoute>
              }
            />*/}
            <Route
              path="/admin/annotations"
              element={
                <AdminRoute>
                  <AdminAnnotations />
                </AdminRoute>
              }
            />
            <Route path="/" element={<HomeRedirect />} />
            <Route path="*" element={<HomeRedirect />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
};

export default App;