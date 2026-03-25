import { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { annotationsAPI } from '../services/api';
import { toast } from 'react-toastify';
import Navbar from '../components/common/Navbar';

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
      const res = await annotationsAPI.getAvailableForTranslation(currentPage * itemsPerPage, itemsPerPage);
      const allAnnotations = res?.data?.items || [];
      
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
          <h1 className="text-3xl font-bold text-gray-900">📚 Traducciones Pendientes</h1>
          <p className="text-gray-600 mt-2">Anotaciones disponibles para traducir. Click en "✏️ Traducir" para asignarte a ti mismo.</p>
        </div>

        {loading ? (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : annotations.length === 0 ? (
          <div className="bg-white rounded-lg shadow-md p-8 text-center">
            <p className="text-gray-600 text-lg">✅ No hay anotaciones pendientes de traducir</p>
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
                            <p className="text-sm font-medium text-gray-600">Número:</p>
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
                      className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition font-semibold disabled:opacity-50 whitespace-nowrap"
                    >
                      {assigning ? '⏳ Asignando...' : '✏️ Traducir'}
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
    </div>
  );
};

export default PendingTranslationsPage;
