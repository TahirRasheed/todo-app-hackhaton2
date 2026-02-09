'use client';

/**
 * SignoutButton Component
 *
 * Button component that handles user signout with loading state and error handling.
 * Calls signoutUser() API, clears token from localStorage, and redirects to signin.
 */

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { signoutUser } from '@/lib/api';

interface SignoutButtonProps {
  className?: string;
  variant?: 'primary' | 'secondary' | 'danger';
}

export default function SignoutButton({
  className = '',
  variant = 'danger',
}: SignoutButtonProps) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSignout = async () => {
    setLoading(true);
    setError(null);

    try {
      // Call signout API endpoint (validates token and clears localStorage)
      await signoutUser();

      // Redirect to signin page
      router.push('/auth/signin');
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to sign out';
      setError(errorMessage);

      // Still redirect to signin even on error (best effort cleanup)
      // User can't stay authenticated if signout was attempted
      setTimeout(() => {
        // Clear any remaining data
        if (typeof window !== 'undefined') {
          localStorage.removeItem('token');
          localStorage.removeItem('user');
        }
        router.push('/auth/signin');
      }, 2000); // Show error for 2 seconds before redirect
    } finally {
      setLoading(false);
    }
  };

  // Variant styling
  const variantClasses = {
    primary: 'bg-blue-600 hover:bg-blue-700 text-white',
    secondary: 'bg-gray-600 hover:bg-gray-700 text-white',
    danger: 'bg-red-600 hover:bg-red-700 text-white',
  };

  return (
    <div className="relative">
      <button
        onClick={handleSignout}
        disabled={loading}
        className={`
          px-4 py-2 rounded-md font-medium transition
          disabled:opacity-50 disabled:cursor-not-allowed
          ${variantClasses[variant]}
          ${className}
        `}
      >
        {loading ? 'Signing out...' : 'Sign Out'}
      </button>

      {/* Error message tooltip */}
      {error && (
        <div className="absolute top-full mt-2 right-0 bg-red-100 border border-red-400 text-red-700 px-3 py-2 rounded text-sm whitespace-nowrap z-10">
          {error}
        </div>
      )}
    </div>
  );
}
