import { useEffect, useState } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

const WeeklyLeaderboard = ({ source = 'api' }) => {
  const [users, setUsers] = useState([]);
  const [weekStart, setWeekStart] = useState(null);
  const [weekEnd, setWeekEnd] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLeaderboard();
  }, [source]);

  const fetchLeaderboard = async () => {
    setLoading(true);

    try {
      let response;

      if (source === 'json') {
        response = await fetch('../data/leaderboard/weekly-leaderboard.json', {
          cache: 'no-store', 
        });
      } else {
        const token = localStorage.getItem('access_token');

        response = await fetch(`${API_BASE_URL}/api/annotations/weekly-user-activity`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
      }

      if (!response.ok) {
        setUsers([]);
        return;
      }

      const data = await response.json();

      setUsers(data.items || []);
      setWeekStart(data.week_start);
      setWeekEnd(data.week_end);
    } catch (error) {
      console.error('Error cargando leaderboard:', error);
      setUsers([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <aside className="w-80 bg-white rounded-lg shadow-md border border-gray-200 overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-200 bg-gray-50">
        <h3 className="text-sm font-bold text-gray-900">
          Ranking semanal de traducciones
        </h3>
      </div>

      {loading ? (
        <div className="p-4 flex justify-center">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-teal-600"></div>
        </div>
      ) : users.length === 0 ? (
        <div className="p-4 text-sm text-gray-500">
          Sin traducciones esta semana.
        </div>
      ) : (
        <div className="divide-y divide-gray-100">
          {users.map((user, index) => (
            <div
              key={user.user_id || `${user.nombre_completo}-${index}`}
              className="flex items-center justify-between px-4 py-3 hover:bg-gray-50"
            >
              <div className="flex items-center gap-3 min-w-0">
                <span className="w-6 text-sm font-bold text-teal-700">
                  {user.position || index + 1}
                </span>

                <div className="min-w-0">
                  <p className="text-sm font-semibold text-gray-900 truncate">
                    {user.nombre_completo || 'Usuario'}
                  </p>
                </div>
              </div>

              <span className="text-sm font-bold text-gray-900">
                {user.traducciones_semana}
              </span>
            </div>
          ))}
        </div>
      )}

      <div className="px-4 py-3 bg-gray-50 border-t border-gray-200">
        <p className="text-[11px] text-gray-500">
          Semana: {weekStart || '-'} al {weekEnd || '-'}
        </p>
      </div>
    </aside>
  );
};

export default WeeklyLeaderboard;