'use client'

/**
 * TaskList Component - Display list of tasks with pagination
 */
import { Task } from '@/types/api'
import TaskItem from './TaskItem'

interface TaskListProps {
  tasks: Task[]
  isLoading?: boolean
  onTaskDelete?: (taskId: string) => Promise<void>
  onTaskEdit?: (task: Task) => void
  onTaskToggleComplete?: (taskId: string, completed: boolean) => Promise<void>
  total?: number
  skip?: number
  limit?: number
  onPageChange?: (skip: number) => void
}

export default function TaskList({
  tasks,
  isLoading = false,
  onTaskDelete,
  onTaskEdit,
  onTaskToggleComplete,
  total = 0,
  skip = 0,
  limit = 20,
  onPageChange,
}: TaskListProps) {
  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow p-6 text-center">
        <p className="text-gray-600">Loading tasks...</p>
      </div>
    )
  }

  if (tasks.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6 text-center">
        <p className="text-gray-600">No tasks yet. Create one to get started!</p>
      </div>
    )
  }

  const hasNextPage = skip + limit < total
  const hasPrevPage = skip > 0

  return (
    <div>
      <div className="space-y-3 mb-6">
        {tasks.map((task) => (
          <TaskItem
            key={task.id}
            task={task}
            onDelete={onTaskDelete}
            onEdit={onTaskEdit}
            onToggleComplete={onTaskToggleComplete}
          />
        ))}
      </div>

      {total > limit && (
        <div className="flex justify-between items-center bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-600">
            Showing {skip + 1}-{Math.min(skip + limit, total)} of {total} tasks
          </p>
          <div className="flex gap-2">
            <button
              onClick={() => onPageChange?.(Math.max(0, skip - limit))}
              disabled={!hasPrevPage}
              className="px-3 py-1 bg-gray-200 text-gray-800 rounded hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
            >
              Previous
            </button>
            <button
              onClick={() => onPageChange?.(skip + limit)}
              disabled={!hasNextPage}
              className="px-3 py-1 bg-gray-200 text-gray-800 rounded hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
