/**
 * API Client with JWT Token Management
 * 
 * Automatically attaches JWT tokens from httpOnly cookies to all requests.
 * Handles 401 responses by redirecting to signin.
 */

import axios, { AxiosInstance, AxiosError, AxiosResponse } from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance with credentials enabled
const api: AxiosInstance = axios.create({
  baseURL: API_URL,
  withCredentials: true, // Include httpOnly cookies in requests
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: Add token to Authorization header if present
api.interceptors.request.use(
  (config) => {
    // Get token from localStorage and attach to Authorization header
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor: Handle 401 (token expired/invalid)
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Token expired or invalid - clear localStorage and redirect to signin
      if (typeof window !== 'undefined') {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/auth/signin';
      }
    }
    return Promise.reject(error);
  }
);

export default api;

/**
 * Helper function to extract error message from API response
 */
export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    return (
      (error.response?.data as any)?.detail ||
      error.message ||
      'An error occurred'
    );
  }
  return 'An unexpected error occurred';
}

/**
 * User token response from auth endpoints
 */
export interface UserTokenResponse {
  id: string
  email: string
  name?: string
  token: string
  expiresIn: number
}

/**
 * Helper function for signup API call
 */
export async function signupUser(
  email: string,
  password: string,
  name?: string
): Promise<UserTokenResponse> {
  const response = await api.post<UserTokenResponse>('/api/v1/auth/signup', {
    email,
    password,
    name,
  });
  return response.data;
}

/**
 * Helper function for signin API call
 */
export async function signinUser(
  email: string,
  password: string
): Promise<UserTokenResponse> {
  const response = await api.post<UserTokenResponse>('/api/v1/auth/signin', {
    email,
    password,
  });
  return response.data;
}

/**
 * Helper function for signout API call
 *
 * Requires valid JWT token in Authorization header.
 * Clears token from localStorage after successful signout.
 */
export async function signoutUser(): Promise<void> {
  // Get token from localStorage to include in request
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;

  if (!token) {
    throw new Error('No authentication token found');
  }

  // Call signout endpoint with token in Authorization header
  await api.post('/api/v1/auth/signout', {}, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  // Clear token from localStorage on success
  if (typeof window !== 'undefined') {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  }
}

/**
 * Helper function to get user's tasks
 */
export async function getUserTasks(
  userId: string,
  skip: number = 0,
  limit: number = 20
) {
  return api.get(`/users/${userId}/tasks`, {
    params: { skip, limit },
  });
}
