import { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { translationsAPI, validationsAPI, suggestionsAPI } from '../services/api';

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
  // Autenticación
  const { user } = useAuth();

  // Estado
  const [currentTranslation, setCurrentTranslation] = useState(null);
  // Stats removed - not used anymore
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [showSuggestionModal, setShowSuggestionModal] = useState(false);
  const [showContinueModal, setShowContinueModal] = useState(false);
  const [selectedSuggestion, setSelectedSuggestion] = useState(null);
  
  // Estado del formulario
  const [formData, setFormData] = useState({
    correctness: '',
    fluency_score: null,
    accuracy_score: null,
    notes: ''
  });

  // Cargar datos iniciales
  useEffect(() => {
    if (user) {
      loadData();
    }
  }, [user]);

  const loadData = async () => {
    setLoading(true);
    try {
      // Try to fetch a translation; if the current user already suggested for it,
      // skip to the next one automatically. Limit attempts to avoid infinite loops.
      let attempts = 10;
      let response = null;

      if (!user) {
        response = await translationsAPI.getRandom();
        setCurrentTranslation(response.data);
        resetForm();
        return;
      }

      // For authenticated users, start with getNext
      response = await translationsAPI.getNext();

      while (attempts > 0) {
        const t = response.data;
        // If user has already suggested for this translation, fetch the next one
        if (t?.user_has_suggested) {
          try {
            response = await translationsAPI.getNextFrom(t.id);
          } catch (errNext) {
            // If no next available, stop and clear
            if (errNext.response?.status === 404) {
              setCurrentTranslation(null);
              return;
            }
            throw errNext;
          }
          attempts -= 1;
          continue;
        }

        // Found a translation the user hasn't suggested for
        setCurrentTranslation(t);
        resetForm();
        break;
      }

      if (attempts <= 0) {
        // Too many attempts, give up
        setCurrentTranslation(null);
      }
    } catch (error) {
      console.error('Error al cargar los datos:', error);
      if (error.response?.status === 404) {
        // No hay más traducciones
        setCurrentTranslation(null);
      }
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      correctness: '',
      fluency_score: null,
      accuracy_score: null,
      notes: ''
    });
  };

  // Funciones de navegación
  const handleNextTranslation = async () => {
    if (!user || !currentTranslation) return;
    
    setLoading(true);
    try {
      const response = await translationsAPI.getNextFrom(currentTranslation.id);
      setCurrentTranslation(response.data);
      resetForm();
      
  // No statistics displayed per user request
    } catch (error) {
      console.error('Error loading next translation:', error);
      if (error.response?.status === 404) {
        // No hay más traducciones, cargar la primera disponible
        try {
          const response = await translationsAPI.getNext();
          setCurrentTranslation(response.data);
          resetForm();
        } catch (nextError) {
          console.error('No more translations available:', nextError);
          setCurrentTranslation(null);
        }
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
      
  // No statistics displayed per user request
    } catch (error) {
      console.error('Error loading previous translation:', error);
    } finally {
      setLoading(false);
    }
  };

  const isFormValid = () => {
    return formData.correctness && 
           formData.fluency_score && 
           formData.accuracy_score;
  };

  // Manejar cambios del formulario
  const handleCorrectnessSelect = (correctness) => {
    setFormData(prev => ({ ...prev, correctness }));
  };

  const handleFluencySelect = (score) => {
    setFormData(prev => ({ ...prev, fluency_score: score }));
  };

  const handleAccuracySelect = (score) => {
    setFormData(prev => ({ ...prev, accuracy_score: score }));
  };

  const handleNotesChange = (notes) => {
    setFormData(prev => ({ ...prev, notes }));
  };

  // Enviar validación
  const handleSubmitValidation = async () => {
    if (!isFormValid() || !currentTranslation) return;

    setSubmitting(true);
    try {
      const payload = {
        translation_id: currentTranslation.id,
        ...formData
      };
      if (selectedSuggestion && selectedSuggestion.id) {
        payload.suggestion_id = selectedSuggestion.id;
      }

      await validationsAPI.create(payload);

      // Cargar la siguiente traducción
      // Clear selected suggestion after submitting
      setSelectedSuggestion(null);
      await loadData();
    } catch (error) {
      console.error('Error al enviar la validación:', error);
      if (error.response?.status === 400) {
        alert('Ya has validado esta traducción.');
        await loadData();
      } else {
        alert('Error al enviar la validación. Inténtalo de nuevo.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  // Nota: la acción de sugerir/continuar y la navegación se manejan desde los controles de navegación.

  // Enviar sugerencia
  const handleSubmitSuggestion = async (suggestionData) => {
    try {
      const response = await suggestionsAPI.create(suggestionData);

      // Mostrar mensaje de éxito
      alert('¡Sugerencia enviada con éxito! Tu propuesta ayudará a mejorar la calidad de las traducciones.');

      // Después de sugerir, cargar directamente la siguiente traducción
      await loadData();

    } catch (error) {
      console.error('Error al enviar la sugerencia:', error);
      
      if (error.response?.status === 400) {
        alert('Error en los datos de la sugerencia. Verifica que has proporcionado al menos una traducción.');
      } else if (error.response?.status === 404) {
        alert('La traducción no fue encontrada.');
      } else {
        alert('Error al enviar la sugerencia. Inténtalo de nuevo.');
      }
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-6xl mx-auto px-4 py-8">
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!currentTranslation) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-6xl mx-auto px-4 py-8">
          {/* StatsBar removed */}
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🎉</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              ¡Felicidades!
            </h2>
            <p className="text-gray-600">
              Has validado todas las traducciones disponibles.
            </p>
            <button 
              onClick={loadData}
              className="btn btn-primary mt-4"
            >
              Buscar nuevas traducciones
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <div className="max-w-6xl mx-auto px-4 py-8">
  {/* StatsBar removed */}

        {/* Controles de navegación */}
        {user && (
          <NavigationControls
            currentTranslation={currentTranslation}
            onNext={handleNextTranslation}
            onPrevious={handlePreviousTranslation}
            onSuggest={() => setShowSuggestionModal(true)}
            loading={loading}
          />
        )}

        {/* Tarjeta de traducción */}
        <TranslationCard translation={currentTranslation} onReplace={(t) => {
          // When the card swaps to the paired translation, update parent state so navigation and form sync
          setCurrentTranslation(t);
          resetForm();
          // stats are not fetched/displayed
        }} onValidateSuggestion={(s) => {
          // When a suggestion is selected for validation, set it in state and show a small banner
          setSelectedSuggestion(s);
        }} selectedSuggestion={selectedSuggestion} />

        {/* Formulario de validación (ahora siempre disponible). Si ya sugeriste, mostramos un aviso pero permitimos validar igualmente. */}
        <div className="card mt-6">
          <div className="space-y-6">
            {/* If the current translation already has 3+ validations, show a warning and disable submit */}
            {currentTranslation.validation_count >= 3 && (
              <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-100 text-yellow-800">
                <h3 className="text-lg font-medium">No disponible para validar</h3>
                <p className="text-sm text-yellow-800 mt-2">
                  Esta traducción ya tiene {currentTranslation.validation_count} validaciones en su dirección. No se pueden añadir más validaciones.
                </p>
              </div>
            )}
            {currentTranslation.user_has_suggested && (
              <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-100">
                <h3 className="text-lg font-medium">Has sugerido una traducción</h3>
                <p className="text-sm text-gray-600 mt-2">
                  Ya enviaste una sugerencia para esta traducción. Puedes editarla si lo deseas, pero esto no impide que puedas validar la traducción.
                </p>
                <div className="pt-3">
                  <button
                    onClick={() => setShowSuggestionModal(true)}
                    className="btn btn-secondary"
                  >
                    ✏️ Editar sugerencia
                  </button>
                </div>
              </div>
            )}

            {/* If a suggestion is selected for validation, show a small banner */}
            {selectedSuggestion && (
              <div className="p-4 bg-blue-50 rounded-lg border border-blue-100">
                <div className="flex items-start justify-between">
                  <div>
                    <h4 className="text-sm font-medium">Validando sugerencia</h4>
                    <div className="text-sm text-gray-700 mt-1">
                      {selectedSuggestion.suggested_guarani && <div><strong>Guaraní:</strong> {selectedSuggestion.suggested_guarani}</div>}
                      {selectedSuggestion.suggested_spanish && <div><strong>Español:</strong> {selectedSuggestion.suggested_spanish}</div>}
                    </div>
                  </div>
                  <div className="ml-4">
                    <button onClick={() => setSelectedSuggestion(null)} className="px-3 py-1 bg-white border rounded">Cancelar</button>
                  </div>
                </div>
              </div>
            )}

            {/* Corrección */}
            <CorrectnessButtons
              selectedCorrectness={formData.correctness}
              onSelect={handleCorrectnessSelect}
              disabled={submitting}
            />

            {/* Puntuaciones */}
            <div className="grid md:grid-cols-2 gap-6">
              <ScoreSelector
                label="Puntuación de fluidez"
                selectedScore={formData.fluency_score}
                onSelect={handleFluencySelect}
                disabled={submitting}
              />
              <ScoreSelector
                label="Puntuación de precisión"
                selectedScore={formData.accuracy_score}
                onSelect={handleAccuracySelect}
                disabled={submitting}
              />
            </div>

            {/* Notas */}
            <NotesTextarea
              notes={formData.notes}
              onNotesChange={handleNotesChange}
              disabled={submitting}
            />

            {/* Botones de acción */}
            <div className="flex flex-wrap gap-3 pt-4 border-t border-gray-200">
              <button
                onClick={handleSubmitValidation}
                disabled={!isFormValid() || submitting || (currentTranslation.validation_count >= 3)}
                className="btn btn-primary flex-1 min-w-[200px]"
              >
                {submitting ? (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Enviando...
                  </div>
                ) : (
                  'Enviar validación'
                )}
              </button>

              {/* Suggestion handled in the navigation controls now; removed inline "Omitir" button per request */}
            </div>
          </div>
        </div>
      </div>

      {/* Modal de sugerencia */}
      <SuggestionModal
        isOpen={showSuggestionModal}
        onClose={() => setShowSuggestionModal(false)}
        onSubmit={handleSubmitSuggestion}
        currentTranslation={currentTranslation}
        isLoading={submitting}
      />

      {/* Modal: continuar después de enviar sugerencia */}
      {showContinueModal && (
        <div className="fixed inset-0 z-40 flex items-center justify-center">
          <div className="absolute inset-0 bg-black opacity-40" onClick={() => setShowContinueModal(false)} />
          <div className="bg-white rounded-lg shadow-lg max-w-md w-full mx-4 z-50">
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-2">Continuar</h3>
              <p className="text-sm text-gray-700 mb-4">¿Quieres continuar con la siguiente traducción?</p>
              <div className="flex justify-end space-x-3">
                <button onClick={() => setShowContinueModal(false)} className="px-4 py-2 rounded-md border">No</button>
                <button
                  onClick={async () => {
                    setShowContinueModal(false);
                    await handleNextTranslation();
                  }}
                  className="px-4 py-2 rounded-md bg-blue-600 text-white"
                >
                  Sí, continuar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ValidatorPage;
