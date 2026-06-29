import { useEffect, useState } from 'react';

// Componentes
import Navbar from '../components/common/Navbar';
import CorrectnessButtons from '../components/translation/CorrectnessButtons';
import ScoreSelector from '../components/translation/ScoreSelector';
import NotesTextarea from '../components/translation/NotesTextarea';
import { validatorAPI } from '../services/api';

const VALIDATOR_TRANSLATION_STORAGE_KEY = 'validator_current_translation';

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
  const [showSuggestionsModal, setShowSuggestionsModal] = useState(false);

  const [suggestionFormData, setSuggestionFormData] = useState({
    suggestion_spanish: '',
    suggestion_guarani: '',
    reason: ''
  });

  const [formData, setFormData] = useState({
    correctness: '',
    fluency_score: null,
    accuracy_score: null,
    notes: ''
  });

  useEffect(() => {
    loadStoredOrFetchTranslation();
  }, []);

  const normalizeValidatorTranslation = (item) => {
    if (!item) return null;

    const translation = item.translation || item;
    const annotation = item.annotation || item;
    const translator = item.translator || {};

    return {
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

  const loadStoredOrFetchTranslation = async () => {
    try {
      const storedTranslation = localStorage.getItem(VALIDATOR_TRANSLATION_STORAGE_KEY);
      if (storedTranslation) {
        const parsedTranslation = JSON.parse(storedTranslation);
        setCurrentTranslation(parsedTranslation);
        setLoading(false);
        return;
      }
    } catch (error) {
      console.error('Error leyendo traducción guardada:', error);
      localStorage.removeItem(VALIDATOR_TRANSLATION_STORAGE_KEY);
    }

    await preloadValidatorTranslation();
  };

  const preloadValidatorTranslation = async () => {
    setLoading(true);
    try {
      const response = await validatorAPI.getRandomTranslations(1);
      const translation = normalizeValidatorTranslation(extractTranslationFromResponse(response.data));
      setCurrentTranslation(translation);
      if (translation) {
        localStorage.setItem(VALIDATOR_TRANSLATION_STORAGE_KEY, JSON.stringify(translation));
      }
    } catch (error) {
      console.error('Error precargando traducción para validar:', error);
      setCurrentTranslation(null);
    } finally {
      setLoading(false);
    }
  };

  const resetSuggestionForm = () => {
    setSuggestionFormData({ suggestion_spanish: '', suggestion_guarani: '', reason: '' });
  };

  const handleCorrectnessSelect = (correctness) => setFormData(prev => ({ ...prev, correctness }));
  const handleFluencySelect = (score) => setFormData(prev => ({ ...prev, fluency_score: score }));
  const handleAccuracySelect = (score) => setFormData(prev => ({ ...prev, accuracy_score: score }));
  const handleNotesChange = (notes) => setFormData(prev => ({ ...prev, notes }));

  const handleSuggestionSubmit = () => {
    alert('Sugerencia enviada (modo mockup)');
    setShowSuggestionsModal(false);
    resetSuggestionForm();
  };

  const insertCharInto = (fieldName, character) => {
    setSuggestionFormData(prev => {
      const currentText = prev[fieldName];
      return {
        ...prev,
        [fieldName]: currentText + character
      };
    });
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
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="bg-white rounded-lg shadow-md p-10 text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">No hay traducciones para validar</h2>
            <p className="text-gray-600">No se pudo cargar una traducción pendiente desde el endpoint.</p>
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

        {/* Translation Card */}
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
              disabled={false}
            />

            {['incorrect', 'regular', 'gn_more', 'es_more'].includes(formData.correctness) && (
              <div className="justify-center flex">
                <button
                  onClick={() => setShowSuggestionsModal(true)}
                  className="justify-center w-50 px-4 py-3 bg-teal-50 border border-teal-200 text-teal-800 rounded-lg hover:bg-teal-100 font-medium text-sm transition-colors"
                >
                  Sugerir una traducción
                </button>
              </div>
            )}

            <div className="grid md:grid-cols-2 gap-6">
              <ScoreSelector
                label="Puntuación de fluidez"
                selectedScore={formData.fluency_score}
                onSelect={handleFluencySelect}
                disabled={false}
              />
              <ScoreSelector
                label="Puntuación de precisión"
                selectedScore={formData.accuracy_score}
                onSelect={handleAccuracySelect}
                disabled={false}
              />
            </div>

            <NotesTextarea
              notes={formData.notes}
              onNotesChange={handleNotesChange}
              disabled={false}
            />

            <div className="border-t pt-6">
              <div className="flex gap-3 justify-end">
                <button
                  type="button"
                  className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 disabled:opacity-50 font-medium"
                >
                  Siguiente evaluación
                </button>
                <button
                  type="button"
                  className="px-6 py-2 bg-gradient-to-r from-teal-600 to-teal-700 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 font-medium"
                >
                  ✓ Enviar evaluación
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

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
              {/* Original Spanish */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Español (referencia)
                </label>
                <div className="p-3 bg-gray-100 rounded-lg text-gray-900 break-words">
                  {currentTranslation.question_es || currentTranslation.answer_es}
                </div>
              </div>

              {/* Original Guarani */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Guaraní (referencia)
                </label>
                <div className="p-3 bg-gray-100 rounded-lg text-gray-900 break-words">
                  {currentTranslation.question_gn || currentTranslation.answer_gn}
                </div>
              </div>

              {/* Premises 
              <div className="p-4 bg-teal-50 border border-teal-200 rounded-lg">
                <h4 className="text-sm font-semibold text-teal-900 mb-3">Premisas relacionadas</h4>
                <ul className="space-y-2 text-sm text-teal-800">
                  <li>• La precisión en la terminología es crítica para documentos administrativos.</li>
                  <li>• La fluidez debe mantener el contexto original.</li>
                  <li>• Considerar los dialectos locales del guaraní en uso.</li>
                </ul>
              </div>*/}

              {/* Suggestion Guarani */}
              <div>
                <label htmlFor="suggestion_guarani" className="block text-sm font-medium text-gray-700 mb-2">
                  Tu sugerencia de traducción en guaraní
                </label>

                {/* Special characters toolbar */}
                <div className="flex flex-wrap gap-2 mb-2 p-2 bg-gray-50 rounded-lg border border-gray-200">
                  {specialChars.map((item) => {
                    const isObj = typeof item === 'object' && item !== null;
                    const label = isObj ? item.label : item;
                    const value = isObj ? item.value : item;
                    return (
                      <button
                        key={label}
                        type="button"
                        onClick={() => insertCharInto('suggestion_guarani', value)}
                        className="text-xs px-2 py-1 bg-white border rounded hover:bg-gray-100 font-medium"
                        title={`Insertar ${label}`}
                      >
                        {label}
                      </button>
                    );
                  })}
                </div>

                <textarea
                  id="suggestion_guarani"
                  value={suggestionFormData.suggestion_guarani}
                  onChange={(e) => setSuggestionFormData(prev => ({ ...prev, suggestion_guarani: e.target.value }))}
                  placeholder="Escribe la traducción mejorada en guaraní aquí..."
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 resize-none"
                  rows={3}
                />
              </div>

              {/* Reason */}
              <div>
                <label htmlFor="reason" className="block text-sm font-medium text-gray-700 mb-2">
                  Razón de la sugerencia
                </label>
                <textarea
                  id="reason"
                  value={suggestionFormData.reason}
                  onChange={(e) => setSuggestionFormData(prev => ({ ...prev, reason: e.target.value }))}
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
