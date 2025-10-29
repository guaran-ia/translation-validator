import { useState, useEffect } from 'react';
import { translationsAPI, suggestionsAPI } from '../../services/api';
import { useAuth } from '../../hooks/useAuth';
import { ArrowsRightLeftIcon } from '@heroicons/react/24/outline';
import { CheckIcon } from '@heroicons/react/24/solid';

const TranslationCard = ({ translation, onDirectionChange, onReplace, onValidateSuggestion, selectedSuggestion, onClearSelection }) => {
  const { user } = useAuth();
  const [current, setCurrent] = useState(translation || null);
  const [suggestions, setSuggestions] = useState([]);
  const [isSaving, setIsSaving] = useState(false);
  const [dirState, setDirState] = useState('sp-gn');
  const [selectedLocal, setSelectedLocal] = useState(null);
  const [forceOriginal, setForceOriginal] = useState(false);

  useEffect(() => setCurrent(translation), [translation]);
  useEffect(() => {
    // Clear any local selection when the translation changes
    setSelectedLocal(null);
    setForceOriginal(false);
  }, [translation]);

  useEffect(() => {
    // If parent clears selectedSuggestion, ensure we respect it; any change to
    // selectedSuggestion means user or parent intentionally selected something.
    setForceOriginal(false);
  }, [selectedSuggestion]);

  useEffect(() => {
    let mounted = true;
    const ensureFull = async () => {
      if (!translation) return;
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

    ensureFull();
    loadSuggestions();
    return () => { mounted = false; };
  }, [translation]);

  if (!current) {
    return (
      <div className="card animate-pulse p-4">
        <div className="h-6 bg-gray-200 rounded mb-2 w-1/3" />
        <div className="h-40 bg-gray-100 rounded" />
      </div>
    );
  }

  const toggleDirection = () => {
    const next = dirState === 'sp-gn' ? 'gn-sp' : 'sp-gn';
    setDirState(next);
    if (typeof onDirectionChange === 'function') onDirectionChange(next);
  };

  const leftIsOriginal = dirState === 'sp-gn' ? 'spanish' : 'guarani';
  const rightIsTranslation = leftIsOriginal === 'spanish' ? 'guarani' : 'spanish';

  // If forceOriginal is true, ignore any selection (local or parent) and show original texts
  // Otherwise, if a suggestion is selected (locally or via prop), use its suggested fields to replace the displayed texts
  const activeSuggestion = forceOriginal ? null : (selectedLocal || selectedSuggestion || null);

  const displayLeftText = (() => {
    if (activeSuggestion) {
      if (leftIsOriginal === 'spanish' && activeSuggestion.suggested_spanish) return activeSuggestion.suggested_spanish;
      if (leftIsOriginal === 'guarani' && activeSuggestion.suggested_guarani) return activeSuggestion.suggested_guarani;
    }
    return leftIsOriginal === 'spanish' ? (current.spanish_text || '') : (current.guarani_text || '');
  })();

  const displayRightText = (() => {
    if (activeSuggestion) {
      if (rightIsTranslation === 'guarani' && activeSuggestion.suggested_guarani) return activeSuggestion.suggested_guarani;
      if (rightIsTranslation === 'spanish' && activeSuggestion.suggested_spanish) return activeSuggestion.suggested_spanish;
    }
    return rightIsTranslation === 'guarani' ? (current.guarani_text || '') : (current.spanish_text || '');
  })();

  return (
    <div className="card">
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
        <h2 className="text-xl font-semibold text-gray-800">Evalúa la siguiente traducción</h2>
        <div className="text-xs text-gray-500 mt-1">ID: {current.id}</div>
      </div>

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

      {/* Suggestions: show above the sentences now */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <h4 className="text-md font-medium text-gray-800">Sugerencias para esta dirección</h4>
          {((selectedLocal && selectedLocal.translation_id === current.id) || selectedSuggestion) && (
            <button onClick={() => { setSelectedLocal(null); setForceOriginal(true); if (typeof onClearSelection === 'function') onClearSelection(); }} className="text-sm px-2 py-1 bg-white border rounded text-gray-700">Revertir original</button>
          )}
        </div>

        <div className="bg-white border border-gray-100 rounded-lg p-3 shadow-sm">
          <div className="space-y-2">
            {(() => {
              const dirSuggestions = (suggestions || []).filter(s => s.direction === dirState).slice(0, 3);
              if (dirSuggestions.length === 0) {
                return <div className="text-sm text-gray-500">No hay sugerencias para esta dirección.</div>;
              }

              return dirSuggestions.map((s) => {
                const isSelected = !forceOriginal && ((selectedLocal && selectedLocal.id === s.id) || (selectedSuggestion && selectedSuggestion.id === s.id));
                return (
                  <div
                    key={s.id}
                    className={`p-3 rounded-lg border ${isSelected ? 'border-blue-300 shadow-lg ring-2 ring-blue-100' : 'border-gray-100'} bg-white transition-transform transform hover:-translate-y-0.5`}
                  >
                    <div className="flex items-start gap-3">
                      <div className="flex-1">
                        <div className="flex items-center justify-between gap-3">
                          <div className="space-y-0.5">
                            {s.suggested_spanish && <div className="text-sm text-gray-800 font-medium">{s.suggested_spanish}</div>}
                            {s.suggested_guarani && <div className="text-sm text-gray-700">{s.suggested_guarani}</div>}
                          </div>

                          <div className="flex flex-col items-end ml-2">
                            <div className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold bg-gray-100 text-gray-800">
                              <CheckIcon className="h-4 w-4 text-green-600" />
                              <span>{s.validation_count ?? 0}</span>
                            </div>
                          </div>
                        </div>

                        <div className="mt-2 flex items-center justify-between gap-3">
                          <div className="text-xs text-gray-500">Por usuario #{s.user_id} • {new Date(s.created_at).toLocaleString()}</div>

                          <div className="flex items-center gap-2">
                            {user && s.user_id === user.id && (
                              <span className="text-xs px-2 py-1 bg-yellow-100 text-yellow-800 rounded">Tu sugerencia</span>
                            )}

                            {user && s.user_id !== user.id && (
                              <button
                                onClick={() => {
                                  // locally select and also notify parent
                                  setSelectedLocal(s);
                                  setForceOriginal(false);
                                  if (typeof onValidateSuggestion === 'function') onValidateSuggestion(s);
                                }}
                                className={`text-xs px-3 py-1 rounded-md text-white ${s.user_has_validated ? 'bg-gray-300 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'}`}
                                disabled={s.user_has_validated}
                                title={s.user_has_validated ? 'Ya validaste esta sugerencia' : 'Validar sugerencia'}
                              >
                                {s.user_has_validated ? 'Validada' : 'Validar'}
                              </button>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              });
            })()}
          </div>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6 mt-6">
        {/* Left (original) */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-800">{leftIsOriginal === 'spanish' ? 'Español (original)' : 'Guaraní (original)'}</h3>
            <span className="text-xs px-2 py-1 rounded-full bg-blue-50 text-blue-700 border border-blue-100">Original</span>
          </div>
          <div className="bg-white border border-blue-100 rounded-lg p-4 min-h-[120px] shadow-sm">
            <p className="text-gray-900 leading-relaxed">{displayLeftText}</p>
          </div>
        </div>

        {/* Right (translation) */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-800">{rightIsTranslation === 'guarani' ? 'Guaraní' : 'Español'}</h3>
            <span className="text-xs px-2 py-1 rounded-full bg-green-50 text-green-700 border border-green-100">Traducción</span>
          </div>
          <div className="bg-white border border-green-100 rounded-lg p-4 min-h-[120px] shadow-sm">
            <p className="text-gray-900 leading-relaxed">{displayRightText}</p>
          </div>
        </div>
        
      </div>

      {/* Additional info */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="flex justify-between items-center text-sm text-gray-600">
          <span>Fuente: {current.source}</span>
          <div className="flex items-center gap-4">
            {user?.is_superuser && current.validation_count !== undefined && (
              <span>Evaluaciones: {current.validation_count}</span>
            )}

            {user?.is_superuser && current.suggestion_count !== undefined && (
              <span className="text-sm text-gray-600">Sugerencias: {current.suggestion_count}</span>
            )}

            {current.user_has_suggested && (
              <span className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded text-xs">Has sugerido esto</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TranslationCard;