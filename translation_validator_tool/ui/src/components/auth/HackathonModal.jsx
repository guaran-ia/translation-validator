import { useState } from 'react';
import imagen from '../../images/hack.jpeg';

const HackathonModal = ({ isOpen, onClose }) => {
  const [showConfirmClose, setShowConfirmClose] = useState(false);

  if (!isOpen) return null;

  const handleConfirmClose = () => {
    try {
      localStorage.setItem('hackathon_seen', 'true');
    } catch (e) {
      console.error('Error guardando en localStorage:', e);
    }
    setShowConfirmClose(false);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center" style={{ pointerEvents: 'auto' }}>
      <div
        className="fixed inset-0 bg-black/60"
        onClick={() => {}}
        style={{ zIndex: 40 }}
      />
      <div className="bg-white rounded-xl overflow-hidden max-w-4xl w-full z-50 p-6 mx-4 shadow-2xl relative" style={{ zIndex: 50, maxHeight: '90vh', overflowY: 'auto' }}>
        <div className="flex justify-end mb-3">
          <button
            type="button"
            aria-label="Cerrar"
            className="inline-flex items-center gap-2 px-3 py-2 rounded-md bg-teal-100 hover:bg-teal-200 text-teal-800 shadow-sm transition-colors text-sm font-medium focus:outline-none focus:ring-2 focus:ring-teal-500"
            onClick={() => setShowConfirmClose(true)}
          >
            <span>Cerrar</span>
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
              <path fillRule="evenodd" d="M10 8.586l4.95-4.95a1 1 0 111.414 1.414L11.414 10l4.95 4.95a1 1 0 01-1.414 1.414L10 11.414l-4.95 4.95a1 1 0 01-1.414-1.414L8.586 10 3.636 5.05A1 1 0 015.05 3.636L10 8.586z" clipRule="evenodd" />
            </svg>
          </button>
        </div>

        <div className="w-full flex items-center justify-center bg-gray-100 rounded-lg overflow-hidden" style={{ minHeight: '400px' }}>
          <img 
            src={imagen} 
            alt="Hackathon Guaraní 2026 - Ñe'ëtech" 
            className="w-full h-full object-contain"
            onError={(e) => {
              console.error('Error cargando imagen del modal:', e);
              e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300"%3E%3Crect fill="%23f3f4f6" width="400" height="300"/%3E%3Ctext x="50%25" y="50%25" font-size="16" text-anchor="middle" dy=".3em" fill="%239ca3af"%3EImagen no disponible%3C/text%3E%3C/svg%3E';
            }}
            onLoad={() => console.log('Imagen del modal cargada correctamente')}
          />
        </div>

        <div className="flex justify-center mt-6">
          <button
            type="button"
            aria-label="Inscribirse en la hackathon"
            className="inline-flex items-center justify-center gap-2 px-6 py-3 rounded-lg bg-green-600 hover:bg-green-700 text-white shadow-md transition-colors font-semibold focus:outline-none focus:ring-2 focus:ring-green-500"
            onClick={() => window.open('https://inscripciones.ciditpy.org/', '_blank')}
          >
            <span>¡Quiero formar parte!</span>
          </button>
        </div>
      </div>

      {/* Modal de confirmación para cerrar */}
      {showConfirmClose && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white rounded-lg shadow-lg p-6 max-w-md mx-4">
            <h3 className="text-lg font-bold text-gray-900 mb-4">¿Estás seguro?</h3>
            <p className="text-gray-600 mb-2">
              Al cerrar este anuncio, no podrás verlo nuevamente.
            </p>
            
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setShowConfirmClose(false)}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={handleConfirmClose}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 font-medium transition-colors"
              >
                Sí, cerrar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default HackathonModal;
