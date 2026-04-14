import instructivoVideo from '../../videos/Instructivo.mp4';

const HelpModal = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div
        className="fixed inset-0 bg-black/60"
        onClick={onClose}
      />
      <div className="bg-white rounded-xl overflow-hidden max-w-6xl w-full z-10 p-4 mx-4 shadow-2xl">
        <div className="flex justify-end mb-3">
          <button
            type="button"
            aria-label="Cerrar"
            className="inline-flex items-center gap-2 px-3 py-2 rounded-md bg-teal-100 hover:bg-teal-200 text-teal-800 shadow-sm transition-colors text-sm font-medium focus:outline-none focus:ring-2 focus:ring-teal-500"
            onClick={onClose}
          >
            <span>Cerrar</span>
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
              <path fillRule="evenodd" d="M10 8.586l4.95-4.95a1 1 0 111.414 1.414L11.414 10l4.95 4.95a1 1 0 01-1.414 1.414L10 11.414l-4.95 4.95a1 1 0 01-1.414-1.414L8.586 10 3.636 5.05A1 1 0 015.05 3.636L10 8.586z" clipRule="evenodd" />
            </svg>
          </button>
        </div>

        <div className="mt-2" style={{ position: 'relative', paddingTop: '56.25%' }}>
          <video
            src={instructivoVideo}
            title="Video instructivo"
            controls
            className="absolute top-0 left-0 w-full h-full rounded-md object-cover"
          />
        </div>
      </div>
    </div>
  );
};

export default HelpModal;
