import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { annotationsAPI, authAPI } from '../services/api';
import api from '../services/api';
import { toast } from 'react-toastify';
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

  // States for Excel upload
  const [showExcelUpload, setShowExcelUpload] = useState(false);
  const [excelFile, setExcelFile] = useState(null);
  const [excelSheets, setExcelSheets] = useState([]);
  const [selectedSheet, setSelectedSheet] = useState('');
  const [excelLoading, setExcelLoading] = useState(false);
  const [excelResult, setExcelResult] = useState(null);

  // States for assignment
  const [translators, setTranslators] = useState([]);
  const [selectedTranslator, setSelectedTranslator] = useState(null);
  const [assignLoading, setAssignLoading] = useState(false);

  useEffect(() => {
    if (isAdmin) {
      loadTable(0);
      loadTranslators();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAdmin]);

  const loadTranslators = async () => {
    try {
      const res = await authAPI.getAllUsers();
      const allUsers = res?.data || res;
      const translators = allUsers.filter(u => u.role === 'traductor');
      setTranslators(translators);
    } catch (err) {
      console.error('Failed to load translators', err);
    }
  };

  const loadTable = async (newSkip = 0) => {
    setTableLoading(true);
    try {
      const res = await annotationsAPI.getAll(newSkip, limit, query);
      const data = res?.data || res;
      
      // Enriquecer cada anotación con información de asignaciones y traducciones
      const enrichedItems = await Promise.all(
        (data.items || []).map(async (item) => {
          try {
            // Obtener asignaciones
            const assignRes = await api.get(`/annotations/${item.id}/assignments`);
            const assignments = assignRes?.data || [];

            // Obtener traducciones (normalizar distintas formas de respuesta)
            const translRes = await api.get(`/annotations/${item.id}/translations`);
            let translations = [];
            if (translRes?.data) {
              if (Array.isArray(translRes.data)) translations = translRes.data;
              else if (Array.isArray(translRes.data.items)) translations = translRes.data.items;
            }

            return {
              ...item,
              assignments_count: assignments.length,
              translations_count: translations.length,
              assignments: assignments,
              translations: translations
            };
          } catch (err) {
            console.error(`Error loading details for annotation ${item.id}:`, err);
            return {
              ...item,
              assignments_count: 0,
              translations_count: 0,
              assignments: [],
              translations: []
            };
          }
        })
      );
      
      setItems(enrichedItems);
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
      // Ensure we load the enriched details (assignments/translations)
      await loadAnnotationDetails(id);
    } catch (err) {
      console.error('Search failed', err);
      setError(err.response?.data?.detail || 'No se encontró la anotación');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAnnotation = async (e) => {
    e.preventDefault();
    
    // Validar que al menos uno de los dos campos esté presente
    if (!formData.question_es.trim() && !formData.answer_es.trim()) {
      setError('Debes ingresar al menos una pregunta o una respuesta en español');
      return;
    }
    
    setCreateLoading(true);
    setError(null);
    
    try {
      // Preparar datos
      const dataToSend = {
        question_es: formData.question_es.trim() || null,
        question_gn: formData.question_gn.trim() || null,
        answer_es: formData.answer_es.trim() || null,
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

  const handleExcelFileSelect = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setExcelFile(file);
    setSelectedSheet('');
    setExcelSheets([]);
    setExcelResult(null);
    setError(null);

    // Get available sheets
    setExcelLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await api.post('/annotations/upload/sheets', formData);

      setExcelSheets(response.data.sheets || []);
      if (response.data.sheets?.length > 0) {
        setSelectedSheet(response.data.sheets[0]);
      }
    } catch (err) {
      console.error('Error reading Excel file:', err);
      setError(err.response?.data?.detail || 'Error al leer el archivo Excel');
    } finally {
      setExcelLoading(false);
    }
  };

  const handleExcelUpload = async () => {
    if (!excelFile || !selectedSheet) {
      setError('Selecciona un archivo y una hoja');
      return;
    }

    setExcelLoading(true);
    setError(null);
    setExcelResult(null);

    try {
      const formData = new FormData();
      formData.append('file', excelFile);
      formData.append('sheet', selectedSheet);

      const response = await api.post('/annotations/upload/bulk', formData);

      setExcelResult(response.data);

      if (response.data.added_count > 0) {
        toast.success(`✅ ${response.data.added_count} anotaciones cargadas exitosamente`);
        // Recargar tabla después de un pequeño delay
        setTimeout(() => {
          loadTable(0);
          setShowExcelUpload(false);
          setExcelFile(null);
          setSelectedSheet('');
          setExcelSheets([]);
        }, 1000);
      }
    } catch (err) {
      console.error('Excel upload failed:', err);
      setError(err.response?.data?.detail || 'Error al cargar el archivo');
    } finally {
      setExcelLoading(false);
    }
  };

  const handleAssignAnnotation = async () => {
    if (!annotation || !selectedTranslator) {
      toast.error('Selecciona un traductor');
      return;
    }

    setAssignLoading(true);
    try {
      const res = await annotationsAPI.assign(annotation.id, {
        assigned_to_user_id: selectedTranslator
      });
      const updatedAnnotation = res?.data || res;
      setAnnotation(updatedAnnotation);
      toast.success(`Anotación asignada a ${translators.find(t => t.id === selectedTranslator)?.username}`);
      setSelectedTranslator(null);
      loadTable(skip);
    } catch (err) {
      console.error('Assign failed', err);
      toast.error(err.response?.data?.detail || 'Error al asignar anotación');
    } finally {
      setAssignLoading(false);
    }
  };

  const handleUnassignAnnotation = async () => {
    if (!annotation) return;

    setAssignLoading(true);
    try {
      const res = await annotationsAPI.assign(annotation.id, {
        assigned_to_user_id: null
      });
      const updatedAnnotation = res?.data || res;
      setAnnotation(updatedAnnotation);
      toast.success('Anotación desasignada');
      setSelectedTranslator(null);
      loadTable(skip);
    } catch (err) {
      console.error('Unassign failed', err);
      toast.error(err.response?.data?.detail || 'Error al desasignar anotación');
    } finally {
      setAssignLoading(false);
    }
  };

  const loadAnnotationDetails = async (annotationId) => {
    try {
      setLoading(true);
      // Fetch base annotation
      const res = await annotationsAPI.getById(annotationId);
      const base = res?.data || res;

      // Fetch assignments and translations (handle different response shapes)
      const assignRes = await api.get(`/annotations/${annotationId}/assignments`);
      const assignments = assignRes?.data || [];

      const translRes = await api.get(`/annotations/${annotationId}/translations`);
      let translations = [];
      if (translRes?.data) {
        if (Array.isArray(translRes.data)) translations = translRes.data;
        else if (Array.isArray(translRes.data.items)) translations = translRes.data.items;
      }

      setAnnotation({
        ...base,
        assignments_count: assignments.length,
        translations_count: translations.length,
        assignments,
        translations,
      });
    } catch (err) {
      console.error('Error loading annotation details:', err);
      toast.error('Error al cargar detalles de la anotación');
    } finally {
      setLoading(false);
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
          <div className="flex gap-2">
            <button
              onClick={() => setShowExcelUpload(true)}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium"
            >
              📁 Cargar Excel
            </button>
            <button
              onClick={() => setShowCreateForm(true)}
              className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-medium"
            >
              + Agregar Anotación
            </button>
          </div>
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
              {annotation.question_es && (
                <div>
                  <label className="text-xs font-medium text-gray-500">Pregunta (Español)</label>
                  <p className="text-sm text-gray-700 mt-1 p-2 bg-gray-50 rounded">{annotation.question_es}</p>
                </div>
              )}
              {annotation.question_gn && (
                <div>
                  <label className="text-xs font-medium text-gray-500">Pregunta (Guaraní)</label>
                  <p className="text-sm text-gray-700 mt-1 p-2 bg-gray-50 rounded">{annotation.question_gn}</p>
                </div>
              )}
              {annotation.answer_es && (
                <div>
                  <label className="text-xs font-medium text-gray-500">Respuesta (Español)</label>
                  <p className="text-sm text-gray-700 mt-1 p-2 bg-gray-50 rounded">{annotation.answer_es}</p>
                </div>
              )}
              {annotation.answer_gn && (
                <div>
                  <label className="text-xs font-medium text-gray-500">Respuesta (Guaraní)</label>
                  <p className="text-sm text-gray-700 mt-1 p-2 bg-gray-50 rounded">{annotation.answer_gn}</p>
                </div>
              )}
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

            {/* Assignment Section 
            <div className="mt-6 border-t pt-6">
              <h4 className="text-sm font-semibold mb-4">Gestión de Asignaciones</h4>
              <div className="bg-blue-50 p-4 rounded-lg border border-blue-200 mb-4">
                <p className="text-sm mb-3">
                  <strong>👥 Personas Asignadas:</strong> <span className="text-blue-700 font-medium text-lg">{annotation.assignments_count || 0}</span>
                </p>
                {annotation.assignments && annotation.assignments.length > 0 && (
                  <div className="mb-3">
                    <ul className="list-disc list-inside">
                      {annotation.assignments.map(a => (
                        <li key={a.id} className="text-sm text-gray-700">
                          {translators.find(t => t.id === a.user_id)?.username || `Usuario #${a.user_id}`}
                          <span className="text-xs text-gray-500 ml-2">
                            ({new Date(a.assigned_at).toLocaleDateString('es-ES')})
                          </span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                <div className="flex gap-2 items-end">
                  <div className="flex-1">
                    <label className="block text-xs font-medium text-gray-700 mb-1">Asignar a otro traductor</label>
                    <select
                      value={selectedTranslator || ''}
                      onChange={(e) => setSelectedTranslator(e.target.value ? parseInt(e.target.value) : null)}
                      className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                      disabled={assignLoading}
                    >
                      <option value="">-- Selecciona traductor --</option>
                      {translators.map(t => (
                        <option key={t.id} value={t.id}>{t.username}</option>
                      ))}
                    </select>
                  </div>
                  <button
                    onClick={handleAssignAnnotation}
                    disabled={assignLoading || !selectedTranslator}
                    className="px-4 py-2 bg-green-600 text-white rounded text-sm font-medium hover:bg-green-700 disabled:opacity-50"
                  >
                    {assignLoading ? 'Asignando...' : 'Asignar'}
                  </button>
                </div>
              </div>
            </div>*/}

            {/* Translations Section */}
            <div className="mt-6 border-t pt-6">
              <h4 className="text-sm font-semibold mb-4">Traducciones Completadas</h4>
              <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                <p className="text-sm mb-4">
                  <strong>✏️ Total de Traducciones:</strong> <span className="text-green-700 font-medium text-lg">{annotation.translations_count || 0}/3</span>
                </p>
                {annotation.translations && annotation.translations.length > 0 ? (
                  <div className="space-y-3">
                    {annotation.translations.map((trans, idx) => (
                      <div key={trans.id} className="bg-white p-3 rounded border border-green-200">
                        <p className="text-xs font-semibold text-gray-600 mb-2">
                          Traducción #{idx + 1} - Por: {translators.find(t => t.id === trans.user_id)?.username || `Usuario #${trans.user_id}`}
                          <span className="text-gray-500 ml-2">
                            ({new Date(trans.created_at).toLocaleDateString('es-ES')})
                          </span>
                        </p>
                        {trans.question_gn && (
                          <div className="mb-2">
                            <label className="text-xs font-medium text-gray-600">Pregunta (Guaraní):</label>
                            <p className="text-sm text-gray-700 p-1 bg-gray-50 rounded mt-1">{trans.question_gn}</p>
                          </div>
                        )}
                        {trans.answer_gn && (
                          <div>
                            <label className="text-xs font-medium text-gray-600">Respuesta (Guaraní):</label>
                            <p className="text-sm text-gray-700 p-1 bg-gray-50 rounded mt-1">{trans.answer_gn}</p>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-600 italic">No hay traducciones completadas aún.</p>
                )}
              </div>
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
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">👥 Asignados</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">✏️ Traducciones</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Estado</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Acciones</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {tableLoading ? (
                  <tr><td colSpan={7} className="px-4 py-6 text-center">Cargando...</td></tr>
                ) : items.length === 0 ? (
                  <tr><td colSpan={7} className="px-4 py-6 text-center">No hay anotaciones.</td></tr>
                ) : (
                items.map(a => (
                  <tr key={a.id}>
                    <td className="px-4 py-3 text-sm text-gray-700 font-medium">{a.id}</td>
                    <td className="px-4 py-3 text-sm text-gray-700">{a.question_es ? a.question_es.substring(0, 40) + '...' : '(sin pregunta)'}</td>
                    <td className="px-4 py-3 text-sm text-gray-700">{a.answer_es ? a.answer_es.substring(0, 40) + '...' : '(sin respuesta)'}</td>
                    <td className="px-4 py-3 text-center">
                      <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-semibold">
                        {a.assignments_count || 0}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        (a.translations_count || 0) >= 3 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {a.translations_count || 0}/3
                      </span>
                    </td>
                    <td className="px-4 py-3 text-center">
                      {a.translated ? (
                        <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs font-medium">
                          ✓ Completada
                        </span>
                      ) : (
                        <span className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs font-medium">
                          ⏳ Pendiente
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-700">
                      <div className="flex gap-2">
                        <button 
                          onClick={() => loadAnnotationDetails(a.id)}
                          className="text-sm text-indigo-600 hover:text-indigo-800 hover:underline font-medium"
                        >
                          Ver Detalles
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
                    Pregunta en Español (al menos uno de los dos es obligatorio)
                  </label>
                  <textarea
                    value={formData.question_es}
                    onChange={(e) => setFormData({...formData, question_es: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows={4}
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
                    Respuesta en Español (opcional)
                  </label>
                  <textarea
                    value={formData.answer_es}
                    onChange={(e) => setFormData({...formData, answer_es: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows={4}
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

        {/* Excel Upload Modal */}
        {showExcelUpload && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold">📁 Cargar Anotaciones desde Excel</h3>
                  <p className="text-xs text-gray-500 mt-1">Sistema Multi-Usuario v2.0</p>
                </div>
                <button
                  onClick={() => {
                    setShowExcelUpload(false);
                    setError(null);
                    setExcelFile(null);
                    setSelectedSheet('');
                    setExcelSheets([]);
                    setExcelResult(null);
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

              <div className="space-y-4">
                {/* Instrucciones - Actualizado */}
                <div className="bg-blue-50 border border-blue-200 rounded p-4">
                  <h4 className="font-semibold text-sm text-blue-900 mb-3">✅ Formato esperado:</h4>
                  <div className="space-y-2">
                    <div className="bg-white p-2 rounded text-xs">
                      <p className="font-semibold text-blue-900 mb-1">Columnas REQUERIDAS:</p>
                      <ul className="space-y-1 text-blue-800 ml-2">
                        <li>• <strong>Columna B:</strong> Pregunta en español</li>
                        <li>• <strong>Columna D:</strong> Respuesta en español</li>
                      </ul>
                    </div>
                    <div className="bg-white p-2 rounded text-xs">
                      <p className="font-semibold text-blue-900 mb-1">Columnas OPCIONALES:</p>
                      <ul className="space-y-1 text-blue-800 ml-2">
                        <li>• <strong>Columna F:</strong> Número de respuesta</li>
                        <li>• <strong>Columna G:</strong> Ecuación/Solución</li>
                      </ul>
                    </div>
                  </div>
                </div>



                {/* File Upload */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Selecciona archivo Excel (.xlsx)
                  </label>
                  <input
                    type="file"
                    accept=".xlsx,.xls"
                    onChange={handleExcelFileSelect}
                    disabled={excelLoading}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                  />
                  {excelFile && (
                    <p className="text-xs text-gray-600 mt-1">
                      📄 {excelFile.name}
                    </p>
                  )}
                </div>

                {/* Sheet Selection */}
                {excelSheets.length > 0 && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Selecciona la hoja a procesar
                    </label>
                    <select
                      value={selectedSheet}
                      onChange={(e) => setSelectedSheet(e.target.value)}
                      disabled={excelLoading}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                    >
                      <option value="">-- Selecciona una hoja --</option>
                      {excelSheets.map((sheet, idx) => (
                        <option key={idx} value={sheet}>{sheet}</option>
                      ))}
                    </select>
                  </div>
                )}

                {/* Results */}
                {excelResult && (
                  <div className="bg-gray-50 border border-gray-200 rounded p-4 space-y-3">
                    <h4 className="font-semibold text-sm">📊 Resultados de la carga:</h4>
                    
                    <div className="grid grid-cols-2 gap-3">
                      <div className="bg-green-50 p-3 rounded border border-green-200">
                        <p className="text-xs text-gray-600">Anotaciones creadas</p>
                        <p className="text-lg font-bold text-green-700">{excelResult.added_count}</p>
                      </div>
                      <div className="bg-yellow-50 p-3 rounded border border-yellow-200">
                        <p className="text-xs text-gray-600">Filas omitidas</p>
                        <p className="text-lg font-bold text-yellow-700">{excelResult.skipped_count}</p>
                      </div>
                    </div>

                    {/* Nuevo: Recordatorio post-carga */}
                    <div className="bg-blue-50 p-3 rounded border border-blue-200">
                      <p className="text-xs font-semibold text-blue-900 mb-1">✅ Próximo paso:</p>
                      <p className="text-xs text-blue-800">
                        Las anotaciones se han creado sin traducciones. 
                        <strong> Ve a la tabla, haz click en "Ver Detalles" y asigna traductores.</strong>
                      </p>
                    </div>

                    {excelResult.errors.length > 0 && (
                      <div>
                        <h5 className="text-xs font-semibold text-red-700 mb-2">❌ Errores encontrados:</h5>
                        <div className="bg-red-50 p-2 rounded max-h-32 overflow-y-auto">
                          {excelResult.errors.map((err, idx) => (
                            <p key={idx} className="text-xs text-red-700 mb-1">{err}</p>
                          ))}
                        </div>
                      </div>
                    )}

                    {excelResult.details.length > 0 && (
                      <div>
                        <h5 className="text-xs font-semibold text-gray-700 mb-2">✅ Primeras anotaciones agregadas:</h5>
                        <div className="bg-white p-2 rounded border border-gray-200 max-h-32 overflow-y-auto space-y-2">
                          {excelResult.details.slice(0, 3).map((detail, idx) => (
                            <div key={idx} className="text-xs bg-gray-50 p-2 rounded">
                              <p className="font-medium">📌 ID: {detail.id}</p>
                              {detail.question_es && <p className="text-gray-600 truncate">❓ {detail.question_es}</p>}
                              {detail.answer_es && <p className="text-gray-600 truncate">✏️ {detail.answer_es}</p>}
                            </div>
                          ))}
                          {excelResult.details.length > 3 && (
                            <p className="text-xs text-gray-500">... y {excelResult.details.length - 3} más</p>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Buttons */}
                <div className="flex items-center justify-end gap-3 pt-4 border-t">
                  <button
                    onClick={() => {
                      setShowExcelUpload(false);
                      setError(null);
                      setExcelFile(null);
                      setSelectedSheet('');
                      setExcelSheets([]);
                      setExcelResult(null);
                    }}
                    className="px-4 py-2 text-gray-600 border border-gray-300 rounded hover:bg-gray-50"
                    disabled={excelLoading}
                  >
                    Cerrar
                  </button>
                  <button
                    onClick={handleExcelUpload}
                    disabled={!excelFile || !selectedSheet || excelLoading}
                    className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                  >
                    {excelLoading ? '⏳ Cargando...' : '📤 Cargar Anotaciones'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminAnnotations;
