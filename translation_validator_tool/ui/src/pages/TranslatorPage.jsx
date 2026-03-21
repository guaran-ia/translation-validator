import Navbar from '../components/common/Navbar';

const TranslatorPage = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-2xl font-bold text-gray-900">Traducir oraciones</h1>
      </div>
    </div>
  );
};

export default TranslatorPage;
