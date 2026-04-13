import instructivoVideo from '../../videos/Instructivo.mp4';
const HelpModal = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div
        className="fixed inset-0 bg-black opacity-50"
        onClick={onClose}
      />
      <div className="bg-white rounded-lg overflow-hidden max-w-[1300px] w-full z-10 p-4 mx-4">
        <div className="flex justify-end mb-4">
          <button
            type="button"
            aria-label="Cerrar"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-md bg-indigo-100 hover:bg-indigo-200 text-indigo-800 shadow-md transition-colors text-sm font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500"
            onClick={onClose}
          >
            <span>Cerrar</span>
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
              <path fillRule="evenodd" d="M10 8.586l4.95-4.95a1 1 0 111.414 1.414L11.414 10l4.95 4.95a1 1 0 01-1.414 1.414L10 11.414l-4.95 4.95a1 1 0 01-1.414-1.414L8.586 10 3.636 5.05A1 1 0 015.05 3.636L10 8.586z" clipRule="evenodd" />
            </svg>
          </button>
        </div>

        <div className="mt-6" style={{ position: 'relative', paddingTop: '56.25%' }}>
          <iframe
            src={instructivoVideo}
            title="Video instructivo"
            style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%' }}
            frameBorder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          />
        </div>
      </div>
    </div>
  );
};

export default HelpModal;
