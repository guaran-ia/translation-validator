import { useEffect, useState } from 'react';
import { authAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import Navbar from '../components/common/Navbar';
import { toast } from 'react-toastify';

const AdminUsers = () => {
  const { user } = useAuth();
  const isAdmin = !!user && (user.is_superuser || user.role === 'admin');
  const [pending, setPending] = useState([]);
  const [loading, setLoading] = useState(true);
  const [confirmUser, setConfirmUser] = useState(null);

  useEffect(() => {
    if (!isAdmin) return;
    const load = async () => {
      setLoading(true);
      try {
        const res = await authAPI.getPendingRegistrations();
        setPending(res.data || []);
      } catch (e) {
        console.error('Failed to load pending users', e);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [isAdmin]);

  const handleApproveClick = (id) => {
    const u = pending.find(p => p.id === id);
    if (!u) return;
    setConfirmUser(u);
  };

  const handleCancelConfirm = () => setConfirmUser(null);

  const handleConfirmApprove = async () => {
    if (!confirmUser) return;
    try {
      await authAPI.approveUser(confirmUser.id);
      setPending(prev => prev.filter(p => p.id !== confirmUser.id));
      setConfirmUser(null);
    } catch (e) {
      console.error('Approve failed', e);
      toast.error('No se pudo aprobar el usuario');
    }
  };

  if (!isAdmin) {
    return (
      <div>
        <Navbar />
        <div className="p-6">No autorizado</div>
      </div>
    );
  }

  return (
    <div>
      <Navbar />
      <div className="max-w-4xl mx-auto p-6">
      <h2 className="text-xl font-semibold mb-4">Registros pendientes</h2>
          {loading ? (
        <div>Loading...</div>
      ) : pending.length === 0 ? (
        <div>No hay registros pendientes.</div>
      ) : (
        <div className="space-y-3">
          {pending.map(u => (
            <div key={u.id} className="flex items-center justify-between border rounded p-3">
              <div>
                <div className="font-medium">{u.username}</div>
                <div className="text-sm text-gray-600">{u.email}</div>
                <div className="text-xs text-gray-500">Creado: {new Date(u.created_at).toLocaleString()}</div>
              </div>
              <div>
                    <button onClick={() => handleApproveClick(u.id)} className="btn btn-primary">Aprobar</button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Confirm modal */}
      {confirmUser && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="absolute inset-0 bg-black opacity-40" onClick={handleCancelConfirm} />
          <div className="bg-white rounded-lg shadow-lg max-w-lg w-full mx-4 z-10">
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-2">Confirmar aprobación</h3>
              <p className="text-sm text-gray-700 mb-4">¿Aprobar al usuario <span className="font-medium">{confirmUser.username}</span>? Esta acción activará la cuenta y notificará al usuario.</p>
              <div className="flex justify-end space-x-3">
                <button onClick={handleCancelConfirm} className="px-4 py-2 rounded-md border">Cancelar</button>
                <button onClick={handleConfirmApprove} className="px-4 py-2 rounded-md bg-blue-600 text-white">Aprobar usuario</button>
              </div>
            </div>
          </div>
        </div>
      )}
      </div>
    </div>
  );
};

export default AdminUsers;
