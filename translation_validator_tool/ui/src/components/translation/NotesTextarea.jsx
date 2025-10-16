import { useState } from 'react';

const NotesTextarea = ({ notes, onNotesChange, disabled, maxLength = 500 }) => {
  const [isFocused, setIsFocused] = useState(false);

  const handleChange = (e) => {
    const value = e.target.value;
    if (value.length <= maxLength) {
      onNotesChange(value);
    }
  };

  return (
    <div className="space-y-2">
      <h4 className="text-base font-medium text-gray-800">
        Notes (Optional)
      </h4>
      <div className="relative">
        <textarea
          value={notes || ''}
          onChange={handleChange}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          disabled={disabled}
          placeholder="Add any comments about the translation quality, errors, or suggestions..."
          className={`
            w-full px-3 py-2 border rounded-lg resize-none transition-all duration-200
            focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
            ${disabled ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'}
            ${isFocused ? 'border-blue-400' : 'border-gray-300'}
          `.replace(/\s+/g, ' ').trim()}
          rows="4"
        />
        
        {/* Character counter */}
        <div className="absolute bottom-2 right-2 text-xs text-gray-500 bg-white px-1 rounded">
          {(notes || '').length}/{maxLength}
        </div>
      </div>
      
      {/* Tips */}
      <div className="text-xs text-gray-500">
        <p>💡 Include notes about:</p>
        <ul className="ml-4 mt-1 space-y-1">
          <li>• Grammar or vocabulary errors</li>
          <li>• Cultural context issues</li>
          <li>• Alternative translations</li>
          <li>• Clarity or naturalness</li>
        </ul>
      </div>
    </div>
  );
};

export default NotesTextarea;