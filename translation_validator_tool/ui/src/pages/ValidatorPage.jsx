import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
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
  const [showSuggestAfterValidationModal, setShowSuggestAfterValidationModal] = useState(false);
  const [selectedSuggestion, setSelectedSuggestion] = useState(null);
  const [comingFromValidation, setComingFromValidation] = useState(false);
  // Admin-specific search state: allow admin to load a translation by ID
  const [adminSearch, setAdminSearch] = useState('');
  const [adminSelectedTranslation, setAdminSelectedTranslation] = useState(false);
  const [searchParams, setSearchParams] = useSearchParams();

  const [formData, setFormData] = useState({
    correctness: '',
    fluency_score: null,
    accuracy_score: null,
    notes: ''
  });
  
  const [selectedCategory, setSelectedCategory] = useState(null);
  
  // Track if user has made changes to validation form without submitting
  const hasUnsavedChanges = () => {
    return formData.correctness !== '' || 
           formData.fluency_score !== null || 
           formData.accuracy_score !== null || 
           formData.notes !== '' ||
           selectedCategory !== null;
  };

  useEffect(() => {
    const translationIdParam = searchParams.get('translation');

    if (translationIdParam && user) {
      // Admin (or authorized user) requested a specific translation via query param
      const tid = parseInt(translationIdParam, 10);
      if (!isNaN(tid)) {
        loadTranslationById(tid);
        return;
      }
    }

    if (user) {
      loadData();
    } else {
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
  }, [user, searchParams]);

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
      // Do not override an admin-selected translation (adminSelectedTranslation flag)
      if (adminSelectedTranslation) {
        // admin has selected a specific translation: just refresh its full data
        if (currentTranslation && currentTranslation.id) {
          const fres = await translationsAPI.getById(currentTranslation.id);
          setCurrentTranslation(fres.data || fres);
          resetForm();
          setSelectedSuggestion(null);
          return;
        }
      }

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
    
    // Check for unsaved changes
    if (hasUnsavedChanges()) {
      toast.warning('Tienes cambios sin guardar. Por favor envía la validación antes de continuar.');
      return;
    }
    
    // navigating manually clears any admin-selected fixed translation
    setAdminSelectedTranslation(false);
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
    
    // Check for unsaved changes
    if (hasUnsavedChanges()) {
      toast.warning('Tienes cambios sin guardar. Por favor envía la validación antes de continuar.');
      return;
    }
    
    // navigating manually clears any admin-selected fixed translation
    setAdminSelectedTranslation(false);
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
    // Use explicit checks to avoid falsy/truthy pitfalls (e.g. score=0)
    const baseValid = !!formData.correctness && formData.fluency_score !== null && formData.accuracy_score !== null;

    // If it's a gn-sp original translation, category is required
    if (currentTranslation?.direction === 'gn-sp' && currentTranslation?.is_original) {
      return baseValid && !!selectedCategory;
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
      
      // Ask if user wants to suggest a translation after validating
      // Only show if user hasn't already suggested for this translation
      if (!currentTranslation?.user_has_suggested) {
        setComingFromValidation(true);
        setShowSuggestAfterValidationModal(true);
      } else {
        // If admin loaded a specific translation, do not replace it with a random one.
        if (adminSelectedTranslation && user?.is_superuser) {
          setShowContinueModal(true);
        } else {
          await loadData();
        }
      }
    } catch (error) {
      console.error('Error al enviar la validación:', error);
      if (error.response?.status === 400) {
        const msg = error.response?.data?.detail || 'Ya has validado esta traducción.';
        toast.error(msg);
        if (!adminSelectedTranslation) await loadData();
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
      // Reset the validation flow flag
      setComingFromValidation(false);
      // Always load next translation after suggesting (whether from normal flow or after validation)
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

  // Admin: load a specific translation by ID (uses /api/translations/{id})
  const loadTranslationById = async (id) => {
    if (!id) return;
    setLoading(true);
    try {
      const res = await translationsAPI.getById(id);
      const t = res?.data || res;
      setCurrentTranslation(t);
      setAdminSelectedTranslation(true);
      resetForm();
      setSelectedSuggestion(null);
      // remove query param (optional) to avoid repeated auto-loads
      try { setSearchParams({}); } catch (e) { /* ignore if not available */ }
      toast.info(`Cargando traducción #${id}`);
    } catch (err) {
      console.error('Error cargando traducción por ID', err);
      toast.error(err.response?.data?.detail || 'No se pudo cargar la traducción');
    } finally {
      setLoading(false);
    }
  };

  const handleAdminLoadById = async () => {
    const id = parseInt(adminSearch, 10);
    if (!id) {
      toast.error('Ingresa un ID de traducción válido');
      return;
    }
    await loadTranslationById(id);
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
        {/* Admin quick-load: allow admins to load a translation by ID */}
        {user?.is_superuser && (
          <div className="mb-4 p-4 bg-white rounded-lg shadow-sm flex items-center gap-3">
            <label className="text-sm font-medium">Cargar traducción por ID:</label>
            <input
              type="text"
              value={adminSearch}
              onChange={(e) => setAdminSearch(e.target.value)}
              placeholder="ID de traducción"
              className="px-3 py-2 border rounded w-40"
            />
            <button onClick={handleAdminLoadById} className="px-3 py-2 bg-blue-600 text-white rounded">Cargar</button>
            <button onClick={() => { setAdminSearch(''); setAdminSelectedTranslation(false); loadData(); }} className="px-3 py-2 border rounded">Cancelar selección</button>
            {adminSelectedTranslation && currentTranslation && (
              <div className="ml-auto text-sm text-blue-700">Seleccionada: #{currentTranslation.id}</div>
            )}
          </div>
        )}

        {user && (
          <>
            <NavigationControls
              currentTranslation={currentTranslation}
              onNext={handleNextTranslation}
              onPrevious={handlePreviousTranslation}
              // disable suggest action when user already suggested
              onSuggest={() => setShowSuggestionModal(true)}
              loading={loading}
              disabled={hasUnsavedChanges()}
            />
            
            {/* Warning banner for unsaved changes */}
            {hasUnsavedChanges() && (
              <div className="mt-4 p-3 bg-amber-50 border-l-4 border-amber-400 rounded-r-md">
                <div className="flex items-start">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-amber-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm text-amber-800">
                      <strong className="font-medium">Tienes cambios sin guardar.</strong>
                      {' '}Los botones de navegación están deshabilitados. Por favor envía la validación o limpia el formulario para continuar.
                    </p>
                  </div>
                </div>
              </div>
            )}
          </>
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
        ) : (
          <>
            {!(currentTranslation.validation_count !== undefined && currentTranslation.validation_count >= 3) && (
              <div className="card mt-6">
                <div className="space-y-6">
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
                    <button
                      onClick={handleSubmitValidation}
                      disabled={!isFormValid() || submitting}
                      aria-disabled={!isFormValid() || submitting}
                      className="btn btn-primary flex-1 min-w-[200px] disabled:opacity-50 disabled:cursor-not-allowed disabled:bg-blue-400"
                    >
                      {submitting ? (
                        <div className="flex items-center justify-center">
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                          Enviando...
                        </div>
                      ) : 'Enviar validación'}
                    </button>
                    {(!isFormValid() && !submitting) && (
                      <p className="text-sm text-gray-500 mt-2">
                        Completa la clasificación (tipo de guaraní si aplica), la corrección (Correcta/Incorrecta) y las puntuaciones de fluidez y precisión para habilitar el botón.
                      </p>
                    )}
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      <SuggestionModal 
        isOpen={showSuggestionModal} 
        onClose={() => {
          setShowSuggestionModal(false);
          // If coming from post-validation flow, return to confirmation modal
          if (comingFromValidation) {
            setShowSuggestAfterValidationModal(true);
          }
        }} 
        onSubmit={handleSubmitSuggestion} 
        currentTranslation={currentTranslation} 
        isLoading={submitting} 
      />

      {/* Modal: Ask if user wants to suggest after validating */}
      {showSuggestAfterValidationModal && (
        <div className="fixed inset-0 z-40 flex items-center justify-center">
          <div className="absolute inset-0 bg-black opacity-40" onClick={async () => {
            setShowSuggestAfterValidationModal(false);
            setComingFromValidation(false);
            // Load next translation since validation was already saved
            await loadData();
          }} />
          <div className="bg-white rounded-lg shadow-lg max-w-md w-full mx-4 z-50">
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-2">✅ Validación enviada</h3>
              <p className="text-sm text-gray-700 mb-4">
                ¿Querés sugerir una traducción alternativa o mejorada para esta traducción que acabás de validar?
              </p>
              <div className="flex justify-end space-x-3">
                <button 
                  onClick={async () => {
                    setShowSuggestAfterValidationModal(false);
                    setComingFromValidation(false);
                    // Load next translation since validation was already saved
                    await loadData();
                  }} 
                  className="px-4 py-2 rounded-md border hover:bg-gray-50"
                >
                  No, continuar
                </button>
                <button 
                  onClick={() => {
                    setShowSuggestAfterValidationModal(false);
                    setShowSuggestionModal(true);
                  }} 
                  className="px-4 py-2 rounded-md bg-blue-600 text-white hover:bg-blue-700"
                >
                  Sí, sugerir traducción
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

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
 
