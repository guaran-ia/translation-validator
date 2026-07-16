import { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// Pages
import LoginPage from './pages/LoginPage';
import ValidatorHome from './pages/ValidatorHome';
import HistoryPage from './pages/HistoryPage';
import RegisterPage from './pages/RegisterPage';
import AdminUsers from './pages/AdminUsers';
import AdminUsersList from './pages/AdminUsersList';
 {/*import AdminTranslations from './pages/AdminTranslations';*/}
import AdminAnnotations from './pages/AdminAnnotations';
import TranslatorAnnotationsPage from './pages/TranslatorAnnotationsPage';
import PendingTranslationsPage from './pages/PendingTranslationsPage';
import HelpPage from './pages/HelpPage';
import ValidatorHelpPage from './pages/ValidatorHelpPage';
import LeaderboardPage from './pages/LeaderboardPage';
import AllTimeLeaderboardPage from './pages/AllTimeLeaderboardPage';
import {
  ACTIVE_TRANSLATOR,
  ACTIVE_VALIDATOR,
  canTranslate,
  canValidate,
  getStoredActiveRole,
  isAdmin,
  routeForActiveRole,
} from './utils/roles';


const ActiveRoleRoute = ({ role, children }) => {
  const { setActiveRole } = useAuth();

  useEffect(() => {
    setActiveRole(role);
  }, [role, setActiveRole]);

  return children;
};

const AdminRoute = ({ children }) => {
  const { isAuthenticated, loading, user } = useAuth();

  if (loading) return <div className="min-h-screen bg-gray-50 flex items-center justify-center"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div></div>;

  if (!isAuthenticated) return <Navigate to="/login" replace />;

  if (!isAdmin(user)) return <Navigate to="/" replace />;

  return children;
};

const ValidatorRoute = ({ children }) => {
  const { isAuthenticated, loading, user } = useAuth();

  if (loading) return <div className="min-h-screen bg-gray-50 flex items-center justify-center"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div></div>;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (!canValidate(user)) return <Navigate to="/" replace />;

  return <ActiveRoleRoute role={ACTIVE_VALIDATOR}>{children}</ActiveRoleRoute>;
};

const TranslatorRoute = ({ children }) => {
  const { isAuthenticated, loading, user } = useAuth();

  if (loading) return <div className="min-h-screen bg-gray-50 flex items-center justify-center"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div></div>;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (!canTranslate(user)) return <Navigate to="/" replace />;

  return <ActiveRoleRoute role={ACTIVE_TRANSLATOR}>{children}</ActiveRoleRoute>;
};

const HistoryRoute = ({ children }) => {
  const { isAuthenticated, loading, user } = useAuth();

  if (loading) return <div className="min-h-screen bg-gray-50 flex items-center justify-center"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div></div>;
  if (!isAuthenticated) return <Navigate to="/login" replace />;

  if (!canValidate(user) && !canTranslate(user)) return <Navigate to="/" replace />;

  return children;
};

const HomeRedirect = () => {
  const { isAuthenticated, loading, user } = useAuth();

  if (loading) return <div className="min-h-screen bg-gray-50 flex items-center justify-center"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div></div>;
  if (!isAuthenticated) return <Navigate to="/login" replace />;

  if (isAdmin(user)) return <Navigate to="/admin/users" replace />;

  const activeRole = getStoredActiveRole(user);
  return <Navigate to={routeForActiveRole(activeRole)} replace />;
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
                  <ValidatorHome />
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
              path="/pending-translations"
              element={
                <TranslatorRoute>
                  <PendingTranslationsPage />
                </TranslatorRoute>
              }
            />
            <Route
              path="/help"
              element={
                <TranslatorRoute>
                  <HelpPage />
                </TranslatorRoute>
              }
            />
            <Route
              path="/validatorHelp"
              element={
                <ValidatorRoute>
                  <ValidatorHelpPage />
                </ValidatorRoute>
              }
            />
            <Route
             path="/leaderboard" 
              element={
                <TranslatorRoute>
                  <LeaderboardPage />
                </TranslatorRoute>
              }
            />
            <Route
              path="/leaderboard-general"
              element={
                <TranslatorRoute>
                  <AllTimeLeaderboardPage />
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
