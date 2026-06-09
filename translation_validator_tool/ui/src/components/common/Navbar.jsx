import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import guaraniaLogoNoBG from '../../images/logo.svg';

const Navbar = () => {
  const { user, logout } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [adminOpen, setAdminOpen] = useState(false);
  const role = !user ? null : (user.role || (user.is_superuser ? 'admin' : 'validador'));
  const isAdmin = role === 'admin';
  const isValidator = role === 'validador';
  const isTranslator = role === 'traductor';
  const canSeeHistory = isValidator || isTranslator;

  return (
    <nav className="bg-gradient-to-r from-slate-900 to-teal-900 shadow-2xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          {/* Logo */}
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <img src={guaraniaLogoNoBG} alt="Mbo'ehara Digital" className="h-10 w-auto" />
            </div>
          </div>

          {/* Desktop Navigation Links */}
          <div className="hidden md:flex items-center space-x-6">
            {user ? (
              <>
                {isValidator && (
                  <a href="/validator" className="text-teal-100 hover:text-teal-300 px-3 py-2 text-sm font-medium transition-colors">Validar</a>
                )}
                {isTranslator && (
                      <a href="/translator-annotations" className="text-teal-100 hover:text-teal-300 px-3 py-2 text-sm font-medium transition-colors">Mis pendientes</a>
                )}
                {isTranslator && (
                      <a href="/pending-translations" className="text-teal-100 hover:text-teal-300 px-3 py-2 text-sm font-medium transition-colors">Traducciones pendientes</a>
                )}
                {isTranslator && (
                      <a href="/leaderboard" className="text-teal-100 hover:text-teal-300 px-3 py-2 text-sm font-medium transition-colors">Ranking semanal</a>
                )}
                {isTranslator && (
                    <Link to="/help" className="text-teal-100 hover:text-teal-300 px-3 py-2 text-sm font-medium transition-colors">Ayuda</Link>
                )}
                {isValidator && (
                  <a href="/history" className="text-teal-100 hover:text-teal-300 px-3 py-2 text-sm font-medium transition-colors">Historial</a>
                )}
                  {isValidator && (
                      <a href="/validatorHelp" className="block text-teal-100 px-3 py-2 rounded-md text-base font-medium hover:bg-slate-700 hover:text-teal-300 transition-colors">Ayuda</a>
                    )}
                {isAdmin && (
                  // Compact admin menu: one label that reveals two explicit admin links
                  <div className="relative">
                    <button
                      onClick={() => setAdminOpen(!adminOpen)}
                      className="text-teal-100 hover:text-teal-300 px-3 py-2 text-sm font-medium flex items-center transition-colors"
                      aria-expanded={adminOpen}
                    >
                      Admin
                      <svg className="ml-1 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={adminOpen ? 'M5 15l7-7 7 7' : 'M19 9l-7 7-7-7'} />
                      </svg>
                    </button>

                    {adminOpen && (
                      <div className="absolute right-0 mt-2 w-56 bg-slate-800 border border-teal-700 rounded shadow-lg z-20">
                        <a href="/admin/users" className="block px-4 py-2 text-sm text-teal-100 hover:bg-slate-700 hover:text-teal-300 transition-colors">Usuarios</a>
                        {/*<a href="/admin/pending" className="block px-4 py-2 text-sm text-teal-100 hover:bg-slate-700 hover:text-teal-300">Registros Pendientes</a>*/}
                        <a href="/admin/annotations" className="block px-4 py-2 text-sm text-teal-100 hover:bg-slate-700 hover:text-teal-300 transition-colors">Anotaciones</a>
                        {/*<a href="/admin/translations" className="block px-4 py-2 text-sm text-teal-100 hover:bg-slate-700 hover:text-teal-300">Traducciones</a>*/}
                      </div>
                    )}
                  </div>
                )}
              </>
            ) : (
              <>
                <a href="/" className="text-teal-100 hover:text-teal-300 px-3 py-2 text-sm font-medium transition-colors">Validar</a>
                <a href="/register" className="text-teal-100 hover:text-teal-300 px-3 py-2 text-sm font-medium transition-colors">Registro</a>
              </>
            )}
          </div>

          {/* Desktop user info and logout */}
          <div className="hidden md:flex items-center space-x-4">
            {user ? (
              <>
                <div className="text-sm text-teal-100"><span className="font-medium text-white">Bienvenido, {user.username}</span></div>
                <button onClick={logout} className="btn bg-teal-600 text-white hover:bg-teal-700 px-4 py-2 rounded-lg font-medium transition-colors">Cerrar sesión</button>
              </>
            ) : (
              <div className="hidden md:flex items-center">
                <a href="/login" className="text-teal-100 hover:text-teal-300 px-3 py-2 text-sm font-medium transition-colors">Iniciar sesión</a>
              </div>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center">
            <button
              onClick={() => setMobileOpen(!mobileOpen)}
              aria-expanded={mobileOpen}
              aria-label="Abrir menú"
              className="inline-flex items-center justify-center p-2 rounded-md text-teal-100 hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-teal-500 transition-colors"
            >
              <svg className="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                {mobileOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu panel */}
      {mobileOpen && (
        <div className="md:hidden bg-slate-800 border-t border-teal-700">
          <div className="px-4 pt-4 pb-3 space-y-2">
                {user ? (
                  <>
                    {isValidator && (
                      <a href="/validator" className="block text-teal-100 px-3 py-2 rounded-md text-base font-medium hover:bg-slate-700 hover:text-teal-300 transition-colors">Validar</a>
                    )}
                    {isTranslator && (
                      <a href="/translator-annotations" className="block text-teal-100 px-3 py-2 rounded-md text-base font-medium hover:bg-slate-700 hover:text-teal-300 transition-colors">Mis pendientes</a>
                    )}
                    {isTranslator && (
                         <a href="/pending-translations" className="block text-teal-100 px-3 py-2 rounded-md text-base font-medium hover:bg-slate-700 hover:text-teal-300 transition-colors">Traducciones pendientes</a>
                    )}
                     {isTranslator && (
                      <Link to="/help" className="block text-teal-100 px-3 py-2 rounded-md text-base font-medium hover:bg-slate-700 hover:text-teal-300 transition-colors">Ayuda</Link>
                    )}
                     {isTranslator && (
                      <a href="/leaderboard" className="text-teal-100 hover:text-teal-300 px-3 py-2 text-sm font-medium transition-colors">Ranking semanal</a>
                    )}
                    {isValidator && (
                      <a href="/history" className="block text-teal-100 px-3 py-2 rounded-md text-base font-medium hover:bg-slate-700 hover:text-teal-300 transition-colors">Historial</a>
                    )}
                     {isValidator && (
                      <a href="/validatorHelp" className="block text-teal-100 px-3 py-2 rounded-md text-base font-medium hover:bg-slate-700 hover:text-teal-300 transition-colors">Ayuda</a>
                    )}
                    {isAdmin && (
                      <div className="pt-2">
                        <div className="text-sm font-medium text-teal-300">Admin</div>
                        <a href="/admin/users" className="block text-teal-100 px-3 py-2 rounded-md text-base font-medium hover:bg-slate-700 hover:text-teal-300 transition-colors">Usuarios</a>
                        <a href="/admin/pending" className="block text-teal-100 px-3 py-2 rounded-md text-base font-medium hover:bg-slate-700 hover:text-teal-300 transition-colors">Registros Pendientes</a>
                        <a href="/admin/annotations" className="block text-teal-100 px-3 py-2 rounded-md text-base font-medium hover:bg-slate-700 hover:text-teal-300 transition-colors">Anotaciones</a>
                      </div>
                    )}

                    <div className="pt-2 border-t border-teal-700">
                      <div className="text-sm text-teal-100">Bienvenido, <span className="font-medium text-white">{user.username}</span></div>
                      <div className="mt-2">
                        <button onClick={logout} className="w-full text-left btn bg-teal-600 text-white hover:bg-teal-700 px-3 py-2 rounded-lg font-medium transition-colors">Cerrar sesión</button>
                      </div>
                    </div>
                  </>
                ) : (
                  <>
                    <a href="/" className="block text-teal-100 px-3 py-2 rounded-md text-base font-medium hover:bg-slate-700 hover:text-teal-300 transition-colors">Inicio</a>
                    <a href="/register" className="block text-teal-100 px-3 py-2 rounded-md text-base font-medium hover:bg-slate-700 hover:text-teal-300 transition-colors">Registro</a>
                    <a href="/login" className="block text-teal-100 px-3 py-2 rounded-md text-base font-medium hover:bg-slate-700 hover:text-teal-300 transition-colors">Iniciar sesión</a>
                  </>
                )}
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
