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
      value: 'partial',
      label: 'Parcial',
      icon: '~',
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

  return (
    <div className="space-y-2">
      <h3 className="text-lg font-medium text-gray-800">
        Corrección de la traducción
      </h3>
      <div className="flex flex-wrap gap-3">
        {options.map((option) => {
          const isSelected = selectedCorrectness === option.value;
          const buttonClasses = `
            flex-1 min-w-[120px] px-4 py-3 border-2 rounded-lg font-medium text-white
            transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2
            ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
            ${isSelected 
              ? `${option.selectedBg} ${option.selectedBorder} ring-2 ring-offset-2 ring-gray-400` 
              : `${option.bgColor} ${option.borderColor}`
            }
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