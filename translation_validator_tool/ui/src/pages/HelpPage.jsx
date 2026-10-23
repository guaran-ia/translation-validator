import Navbar from '../components/common/Navbar';
import WeeklyLeaderboard from '../components/common/WeeklyLeaderboard';
import TranslationHelpContent from '../components/common/TranslationHelpContent';

const HelpPage = () => (
  <div className="min-h-screen bg-gray-50">
    <Navbar />
    <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
      <header className="mb-8 rounded-2xl bg-gradient-to-r from-teal-600 to-teal-700 p-8 text-white shadow-lg">
        <h1 className="text-3xl font-bold">Guía de traducción</h1>
        <p className="mt-2 text-teal-100">Aprende a seleccionar tareas y aportar traducciones al guaraní.</p>
      </header>
      <div className="rounded-lg bg-white p-6 shadow-lg">
        <TranslationHelpContent />
      </div>
    </main>
    <div className="absolute right-1 top-28 hidden xl:block">
      <WeeklyLeaderboard source="api" />
    </div>
  </div>
);

export default HelpPage;
