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

  return (
    <div className="card">
      <div className="mb-4 text-center">
        <h2 className="text-xl font-semibold text-gray-800">
          Evaluate the following translation
        </h2>
        <p className="text-sm text-gray-600 mt-1">
          Translation ID: {translation.id}
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Guarani Text */}
        <div className="space-y-2">
          <h3 className="text-lg font-medium text-green-700 flex items-center">
            <span className="w-3 h-3 bg-green-500 rounded-full mr-2"></span>
            Guaraní
          </h3>
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 min-h-[120px]">
            <p className="text-gray-800 leading-relaxed">
              {translation.guarani_text}
            </p>
          </div>
        </div>

        {/* Spanish Text */}
        <div className="space-y-2">
          <h3 className="text-lg font-medium text-blue-700 flex items-center">
            <span className="w-3 h-3 bg-blue-500 rounded-full mr-2"></span>
            Español
          </h3>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 min-h-[120px]">
            <p className="text-gray-800 leading-relaxed">
              {translation.spanish_text}
            </p>
          </div>
        </div>
      </div>

      {/* Additional info */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="flex justify-between items-center text-sm text-gray-600">
          <span>Source: {translation.source}</span>
          <div className="flex items-center gap-4">
            {translation.validation_count !== undefined && (
              <span>
                Validations: {translation.validation_count}
              </span>
            )}

            {/* Suggestion info */}
            {translation.suggestion_count !== undefined && (
              <span className="text-sm text-gray-600">
                Suggestions: {translation.suggestion_count}
              </span>
            )}

            {translation.user_has_suggested && (
              <span className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded text-xs">
                You suggested this
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TranslationCard;