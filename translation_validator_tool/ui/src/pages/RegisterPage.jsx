import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline';

const RegisterPage = () => {
  const { register, error, clearError } = useAuth();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({ 
    username: '', 
    email: '', 
    nombre_completo: '',
    contacto: '',
    password: '', 
    confirmPassword: '' 
  });
  const [loading, setLoading] = useState(false);
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
      navigate('/login', { state: { notice: 'Cuenta creada exitosamente. Ya puedes iniciar sesión.' } });
      return;
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-teal-900 to-slate-900 flex items-center justify-center overflow-hidden">
      {/* Decorative SVG Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <svg className="absolute -left-40 -top-40 w-80 h-80 text-teal-700 opacity-20" viewBox="0 0 200 200">
          <circle cx="100" cy="100" r="100" fill="currentColor" />
        </svg>
        <svg className="absolute -right-40 -bottom-40 w-96 h-96 text-teal-600 opacity-15" viewBox="0 0 200 200">
          <path d="M100,20 Q160,60 160,120 Q160,180 100,180 Q40,180 40,120 Q40,60 100,20" fill="currentColor" />
        </svg>
        <svg className="absolute top-1/3 right-10 w-64 h-64 text-teal-500 opacity-10" viewBox="0 0 200 200">
          <path d="M50,50 L150,50 L150,150 L50,150 Z M80,80 L120,80 L120,120 L80,120 Z" fill="currentColor" />
        </svg>
      </div>

      {/* Main Container */}
      <div className="relative z-10 w-full max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-center">
          {/* Registration Form Card */}
          <div className="w-full max-w-2xl bg-white rounded-2xl shadow-2xl overflow-hidden transform transition duration-300 hover:shadow-3xl">
            {/* Card Header */}
            <div className="bg-gradient-to-r from-teal-600 to-teal-700 px-4 py-6 text-center">
              <h2 className="text-2xl font-bold text-white mb-2">Crear cuenta</h2>
              {/* <p className="text-teal-100 text-sm">El administrador deberá aprobar tu registro.</p> */}
            </div>

            {/* Card Body */}
            <form onSubmit={handleSubmit} className="px-8 py-8 space-y-6">
              {/* Error Message */}
              {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <p className="text-red-700 text-sm font-medium">{error}</p>
                </div>
              )}

              {validationErrors.general && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <p className="text-red-700 text-sm font-medium">{validationErrors.general}</p>
                </div>
              )}

              {/* Two Column Grid */}
              <div className="grid grid-cols-2 gap-4">
                {/* Username Input */}
                <div className="space-y-2">
                  <label htmlFor="username" className="block text-sm font-semibold text-gray-700">
                    Usuario
                  </label>
                  <input 
                    id="username"
                    name="username" 
                    required 
                    value={formData.username} 
                    onChange={handleChange}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-teal-500 focus:ring-2 focus:ring-teal-200 outline-none transition duration-200 text-gray-800 placeholder-gray-400"
                    placeholder="juanperez124"
                  />
                  <p className="text-xs text-gray-500">Solo minúsculas, números, guiones</p>
                  {validationErrors.username && (
                    <p className="text-sm text-red-600">{validationErrors.username}</p>
                  )}
                </div>

                {/* Nombre Completo Input */}
                <div className="space-y-2">
                  <label htmlFor="nombre_completo" className="block text-sm font-semibold text-gray-700">
                    Nombre Completo
                  </label>
                  <input 
                    id="nombre_completo"
                    name="nombre_completo" 
                    value={formData.nombre_completo} 
                    onChange={handleChange}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-teal-500 focus:ring-2 focus:ring-teal-200 outline-none transition duration-200 text-gray-800 placeholder-gray-400"
                    placeholder="Juan Pérez"
                  />
                </div>

                {/* Email Input */}
                <div className="space-y-2">
                  <label htmlFor="email" className="block text-sm font-semibold text-gray-700">
                    Correo electrónico
                  </label>
                  <input 
                    id="email"
                    name="email" 
                    type="email" 
                    required 
                    value={formData.email} 
                    onChange={handleChange}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-teal-500 focus:ring-2 focus:ring-teal-200 outline-none transition duration-200 text-gray-800 placeholder-gray-400"
                    placeholder="usuario@ejemplo.com"
                  />
                </div>

                {/* Contacto Input */}
                <div className="space-y-2">
                  <label htmlFor="contacto" className="block text-sm font-semibold text-gray-700">
                    Contacto
                  </label>
                  <input 
                    id="contacto"
                    name="contacto" 
                    value={formData.contacto} 
                    onChange={handleChange}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-teal-500 focus:ring-2 focus:ring-teal-200 outline-none transition duration-200 text-gray-800 placeholder-gray-400"
                    placeholder="Teléfono o WhatsApp"
                  />
                </div>

                {/* Password Input */}
                <div className="space-y-2">
                  <label htmlFor="password" className="block text-sm font-semibold text-gray-700">
                    Contraseña
                  </label>
                  <div className="relative">
                    <input 
                      id="password"
                      name="password" 
                      type={showPassword ? "text" : "password"} 
                      required 
                      value={formData.password} 
                      onChange={handleChange}
                      className="w-full px-4 py-3 pr-10 border-2 border-gray-200 rounded-lg focus:border-teal-500 focus:ring-2 focus:ring-teal-200 outline-none transition duration-200 text-gray-800 placeholder-gray-400"
                      placeholder="Mínimo 6 caracteres"
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
                    <p className="text-sm text-red-600">{validationErrors.password}</p>
                  )}
                </div>

                {/* Confirm Password Input */}
                <div className="space-y-2">
                  <label htmlFor="confirmPassword" className="block text-sm font-semibold text-gray-700">
                    Confirmar contraseña
                  </label>
                  <div className="relative">
                    <input 
                      id="confirmPassword"
                      name="confirmPassword" 
                      type={showConfirmPassword ? "text" : "password"} 
                      required 
                      value={formData.confirmPassword} 
                      onChange={handleChange}
                      className="w-full px-4 py-3 pr-10 border-2 border-gray-200 rounded-lg focus:border-teal-500 focus:ring-2 focus:ring-teal-200 outline-none transition duration-200 text-gray-800 placeholder-gray-400"
                      placeholder="Repetir contraseña"
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
                    <p className="text-sm text-red-600">{validationErrors.confirmPassword}</p>
                  )}
                </div>
              </div>

              {/* Register Button */}
              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 px-4 bg-gradient-to-r from-teal-500 to-teal-600 hover:from-teal-600 hover:to-teal-700 text-white font-bold rounded-lg transition duration-200 transform hover:scale-105 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
              >
                {loading ? (
                  <>
                    <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span>Creando cuenta...</span>
                  </>
                ) : (
                  <span>Crear cuenta</span>
                )}
              </button>

              {/* Back to Login Button */}
              <button
                type="button"
                onClick={() => navigate('/login')}
                className="w-full inline-flex flex-col items-center justify-center bg-teal-500 hover:bg-teal-600 text-white text-sm font-semibold px-4 py-3 rounded-full shadow-md transition duration-200"
              >
                <span className="text-sm font-semibold">¿Ya tienes cuenta?</span>
                <span className="text-xs font-normal text-teal-100">Volver al login</span>
              </button>
            </form>

            {/* Card Footer */}
            <div className="bg-gray-50 px-8 py-4 text-center border-t border-gray-100">
              <p className="text-xs text-gray-600">
                GuaranIA © 2026
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
