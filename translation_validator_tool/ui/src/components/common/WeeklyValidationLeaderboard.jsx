import { useEffect, useState } from 'react';
import { validatorAPI } from '../../services/api';

const WeeklyValidationLeaderboard = () => {
  const [users, setUsers] = useState([]);
  const [weekStart, setWeekStart] = useState(null);
  const [weekEnd, setWeekEnd] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLeaderboard();
  }, []);

  const fetchLeaderboard = async () => {
    setLoading(true);

    try {
      const response = await validatorAPI.getWeeklyUserActivity();
      const data = response.data;

      setUsers(data.items || []);
      setWeekStart(data.week_start);
      setWeekEnd(data.week_end);
    } catch (error) {
      console.error('Error cargando leaderboard de validaciones:', error);
      setUsers([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <aside className="hidden 2xl:block w-72 bg-white rounded-lg shadow-md border border-gray-200 overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-200 bg-gray-50">
        <h3 className="text-sm 2xl:text-xs font-bold text-gray-900">
          Ranking semanal de validaciones
        </h3>
      </div>

      {loading ? (
        <div className="p-4 flex justify-center">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-teal-600"></div>
        </div>
      ) : users.length === 0 ? (
        <div className="p-4 text-sm text-gray-500">
          Sin validaciones esta semana.
        </div>
      ) : (
        <div className="divide-y divide-gray-100">
          {users.map((user, index) => (
            <div
              key={user.user_id || `${user.nombre_completo}-${index}`}
              className="flex items-center justify-between px-4 py-3 2xl:px-3 2xl:py-2 hover:bg-gray-50"
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
                {user.validaciones_semana}
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

export default WeeklyValidationLeaderboard;
