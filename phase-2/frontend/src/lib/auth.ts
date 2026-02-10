// T015: Auth Utility Functions

import { User } from '@/types/auth';
import { getCookie, setCookie, deleteCookie } from './storage';

const USER_STORAGE_KEY = 'user';

export function isAuthenticated(): boolean {
  if (typeof window === 'undefined') {
    return false;
  }
  return !!getCookie('token');
}

export function getToken(): string | null {
  if (typeof window === 'undefined') {
    return null;
  }
  return getCookie('token');
}

export function setToken(token: string): void {
  if (typeof window !== 'undefined') {
    setCookie('token', token, {
      maxAge: 15 * 60, // 15 minutes
      path: '/',
      sameSite: 'Lax',
    });
  }
}

export function clearToken(): void {
  if (typeof window !== 'undefined') {
    deleteCookie('token');
  }
}

export function getUser(): User | null {
  if (typeof window === 'undefined') {
    return null;
  }

  try {
    const userJson = localStorage.getItem(USER_STORAGE_KEY);
    if (userJson) {
      return JSON.parse(userJson);
    }
  } catch (error) {
    console.error('Failed to parse user from localStorage:', error);
  }

  return null;
}

export function setUser(user: User): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user));
  }
}

export function clearUser(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(USER_STORAGE_KEY);
  }
}

export function logout(): void {
  clearToken();
  clearUser();
}
