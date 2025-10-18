const TranslationCard = ({ translation }) => {
  if (!translation) {
    return (
      <div className="card animate-pulse">
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <div className="h-4 bg-gray-200 rounded w-1/4 mb-2"></div>
            <div className="h-20 bg-gray-200 rounded"></div>
          </div>
          <div>
            <div className="h-4 bg-gray-200 rounded w-1/4 mb-2"></div>
            <div className="h-20 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  // Determine ordering based on translation.direction (default sp-gn)
  const dir = translation?.direction || 'sp-gn';
  const leftIsOriginal = dir === 'sp-gn' ? 'spanish' : 'guarani';
  const rightIsTranslation = leftIsOriginal === 'spanish' ? 'guarani' : 'spanish';

  const leftText = leftIsOriginal === 'spanish' ? translation.spanish_text : translation.guarani_text;
  const rightText = rightIsTranslation === 'guarani' ? translation.guarani_text : translation.spanish_text;

  return (
    <div className="card">
      <div className="mb-4 text-center">
        <h2 className="text-xl font-semibold text-gray-800">
          Evalúa la siguiente traducción
        </h2>
        <p className="text-sm text-gray-600 mt-1">
          ID de traducción: {translation.id}
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Left (original) */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium text-gray-700 flex items-center">
              <span className="w-3 h-3 bg-blue-400 rounded-full mr-2 shadow-sm"></span>
              {leftIsOriginal === 'spanish' ? 'Español (original)' : 'Guaraní (original)'}
            </h3>
            <span className="text-xs px-2 py-1 rounded-full bg-blue-50 text-blue-700 border border-blue-100">Original</span>
          </div>
          <div className="bg-white border border-blue-100 rounded-lg p-4 min-h-[120px] shadow-sm">
            <p className="text-gray-900 leading-relaxed">{leftText}</p>
          </div>
        </div>

        {/* Right (translation) */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium text-gray-700 flex items-center">
              <span className="w-3 h-3 bg-green-400 rounded-full mr-2 shadow-sm"></span>
              {rightIsTranslation === 'guarani' ? 'Guaraní' : 'Español'}
            </h3>
            <span className="text-xs px-2 py-1 rounded-full bg-green-50 text-green-700 border border-green-100">Traducción</span>
          </div>
          <div className="bg-white border border-green-100 rounded-lg p-4 min-h-[120px] shadow-sm">
            <p className="text-gray-900 leading-relaxed">{rightText}</p>
          </div>
        </div>
      </div>

      {/* Additional info */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="flex justify-between items-center text-sm text-gray-600">
          <span>Fuente: {translation.source}</span>
          <div className="flex items-center gap-4">
            {translation.validation_count !== undefined && (
              <span>
                Evaluaciones: {translation.validation_count}
              </span>
            )}

            {/* Suggestion info */}
            {translation.suggestion_count !== undefined && (
              <span className="text-sm text-gray-600">
                Sugerencias: {translation.suggestion_count}
              </span>
            )}

            {translation.user_has_suggested && (
              <span className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded text-xs">
                Has sugerido esto
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TranslationCard;