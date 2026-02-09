/**
 * useAuth Hook
 * 
 * Provides authentication context and utility functions.
 * Manages current user state and logout functionality.
 */

'use client';

import { useCallback, useState } from 'react';
import { useRouter } from 'next/navigation';
import { signoutUser } from '@/lib/api';

export interface AuthUser {
  id: string;
  email: string;
  name?: string;
}

export function useAuth() {
  const router = useRouter();
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Set the current user after successful authentication
   */
  const setCurrentUser = useCallback((userData: AuthUser) => {
    setUser(userData);
    setError(null);
  }, []);

  /**
   * Clear the current user and error state
   */
  const clearUser = useCallback(() => {
    setUser(null);
    setError(null);
  }, []);

  /**
   * Logout the current user
   */
  const logout = useCallback(async () => {
    setIsLoading(true);
    try {
      await signoutUser();
      clearUser();
      router.push('/auth/signin');
    } catch (err: any) {
      setError(err.message || 'Failed to logout');
      // Still clear user and redirect on error
      clearUser();
      router.push('/auth/signin');
    } finally {
      setIsLoading(false);
    }
  }, [clearUser, router]);

  /**
   * Set error message
   */
  const setAuthError = useCallback((errorMessage: string) => {
    setError(errorMessage);
  }, []);

  /**
   * Clear error message
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    user,
    isLoading,
    error,
    setCurrentUser,
    clearUser,
    logout,
    setAuthError,
    clearError,
    isAuthenticated: !!user,
  };
}
