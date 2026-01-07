import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import Navbar from '../components/common/Navbar';

const PRODIGY_MANAGER_URL = import.meta.env.VITE_PRODIGY_PROXY_URL || 'http://localhost:8085';
const POS_PORT = import.meta.env.VITE_PRODIGY_POS_PORT || '8080';
const FEATURES_PORT = import.meta.env.VITE_PRODIGY_FEATURES_PORT || '8081';
const RELATIONS_PORT = import.meta.env.VITE_PRODIGY_RELATIONS_PORT || '8082';

const SERVICES = {
  pos: { name: 'POS Tagging', description: 'Etiquetado morfosintáctico', port: POS_PORT, step: 1 },
  features: { name: 'Features', description: 'Características morfológicas', port: FEATURES_PORT, step: 2 },
  relations: { name: 'Relations', description: 'Relaciones sintácticas', port: RELATIONS_PORT, step: 3 },
};

const TOTAL_BATCHES = 60;
const BATCH_SIZE = 50;

const ProdigyPage = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [selectedBatch, setSelectedBatch] = useState(1);
  const [selectedService, setSelectedService] = useState('pos');
  const [isStarting, setIsStarting] = useState(false);
  const [startError, setStartError] = useState(null);
  const [runningServices, setRunningServices] = useState({});
  
  // Estado para configuración de buffer
  const [bufferConfig, setBufferConfig] = useState({
    instant_submit: false,
    batch_size: 3,
  });
  const [showBufferConfig, setShowBufferConfig] = useState(false);
  const [savingConfig, setSavingConfig] = useState(false);
  const [configError, setConfigError] = useState(null);
  const [configSuccess, setConfigSuccess] = useState(false);

  // Verificar si el usuario es admin (is_superuser del backend o role === 'admin')
  const isAdmin = user?.is_superuser === true || user?.role === 'admin';

  useEffect(() => {
    const init = async () => {
      await Promise.all([
        fetchRunningServices(),
        fetchBufferConfig(),
      ]);
      setLoading(false);
    };
    init();
    const interval = setInterval(fetchRunningServices, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchRunningServices = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${PRODIGY_MANAGER_URL}/api/services`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setRunningServices(data.services || {});
      } else {
        setRunningServices({});
      }
    } catch (error) {
      console.log('No se pudo conectar al Prodigy Manager');
      setRunningServices({});
    }
  };

  const fetchBufferConfig = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${PRODIGY_MANAGER_URL}/api/config/buffer`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setBufferConfig(data.config || bufferConfig);
      }
    } catch (error) {
      console.log('No se pudo obtener configuración de buffer');
    }
  };

  const saveBufferConfig = async () => {
    setSavingConfig(true);
    setConfigError(null);
    setConfigSuccess(false);
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${PRODIGY_MANAGER_URL}/api/config/buffer`, {
        method: 'POST',
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(bufferConfig),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Error guardando configuración');
      setConfigSuccess(true);
      // Mensaje persiste más tiempo para indicar necesidad de reinicio
      setTimeout(() => setConfigSuccess(false), 8000);
    } catch (error) {
      setConfigError(error.message);
    } finally {
      setSavingConfig(false);
    }
  };

  const resetBufferConfig = async () => {
    setSavingConfig(true);
    setConfigError(null);
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${PRODIGY_MANAGER_URL}/api/config/buffer/reset`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Error restableciendo configuración');
      setBufferConfig(data.config);
      setConfigSuccess(true);
      setTimeout(() => setConfigSuccess(false), 8000);
    } catch (error) {
      setConfigError(error.message);
    } finally {
      setSavingConfig(false);
    }
  };

  // Reiniciar todos los servicios activos para aplicar nueva config
  const restartAllServices = async () => {
    setIsStarting(true);
    setStartError(null);
    const activeServices = Object.entries(runningServices)
      .filter(([_, info]) => info?.running)
      .map(([service, info]) => ({ service, batch: info.batch || selectedBatch }));
    
    try {
      const token = localStorage.getItem('access_token');
      // Detener todos
      for (const { service } of activeServices) {
        await fetch(`${PRODIGY_MANAGER_URL}/api/stop-prodigy/${service}`, {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` }
        });
      }
      // Esperar un momento
      await new Promise(r => setTimeout(r, 2000));
      // Reiniciar todos
      for (const { service, batch } of activeServices) {
        await fetch(`${PRODIGY_MANAGER_URL}/api/start-prodigy`, {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
          body: JSON.stringify({ recipe: 'batch', annotation_type: service, batch_number: batch })
        });
        await new Promise(r => setTimeout(r, 1000));
      }
      setConfigSuccess(true);
      setTimeout(() => setConfigSuccess(false), 3000);
    } catch (error) {
      setStartError(`Error reiniciando: ${error.message}`);
    } finally {
      setIsStarting(false);
      setTimeout(fetchRunningServices, 2000);
    }
  };

  const isServiceOnline = (service) => {
    return runningServices[service]?.running === true;
  };

  const startProdigyService = async (service, batch) => {
    setIsStarting(true);
    setStartError(null);
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${PRODIGY_MANAGER_URL}/api/start-prodigy`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ recipe: 'batch', annotation_type: service, batch_number: batch })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Error iniciando servicio');
      setTimeout(fetchRunningServices, 2000);
      return data;
    } catch (error) {
      setStartError(error.message);
      throw error;
    } finally {
      setIsStarting(false);
    }
  };

  const stopProdigyService = async (service) => {
    try {
      const token = localStorage.getItem('access_token');
      await fetch(`${PRODIGY_MANAGER_URL}/api/stop-prodigy/${service}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setTimeout(fetchRunningServices, 1000);
    } catch (error) {
      console.error('Error deteniendo servicio:', error);
    }
  };

  const openProdigyService = async (service) => {
    const config = SERVICES[service];
    if (!config) return;
    const token = localStorage.getItem('access_token');
    if (!token) { alert('No hay sesión activa'); return; }
    
    // Solo admins pueden iniciar servicios automáticamente
    if (!isServiceOnline(service)) {
      if (!isAdmin) {
        alert('El servicio no está activo. Contacta a un administrador para iniciarlo.');
        return;
      }
      try {
        await startProdigyService(service, selectedBatch);
        await new Promise(resolve => setTimeout(resolve, 3000));
      } catch (error) {
        alert(`Error: ${error.message}`);
        return;
      }
    }
    
    const username = user?.username || user?.email || 'annotator';
    const proxyUrl = `${PRODIGY_MANAGER_URL}/?token=${encodeURIComponent(token)}&service=${service}&session=${encodeURIComponent(username)}`;
    window.open(proxyUrl, `prodigy_${service}`, 'width=1400,height=900');
  };

  const onlineCount = Object.keys(SERVICES).filter(key => isServiceOnline(key)).length;

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100">
        <Navbar />
        <div className="flex items-center justify-center" style={{ height: 'calc(100vh - 64px)' }}>
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Cargando...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <Navbar />
      
      <div className="max-w-6xl mx-auto px-4 py-6">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Sistema de Anotación Guaraní</h1>
          <p className="text-gray-500 text-sm">{TOTAL_BATCHES} lotes × {BATCH_SIZE} oraciones = {TOTAL_BATCHES * BATCH_SIZE} total</p>
        </div>

        {/* Status Bar */}
        <div className={`card mb-6 flex items-center justify-between ${onlineCount > 0 ? 'border-l-4 border-green-500' : 'border-l-4 border-gray-300'}`}>
          <div className="flex items-center gap-3">
            <span className={`inline-block w-3 h-3 rounded-full ${onlineCount > 0 ? 'bg-green-500' : 'bg-gray-400'}`}></span>
            <span className="font-medium text-gray-700">{onlineCount}/3 servicios activos</span>
          </div>
          <button 
            onClick={fetchRunningServices}
            className="text-sm text-blue-600 hover:text-blue-800"
          >
            ↻ Actualizar
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Panel - Configuration (Solo para Admins) */}
          <div className="space-y-6">
            {/* Config Card - Solo visible para admins */}
            {isAdmin ? (
              <div className="card">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">
                  <span className="mr-2">⚙️</span>Panel de Administración
                </h2>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Tipo de Anotación</label>
                    <select
                      value={selectedService}
                      onChange={(e) => setSelectedService(e.target.value)}
                      className="input"
                    >
                      {Object.entries(SERVICES).map(([key, config]) => (
                        <option key={key} value={key}>{config.step}. {config.name}</option>
                      ))}
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Número de Lote (1-{TOTAL_BATCHES})</label>
                    <input
                      type="number"
                      min="1"
                      max={TOTAL_BATCHES}
                      value={selectedBatch}
                      onChange={(e) => setSelectedBatch(Math.max(1, Math.min(TOTAL_BATCHES, parseInt(e.target.value) || 1)))}
                      className="input"
                    />
                  </div>

                  <button
                    onClick={() => startProdigyService(selectedService, selectedBatch)}
                    disabled={isStarting}
                    className={`w-full btn-primary ${isStarting ? 'opacity-50 cursor-not-allowed' : ''}`}
                  >
                    {isStarting ? 'Iniciando...' : 'Iniciar Servicio'}
                  </button>
                  
                  {startError && (
                    <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                      {startError}
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="card bg-blue-50 border-blue-200">
                <div className="flex items-start gap-3">
                  <span className="text-2xl">📝</span>
                  <div>
                    <h3 className="font-semibold text-blue-900">Modo Anotador</h3>
                    <p className="text-sm text-blue-700 mt-1">
                      Puedes abrir los servicios de anotación que estén activos. 
                      Contacta a un administrador si necesitas iniciar un servicio.
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Quick Selection - Solo visible para admins */}
            {isAdmin && (
              <div className="card">
                <h3 className="text-sm font-medium text-gray-700 mb-3">Selección rápida de lote</h3>
                <div className="flex flex-wrap gap-2">
                  {[1, 5, 10, 20, 30, 40, 50, 60].map(batch => (
                    <button
                      key={batch}
                      onClick={() => setSelectedBatch(batch)}
                      className={`px-3 py-1.5 rounded text-sm font-medium transition-colors ${
                        selectedBatch === batch 
                          ? 'bg-blue-600 text-white' 
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {batch}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Configuración de Buffer - Solo visible para admins */}
            {isAdmin && (
              <div className="card">
                <div 
                  className="flex items-center justify-between cursor-pointer"
                  onClick={() => setShowBufferConfig(!showBufferConfig)}
                >
                  <h3 className="text-sm font-medium text-gray-700 flex items-center gap-2">
                    <span>💾</span> Configuración de Buffer
                  </h3>
                  <span className={`transform transition-transform ${showBufferConfig ? 'rotate-180' : ''}`}>
                    ▼
                  </span>
                </div>
                
                {showBufferConfig && (
                  <div className="mt-4 space-y-4 border-t pt-4">
                    {/* Instant Submit Toggle */}
                    <div className="flex items-center justify-between">
                      <div>
                        <label className="text-sm font-medium text-gray-700">Envío instantáneo</label>
                        <p className="text-xs text-gray-500">Guardar cada anotación inmediatamente</p>
                      </div>
                      <button
                        onClick={() => setBufferConfig(prev => ({ ...prev, instant_submit: !prev.instant_submit }))}
                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                          bufferConfig.instant_submit ? 'bg-blue-600' : 'bg-gray-300'
                        }`}
                      >
                        <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                          bufferConfig.instant_submit ? 'translate-x-6' : 'translate-x-1'
                        }`} />
                      </button>
                    </div>

                    {/* Batch Size Slider - Solo visible si instant_submit está desactivado */}
                    {!bufferConfig.instant_submit && (
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <label className="text-sm font-medium text-gray-700">Tamaño del buffer</label>
                          <span className="text-sm font-bold text-blue-600">{bufferConfig.batch_size}</span>
                        </div>
                        <input
                          type="range"
                          min="1"
                          max="10"
                          value={bufferConfig.batch_size}
                          onChange={(e) => setBufferConfig(prev => ({ ...prev, batch_size: parseInt(e.target.value) }))}
                          className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                        />
                        <div className="flex justify-between text-xs text-gray-400 mt-1">
                          <span>1</span>
                          <span>5</span>
                          <span>10</span>
                        </div>
                        <p className="text-xs text-gray-500 mt-2">
                          Número de anotaciones a acumular antes de enviar al servidor
                        </p>
                      </div>
                    )}

                    {/* Estado visual del modo */}
                    <div className={`p-3 rounded-lg text-sm ${
                      bufferConfig.instant_submit 
                        ? 'bg-green-50 border border-green-200 text-green-700' 
                        : 'bg-blue-50 border border-blue-200 text-blue-700'
                    }`}>
                      {bufferConfig.instant_submit ? (
                        <span>⚡ <strong>Modo instantáneo:</strong> Cada anotación se guarda inmediatamente</span>
                      ) : (
                        <span>📦 <strong>Modo buffer:</strong> Se acumulan {bufferConfig.batch_size} anotaciones antes de enviar</span>
                      )}
                    </div>

                    {/* Botones de acción */}
                    <div className="flex gap-2">
                      <button
                        onClick={saveBufferConfig}
                        disabled={savingConfig}
                        className={`flex-1 btn-primary text-sm ${savingConfig ? 'opacity-50 cursor-not-allowed' : ''}`}
                      >
                        {savingConfig ? 'Guardando...' : 'Guardar'}
                      </button>
                      <button
                        onClick={resetBufferConfig}
                        disabled={savingConfig}
                        className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
                      >
                        Restablecer
                      </button>
                    </div>

                    {/* Mensajes de éxito/error */}
                    {configSuccess && (
                      <div className="space-y-2">
                        <div className="p-2 bg-green-50 border border-green-200 rounded text-green-700 text-sm text-center">
                          ✓ Configuración guardada
                        </div>
                        {Object.values(runningServices).some(s => s?.running) && (
                          <div className="p-2 bg-amber-50 border border-amber-200 rounded text-amber-700 text-sm">
                            <p className="font-medium">⚠️ Servicios activos detectados</p>
                            <p className="text-xs mt-1">Los cambios se aplicarán al reiniciar los servicios.</p>
                            <button
                              onClick={restartAllServices}
                              disabled={isStarting}
                              className="mt-2 w-full py-1.5 bg-amber-500 hover:bg-amber-600 text-white rounded text-xs font-medium transition-colors disabled:opacity-50"
                            >
                              {isStarting ? 'Reiniciando...' : '🔄 Reiniciar servicios ahora'}
                            </button>
                          </div>
                        )}
                      </div>
                    )}
                    {configError && (
                      <div className="p-2 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
                        {configError}
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* User Info */}
            <div className="card">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center text-white font-bold">
                  {(user?.username || user?.email || 'U')[0].toUpperCase()}
                </div>
                <div>
                  <p className="font-medium text-gray-900">{user?.username || user?.email}</p>
                  <p className="text-xs text-gray-500">{isAdmin ? 'Administrador' : 'Anotador'}</p>
                </div>
              </div>
            </div>

            {/* Indicador de Buffer para todos los usuarios */}
            {!isAdmin && (
              <div className="card bg-gray-50">
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <span>{bufferConfig.instant_submit ? '⚡' : '📦'}</span>
                  <span>
                    {bufferConfig.instant_submit 
                      ? 'Guardado instantáneo' 
                      : `Buffer: ${bufferConfig.batch_size} anotaciones`
                    }
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* Right Panel - Services */}
          <div className="lg:col-span-2 space-y-4">
            {/* Pipeline Flow */}
            <div className="card">
              <div className="flex items-center justify-center gap-4">
                {Object.entries(SERVICES).map(([key, config], index) => (
                  <div key={key} className="flex items-center">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                      isServiceOnline(key) 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-gray-100 text-gray-600'
                    }`}>
                      {config.step}. {config.name} {isServiceOnline(key) && '✓'}
                    </span>
                    {index < 2 && <span className="mx-2 text-gray-400">→</span>}
                  </div>
                ))}
              </div>
            </div>

            {/* Service Cards */}
            {Object.entries(SERVICES).map(([key, config]) => {
              const isOnline = isServiceOnline(key);
              const runningInfo = runningServices[key];
              
              return (
                <div key={key} className={`card ${isOnline ? 'border-l-4 border-green-500' : ''}`}>
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="font-semibold text-gray-900">{config.name}</h3>
                        <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                          isOnline ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'
                        }`}>
                          {isOnline ? 'Online' : 'Offline'}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600">{config.description}</p>
                      {runningInfo && isOnline && (
                        <p className="text-xs text-gray-500 mt-1">Lote {runningInfo.batch || '?'} • Puerto {runningInfo.port || config.port}</p>
                      )}
                    </div>
                    
                    <div className="flex items-center gap-2">
                      {isOnline ? (
                        <>
                          {/* Botón Detener - Solo para admins */}
                          {isAdmin && (
                            <button
                              onClick={() => stopProdigyService(key)}
                              className="btn-danger text-sm"
                            >
                              Detener
                            </button>
                          )}
                          <button
                            onClick={() => openProdigyService(key)}
                            className="btn-success"
                          >
                            Abrir
                          </button>
                        </>
                      ) : (
                        /* Servicio offline */
                        isAdmin ? (
                          <button
                            onClick={() => openProdigyService(key)}
                            className="btn-primary"
                          >
                            Iniciar y Abrir
                          </button>
                        ) : (
                          <span className="text-sm text-gray-400 italic">
                            No disponible
                          </span>
                        )
                      )}
                    </div>
                  </div>
                </div>
              );
            })}

            {/* Keyboard Shortcuts */}
            <div className="card bg-gray-800 text-white">
              <h3 className="font-medium mb-3">Atajos de teclado en Prodigy</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                <div><kbd className="px-2 py-1 bg-gray-700 rounded mr-2">A</kbd>Aceptar</div>
                <div><kbd className="px-2 py-1 bg-gray-700 rounded mr-2">X</kbd>Rechazar</div>
                <div><kbd className="px-2 py-1 bg-gray-700 rounded mr-2">Space</kbd>Ignorar</div>
                <div><kbd className="px-2 py-1 bg-gray-700 rounded mr-2">⌫</kbd>Deshacer</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProdigyPage;
