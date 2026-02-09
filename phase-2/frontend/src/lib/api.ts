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
    // Token is sent automatically in httpOnly cookies via withCredentials
    // No need to manually attach it
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
      // Token expired or invalid - redirect to signin
      if (typeof window !== 'undefined') {
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
 * Helper function for signup API call
 */
export async function signupUser(
  email: string,
  password: string,
  name: string
) {
  return api.post('/auth/signup', {
    email,
    password,
    name,
  });
}

/**
 * Helper function for signin API call
 */
export async function signinUser(email: string, password: string) {
  return api.post('/auth/signin', {
    email,
    password,
  });
}

/**
 * Helper function for signout API call
 */
export async function signoutUser() {
  return api.post('/auth/signout');
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
