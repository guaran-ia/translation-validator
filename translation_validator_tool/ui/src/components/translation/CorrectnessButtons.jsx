const CorrectnessButtons = ({ selectedCorrectness, regularReason = '', onSelect, onRegularReasonChange, disabled }) => {
  const mainOptions = [
    {
      value: 'correct',
      label: 'Correcta',
      icon: '✓',
      bgColor: 'bg-green-600 hover:bg-green-700',
      selectedBg: 'bg-green-700',
      borderColor: 'border-green-600',
      selectedBorder: 'border-green-700'
    },
    {
      value: 'regular',
      label: 'Regular',
      icon: '!',
      bgColor: 'bg-yellow-500 hover:bg-yellow-600',
      selectedBg: 'bg-yellow-600',
      borderColor: 'border-yellow-500',
      selectedBorder: 'border-yellow-600'
    },
    {
      value: 'incorrect',
      label: 'Incorrecta',
      icon: '✗',
      bgColor: 'bg-red-600 hover:bg-red-700',
      selectedBg: 'bg-red-700',
      borderColor: 'border-red-600',
      selectedBorder: 'border-red-700'
    }
  ];

  const detailOptions = [
    {
      value: 'gn_more',
      label: 'Guaraní tiene más información',
      icon: 'G',
      bgColor: 'bg-indigo-600 hover:bg-indigo-700',
      selectedBg: 'bg-indigo-700',
      borderColor: 'border-indigo-600',
      selectedBorder: 'border-indigo-700'
    },
    {
      value: 'es_more',
      label: 'Español tiene más información',
      icon: 'E',
      bgColor: 'bg-purple-600 hover:bg-purple-700',
      selectedBg: 'bg-purple-700',
      borderColor: 'border-purple-600',
      selectedBorder: 'border-purple-700'
    },
    {
      value: 'regular_other',
      label: 'Otro',
      icon: '?',
      bgColor: 'bg-slate-600 hover:bg-slate-700',
      selectedBg: 'bg-slate-700',
      borderColor: 'border-slate-600',
      selectedBorder: 'border-slate-700'
    }
  ];

  const isRegularGroupSelected =
    selectedCorrectness === 'regular' ||
    selectedCorrectness === 'gn_more' ||
    selectedCorrectness === 'es_more' ||
    selectedCorrectness === 'regular_other';

  const showDetailOptions = isRegularGroupSelected;

  const getMainButtonClasses = (option) => {
    const isSelected =
      selectedCorrectness === option.value ||
      (option.value === 'regular' && isRegularGroupSelected);

    const isDimmed = selectedCorrectness && !isSelected;

    return `
      flex-1 min-w-[140px] px-5 py-3 border-2 rounded-lg font-semibold text-white text-sm
      transition-all duration-200 transform hover:-translate-y-0.5 focus:outline-none focus:ring-2 focus:ring-offset-2
      ${disabled ? 'opacity-60 cursor-not-allowed' : 'cursor-pointer'}
      ${
        isSelected
          ? `${option.selectedBg} ${option.selectedBorder} shadow-md scale-105`
          : isDimmed
            ? 'bg-gray-100 text-gray-500 border-gray-200 filter grayscale opacity-80 transform scale-100'
            : `${option.bgColor} ${option.borderColor} hover:shadow-sm`
      }
    `.replace(/\s+/g, ' ').trim();
  };

  const getDetailButtonClasses = (option) => {
  const isSelected = selectedCorrectness === option.value;

  const hasSecondarySelection =
    selectedCorrectness === 'gn_more' ||
    selectedCorrectness === 'es_more' ||
    selectedCorrectness === 'regular_other';

  const isDimmed = hasSecondarySelection && !isSelected;

  return `
    w-full md:w-[320px] px-5 py-3 border-2 rounded-lg font-semibold text-white text-sm
    transition-all duration-200 transform hover:-translate-y-0.5 focus:outline-none focus:ring-2 focus:ring-offset-2
    ${disabled ? 'opacity-60 cursor-not-allowed' : 'cursor-pointer'}
    ${
      isSelected
        ? `${option.selectedBg} ${option.selectedBorder} shadow-md scale-105`
        : isDimmed
          ? 'bg-gray-100 text-gray-500 border-gray-200 filter grayscale opacity-80 transform scale-100'
          : `${option.bgColor} ${option.borderColor} hover:shadow-sm`
    }
  `.replace(/\s+/g, ' ').trim();
  };

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-medium text-gray-800">
        Corrección de la traducción
      </h3>

      <div className="flex flex-wrap gap-3">
        {mainOptions.map((option) => (
          <button
            key={option.value}
            type="button"
            className={getMainButtonClasses(option)}
            onClick={() => !disabled && onSelect(option.value)}
            disabled={disabled}
          >
            <div className="flex items-center justify-center space-x-2">
              <span className="text-xl">{option.icon}</span>
              <span>{option.label}</span>
            </div>
          </button>
        ))}
      </div>

      {showDetailOptions && (
        <div className="pt-3 space-y-3">
          <p className="text-sm font-medium text-gray-700 text-center">
            ¿Por qué es regular?
          </p>

          <div className="flex flex-wrap justify-center gap-3">
            {detailOptions.map((option) => (
              <button
                key={option.value}
                type="button"
                className={getDetailButtonClasses(option)}
                onClick={() => !disabled && onSelect(option.value)}
                disabled={disabled}
              >
                <div className="flex items-center justify-center space-x-2">
                  <span className="text-xl">{option.icon}</span>
                  <span>{option.label}</span>
                </div>
              </button>
            ))}
          </div>

          {selectedCorrectness === 'regular_other' && (
            <div className="max-w-xl mx-auto pt-2">
              <label htmlFor="regular_reason" className="block text-sm font-medium text-gray-700 mb-2">
                Razón (Opcional):
              </label>
              <textarea
                id="regular_reason"
                value={regularReason}
                onChange={(e) => onRegularReasonChange?.(e.target.value)}
                rows={2}
                placeholder="Explica brevemente por qué consideras que la traducción es regular..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 resize-none text-sm"
                disabled={disabled}
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default CorrectnessButtons;
