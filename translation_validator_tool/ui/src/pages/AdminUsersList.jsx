import { useEffect, useState } from 'react';
import { authAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import Navbar from '../components/common/Navbar';
import { toast } from 'react-toastify';

const AdminUsersList = () => {
  const { user } = useAuth();
  const isAdmin = !!user && (user.is_superuser || user.role === 'admin');
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('list');
  const [editUser, setEditUser] = useState(null);
  const [deleteUser, setDeleteUser] = useState(null);
  const [changePasswordUser, setChangePasswordUser] = useState(null);
  const [newPassword, setNewPassword] = useState('');
  const [editForm, setEditForm] = useState({ username: '', email: '', role: 'validador', is_active: true });
  const [createForm, setCreateForm] = useState({ username: '', email: '', password: '', role: 'validador' });
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    if (!isAdmin) return;
    loadUsers();
  }, [isAdmin]);

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
      role: u.role || (u.is_superuser ? 'admin' : 'validador'),
      is_active: u.is_active,
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

  const handleCreateUser = async (e) => {
    e.preventDefault();
    if (!createForm.username.trim() || !createForm.email.trim() || !createForm.password.trim()) {
      toast.error('Completa usuario, email y contraseña');
      return;
    }

    setCreating(true);
    try {
      const registerRes = await authAPI.register({
        username: createForm.username.trim(),
        email: createForm.email.trim(),
        password: createForm.password,
      });

      const createdUser = registerRes.data;
      await authAPI.approveUser(createdUser.id);
      await authAPI.updateUser(createdUser.id, { role: createForm.role });

      toast.success('Usuario creado y activado correctamente');
      setCreateForm({ username: '', email: '', password: '', role: 'validador' });
      setActiveTab('list');
      loadUsers();
    } catch (e) {
      console.error('Create user failed', e);
      toast.error(e.response?.data?.detail || 'Error al crear usuario');
    } finally {
      setCreating(false);
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
      <div className="max-w-6xl mx-auto p-6">
        <h2 className="text-2xl font-semibold mb-4">Gestión de Usuarios</h2>
        <div className="mb-4 border-b">
          <div className="flex gap-2">
            <button
              className={`px-4 py-2 text-sm font-medium border-b-2 ${activeTab === 'list' ? 'border-blue-600 text-blue-700' : 'border-transparent text-gray-600 hover:text-gray-900'}`}
              onClick={() => setActiveTab('list')}
            >
              Listado y edición
            </button>
            <button
              className={`px-4 py-2 text-sm font-medium border-b-2 ${activeTab === 'create' ? 'border-blue-600 text-blue-700' : 'border-transparent text-gray-600 hover:text-gray-900'}`}
              onClick={() => setActiveTab('create')}
            >
              Crear usuario
            </button>
          </div>
        </div>

        {activeTab === 'list' && (
          loading ? (
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
                    <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Rol</th>
                    <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Activo</th>
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
                        <span className="capitalize">{u.role || (u.is_superuser ? 'admin' : 'validador')}</span>
                      </td>
                      <td className="px-4 py-2 text-sm">
                        {u.is_active ? (
                          <span className="text-green-600 font-medium">Sí</span>
                        ) : (
                          <span className="text-red-600 font-medium">No</span>
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
          )
        )}

        {activeTab === 'create' && (
          <div className="bg-white border rounded-lg p-4 md:p-6 max-w-2xl">
            <h3 className="text-lg font-semibold mb-4">Crear usuario</h3>
            <form className="space-y-4" onSubmit={handleCreateUser}>
              <div>
                <label className="block text-sm font-medium mb-1">Usuario</label>
                <input
                  type="text"
                  value={createForm.username}
                  onChange={(e) => setCreateForm({ ...createForm, username: e.target.value })}
                  className="w-full border rounded px-3 py-2"
                  placeholder="usuario"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Email</label>
                <input
                  type="email"
                  value={createForm.email}
                  onChange={(e) => setCreateForm({ ...createForm, email: e.target.value })}
                  className="w-full border rounded px-3 py-2"
                  placeholder="usuario@dominio.com"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Contraseña</label>
                <input
                  type="password"
                  value={createForm.password}
                  onChange={(e) => setCreateForm({ ...createForm, password: e.target.value })}
                  className="w-full border rounded px-3 py-2"
                  placeholder="Contraseña inicial"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Rol</label>
                <select
                  value={createForm.role}
                  onChange={(e) => setCreateForm({ ...createForm, role: e.target.value })}
                  className="w-full border rounded px-3 py-2 bg-white"
                >
                  <option value="validador">Validador</option>
                  <option value="traductor">Traductor</option>
                  <option value="admin">Admin</option>
                </select>
              </div>
              <div className="flex justify-end">
                <button
                  type="submit"
                  disabled={creating}
                  className="px-4 py-2 rounded-md bg-blue-600 text-white disabled:opacity-60"
                >
                  {creating ? 'Creando...' : 'Crear usuario'}
                </button>
              </div>
            </form>
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
                  <div>
                    <label className="block text-sm font-medium mb-1">Rol</label>
                    <select
                      value={editForm.role}
                      onChange={(e) => setEditForm({ ...editForm, role: e.target.value })}
                      className="border rounded px-3 py-2 bg-white"
                    >
                      <option value="validador">Validador</option>
                      <option value="traductor">Traductor</option>
                      <option value="admin">Admin</option>
                    </select>
                  </div>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={editForm.is_active}
                      onChange={(e) => setEditForm({ ...editForm, is_active: e.target.checked })}
                      className="mr-2"
                    />
                    <span className="text-sm">Activo</span>
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
