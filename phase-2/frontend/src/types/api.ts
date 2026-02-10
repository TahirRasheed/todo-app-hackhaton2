// T012: TypeScript API Response Type Definitions

export interface ApiMeta {
  timestamp: string;
  request_id: string;
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, string[]>;
}

export interface ApiResponse<T> {
  data: T | null;
  meta: ApiMeta;
  error: ApiError | null;
}
