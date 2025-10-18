const CorrectnessButtons = ({ selectedCorrectness, onSelect, disabled }) => {
  const options = [
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
      value: 'incorrect',
      label: 'Incorrecta',
      icon: '✗',
      bgColor: 'bg-red-600 hover:bg-red-700',
      selectedBg: 'bg-red-700',
      borderColor: 'border-red-600',
      selectedBorder: 'border-red-700'
    }
  ];

  return (
    <div className="space-y-2">
      <h3 className="text-lg font-medium text-gray-800">
        Corrección de la traducción
      </h3>
      <div className="flex flex-wrap gap-3">
        {options.map((option) => {
          const isSelected = selectedCorrectness === option.value;
          const buttonClasses = `
            flex-1 min-w-[140px] px-5 py-3 border-2 rounded-lg font-semibold text-white text-sm
            transition-all duration-200 transform hover:-translate-y-0.5 focus:outline-none focus:ring-2 focus:ring-offset-2
            ${disabled ? 'opacity-60 cursor-not-allowed' : 'cursor-pointer'}
            ${isSelected 
              ? `${option.selectedBg} ${option.selectedBorder} shadow-md scale-105` 
              : `${option.bgColor} ${option.borderColor} hover:shadow-sm`}
          `.replace(/\s+/g, ' ').trim();

          return (
            <button
              key={option.value}
              type="button"
              className={buttonClasses}
              onClick={() => !disabled && onSelect(option.value)}
              disabled={disabled}
            >
              <div className="flex items-center justify-center space-x-2">
                <span className="text-xl">{option.icon}</span>
                <span>{option.label}</span>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default CorrectnessButtons;