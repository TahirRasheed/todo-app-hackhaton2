// T032: Task Card Component - Displays individual task

'use client';

import { useState } from 'react';
import { Task } from '@/types/task';
import { updateTask, deleteTask } from '@/lib/api';
import { EditTaskModal } from './EditTaskModal';
import { ConfirmDialog } from '../ui/ConfirmDialog';
import { ErrorAlert } from '../ui/ErrorAlert';

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
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
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

  const handleConfirmDelete = async () => {
    setIsDeleting(true);
    setError(null);

    try {
      const response = await deleteTask(userId, task.id);

      if (response.error) {
        setError(response.error.message || 'Failed to delete task');
        setIsDeleting(false);
      } else {
        onTaskDeleted();
      }
    } catch (err) {
      setError('Failed to delete task');
      setIsDeleting(false);
    }
  };

  return (
    <>
      <div className="bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition border border-gray-100">
        <div className="flex items-start gap-3 mb-3">
          <input
            type="checkbox"
            checked={task.completed}
            onChange={handleToggleCompletion}
            disabled={isTogglingCompletion}
            className="mt-1.5 w-5 h-5 text-blue-600 rounded cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
            aria-label={`Mark "${task.title}" as ${task.completed ? 'incomplete' : 'complete'}`}
          />
          <div className="flex-1 min-w-0">
            <h3
              className={`font-semibold break-words transition-all ${
                task.completed
                  ? 'line-through text-gray-400'
                  : 'text-gray-900'
              }`}
            >
              {task.title}
            </h3>
            {task.description && (
              <p className={`text-sm mt-1 break-words transition-all ${
                task.completed ? 'text-gray-300' : 'text-gray-600'
              }`}>
                {task.description}
              </p>
            )}
            <p className="text-gray-400 text-xs mt-2">
              {new Date(task.createdAt).toLocaleDateString(undefined, {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
              })}
            </p>
          </div>
        </div>

        {error && (
          <ErrorAlert
            message={error}
            onDismiss={() => setError(null)}
            isDismissible={true}
          />
        )}

        <div className="flex gap-2">
          <button
            onClick={() => setIsEditing(true)}
            disabled={task.completed || isEditing}
            className="flex-1 px-3 py-2 bg-blue-100 text-blue-700 rounded text-sm font-medium hover:bg-blue-200 active:bg-blue-300 disabled:opacity-50 disabled:cursor-not-allowed transition"
            aria-label={`Edit "${task.title}"`}
          >
            Edit
          </button>
          <button
            onClick={() => setShowDeleteConfirm(true)}
            disabled={isDeleting}
            className="flex-1 px-3 py-2 bg-red-100 text-red-700 rounded text-sm font-medium hover:bg-red-200 active:bg-red-300 disabled:opacity-50 disabled:cursor-not-allowed transition"
            aria-label={`Delete "${task.title}"`}
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

      <ConfirmDialog
        title="Delete Task"
        message={`Are you sure you want to delete "${task.title}"? This action cannot be undone.`}
        confirmText="Delete"
        cancelText="Cancel"
        isDangerous={true}
        isOpen={showDeleteConfirm}
        isLoading={isDeleting}
        onConfirm={handleConfirmDelete}
        onCancel={() => setShowDeleteConfirm(false)}
      />
    </>
  );
}
