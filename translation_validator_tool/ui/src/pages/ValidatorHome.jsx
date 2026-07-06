import { useEffect, useState } from 'react';

// Componentes
import Navbar from '../components/common/Navbar';
import CorrectnessButtons from '../components/translation/CorrectnessButtons';
import ScoreSelector from '../components/translation/ScoreSelector';
import NotesTextarea from '../components/translation/NotesTextarea';
import { annotationsAPI, validatorAPI } from '../services/api';
import { toast } from 'react-toastify';

// Caracteres especiales Guaraní
const specialChars = [
  'ã','ẽ','ĩ','õ','ũ','ỹ',
  'á','é','í','ó','ú','ý',
  'g̃','G̃','ñ','Ñ',
  { label: 'pusó ( \' )', value: "'" }
];

const ValidatorHome = () => {
  const [currentTranslation, setCurrentTranslation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [assigningNext, setAssigningNext] = useState(false);
  const [assigningNextMessage, setAssigningNextMessage] = useState('');
  const [showSuggestionsModal, setShowSuggestionsModal] = useState(false);
  const [showSubmitConfirmModal, setShowSubmitConfirmModal] = useState(false);
  const [showSkipConfirmModal, setShowSkipConfirmModal] = useState(false);
  const [hasSubmittedSuggestion, setHasSubmittedSuggestion] = useState(false);
  const [pendingSuggestionData, setPendingSuggestionData] = useState(null);

  const [suggestionFormData, setSuggestionFormData] = useState({
    suggested_question_gn: '',
    suggested_answer_gn: '',
    reason: ''
  });

  const [formData, setFormData] = useState({
    correctness: '',
    fluency_score: null,
    accuracy_score: null,
    notes: ''
  });

  useEffect(() => {
    preloadValidatorTranslation();
  }, []);

  const normalizeValidatorTranslation = (item) => {
    if (!item) return null;

    const translation = item.translation || item;
    const annotation = item.annotation || item;
    const translator = item.translator || {};

    return {
      validation_id: item.validation_id,
      id: translation.id || item.id,
      annotation_id: translation.annotation_id || annotation.id,
      question_es: annotation.question_es || '',
      answer_es: annotation.answer_es || '',
      question_gn: translation.question_gn || '',
      answer_gn: translation.answer_gn || '',
      source: annotation.source || '',
      translator_name: translator.nombre_completo || translator.username || '',
      translator_id: translator.user_id || translation.user_id,
      validation_count: item.validation_count || 0,
      user_has_validated: item.user_has_validated || false
    };
  };

  const extractTranslationFromResponse = (data) => {
    if (Array.isArray(data)) return data[0] || null;
    if (Array.isArray(data?.items)) return data.items[0] || null;
    return data || null;
  };

  const resetValidationForm = () => {
    setFormData({
      correctness: '',
      fluency_score: null,
      accuracy_score: null,
      notes: ''
    });
    setHasSubmittedSuggestion(false);
    setPendingSuggestionData(null);
  };

  const preloadValidatorTranslation = async () => {
    setLoading(true);
    try {
      const response = await validatorAPI.getRandomTranslations(1);
      const translation = normalizeValidatorTranslation(extractTranslationFromResponse(response.data));
      setCurrentTranslation(translation);
      resetValidationForm();
    } catch (error) {
      console.error('Error precargando traducción para validar:', error);
      setCurrentTranslation(null);
    } finally {
      setLoading(false);
    }
  };

  const resetSuggestionForm = () => {
    setSuggestionFormData({ suggested_question_gn: '', suggested_answer_gn: '', reason: '' });
  };

  const handleCorrectnessSelect = (correctness) => setFormData(prev => ({ ...prev, correctness }));
  const handleFluencySelect = (score) => setFormData(prev => ({ ...prev, fluency_score: score }));
  const handleAccuracySelect = (score) => setFormData(prev => ({ ...prev, accuracy_score: score }));
  const handleNotesChange = (notes) => setFormData(prev => ({ ...prev, notes }));
  const handleSuggestionFieldChange = (fieldName, value) => {
    setSuggestionFormData(prev => ({ ...prev, [fieldName]: value }));
    setHasSubmittedSuggestion(false);
    setPendingSuggestionData(null);
  };

  const handleSuggestionSubmit = () => {
    const suggestedQuestion = suggestionFormData.suggested_question_gn.trim();
    const suggestedAnswer = suggestionFormData.suggested_answer_gn.trim();
    const reason = suggestionFormData.reason.trim();

    if (!suggestedQuestion && !suggestedAnswer) {
      toast.error('Completa al menos una sugerencia antes de continuar.');
      return;
    }
    if (!reason) {
      toast.error('Completa la razón antes de continuar.');
      return;
    }

    setPendingSuggestionData({
      translation_id: currentTranslation.id,
      part_type: suggestedQuestion && suggestedAnswer ? 'both' : (suggestedQuestion ? 'question' : 'answer'),
      suggested_question_gn: suggestedQuestion || null,
      suggested_answer_gn: suggestedAnswer || null,
      reason
    });
    toast.success('Sugerencia preparada. Se enviará junto con la evaluación.');
    setHasSubmittedSuggestion(true);
    setShowSuggestionsModal(false);
  };

  const validationAverage = formData.fluency_score !== null && formData.accuracy_score !== null
    ? (formData.fluency_score + formData.accuracy_score) / 2
    : null;
  const requiresSuggestion = validationAverage !== null && validationAverage < 3;
  const shouldShowSuggestionButton = requiresSuggestion || ['incorrect', 'regular', 'gn_more', 'es_more'].includes(formData.correctness);

  const applyValidatorResponse = (data) => {
    const translation = normalizeValidatorTranslation(extractTranslationFromResponse(data));
    setCurrentTranslation(translation);
    resetValidationForm();
    resetSuggestionForm();
    setShowSuggestionsModal(false);
    setShowSubmitConfirmModal(false);
    setShowSkipConfirmModal(false);
    setAssigningNextMessage('');
  };

  const waitForNextAssignment = () => new Promise(resolve => setTimeout(resolve, 700));
  const limitReachedMessage = 'Lo sentimos, la traducción ya fue validada 3 veces. Te asignaremos una nueva.';

  const isValidationLimitError = (error) => {
    const detail = error?.response?.data?.detail;
    const message = Array.isArray(detail)
      ? detail.map(item => item?.msg || item?.detail || JSON.stringify(item)).join(' ')
      : String(detail || error?.response?.data?.message || error?.message || '');
    return /traducci[oó]n/i.test(message) && /3/.test(message) && /validaci/i.test(message);
  };

  const canRecoverByAssigningNext = (error) => {
    const status = error?.response?.status;
    return isValidationLimitError(error) || [400, 404, 409].includes(status);
  };

  const assignNextAfterLimitReached = async () => {
    toast.info(limitReachedMessage);
    setAssigningNextMessage(limitReachedMessage);
    setAssigningNext(true);
    await waitForNextAssignment();
    const response = await validatorAPI.skipCurrent();
    applyValidatorResponse(response.data);
  };

  const submitPendingSuggestion = async () => {
    if (!pendingSuggestionData) return null;

    const response = await annotationsAPI.suggest(currentTranslation.annotation_id, pendingSuggestionData);
    setPendingSuggestionData(null);
    return response?.data?.id || null;
  };

  const handleNextEvaluation = async () => {
    setShowSkipConfirmModal(true);
  };

  const confirmNextEvaluation = async () => {
    setShowSkipConfirmModal(false);
    setSubmitting(true);
    try {
      const response = await validatorAPI.skipCurrent();
      setAssigningNextMessage('Validación omitida. Se asignará otra traducción.');
      setAssigningNext(true);
      await waitForNextAssignment();
      applyValidatorResponse(response.data);
    } catch (error) {
      console.error('Error al saltar la validación actual:', error);
      toast.error('No se pudo cargar la siguiente evaluación.');
    } finally {
      setAssigningNext(false);
      setSubmitting(false);
    }
  };

  const handleSubmitValidation = async () => {
    if (!formData.correctness || !formData.fluency_score || !formData.accuracy_score) {
      toast.error('Selecciona corrección, fluidez y precisión antes de enviar.');
      return;
    }

    if (requiresSuggestion && !hasSubmittedSuggestion) {
      toast.error('La sugerencia es obligatoria cuando el promedio de fluidez y precisión es menor a 3.');
      return;
    }

    setShowSubmitConfirmModal(true);
  };

  const confirmSubmitValidation = async () => {
    setShowSubmitConfirmModal(false);
    setSubmitting(true);
    try {
      let suggestionId = null;
      if (hasSubmittedSuggestion) {
        suggestionId = await submitPendingSuggestion();
      }

      const payload = {
        correctness: formData.correctness,
        fluency_score: formData.fluency_score,
        accuracy_score: formData.accuracy_score,
        notes: formData.notes || null
      };
      if (suggestionId) payload.suggestion_id = suggestionId;

      let response;
      try {
        response = await validatorAPI.completeCurrent(payload);
      } catch (completeError) {
        if (canRecoverByAssigningNext(completeError)) {
          await assignNextAfterLimitReached();
          return;
        }
        throw completeError;
      }

      const limitReached = response.data?.replaced_due_to_limit;
      setAssigningNextMessage(limitReached ? limitReachedMessage : 'Validación enviada correctamente.');
      if (limitReached) toast.info(limitReachedMessage);
      setAssigningNext(true);
      await waitForNextAssignment();
      applyValidatorResponse(response.data);
    } catch (error) {
      console.error('Error al enviar la validación:', error);
      if (canRecoverByAssigningNext(error)) {
        try {
          await assignNextAfterLimitReached();
        } catch (assignError) {
          console.error('Error al asignar una nueva validación:', assignError);
          toast.error('No se pudo asignar una nueva evaluación.');
        }
      } else {
        toast.error('No se pudo enviar la evaluación.');
      }
    } finally {
      setAssigningNext(false);
      setSubmitting(false);
    }
  };

  const insertCharInto = (fieldName, character) => {
    setSuggestionFormData(prev => {
      const currentText = prev[fieldName];
      return {
        ...prev,
        [fieldName]: currentText + character
      };
    });
    setHasSubmittedSuggestion(false);
    setPendingSuggestionData(null);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="bg-white rounded-lg shadow-md p-10 flex items-center justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-600"></div>
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
          <div className="text-center py-16">
            <div className="text-6xl mb-4">🎉</div>
            <h2 className="text-3xl font-bold text-gray-900 mb-4">¡Felicidades!</h2>
            <p className="text-xl text-gray-600 mb-2">No tienes validaciones pendientes</p>

            <div className="mt-8 p-6 bg-teal-50 rounded-lg border border-teal-200 max-w-md mx-auto">
              <p className="text-teal-800">
                <strong>No hay más traducciones disponibles para validar.</strong>
              </p>
              <p className="text-teal-700 text-sm mt-2">
                Vuelve más tarde para revisar nuevas validaciones.
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <div className="bg-gradient-to-r from-teal-600 to-teal-700 rounded-2xl shadow-lg p-8 text-white">
            <h1 className="text-3xl font-bold">Validaciones pendientes</h1>
            <p className="mt-2 text-teal-100">
              Revisa traducciones en español y guaraní, califica su calidad y sugiere mejoras cuando sea necesario.
            </p>
          </div>
        </div>

        {assigningNext ? (
          <div className="bg-white rounded-lg shadow-md p-12 flex flex-col items-center justify-center min-h-[360px] text-center">
            <div className="h-14 w-14 animate-spin rounded-full border-4 border-teal-100 border-t-teal-700"></div>
            <p className="mt-6 text-base font-semibold text-gray-900">
              Asignando siguiente traducción...
            </p>
            {assigningNextMessage && (
              <p className="mt-2 text-sm text-gray-600">
                {assigningNextMessage}
              </p>
            )}
          </div>
        ) : (
        <div className="bg-white rounded-lg shadow-md p-6">
        {/* Translation Info */}
        <div className="mb-6 p-4 bg-teal-50 border border-teal-100 rounded-lg">
          <div>
            <h3 className="text-sm font-semibold text-teal-800">
              Traducción a validar
            </h3>
            <p className="text-lg font-bold text-gray-900 mt-1">
              ID: #{currentTranslation.id}
            </p>
          </div>
        </div>


          {/* Original and Translation Sections */}
          <div className="grid md:grid-cols-2 gap-6 mb-6">
            {/* Spanish (Original) */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-800">Español (texto original)</h3>
                <span className="text-xs px-2 py-1 rounded-full bg-gray-100 text-gray-700 border border-gray-200">Original</span>
              </div>
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 min-h-[120px] shadow-sm">
                {currentTranslation.question_es && (
                  <div className="mb-4">
                    <p className="text-sm font-semibold text-gray-700 mb-1">Pregunta</p>
                    <p className="text-gray-900 leading-relaxed">{currentTranslation.question_es}</p>
                  </div>
                )}
                {currentTranslation.answer_es && (
                  <div>
                    <p className="text-sm font-semibold text-gray-700 mb-1">Respuesta</p>
                    <p className="text-gray-900 leading-relaxed">{currentTranslation.answer_es}</p>
                  </div>
                )}
              </div>
            </div>

            {/* Guarani Translation */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-800">Guaraní (traducción)</h3>
                <span className="text-xs px-2 py-1 rounded-full bg-gray-100 text-gray-700 border border-gray-200">Traducción</span>
              </div>
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 min-h-[120px] shadow-sm">
                {currentTranslation.question_gn && (
                  <div className="mb-4">
                    <p className="text-sm font-semibold text-gray-700 mb-1">Pregunta</p>
                    <p className="text-gray-900 leading-relaxed">{currentTranslation.question_gn}</p>
                  </div>
                )}
                {currentTranslation.answer_gn && (
                  <div>
                    <p className="text-sm font-semibold text-gray-700 mb-1">Respuesta</p>
                    <p className="text-gray-900 leading-relaxed">{currentTranslation.answer_gn}</p>
                  </div>
                )}
              </div>
            </div>
          </div>

      
          {/* Validation Form */}
          <div className="space-y-6 border-t border-gray-200 pt-6">
            <CorrectnessButtons
              selectedCorrectness={formData.correctness}
              onSelect={handleCorrectnessSelect}
              disabled={submitting}
            />

            {shouldShowSuggestionButton && (
              <div className="justify-center flex">
                <button
                  onClick={() => setShowSuggestionsModal(true)}
                  className="justify-center w-50 px-4 py-3 bg-teal-50 border border-teal-200 text-teal-800 rounded-lg hover:bg-teal-100 font-medium text-sm transition-colors"
                >
                  {requiresSuggestion && !hasSubmittedSuggestion ? 'Sugerir una traducción (obligatorio)' : 'Sugerir una traducción'}
                </button>
              </div>
            )}

            {requiresSuggestion && hasSubmittedSuggestion && (
              <p className="text-center text-sm font-medium text-teal-700">
                Sugerencia registrada para esta evaluación.
              </p>
            )}

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

            <NotesTextarea
              notes={formData.notes}
              onNotesChange={handleNotesChange}
              disabled={submitting}
            />

            <div className="border-t pt-6">
              <div className="flex gap-3 justify-end">
                <button
                  type="button"
                  onClick={handleNextEvaluation}
                  disabled={submitting}
                  className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 disabled:opacity-50 font-medium"
                >
                  Siguiente evaluación
                </button>
                <button
                  type="button"
                  onClick={handleSubmitValidation}
                  disabled={submitting}
                  className="px-6 py-2 bg-gradient-to-r from-teal-600 to-teal-700 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 font-medium"
                >
                  ✓ Enviar evaluación
                </button>
              </div>
            </div>
          </div>
        </div>
        )}
      </div>

      {/* Submit Confirmation Modal */}
      {showSubmitConfirmModal && (
        <div className="fixed inset-0 z-60 flex items-center justify-center">
          <div className="absolute inset-0 bg-black opacity-40" onClick={() => !submitting && setShowSubmitConfirmModal(false)} />
          <div className="bg-white rounded-lg shadow-lg max-w-md w-full mx-4 z-50 p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">¿Enviar evaluación?</h3>
            <p className="text-gray-600 mb-2">
              Estás a punto de enviar tu evaluación para esta traducción.
            </p>
            <p className="text-gray-600 mb-6">
              Una vez enviada, se registrará tu validación y se te asignará otra traducción si hay disponibles.
            </p>

            <div className="flex gap-3 justify-end">
              <button
                type="button"
                onClick={() => setShowSubmitConfirmModal(false)}
                disabled={submitting}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 disabled:opacity-50 font-medium"
              >
                Cancelar
              </button>
              <button
                type="button"
                onClick={confirmSubmitValidation}
                disabled={submitting}
                className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 disabled:opacity-50 font-medium"
              >
                {submitting ? 'Enviando...' : 'Sí, enviar evaluación'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Skip Confirmation Modal */}
      {showSkipConfirmModal && (
        <div className="fixed inset-0 z-60 flex items-center justify-center">
          <div className="absolute inset-0 bg-black opacity-40" onClick={() => !submitting && setShowSkipConfirmModal(false)} />
          <div className="bg-white rounded-lg shadow-lg max-w-md w-full mx-4 z-50 p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">¿Omitir esta validación?</h3>
            <p className="text-gray-600 mb-2">
              Estás a punto de omitir esta traducción.
            </p>
            <p className="text-gray-600 mb-6">
              Se te desasignará esta validación y se te asignará otra traducción aleatoriamente para validar.
            </p>

            <div className="flex gap-3 justify-end">
              <button
                type="button"
                onClick={() => setShowSkipConfirmModal(false)}
                disabled={submitting}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 disabled:opacity-50 font-medium"
              >
                Cancelar
              </button>
              <button
                type="button"
                onClick={confirmNextEvaluation}
                disabled={submitting}
                className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 disabled:opacity-50 font-medium"
              >
                {submitting ? 'Asignando...' : 'Sí, omitir y asignar otra'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Suggestions Modal */}
      {showSuggestionsModal && (
        <div className="fixed inset-0 z-60 flex items-center justify-center">
          <div className="absolute inset-0 bg-black opacity-40" onClick={() => setShowSuggestionsModal(false)} />
          <div className="bg-white rounded-lg shadow-lg max-w-4xl w-full mx-4 z-50 max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900">Sugerir una mejora</h3>
              <p className="text-sm text-gray-600 mt-1">Propón una traducción alternativa o mejorada</p>
            </div>

            <div className="p-6 space-y-6">
              {currentTranslation.question_es && (
                <div className="mb-8">
                  <h4 className="text-lg font-semibold text-gray-800 mb-4">Pregunta</h4>

                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Pregunta (Español)
                    </label>
                    <div className="p-3 bg-gray-100 rounded-lg text-gray-900 break-words">
                      {currentTranslation.question_es}
                    </div>
                  </div>

                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Traducción actual al Guaraní
                    </label>
                    <div className="p-3 bg-gray-100 rounded-lg text-gray-900 break-words">
                      {currentTranslation.question_gn || 'Sin traducción de pregunta'}
                    </div>
                  </div>

                  <div>
                    <label htmlFor="suggested_question_gn" className="block text-sm font-medium text-gray-700 mb-2">
                      Sugerencia para la pregunta en Guaraní
                    </label>
                    <div className="flex flex-wrap gap-2 mb-2 p-2 bg-gray-50 rounded-lg border border-gray-200">
                      {specialChars.map((item) => {
                        const isObj = typeof item === 'object' && item !== null;
                        const label = isObj ? item.label : item;
                        const value = isObj ? item.value : item;
                        return (
                          <button
                            key={`question-${label}`}
                            type="button"
                            onClick={() => insertCharInto('suggested_question_gn', value)}
                            className="text-xs px-2 py-1 bg-white border rounded hover:bg-gray-100 font-medium"
                            title={`Insertar ${label}`}
                          >
                            {label}
                          </button>
                        );
                      })}
                    </div>
                    <textarea
                      id="suggested_question_gn"
                      value={suggestionFormData.suggested_question_gn}
                      onChange={(e) => handleSuggestionFieldChange('suggested_question_gn', e.target.value)}
                      placeholder="Escribe una mejora para la pregunta en guaraní..."
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 resize-none"
                      rows={4}
                    />
                  </div>
                </div>
              )}

              {currentTranslation.answer_es && (
                <div className="mb-8 border-t pt-8">
                  <h4 className="text-lg font-semibold text-gray-800 mb-4">Respuesta</h4>

                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Respuesta (Español)
                    </label>
                    <div className="p-3 bg-gray-100 rounded-lg text-gray-900 break-words">
                      {currentTranslation.answer_es}
                    </div>
                  </div>

                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Traducción actual al Guaraní
                    </label>
                    <div className="p-3 bg-gray-100 rounded-lg text-gray-900 break-words">
                      {currentTranslation.answer_gn || 'Sin traducción de respuesta'}
                    </div>
                  </div>

                  <div>
                    <label htmlFor="suggested_answer_gn" className="block text-sm font-medium text-gray-700 mb-2">
                      Sugerencia para la respuesta en Guaraní
                    </label>
                    <div className="flex flex-wrap gap-2 mb-2 p-2 bg-gray-50 rounded-lg border border-gray-200">
                      {specialChars.map((item) => {
                        const isObj = typeof item === 'object' && item !== null;
                        const label = isObj ? item.label : item;
                        const value = isObj ? item.value : item;
                        return (
                          <button
                            key={`answer-${label}`}
                            type="button"
                            onClick={() => insertCharInto('suggested_answer_gn', value)}
                            className="text-xs px-2 py-1 bg-white border rounded hover:bg-gray-100 font-medium"
                            title={`Insertar ${label}`}
                          >
                            {label}
                          </button>
                        );
                      })}
                    </div>
                    <textarea
                      id="suggested_answer_gn"
                      value={suggestionFormData.suggested_answer_gn}
                      onChange={(e) => handleSuggestionFieldChange('suggested_answer_gn', e.target.value)}
                      placeholder="Escribe una mejora para la respuesta en guaraní..."
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 resize-none"
                      rows={4}
                    />
                  </div>
                </div>
              )}

              {/* Reason */}
              <div>
                <label htmlFor="reason" className="block text-sm font-medium text-gray-700 mb-2">
                  Razón de la sugerencia
                </label>
                <textarea
                  id="reason"
                  value={suggestionFormData.reason}
                  onChange={(e) => handleSuggestionFieldChange('reason', e.target.value)}
                  placeholder="Explica por qué sugieres esta mejora..."
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 resize-none"
                  rows={3}
                />
              </div>

              {/* Buttons */}
              <div className="flex gap-3 pt-4 border-t border-gray-200">
                <button
                  onClick={() => {
                    setShowSuggestionsModal(false);
                    resetSuggestionForm();
                  }}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium"
                >
                  Cancelar
                </button>
                <button
                  onClick={handleSuggestionSubmit}
                  className="flex-1 px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 font-medium"
                >
                  Sugerir
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ValidatorHome;
