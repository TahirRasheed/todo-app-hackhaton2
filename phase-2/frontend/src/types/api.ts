/**
 * API Response and Data Types
 */

export interface ApiResponse<T> {
  data: T | null;
  meta: {
    timestamp: string;
    request_id: string;
  };
  error: {
    code: string;
    message: string;
    details?: Record<string, string>;
  } | null;
}

export interface User {
  id: string;
  email: string;
  name: string;
  created_at: string;
}

export interface Task {
  id: string;
  user_id: string;
  title: string;
  description?: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
}
