import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

const RegisterPage = () => {
  const { register, error, clearError } = useAuth();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({ username: '', email: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [successMsg, setSuccessMsg] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (error) clearError();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setSuccessMsg(null);
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
          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <label className="sr-only">Usuario</label>
              <input name="username" required className="relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none" placeholder="Usuario" value={formData.username} onChange={handleChange} />
            </div>
            <div>
              <label className="sr-only">Email</label>
              <input name="email" type="email" required className="relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none" placeholder="Correo electrónico" value={formData.email} onChange={handleChange} />
            </div>
            <div>
              <label className="sr-only">Contraseña</label>
              <input name="password" type="password" required className="relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none" placeholder="Contraseña" value={formData.password} onChange={handleChange} />
            </div>
          </div>

          {error && <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded">{error}</div>}

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
