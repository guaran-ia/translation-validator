import { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { translationsAPI } from '../services/api';
import Navbar from '../components/common/Navbar';
import TranslationCard from '../components/translation/TranslationCard';

const HistoryPage = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('validated');
  const [validatedTranslations, setValidatedTranslations] = useState([]);
  const [pendingTranslations, setPendingTranslations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({
    validated: { skip: 0, limit: 20, total: 0, hasNext: false },
    pending: { skip: 0, limit: 20, total: 0, hasNext: false }
  });

  useEffect(() => {
    if (user) {
      loadValidatedTranslations();
      loadPendingTranslations();
    }
  }, [user]);

  const loadValidatedTranslations = async (skip = 0) => {
    setLoading(true);
    try {
      const response = await translationsAPI.getMyValidatedHistory(skip, 20);
      setValidatedTranslations(response.data.items);
      setPagination(prev => ({
        ...prev,
        validated: {
          skip: response.data.skip,
          limit: response.data.limit,
          total: response.data.total,
          hasNext: response.data.has_next
        }
      }));
    } catch (error) {
      console.error('Error cargando traducciones evaluadas:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadPendingTranslations = async (skip = 0) => {
    setLoading(true);
    try {
      const response = await translationsAPI.getMyPendingTranslations(skip, 20);
      setPendingTranslations(response.data.items);
      setPagination(prev => ({
        ...prev,
        pending: {
          skip: response.data.skip,
          limit: response.data.limit,
          total: response.data.total,
          hasNext: response.data.has_next
        }
      }));
    } catch (error) {
      console.error('Error cargando traducciones pendientes:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleNextPage = () => {
    const currentPagination = pagination[activeTab];
    const newSkip = currentPagination.skip + currentPagination.limit;
    
    if (activeTab === 'validated') {
      loadValidatedTranslations(newSkip);
    } else {
      loadPendingTranslations(newSkip);
    }
  };

  const handlePrevPage = () => {
    const currentPagination = pagination[activeTab];
    const newSkip = Math.max(0, currentPagination.skip - currentPagination.limit);
    
    if (activeTab === 'validated') {
      loadValidatedTranslations(newSkip);
    } else {
      loadPendingTranslations(newSkip);
    }
  };

  const currentPagination = pagination[activeTab];
  const currentTranslations = activeTab === 'validated' ? validatedTranslations : pendingTranslations;

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Historial de Traducciones</h1>
          <p className="mt-2 text-gray-600">
            Revisa las traducciones que ya has evaluado y las que están pendientes
          </p>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200 mb-8">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('validated')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'validated'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {/*Evaluadas ({pagination.validated.total})*/}
            </button>
            <button
              onClick={() => setActiveTab('pending')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'pending'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {/*Pendientes ({pagination.pending.total})*/}
            </button>
          </nav>
        </div>

        {/* Content */}
        {loading ? (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : (
          <>
            {/* Translations List */}
            <div className="space-y-6 mb-8">
              {currentTranslations.length === 0 ? (
                <div className="text-center py-12">
                  <p className="text-gray-500">
                    {activeTab === 'validated' 
                      ? 'Aún no has evaluado ninguna traducción' 
                      : 'No hay traducciones pendientes'}
                  </p>
                </div>
              ) : (
                currentTranslations.map((item) => (
                  <div key={activeTab === 'validated' ? item.validation.id : item.id} 
                       className="bg-white rounded-lg shadow-sm border p-6">
                    <TranslationCard 
                      translation={activeTab === 'validated' ? item.translation : item}
                    />
                    
                    {/* Show validation details for evaluated translations */}
                    {activeTab === 'validated' && item.validation && (
                      <div className="mt-4 pt-4 border-t border-gray-100">
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
                          <div>
                            <span className="font-medium text-gray-700">Corrección:</span>
                            <span className={`ml-2 px-2 py-1 rounded-full text-xs ${
                              item.validation.correctness === 'correct' 
                                ? 'bg-green-100 text-green-800'
                                : item.validation.correctness === 'incorrect'
                                ? 'bg-red-100 text-red-800'
                                : 'bg-yellow-100 text-yellow-800'
                            }`}>
                              {item.validation.correctness}
                            </span>
                          </div>
                          <div>
                            <span className="font-medium text-gray-700">Fluidez:</span>
                            <span className="ml-2">{item.validation.fluency_score}/5</span>
                          </div>
                          <div>
                            <span className="font-medium text-gray-700">Precisión:</span>
                            <span className="ml-2">{item.validation.accuracy_score}/5</span>
                          </div>
                          <div>
                            <span className="font-medium text-gray-700">Evaluado:</span>
                            <span className="ml-2">
                              {new Date(item.validation.created_at).toLocaleDateString()}
                            </span>
                          </div>
                        </div>
                        {item.validation.notes && (
                          <div className="mt-3">
                            <span className="font-medium text-gray-700">Notas:</span>
                            <p className="mt-1 text-gray-600">{item.validation.notes}</p>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>

            {/* Pagination */}
            {currentTranslations.length > 0 && (
              <div className="flex items-center justify-between bg-white px-4 py-3 border border-gray-200 rounded-lg">
                <div className="flex-1 flex justify-between sm:hidden">
                  <button
                    onClick={handlePrevPage}
                    disabled={currentPagination.skip === 0}
                    className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Anterior
                  </button>
                  <button
                    onClick={handleNextPage}
                    disabled={!currentPagination.hasNext}
                    className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Siguiente
                  </button>
                </div>
                <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                  <div>
                    <p className="text-sm text-gray-700">
                      Mostrando{' '}
                      <span className="font-medium">{currentPagination.skip + 1}</span>
                      {' '}a{' '}
                      <span className="font-medium">
                        {Math.min(currentPagination.skip + currentPagination.limit, currentPagination.total)}
                      </span>
                      {' '}de{' '}
                      <span className="font-medium">{currentPagination.total}</span>
                      {' '}resultados
                    </p>
                  </div>
                  <div>
                    <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                      <button
                        onClick={handlePrevPage}
                        disabled={currentPagination.skip === 0}
                        className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        Anterior
                      </button>
                      <button
                        onClick={handleNextPage}
                        disabled={!currentPagination.hasNext}
                        className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        Siguiente
                      </button>
                    </nav>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default HistoryPage;