import { useState } from 'react';
import { useAuth } from '../../hooks/useAuth';

const Navbar = () => {
  const { user, logout } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <nav className="bg-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          {/* Logo and title */}
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <h1 className="text-xl font-bold text-gray-900">Translation Validator</h1>
            </div>
            <div className="ml-4 text-sm text-gray-600 hidden sm:block">Guaraní ↔ Español</div>
          </div>

          {/* Desktop Navigation Links */}
          <div className="hidden md:flex items-center space-x-6">
            {user ? (
              <>
                <a href="/" className="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium">Validar</a>
                <a href="/history" className="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium">Historial</a>
                {user.is_superuser && (
                  <a href="/admin/users" className="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium">Admin</a>
                )}
              </>
            ) : (
              <>
                <a href="/" className="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium">Validar</a>
                <a href="/register" className="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium">Registro</a>
              </>
            )}
          </div>

          {/* Desktop user info and logout */}
          <div className="hidden md:flex items-center space-x-4">
            {user ? (
              <>
                <div className="text-sm text-gray-700">Bienvenido, <span className="font-medium">{user.username}</span></div>
                <button onClick={logout} className="btn btn-secondary">Cerrar sesión</button>
              </>
            ) : (
              <div className="hidden md:flex items-center">
                <a href="/login" className="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium">Iniciar sesión</a>
              </div>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center">
            <button
              onClick={() => setMobileOpen(!mobileOpen)}
              aria-expanded={mobileOpen}
              aria-label="Abrir menú"
              className="inline-flex items-center justify-center p-2 rounded-md text-gray-700 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500"
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
        <div className="md:hidden bg-white border-t border-gray-100">
          <div className="px-4 pt-4 pb-3 space-y-2">
            <a href="/" className="block text-gray-700 px-3 py-2 rounded-md text-base font-medium hover:bg-gray-50">Validar</a>
            {user ? (
              <>
                <a href="/history" className="block text-gray-700 px-3 py-2 rounded-md text-base font-medium hover:bg-gray-50">Historial</a>
                {user.is_superuser && (
                  <a href="/admin/users" className="block text-gray-700 px-3 py-2 rounded-md text-base font-medium hover:bg-gray-50">Admin</a>
                )}
                <div className="pt-2 border-t border-gray-100">
                  <div className="text-sm text-gray-700">Bienvenido, <span className="font-medium">{user.username}</span></div>
                  <div className="mt-2">
                    <button onClick={logout} className="w-full text-left btn btn-secondary">Cerrar sesión</button>
                  </div>
                </div>
              </>
            ) : (
              <>
                <a href="/register" className="block text-gray-700 px-3 py-2 rounded-md text-base font-medium hover:bg-gray-50">Registro</a>
                <a href="/login" className="block text-gray-700 px-3 py-2 rounded-md text-base font-medium hover:bg-gray-50">Iniciar sesión</a>
              </>
            )}
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
