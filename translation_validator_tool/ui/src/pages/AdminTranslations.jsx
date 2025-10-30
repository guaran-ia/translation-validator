import { useState, useEffect } from 'react';
import { translationsAPI, validationsAPI } from '../services/api';
import { useAuth } from '../hooks/useAuth';
import TranslationCard from '../components/translation/TranslationCard';
import Navbar from '../components/common/Navbar';

// Simple helper to truncate long text in table cells
const truncate = (s, n = 80) => (s && s.length > n ? s.slice(0, n) + '…' : s);

const AdminTranslations = () => {
  const { user } = useAuth();
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

  useEffect(() => {
    if (user && user.is_superuser) loadTable(0);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]);

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

  if (!user || !user.is_superuser) return (
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
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Validaciones</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Sugerencias</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Acciones</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {tableLoading ? (
                <tr><td colSpan={6} className="px-4 py-6 text-center">Cargando...</td></tr>
              ) : items.length === 0 ? (
                <tr><td colSpan={6} className="px-4 py-6 text-center">No hay traducciones.</td></tr>
              ) : (
                items.map(t => (
                  <tr key={t.id}>
                    <td className="px-4 py-3 text-sm text-gray-700">{t.id}</td>
                    <td className="px-4 py-3 text-sm text-gray-700">{t.direction}</td>
                    <td className="px-4 py-3 text-sm text-gray-700">{truncate(t.guarani_text || t.spanish_text)}</td>
                    <td className="px-4 py-3 text-sm text-gray-700">{t.validation_count}</td>
                    <td className="px-4 py-3 text-sm text-gray-700">{t.suggestion_count}</td>
                    <td className="px-4 py-3 text-sm text-gray-700">
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
      </div>
    </div>
  );
};

export default AdminTranslations;