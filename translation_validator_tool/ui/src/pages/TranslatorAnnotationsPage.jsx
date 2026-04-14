import { useState, useEffect, useRef } from 'react';
import { useAuth } from '../hooks/useAuth';
import { annotationsAPI } from '../services/api';
import { toast } from 'react-toastify';
import Navbar from '../components/common/Navbar';

const TranslatorAnnotationsPage = () => {
  const { user } = useAuth();
  const [currentAnnotation, setCurrentAnnotation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [showConfirmModal, setShowConfirmModal] = useState(false);

  // Form state para las traducciones
  const [formData, setFormData] = useState({
    question_gn: '',
    answer_gn: ''
  });

  // Almacenamiento local (no sincronizado con servidor)
  const [savedData, setSavedData] = useState({
    question_gn: '',
    answer_gn: ''
  });

  // Índice para navegación
  const [allAnnotations, setAllAnnotations] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);

  // Caracteres especiales guaraní
  const specialChars = [
    'ã','ẽ','ĩ','õ','ũ','ỹ',
    'á','é','í','ó','ú','ý',
    'g̃','G̃','ñ','Ñ',
    { label: 'pusó ( \' )', value: "'" }
  ];

  // Refs para insertar caracteres especiales
  const questionGnRef = useRef(null);
  const answerGnRef = useRef(null);

  useEffect(() => {
    if (user) {
      loadAnnotations();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]);

  const loadAnnotations = async () => {
    setLoading(true);
    try {
      // Usar el nuevo endpoint para obtener solo las anotaciones asignadas al usuario actual
      const res = await annotationsAPI.getMyAssignments();
      const annotationsData = res?.data?.items || res?.data || [];
      console.log('DEBUG: annotationsData from API:', annotationsData);
      
      if (annotationsData && annotationsData.length > 0) {
        // Las anotaciones ya vienen completas del backend
        // Solo verificar si el usuario ya tradujo cada una
        const annotationsWithDetails = await Promise.all(
          annotationsData.map(async (ann) => {
            try {
              // Obtener si el usuario ya tradujo esta anotación
              let existingTranslation = null;
              try {
                const translRes = await annotationsAPI.getTranslationByUser(ann.id, user.id);
                existingTranslation = translRes?.data || null;
                console.log(`DEBUG: user translation for ${ann.id}:`, existingTranslation);
              } catch (tErr) {
                // If 404, user hasn't translated yet - treat as no translation.
                if (tErr?.response?.status === 404) {
                  console.log(`DEBUG: no translation for ${ann.id} (404 - expected)`);
                  existingTranslation = null;
                } else {
                  console.error(`Error fetching translation for annotation ${ann.id}:`, tErr);
                  existingTranslation = null;
                }
              }

              return {
                ...ann,
                existing_translation: existingTranslation
              };
            } catch (err) {
              console.error(`Error loading annotation ${ann.id}:`, err);
              return null;
            }
          })
        );
        
        console.log('DEBUG: annotationsWithDetails:', annotationsWithDetails);
        
        // Filtrar anotaciones válidas (mostrar todo lo asignado al usuario; no excluimos las ya traducidas)
        const validAnnotations = annotationsWithDetails
          .filter(a => a !== null);
        
        console.log('DEBUG: validAnnotations after filter:', validAnnotations);
        
        if (validAnnotations.length > 0) {
          setAllAnnotations(validAnnotations);
          setCurrentIndex(0);
          setCurrentAnnotation(validAnnotations[0]);
          resetForm();
        } else {
          console.log('DEBUG: No valid annotations found');
          setCurrentAnnotation(null);
          setAllAnnotations([]);
        }
      } else {
        console.log('DEBUG: No assignments found');
        setCurrentAnnotation(null);
        setAllAnnotations([]);
      }
    } catch (err) {
      console.error('Error loading annotations:', err);
      toast.error('Error al cargar anotaciones asignadas');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    // Limpiar completamente el formulario
    setFormData({
      question_gn: '',
      answer_gn: ''
    });
  };

  const insertCharInto = (ref, fieldName, character) => {
    const el = ref.current;
    if (!el) return;

    const start = el.selectionStart ?? el.value.length;
    const end = el.selectionEnd ?? el.value.length;
    const before = el.value.slice(0, start);
    const after = el.value.slice(end);
    const newVal = before + character + after;

    setFormData(prev => ({
      ...prev,
      [fieldName]: newVal
    }));

    el.value = newVal;
    const pos = start + character.length;
    el.focus();
    el.setSelectionRange(pos, pos);
  };

  const handleTextChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmitTranslation = async (e) => {
    e.preventDefault();

    if (!currentAnnotation || (!formData.question_gn.trim() && !formData.answer_gn.trim())) {
      toast.error('Por favor ingresa al menos una traducción');
      return;
    }

    setSubmitting(true);
    try {
      const payload = {
        question_gn: formData.question_gn.trim() || null,
        answer_gn: formData.answer_gn.trim() || null
      };

      await annotationsAPI.update(currentAnnotation.id, payload);
      toast.success('Traducción guardada correctamente');
      
      resetForm();
      await loadAnnotations();
    } catch (err) {
      console.error('Error saving translation:', err);
      toast.error(err.response?.data?.detail || 'Error al guardar traducción');
    } finally {
      setSubmitting(false);
    }
  };

  const handleSkip = async () => {
    resetForm();
    await loadNextAnnotation();
  };

  const handlePrevious = async () => {
    setLoading(true);
    try {
      // Cargar anotación anterior (implementar lógica de navegación si es necesario)
      // Por ahora simplemente recarga
      await loadAnnotations();
    } finally {
      setLoading(false);
    }
  };

  const handleIgnore = async () => {
    if (!currentAnnotation) return;
    
    setSubmitting(true);
    try {
      // Desasignar al usuario de esta anotación
      await annotationsAPI.unassignUser(currentAnnotation.id, user.id);
      toast.info('Anotación ignorada y desasignada');
      
      // Remover la anotación actual del buffer
      const updatedAnnotations = allAnnotations.filter((_, idx) => idx !== currentIndex);
      
      if (updatedAnnotations.length > 0) {
        setAllAnnotations(updatedAnnotations);
        let newIndex = currentIndex;
        if (currentIndex >= updatedAnnotations.length) {
          newIndex = updatedAnnotations.length - 1;
        }
        setCurrentIndex(newIndex);
        setCurrentAnnotation(updatedAnnotations[newIndex]);
        setSavedData({ question_gn: '', answer_gn: '' });
        resetForm();
      } else {
        setCurrentIndex(0);
        setCurrentAnnotation(null);
        setAllAnnotations([]);
      }
    } catch (err) {
      console.error('Error ignoring annotation:', err);
      toast.error('Error al ignorar anotación');
    } finally {
      setSubmitting(false);
    }
  };

  const handleSendTranslation = async () => {
    if (!currentAnnotation) {
      toast.error('Error: no hay anotación cargada');
      return;
    }

    // Determinar qué campos fuente existen
    const hasQuestion = !!currentAnnotation.question_es;
    const hasAnswer = !!currentAnnotation.answer_es;

    // Validar que se completen TODOS los campos que tienen fuente
    if (hasQuestion && !formData.question_gn.trim()) {
      toast.error('La pregunta es obligatoria');
      return;
    }
    if (hasAnswer && !formData.answer_gn.trim()) {
      toast.error('La respuesta es obligatoria');
      return;
    }

    // Función de validación de longitud
    const validateLengthRatio = (sourceText, translatedText) => {
      const s = sourceText.trim().length;
      const t = translatedText.trim().length;
      if (s === 0) return true;
      const min = Math.ceil(s * 0.5);
      const max = Math.floor(s * 1.7);
      return { valid: t >= min && t <= max, min, max };
    };

    // Validar longitud de la pregunta si aplicable
    if (hasQuestion && formData.question_gn.trim()) {
      const result = validateLengthRatio(currentAnnotation.question_es, formData.question_gn);
      if (!result.valid) {
        toast.error(`En la pregunta la longitud es inválida. El texto traducido es demasiado corto o demasiado largo.`);
        return;
      }
    }

    // Validar longitud de la respuesta si aplicable
    if (hasAnswer && formData.answer_gn.trim()) {
      const result = validateLengthRatio(currentAnnotation.answer_es, formData.answer_gn);
      if (!result.valid) {
        toast.error(`En la respuesta la longitud es inválida. El texto traducido es demasiado corto o demasiado largo.`);
        return;
      }
    }

    // Abrir modal de confirmación
    setShowConfirmModal(true);
  };

  const confirmSendTranslation = async () => {
    setShowConfirmModal(false);
    setSubmitting(true);
    try {
      const payload = {
        question_gn: formData.question_gn.trim() || null,
        answer_gn: formData.answer_gn.trim() || null
      };

      // Verificar si ya existen 3 traducciones para esta anotación
      try {
        const translationsRes = await annotationsAPI.getTranslations(currentAnnotation.id);
        const translationsList = translationsRes?.data?.items || translationsRes?.data || [];
        
        if (translationsList.length >= 3) {
          // Desasignar al usuario y remover la anotación del buffer
          try {
            await annotationsAPI.unassignUser(currentAnnotation.id, user.id);
            toast.info('La anotación ya tiene 3 traducciones; te hemos desasignado.');
          } catch (uErr) {
            console.error('Error al desasignar:', uErr);
            toast.error('No se pudo desasignar la anotación.');
          }

          // Remover la anotación actual del buffer
          const updatedAnnotations = allAnnotations.filter((_, idx) => idx !== currentIndex);
          if (updatedAnnotations.length > 0) {
            setAllAnnotations(updatedAnnotations);
            let newIndex = currentIndex;
            if (currentIndex >= updatedAnnotations.length) {
              newIndex = updatedAnnotations.length - 1;
            }
            setCurrentIndex(newIndex);
            setCurrentAnnotation(updatedAnnotations[newIndex]);
            setSavedData({ question_gn: '', answer_gn: '' });
            resetForm();
          } else {
            setCurrentIndex(0);
            setCurrentAnnotation(null);
            setAllAnnotations([]);
          }

          return;
        }
      } catch (checkErr) {
        console.error('Error verificando count de traducciones:', checkErr);
        // Si falla la comprobación, seguimos intentando guardar la traducción
      }

      // Si hay menos de 3 traducciones, crear la traducción normalmente
      await annotationsAPI.createTranslation(currentAnnotation.id, payload);
      toast.success('¡Traducción enviada correctamente!');
      
      // Remover la anotación actual del buffer
      const updatedAnnotations = allAnnotations.filter((_, idx) => idx !== currentIndex);
      
      if (updatedAnnotations.length > 0) {
        // Si hay más anotaciones, mostrar la siguiente
        setAllAnnotations(updatedAnnotations);
        
        // Ajustar el índice: si eliminamos la última anotación, retroceder
        let newIndex = currentIndex;
        if (currentIndex >= updatedAnnotations.length) {
          newIndex = updatedAnnotations.length - 1;
        }
        
        setCurrentIndex(newIndex);
        setCurrentAnnotation(updatedAnnotations[newIndex]);
        setSavedData({ question_gn: '', answer_gn: '' });
        resetForm();
      } else {
        // No hay más anotaciones
        setCurrentIndex(0);
        setCurrentAnnotation(null);
        setAllAnnotations([]);
      }
    } catch (err) {
      console.error('Error sending translation:', err);
      toast.error(err.response?.data?.detail || 'Error al enviar traducción');
    } finally {
      setSubmitting(false);
    }
  };

  const handleNext = () => {
    if (currentIndex < allAnnotations.length - 1) {
      const nextIndex = currentIndex + 1;
      setCurrentIndex(nextIndex);
      setCurrentAnnotation(allAnnotations[nextIndex]);
      // Clear saved data for new annotation
      setSavedData({
        question_gn: '',
        answer_gn: ''
      });
      resetForm();
    } else {
      toast.info('No hay más anotaciones disponibles');
    }
  };

  const handlePreviousClick = () => {
    if (currentIndex > 0) {
      const prevIndex = currentIndex - 1;
      setCurrentIndex(prevIndex);
      setCurrentAnnotation(allAnnotations[prevIndex]);
      // Clear saved data for new annotation
      setSavedData({
        question_gn: '',
        answer_gn: ''
      });
      resetForm();
    } else {
      toast.info('Esta es la primera anotación');
    }
  };

  if (loading) return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-600"></div>
        </div>
      </div>
    </div>
  );

  if (!currentAnnotation) return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="text-center py-16">
          <div className="text-6xl mb-4">🎉</div>
          <h2 className="text-3xl font-bold text-gray-900 mb-4">¡Felicidades!</h2>
          <p className="text-xl text-gray-600 mb-2">Ya no tienes traducciones pendientes</p>
          
          <div className="mt-8 p-6 bg-teal-50 rounded-lg border border-teal-200 max-w-md mx-auto">
            <p className="text-teal-800">
              <strong>¿Quieres más preguntas?</strong>
            </p>
            <p className="text-teal-700 text-sm mt-2">
              Visita la página de
              <a href="/pending-translations" className="font-semibold underline"> Traducciones pendientes</a>
            </p>
          </div>
          
          <button onClick={() => window.location.href = '/pending-translations'} className="btn mt-6 bg-teal-600 text-white hover:bg-teal-700 px-4 py-2 rounded-lg font-medium transition-colors">Ver Traducciones Pendientes</button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Navigation Controls */}
        <div className="mb-6 flex items-center justify-between bg-white p-4 rounded-lg shadow-sm">
          <div className="flex gap-3">
            <button
              onClick={handlePreviousClick}
              disabled={loading || submitting || currentIndex === 0}
              className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 disabled:opacity-50"
            >
              ← Anterior
            </button>
            <button
              onClick={handleNext}
              disabled={loading || submitting || currentIndex >= allAnnotations.length - 1}
              className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 disabled:opacity-50"
            >
              Siguiente →
            </button>
          </div>
          <div className="text-sm text-gray-600">
            Anotación {currentIndex + 1} de {allAnnotations.length}
          </div>
        </div>

        {/* Main Content */}
        <div className="bg-white p-6 rounded-lg shadow-sm mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-6">📋 Mis pendientes - Traduce las siguientes oraciones:</h1>

          {/* Preguntas */}
          {currentAnnotation.question_es && (
          <div className="mb-8">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">Pregunta</h2>
            
            {/* Spanish Original */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Pregunta (Español)
              </label>
              <div className="p-3 bg-gray-100 rounded-lg text-gray-900 break-words">
                {currentAnnotation.question_es}
              </div>
            </div>

            {/* Guarani Translation */}
            <div>
              <label htmlFor="question_gn" className="block text-sm font-medium text-gray-700 mb-2">
                Traducción al Guaraní
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
                      onClick={() => insertCharInto(questionGnRef, 'question_gn', value)}
                      className="text-xs px-2 py-1 bg-white border rounded hover:bg-gray-100 font-medium"
                      title={`Insertar ${label}`}
                    >
                      {label}
                    </button>
                  );
                })}
              </div>

              <textarea
                ref={questionGnRef}
                name="question_gn"
                value={formData.question_gn}
                onChange={handleTextChange}
                placeholder="Traduce la pregunta al guaraní aquí..."
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 resize-none"
                rows={4}
                disabled={submitting}
              />
            </div>

            {/* Suggestions */}
            {currentAnnotation.suggestion_count > 0 && (
              <div className="mt-4 p-3 bg-teal-50 border border-teal-200 rounded-lg">
                <p className="text-sm font-semibold text-teal-800 mb-2">
                  💡 Sugerencias disponibles: {currentAnnotation.suggestion_count}
                </p>
              </div>
            )}
          </div>
          )}

          {/* Respuestas */}
          {currentAnnotation.answer_es && (
          <div className="mb-8 border-t pt-8">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">Respuesta</h2>
            
            {/* Spanish Original */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Respuesta (Español)
              </label>
              <div className="p-3 bg-gray-100 rounded-lg text-gray-900 break-words">
                {currentAnnotation.answer_es}
              </div>
            </div>

            {/* Guarani Translation */}
            <div>
              <label htmlFor="answer_gn" className="block text-sm font-medium text-gray-700 mb-2">
                Traducción al Guaraní
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
                      onClick={() => insertCharInto(answerGnRef, 'answer_gn', value)}
                      className="text-xs px-2 py-1 bg-white border rounded hover:bg-gray-100 font-medium"
                      title={`Insertar ${label}`}
                    >
                      {label}
                    </button>
                  );
                })}
              </div>

              <textarea
                ref={answerGnRef}
                name="answer_gn"
                value={formData.answer_gn}
                onChange={handleTextChange}
                placeholder="Traduce la respuesta al guaraní aquí..."
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 resize-none"
                rows={4}
                disabled={submitting}
              />
            </div>

            {/* Suggestions */}
            {currentAnnotation.suggestion_count > 0 && (
              <div className="mt-4 p-3 bg-teal-50 border border-teal-200 rounded-lg">
                <p className="text-sm font-semibold text-teal-800 mb-2">
                  💡 Sugerencias disponibles: {currentAnnotation.suggestion_count}
                </p>
              </div>
            )}
          </div>
          )}

          {/* Metadata */}
          {(currentAnnotation.answer_number || currentAnnotation.equation_solution) && (
            <div className="mb-8 border-t pt-8">
              <h2 className="text-lg font-semibold text-gray-800 mb-4">Información adicional</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {currentAnnotation.answer_number && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Número de Respuesta
                    </label>
                    <input
                      type="text"
                      value={currentAnnotation.answer_number}
                      disabled
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-100 text-gray-700"
                    />
                  </div>
                )}
                
                {currentAnnotation.equation_solution && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Ecuación/Solución
                    </label>
                    <input
                      type="text"
                      value={currentAnnotation.equation_solution}
                      disabled
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-100 text-gray-700"
                    />
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Submit */}
          <div className="border-t pt-6">
            <div className="flex gap-3 justify-end">
              <button
                onClick={handleIgnore}
                disabled={loading || submitting}
                className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 disabled:opacity-50 font-medium"
              >
                ⊘ Ignorar
              </button>
              <button
                onClick={handleSendTranslation}
                disabled={submitting || (!formData.question_gn.trim() && !formData.answer_gn.trim())}
                className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 font-medium"
              >
                {submitting ? 'Enviando...' : '✓ Enviar traducción'}
              </button>
            </div>
          </div>
        </div>

        {/* Confirmation Modal */}
        {showConfirmModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-lg p-6 max-w-md mx-4">
              <h3 className="text-lg font-bold text-gray-900 mb-4">¿Estás seguro?</h3>
              <p className="text-gray-600 mb-2">
                Estás a punto de enviar la traducción de esta anotación.
              </p>
              <p className="text-gray-600 mb-6">
                Una vez enviada, no podrás modificarla nuevamente.
              </p>
              
              <div className="flex gap-3 justify-end">
                <button
                  onClick={() => setShowConfirmModal(false)}
                  disabled={submitting}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 disabled:opacity-50 font-medium"
                >
                  Cancelar
                </button>
                <button
                  onClick={confirmSendTranslation}
                  disabled={submitting}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 font-medium"
                >
                  {submitting ? 'Enviando...' : 'Sí, enviar'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TranslatorAnnotationsPage;
