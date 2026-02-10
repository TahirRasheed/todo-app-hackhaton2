// T013: Custom Auth Hook

'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, AuthContextType } from '@/types/auth';
import * as authApi from '@/lib/api';
import * as authUtils from '@/lib/auth';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Initialize auth state on mount
  useEffect(() => {
    const storedUser = authUtils.getUser();
    if (storedUser && authUtils.isAuthenticated()) {
      setUser(storedUser);
    }
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    try {
      setError(null);
      const response = await authApi.signin(email, password);

      if (response.error) {
        setError(response.error.message);
        throw new Error(response.error.message);
      }

      if (response.data) {
        authUtils.setToken(response.data.token);
        const userData: User = {
          id: response.data.id,
          email: response.data.email,
          name: response.data.name,
        };
        authUtils.setUser(userData);
        setUser(userData);
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Login failed';
      setError(message);
      throw err;
    }
  };

  const signup = async (email: string, password: string, name: string) => {
    try {
      setError(null);
      const response = await authApi.signup(email, password, name);

      if (response.error) {
        setError(response.error.message);
        throw new Error(response.error.message);
      }

      if (response.data) {
        authUtils.setToken(response.data.token);
        const userData: User = {
          id: response.data.id,
          email: response.data.email,
          name: response.data.name,
        };
        authUtils.setUser(userData);
        setUser(userData);
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Signup failed';
      setError(message);
      throw err;
    }
  };

  const logout = async () => {
    try {
      await authApi.signout();
    } catch (err) {
      console.error('Logout API failed:', err);
    } finally {
      authUtils.logout();
      setUser(null);
      setError(null);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user && authUtils.isAuthenticated(),
        isLoading,
        error,
        login,
        signup,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
