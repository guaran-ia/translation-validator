import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import Navbar from '../components/common/Navbar';

// URL del proxy de Prodigy desde variable de entorno
const PRODIGY_PROXY_URL = import.meta.env.VITE_PRODIGY_PROXY_URL || 'http://localhost:8082';

const ProdigyPage = () => {
  const { user } = useAuth();
  const [prodigyInfo, setProdigyInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [prodigyStatus, setProdigyStatus] = useState('checking'); // 'checking', 'online', 'offline'

  useEffect(() => {
    fetchProdigySession();
    checkProdigyStatus();
  }, []);

  const fetchProdigySession = async () => {
    try {
      const response = await api.get('/prodigy/session');
      setProdigyInfo(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  const checkProdigyStatus = async () => {
    try {
      // Intentar conectar al proxy seguro de Prodigy
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3000);
      
      await fetch(`${PRODIGY_PROXY_URL}/`, { 
        method: 'HEAD',
        mode: 'no-cors',
        signal: controller.signal
      });
      clearTimeout(timeoutId);
      setProdigyStatus('online');
    } catch {
      setProdigyStatus('offline');
    }
  };

  const openProdigy = () => {
    if (prodigyInfo?.session_url) {
      window.open(prodigyInfo.session_url, '_blank', 'width=1400,height=900');
    }
  };

  const copyToken = () => {
    if (prodigyInfo?.token) {
      navigator.clipboard.writeText(prodigyInfo.token);
      alert('Token copiado al portapapeles');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Cargando sesión de Prodigy...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="bg-red-50 border-l-4 border-red-400 p-6 rounded-lg max-w-md">
          <div className="flex items-center">
            <svg className="h-6 w-6 text-red-400 mr-3" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <p className="text-red-800">{error}</p>
          </div>
          <button
            onClick={fetchProdigySession}
            className="mt-4 text-sm text-red-600 hover:text-red-800 font-medium"
          >
            Intentar de nuevo
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Navbar */}
      <Navbar />
      
      <div className="py-12 px-4">
        <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            🏷️ Anotación con Prodigy
          </h1>
          <p className="text-gray-600">
            Sistema de anotación POS para Guaraní
          </p>
        </div>

        {/* Prodigy Status Banner */}
        <div className={`mb-6 rounded-lg p-4 flex items-center justify-between ${
          prodigyStatus === 'online' 
            ? 'bg-green-50 border border-green-200' 
            : prodigyStatus === 'offline'
            ? 'bg-red-50 border border-red-200'
            : 'bg-gray-50 border border-gray-200'
        }`}>
          <div className="flex items-center gap-3">
            <div className={`w-3 h-3 rounded-full ${
              prodigyStatus === 'online' 
                ? 'bg-green-500 animate-pulse' 
                : prodigyStatus === 'offline'
                ? 'bg-red-500'
                : 'bg-gray-400 animate-pulse'
            }`}></div>
            <span className={`font-medium ${
              prodigyStatus === 'online' 
                ? 'text-green-800' 
                : prodigyStatus === 'offline'
                ? 'text-red-800'
                : 'text-gray-600'
            }`}>
              {prodigyStatus === 'online' && '✅ Prodigy Secure Proxy está activo'}
              {prodigyStatus === 'offline' && '❌ Prodigy no está corriendo'}
              {prodigyStatus === 'checking' && '🔄 Verificando estado...'}
            </span>
          </div>
          <button 
            onClick={checkProdigyStatus}
            className="text-sm text-gray-600 hover:text-gray-800 underline"
          >
            Refrescar
          </button>
        </div>

        {/* User Info Card */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-xl font-semibold text-gray-900">Tu sesión</h2>
              <p className="text-sm text-gray-600 mt-1">Información del usuario actual</p>
            </div>
            <div className={`px-4 py-2 rounded-full text-sm font-semibold ${
              prodigyInfo?.role === 'admin' 
                ? 'bg-red-100 text-red-800' 
                : 'bg-green-100 text-green-800'
            }`}>
              {prodigyInfo?.role === 'admin' ? '👑 Admin' : '✍️ Anotador'}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4 mb-6">
            <div>
              <span className="text-sm text-gray-600">Usuario:</span>
              <p className="font-semibold text-gray-900">{prodigyInfo?.username}</p>
            </div>
            <div>
              <span className="text-sm text-gray-600">Email:</span>
              <p className="font-semibold text-gray-900">{user?.email}</p>
            </div>
          </div>

          {/* Open Prodigy Button */}
          <button
            onClick={openProdigy}
            disabled={prodigyStatus === 'offline'}
            className={`w-full py-4 px-6 rounded-lg font-semibold text-lg transition-all transform shadow-lg ${
              prodigyStatus === 'offline'
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-gradient-to-r from-indigo-600 to-indigo-700 text-white hover:from-indigo-700 hover:to-indigo-800 hover:scale-105'
            }`}
          >
            {prodigyStatus === 'offline' ? '⚠️ Prodigy no disponible' : '▶️ Abrir Prodigy'}
          </button>

          {prodigyStatus === 'offline' && (
            <p className="text-sm text-red-600 mt-3 text-center">
              El servidor de Prodigy no está corriendo. Contacta al administrador.
            </p>
          )}
        </div>

        {/* Instructions Card */}
        <div className="bg-yellow-50 border-l-4 border-yellow-400 rounded-lg p-6 mb-6">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-6 w-6 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-yellow-800 mb-2">📌 Instrucciones</h3>
              <div className="text-sm text-yellow-700">
                {prodigyInfo?.instructions}
              </div>
            </div>
          </div>
        </div>

        {/* Info Grid */}
        <div className="grid md:grid-cols-2 gap-6">
          {/* What is Prodigy */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="font-semibold text-gray-900 mb-3">¿Qué es Prodigy?</h3>
            <p className="text-sm text-gray-600">
              Prodigy es una herramienta de anotación que permite etiquetar 
              palabras con categorías gramaticales (POS tags) de manera eficiente.
            </p>
          </div>

          {/* Task Info */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="font-semibold text-gray-900 mb-3">Tu tarea</h3>
            <p className="text-sm text-gray-600">
              Anotar traducciones en Guaraní con etiquetas POS siguiendo 
              las guías de anotación del proyecto.
            </p>
          </div>

          {/* Controls */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="font-semibold text-gray-900 mb-3">⌨️ Controles</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• <kbd className="px-2 py-1 bg-gray-100 rounded">Accept</kbd> - Guardar anotación</li>
              <li>• <kbd className="px-2 py-1 bg-gray-100 rounded">Reject</kbd> - Rechazar ejemplo</li>
              <li>• <kbd className="px-2 py-1 bg-gray-100 rounded">Ignore</kbd> - Saltar</li>
            </ul>
          </div>

          {/* Session Info */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="font-semibold text-gray-900 mb-3">🔗 Conexión Segura</h3>
            <p className="text-sm text-gray-600 mb-2">
              Tu sesión usa autenticación JWT. El token expira en 24 horas.
            </p>
            <button
              onClick={copyToken}
              className="text-xs text-indigo-600 hover:text-indigo-800 underline"
            >
              📋 Copiar token
            </button>
          </div>
        </div>

        {/* Footer Note */}
        <div className="mt-8 text-center text-sm text-gray-600">
          <p>
            Si tienes problemas, contacta al administrador o revisa la{' '}
            <a href="/docs" className="text-indigo-600 hover:underline">documentación</a>
          </p>
        </div>
      </div>
      </div>
    </div>
  );
};

export default ProdigyPage;
