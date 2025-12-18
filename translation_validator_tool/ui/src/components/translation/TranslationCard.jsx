import { useState, useEffect } from 'react';
import { translationsAPI, suggestionsAPI } from '../../services/api';
import { useAuth } from '../../hooks/useAuth';
import { ArrowsRightLeftIcon, DocumentTextIcon } from '@heroicons/react/24/outline';
import { CheckIcon } from '@heroicons/react/24/solid';
import guaraniTooltips from '../../config/guaraniTooltips';
import ContextModal from './ContextModal';

const TranslationCard = ({ translation, onDirectionChange, onReplace, onValidateSuggestion, selectedSuggestion, onClearSelection, onCategoryChange }) => {
  const { user } = useAuth();
  const [current, setCurrent] = useState(translation || null);
  const [suggestions, setSuggestions] = useState([]);
  const [isSaving, setIsSaving] = useState(false);
  const [dirState, setDirState] = useState('sp-gn');
  const [selectedLocal, setSelectedLocal] = useState(null);
  const [forceOriginal, setForceOriginal] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState(null);
  
  // Context modal states
  const [showContextModal, setShowContextModal] = useState(false);
  const [contextLoading, setContextLoading] = useState(false);
  const [prevTranslation, setPrevTranslation] = useState(null);
  const [nextTranslation, setNextTranslation] = useState(null);

  // Fetch context (previous and next original sentences)
  const fetchContext = async () => {
    if (!current?.id) return;
    setContextLoading(true);
    setPrevTranslation(null);
    setNextTranslation(null);
    
    try {
      // Use the context endpoint that returns only original sentences
      const res = await translationsAPI.getContext(current.id);
      const data = res?.data || res;
      
      if (data.previous) {
        setPrevTranslation(data.previous);
      }
      if (data.next) {
        setNextTranslation(data.next);
      }
    } catch (err) {
      console.warn('Could not fetch context translations', err);
    } finally {
      setContextLoading(false);
    }
  };

  const openContextModal = () => {
    setShowContextModal(true);
    fetchContext();
  };

  useEffect(() => {
    setCurrent(translation);
    setSelectedCategory(translation?.category || null);
  }, [translation]);
  useEffect(() => {
    // Clear any local selection when the translation changes
    setSelectedLocal(null);
    setForceOriginal(false);
  }, [translation]);

  // Keep direction state in sync with the provided translation when it changes
  useEffect(() => {
    if (translation && translation.direction) {
      setDirState(translation.direction);
    }
  }, [translation?.id]);

  useEffect(() => {
    // If parent clears selectedSuggestion, ensure we respect it; any change to
    // selectedSuggestion means user or parent intentionally selected something.
    setForceOriginal(false);
  }, [selectedSuggestion]);

  useEffect(() => {
    let mounted = true;
    let abortController = new AbortController();
    
    const ensureFull = async () => {
      if (!translation) return;
      if (translation.pair_is_complete !== undefined) return;
      try {
        setIsSaving(true);
        const res = await translationsAPI.getById(translation.id);
        const full = res?.data || res;
        if (mounted && full) setCurrent(full);
      } catch (e) {
        if (!abortController.signal.aborted) {
          console.warn('Could not fetch full translation with stats', e);
        }
      } finally {
        if (mounted) setIsSaving(false);
      }
    };

    const loadSuggestions = async () => {
      if (!translation || !translation.id) return;
      try {
        const res = await suggestionsAPI.getByTranslation(translation.id);
        const list = res?.data || [];
        if (mounted && !abortController.signal.aborted) setSuggestions(list);
      } catch (err) {
        if (!abortController.signal.aborted) {
          console.warn('Could not fetch suggestions for translation', err);
          if (mounted) setSuggestions([]);
        }
      }
    };

    // Only run if we have a translation and it's different from current
    if (translation && (!current || current.id !== translation.id)) {
      ensureFull();
      loadSuggestions();
    }
    
    return () => { 
      mounted = false; 
      abortController.abort();
    };
  }, [translation?.id]); // Only depend on translation.id to avoid unnecessary re-runs

  // Keyboard shortcut for context modal (Ctrl+Shift+C)
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.ctrlKey && e.shiftKey && e.key.toLowerCase() === 'c') {
        e.preventDefault();
        setShowContextModal(prev => !prev);
      }
      // Also ESC to close
      if (e.key === 'Escape' && showContextModal) {
        setShowContextModal(false);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [showContextModal]);

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

    // Try to fetch the paired translation from the API and ask parent to replace
    const doSwap = async () => {
      setIsSaving(true);
      try {
        const res = await translationsAPI.getPair(current.id);
        const pair = res?.data || res;
        // Inform parent to replace the current translation with its pair
        if (pair && typeof onReplace === 'function') {
          onReplace(pair);
        }
        // Update local direction state so the UI arrow/text updates immediately
        setDirState(next);
        // Clear any local selection when switching directions
        setSelectedLocal(null);
        setForceOriginal(false);
      } catch (err) {
        console.warn('Could not fetch pair translation', err);
      } finally {
        setIsSaving(false);
      }
    };

    doSwap();
  };

  const handleCategorySelect = (category) => {
    setSelectedCategory(category);
    // Notify parent component about category selection
    if (typeof onCategoryChange === 'function') {
      onCategoryChange(category);
    }
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
        {/*<div className="text-xs text-gray-500 mt-1">ID: {current.id}</div>*/}
      </div>

      {/* Context Button */}
      <div className="flex justify-center mb-3">
        <button
          onClick={() => setShowContextModal(true)}
          className="flex items-center gap-1.5 px-3 py-1.5 text-gray-600 border border-gray-300 bg-white hover:bg-gray-50 rounded text-xs"
          title="Ver contexto (Ctrl+Shift+C)"
        >
          <DocumentTextIcon className="h-4 w-4" />
          <span>Contexto</span>
        </button>
      </div>

      {/* Context Modal */}
      <ContextModal 
        translation={current}
        isOpen={showContextModal}
        onClose={() => setShowContextModal(false)}
      />

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
                              (() => {
                                const reachedLimit = (s.validation_count ?? 0) >= 3;
                                const alreadyValidated = !!s.user_has_validated;
                                const disabled = alreadyValidated || reachedLimit;
                                const btnClass = disabled ? 'bg-gray-300 cursor-not-allowed text-gray-700' : 'bg-blue-600 hover:bg-blue-700 text-white';
                                const title = alreadyValidated ? 'Ya validaste esta sugerencia' : (reachedLimit ? 'Esta sugerencia ya alcanzó el límite de 3 validaciones' : 'Validar sugerencia');

                                return (
                                  <button
                                    onClick={() => {
                                      // locally select and also notify parent
                                      setSelectedLocal(s);
                                      setForceOriginal(false);
                                      if (typeof onValidateSuggestion === 'function') onValidateSuggestion(s);
                                    }}
                                    className={`text-xs px-3 py-1 rounded-md ${btnClass}`}
                                    disabled={disabled}
                                    title={title}
                                  >
                                    {alreadyValidated ? 'Validada' : (reachedLimit ? 'Límite alcanzado' : 'Validar')}
                                  </button>
                                );
                              })()
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
          <div className={`bg-white rounded-lg p-4 min-h-[120px] shadow-sm ${!displayRightText ? 'border-2 border-dashed border-orange-300 bg-orange-50' : 'border border-green-100'}`}>
            {!displayRightText ? (
              <div className="flex flex-col items-center justify-center h-full text-center">
                <span className="text-3xl mb-2">❓</span>
                <p className="text-orange-700 font-medium">Traducción pendiente</p>
                <p className="text-xs text-orange-600 mt-1">Se necesita una traducción al español</p>
              </div>
            ) : (
              <p className="text-gray-900 leading-relaxed">{displayRightText}</p>
            )}
          </div>
        </div>
        
      </div>

      {/* Category classification for Guarani sentences - only for gn-sp direction */}
      {dirState === 'gn-sp' && (
        <div className="mt-6 bg-white border border-gray-200 rounded-lg shadow-sm">
          <div className="px-4 py-3 border-b border-gray-200 bg-gray-50">
            <h4 className="text-base font-semibold text-gray-800">
              Clasificación de la oración en Guaraní
            </h4>
            <p className="text-xs text-gray-600 mt-1">Selecciona la categoría que mejor describe esta oración</p>
          </div>
          
          <div className="p-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <button 
                onClick={() => handleCategorySelect('guarani_puro')}
                className={`group relative p-4 border-2 rounded-lg transition-all duration-200 ${
                  selectedCategory === 'guarani_puro'
                    ? 'border-indigo-500 bg-indigo-50 shadow-md'
                    : 'border-gray-200 bg-white hover:border-indigo-300 hover:bg-indigo-50 hover:shadow-sm'
                }`}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <div className={`text-sm font-semibold mb-1 ${selectedCategory === 'guarani_puro' ? 'text-indigo-900' : 'text-gray-800'}`}>
                      Guaraní Puro
                    </div>
                    <div className={`text-xs ${selectedCategory === 'guarani_puro' ? 'text-indigo-700' : 'text-gray-600'}`}>
                      Académico / Tradicional
                    </div>
                  </div>
                  {selectedCategory === 'guarani_puro' && (
                    <div className="flex-shrink-0 ml-2">
                      <div className="w-6 h-6 bg-indigo-500 rounded-full flex items-center justify-center">
                        <CheckIcon className="h-4 w-4 text-white" />
                      </div>
                    </div>
                  )}
                </div>
                <div className={`text-xs leading-relaxed ${selectedCategory === 'guarani_puro' ? 'text-indigo-600' : 'text-gray-500'}`}>
                  Forma tradicional y académica del guaraní
                </div>
                
                {/* Tooltip (configurable) */}
                <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 text-white text-xs rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 w-72 z-10">
                  <div className="font-semibold mb-1">{guaraniTooltips.guarani_puro.title}</div>
                  <div className="text-gray-200">{guaraniTooltips.guarani_puro.desc}</div>
                  {guaraniTooltips.guarani_puro.example && (
                    <div className="text-gray-300 italic text-[10px] mt-1">{guaraniTooltips.guarani_puro.example}</div>
                  )}
                  <div className="absolute top-full left-1/2 transform -translate-x-1/2 -mt-1">
                    <div className="border-4 border-transparent border-t-gray-900"></div>
                  </div>
                </div>
              </button>
              
              <button 
                onClick={() => handleCategorySelect('jopara')}
                className={`group relative p-4 border-2 rounded-lg transition-all duration-200 ${
                  selectedCategory === 'jopara'
                    ? 'border-green-500 bg-green-50 shadow-md'
                    : 'border-gray-200 bg-white hover:border-green-300 hover:bg-green-50 hover:shadow-sm'
                }`}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <div className={`text-sm font-semibold mb-1 ${selectedCategory === 'jopara' ? 'text-green-900' : 'text-gray-800'}`}>
                      Jopara
                    </div>
                    <div className={`text-xs ${selectedCategory === 'jopara' ? 'text-green-700' : 'text-gray-600'}`}>
                      Mezcla léxica GN-ES
                    </div>
                  </div>
                  {selectedCategory === 'jopara' && (
                    <div className="flex-shrink-0 ml-2">
                      <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
                        <CheckIcon className="h-4 w-4 text-white" />
                      </div>
                    </div>
                  )}
                </div>
                <div className={`text-xs leading-relaxed ${selectedCategory === 'jopara' ? 'text-green-600' : 'text-gray-500'}`}>
                  Combinación de guaraní y español
                </div>
                
                {/* Tooltip (configurable) */}
                <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 text-white text-xs rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 w-72 z-10">
                  <div className="font-semibold mb-1">{guaraniTooltips.jopara.title}</div>
                  <div className="text-gray-200 mb-2">{guaraniTooltips.jopara.desc}</div>
                  {guaraniTooltips.jopara.example && (
                    <div className="text-gray-300 italic text-[10px]">{guaraniTooltips.jopara.example}</div>
                  )}
                  <div className="absolute top-full left-1/2 transform -translate-x-1/2 -mt-1">
                    <div className="border-4 border-transparent border-t-gray-900"></div>
                  </div>
                </div>
              </button>
              
              <button 
                onClick={() => handleCategorySelect('jehea')}
                className={`group relative p-4 border-2 rounded-lg transition-all duration-200 ${
                  selectedCategory === 'jehea'
                    ? 'border-orange-500 bg-orange-50 shadow-md'
                    : 'border-gray-200 bg-white hover:border-orange-300 hover:bg-orange-50 hover:shadow-sm'
                }`}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <div className={`text-sm font-semibold mb-1 ${selectedCategory === 'jehea' ? 'text-orange-900' : 'text-gray-800'}`}>
                      Jehe'a
                    </div>
                    <div className={`text-xs ${selectedCategory === 'jehea' ? 'text-orange-700' : 'text-gray-600'}`}>
                      Guaraní paraguayo
                    </div>
                  </div>
                  {selectedCategory === 'jehea' && (
                    <div className="flex-shrink-0 ml-2">
                      <div className="w-6 h-6 bg-orange-500 rounded-full flex items-center justify-center">
                        <CheckIcon className="h-4 w-4 text-white" />
                      </div>
                    </div>
                  )}
                </div>
                <div className={`text-xs leading-relaxed ${selectedCategory === 'jehea' ? 'text-orange-600' : 'text-gray-500'}`}>
                  Forma cotidiana hablada en Paraguay
                </div>
                
                {/* Tooltip (configurable) */}
                <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 text-white text-xs rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 w-72 z-10">
                  <div className="font-semibold mb-1">{guaraniTooltips.jehea.title}</div>
                  <div className="text-gray-200 mb-2">{guaraniTooltips.jehea.desc}</div>
                  {guaraniTooltips.jehea.example && (
                    <div className="text-gray-300 text-[10px]">{guaraniTooltips.jehea.example}</div>
                  )}
                  <div className="absolute top-full left-1/2 transform -translate-x-1/2 -mt-1">
                    <div className="border-4 border-transparent border-t-gray-900"></div>
                  </div>
                </div>
              </button>
            </div>
            
            {selectedCategory && (
              <div className="mt-4 p-3 bg-gray-50 border border-gray-200 rounded-lg">
                <div className="flex items-center gap-2 text-sm">
                  <CheckIcon className="h-4 w-4 text-green-600 flex-shrink-0" />
                  <span className="text-gray-700">
                    Categoría seleccionada: <span className="font-semibold text-gray-900">{
                      selectedCategory === 'guarani_puro' ? 'Guaraní Puro' :
                      selectedCategory === 'jopara' ? 'Jopara' :
                      'Jehe\'a'
                    }</span>
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Additional info */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="flex justify-between items-center text-sm text-gray-600">
          <span>Fuente: {current.source}</span>
          <div className="flex items-center gap-4">
            {/*current.validation_count !== undefined && (
              <span>Evaluaciones: {current.validation_count}</span>
            )*/}

            {/*current.suggestion_count !== undefined && (
              <span className="text-sm text-gray-600">Sugerencias: {current.suggestion_count}</span>
            )*/}

            {current.user_has_suggested && (
              <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">✓ Ya sugeriste para esta traducción</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TranslationCard;