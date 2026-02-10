// T032: Task Card Component - Displays individual task

'use client';

import { useState } from 'react';
import { Task } from '@/types/task';
import { updateTask, deleteTask } from '@/lib/api';
import { EditTaskModal } from './EditTaskModal';

interface TaskCardProps {
  task: Task;
  userId: string;
  onTaskDeleted: () => void;
  onTaskUpdated: () => void;
}

export function TaskCard({
  task,
  userId,
  onTaskDeleted,
  onTaskUpdated,
}: TaskCardProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isTogglingCompletion, setIsTogglingCompletion] = useState(false);

  const handleToggleCompletion = async () => {
    setIsTogglingCompletion(true);
    setError(null);

    try {
      const response = await updateTask(userId, task.id, {
        completed: !task.completed,
      });

      if (response.error) {
        setError(response.error.message || 'Failed to update task');
      } else {
        onTaskUpdated();
      }
    } catch (err) {
      setError('Failed to update task');
    } finally {
      setIsTogglingCompletion(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this task?')) {
      return;
    }

    setIsDeleting(true);
    setError(null);

    try {
      const response = await deleteTask(userId, task.id);

      if (response.error) {
        setError(response.error.message || 'Failed to delete task');
      } else {
        onTaskDeleted();
      }
    } catch (err) {
      setError('Failed to delete task');
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <>
      <div className="bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition">
        <div className="flex items-start gap-3 mb-3">
          <input
            type="checkbox"
            checked={task.completed}
            onChange={handleToggleCompletion}
            disabled={isTogglingCompletion}
            className="mt-1 w-5 h-5 text-blue-600 rounded cursor-pointer disabled:opacity-50"
          />
          <div className="flex-1 min-w-0">
            <h3
              className={`font-semibold text-gray-900 break-words ${
                task.completed ? 'line-through text-gray-400' : ''
              }`}
            >
              {task.title}
            </h3>
            {task.description && (
              <p className="text-gray-600 text-sm mt-1 break-words">
                {task.description}
              </p>
            )}
            <p className="text-gray-400 text-xs mt-2">
              {new Date(task.createdAt).toLocaleDateString()}
            </p>
          </div>
        </div>

        {error && (
          <div className="mb-3 p-2 bg-red-50 border border-red-200 rounded-md">
            <p className="text-red-700 text-xs">{error}</p>
          </div>
        )}

        <div className="flex gap-2">
          <button
            onClick={() => setIsEditing(true)}
            disabled={task.completed || isEditing}
            className="flex-1 px-3 py-1 bg-blue-100 text-blue-700 rounded text-sm font-medium hover:bg-blue-200 disabled:opacity-50 transition"
          >
            Edit
          </button>
          <button
            onClick={handleDelete}
            disabled={isDeleting}
            className="flex-1 px-3 py-1 bg-red-100 text-red-700 rounded text-sm font-medium hover:bg-red-200 disabled:opacity-50 transition"
          >
            Delete
          </button>
        </div>
      </div>

      {isEditing && (
        <EditTaskModal
          task={task}
          userId={userId}
          onClose={() => setIsEditing(false)}
          onTaskUpdated={onTaskUpdated}
        />
      )}
    </>
  );
}
