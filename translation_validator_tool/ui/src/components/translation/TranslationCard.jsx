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
        <div className="mt-2 flex items-center justify-center gap-3">
          <button
            onClick={toggleDirection}
            className={`text-xs px-3 py-1 rounded-full border border-gray-200 ${isSaving ? 'bg-gray-200 cursor-not-allowed' : 'bg-gray-100 hover:bg-gray-200'}`}
            disabled={isSaving}
            title="Cambiar dirección / ver par"
          >
            {dirState === 'sp-gn' ? 'Español → Guaraní' : 'Guaraní → Español'}
          </button>
          {isSaving && <span className="text-xs text-gray-500">Guardando...</span>}
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