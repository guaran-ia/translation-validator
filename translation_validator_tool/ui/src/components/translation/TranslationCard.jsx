import { useState, useEffect } from 'react';
import { translationsAPI } from '../../services/api';

const TranslationCard = ({ translation, onDirectionChange, onReplace }) => {
  const [current, setCurrent] = useState(translation);
  useEffect(() => {
    setCurrent(translation);
  }, [translation]);

  if (!current) {
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

  // Determine ordering based on current.direction (default sp-gn)
  const dir = current?.direction || 'sp-gn';
  const leftIsOriginal = dir === 'sp-gn' ? 'spanish' : 'guarani';
  const rightIsTranslation = leftIsOriginal === 'spanish' ? 'guarani' : 'spanish';

  const leftText = leftIsOriginal === 'spanish' ? current.spanish_text : current.guarani_text;
  const rightText = rightIsTranslation === 'guarani' ? current.guarani_text : current.spanish_text;

  const [dirState, setDirState] = useState(current.direction || 'sp-gn');
  const [isSaving, setIsSaving] = useState(false);

  const toggleDirection = async () => {
    // Try to fetch the paired translation (either direction). Backend provides /translations/pair/{id}
    try {
      setIsSaving(true);
      const res = await translationsAPI.getPair(current.id);
      const paired = res?.data || res;
      if (paired) {
        // Replace current with paired and notify parent if provided
        setCurrent(paired);
        const newDir = paired.direction || 'sp-gn';
        setDirState(newDir);
        if (onDirectionChange) onDirectionChange(newDir);
        if (typeof onReplace === 'function') {
          onReplace(paired);
        }
        return;
      }
    } catch (e) {
      console.error('Failed to fetch paired translation via /pair endpoint', e);
      const status = e?.response?.status;
      // If not found or unauthorized, notify and fall back to patch behavior
      if (status === 404) {
        // no paired translation exists
        alert('No se encontró la traducción emparejada. Se intentará alternar la dirección localmente.');
      } else if (status === 401) {
        alert('Necesitas iniciar sesión para ver la traducción emparejada.');
      } else {
        // generic error
        console.error(e);
      }
    } finally {
      setIsSaving(false);
    }

    // Fallback: if no pair exists, keep previous behavior (PATCH direction)
    const newDir = dirState === 'sp-gn' ? 'gn-sp' : 'sp-gn';
    // Optimistic UI
    setDirState(newDir);
    if (onDirectionChange) {
      onDirectionChange(newDir);
    }
    try {
      setIsSaving(true);
      await translationsAPI.updateDirection(current.id, newDir);
      // update local current.direction too
      setCurrent({ ...current, direction: newDir });
    } catch (e) {
      console.error('Failed to update direction', e);
      // revert on error
      const revert = newDir === 'sp-gn' ? 'gn-sp' : 'sp-gn';
      setDirState(revert);
      if (onDirectionChange) onDirectionChange(revert);
      alert('Error actualizando la dirección (ver consola)');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="card">
      {/* Loading overlay when fetching paired translation or saving */}
      {isSaving && (
        <div className="absolute inset-0 bg-white/60 flex items-center justify-center z-50">
          <div className="flex items-center gap-3">
            <svg className="animate-spin -ml-1 mr-2 h-6 w-6 text-gray-700" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path>
            </svg>
            <span className="text-gray-700">Cargando traducción emparejada…</span>
          </div>
        </div>
      )}
      <div className="mb-4 text-center">
          <h2 className="text-xl font-semibold text-gray-800">
          Evalúa la siguiente traducción
        </h2>
        <p className="text-sm text-gray-600 mt-1">
          ID de traducción: {current.id}
        </p>
        <div className="mt-3 flex items-center justify-center gap-2">
          <button
            onClick={toggleDirection}
            disabled={isSaving}
            className={`
              group relative inline-flex items-center gap-2 px-3 py-2 rounded-lg font-medium text-xs
              transform transition-all duration-300 ease-out shadow-md hover:shadow-lg
              ${isSaving 
                ? 'bg-gray-200 text-gray-500 cursor-not-allowed' 
                : 'bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 text-white hover:from-indigo-600 hover:via-purple-600 hover:to-pink-600 hover:scale-102'
              }
            `}
            title={`Cambiar a ${dirState === 'sp-gn' ? 'Guaraní → Español' : 'Español → Guaraní'}`}
          >
            {/* Left flag/emoji */}
            <span className="text-sm">
              {dirState === 'sp-gn' ? '🇪🇸' : '🇵🇾'}
            </span>
            
            {/* Swap icon */}
            <div className={`relative ${!isSaving && 'group-hover:rotate-180'} transition-transform duration-500`}>
              <svg 
                xmlns="http://www.w3.org/2000/svg" 
                className="h-4 w-4" 
                fill="none" 
                viewBox="0 0 24 24" 
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m0-4l4-4" />
              </svg>
            </div>
            
            {/* Right flag/emoji */}
            <span className="text-sm">
              {dirState === 'sp-gn' ? '🇵🇾' : '🇪🇸'}
            </span>
            
            {/* Text label */}
            <span className="text-xs font-semibold">
              {dirState === 'sp-gn' ? 'ES → GN' : 'GN → ES'}
            </span>

            {/* Shimmer effect when not disabled */}
            {!isSaving && (
              <div className="absolute inset-0 rounded-lg bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000 ease-out"></div>
            )}
          </button>
          
          {isSaving && (
            <div className="flex items-center gap-2 text-xs text-gray-500">
              <div className="animate-spin w-4 h-4 border-2 border-gray-300 border-t-gray-600 rounded-full"></div>
              <span>Cambiando...</span>
            </div>
          )}
        </div>
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
          <span>Fuente: {current.source}</span>
          <div className="flex items-center gap-4">
            {current.validation_count !== undefined && (
              <span>
                Evaluaciones: {current.validation_count}
              </span>
            )}

            {/* Suggestion info */}
            {current.suggestion_count !== undefined && (
              <span className="text-sm text-gray-600">
                Sugerencias: {current.suggestion_count}
              </span>
            )}

            {current.user_has_suggested && (
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