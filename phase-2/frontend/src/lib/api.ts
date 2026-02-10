// T016-T017: Centralized API Client Wrapper & Type-Safe Helpers

import { ApiResponse, ApiError } from '@/types/api';
import { AuthResponse, SignupRequest, SigninRequest } from '@/types/auth';
import { Task, TaskListResponse, TaskCreateInput, TaskUpdateInput } from '@/types/task';
import { getToken } from './storage';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// T016: Core API call wrapper
export async function apiCall<T>(
  endpoint: string,
  options: RequestInit & { requiresAuth?: boolean } = {}
): Promise<ApiResponse<T>> {
  const { requiresAuth = true, ...fetchOptions } = options;

  // Prepare headers
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...fetchOptions.headers,
  };

  // Attach JWT token if required
  if (requiresAuth) {
    const token = getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
  }

  try {
    const response = await fetch(`${API_URL}${endpoint}`, {
      ...fetchOptions,
      headers,
    });

    const data: ApiResponse<T> = await response.json();

    // Handle 401 Unauthorized - redirect to signin
    if (response.status === 401) {
      if (typeof window !== 'undefined') {
        window.location.href = '/signin';
      }
      return {
        data: null,
        meta: { timestamp: new Date().toISOString(), request_id: '' },
        error: { code: 'UNAUTHORIZED', message: 'Your session has expired. Please sign in again.' },
      };
    }

    // Handle 403 Forbidden
    if (response.status === 403) {
      return {
        data: null,
        meta: { timestamp: new Date().toISOString(), request_id: '' },
        error: { code: 'FORBIDDEN', message: "You don't have permission to access this resource." },
      };
    }

    return data;
  } catch (error) {
    console.error('API call failed:', error);
    return {
      data: null,
      meta: { timestamp: new Date().toISOString(), request_id: '' },
      error: {
        code: 'NETWORK_ERROR',
        message: 'Unable to connect. Please check your internet connection.',
      },
    };
  }
}

// T017: Type-safe API helpers

export async function signup(
  email: string,
  password: string,
  name: string
): Promise<ApiResponse<AuthResponse>> {
  const request: SignupRequest = { email, password, name };
  return apiCall<AuthResponse>('/api/v1/auth/signup', {
    method: 'POST',
    body: JSON.stringify(request),
    requiresAuth: false,
  });
}

export async function signin(
  email: string,
  password: string
): Promise<ApiResponse<AuthResponse>> {
  const request: SigninRequest = { email, password };
  return apiCall<AuthResponse>('/api/v1/auth/signin', {
    method: 'POST',
    body: JSON.stringify(request),
    requiresAuth: false,
  });
}

export async function signout(): Promise<ApiResponse<{ message: string }>> {
  return apiCall<{ message: string }>('/api/v1/auth/signout', {
    method: 'POST',
    body: JSON.stringify({}),
    requiresAuth: true,
  });
}

export async function getTasks(
  userId: string,
  skip: number = 0,
  limit: number = 20
): Promise<ApiResponse<TaskListResponse>> {
  return apiCall<TaskListResponse>(
    `/api/v1/users/${userId}/tasks?skip=${skip}&limit=${limit}`,
    {
      method: 'GET',
      requiresAuth: true,
    }
  );
}

export async function createTask(
  userId: string,
  title: string,
  description?: string
): Promise<ApiResponse<Task>> {
  const request: TaskCreateInput = { title, description };
  return apiCall<Task>(`/api/v1/users/${userId}/tasks`, {
    method: 'POST',
    body: JSON.stringify(request),
    requiresAuth: true,
  });
}

export async function updateTask(
  userId: string,
  taskId: string,
  updates: Partial<TaskUpdateInput>
): Promise<ApiResponse<Task>> {
  return apiCall<Task>(`/api/v1/users/${userId}/tasks/${taskId}`, {
    method: 'PUT',
    body: JSON.stringify(updates),
    requiresAuth: true,
  });
}

export async function deleteTask(
  userId: string,
  taskId: string
): Promise<ApiResponse<null>> {
  return apiCall<null>(`/api/v1/users/${userId}/tasks/${taskId}`, {
    method: 'DELETE',
    requiresAuth: true,
  });
}
