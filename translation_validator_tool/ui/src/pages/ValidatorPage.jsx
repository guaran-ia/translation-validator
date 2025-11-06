import { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { translationsAPI, validationsAPI, suggestionsAPI } from '../services/api';
import { toast } from 'react-toastify';

// Componentes
import Navbar from '../components/common/Navbar';
// StatsBar removed per user request: statistics will not be shown
import NavigationControls from '../components/common/NavigationControls';
import TranslationCard from '../components/translation/TranslationCard';
import CorrectnessButtons from '../components/translation/CorrectnessButtons';
import ScoreSelector from '../components/translation/ScoreSelector';
import NotesTextarea from '../components/translation/NotesTextarea';
import SuggestionModal from '../components/suggestion/SuggestionModal';

const ValidatorPage = () => {
  const { user } = useAuth();

  const [currentTranslation, setCurrentTranslation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [showSuggestionModal, setShowSuggestionModal] = useState(false);
  const [showContinueModal, setShowContinueModal] = useState(false);
  const [selectedSuggestion, setSelectedSuggestion] = useState(null);

  const [formData, setFormData] = useState({
    correctness: '',
    fluency_score: null,
    accuracy_score: null,
    notes: ''
  });
  
  const [selectedCategory, setSelectedCategory] = useState(null);

  useEffect(() => {
    if (user) loadData();
    else {
      // If no user, still load a random translation for anonymous flow
      (async () => {
        setLoading(true);
        try {
          const res = await translationsAPI.getRandom();
          setCurrentTranslation(res.data || res);
          resetForm();
          setSelectedSuggestion(null);
        } catch (err) {
          console.warn('Could not load random translation for anonymous user', err);
          setCurrentTranslation(null);
        } finally {
          setLoading(false);
        }
      })();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]);

  // Whenever the current translation changes, refresh full data if needed
  useEffect(() => {
    if (!currentTranslation || !currentTranslation.id) return;
    if (currentTranslation.validation_count !== undefined) return;

    let mounted = true;
    const refresh = async () => {
      try {
        const res = await translationsAPI.getById(currentTranslation.id);
        const full = res?.data || res;
        if (mounted && full) {
          setCurrentTranslation(full);
          setSelectedSuggestion(null);
        }
      } catch (err) {
        console.warn('Could not refresh current translation', err);
      }
    };

    refresh();
    return () => { mounted = false; };
  }, [currentTranslation?.id]);

  const resetForm = () => {
    setFormData({ correctness: '', fluency_score: null, accuracy_score: null, notes: '' });
    setSelectedCategory(null);
  };

  // loadData: fetch next translation that the user hasn't suggested/validated and
  // that has fewer than 3 validations. For anonymous users use getRandom().
  const loadData = async () => {
    setLoading(true);
    try {
      if (!user) {
        const response = await translationsAPI.getRandom();
        setCurrentTranslation(response.data || response);
        resetForm();
        setSelectedSuggestion(null);
        return;
      }

      // Use server-side endpoint that returns a suitable translation for the current validator
      const response = await translationsAPI.getNextSuitable();
      const t = response.data || response;
      setCurrentTranslation(t);
      resetForm();
      setSelectedSuggestion(null);
    } catch (error) {
      console.error('Error al cargar los datos:', error);
      if (error.response?.status === 404) {
        setCurrentTranslation(null);
        setSelectedSuggestion(null);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleNextTranslation = async () => {
    if (!user || !currentTranslation) return;
    setLoading(true);
    try {
      // For the 'Next' button we want the sequential next translation (navigation),
      // not the "suitable" filtered selection used only on initial entry.
      const response = await translationsAPI.getNextFrom(currentTranslation.id);
      const t = response.data || response;
      setCurrentTranslation(t);
      resetForm();
      setSelectedSuggestion(null);
    } catch (error) {
      console.error('Error loading next translation:', error);
      if (error.response?.status === 404) {
        setCurrentTranslation(null);
        setSelectedSuggestion(null);
      }
    } finally {
      setLoading(false);
    }
  };

  const handlePreviousTranslation = async () => {
    if (!user || !currentTranslation) return;
    setLoading(true);
    try {
      const response = await translationsAPI.getPrevious(currentTranslation.id);
      setCurrentTranslation(response.data);
      resetForm();
      setSelectedSuggestion(null);
    } catch (error) {
      console.error('Error loading previous translation:', error);
    } finally {
      setLoading(false);
    }
  };

  const isFormValid = () => {
    const baseValid = formData.correctness && formData.fluency_score && formData.accuracy_score;
    
    // If it's a gn-sp original translation, category is required
    if (currentTranslation?.direction === 'gn-sp' && currentTranslation?.is_original) {
      return baseValid && selectedCategory;
    }
    
    return baseValid;
  };

  const handleCorrectnessSelect = (correctness) => setFormData(prev => ({ ...prev, correctness }));
  const handleFluencySelect = (score) => setFormData(prev => ({ ...prev, fluency_score: score }));
  const handleAccuracySelect = (score) => setFormData(prev => ({ ...prev, accuracy_score: score }));
  const handleNotesChange = (notes) => setFormData(prev => ({ ...prev, notes }));
  const handleCategoryChange = (category) => setSelectedCategory(category);

  const handleSubmitValidation = async () => {
    if (!isFormValid() || !currentTranslation) return;

    // Refresh before submit to avoid validating a translation with >=3 validations
    try {
      const res = await translationsAPI.getById(currentTranslation.id);
      const fresh = res?.data || res;
      if (fresh && fresh.validation_count !== undefined && fresh.validation_count >= 3) {
        toast.error('No es posible validar: esta traducción ya tiene 3 o más validaciones en su dirección.');
        setCurrentTranslation(fresh);
        setSelectedSuggestion(null);
        return;
      }
    } catch (err) {
      console.warn('Could not refresh translation before submit', err);
    }

    setSubmitting(true);
    try {
      const payload = { translation_id: currentTranslation.id, ...formData };
      if (selectedSuggestion && selectedSuggestion.id) payload.suggestion_id = selectedSuggestion.id;
      
      // Include category if selected (required for gn-sp original translations)
      if (selectedCategory) {
        payload.category = selectedCategory;
      }

      await validationsAPI.create(payload);
      setSelectedSuggestion(null);
      await loadData();
    } catch (error) {
      console.error('Error al enviar la validación:', error);
      if (error.response?.status === 400) {
        const msg = error.response?.data?.detail || 'Ya has validado esta traducción.';
        toast.error(msg);
        await loadData();
      } else {
        toast.error('Error al enviar la validación. Inténtalo de nuevo.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  const handleSubmitSuggestion = async (suggestionData) => {
    try {
      await suggestionsAPI.create(suggestionData);
      toast.success('¡Sugerencia enviada con éxito! Tu propuesta ayudará a mejorar la calidad de las traducciones.');
      await loadData();
    } catch (error) {
      console.error('Error al enviar la sugerencia:', error);
      if (error.response?.status === 400) {
        toast.error('Error en los datos de la sugerencia. Verifica que has proporcionado al menos una traducción.');
      } else if (error.response?.status === 404) {
        toast.error('La traducción no fue encontrada.');
      } else {
        toast.error('Error al enviar la sugerencia. Inténtalo de nuevo.');
      }
    }
  };

  if (loading) return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </div>
    </div>
  );

  if (!currentTranslation) return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="text-center py-12">
          <div className="text-6xl mb-4">🎉</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">¡Felicidades!</h2>
          <p className="text-gray-600">Has validado todas las traducciones disponibles.</p>
          <button onClick={loadData} className="btn btn-primary mt-4">Buscar nuevas traducciones</button>
        </div>
      </div>
    </div>
  );

  // Check if this is a Guarani sentence without Spanish translation AND no suggestion selected
  const isGuaraniWithoutTranslation = currentTranslation?.direction === 'gn-sp' && 
                                       currentTranslation?.is_original && 
                                       !currentTranslation?.spanish_text &&
                                       !selectedSuggestion; // Allow validation if suggestion is selected

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-6xl mx-auto px-4 py-8">
        {user && (
          <NavigationControls
            currentTranslation={currentTranslation}
            onNext={handleNextTranslation}
            onPrevious={handlePreviousTranslation}
            onSuggest={() => setShowSuggestionModal(true)}
            loading={loading}
          />
        )}

        <TranslationCard
          translation={currentTranslation}
          onReplace={(t) => { setCurrentTranslation(t); resetForm(); setSelectedSuggestion(null); }}
          onValidateSuggestion={(s) => setSelectedSuggestion(s)}
          onClearSelection={() => setSelectedSuggestion(null)}
          onCategoryChange={handleCategoryChange}
          selectedSuggestion={selectedSuggestion}
        />

        {selectedSuggestion && (
          <div className="mt-4 mb-2 p-3 rounded-md bg-blue-50 border border-blue-100 text-sm text-blue-800 flex items-center justify-between">
            <div className="text-sm">
              <strong className="mr-2">Sugerencia seleccionada</strong>
              <span className="text-gray-700">por usuario #{selectedSuggestion.user_id}</span>
              <span className="mx-2 text-gray-400">•</span>
              <span className="text-gray-600">{new Date(selectedSuggestion.created_at).toLocaleString()}</span>
              <span className="mx-2 text-gray-400">•</span>
              <span className="text-gray-500">sugerencia #{selectedSuggestion.id}</span>
            </div>
            <div>
              <button onClick={() => setSelectedSuggestion(null)} className="text-xs px-2 py-1 bg-white border rounded text-blue-700 hover:bg-blue-50">Quitar selección</button>
            </div>
          </div>
        )}

        {currentTranslation?.validation_count !== undefined && currentTranslation.validation_count >= 3 && (
          <div className="mt-4 mb-2 p-3 rounded-md bg-red-50 border border-red-100 text-sm text-red-800 flex items-center justify-between">
            <div>
              <strong>No disponible para validar</strong>
              <span className="ml-2 text-gray-700">Esta traducción ya tiene {currentTranslation.validation_count} validaciones en su dirección.</span>
            </div>
            <div className="text-xs text-gray-500">ID: {currentTranslation.id}</div>
          </div>
        )}

        {/* Show message for Guarani sentences without translation and no suggestion selected */}
        {isGuaraniWithoutTranslation ? (
          <div className="card mt-6">
            <div className="text-center py-8 space-y-4">
              <div className="text-5xl mb-4">📝</div>
              <h3 className="text-xl font-semibold text-gray-800">Esta oración aún no tiene traducción al español</h3>
              <p className="text-gray-600 max-w-lg mx-auto">
                Esta oración en Guaraní aún no tiene una traducción oficial al español. 
                Puedes <strong>sugerir una traducción</strong> o <strong>validar una sugerencia existente</strong> haciendo clic en "Validar" en las sugerencias arriba.
              </p>
              <div className="pt-4 flex flex-col items-center gap-3">
                <button 
                  onClick={() => setShowSuggestionModal(true)} 
                  className="btn btn-primary text-lg px-6 py-3"
                >
                  Sugerir traducción al español
                </button>
                <p className="text-sm text-gray-500">
                  💡 Tip: Si hay sugerencias arriba, puedes hacer clic en "Validar" para evaluarlas
                </p>
              </div>
            </div>
          </div>
        ) : !(currentTranslation.validation_count !== undefined && currentTranslation.validation_count >= 3) && (
          <div className="card mt-6">
            <div className="space-y-6">
              {currentTranslation.user_has_suggested && (
                <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-100">
                  <h3 className="text-lg font-medium">Has sugerido una traducción</h3>
                  <p className="text-sm text-gray-600 mt-2">Ya enviaste una sugerencia para esta traducción. Puedes editarla si lo deseas, pero esto no impide que puedas validar la traducción.</p>
                  <div className="pt-3">
                    <button onClick={() => setShowSuggestionModal(true)} className="btn btn-secondary">✏️ Editar sugerencia</button>
                  </div>
                </div>
              )}

              <CorrectnessButtons selectedCorrectness={formData.correctness} onSelect={handleCorrectnessSelect} disabled={submitting} />

              <div className="grid md:grid-cols-2 gap-6">
                <ScoreSelector label="Puntuación de fluidez" selectedScore={formData.fluency_score} onSelect={handleFluencySelect} disabled={submitting} />
                <ScoreSelector label="Puntuación de precisión" selectedScore={formData.accuracy_score} onSelect={handleAccuracySelect} disabled={submitting} />
              </div>

              <NotesTextarea notes={formData.notes} onNotesChange={handleNotesChange} disabled={submitting} />

              {/* Category requirement message for gn-sp */}
              {currentTranslation?.direction === 'gn-sp' && currentTranslation?.is_original && !selectedCategory && (
                <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-md text-sm text-yellow-800">
                  <strong>📋 Clasificación requerida:</strong> Para oraciones originales en Guaraní, debes seleccionar una categoría (Guaraní Puro, Jopara, o Jehe'a) antes de enviar la validación.
                </div>
              )}

              <div className="flex flex-wrap gap-3 pt-4 border-t border-gray-200">
                <button onClick={handleSubmitValidation} disabled={!isFormValid() || submitting} className="btn btn-primary flex-1 min-w-[200px]">
                  {submitting ? (
                    <div className="flex items-center justify-center">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Enviando...
                    </div>
                  ) : 'Enviar validación'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      <SuggestionModal isOpen={showSuggestionModal} onClose={() => setShowSuggestionModal(false)} onSubmit={handleSubmitSuggestion} currentTranslation={currentTranslation} isLoading={submitting} />

      {showContinueModal && (
        <div className="fixed inset-0 z-40 flex items-center justify-center">
          <div className="absolute inset-0 bg-black opacity-40" onClick={() => setShowContinueModal(false)} />
          <div className="bg-white rounded-lg shadow-lg max-w-md w-full mx-4 z-50">
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-2">Continuar</h3>
              <p className="text-sm text-gray-700 mb-4">¿Quieres continuar con la siguiente traducción?</p>
              <div className="flex justify-end space-x-3">
                <button onClick={() => setShowContinueModal(false)} className="px-4 py-2 rounded-md border">No</button>
                <button onClick={async () => { setShowContinueModal(false); await handleNextTranslation(); }} className="px-4 py-2 rounded-md bg-blue-600 text-white">Sí, continuar</button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ValidatorPage;
 
