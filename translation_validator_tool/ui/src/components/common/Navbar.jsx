import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import guaraniaLogoNoBG from '../../images/logo.svg';
import { ACTIVE_TRANSLATOR, ACTIVE_VALIDATOR, canTranslate, canValidate, isAdmin as userIsAdmin } from '../../utils/roles';

const Navbar = () => {
  const { user, logout, activeRole, setActiveRole } = useAuth();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [adminOpen, setAdminOpen] = useState(false);
  const [rankingOpen, setRankingOpen] = useState(false);
  const isAdmin = userIsAdmin(user);
  const isValidator = !isAdmin && activeRole === ACTIVE_VALIDATOR;
  const isTranslator = !isAdmin && activeRole === ACTIVE_TRANSLATOR;
  const canSwitchToTranslator = !!user && !isAdmin && canTranslate(user) && activeRole !== ACTIVE_TRANSLATOR;
  const canSwitchToValidator = !!user && !isAdmin && canValidate(user) && activeRole !== ACTIVE_VALIDATOR;

  const switchRole = (role) => {
    setActiveRole(role);
    setMobileOpen(false);
    navigate(role === ACTIVE_VALIDATOR ? '/validator' : '/translator-annotations');
  };

  return (
    <nav className="bg-gradient-to-r from-slate-900 to-teal-900 shadow-2xl">
      <div className="w-full px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 md:grid-cols-[1fr_auto_1fr] h-16 items-center">
          {/* Logo */}
          <div className="flex items-center justify-self-start">
            <div className="flex-shrink-0">
              <img src={guaraniaLogoNoBG} alt="Mbo'ehara Digital" className="h-10 w-auto" />
            </div>
          </div>

          {/* Desktop Navigation Links */}
          <div className="hidden md:flex items-center space-x-6 justify-self-center">
            {user ? (
              <>
                {isValidator && (
                  <a href="/validator" className="text-teal-100 hover:text-teal-300 px-3 py-2 text-sm font-medium transition-colors">Validar</a>
                )}
                {isValidator && (
                  <div className="relative">
                    <button
                      onClick={() => setRankingOpen(!rankingOpen)}
                      className="text-teal-100 hover:text-teal-300 px-3 py-2 text-sm font-medium flex items-center transition-colors"
                      aria-expanded={rankingOpen}
                    >
                      Ranking
                      <svg className="ml-1 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={rankingOpen ? 'M5 15l7-7 7 7' : 'M19 9l-7 7-7-7'} />
                      </svg>
                    </button>

                    {rankingOpen && (
                      <div className="absolute right-0 mt-2 w-48 bg-slate-800 border border-teal-700 rounded shadow-lg z-20">
                        <a href="/validation-leaderboard" className="block px-4 py-2 text-sm text-teal-100 hover:bg-slate-700 hover:text-teal-300 transition-colors">Semanal</a>
                        <a href="/validation-leaderboard-general" className="block px-4 py-2 text-sm text-teal-100 hover:bg-slate-700 hover:text-teal-300 transition-colors">General</a>
                      </div>
                    )}
                  </div>
                )}
                {isTranslator && (
                      <a href="/translator-annotations" className="text-teal-100 hover:text-teal-300 px-3 py-2 text-sm font-medium transition-colors">Mis pendientes</a>
                )}
                {isTranslator && (
                      <a href="/pending-translations" className="text-teal-100 hover:text-teal-300 px-3 py-2 text-sm font-medium transition-colors">Traducciones pendientes</a>
                )}
                {isTranslator && (
                  <div className="relative">
                    <button
                      onClick={() => setRankingOpen(!rankingOpen)}
                      className="text-teal-100 hover:text-teal-300 px-3 py-2 text-sm font-medium flex items-center transition-colors"
                      aria-expanded={rankingOpen}
                    >
                      Ranking
                      <svg className="ml-1 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={rankingOpen ? 'M5 15l7-7 7 7' : 'M19 9l-7 7-7-7'} />
                      </svg>
                    </button>

                    {rankingOpen && (
                      <div className="absolute right-0 mt-2 w-48 bg-slate-800 border border-teal-700 rounded shadow-lg z-20">
                        <a href="/leaderboard" className="block px-4 py-2 text-sm text-teal-100 hover:bg-slate-700 hover:text-teal-300 transition-colors">Semanal</a>
                        <a href="/leaderboard-general" className="block px-4 py-2 text-sm text-teal-100 hover:bg-slate-700 hover:text-teal-300 transition-colors">General</a>
                      </div>
                    )}
                  </div>
                )}
                {isTranslator && (
                    <Link to="/help" className="text-teal-100 hover:text-teal-300 px-3 py-2 text-sm font-medium transition-colors">Ayuda</Link>
                )}
                {isValidator && (
                  <a href="/validatorHelp" className="text-teal-100 hover:text-teal-300 px-3 py-2 text-sm font-medium transition-colors">Ayuda</a>
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
          <div className="hidden md:flex items-center space-x-4 justify-self-end">
            {user ? (
              <>
                <div className="text-sm text-teal-100"><span className="font-medium text-white">Bienvenido, {user.username}</span></div>
                {canSwitchToTranslator && (
                  <button type="button" onClick={() => switchRole(ACTIVE_TRANSLATOR)} className="btn bg-teal-600 text-white hover:bg-teal-700 px-4 py-2 rounded-lg font-medium transition-colors">Cambiar a traductor</button>
                )}
                {canSwitchToValidator && (
                  <button type="button" onClick={() => switchRole(ACTIVE_VALIDATOR)} className="btn bg-teal-600 text-white hover:bg-teal-700 px-4 py-2 rounded-lg font-medium transition-colors">Cambiar a validador</button>
                )}
                <button onClick={logout} className="btn bg-teal-600 text-white hover:bg-teal-700 px-4 py-2 rounded-lg font-medium transition-colors">Cerrar sesión</button>
              </>
            ) : (
              <div className="hidden md:flex items-center">
                <a href="/login" className="text-teal-100 hover:text-teal-300 px-3 py-2 text-sm font-medium transition-colors">Iniciar sesión</a>
              </div>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center justify-self-end">
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
                    {isValidator && (
                      <div>
                        <button
                          onClick={() => setRankingOpen(!rankingOpen)}
                          className="w-full flex items-center justify-between text-teal-100 px-3 py-2 rounded-md text-base font-medium hover:bg-slate-700 hover:text-teal-300 transition-colors"
                          aria-expanded={rankingOpen}
                        >
                          Ranking
                          <svg className="ml-1 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={rankingOpen ? 'M5 15l7-7 7 7' : 'M19 9l-7 7-7-7'} />
                          </svg>
                        </button>

                        {rankingOpen && (
                          <div className="ml-4 mt-1 space-y-1">
                            <a href="/validation-leaderboard" className="block text-teal-100 px-3 py-2 rounded-md text-sm font-medium hover:bg-slate-700 hover:text-teal-300 transition-colors">Semanal</a>
                            <a href="/validation-leaderboard-general" className="block text-teal-100 px-3 py-2 rounded-md text-sm font-medium hover:bg-slate-700 hover:text-teal-300 transition-colors">General</a>
                          </div>
                        )}
                      </div>
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
                      <div>
                        <button
                          onClick={() => setRankingOpen(!rankingOpen)}
                          className="w-full flex items-center justify-between text-teal-100 px-3 py-2 rounded-md text-base font-medium hover:bg-slate-700 hover:text-teal-300 transition-colors"
                          aria-expanded={rankingOpen}
                        >
                          Ranking
                          <svg className="ml-1 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={rankingOpen ? 'M5 15l7-7 7 7' : 'M19 9l-7 7-7-7'} />
                          </svg>
                        </button>

                        {rankingOpen && (
                          <div className="ml-4 mt-1 space-y-1">
                            <a href="/leaderboard" className="block text-teal-100 px-3 py-2 rounded-md text-sm font-medium hover:bg-slate-700 hover:text-teal-300 transition-colors">Semanal</a>
                            <a href="/leaderboard-general" className="block text-teal-100 px-3 py-2 rounded-md text-sm font-medium hover:bg-slate-700 hover:text-teal-300 transition-colors">General</a>
                          </div>
                        )}
                      </div>
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
                      <div className="mt-2 space-y-2">
                        {canSwitchToTranslator && (
                          <button type="button" onClick={() => switchRole(ACTIVE_TRANSLATOR)} className="w-full text-left btn bg-teal-600 text-white hover:bg-teal-700 px-3 py-2 rounded-lg font-medium transition-colors">Cambiar a traductor</button>
                        )}
                        {canSwitchToValidator && (
                          <button type="button" onClick={() => switchRole(ACTIVE_VALIDATOR)} className="w-full text-left btn bg-teal-600 text-white hover:bg-teal-700 px-3 py-2 rounded-lg font-medium transition-colors">Cambiar a validador</button>
                        )}
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
