'use client'

/**
 * TaskItem Component - Display single task with actions
 */
import { useState } from 'react'
import { Task } from '@/types/api'

interface TaskItemProps {
  task: Task
  onDelete?: (taskId: string) => Promise<void>
  onEdit?: (task: Task) => void
  onToggleComplete?: (taskId: string, completed: boolean) => Promise<void>
}

export default function TaskItem({
  task,
  onDelete,
  onEdit,
  onToggleComplete
}: TaskItemProps) {
  const [isDeleting, setIsDeleting] = useState(false)
  const [isToggling, setIsToggling] = useState(false)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [currentTask, setCurrentTask] = useState(task)

  const handleDelete = async () => {
    if (!onDelete) return

    setIsDeleting(true)
    try {
      await onDelete(currentTask.id)
      setShowDeleteConfirm(false)
    } catch (error) {
      console.error('Failed to delete task:', error)
      setShowDeleteConfirm(false)
    } finally {
      setIsDeleting(false)
    }
  }

  const handleToggleComplete = async () => {
    if (!onToggleComplete) return

    setIsToggling(true)
    try {
      await onToggleComplete(currentTask.id, !currentTask.completed)
      setCurrentTask({ ...currentTask, completed: !currentTask.completed })
    } catch (error) {
      console.error('Failed to toggle task completion:', error)
    } finally {
      setIsToggling(false)
    }
  }

  const createdAt = new Date(task.created_at).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })

  const truncatedDescription =
    task.description && task.description.length > 100
      ? task.description.substring(0, 100) + '...'
      : task.description || 'No description'

  return (
    <div className="bg-white rounded-lg shadow p-4 hover:shadow-md transition">
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-3 flex-1">
          {/* Completion checkbox */}
          {onToggleComplete && (
            <input
              type="checkbox"
              checked={currentTask.completed}
              onChange={handleToggleComplete}
              disabled={isToggling}
              className="mt-1 w-5 h-5 text-green-600 rounded focus:ring-2 focus:ring-green-500 cursor-pointer disabled:opacity-50"
            />
          )}
          <div className="flex-1">
            <h4
              className={`text-lg font-semibold ${
                currentTask.completed
                  ? 'text-gray-400 line-through'
                  : 'text-gray-900'
              }`}
            >
              {currentTask.title}
            </h4>
            <p
              className={`text-sm mt-1 ${
                currentTask.completed ? 'text-gray-400 line-through' : 'text-gray-600'
              }`}
            >
              {truncatedDescription}
            </p>
            <p className="text-xs text-gray-500 mt-2">Created: {createdAt}</p>
          </div>
        </div>
        <div className="flex gap-2 ml-4">
          {onEdit && (
            <button
              onClick={() => onEdit(currentTask)}
              className="px-3 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 text-sm font-medium disabled:opacity-50"
              disabled={isToggling || isDeleting}
            >
              Edit
            </button>
          )}
          {onDelete && (
            <>
              {!showDeleteConfirm && (
                <button
                  onClick={() => setShowDeleteConfirm(true)}
                  className="px-3 py-1 bg-red-100 text-red-700 rounded hover:bg-red-200 text-sm font-medium disabled:opacity-50"
                  disabled={isToggling || isDeleting}
                >
                  Delete
                </button>
              )}
            </>
          )}
        </div>
      </div>

      {showDeleteConfirm && (
        <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded">
          <p className="text-sm text-red-800 mb-3">
            Are you sure you want to delete this task? This action cannot be undone.
          </p>
          <div className="flex gap-2">
            <button
              onClick={handleDelete}
              disabled={isDeleting}
              className="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50 text-sm font-medium"
            >
              {isDeleting ? 'Deleting...' : 'Confirm Delete'}
            </button>
            <button
              onClick={() => setShowDeleteConfirm(false)}
              disabled={isDeleting}
              className="px-3 py-1 bg-gray-300 text-gray-800 rounded hover:bg-gray-400 disabled:opacity-50 text-sm font-medium"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
