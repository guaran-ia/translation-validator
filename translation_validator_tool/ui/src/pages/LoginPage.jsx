import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import HelpModal from '../components/auth/HelpModal';
import guaraniaLogoNoBG from '../images/logo.svg';
import WeeklyLeaderboard from '../components/common/WeeklyLeaderboard';
import { getStoredActiveRole, isAdmin, routeForActiveRole } from '../utils/roles';

const LoginPage = () => {
  const navigate = useNavigate();
  const { isAuthenticated, user, login, error, clearError } = useAuth();
  const [formData, setFormData] = useState({ username: '', password: '' });
  const [isLoading, setIsLoading] = useState(false);
  const [showHelp, setShowHelp] = useState(false);

  const redirectByRole = (u) => {
    if (isAdmin(u)) return '/admin/users';
    return routeForActiveRole(getStoredActiveRole(u));
  };

  useEffect(() => {
    if (isAuthenticated) {
      navigate(redirectByRole(user), { replace: true });
    }
  }, [isAuthenticated, user, navigate]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (error) clearError();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const result = await login(formData.username, formData.password);
      if (result.success) {
        navigate(redirectByRole(result.user));
      }
    } catch (err) {
      console.error('Login error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const location = useLocation();
  const notice = location.state?.notice;

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
        <div className="grid grid-cols-1 xl:grid-cols-[minmax(620px,1fr)_420px_320px] gap-8 items-start">
          {/* Left Section - Branding (Hidden on mobile, 60% on desktop) */}
          <div className="hidden xl:flex flex-col justify-center items-start space-y-8 pr-8">
            {/* Logo - image plus descriptive text */}
            <div className="flex items-center space-x-4">
              <img src={guaraniaLogoNoBG} alt="Mbo'ehara Digital" className="h-14 w-auto" />
            </div>

            {/* Main Title */}
            <div className="space-y-4">
              <h1 className="text-5xl lg:text-6xl font-bold text-white leading-tight">
                ¡Convertite en
              </h1>
              <h1 className="text-5xl lg:text-6xl font-bold text-teal-400 leading-tight">"Mbo'ehara Digital"!
              </h1>
               <p className="text-xl text-teal-100 max-w-2xl">
                Buscamos impulsar la inclusión de nuestra lengua en el ecosistema tecnológico actual. Queremos que asumas un rol protagónico como "profesor" de la Inteligencia Artificial (IA), permitiendo que el futuro hable nuestro idioma..
              </p>
            </div>

            {/* Key Points */}
            <div className="space-y-4 pt-4">
              <p className="text-xl text-white font-semibold">Buscamos:</p>
              <div className="flex items-start space-x-4">
                <div className="w-8 h-8 rounded-lg bg-teal-500 flex items-center justify-center flex-shrink-0 mt-1">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <div>
                  <h4 className="text-white font-semibold">Inclusión Digital:</h4>
                  <p className="text-sm text-teal-100">Democratiza el acceso tecnológico para comunidades que utilizan el guaraní como lengua materna.</p>
                </div>
              </div>

              <div className="flex items-start space-x-4">
                <div className="w-8 h-8 rounded-lg bg-teal-500 flex items-center justify-center flex-shrink-0 mt-1">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <div>
                  <h4 className="text-white font-semibold">Preservación Lingüística:</h4>
                  <p className="text-sm text-teal-100">Evita que el idioma quede rezagado, otorgándole una "segunda vida" como lengua tecnológica.</p>
                </div>
              </div>

              <div className="flex items-start space-x-4">
                <div className="w-8 h-8 rounded-lg bg-teal-500 flex items-center justify-center flex-shrink-0 mt-1">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <div>
                  <h4 className="text-white font-semibold">Soberanía y Naturalidad:</h4>
                  <p className="text-sm text-teal-100">Al ser entrenada por voluntarios y no por máquinas, la IA aprende modismos y contextos reales, permitiendo que Paraguay lidere la representación de su propia cultura en la informática.</p>
                </div>
              </div>
            </div>
          </div>

          {/* Right Section - Login Form (40% on desktop, full on mobile) */}
          <div className="lg:col-span-1 flex items-center justify-center">
            <div className="w-full max-w-sm bg-white rounded-2xl shadow-2xl overflow-hidden transform transition duration-300 hover:shadow-3xl">
              {/* Card Header */}
              <div className="bg-gradient-to-r from-teal-600 to-teal-700 px-8 py-10 text-center">
                <h2 className="text-2xl font-bold text-white mb-2">Bienvenido a la plataforma</h2>
                <p className="text-teal-100 text-sm">Inicia sesión para continuar.</p>
              </div>

              {/* Card Body */}
              <form onSubmit={handleSubmit} className="px-8 py-8 space-y-6">
                {/* Notice */}
                {notice && (
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <p className="text-green-800 text-sm font-medium">{notice}</p>
                  </div>
                )}

                {/* Error Message */}
                {error && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <p className="text-red-700 text-sm font-medium">{error}</p>
                  </div>
                )}

                {/* Username Input */}
                <div className="space-y-2">
                  <label htmlFor="username" className="block text-sm font-semibold text-gray-700">
                    Usuario
                  </label>
                  <input
                    id="username"
                    name="username"
                    type="text"
                    required
                    value={formData.username}
                    onChange={handleChange}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-teal-500 focus:ring-2 focus:ring-teal-200 outline-none transition duration-200 text-gray-800 placeholder-gray-400"
                    placeholder="Ingresa tu usuario"
                  />
                </div>

                {/* Password Input */}
                <div className="space-y-2">
                  <label htmlFor="password" className="block text-sm font-semibold text-gray-700">
                    Contraseña
                  </label>
                  <input
                    id="password"
                    name="password"
                    type="password"
                    required
                    value={formData.password}
                    onChange={handleChange}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-teal-500 focus:ring-2 focus:ring-teal-200 outline-none transition duration-200 text-gray-800 placeholder-gray-400"
                    placeholder="Ingresa tu contraseña"
                  />
                </div>

                {/* Login Button */}
                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full py-3 px-4 bg-gradient-to-r from-teal-500 to-teal-600 hover:from-teal-600 hover:to-teal-700 text-white font-bold rounded-lg transition duration-200 transform hover:scale-105 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
                >
                  {isLoading ? (
                    <>
                      <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      <span>Iniciando sesión...</span>
                    </>
                  ) : (
                    <span>Iniciar sesión</span>
                  )}
                </button>

                {/* Help and Register Buttons */}
                <div className="pt-4 space-y-3">
  
                  <button
                    type="button"
                    onClick={() => navigate('/register')}
                    className="w-full inline-flex flex-col items-start justify-center bg-teal-500 hover:bg-teal-600 text-white text-sm font-semibold px-4 py-3 rounded-full shadow-md transition duration-200"
                    aria-label="Crear cuenta - regístrate en la plataforma"
                  >
                    <div className="flex items-center space-x-3">
                      <div className="text-left">
                        <span className="block text-sm font-semibold">¿No tienes cuenta?</span>
                        <span className="block text-xs font-normal text-teal-100">Regístrate en la plataforma.</span>
                      </div>
                    </div>
                  </button>

                  <button
                    type="button"
                    onClick={() => setShowHelp(true)}
                    className="w-full inline-flex flex-col items-start justify-center bg-teal-500 hover:bg-teal-600 text-white text-sm font-semibold px-4 py-3 rounded-full shadow-md transition duration-200"
                    aria-label="Necesitas ayuda - ver video instructivo"
                  >
                    <div className="flex items-center space-x-3">
                      <div className="text-left">
                        <span className="block text-sm font-semibold">¿Necesitas ayuda?</span>
                        <span className="block text-xs font-normal text-teal-100">Tenemos un video instructivo que puede ayudarte.</span>
                      </div>
                    </div>
                  </button>
                  
                </div>
              </form>

              {/* Card Footer */}
              <div className="bg-gray-50 px-8 py-4 text-center border-t border-gray-100">
                <p className="text-xs text-gray-600">
                  GuaranIA © 2026
                </p>
              </div>
            </div>
          </div>
            <div className="hidden 2xl:flex justify-center">
          <WeeklyLeaderboard source="json" />
        </div>
        </div>
      </div>

      {/* Help Modal */}
      <HelpModal isOpen={showHelp} onClose={() => setShowHelp(false)} />
    </div>
  );
};

export default LoginPage;
