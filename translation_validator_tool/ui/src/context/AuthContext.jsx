import { createContext, useState, useEffect, useContext } from 'react';
import { authAPI } from '../services/api';
import { getStoredToken, setStoredToken, removeStoredToken, isAuthenticated } from '../services/auth';
import { getStoredActiveRole, removeStoredActiveRole, setStoredActiveRole } from '../utils/roles';

export const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [activeRole, setActiveRoleState] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const initializeAuth = async () => {
      const token = getStoredToken();
      
      if (token && isAuthenticated()) {
        try {
          const response = await authAPI.getCurrentUser();
          setUser(response.data);
          setActiveRoleState(getStoredActiveRole(response.data));
        } catch (error) {
          console.error('Failed to get current user:', error);
          removeStoredToken();
        }
      }
      
      setLoading(false);
    };

    initializeAuth();
  }, []);

  useEffect(() => {
    setActiveRoleState(getStoredActiveRole(user));
  }, [user]);

  const setActiveRole = (role) => {
    setStoredActiveRole(role);
    setActiveRoleState(role);
  };

  const login = async (username, password) => {
    try {
      setError(null);
      const response = await authAPI.login(username, password);
      const { access_token, user: userData } = response.data;
      
      setStoredToken(access_token);
      setUser(userData);
      setActiveRoleState(getStoredActiveRole(userData));
      
      return { success: true, user: userData };
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Login failed';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  const register = async (userData) => {
    try {
      setError(null);
      const response = await authAPI.register(userData);
      return { success: true, user: response.data };
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Registration failed';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  const logout = () => {
    removeStoredToken();
    removeStoredActiveRole();
    setUser(null);
    setActiveRoleState(null);
    setError(null);
  };

  const clearError = () => {
    setError(null);
  };

  const value = {
    user,
    loading,
    error,
    login,
    register,
    logout,
    activeRole,
    setActiveRole,
    clearError,
    isAuthenticated: !!user,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
