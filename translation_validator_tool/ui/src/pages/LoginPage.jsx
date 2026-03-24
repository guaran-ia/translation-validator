import { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import LoginForm from '../components/auth/LoginForm';

const LoginPage = () => {
  const navigate = useNavigate();
  const { isAuthenticated, user } = useAuth();

  const getUserRole = (u) => {
    if (!u) return null;
    if (u.role) return u.role;
    return u.is_superuser ? 'admin' : 'validador';
  };

  const redirectByRole = (u) => {
    const role = getUserRole(u);
    if (role === 'admin') return '/admin/users';
    if (role === 'traductor') return '/translator-annotations';
    return '/validator';
  };

  useEffect(() => {
    if (isAuthenticated) {
      navigate(redirectByRole(user), { replace: true });
    }
  }, [isAuthenticated, user, navigate]);

  const handleLoginSuccess = (loggedUser) => {
    navigate(redirectByRole(loggedUser));
  };

  // Show optional notice passed from registration redirect
  const location = useLocation();
  const notice = location.state?.notice;

  return (
    <div>
      {notice && (
        <div className="max-w-md mx-auto mt-6 bg-green-50 border border-green-100 text-green-800 px-4 py-3 rounded">
          {notice}
        </div>
      )}
      <LoginForm onSuccess={handleLoginSuccess} />
    </div>
  );
};

export default LoginPage;