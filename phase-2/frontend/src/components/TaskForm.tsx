'use client'

/**
 * TaskForm Component - Create and edit tasks
 */
import { useState } from 'react'

interface TaskFormProps {
  mode?: 'create' | 'edit'
  initialTitle?: string
  initialDescription?: string
  onSubmit: (title: string, description: string) => Promise<void>
  onCancel?: () => void
  isLoading?: boolean
}

export default function TaskForm({
  mode = 'create',
  initialTitle = '',
  initialDescription = '',
  onSubmit,
  onCancel,
  isLoading = false,
}: TaskFormProps) {
  const [title, setTitle] = useState(initialTitle)
  const [description, setDescription] = useState(initialDescription)
  const [error, setError] = useState<string | null>(null)

  const isEdit = mode === 'edit'
  const isTitleValid = title.trim().length > 0 && title.length <= 500
  const isDescriptionValid = !description || description.length <= 5000

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setError(null)

    if (!title.trim()) {
      setError('Title is required')
      return
    }

    if (title.length > 500) {
      setError('Title must not exceed 500 characters')
      return
    }

    if (description.length > 5000) {
      setError('Description must not exceed 5000 characters')
      return
    }

    try {
      await onSubmit(title.trim(), description.trim())
      if (!isEdit) {
        setTitle('')
        setDescription('')
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to save task'
      setError(message)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow p-6 mb-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        {isEdit ? 'Edit Task' : 'Create New Task'}
      </h3>

      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      <div className="mb-4">
        <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
          Task Title *
        </label>
        <input
          id="title"
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="What needs to be done?"
          maxLength={500}
          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <p className="text-xs text-gray-500 mt-1">
          {title.length} / 500 characters
        </p>
      </div>

      <div className="mb-4">
        <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
          Description
        </label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Add details..."
          maxLength={5000}
          rows={4}
          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
        />
        <p className="text-xs text-gray-500 mt-1">
          {description.length} / 5000 characters
        </p>
      </div>

      <div className="flex gap-2">
        <button
          type="submit"
          disabled={isLoading || !isTitleValid || !isDescriptionValid}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition font-medium"
        >
          {isLoading ? 'Saving...' : (isEdit ? 'Update Task' : 'Create Task')}
        </button>
        {isEdit && onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 bg-gray-300 text-gray-800 rounded-md hover:bg-gray-400 transition font-medium"
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  )
}
