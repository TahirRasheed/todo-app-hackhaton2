// Loading skeleton for task cards

export function TaskSkeleton() {
  return (
    <div className="bg-white rounded-lg shadow-md p-4 border border-gray-100 animate-pulse">
      <div className="flex items-start gap-3 mb-3">
        <div className="w-5 h-5 bg-gray-300 rounded mt-1" />
        <div className="flex-1">
          <div className="h-5 bg-gray-300 rounded w-3/4 mb-2" />
          <div className="h-4 bg-gray-200 rounded w-full mb-2" />
          <div className="h-3 bg-gray-200 rounded w-1/4" />
        </div>
      </div>
      <div className="flex gap-2">
        <div className="flex-1 h-8 bg-gray-200 rounded" />
        <div className="flex-1 h-8 bg-gray-200 rounded" />
      </div>
    </div>
  );
}

export function TaskListSkeleton() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {[...Array(6)].map((_, i) => (
        <TaskSkeleton key={i} />
      ))}
    </div>
  );
}
