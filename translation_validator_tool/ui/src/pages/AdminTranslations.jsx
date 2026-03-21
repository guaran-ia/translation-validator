import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { translationsAPI, validationsAPI } from '../services/api';
import { useAuth } from '../hooks/useAuth';
import TranslationCard from '../components/translation/TranslationCard';
import Navbar from '../components/common/Navbar';

// Simple helper to truncate long text in table cells
const truncate = (s, n = 80) => (s && s.length > n ? s.slice(0, n) + '…' : s);

const AdminTranslations = () => {
  const { user } = useAuth();
  const isAdmin = !!user && (user.is_superuser || user.role === 'admin');
  const navigate = useNavigate();
  const [idInput, setIdInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [translation, setTranslation] = useState(null);
  const [error, setError] = useState(null);
  const [validations, setValidations] = useState([]);

  const [items, setItems] = useState([]);
  const [skip, setSkip] = useState(0);
  const [limit, setLimit] = useState(20);
  const [total, setTotal] = useState(0);
  const [hasNext, setHasNext] = useState(false);
  const [query, setQuery] = useState('');
  const [tableLoading, setTableLoading] = useState(false);

  // Form states for creating new translations
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [createLoading, setCreateLoading] = useState(false);
  const [formData, setFormData] = useState({
    guarani_text: '',
    spanish_text: '',
    source: 'admin',
    direction: 'sp-gn', // Por defecto español->guaraní (español original)
    is_original: true
  });

  useEffect(() => {
    if (isAdmin) loadTable(0);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAdmin]);

  const loadTable = async (newSkip = 0) => {
    setTableLoading(true);
    try {
      const res = await translationsAPI.getAdminList(newSkip, limit, query);
      const data = res.data;
      setItems(data.items || []);
      setSkip(data.skip || newSkip);
      setTotal(data.total || 0);
      setHasNext(Boolean(data.has_next));
    } catch (e) {
      console.error('Failed to load admin translations', e);
    } finally {
      setTableLoading(false);
    }
  };

  const handleSearch = async () => {
    setError(null);
    setTranslation(null);
    setValidations([]);
    const id = parseInt(idInput, 10);
    if (!id) {
      setError('Ingresa un ID válido');
      return;
    }
    setLoading(true);
    try {
      const res = await translationsAPI.getById(id);
      const t = res?.data || res;
      setTranslation(t);

      // load validations for display
      try {
        const vres = await validationsAPI.getByTranslation(id);
        setValidations(vres?.data ? [vres.data] : []);
      } catch (e) {
        // validations endpoint may return 404 if user has not validated; ignore
        setValidations([]);
      }
    } catch (err) {
      console.error('Search failed', err);
      setError(err.response?.data?.detail || 'No se encontró la traducción');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTranslation = async (e) => {
    e.preventDefault();
    if (!formData.guarani_text.trim()) {
      setError('El texto en guaraní es obligatorio');
      return;
    }
    
    setCreateLoading(true);
    setError(null);
    
    try {
      // Prepare data, remove empty spanish_text to make it null
      const dataToSend = {
        ...formData,
        spanish_text: formData.spanish_text.trim() || null
      };
      
      const res = await translationsAPI.adminCreate(dataToSend);
      const newTranslation = res?.data || res;
      
      // Reset form and close modal
      setFormData({
        guarani_text: '',
        spanish_text: '',
        source: 'admin',
        direction: 'sp-gn',
        is_original: true
      });
      setShowCreateForm(false);
      
      // Reload table to show new translation
      loadTable(0);
      
      // Show success message
      alert(`Traducción creada exitosamente con ID: ${newTranslation.id}`);
      
    } catch (err) {
      console.error('Create failed', err);
      setError(err.response?.data?.detail || 'Error al crear la traducción');
    } finally {
      setCreateLoading(false);
    }
  };

  if (!isAdmin) return (
    <div>
      <Navbar />
      <div className="p-6">No autorizado</div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">Administración de traducciones</h1>
            <p className="text-sm text-gray-600">Busca, filtra y explora todas las traducciones con sus estadísticas.</p>
          </div>
          <button
            onClick={() => setShowCreateForm(true)}
            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-medium"
          >
            + Agregar Traducción
          </button>
        </div>

        <div className="bg-white p-4 rounded-lg shadow-sm mb-6">
          <div className="flex gap-3 items-center">
            <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Buscar por ID o texto..." className="flex-1 border rounded px-3 py-2" />
            <button onClick={() => loadTable(0)} className="btn btn-primary">Buscar</button>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">ID</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Dirección</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Texto (truncado)</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Categoría</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Validaciones</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Sugerencias</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Acciones</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {tableLoading ? (
                  <tr><td colSpan={7} className="px-4 py-6 text-center">Cargando...</td></tr>
                ) : items.length === 0 ? (
                  <tr><td colSpan={7} className="px-4 py-6 text-center">No hay traducciones.</td></tr>
                ) : (
                items.map(t => (
                  <tr key={t.id}>
                    <td className="px-4 py-3 text-sm text-gray-700">{t.id}</td>
                    <td className="px-4 py-3 text-sm text-gray-700">{t.direction}</td>
                    <td className="px-4 py-3 text-sm text-gray-700">{truncate(t.guarani_text || t.spanish_text)}</td>
                    <td className="px-4 py-3 text-sm text-gray-700">{t.validation_count}</td>
                    <td className="px-4 py-3 text-sm text-gray-700">{t.suggestion_count}</td>
                    <td className="px-4 py-3 text-sm text-gray-700">
                      <div className="flex gap-2">
                        <button onClick={async () => {
                          try {
                            const res = await translationsAPI.getById(t.id);
                            setTranslation(res.data || res);
                            // load validations for this translation for admin inspector
                            try {
                              const vres = await validationsAPI.getByTranslation(t.id);
                              setValidations(vres?.data ? [vres.data] : []);
                            } catch (e) {
                              setValidations([]);
                            }
                          } catch (e) {
                            console.error('Failed to load translation', e);
                          }
                        }} className="text-sm text-indigo-600 hover:underline">Ver</button>
                        <button onClick={() => navigate(`/validator?translation=${t.id}`)} className="text-sm text-green-600 hover:underline font-medium">Validar</button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination controls */}
        <div className="mt-4 flex items-center justify-between">
          <div className="text-sm text-gray-600">Mostrando {skip + 1}–{Math.min(skip + limit, total)} de {total}</div>
          <div className="flex gap-2">
            <button onClick={() => loadTable(Math.max(0, skip - limit))} disabled={skip === 0} className="px-3 py-1 border rounded disabled:opacity-50">Anterior</button>
            <button onClick={() => loadTable(skip + limit)} disabled={!hasNext} className="px-3 py-1 border rounded disabled:opacity-50">Siguiente</button>
          </div>
        </div>

        {/* Inspector: show translation card if selected */}
        {translation && (
          <div className="mt-8 bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-3">Inspección de traducción</h3>
            <TranslationCard translation={translation} />

            <div className="mt-6">
              <h4 className="text-md font-medium mb-2">Validaciones</h4>
              {validations.length === 0 ? (
                <div className="text-sm text-gray-600">No hay validaciones para esta traducción.</div>
              ) : (
                <div className="space-y-3">
                  {validations.map(v => (
                    <div key={v.id} className="border rounded p-3">
                      <div className="text-sm">ID: {v.id} • Correctness: {v.correctness}</div>
                      <div className="text-xs text-gray-600">Fluidez: {v.fluency_score} • Precisión: {v.accuracy_score}</div>
                      <div className="text-xs text-gray-500 mt-1">Notas: {v.notes || '—'}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Create Translation Modal */}
        {showCreateForm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Agregar Nueva Traducción</h3>
                <button
                  onClick={() => {
                    setShowCreateForm(false);
                    setError(null);
                  }}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>

              {error && (
                <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
                  {error}
                </div>
              )}

              <form onSubmit={handleCreateTranslation} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Texto en Guaraní *
                  </label>
                  <textarea
                    value={formData.guarani_text}
                    onChange={(e) => setFormData({...formData, guarani_text: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows={3}
                    required
                    placeholder="Ingresa el texto original en guaraní..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Texto en Español (opcional)
                  </label>
                  <textarea
                    value={formData.spanish_text}
                    onChange={(e) => setFormData({...formData, spanish_text: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows={3}
                    placeholder="Si no tiene traducción, dejar en blanco para que sea sugerida..."
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Si se deja vacío, los usuarios podrán sugerir traducciones para esta oración. 
                    {!formData.spanish_text.trim() && formData.guarani_text.trim() && 
                      " Se creará solo una entrada (gn-sp) hasta que se agregue la primera traducción."
                    }
                  </p>
                </div>



                {/* Dirección de traducción - solo si ambos textos están presentes */}
                {formData.guarani_text.trim() && formData.spanish_text.trim() && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Dirección de traducción
                    </label>
                    <div className="space-y-2">
                      <div className="flex items-center">
                        <input
                          type="radio"
                          id="direction_sp_gn"
                          name="direction"
                          value="sp-gn"
                          checked={formData.direction === 'sp-gn'}
                          onChange={(e) => setFormData({...formData, direction: e.target.value})}
                          className="mr-2"
                        />
                        <label htmlFor="direction_sp_gn" className="text-sm">
                          <span className="font-medium">Español → Guaraní</span> (español es el original)
                        </label>
                      </div>
                      <div className="flex items-center">
                        <input
                          type="radio"
                          id="direction_gn_sp"
                          name="direction"
                          value="gn-sp"
                          checked={formData.direction === 'gn-sp'}
                          onChange={(e) => setFormData({...formData, direction: e.target.value})}
                          className="mr-2"
                        />
                        <label htmlFor="direction_gn_sp" className="text-sm">
                          <span className="font-medium">Guaraní → Español</span> (guaraní es el original)
                        </label>
                      </div>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      Se crearán automáticamente ambas direcciones en la base de datos
                    </p>
                  </div>
                )}

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Fuente
                  </label>
                  <input
                    type="text"
                    value={formData.source}
                    onChange={(e) => setFormData({...formData, source: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Fuente del texto (ej: admin, corpus, etc.)"
                  />
                </div>

                <div className="flex items-center justify-end gap-3 pt-4 border-t">
                  <button
                    type="button"
                    onClick={() => {
                      setShowCreateForm(false);
                      setError(null);
                      setFormData({
                        guarani_text: '',
                        spanish_text: '',
                        source: 'admin',
                        direction: 'sp-gn',
                        is_original: true
                      });
                    }}
                    className="px-4 py-2 text-gray-600 border border-gray-300 rounded hover:bg-gray-50"
                    disabled={createLoading}
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
                    disabled={createLoading}
                  >
                    {createLoading ? 'Creando...' : 'Crear Traducción'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminTranslations;