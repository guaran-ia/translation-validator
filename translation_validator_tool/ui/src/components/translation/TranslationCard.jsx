import { useState, useEffect } from 'react';
import { translationsAPI, suggestionsAPI } from '../../services/api';
import { useAuth } from '../../hooks/useAuth';
import { ArrowsRightLeftIcon } from '@heroicons/react/24/outline';

const TranslationCard = ({ translation, onDirectionChange, onReplace, onValidateSuggestion, selectedSuggestion }) => {
  const [current, setCurrent] = useState(translation);
  useEffect(() => {
    setCurrent(translation);
  }, [translation]);

  // Ensure we have the full TranslationWithStats when the card mounts or when
  // the provided translation prop changes. Some parent callers pass a lightweight
  // TranslationResponse without `pair_is_complete` / stats; fetch the full
  // translation when those fields are missing so the banner can be shown.
  useEffect(() => {
    let mounted = true;
    const ensureFull = async () => {
      if (!translation) return;
      // If the translation already includes pair_is_complete, no need to fetch
      if (translation.pair_is_complete !== undefined) return;
      try {
        setIsSaving(true);
        const res = await translationsAPI.getById(translation.id);
        const full = res?.data || res;
        if (mounted && full) setCurrent(full);
      } catch (e) {
        console.warn('Could not fetch full translation with stats', e);
      } finally {
        if (mounted) setIsSaving(false);
      }
    };
    ensureFull();
    // Also load suggestions for this translation so they can be displayed above
    const loadSuggestions = async () => {
      if (!translation || !translation.id) return;
      try {
        const res = await suggestionsAPI.getByTranslation(translation.id);
        const list = res?.data || [];
        if (mounted) setSuggestions(list);
      } catch (err) {
        console.warn('Could not fetch suggestions for translation', err);
        if (mounted) setSuggestions([]);
      }
    };
    loadSuggestions();
    return () => { mounted = false; };
  }, [translation]);

  const [suggestions, setSuggestions] = useState([]);

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
  const { user } = useAuth();

  // If a suggestion has been selected for validation, overlay its text onto the card
  let displayLeftText = leftText;
  let displayRightText = rightText;
  if (selectedSuggestion && selectedSuggestion.translation_id === current.id) {
    // If direction is Spanish -> Guarani
    if (dirState === 'sp-gn') {
      if (selectedSuggestion.suggested_spanish) displayLeftText = selectedSuggestion.suggested_spanish;
      if (selectedSuggestion.suggested_guarani) displayRightText = selectedSuggestion.suggested_guarani;
    } else {
      // gn-sp
      if (selectedSuggestion.suggested_guarani) displayLeftText = selectedSuggestion.suggested_guarani;
      if (selectedSuggestion.suggested_spanish) displayRightText = selectedSuggestion.suggested_spanish;
    }
  }

  const toggleDirection = async () => {
    // Try to fetch the paired translation (either direction). Backend provides /translations/pair/{id}
    try {
      setIsSaving(true);
      const res = await translationsAPI.getPair(current.id);
      const paired = res?.data || res;
      if (paired) {
        // The /pair endpoint returns a TranslationResponse (without pair stats).
        // Request the full TranslationWithStats for the paired id so the UI can show
        // whether the paired translation already has 3+ validations (pair_is_complete).
        try {
          const full = await translationsAPI.getById(paired.id);
          const pairedFull = full?.data || full;
          // Replace current with the full paired translation and notify parent
          setCurrent(pairedFull);
          const newDir = pairedFull.direction || 'sp-gn';
          setDirState(newDir);
          if (onDirectionChange) onDirectionChange(newDir);
          if (typeof onReplace === 'function') {
            onReplace(pairedFull);
          }
          return;
        } catch (errFull) {
          // If fetching full stats fails, fall back to using the paired object
          console.warn('Failed to fetch full paired translation with stats, using basic paired object', errFull);
          setCurrent(paired);
          const newDir = paired.direction || 'sp-gn';
          setDirState(newDir);
          if (onDirectionChange) onDirectionChange(newDir);
          if (typeof onReplace === 'function') {
            onReplace(paired);
          }
          return;
        }
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
        // update local current.direction and refresh full translation with stats
      try {
        const refreshed = await translationsAPI.getById(current.id);
        const refreshedData = refreshed?.data || refreshed;
        setCurrent(refreshedData);
      } catch (errRef) {
        // If refresh fails, at least update direction locally
        console.warn('Failed to refresh translation after direction update', errRef);
        setCurrent({ ...current, direction: newDir });
      }
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
        {/* If there are suggestions for this translation, show them above the card */}
        {suggestions && suggestions.length > 0 && (
          <div className="mx-auto mt-3 max-w-2xl bg-white border border-gray-100 px-4 py-3 rounded-lg text-sm text-gray-800">
            <div className="font-medium mb-2">Sugerencias existentes</div>
            <div className="space-y-2">
              {suggestions.map((s) => {
                const isSelected = selectedSuggestion && selectedSuggestion.id === s.id;
                return (
                <div key={s.id} className={`p-2 ${isSelected ? 'bg-white border-blue-300 shadow-md ring-2 ring-blue-200' : 'bg-gray-50 border-gray-100'} rounded flex flex-col md:flex-row md:items-start md:justify-between gap-2`}>
                  <div>
                    {s.suggested_guarani && (
                      <div className="text-sm text-gray-700"><strong>Guaraní:</strong> {s.suggested_guarani}</div>
                    )}
                    {s.suggested_spanish && (
                      <div className="text-sm text-gray-700"><strong>Español:</strong> {s.suggested_spanish}</div>
                    )}
                    <div className="text-xs text-gray-500 mt-1">Por usuario #{s.user_id} • {new Date(s.created_at).toLocaleString()}</div>
                  </div>

                  <div className="flex items-center gap-3">
                    <div className="text-xs text-gray-600">Validaciones: <strong>{s.validation_count ?? 0}</strong></div>
                    {/* If user is present, allow them to validate this suggestion (unless they authored it) */}
                    {user && s.user_id !== user.id && typeof onValidateSuggestion === 'function' && (
                      <button
                        onClick={() => onValidateSuggestion(s)}
                        className="text-xs px-2 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-60"
                        disabled={s.user_has_validated}
                        title={s.user_has_validated ? 'Ya validaste esta sugerencia' : 'Validar sugerencia'}
                      >
                        {s.user_has_validated ? 'Validada' : 'Validar sugerencia'}
                      </button>
                    )}

                    {/* If the user is the author, show a small badge */}
                    {user && s.user_id === user.id && (
                      <span className="text-xs px-2 py-1 bg-yellow-100 text-yellow-800 rounded">Tu sugerencia</span>
                    )}
                  </div>
                </div>
                )
              })}
            </div>
          </div>
        )}

        {/* Warning banner when the translation itself has reached the validation threshold */}
        {current.validation_count >= 3 && (
          <div className="mx-auto mt-3 max-w-2xl bg-yellow-50 border border-yellow-100 text-yellow-800 px-4 py-2 rounded-lg text-sm">
            <strong className="font-semibold">Aviso:</strong>{' '}
            Esta traducción ya tiene {current.validation_count} validaciones en su dirección, por lo tanto no se pueden añadir más validaciones.
          </div>
        )}
        <div className="mt-3 flex items-center justify-center gap-2">
          <button
            onClick={toggleDirection}
            disabled={isSaving}
            className={`px-2 py-1 rounded-sm text-[11px] border bg-white text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-blue-200 ${isSaving ? 'opacity-60 cursor-not-allowed' : ''}`}
            title={`Cambiar dirección`}
          >
            <div className="flex items-center gap-3 min-w-[140px]">
              <div className="flex-1 text-right">
                <span className="block text-[11px] font-medium text-gray-700">{dirState === 'sp-gn' ? 'ES' : 'GN'}</span>
              </div>

              <div className="flex-shrink-0 text-center">
                <ArrowsRightLeftIcon className="h-5 w-5 text-gray-700" />
              </div>

              <div className="flex-1 text-left">
                <span className="block text-[11px] font-medium text-gray-700">{dirState === 'sp-gn' ? 'GN' : 'ES'}</span>
              </div>
            </div>
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
            <h3 className="text-lg font-semibold text-gray-800">
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
            <h3 className="text-lg font-semibold text-gray-800">
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
            {/* Only show detailed stats to superusers (administrators). Validators should not see counts. */}
            {user?.is_superuser && current.validation_count !== undefined && (
              <span>
                Evaluaciones: {current.validation_count}
              </span>
            )}

            {user?.is_superuser && current.suggestion_count !== undefined && (
              <span className="text-sm text-gray-600">
                Sugerencias: {current.suggestion_count}
              </span>
            )}

            {/* The badge that indicates the current user has suggested should remain visible to that user */}
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