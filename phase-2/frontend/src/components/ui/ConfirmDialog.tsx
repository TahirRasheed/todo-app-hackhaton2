// T050: Confirm Dialog Component for destructive actions

'use client';

import { useState } from 'react';

interface ConfirmDialogProps {
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  isDangerous?: boolean;
  isOpen: boolean;
  isLoading?: boolean;
  onConfirm: () => void | Promise<void>;
  onCancel: () => void;
}

export function ConfirmDialog({
  title,
  message,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  isDangerous = false,
  isOpen,
  isLoading = false,
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  const [error, setError] = useState<string | null>(null);

  const handleConfirm = async () => {
    try {
      setError(null);
      await onConfirm();
    } catch (err) {
      const message = err instanceof Error ? err.message : 'An error occurred';
      setError(message);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-lg max-w-sm w-full p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-2">{title}</h2>
        <p className="text-gray-600 mb-4">{message}</p>

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        )}

        <div className="flex gap-3 justify-end pt-4">
          <button
            onClick={onCancel}
            disabled={isLoading}
            className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md font-medium hover:bg-gray-300 disabled:opacity-50 transition"
          >
            {cancelText}
          </button>
          <button
            onClick={handleConfirm}
            disabled={isLoading}
            className={`px-4 py-2 rounded-md font-medium transition disabled:opacity-50 ${
              isDangerous
                ? 'bg-red-600 text-white hover:bg-red-700'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            {isLoading ? 'Processing...' : confirmText}
          </button>
        </div>
      </div>
    </div>
  );
}
