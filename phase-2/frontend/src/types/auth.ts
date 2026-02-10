// T010: TypeScript Auth Type Definitions

export interface User {
  id: string;
  email: string;
  name: string;
}

export interface AuthResponse {
  id: string;
  email: string;
  name: string;
  token: string;
  expiresIn: number;
}

export interface SignupRequest {
  email: string;
  password: string;
  name: string;
}

export interface SigninRequest {
  email: string;
  password: string;
}

export interface SignoutRequest {
  // Empty body
}

export interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, name: string) => Promise<void>;
  logout: () => Promise<void>;
}
