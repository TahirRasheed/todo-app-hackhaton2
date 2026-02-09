/**
 * API Client - Fetch wrapper with JWT token attachment
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface RequestOptions extends RequestInit {
  includeAuth?: boolean;
}

async function apiClient<T>(
  endpoint: string,
  options: RequestOptions = {},
): Promise<T> {
  const { includeAuth = true, ...init } = options;

  const headers = new Headers(init.headers || {});
  headers.set('Content-Type', 'application/json');

  // Attach JWT token if needed
  if (includeAuth) {
    const token = getToken();
    if (token) {
      headers.set('Authorization', `Bearer ${token}`);
    }
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...init,
    headers,
  });

  if (response.status === 401) {
    // Token expired or invalid
    clearToken();
    window.location.href = '/auth/signin';
    throw new Error('Unauthorized');
  }

  if (response.status === 403) {
    throw new Error('Access Denied');
  }

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error?.message || 'Request failed');
  }

  return response.json();
}

function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  // Get token from localStorage (for MVP, in production use httpOnly cookies)
  return localStorage.getItem('token');
}

function setToken(token: string): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem('token', token);
  }
}

function clearToken(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('token');
  }
}

export { apiClient, getToken, setToken, clearToken, API_URL };
