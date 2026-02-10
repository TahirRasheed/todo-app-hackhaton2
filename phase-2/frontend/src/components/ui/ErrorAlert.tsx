// T054: Error Alert Component for displaying errors

'use client';

import { useState } from 'react';

interface ErrorAlertProps {
  message: string;
  onDismiss?: () => void;
  onRetry?: () => void;
  isDismissible?: boolean;
  autoClose?: number;
}

export function ErrorAlert({
  message,
  onDismiss,
  onRetry,
  isDismissible = true,
  autoClose,
}: ErrorAlertProps) {
  const [isVisible, setIsVisible] = useState(true);

  const handleDismiss = () => {
    setIsVisible(false);
    onDismiss?.();
  };

  const handleRetry = () => {
    onRetry?.();
  };

  if (!isVisible) return null;

  // Auto-close timer
  if (autoClose) {
    setTimeout(() => {
      setIsVisible(false);
    }, autoClose);
  }

  return (
    <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md animate-in fade-in">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-red-700 font-medium">{message}</p>
        </div>
        <div className="flex gap-2 ml-4">
          {onRetry && (
            <button
              onClick={handleRetry}
              className="text-red-700 hover:text-red-900 font-medium text-sm underline"
            >
              Retry
            </button>
          )}
          {isDismissible && (
            <button
              onClick={handleDismiss}
              className="text-red-700 hover:text-red-900 text-sm"
              aria-label="Dismiss error"
            >
              ✕
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
