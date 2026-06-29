import { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { annotationsAPI } from '../services/api';
import { toast } from 'react-toastify';
import Navbar from '../components/common/Navbar';
import WeeklyLeaderboard from '../components/common/WeeklyLeaderboard';

// Fisher-Yates shuffle
const shuffleArray = (arr) => {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
};

const PendingTranslationsPage = () => {
  const { user } = useAuth();
  const [annotations, setAnnotations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [assigning, setAssigning] = useState(false);
  const [currentPage, setCurrentPage] = useState(0);
  const itemsPerPage = 10;

  useEffect(() => {
    if (user) {
      loadPendingAnnotations();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user, currentPage]);

  const loadPendingAnnotations = async () => {
    setLoading(true);
    try {
      // Obtener anotaciones disponibles para traducir con paginación
      const res = await annotationsAPI.getAvailableForTranslation(currentPage * itemsPerPage, itemsPerPage, true);
      let allAnnotations = res?.data?.items || [];
      // Randomizar orden antes de mostrar
      if (allAnnotations.length > 1) {
        allAnnotations = shuffleArray(allAnnotations.slice());
      }

      setAnnotations(allAnnotations);
    } catch (error) {
      console.error('Error loading pending annotations:', error);
      toast.error('Error al cargar las anotaciones pendientes');
    } finally {
      setLoading(false);
    }
  };

  const handleAssignToMe = async (annotation) => {
    setAssigning(true);
    try {
      // Asignar al usuario actual
      await annotationsAPI.assignUser(annotation.id, user.id);
      
      toast.success('✅ ¡Asigando correctamente! Aparecerá en "Mis pendientes"');
      
      // Recargar la lista
      await loadPendingAnnotations();
    } catch (error) {
      console.error('Error assigning annotation:', error);
      toast.error('Error al asignarte a ti mismo');
    } finally {
      setAssigning(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="mb-8">
          <div className="bg-gradient-to-r from-teal-600 to-teal-700 rounded-2xl shadow-lg p-8 text-white">
            <h1 className="text-3xl font-bold">
              Traducciones pendientes
            </h1>

            <p className="mt-2 text-teal-100">
              Selecciona las anotaciones que deseas traducir y asígnatelas para comenzar. Para ello, haz clic en el botón "Traducir" y aparecerán en tu sección de "Mis pendientes".
            </p>
          </div>
        </div>

        {/* Disclaimer */}
        <div className="mb-6 bg-blue-50 border-l-4 border-blue-400 p-4 rounded">
          <p className="text-blue-800 text-sm">
            <span className="font-semibold">Nota:</span> No es necesario traducir todo el listado. Puedes seleccionar únicamente los enunciados que prefieras.
          </p>
        </div>

        {loading ? (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : annotations.length === 0 ? (
          <div className="bg-white rounded-lg shadow-md p-8 text-center">
            <p className="text-gray-600 text-lg">No hay anotaciones pendientes de traducir</p>
          </div>
        ) : (
          <>
            <div className="grid gap-4 mb-6">
              {annotations.map((annotation) => (
                <div key={annotation.id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 mb-3">
                        {annotation.question_es}
                      </h3>

                      <div className="space-y-2">
                        {annotation.answer_es && (
                        <div>
                          <p className="text-gray-900">{annotation.answer_es}</p>
                        </div>
                          )}
                         {annotation.answer_number && (
                            <div>
                                <p className="text-sm font-medium text-gray-600">Información adicional:</p>
                            </div>
                        )}
                        {annotation.answer_number && (
                          <div>
                            <p className="text-sm font-medium text-gray-600">Número de respuesta:</p>
                            <p className="text-gray-900">{annotation.answer_number}</p>
                          </div>
                        )}
                        {annotation.equation_solution && (
                          <div>
                            <p className="text-sm font-medium text-gray-600">Ecuación:</p>
                            <p className="text-gray-900">{annotation.equation_solution}</p>
                          </div>
                        )}
                      </div>
                    </div>
                    <button
                      onClick={() => handleAssignToMe(annotation)}
                      disabled={assigning}
                      className="px-6 py-3 bg-gradient-to-r from-teal-600 to-teal-700 text-white rounded-lg hover:bg-green-700 transition font-semibold disabled:opacity-50 whitespace-nowrap"
                    >
                      {assigning ? '⏳ Asignando...' : 'Traducir'}
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {/* Paginación */}
            <div className="flex justify-between items-center bg-white rounded-lg shadow-md p-4">
              <button
                onClick={() => setCurrentPage(Math.max(0, currentPage - 1))}
                disabled={currentPage === 0 || loading}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition font-medium"
              >
                ← Anterior
              </button>
              <div className="text-gray-600 font-medium">
                Página {currentPage + 1} • Mostrando {annotations.length} anotaciones
              </div>
              <button
                onClick={() => setCurrentPage(currentPage + 1)}
                disabled={annotations.length < itemsPerPage || loading}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition font-medium"
              >
                Siguiente →
              </button>
            </div>
          </>
        )}
      </div>
      <div className="hidden xl:block absolute top-28 right-1">
        <WeeklyLeaderboard source="api"/>
      </div>
    </div>
  );
};

export default PendingTranslationsPage;
