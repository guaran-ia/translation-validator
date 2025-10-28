import { useEffect, useState } from 'react';
import { authAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';

const AdminUsers = () => {
  const { user } = useAuth();
  const [pending, setPending] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user || !user.is_superuser) return;
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
  }, [user]);

  const handleApprove = async (id) => {
    // Confirmation modal
    const ok = window.confirm('¿Aprobar este usuario? Esta acción activará la cuenta.');
    if (!ok) return;

    try {
      await authAPI.approveUser(id);
      setPending(prev => prev.filter(p => p.id !== id));
      alert('Usuario aprobado');
    } catch (e) {
      console.error('Approve failed', e);
      alert('No se pudo aprobar el usuario');
    }
  };

  if (!user || !user.is_superuser) {
    return <div className="p-6">No autorizado</div>;
  }

  return (
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
                <button onClick={() => handleApprove(u.id)} className="btn btn-primary">Aprobar</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default AdminUsers;
