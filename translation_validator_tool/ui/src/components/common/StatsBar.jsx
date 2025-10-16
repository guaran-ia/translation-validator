const StatsBar = ({ stats }) => {
  if (!stats) return null;

  const progressPercentage = stats.total > 0 
    ? Math.round((stats.user_progress / stats.total) * 100) 
    : 0;

  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        {/* Stats */}
        <div className="flex flex-wrap gap-6 text-sm">
          <div className="flex items-center space-x-2">
            <span className="font-medium text-gray-700">Total:</span>
            <span className="text-blue-600 font-semibold">{stats.total}</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="font-medium text-gray-700">Validated:</span>
            <span className="text-green-600 font-semibold">{stats.validated}</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="font-medium text-gray-700">Pending:</span>
            <span className="text-orange-600 font-semibold">{stats.pending}</span>
          </div>
        </div>

        {/* User progress */}
        <div className="flex items-center space-x-3">
          <span className="text-sm font-medium text-gray-700">
            Your progress: {stats.user_progress}/{stats.total}
          </span>
          <div className="w-24 bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progressPercentage}%` }}
            ></div>
          </div>
          <span className="text-sm font-semibold text-blue-600">
            {progressPercentage}%
          </span>
        </div>
      </div>
    </div>
  );
};

export default StatsBar;