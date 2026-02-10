# Task Management API Contracts

**Feature**: 003-frontend-ui | **Date**: 2026-02-10
**Backend Spec**: [002-jwt-auth-api-security](../../002-jwt-auth-api-security/spec.md)

---

## Common Headers

All task endpoints require JWT authentication:

```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

---

## List Tasks Endpoint

**URL**: `GET /api/v1/users/{user_id}/tasks?skip=0&limit=20`

**Purpose**: Retrieve authenticated user's tasks with pagination

### Request

**URL Parameters**:
- `user_id` (required): UUID of the authenticated user (from JWT token)
- `skip` (optional): Number of tasks to skip (default: 0)
- `limit` (optional): Number of tasks per page (default: 20, max: 100)

**Headers**:
```
Authorization: Bearer <jwt_token>
```

**Example**:
```
GET /api/v1/users/550e8400-e29b-41d4-a716-446655440000/tasks?skip=0&limit=20
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Response

**Success (200 OK)**:
```json
{
  "data": {
    "items": [
      {
        "id": "task-uuid-1",
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "Buy groceries",
        "description": "Milk, eggs, bread",
        "completed": false,
        "createdAt": "2026-02-10T10:00:00Z",
        "updatedAt": "2026-02-10T10:00:00Z"
      },
      {
        "id": "task-uuid-2",
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "Finish project",
        "description": null,
        "completed": true,
        "createdAt": "2026-02-10T09:00:00Z",
        "updatedAt": "2026-02-10T11:30:00Z"
      }
    ],
    "total": 45,
    "skip": 0,
    "limit": 20
  },
  "meta": {
    "timestamp": "2026-02-10T12:00:00Z",
    "request_id": "req-abc123"
  },
  "error": null
}
```

**Frontend handling**:
- Display items in list
- Show pagination: "Page 1 of 3 (45 total tasks)"
- Enable "Previous" / "Next" buttons if more pages available
- Update currentPage state for subsequent requests

### Error Responses

**401 Unauthorized** (Token missing or expired):
```json
{
  "data": null,
  "meta": { ... },
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Missing or invalid authentication token",
    "details": null
  }
}
```

**Frontend handling**:
- Clear token
- Redirect to /signin
- Show message "Your session has expired"

**403 Forbidden** (Wrong user_id in URL):
```json
{
  "data": null,
  "meta": { ... },
  "error": {
    "code": "FORBIDDEN",
    "message": "You don't have permission to access this resource",
    "details": null
  }
}
```

**Frontend handling**:
- This should never happen if frontend correctly uses authenticated user_id
- Show error "You don't have permission to access this resource"
- Redirect to dashboard

---

## Create Task Endpoint

**URL**: `POST /api/v1/users/{user_id}/tasks`

**Purpose**: Create a new task for the authenticated user

### Request

**URL Parameters**:
- `user_id` (required): UUID of the authenticated user (from JWT token)

**Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Body** (JSON):
```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}
```

**Validation** (Client-side pre-checks):
- Title: Required, non-empty, max 255 characters
- Description: Optional, max 1000 characters

### Response

**Success (201 Created)**:
```json
{
  "data": {
    "id": "task-uuid-new",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "createdAt": "2026-02-10T12:00:00Z",
    "updatedAt": "2026-02-10T12:00:00Z"
  },
  "meta": { ... },
  "error": null
}
```

**Frontend handling**:
- Add returned task to tasks[] array
- Close create modal
- Show success message (optional toast)
- Refresh pagination (increment total count)

### Error Responses

**400 Bad Request** (Missing or invalid title):
```json
{
  "data": null,
  "meta": { ... },
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation error",
    "details": {
      "title": ["Title is required"]
    }
  }
}
```

**401 Unauthorized**: See List Tasks response

**403 Forbidden**: See List Tasks response

**Frontend handling**:
- Show field-level error next to title input
- Do NOT submit form again
- Allow user to correct and retry

---

## Update Task Endpoint

**URL**: `PUT /api/v1/users/{user_id}/tasks/{task_id}`

**Purpose**: Update an existing task

### Request

**URL Parameters**:
- `user_id` (required): UUID of the authenticated user (from JWT token)
- `task_id` (required): UUID of the task to update

**Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Body** (JSON) - All fields optional:
```json
{
  "title": "Updated title",
  "description": "Updated description",
  "completed": true
}
```

### Response

**Success (200 OK)**:
```json
{
  "data": {
    "id": "task-uuid",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Updated title",
    "description": "Updated description",
    "completed": true,
    "createdAt": "2026-02-10T10:00:00Z",
    "updatedAt": "2026-02-10T12:30:00Z"
  },
  "meta": { ... },
  "error": null
}
```

**Frontend handling**:
- Update task in tasks[] array
- If modal open: pre-fill with returned values
- Close edit modal (if was open)
- Show success message (optional)
- Refresh list display

### Error Responses

**400 Bad Request** (Invalid data):
```json
{
  "data": null,
  "meta": { ... },
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation error",
    "details": {
      "title": ["Title cannot be empty"]
    }
  }
}
```

**401 Unauthorized**: See List Tasks response

**403 Forbidden**: See List Tasks response

**404 Not Found** (Task doesn't exist):
```json
{
  "data": null,
  "meta": { ... },
  "error": {
    "code": "NOT_FOUND",
    "message": "Task not found",
    "details": null
  }
}
```

**Frontend handling**:
- Task was deleted elsewhere
- Show error "Task not found"
- Remove from tasks[] array
- Close modal

---

## Delete Task Endpoint

**URL**: `DELETE /api/v1/users/{user_id}/tasks/{task_id}`

**Purpose**: Delete a task

### Request

**URL Parameters**:
- `user_id` (required): UUID of the authenticated user (from JWT token)
- `task_id` (required): UUID of the task to delete

**Headers**:
```
Authorization: Bearer <jwt_token>
```

**Example**:
```
DELETE /api/v1/users/550e8400-e29b-41d4-a716-446655440000/tasks/task-uuid-1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Response

**Success (204 No Content)**:
```
(empty body)
```

**Frontend handling**:
- Remove task from tasks[] array
- Close any modals
- Show success message (optional)
- Refresh pagination (decrement total count)

### Error Responses

**401 Unauthorized**: See List Tasks response

**403 Forbidden**: See List Tasks response

**404 Not Found** (Task doesn't exist):
```json
{
  "data": null,
  "meta": { ... },
  "error": {
    "code": "NOT_FOUND",
    "message": "Task not found",
    "details": null
  }
}
```

**Frontend handling**:
- Task already deleted (or never existed)
- Show error "Task not found"
- Remove from tasks[] array anyway
- Close confirmation dialog

---

## Toggle Completion Endpoint

**Implementation**: Use Update Task endpoint with `{ "completed": !current_value }`

**Frontend logic**:
```typescript
const handleToggleCompletion = async (task: Task) => {
  // Optimistic update
  const newCompleted = !task.completed;
  setTasks(tasks.map(t => t.id === task.id ? { ...t, completed: newCompleted } : t));

  try {
    // API call
    const response = await updateTask(userId, task.id, { completed: newCompleted });
    // Verify it matches optimistic update
    setTasks(tasks.map(t => t.id === task.id ? response : t));
  } catch (error) {
    // Revert optimistic update
    setTasks(tasks.map(t => t.id === task.id ? { ...t, completed: !newCompleted } : t));
    setError("Failed to update task. Please try again.");
  }
};
```

---

## Frontend API Wrapper Implementation

**File**: `src/lib/api.ts`

```typescript
export async function getTasks(
  userId: string,
  skip: number = 0,
  limit: number = 20
): Promise<TaskListResponse> {
  const response = await apiCall<{ data: TaskListResponse }>(
    `/api/v1/users/${userId}/tasks?skip=${skip}&limit=${limit}`,
    {
      method: 'GET',
      requiresAuth: true,
    }
  );
  return response.data;
}

export async function createTask(
  userId: string,
  title: string,
  description?: string
): Promise<Task> {
  const response = await apiCall<{ data: Task }>(
    `/api/v1/users/${userId}/tasks`,
    {
      method: 'POST',
      body: JSON.stringify({ title, description }),
      requiresAuth: true,
    }
  );
  return response.data;
}

export async function updateTask(
  userId: string,
  taskId: string,
  updates: Partial<Task>
): Promise<Task> {
  const response = await apiCall<{ data: Task }>(
    `/api/v1/users/${userId}/tasks/${taskId}`,
    {
      method: 'PUT',
      body: JSON.stringify(updates),
      requiresAuth: true,
    }
  );
  return response.data;
}

export async function deleteTask(
  userId: string,
  taskId: string
): Promise<void> {
  await apiCall<void>(
    `/api/v1/users/${userId}/tasks/${taskId}`,
    {
      method: 'DELETE',
      requiresAuth: true,
    }
  );
}
```

---

## Error Code Reference

| Code | HTTP Status | Meaning | Frontend Action |
|------|-------------|---------|-----------------|
| UNAUTHORIZED | 401 | Token missing/expired | Redirect to signin |
| FORBIDDEN | 403 | Wrong user_id | Show "No permission" error |
| NOT_FOUND | 404 | Task doesn't exist | Remove from list, show message |
| VALIDATION_ERROR | 400 | Invalid input | Show field-level errors |
| SERVER_ERROR | 500 | Backend error | Show "Something went wrong" |

---

## Idempotency & Retry Logic

- **GET requests**: Safe to retry, no side effects
- **POST (create)**: Not idempotent - do NOT retry automatically
  - If fails: show error, allow manual retry
- **PUT (update)**: Idempotent - can safely retry
  - If network error: can retry (same result)
- **DELETE**: Can retry (deleting already-deleted resource returns 404)

---

## Testing Scenarios

### Create Task
- [ ] Valid create: Title + optional description → Task added to list
- [ ] Missing title: 400 error, show "Title is required"
- [ ] Very long title: 400 error, show "Title too long"
- [ ] Network error: Show "Unable to connect", allow retry
- [ ] 401 token expired: Redirect to signin

### Update Task
- [ ] Update title: Title changes in list immediately
- [ ] Update completion: Checkbox toggle, visual change (strikethrough)
- [ ] Update description: Description changes in list or detail view
- [ ] Empty title: 400 error, show "Title required"
- [ ] Task deleted elsewhere: 404 error, remove from list

### Delete Task
- [ ] Delete with confirmation: Task removed from list
- [ ] Cancel delete: Confirmation closes, task remains
- [ ] Task already deleted: 404 error, handle gracefully
- [ ] Network error: Show "Unable to connect", allow retry

### Pagination
- [ ] Load first page: Show tasks 0-19, "Page 1 of 3" (if 45 total)
- [ ] Next page: Show tasks 20-39
- [ ] Previous page: Show tasks 0-19
- [ ] Create 21st task: Should appear when navigating to page 2
- [ ] Delete task: Total count decrements, pagination updates
