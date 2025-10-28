import { ChevronLeftIcon, ChevronRightIcon } from '@heroicons/react/24/outline';

const NavigationControls = ({ 
  onPrevious, 
  onNext, 
  onSuggest,
  currentTranslation, 
  loading = false 
}) => {
  

  return (
    <div className="flex items-center justify-between bg-gray-50 px-4 py-3 rounded-lg border">
      <button
        onClick={onPrevious}
        disabled={loading || !currentTranslation}
        className="flex items-center space-x-2 px-4 py-2 bg-white border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <ChevronLeftIcon className="h-4 w-4" />
        <span>Anterior</span>
      </button>

      <div className="flex flex-col items-center space-y-2 text-sm text-gray-600">
        {currentTranslation && (
          <>
            {/* Suggest button lives here now; parent can supply onSuggest to open the suggestion modal */}
            <div>
              <button
                onClick={onSuggest}
                disabled={loading || !currentTranslation}
                className="mt-1 px-3 py-1 bg-blue-50 text-blue-700 border border-blue-100 rounded-md text-sm hover:bg-blue-100 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                🔄 Sugerir traducción
              </button>
            </div>
          </>
        )}
      </div>

      <button
        onClick={onNext}
        disabled={loading || !currentTranslation}
        className="flex items-center space-x-2 px-4 py-2 bg-blue-600 border border-transparent rounded-md shadow-sm text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <span>Siguiente</span>
        <ChevronRightIcon className="h-4 w-4" />
      </button>
    </div>
  );
};

export default NavigationControls;