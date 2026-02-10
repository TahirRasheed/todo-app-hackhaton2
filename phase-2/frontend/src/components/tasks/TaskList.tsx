// T031: Task List Component - Displays paginated task list

'use client';

import { useEffect, useState } from 'react';
import { Task } from '@/types/task';
import { getTasks } from '@/lib/api';
import { TaskCard } from './TaskCard';
import { CreateTaskModal } from './CreateTaskModal';
import { ErrorAlert } from '../ui/ErrorAlert';

interface TaskListProps {
  userId: string;
}

const TASKS_PER_PAGE = 10;

export function TaskList({ userId }: TaskListProps) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [skip, setSkip] = useState(0);
  const [total, setTotal] = useState(0);
  const [isCreatingTask, setIsCreatingTask] = useState(false);

  useEffect(() => {
    const fetchTasks = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const response = await getTasks(userId, skip, TASKS_PER_PAGE);
        if (response.data) {
          setTasks(response.data.items);
          setTotal(response.data.total);
        } else if (response.error) {
          setError(response.error.message || 'Failed to fetch tasks');
        }
      } catch (err) {
        setError('An unexpected error occurred while fetching tasks');
      } finally {
        setIsLoading(false);
      }
    };

    fetchTasks();
  }, [userId, skip]);

  const handleTaskCreated = async () => {
    // Reset pagination and refresh task list
    setSkip(0);
    setIsCreatingTask(false);
    
    // Refetch tasks
    try {
      const response = await getTasks(userId, 0, TASKS_PER_PAGE);
      if (response.data) {
        setTasks(response.data.items);
        setTotal(response.data.total);
      }
    } catch (err) {
      setError('Failed to refresh tasks after creation');
    }
  };

  const handleTaskDeleted = () => {
    // Refresh task list
    setSkip(0);
    window.location.reload();
  };

  const handleTaskUpdated = async () => {
    // Refresh task list
    try {
      const response = await getTasks(userId, skip, TASKS_PER_PAGE);
      if (response.data) {
        setTasks(response.data.items);
        setTotal(response.data.total);
      }
    } catch (err) {
      setError('Failed to refresh tasks after update');
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-pulse text-gray-600">Loading tasks...</div>
      </div>
    );
  }

  return (
    <div>
      {error && (
        <ErrorAlert
          message={error}
          onDismiss={() => setError(null)}
          onRetry={() => {
            setSkip(0);
            setError(null);
          }}
          isDismissible={true}
          autoClose={8000}
        />
      )}

      <div className="mb-6 flex justify-between items-center">
        <h2 className="text-xl font-semibold text-gray-900">
          Tasks ({total})
        </h2>
        <button
          onClick={() => setIsCreatingTask(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-md font-medium hover:bg-blue-700 transition"
        >
          + Create Task
        </button>
      </div>

      {isCreatingTask && (
        <CreateTaskModal
          userId={userId}
          onClose={() => setIsCreatingTask(false)}
          onTaskCreated={handleTaskCreated}
        />
      )}

      {tasks.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-gray-400 mb-3">
            <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <p className="text-gray-500 text-lg font-medium">No tasks yet</p>
          <p className="text-gray-400 text-sm">Create one to get started!</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {tasks.map((task) => (
            <TaskCard
              key={task.id}
              task={task}
              userId={userId}
              onTaskDeleted={handleTaskDeleted}
              onTaskUpdated={handleTaskUpdated}
            />
          ))}
        </div>
      )}

      {/* Pagination */}
      {total > TASKS_PER_PAGE && (
        <div className="mt-8 flex flex-col sm:flex-row justify-between items-center gap-4 bg-gray-50 p-4 rounded-lg">
          <button
            onClick={() => setSkip(Math.max(0, skip - TASKS_PER_PAGE))}
            disabled={skip === 0}
            className="w-full sm:w-auto px-4 py-2 bg-gray-200 text-gray-700 rounded-md font-medium hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed active:bg-gray-400 transition"
          >
            ← Previous
          </button>

          <span className="text-gray-600 text-sm text-center">
            Page {Math.floor(skip / TASKS_PER_PAGE) + 1} of {Math.ceil(total / TASKS_PER_PAGE)}
            <span className="block text-xs text-gray-500 mt-1">
              {skip + 1}–{Math.min(skip + TASKS_PER_PAGE, total)} of {total} tasks
            </span>
          </span>

          <button
            onClick={() => setSkip(skip + TASKS_PER_PAGE)}
            disabled={skip + TASKS_PER_PAGE >= total}
            className="w-full sm:w-auto px-4 py-2 bg-gray-200 text-gray-700 rounded-md font-medium hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed active:bg-gray-400 transition"
          >
            Next →
          </button>
        </div>
      )}
    </div>
  );
}
