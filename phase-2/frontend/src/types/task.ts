// T011: TypeScript Task Type Definitions

export interface Task {
  id: string;
  user_id: string;
  title: string;
  description?: string | null;
  completed: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface TaskListResponse {
  items: Task[];
  total: number;
  skip: number;
  limit: number;
}

export interface TaskCreateInput {
  title: string;
  description?: string;
}

export interface TaskUpdateInput {
  title?: string;
  description?: string;
  completed?: boolean;
}
