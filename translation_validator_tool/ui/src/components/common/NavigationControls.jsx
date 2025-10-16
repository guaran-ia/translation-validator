import { ChevronLeftIcon, ChevronRightIcon } from '@heroicons/react/24/outline';

const NavigationControls = ({ 
  onPrevious, 
  onNext, 
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

      <div className="flex items-center space-x-4 text-sm text-gray-600">
        {currentTranslation && (
          <>
            <span>ID: {currentTranslation.id}</span>
            <div className="flex items-center space-x-1">
              <span className={`inline-block w-2 h-2 rounded-full ${
                currentTranslation.user_has_validated ? 'bg-green-500' : 'bg-orange-500'
              }`}></span>
              <span>
                {currentTranslation.user_has_validated ? 'Evaluado' : 'Pendiente'}
              </span>
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