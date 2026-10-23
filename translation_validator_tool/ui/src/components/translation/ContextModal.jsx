import { useState, useEffect } from 'react';
import { XMarkIcon, DocumentTextIcon } from '@heroicons/react/24/outline';
import { translationsAPI } from '../../services/api';

/**
 * Modal que muestra el contexto de una traducción.
 * Muestra las oraciones anteriores y siguientes con la oración actual resaltada.
 * Similar al botón de contexto en Prodigy.
 */
const ContextModal = ({ translation, isOpen, onClose }) => {
  const [context, setContext] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isOpen && translation?.id) {
      loadContext();
    }
  }, [isOpen, translation?.id]);

  const loadContext = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await translationsAPI.getContext(translation.id, 3, 3);
      setContext(response.data || response);
    } catch (err) {
      console.error('Error loading context:', err);
      setError('No se pudo cargar el contexto');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  // Determinar qué texto mostrar basado en la dirección de la traducción actual
  const direction = translation?.direction || 'sp-gn';
  const showGuarani = true; // Siempre mostramos guaraní (el texto a anotar)

  const renderSentence = (t, isCurrent = false) => {
    const text = t.guarani_text || '';
    
    if (isCurrent) {
      return (
        <span className="font-bold underline decoration-2 decoration-blue-500 bg-yellow-100 px-1 rounded">
          {text}
        </span>
      );
    }
    return <span className="text-gray-600">{text}</span>;
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-3xl w-full max-h-[80vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b bg-gradient-to-r from-blue-600 to-blue-700">
          <div className="flex items-center gap-3">
            <DocumentTextIcon className="h-6 w-6 text-white" />
            <h2 className="text-lg font-semibold text-white">Contexto</h2>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-white/20 transition-colors"
          >
            <XMarkIcon className="h-6 w-6 text-white" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[60vh]">
          {loading && (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full"></div>
              <span className="ml-3 text-gray-600">Cargando contexto...</span>
            </div>
          )}

          {error && (
            <div className="text-center py-12">
              <p className="text-red-500">{error}</p>
              <button
                onClick={loadContext}
                className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Reintentar
              </button>
            </div>
          )}

          {context && !loading && (
            <div className="space-y-4">
              {/* Información del documento */}
              <div className="text-sm text-gray-500 mb-4">
                <span className="font-medium">Fuente:</span> {context.current?.source || 'Desconocida'}
                <span className="mx-2">•</span>
                <span className="font-medium">ID:</span> {context.current?.id}
              </div>

              {/* Bloque de texto continuo */}
              <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
                <div className="text-lg leading-relaxed space-y-0">
                  {/* Texto como bloque continuo */}
                  <p className="text-justify">
                    {/* Oraciones anteriores */}
                    {context.before?.map((t, idx) => (
                      <span key={`before-${t.id}`}>
                        {renderSentence(t, false)}
                        {' '}
                      </span>
                    ))}
                    
                    {/* Oración actual (resaltada) */}
                    {context.current && (
                      <span>
                        {renderSentence(context.current, true)}
                        {' '}
                      </span>
                    )}
                    
                    {/* Oraciones siguientes */}
                    {context.after?.map((t, idx) => (
                      <span key={`after-${t.id}`}>
                        {renderSentence(t, false)}
                        {' '}
                      </span>
                    ))}
                  </p>
                </div>
              </div>

              {/* Leyenda */}
              <div className="flex items-center justify-center gap-4 text-sm text-gray-500 mt-4">
                <div className="flex items-center gap-2">
                  <span className="font-bold underline decoration-2 decoration-blue-500 bg-yellow-100 px-2 py-0.5 rounded text-gray-800">
                    Texto
                  </span>
                  <span>= Oración actual</span>
                </div>
              </div>

              {/* Nota si no hay contexto */}
              {context.before?.length === 0 && context.after?.length === 0 && (
                <p className="text-center text-gray-500 text-sm mt-4">
                  No hay oraciones de contexto disponibles para esta traducción.
                </p>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t bg-gray-50 flex justify-between items-center">
          <p className="text-xs text-gray-500">
            Usa Ctrl+Shift+C para abrir/cerrar el contexto
          </p>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
          >
            Cerrar
          </button>
        </div>
      </div>
    </div>
  );
};

export default ContextModal;
