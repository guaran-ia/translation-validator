import { useState } from 'react';

const ColumnMappingModal = ({ isOpen, onClose, onConfirm, availableColumns, previewData }) => {
  const [mapping, setMapping] = useState({
    question_es: null,
    answer_es: null,
    answer_number: null,
    equation_solution: null,
    md5: null,
  });

  const handleMappingChange = (field, column) => {
    setMapping(prev => ({
      ...prev,
      [field]: column
    }));
  };

  const handleConfirm = () => {
    // Validar que al menos pregunta esté mapeada
    if (!mapping.question_es && !mapping.answer_es) {
      alert('Debes mapear al menos la pregunta o la respuesta');
      return;
    }
    // Validar que md5 esté mapeado
    if (!mapping.md5) {
      alert('Debes mapear la columna MD5 (es obligatoria)');
      return;
    }
    onConfirm(mapping);
    onClose();
  };

  if (!isOpen) return null;

  const fieldLabels = {
    question_es: 'Pregunta (ES)',
    answer_es: 'Respuesta (ES)',
    answer_number: 'Número (opcional)',
    equation_solution: 'Ecuación (opcional)',
    md5: 'MD5 (obligatorio)',
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-screen overflow-y-auto">
        {/* Header */}
        <div className="bg-blue-600 text-white px-8 py-5 flex justify-between items-center">
          <h2 className="text-2xl font-bold">Mapeo de Columnas</h2>
          <button
            onClick={onClose}
            className="text-white hover:bg-blue-700 p-2 rounded text-2xl"
          >
            ✕
          </button>
        </div>

        {/* Body */}
        <div className="p-8">
          <p className="text-gray-700 mb-8 text-lg">
            Selecciona qué columna corresponde a cada campo:
          </p>

          {/* Column Mapping Form */}
          <div className="space-y-6 mb-8">
            {Object.entries(fieldLabels).map(([field, label]) => (
              <div key={field} className="flex items-center gap-6">
                <label className="w-48 font-semibold text-gray-800 text-base">
                  {label}
                </label>
                <select
                  value={mapping[field] || ''}
                  onChange={(e) => handleMappingChange(field, e.target.value || null)}
                  className="flex-1 px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-base"
                >
                  <option value="">-- Sin mapear --</option>
                  {availableColumns.map((col, idx) => (
                    <option key={idx} value={col}>
                      {col}
                    </option>
                  ))}
                </select>
              </div>
            ))}
          </div>

          {/* Preview of Data */}
          {previewData && (
            <div className="bg-gray-50 p-6 rounded-lg mb-8">
              <h3 className="font-bold text-gray-800 mb-4 text-lg">Vista previa de datos (primera fila):</h3>
              <div className="space-y-3 text-base">
                {mapping.question_es && (
                  <p className="text-gray-700">
                    <span className="font-semibold text-blue-700">Pregunta:</span> <span className="text-gray-600">{previewData[mapping.question_es] || '(vacío)'}</span>
                  </p>
                )}
                {mapping.answer_es && (
                  <p className="text-gray-700">
                    <span className="font-semibold text-blue-700">Respuesta:</span> <span className="text-gray-600">{previewData[mapping.answer_es] || '(vacío)'}</span>
                  </p>
                )}
                {mapping.answer_number && (
                  <p className="text-gray-700">
                    <span className="font-semibold text-blue-700">Número:</span> <span className="text-gray-600">{previewData[mapping.answer_number] || '(vacío)'}</span>
                  </p>
                )}
                {mapping.equation_solution && (
                  <p className="text-gray-700">
                    <span className="font-semibold text-blue-700">Ecuación:</span> <span className="text-gray-600">{previewData[mapping.equation_solution] || '(vacío)'}</span>
                  
                {mapping.md5 && (
                  <p className="text-gray-700">
                    <span className="font-semibold text-blue-700">MD5:</span> <span className="text-gray-600">{previewData[mapping.md5] || '(vacío)'}</span>
                  </p>
                )}</p>
                )}
              </div>
            </div>
          )}

          {/* All Columns Available */}
          <div className="bg-blue-50 p-6 rounded-lg mb-8">
            <h3 className="font-bold text-blue-900 mb-4 text-lg">Todas las columnas disponibles en tu Excel:</h3>
            <div className="flex flex-wrap gap-3">
              {availableColumns.map((col, idx) => (
                <span key={idx} className="bg-blue-200 text-blue-900 px-4 py-2 rounded-full text-base font-medium">
                  {col}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="bg-gray-50 px-8 py-5 flex justify-end gap-4 border-t">
          <button
            onClick={onClose}
            className="px-6 py-3 text-gray-700 hover:bg-gray-200 rounded-md font-semibold text-base"
          >
            Cancelar
          </button>
          <button
            onClick={handleConfirm}
            className="px-6 py-3 bg-blue-600 text-white hover:bg-blue-700 rounded-md font-semibold text-base"
          >
            Confirmar Mapeo
          </button>
        </div>
      </div>
    </div>
  );
};

export default ColumnMappingModal;
