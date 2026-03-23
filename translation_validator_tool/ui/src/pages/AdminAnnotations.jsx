import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { annotationsAPI } from '../services/api';
import Navbar from '../components/common/Navbar';

const AdminAnnotations = () => {
  const { user } = useAuth();
  const isAdmin = !!user && (user.is_superuser || user.role === 'admin');
  const navigate = useNavigate();
  const [idInput, setIdInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [annotation, setAnnotation] = useState(null);
  const [error, setError] = useState(null);

  const [items, setItems] = useState([]);
  const [skip, setSkip] = useState(0);
  const [limit, setLimit] = useState(20);
  const [total, setTotal] = useState(0);
  const [hasNext, setHasNext] = useState(false);
  const [query, setQuery] = useState('');
  const [tableLoading, setTableLoading] = useState(false);

  // Form states for creating new annotations
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [createLoading, setCreateLoading] = useState(false);
  const [formData, setFormData] = useState({
    question_es: '',
    question_gn: '',
    answer_es: '',
    answer_gn: '',
    answer_number: '',
    equation_solution: '',
    source: 'GuaranIA'
  });

  useEffect(() => {
    if (isAdmin) loadTable(0);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAdmin]);

  const loadTable = async (newSkip = 0) => {
    setTableLoading(true);
    try {
      const res = await annotationsAPI.getAll(newSkip, limit, query);
      const data = res?.data || res;
      setItems(data.items || []);
      setSkip(newSkip);
      setTotal(data.total || 0);
      setHasNext(data.has_next || false);
    } catch (e) {
      console.error('Failed to load admin annotations', e);
      setError('No se pudieron cargar las anotaciones');
    } finally {
      setTableLoading(false);
    }
  };

  const handleSearch = async () => {
    setError(null);
    setAnnotation(null);
    const id = parseInt(idInput, 10);
    if (!id) {
      setError('Ingresa un ID válido');
      return;
    }
    setLoading(true);
    try {
      const res = await annotationsAPI.getById(id);
      setAnnotation(res?.data || res);
    } catch (err) {
      console.error('Search failed', err);
      setError(err.response?.data?.detail || 'No se encontró la anotación');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAnnotation = async (e) => {
    e.preventDefault();
    if (!formData.question_es.trim()) {
      setError('La pregunta en español es obligatoria');
      return;
    }
    if (!formData.answer_es.trim()) {
      setError('La respuesta en español es obligatoria');
      return;
    }
    
    setCreateLoading(true);
    setError(null);
    
    try {
      // Preparar datos
      const dataToSend = {
        question_es: formData.question_es.trim(),
        question_gn: formData.question_gn.trim() || null,
        answer_es: formData.answer_es.trim(),
        answer_gn: formData.answer_gn.trim() || null,
        answer_number: formData.answer_number ? parseInt(formData.answer_number) : null,
        equation_solution: formData.equation_solution.trim() || null,
        source: 'GuaranIA'
      };
      
      const res = await annotationsAPI.create(dataToSend);
      const newAnnotation = res?.data || res;
      
      // Resetear formulario y cerrar modal
      setFormData({
        question_es: '',
        question_gn: '',
        answer_es: '',
        answer_gn: '',
        answer_number: '',
        equation_solution: '',
        source: 'GuaranIA'
      });
      setShowCreateForm(false);
      
      // Recargar tabla
      loadTable(0);
      
      // Mostrar mensaje de éxito
      alert(`Anotación creada exitosamente con ID: ${newAnnotation.id}`);
      
    } catch (err) {
      console.error('Create failed', err);
      setError(err.response?.data?.detail || 'Error al crear la anotación');
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
            <h1 className="text-2xl font-bold">Administración de Anotaciones</h1>
            <p className="text-sm text-gray-600">Crea, edita y explora anotaciones (preguntas y respuestas) para traducción.</p>
          </div>
          <button
            onClick={() => setShowCreateForm(true)}
            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-medium"
          >
            + Agregar Anotación
          </button>
        </div>

        {/* Búsqueda por ID */}
        <div className="bg-white p-4 rounded-lg shadow-sm mb-6">
          <h3 className="text-sm font-semibold mb-3">Buscar por ID</h3>
          <div className="flex gap-3 items-center">
            <input 
              value={idInput} 
              onChange={(e) => setIdInput(e.target.value)} 
              placeholder="Ingresa ID de anotación..." 
              className="flex-1 border rounded px-3 py-2 text-sm" 
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
            <button 
              onClick={handleSearch} 
              disabled={loading}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded text-sm font-medium disabled:opacity-50"
            >
              {loading ? 'Buscando...' : 'Ver'}
            </button>
          </div>
          {error && (
            <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
              {error}
            </div>
          )}
        </div>

        {/* Detalle de anotación */}
        {annotation && (
          <div className="bg-white p-6 rounded-lg shadow-sm mb-6 border-l-4 border-blue-600">
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-lg font-semibold">Detalles de Anotación #{annotation.id}</h3>
              <button 
                onClick={() => setAnnotation(null)} 
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-xs font-medium text-gray-500">Pregunta (Español)</label>
                <p className="text-sm text-gray-700 mt-1 p-2 bg-gray-50 rounded">{annotation.question_es}</p>
              </div>
              <div>
                <label className="text-xs font-medium text-gray-500">Pregunta (Guaraní)</label>
                <p className="text-sm text-gray-700 mt-1 p-2 bg-gray-50 rounded">{annotation.question_gn || '(No traducida)'}</p>
              </div>
              <div>
                <label className="text-xs font-medium text-gray-500">Respuesta (Español)</label>
                <p className="text-sm text-gray-700 mt-1 p-2 bg-gray-50 rounded">{annotation.answer_es}</p>
              </div>
              <div>
                <label className="text-xs font-medium text-gray-500">Respuesta (Guaraní)</label>
                <p className="text-sm text-gray-700 mt-1 p-2 bg-gray-50 rounded">{annotation.answer_gn || '(No traducida)'}</p>
              </div>
              {annotation.answer_number && (
                <div>
                  <label className="text-xs font-medium text-gray-500">Número de Respuesta</label>
                  <p className="text-sm text-gray-700 mt-1 p-2 bg-gray-50 rounded">{annotation.answer_number}</p>
                </div>
              )}
              {annotation.equation_solution && (
                <div>
                  <label className="text-xs font-medium text-gray-500">Ecuación/Solución</label>
                  <p className="text-sm text-gray-700 mt-1 p-2 bg-gray-50 rounded">{annotation.equation_solution}</p>
                </div>
              )}
            </div>
            <div className="mt-4 text-xs text-gray-500">
              <p>Creada: {new Date(annotation.created_at).toLocaleString('es-ES')}</p>
            </div>
          </div>
        )}

        {/* Búsqueda por texto */}
        <div className="bg-white p-4 rounded-lg shadow-sm mb-6">
          <h3 className="text-sm font-semibold mb-3">Buscar por texto</h3>
          <div className="flex gap-3 items-center">
            <input 
              value={query} 
              onChange={(e) => setQuery(e.target.value)} 
              placeholder="Buscar en preguntas y respuestas..." 
              className="flex-1 border rounded px-3 py-2 text-sm" 
              onKeyPress={(e) => e.key === 'Enter' && loadTable(0)}
            />
            <button onClick={() => loadTable(0)} className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded text-sm font-medium">Buscar</button>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">ID</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Pregunta</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Respuesta</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Nº Respuesta</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Acciones</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {tableLoading ? (
                  <tr><td colSpan={5} className="px-4 py-6 text-center">Cargando...</td></tr>
                ) : items.length === 0 ? (
                  <tr><td colSpan={5} className="px-4 py-6 text-center">No hay anotaciones.</td></tr>
                ) : (
                items.map(a => (
                  <tr key={a.id}>
                    <td className="px-4 py-3 text-sm text-gray-700">{a.id}</td>
                    <td className="px-4 py-3 text-sm text-gray-700">{a.question_es.substring(0, 60)}...</td>
                    <td className="px-4 py-3 text-sm text-gray-700">{a.answer_es.substring(0, 60)}...</td>
                    <td className="px-4 py-3 text-sm text-gray-700">{a.answer_number || '-'}</td>
                    <td className="px-4 py-3 text-sm text-gray-700">
                      <div className="flex gap-2">
                        <button 
                          onClick={() => setAnnotation(a)}
                          className="text-sm text-indigo-600 hover:underline font-medium"
                        >
                          Ver
                        </button>
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

        {/* Create Annotation Modal */}
        {showCreateForm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Agregar Nueva Anotación</h3>
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

              <form onSubmit={handleCreateAnnotation} className="space-y-4">
                {/* PREGUNTA EN ESPAÑOL */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Pregunta en Español *
                  </label>
                  <textarea
                    value={formData.question_es}
                    onChange={(e) => setFormData({...formData, question_es: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows={4}
                    required
                    placeholder="Ingresa la pregunta en español..."
                  />
                </div>

                {/* PREGUNTA EN GUARANÍ */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Pregunta en Guaraní (opcional)
                  </label>
                  <textarea
                    value={formData.question_gn}
                    onChange={(e) => setFormData({...formData, question_gn: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows={4}
                    placeholder="Traducción sugerida de la pregunta al guaraní..."
                  />
                </div>

                {/* RESPUESTA EN ESPAÑOL */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Respuesta en Español *
                  </label>
                  <textarea
                    value={formData.answer_es}
                    onChange={(e) => setFormData({...formData, answer_es: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows={4}
                    required
                    placeholder="Ingresa la respuesta en español..."
                  />
                </div>

                {/* RESPUESTA EN GUARANÍ */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Respuesta en Guaraní (opcional)
                  </label>
                  <textarea
                    value={formData.answer_gn}
                    onChange={(e) => setFormData({...formData, answer_gn: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows={4}
                    placeholder="Traducción sugerida de la respuesta al guaraní..."
                  />
                </div>

                {/* METADATA - Dos columnas */}
                <div className="grid grid-cols-2 gap-4">
                  {/* ANSWER NUMBER */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Número de Respuesta (opcional)
                    </label>
                    <input
                      type="number"
                      value={formData.answer_number}
                      onChange={(e) => setFormData({...formData, answer_number: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Ej: 11"
                    />
                  </div>

                  {/* EQUATION SOLUTION */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Ecuación/Solución (opcional)
                    </label>
                    <input
                      type="text"
                      value={formData.equation_solution}
                      onChange={(e) => setFormData({...formData, equation_solution: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Ej: 5 + 6 = 11"
                    />
                  </div>
                </div>

                {/* BUTTONS */}
                <div className="flex items-center justify-end gap-3 pt-4 border-t">
                  <button
                    type="button"
                    onClick={() => {
                      setShowCreateForm(false);
                      setError(null);
                      setFormData({
                        question_es: '',
                        question_gn: '',
                        answer_es: '',
                        answer_gn: '',
                        answer_number: '',
                        equation_solution: '',
                        source: 'GuaranIA'
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
                    {createLoading ? 'Creando...' : 'Crear Anotación'}
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

export default AdminAnnotations;
