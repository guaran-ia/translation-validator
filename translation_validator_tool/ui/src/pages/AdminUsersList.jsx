import { useEffect, useState } from 'react';
import { authAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import Navbar from '../components/common/Navbar';
import { toast } from 'react-toastify';

const AdminUsersList = () => {
  const { user } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editUser, setEditUser] = useState(null);
  const [deleteUser, setDeleteUser] = useState(null);
  const [changePasswordUser, setChangePasswordUser] = useState(null);
  const [newPassword, setNewPassword] = useState('');
  const [editForm, setEditForm] = useState({ username: '', email: '', is_active: true, is_superuser: false });

  useEffect(() => {
    if (!user || !user.is_superuser) return;
    loadUsers();
  }, [user]);

  const loadUsers = async () => {
    setLoading(true);
    try {
      const res = await authAPI.getAllUsers();
      setUsers(res.data || []);
    } catch (e) {
      console.error('Failed to load users', e);
      toast.error('Error al cargar usuarios');
    } finally {
      setLoading(false);
    }
  };

  const handleEditClick = (u) => {
    setEditUser(u);
    setEditForm({
      username: u.username,
      email: u.email,
      is_active: u.is_active,
      is_superuser: u.is_superuser,
    });
  };

  const handleEditSave = async () => {
    if (!editUser) return;
    try {
      await authAPI.updateUser(editUser.id, editForm);
      toast.success('Usuario actualizado');
      setEditUser(null);
      loadUsers();
    } catch (e) {
      console.error('Update failed', e);
      toast.error('Error al actualizar usuario');
    }
  };

  const handleDeleteClick = (u) => {
    setDeleteUser(u);
  };

  const handleDeleteConfirm = async () => {
    if (!deleteUser) return;
    try {
      await authAPI.deleteUser(deleteUser.id);
      toast.success('Usuario eliminado');
      setDeleteUser(null);
      loadUsers();
    } catch (e) {
      console.error('Delete failed', e);
      toast.error(e.response?.data?.detail || 'Error al eliminar usuario');
    }
  };

  const handleChangePasswordClick = (u) => {
    setChangePasswordUser(u);
    setNewPassword('');
  };

  const handleChangePasswordSave = async () => {
    if (!changePasswordUser || !newPassword.trim()) {
      toast.error('Ingrese una contraseña válida');
      return;
    }
    try {
      await authAPI.changeUserPassword(changePasswordUser.id, newPassword);
      toast.success('Contraseña actualizada');
      setChangePasswordUser(null);
      setNewPassword('');
    } catch (e) {
      console.error('Change password failed', e);
      toast.error('Error al cambiar contraseña');
    }
  };

  if (!user || !user.is_superuser) {
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
      <div className="max-w-6xl mx-auto p-6">
        <h2 className="text-2xl font-semibold mb-4">Gestión de Usuarios</h2>
        {loading ? (
          <div>Cargando...</div>
        ) : users.length === 0 ? (
          <div>No hay usuarios registrados.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full bg-white border rounded-lg">
              <thead className="bg-gray-100">
                <tr>
                  <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">ID</th>
                  <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Usuario</th>
                  <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Email</th>
                  <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Activo</th>
                  <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Admin</th>
                  <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Creado</th>
                  <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id} className="border-t hover:bg-gray-50">
                    <td className="px-4 py-2 text-sm">{u.id}</td>
                    <td className="px-4 py-2 text-sm font-medium">{u.username}</td>
                    <td className="px-4 py-2 text-sm">{u.email}</td>
                    <td className="px-4 py-2 text-sm">
                      {u.is_active ? (
                        <span className="text-green-600 font-medium">Sí</span>
                      ) : (
                        <span className="text-red-600 font-medium">No</span>
                      )}
                    </td>
                    <td className="px-4 py-2 text-sm">
                      {u.is_superuser ? (
                        <span className="text-blue-600 font-medium">Sí</span>
                      ) : (
                        <span className="text-gray-500">No</span>
                      )}
                    </td>
                    <td className="px-4 py-2 text-sm text-gray-600">
                      {new Date(u.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-2 text-sm space-x-2">
                      <button
                        onClick={() => handleEditClick(u)}
                        className="text-blue-600 hover:text-blue-800"
                      >
                        Editar
                      </button>
                      <button
                        onClick={() => handleChangePasswordClick(u)}
                        className="text-purple-600 hover:text-purple-800"
                      >
                        Contraseña
                      </button>
                      {user.id !== u.id && (
                        <button
                          onClick={() => handleDeleteClick(u)}
                          className="text-red-600 hover:text-red-800"
                        >
                          Eliminar
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Edit Modal */}
        {editUser && (
          <div className="fixed inset-0 z-50 flex items-center justify-center">
            <div className="absolute inset-0 bg-black opacity-40" onClick={() => setEditUser(null)} />
            <div className="bg-white rounded-lg shadow-lg max-w-lg w-full mx-4 z-10 p-6">
              <h3 className="text-lg font-semibold mb-4">Editar Usuario</h3>
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium mb-1">Usuario</label>
                  <input
                    type="text"
                    value={editForm.username}
                    onChange={(e) => setEditForm({ ...editForm, username: e.target.value })}
                    className="w-full border rounded px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Email</label>
                  <input
                    type="email"
                    value={editForm.email}
                    onChange={(e) => setEditForm({ ...editForm, email: e.target.value })}
                    className="w-full border rounded px-3 py-2"
                  />
                </div>
                <div className="flex items-center space-x-4">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={editForm.is_active}
                      onChange={(e) => setEditForm({ ...editForm, is_active: e.target.checked })}
                      className="mr-2"
                    />
                    <span className="text-sm">Activo</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={editForm.is_superuser}
                      onChange={(e) => setEditForm({ ...editForm, is_superuser: e.target.checked })}
                      className="mr-2"
                    />
                    <span className="text-sm">Administrador</span>
                  </label>
                </div>
              </div>
              <div className="flex justify-end space-x-3 mt-6">
                <button onClick={() => setEditUser(null)} className="px-4 py-2 rounded-md border">
                  Cancelar
                </button>
                <button onClick={handleEditSave} className="px-4 py-2 rounded-md bg-blue-600 text-white">
                  Guardar
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Delete Confirmation Modal */}
        {deleteUser && (
          <div className="fixed inset-0 z-50 flex items-center justify-center">
            <div className="absolute inset-0 bg-black opacity-40" onClick={() => setDeleteUser(null)} />
            <div className="bg-white rounded-lg shadow-lg max-w-lg w-full mx-4 z-10 p-6">
              <h3 className="text-lg font-semibold mb-2">Confirmar Eliminación</h3>
              <p className="text-sm text-gray-700 mb-4">
                ¿Estás seguro de que deseas eliminar al usuario{' '}
                <span className="font-medium">{deleteUser.username}</span>? Esta acción no se puede deshacer.
              </p>
              <div className="flex justify-end space-x-3">
                <button onClick={() => setDeleteUser(null)} className="px-4 py-2 rounded-md border">
                  Cancelar
                </button>
                <button onClick={handleDeleteConfirm} className="px-4 py-2 rounded-md bg-red-600 text-white">
                  Eliminar
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Change Password Modal */}
        {changePasswordUser && (
          <div className="fixed inset-0 z-50 flex items-center justify-center">
            <div
              className="absolute inset-0 bg-black opacity-40"
              onClick={() => setChangePasswordUser(null)}
            />
            <div className="bg-white rounded-lg shadow-lg max-w-lg w-full mx-4 z-10 p-6">
              <h3 className="text-lg font-semibold mb-4">
                Cambiar Contraseña de {changePasswordUser.username}
              </h3>
              <div>
                <label className="block text-sm font-medium mb-1">Nueva Contraseña</label>
                <input
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  className="w-full border rounded px-3 py-2"
                  placeholder="Ingrese nueva contraseña"
                />
              </div>
              <div className="flex justify-end space-x-3 mt-6">
                <button
                  onClick={() => setChangePasswordUser(null)}
                  className="px-4 py-2 rounded-md border"
                >
                  Cancelar
                </button>
                <button
                  onClick={handleChangePasswordSave}
                  className="px-4 py-2 rounded-md bg-purple-600 text-white"
                >
                  Cambiar Contraseña
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminUsersList;
