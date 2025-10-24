import { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { translationsAPI, validationsAPI, suggestionsAPI } from '../services/api';

// Componentes
import Navbar from '../components/common/Navbar';
import StatsBar from '../components/common/StatsBar';
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
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [showSuggestionModal, setShowSuggestionModal] = useState(false);
  
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
      // Cargar estadísticas y la siguiente traducción en paralelo
      const [statsResponse, translationResponse] = await Promise.all([
        user ? translationsAPI.getStats() : translationsAPI.getPublicStats(),
        user ? translationsAPI.getNext() : translationsAPI.getRandom()
      ]);

      setStats(statsResponse.data);
      setCurrentTranslation(translationResponse.data);
      
      // Reiniciar formulario
      resetForm();
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
      
      // Actualizar estadísticas
      const statsResponse = await translationsAPI.getStats();
      setStats(statsResponse.data);
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
      
      // Actualizar estadísticas
      const statsResponse = await translationsAPI.getStats();
      setStats(statsResponse.data);
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
      await validationsAPI.create({
        translation_id: currentTranslation.id,
        ...formData
      });

      // Cargar la siguiente traducción
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

  // Saltar traducción (cargar la siguiente sin validar)
  const handleSkip = async () => {
    await loadData();
  };

  // Enviar sugerencia
  const handleSubmitSuggestion = async (suggestionData) => {
    try {
      const response = await suggestionsAPI.create(suggestionData);
      
      // Mostrar mensaje de éxito
      alert('¡Sugerencia enviada con éxito! Tu propuesta ayudará a mejorar la calidad de las traducciones.');
      
      // Opcional: Cargar la siguiente traducción automáticamente
      const userWantsNext = confirm('¿Quieres continuar con la siguiente traducción?');
      if (userWantsNext) {
        await handleNextTranslation();
      }
      
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
          <StatsBar stats={stats} />
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
        <StatsBar stats={stats} />

        {/* Controles de navegación */}
        {user && (
          <NavigationControls
            currentTranslation={currentTranslation}
            onNext={handleNextTranslation}
            onPrevious={handlePreviousTranslation}
            loading={loading}
          />
        )}

        {/* Tarjeta de traducción */}
        <TranslationCard translation={currentTranslation} onReplace={(t) => {
          // When the card swaps to the paired translation, update parent state so navigation and form sync
          setCurrentTranslation(t);
          resetForm();
          // refresh stats
          translationsAPI.getStats().then(r => setStats(r.data)).catch(()=>{});
        }} />

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

              <button
                onClick={() => setShowSuggestionModal(true)}
                disabled={submitting}
                className="btn btn-secondary"
              >
                🔄 Sugerir nueva traducción
              </button>

              <button
                onClick={handleSkip}
                disabled={submitting}
                className="btn btn-secondary"
              >
                Omitir →
              </button>
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
    </div>
  );
};

export default ValidatorPage;
