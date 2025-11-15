import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline';

const RegisterPage = () => {
  const { register, error, clearError } = useAuth();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({ username: '', email: '', password: '', confirmPassword: '' });
  const [loading, setLoading] = useState(false);
  const [successMsg, setSuccessMsg] = useState(null);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [validationErrors, setValidationErrors] = useState({});

  const handleChange = (e) => {
    const { name, value } = e.target;
    let processedValue = value;
    
    // Validación username: solo minúsculas y sin espacios
    if (name === 'username') {
      processedValue = value.toLowerCase().replace(/\s/g, '');
    }
    
    setFormData(prev => ({ ...prev, [name]: processedValue }));
    
    // Limpiar errores cuando el usuario escribe
    if (error) clearError();
    if (validationErrors[name]) {
      setValidationErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = () => {
    const errors = {};
    
    // Validar username
    if (formData.username.length < 3) {
      errors.username = 'El nombre de usuario debe tener al menos 3 caracteres';
    }
    if (!/^[a-z0-9_-]+$/.test(formData.username)) {
      errors.username = 'Solo se permiten letras minúsculas, números, guiones y guiones bajos';
    }
    
    // Validar contraseña
    if (formData.password.length < 6) {
      errors.password = 'La contraseña debe tener al menos 6 caracteres';
    }
    
    // Validar confirmación de contraseña
    if (formData.password !== formData.confirmPassword) {
      errors.confirmPassword = 'Las contraseñas no coinciden';
    }
    
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setSuccessMsg(null);

    if (!formData.username || !formData.email || !formData.password || !formData.confirmPassword) {
      setValidationErrors({ general: 'Por favor completa todos los campos' });
      setLoading(false);
      return;
    }

    // Validar formulario
    if (!validateForm()) {
      setLoading(false);
      return;
    }

    const res = await register(formData);
    if (res.success) {
      // After successful registration show the message and navigate back to login
      // so the user can see the notice and attempt to login later after approval.
      // Navigate to login and pass a notice so the login page can show feedback.
      navigate('/login', { state: { notice: 'Registro creado. Esperando aprobación del administrador.' } });
      return;
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">Crear cuenta</h2>
          <p className="mt-2 text-center text-sm text-gray-600">El administrador deberá aprobar tu registro.</p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-4">
            {/* Username */}
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-1">
                Usuario
              </label>
              <input 
                id="username"
                name="username" 
                required 
                className="relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500" 
                placeholder="usuario123" 
                value={formData.username} 
                onChange={handleChange} 
              />
              <p className="mt-1 text-xs text-gray-500">Solo minúsculas, números, guiones y guiones bajos</p>
              {validationErrors.username && (
                <p className="mt-1 text-sm text-red-600">{validationErrors.username}</p>
              )}
            </div>

            {/* Email */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                Correo electrónico
              </label>
              <input 
                id="email"
                name="email" 
                type="email" 
                required 
                className="relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500" 
                placeholder="usuario@ejemplo.com" 
                value={formData.email} 
                onChange={handleChange} 
              />
            </div>

            {/* Password */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                Contraseña
              </label>
              <div className="relative">
                <input 
                  id="password"
                  name="password" 
                  type={showPassword ? "text" : "password"} 
                  required 
                  className="relative block w-full px-3 py-2 pr-10 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500" 
                  placeholder="Mínimo 6 caracteres" 
                  value={formData.password} 
                  onChange={handleChange} 
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
                >
                  {showPassword ? (
                    <EyeSlashIcon className="h-5 w-5" />
                  ) : (
                    <EyeIcon className="h-5 w-5" />
                  )}
                </button>
              </div>
              {validationErrors.password && (
                <p className="mt-1 text-sm text-red-600">{validationErrors.password}</p>
              )}
            </div>

            {/* Confirm Password */}
            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-1">
                Confirmar contraseña
              </label>
              <div className="relative">
                <input 
                  id="confirmPassword"
                  name="confirmPassword" 
                  type={showConfirmPassword ? "text" : "password"} 
                  required 
                  className="relative block w-full px-3 py-2 pr-10 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500" 
                  placeholder="Repetir contraseña" 
                  value={formData.confirmPassword} 
                  onChange={handleChange} 
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
                >
                  {showConfirmPassword ? (
                    <EyeSlashIcon className="h-5 w-5" />
                  ) : (
                    <EyeIcon className="h-5 w-5" />
                  )}
                </button>
              </div>
              {validationErrors.confirmPassword && (
                <p className="mt-1 text-sm text-red-600">{validationErrors.confirmPassword}</p>
              )}
            </div>
          </div>

          {error && <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded mt-4">{error}</div>}
          {validationErrors.general && <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded mt-4">{validationErrors.general}</div>}

          <div className="flex flex-col gap-3">
            <div>
              <button type="submit" disabled={loading} className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50">
                {loading ? 'Creando cuenta...' : 'Crear cuenta'}
              </button>
            </div>
            <div className="text-center">
              <Link to="/login" className="text-sm text-indigo-600 hover:text-indigo-700">Volver al login</Link>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default RegisterPage;
