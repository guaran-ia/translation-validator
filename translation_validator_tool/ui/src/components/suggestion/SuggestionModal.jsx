import { useState } from 'react';

const SuggestionModal = ({ 
  isOpen, 
  onClose, 
  onSubmit, 
  currentTranslation,
  isLoading = false 
}) => {
  const [formData, setFormData] = useState({
    suggested_guarani: '',
    suggested_spanish: '',
    reason: ''
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!currentTranslation) return;

    // Determine target language based on direction
    const dir = currentTranslation.direction || 'sp-gn';
    const targetIsGuarani = dir === 'sp-gn';

    // Validate that suggestion for target language is provided
    if (targetIsGuarani) {
      if (!formData.suggested_guarani.trim()) {
        alert('Por favor proporciona una sugerencia en Guaraní.');
        return;
      }
    } else {
      if (!formData.suggested_spanish.trim()) {
        alert('Por favor proporciona una sugerencia en Español.');
        return;
      }
    }

    try {
      const payload = {
        translation_id: currentTranslation.id,
        reason: formData.reason.trim() || null
      };

      if (targetIsGuarani) {
        payload.suggested_guarani = formData.suggested_guarani.trim();
        payload.suggested_spanish = null;
      } else {
        payload.suggested_spanish = formData.suggested_spanish.trim();
        payload.suggested_guarani = null;
      }

      await onSubmit(payload);

      // Reset form
      setFormData({
        suggested_guarani: '',
        suggested_spanish: '',
        reason: ''
      });
      
      onClose();
    } catch (error) {
      console.error('Error enviando la sugerencia:', error);
    }
  };

  const handleCancel = () => {
    setFormData({
      suggested_guarani: '',
      suggested_spanish: '',
      reason: ''
    });
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          {/* Header */}
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-bold text-gray-900">
              Sugerir nueva traducción
            </h2>
            <button
              onClick={handleCancel}
              className="text-gray-400 hover:text-gray-600 text-2xl"
              disabled={isLoading}
            >
              ×
            </button>
          </div>

          {/* Current translation */}
          {currentTranslation && (
            <div className="mb-6 p-4 bg-gray-50 rounded-lg">
              <h3 className="text-sm font-medium text-gray-700 mb-2">
                Traducción actual:
              </h3>
              <div className="grid md:grid-cols-2 gap-4 text-sm">
                {(() => {
                  const dir = currentTranslation.direction || 'sp-gn';
                  const leftIsOriginal = dir === 'sp-gn' ? 'spanish' : 'guarani';
                  const rightIsTranslation = leftIsOriginal === 'spanish' ? 'guarani' : 'spanish';

                  const leftText = leftIsOriginal === 'spanish' ? currentTranslation.spanish_text : currentTranslation.guarani_text;
                  const rightText = rightIsTranslation === 'guarani' ? currentTranslation.guarani_text : currentTranslation.spanish_text;

                  return (
                    <>
                      <div>
                        <span className="font-medium text-gray-700">{leftIsOriginal === 'spanish' ? 'Español (original):' : 'Guaraní (original):'}</span>
                        <p className="text-gray-800 mt-1">{leftText}</p>
                      </div>
                      <div>
                        <span className="font-medium text-gray-700">{rightIsTranslation === 'guarani' ? 'Guaraní:' : 'Español:'}</span>
                        <p className="text-gray-800 mt-1">{rightText}</p>
                      </div>
                    </>
                  );
                })()}
              </div>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Suggested input: only for target language */}
            {(() => {
              const dir = currentTranslation?.direction || 'sp-gn';
              const targetIsGuarani = dir === 'sp-gn';

              if (targetIsGuarani) {
                  return (
                    <div>
                      <label htmlFor="suggested_guarani" className="block text-sm font-medium text-gray-700 mb-1">
                        Sugerencia en guaraní
                      </label>
                      <textarea
                        id="suggested_guarani"
                        name="suggested_guarani"
                        value={formData.suggested_guarani}
                        onChange={handleChange}
                        placeholder="Introduce tu sugerencia en guaraní..."
                        className="w-full px-4 py-3 border-2 border-blue-100 bg-blue-50 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent resize-y shadow-sm"
                        rows="4"
                        disabled={isLoading}
                      />
                      <p className="text-xs text-gray-500 mt-1">Por favor sugiere la traducción objetivo (Guaraní).</p>
                    </div>
                  );
                }

              return (
                <div>
                  <label htmlFor="suggested_spanish" className="block text-sm font-medium text-gray-700 mb-1">
                    Sugerencia en español
                  </label>
                  <textarea
                      id="suggested_spanish"
                      name="suggested_spanish"
                      value={formData.suggested_spanish}
                      onChange={handleChange}
                      placeholder="Introduce tu sugerencia en español..."
                      className="w-full px-4 py-3 border-2 border-green-100 bg-green-50 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-400 focus:border-transparent resize-y shadow-sm"
                      rows="4"
                      disabled={isLoading}
                    />
                    <p className="text-xs text-gray-500 mt-1">Por favor sugiere la traducción objetivo (Español).</p>
                </div>
              );
            })()}

            {/* Reason */}
            <div>
              <label htmlFor="reason" className="block text-sm font-medium text-gray-700 mb-1">
                Motivo del cambio (opcional)
              </label>
              <textarea
                id="reason"
                name="reason"
                value={formData.reason}
                onChange={handleChange}
                placeholder="Explica por qué crees que esto mejora la traducción..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                rows="3"
                disabled={isLoading}
              />
            </div>

            {/* Note */}
            <div className="text-sm text-gray-600 bg-blue-50 p-3 rounded-lg">
              <p><strong>Nota:</strong> Debes proporcionar al menos una sugerencia de traducción (guaraní o español).</p>
            </div>

            {/* Buttons */}
            <div className="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                onClick={handleCancel}
                className="btn btn-secondary"
                disabled={isLoading}
              >
                Cancelar
              </button>
              <button
                type="submit"
                className="btn btn-primary"
                disabled={isLoading}
              >
                {isLoading ? (
                  <div className="flex items-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Enviando...
                  </div>
                ) : (
                  'Enviar sugerencia'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default SuggestionModal;