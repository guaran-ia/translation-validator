import { useAuth } from '../../hooks/useAuth';

const Navbar = () => {
  const { user, logout } = useAuth();

  return (
    <nav className="bg-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo and title */}
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <h1 className="text-xl font-bold text-gray-900">
                Translation Validator
              </h1>
            </div>
            <div className="ml-4 text-sm text-gray-600">
              Guaraní ↔ Español
            </div>
          </div>

          {/* Navigation Links */}
          {user && (
            <div className="flex items-center space-x-6">
              <a 
                href="/" 
                className="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium"
              >
                Validar
              </a>
              <a 
                href="/history" 
                className="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium"
              >
                Historial
              </a>
            </div>
          )}

          {/* User info and logout */}
          <div className="flex items-center space-x-4">
            {user && (
              <>
                <div className="text-sm text-gray-700">
                  Bienvenido, <span className="font-medium">{user.username}</span>
                </div>
                <button
                  onClick={logout}
                  className="btn btn-secondary"
                >
                  Cerrar sesión
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;