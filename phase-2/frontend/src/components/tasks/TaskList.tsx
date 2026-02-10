// T031: Task List Component - Displays paginated task list

'use client';

import { useEffect, useState } from 'react';
import { Task, TaskListResponse } from '@/types/task';
import { getTasks } from '@/lib/api';
import { TaskCard } from './TaskCard';
import { CreateTaskModal } from './CreateTaskModal';

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
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
          <p className="text-red-700 text-sm">{error}</p>
        </div>
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
          <p className="text-gray-500 text-lg">No tasks yet. Create one to get started!</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
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
      <div className="mt-8 flex justify-between items-center">
        <button
          onClick={() => setSkip(Math.max(0, skip - TASKS_PER_PAGE))}
          disabled={skip === 0}
          className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md font-medium hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed transition"
        >
          Previous
        </button>

        <span className="text-gray-600 text-sm">
          Showing {skip + 1} to {Math.min(skip + TASKS_PER_PAGE, total)} of {total}
        </span>

        <button
          onClick={() => setSkip(skip + TASKS_PER_PAGE)}
          disabled={skip + TASKS_PER_PAGE >= total}
          className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md font-medium hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed transition"
        >
          Next
        </button>
      </div>
    </div>
  );
}
