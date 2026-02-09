'use client'

/**
 * Dashboard Page - Main authenticated page with task management
 */
import { useEffect, useState } from 'react'
import { User, Task } from '@/types/api'
import { apiClient } from '@/lib/api-client'
import TaskForm from '@/components/TaskForm'
import TaskList from '@/components/TaskList'

interface PaginationMeta {
  total?: number
  skip?: number
  limit?: number
}

export default function DashboardPage() {
  const [user, setUser] = useState<User | null>(null)
  const [tasks, setTasks] = useState<Task[]>([])
  const [paginationMeta, setPaginationMeta] = useState<PaginationMeta>({})
  const [loading, setLoading] = useState(true)
  const [tasksLoading, setTasksLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [currentPage, setCurrentPage] = useState(0)

  // Load user on mount
  useEffect(() => {
    const loadUser = async () => {
      try {
        const response = await apiClient<{ data: User }>('/auth/me', {
          method: 'GET',
        })
        setUser(response.data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load user')
      } finally {
        setLoading(false)
      }
    }

    loadUser()
  }, [])

  // Load tasks when user is available
  useEffect(() => {
    if (!user) return

    const loadTasks = async () => {
      setTasksLoading(true)
      try {
        const response = await apiClient<{ data: Task[] }>(
          `/api/v1/users/${user.id}/tasks?skip=${currentPage}&limit=20`,
          { method: 'GET' }
        )
        setTasks(response.data || [])
        // Extract pagination meta from response meta
        setPaginationMeta({
          total: (response as any).meta?.total || 0,
          skip: (response as any).meta?.skip || currentPage,
          limit: (response as any).meta?.limit || 20,
        })
      } catch (err) {
        console.error('Failed to load tasks:', err)
      } finally {
        setTasksLoading(false)
      }
    }

    loadTasks()
  }, [user, currentPage])

  const handleCreateTask = async (title: string, description: string) => {
    if (!user) return

    try {
      const response = await apiClient<{ data: Task }>(
        `/api/v1/users/${user.id}/tasks`,
        {
          method: 'POST',
          body: JSON.stringify({ title, description: description || undefined }),
        }
      )
      // Add task to list and reset form
      setTasks([response.data, ...tasks])
      setShowCreateForm(false)
      // Update total count
      setPaginationMeta((prev) => ({
        ...prev,
        total: (prev.total || 0) + 1,
      }))
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to create task'
      throw new Error(message)
    }
  }

  const handleToggleComplete = async (taskId: string, completed: boolean) => {
    if (!user) return

    try {
      const response = await apiClient<{ data: Task }>(
        `/api/v1/users/${user.id}/tasks/${taskId}`,
        {
          method: 'PUT',
          body: JSON.stringify({ completed }),
        }
      )
      // Update task in list
      setTasks(tasks.map((t) => (t.id === taskId ? response.data : t)))
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to update task'
      throw new Error(message)
    }
  }

  const handleDeleteTask = async (taskId: string) => {
    if (!user) return

    try {
      await apiClient(`/api/v1/users/${user.id}/tasks/${taskId}`, {
        method: 'DELETE',
      })
      // Remove task from list
      setTasks(tasks.filter((t) => t.id !== taskId))
      // Update total count
      setPaginationMeta((prev) => ({
        ...prev,
        total: Math.max(0, (prev.total || 0) - 1),
      }))
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to delete task'
      throw new Error(message)
    }
  }

  if (loading) {
    return <div className="text-center text-gray-600">Loading authenticated content...</div>
  }

  if (error) {
    return (
      <div className="p-4 bg-red-100 border border-red-400 text-red-700 rounded">
        {error}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Welcome section */}
      <section className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Welcome!</h2>
        {user && (
          <p className="text-lg text-gray-700">
            Authenticated as <strong>{user.email}</strong>
          </p>
        )}
      </section>

      {/* Create task section */}
      {showCreateForm ? (
        <>
          <TaskForm
            mode="create"
            onSubmit={handleCreateTask}
            onCancel={() => setShowCreateForm(false)}
          />
        </>
      ) : (
        <div className="flex">
          <button
            onClick={() => setShowCreateForm(true)}
            className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition font-medium"
          >
            + Add Task
          </button>
        </div>
      )}

      {/* Tasks section */}
      <section>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Your Tasks</h3>
        <TaskList
          tasks={tasks}
          isLoading={tasksLoading}
          total={paginationMeta.total || 0}
          skip={paginationMeta.skip || 0}
          limit={paginationMeta.limit || 20}
          onPageChange={(skip) => setCurrentPage(skip)}
          onTaskDelete={handleDeleteTask}
          onTaskEdit={(task) => console.log('Edit task:', task)}
          onTaskToggleComplete={handleToggleComplete}
        />
      </section>

      {/* Stats section */}
      <section className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Stats</h3>
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center">
            <p className="text-3xl font-bold text-blue-600">{paginationMeta.total || 0}</p>
            <p className="text-sm text-gray-600">Total Tasks</p>
          </div>
          <div className="text-center">
            <p className="text-3xl font-bold text-green-600">0</p>
            <p className="text-sm text-gray-600">Completed</p>
          </div>
          <div className="text-center">
            <p className="text-3xl font-bold text-orange-600">
              {Math.max(0, (paginationMeta.total || 0))}
            </p>
            <p className="text-sm text-gray-600">Pending</p>
          </div>
        </div>
      </section>

      {/* Phase 4 status */}
      <section className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-2">Phase 4 Complete ✓</h3>
        <p className="text-blue-800">
          Task creation and listing is now live! You can create tasks with titles and descriptions,
          and view them in a paginated list.
        </p>
      </section>
    </div>
  )
}
