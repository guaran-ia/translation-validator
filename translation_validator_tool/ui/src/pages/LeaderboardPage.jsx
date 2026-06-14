import { useEffect, useMemo, useState } from 'react';
import Navbar from '../components/common/Navbar';

import { annotationsAPI } from '../services/api';

const LeaderboardPage = () => {
  const [items, setItems] = useState([]);
  const [weekStart, setWeekStart] = useState(null);
  const [weekEnd, setWeekEnd] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchLeaderboard();
  }, []);

 const fetchLeaderboard = async () => {
  setLoading(true);
  setError('');

  try {
    const response = await annotationsAPI.getWeeklyUserActivity();
    const data = response.data;

    setItems(data.items || []);
    setWeekStart(data.week_start);
    setWeekEnd(data.week_end);
  } catch (err) {
    console.error(err);
    setError('No se pudo cargar el ranking. Verifica tu sesión o intenta nuevamente.');
  } finally {
    setLoading(false);
  }
};

  const topUsers = useMemo(() => {
    return [...items]
      .sort((a, b) => b.traducciones_semana - a.traducciones_semana)
      .slice(0, 10);
  }, [items]);

  const getMedal = (index) => {
    if (index === 0) return '🥇';
    if (index === 1) return '🥈';
    if (index === 2) return '🥉';
    return `#${index + 1}`;
  };

  const getInitials = (name = '') => {
    return (
      name
        .split(' ')
        .filter(Boolean)
        .slice(0, 2)
        .map((word) => word[0])
        .join('')
        .toUpperCase() || '?'
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <div className="bg-gradient-to-r from-teal-600 to-teal-700 rounded-2xl shadow-lg p-8 text-white">
            <h1 className="text-3xl font-bold">Ranking semanal</h1>
            <p className="mt-2 text-teal-100">
              Ranking de las 10 personas con más traducciones realizadas en la semana.
            </p>

            <div className="mt-4 inline-flex items-center px-4 py-2 bg-white/10 border border-white/20 rounded-full text-sm">
              Semana actual: {weekStart || '-'} al {weekEnd || '-'}
            </div>
          </div>
        </div>

        {loading && (
          <div className="bg-white rounded-lg shadow-md p-10 flex items-center justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-600"></div>
          </div>
        )}

        {!loading && error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
            {error}
          </div>
        )}

        {!loading && !error && topUsers.length === 0 && (
          <div className="bg-white rounded-lg shadow-md p-10 text-center">
            <div className="text-5xl mb-4">📊</div>
            <h2 className="text-xl font-bold text-gray-900">Sin traducciones esta semana</h2>
            <p className="text-gray-600 mt-2">
              Aún no hay traducciones registradas en la semana actual.
            </p>
          </div>
        )}

        {!loading && !error && topUsers.length > 0 && (
          <div className="space-y-4">
            {topUsers.map((user, index) => (
              <div
                key={user.user_id}
                className={`bg-white rounded-xl shadow-md p-5 border transition hover:shadow-lg ${
                  index < 3 ? 'border-teal-200' : 'border-gray-100'
                }`}
              >
                <div className="flex flex-col md:flex-row md:items-center gap-4">
                  <div className="w-16 h-16 rounded-2xl bg-teal-50 flex items-center justify-center text-2xl font-bold text-teal-700">
                    {getMedal(index)}
                  </div>

                  <div className="flex items-center gap-4 flex-1">
                    <div className="w-12 h-12 rounded-full bg-teal-600 text-white flex items-center justify-center font-bold">
                      {getInitials(user.nombre_completo)}
                    </div>

                    <div>
                      <h3 className="font-bold text-gray-900">
                        {user.nombre_completo || 'Usuario sin nombre'}
                      </h3>
                    </div>
                  </div>

                  <div className="bg-teal-50 rounded-lg px-6 py-4 text-center border border-teal-100 min-w-[150px]">
                    <p className="text-xs text-teal-700">Traducciones</p>
                    <p className="text-2xl font-bold text-teal-800">
                      {user.traducciones_semana}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="mt-8 p-4 bg-teal-50 border border-teal-200 rounded-lg">
          <h3 className="font-semibold text-teal-900 mb-2">¿Cómo se calcula?</h3>
          <p className="text-sm text-teal-800">
            Se cuentan únicamente las traducciones realizadas durante la semana actual,
            de lunes a domingo. El ranking se reinicia automáticamente cada lunes.
          </p>
        </div>
      </div>
    </div>
  );
};

export default LeaderboardPage;