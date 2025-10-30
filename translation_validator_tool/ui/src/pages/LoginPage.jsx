import { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import LoginForm from '../components/auth/LoginForm';

const LoginPage = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/validator', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const handleLoginSuccess = () => {
    navigate('/validator');
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