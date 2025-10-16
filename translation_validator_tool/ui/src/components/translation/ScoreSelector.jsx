const ScoreSelector = ({ label, selectedScore, onSelect, disabled }) => {
  const scores = [1, 2, 3, 4, 5];

  return (
    <div className="space-y-2">
      <h4 className="text-base font-medium text-gray-800">
        {label}
      </h4>
      <div className="flex space-x-2">
        {scores.map((score) => {
          const isSelected = selectedScore === score;
          const buttonClasses = `
            w-10 h-10 rounded-full border-2 font-semibold text-sm
            transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500
            ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
            ${isSelected
              ? 'bg-blue-600 text-white border-blue-600'
              : 'bg-white text-gray-700 border-gray-300 hover:border-blue-400 hover:text-blue-600'
            }
          `.replace(/\s+/g, ' ').trim();

          return (
            <button
              key={score}
              type="button"
              className={buttonClasses}
              onClick={() => !disabled && onSelect(score)}
              disabled={disabled}
              title={`Score: ${score}/5`}
            >
              {score}
            </button>
          );
        })}
      </div>
      <p className="text-xs text-gray-500">
        1 = Poor, 5 = Excellent
      </p>
    </div>
  );
};

export default ScoreSelector;