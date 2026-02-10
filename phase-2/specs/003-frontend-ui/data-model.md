# Data Model: Frontend Application — Todo Web Interface

**Created**: 2026-02-10 | **Feature**: 003-frontend-ui | **Related**: [plan.md](plan.md)

---

## Frontend Component Hierarchy & State Model

### Root Application Structure

```
App (Root)
├── Root Layout (src/pages/layout.tsx)
│   ├── AuthProvider (Context wrapper)
│   ├── Header Navigation
│   ├── Main Content (Route-specific)
│   └── Footer
└── Error Boundary
```

---

## Key Entities & Interfaces

### User (Authenticated User)

**TypeScript Interface** (`src/types/auth.ts`):
```typescript
interface User {
  id: string;           // UUID from backend
  email: string;        // Unique email address
  name: string;         // Display name
}

interface AuthContext {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  token: string | null;
  login(email: string, password: string): Promise<void>;
  signup(email: string, password: string, name: string): Promise<void>;
  logout(): Promise<void>;
  error: string | null;
}
```

**Where stored**:
- User object: React Context (AuthContext)
- JWT token: httpOnly cookie (set by backend)
- Expiration: JWT `exp` claim (15 minutes from login)

**Validation Rules**:
- Email: RFC 5322 format (validated client-side, backend confirms uniqueness)
- Password: 8+ characters, uppercase, lowercase, number (client-side validation only)
- Name: Non-empty string, max 255 characters

---

### Task (Individual Todo Item)

**TypeScript Interface** (`src/types/task.ts`):
```typescript
interface Task {
  id: string;                  // UUID from backend
  user_id: string;             // Owner (must match authenticated user_id)
  title: string;               // Required, non-empty
  description?: string;        // Optional
  completed: boolean;          // Default false
  createdAt: string;          // ISO 8601 timestamp
  updatedAt: string;          // ISO 8601 timestamp
}

interface TaskListResponse {
  items: Task[];              // Array of tasks for current page
  total: number;              // Total count of user's tasks
  skip: number;               // Offset (pagination)
  limit: number;              // Page size (typically 20)
}

interface TaskCreateInput {
  title: string;              // Required
  description?: string;       // Optional
}

interface TaskUpdateInput {
  title?: string;             // Optional update
  description?: string;       // Optional update
  completed?: boolean;        // Optional update
}
```

**Where stored**:
- Task list: React state (TaskList component or custom hook)
- Current editing task: React state (TaskForm modal)
- Pagination state: React state (current page, total count)

**Validation Rules**:
- Title: Required, non-empty, max 255 characters
- Description: Optional, max 1000 characters
- Completed: Boolean (true/false)
- user_id: Must match authenticated user (backend enforces)

**State Transitions**:
```
Task Creation:
incomplete → pending (API call) → completed in list or error

Task Update:
any state → pending (API call) → updated state or error

Task Deletion:
any state → pending (confirm dialog) → removed from list or error

Task Completion Toggle:
incomplete → completed (optimistic) → persisted (API)
completed → incomplete (optimistic) → persisted (API)
```

---

### JWT Token (Authentication)

**Where stored**: httpOnly cookie (set by backend, browser sends automatically)

**Contents** (JWT claims):
```json
{
  "sub": "user-id-uuid",        // Subject (user ID)
  "email": "user@example.com",  // User email
  "iat": 1707528000,            // Issued at (unix timestamp)
  "exp": 1707528900,            // Expiration (900 seconds = 15 minutes)
  "iss": "todo-app",            // Issuer
  "aud": "todo-app-users"       // Audience
}
```

**Frontend usage**:
- Automatically sent with every API request (browser handles httpOnly cookie)
- Frontend reads from cookie only for debugging/validation
- Expiration check: if current time > exp, redirect to signin

---

### UI State (Component-Level)

**Loading State**:
```typescript
interface LoadingState {
  isLoading: boolean;           // True while API call in progress
  loadingMessage?: string;      // "Loading tasks...", "Creating task..."
}
```

**Error State**:
```typescript
interface ErrorState {
  error: ErrorResponse | null;
}

interface ErrorResponse {
  code: string;                 // "VALIDATION_ERROR", "UNAUTHORIZED", etc.
  message: string;              // User-friendly error message
  details?: Record<string, string[]>;  // Field-level errors
}
```

**Form State** (Create/Edit Task Modal):
```typescript
interface TaskFormState {
  title: string;
  description: string;
  isSubmitting: boolean;
  errors: Record<string, string>;
}
```

**Pagination State**:
```typescript
interface PaginationState {
  currentPage: number;          // 0-indexed page number
  pageSize: number;             // Items per page (20)
  totalItems: number;           // Total task count
  totalPages: number;           // Computed: ceil(totalItems / pageSize)
}
```

---

## Component State Tree

### Authentication Flow

```
AuthContext (Global)
├── user: User | null
├── isAuthenticated: boolean
├── token: string | null
├── isLoading: boolean
├── error: string | null
├── login()
├── signup()
└── logout()

↓ Consumed by

Header Component
├── Display user name
├── Show logout button
└── Handle logout click

ProtectedRoute Wrapper
├── Check isAuthenticated
├── Redirect to /signin if false
└── Render component if true
```

### Task Management Flow

```
DashboardPage (Local State)
├── tasks: Task[]
├── isLoading: boolean
├── error: string | null
├── currentPage: number
├── pageSize: number
├── totalItems: number
├── selectedTask: Task | null (currently editing)
├── showDeleteConfirm: boolean
├── deleteTargetId: string | null
└── Actions:
    ├── fetchTasks()
    ├── createTask()
    ├── updateTask()
    ├── deleteTask()
    ├── toggleCompletion()
    └── openEditModal()

↓ Passed to child components

TaskList Component
├── tasks (props)
├── isLoading (props)
├── error (props)
├── pagination (props)
├── onEdit (callback)
├── onDelete (callback)
├── onToggleCompletion (callback)
└── Children:
    ├── TaskCard (repeating)
    └── Pagination Controls

TaskCard Component (per task)
├── task (props)
├── onEdit (callback)
├── onDelete (callback)
└── onToggleCompletion (callback)

TaskForm Modal
├── task (props, for edit mode)
├── mode: "create" | "edit" (props)
├── isSubmitting (local)
├── onSubmit (callback)
└── onCancel (callback)

ConfirmDialog (Delete Confirmation)
├── message (props)
├── onConfirm (callback)
└── onCancel (callback)
```

---

## Data Flow Patterns

### User Authentication

```
Signup Form (SignupPage)
    ↓ User fills: email, password, name
    ↓ Client-side validation (email format, password strength)
    ↓ POST /api/v1/auth/signup { email, password, name }
    ↓
Backend (FastAPI)
    ├─ Validate input (Pydantic schema)
    ├─ Check email uniqueness
    ├─ Hash password (bcrypt)
    ├─ Create user record
    ├─ Generate JWT token
    └─ Set-Cookie: token (httpOnly, Secure)
    ↓ Response: { user: { id, email, name }, token, expiresIn }
    ↓
Frontend
    ├─ Store token in httpOnly cookie (automatic)
    ├─ Save user to AuthContext
    ├─ Set isAuthenticated = true
    └─ Redirect to /dashboard
```

### Task Creation

```
Dashboard Page
    ↓ User clicks "Create Task" button
    ↓ TaskForm Modal opens (mode: "create")
    ↓ User fills: title, description
    ↓ Client-side validation (title required, non-empty)
    ↓ User clicks "Create"
    ↓ Optimistic update: add task to tasks[] with pending state
    ↓ POST /api/v1/users/{user_id}/tasks { title, description }
    ↓   (Authorization: Bearer <token> sent automatically)
    ↓
Backend (FastAPI)
    ├─ Extract JWT token from Authorization header
    ├─ Verify JWT signature
    ├─ Extract user_id from token
    ├─ Validate user_id in URL matches token user_id
    ├─ Create task record in database (user_id set to authenticated user)
    └─ Return: { id, user_id, title, description, completed: false, createdAt, updatedAt }
    ↓ Response: { data: task, meta: {}, error: null }
    ↓
Frontend
    ├─ Replace optimistic task with real task from response
    ├─ Close modal
    ├─ Show success message (optional toast)
    └─ Render task in list
```

### Task Update (Edit)

```
Dashboard Page
    ↓ User clicks edit button on task
    ↓ TaskForm Modal opens (mode: "edit", task pre-populated)
    ↓ User modifies title/description/completion
    ↓ User clicks "Save"
    ↓ PUT /api/v1/users/{user_id}/tasks/{task_id} { title, description, completed }
    ↓   (Authorization: Bearer <token> sent automatically)
    ↓
Backend (FastAPI)
    ├─ Extract JWT token, verify signature
    ├─ Extract user_id from token
    ├─ Query task: SELECT * FROM tasks WHERE id = ? AND user_id = ?
    ├─ If not found or user_id mismatch: return 403 Forbidden
    ├─ Update task record in database
    └─ Return: { id, user_id, title, description, completed, createdAt, updatedAt }
    ↓ Response: { data: updated_task, meta: {}, error: null }
    ↓
Frontend
    ├─ Update task in tasks[] array
    ├─ Close modal
    └─ Refresh list display
```

### Task Deletion

```
Dashboard Page
    ↓ User clicks delete button on task
    ↓ ConfirmDialog appears: "Are you sure?"
    ↓ User clicks "Confirm"
    ↓ Optimistic remove: remove task from tasks[] array
    ↓ DELETE /api/v1/users/{user_id}/tasks/{task_id}
    ↓   (Authorization: Bearer <token> sent automatically)
    ↓
Backend (FastAPI)
    ├─ Extract JWT token, verify signature
    ├─ Extract user_id from token
    ├─ Query task: SELECT * FROM tasks WHERE id = ? AND user_id = ?
    ├─ If not found or user_id mismatch: return 403 or 404
    ├─ Delete task record
    └─ Return: 204 No Content (empty body)
    ↓ Response: { data: null, meta: {}, error: null }
    ↓
Frontend
    ├─ Task already removed (optimistic)
    ├─ If error: revert optimistic delete, show error message
    └─ List now reflects deletion
```

---

## Reactive State Management

### React Hooks Used

**useAuth()** (Custom hook):
```typescript
const { user, isAuthenticated, login, signup, logout } = useAuth();
```

**useState()** (React built-in):
```typescript
const [tasks, setTasks] = useState<Task[]>([]);
const [isLoading, setIsLoading] = useState(false);
const [error, setError] = useState<string | null>(null);
const [currentPage, setCurrentPage] = useState(0);
```

**useEffect()** (React built-in):
```typescript
useEffect(() => {
  if (isAuthenticated) {
    fetchTasks(currentPage);
  }
}, [isAuthenticated, currentPage]);
```

**useCallback()** (React built-in):
```typescript
const handleCreateTask = useCallback(async (title, description) => {
  // Create task logic
}, [userId, setTasks]);
```

---

## Error States & Handling

### Common Error Scenarios

**401 Unauthorized** (Token missing or expired):
- User redirected to /signin
- Error message: "Your session has expired. Please sign in again."
- Token cleared from cookie

**403 Forbidden** (User accessing another user's task):
- Error displayed in UI
- Error message: "You don't have permission to access this resource."
- Task operation cancelled

**400 Bad Request** (Invalid input):
- Form validation errors displayed
- Error message: "Title is required" (field-specific)
- Form submission prevented

**500 Internal Server Error**:
- Generic error message: "Something went wrong. Please try again later."
- Retry button shown
- Task state preserved for retry

**Network Error** (No internet connection):
- Error message: "Unable to connect. Please check your internet connection."
- Retry button shown
- No state changes applied

---

## Summary

This data model defines the component hierarchy, state management patterns, and data flow for the frontend application. All state is client-side (React state), with data persisted on the backend via REST API. Authentication state is global (Context), while task state is local to the dashboard page. All API responses flow through a consistent error handling pipeline that updates UI state appropriately.
