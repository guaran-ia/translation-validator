import TranslationHelpContent from '../common/TranslationHelpContent';

const HelpModal = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="fixed inset-0 bg-black/60" onClick={onClose} />
      <div
        role="dialog"
        aria-modal="true"
        aria-label="Guía de uso"
        className="relative z-10 mx-4 max-h-[90vh] w-full max-w-3xl overflow-y-auto rounded-xl bg-white p-6 shadow-2xl"
      >
        <div className="mb-4 flex justify-end">
          <button
            type="button"
            aria-label="Cerrar"
            className="rounded-md bg-teal-100 px-4 py-2 text-sm font-medium text-teal-800 hover:bg-teal-200 focus:outline-none focus:ring-2 focus:ring-teal-500"
            onClick={onClose}
          >
            Cerrar
          </button>
        </div>
        <TranslationHelpContent />
      </div>
    </div>
  );
};

export default HelpModal;
