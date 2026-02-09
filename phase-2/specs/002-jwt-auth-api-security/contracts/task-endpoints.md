# API Contracts: Task Endpoints (Protected with JWT)

**Feature**: 002-jwt-auth-api-security
**Date**: 2026-02-09
**Base URL**: `http://localhost:8000/api/v1` (development)
**Authentication**: Required on ALL endpoints (Bearer token)

---

## Common Headers (All Task Endpoints)

**Required**:
```
Authorization: Bearer <jwt-token>
Content-Type: application/json
```

**Token Requirements**:
- Must be valid JWT token from `/auth/signin` or `/auth/signup`
- Must not be expired (checked against `exp` claim)
- Must be signed with correct JWT_SECRET

**If Missing or Invalid**:
- Returns 401 Unauthorized
- Message: "Missing authentication" or "Invalid token"

---

## GET /users/{user_id}/tasks

**Purpose**: List all tasks for the authenticated user

**Method**: GET

**Path**: `/users/{user_id}/tasks`

**Authentication**: Required (Bearer token)

### Path Parameters

- `user_id` (string, required): User ID to fetch tasks for. Must match the authenticated user's ID (from token).

### Query Parameters (Optional)

```
?skip=0&limit=20
```

- `skip` (integer, default 0): Number of tasks to skip (pagination offset)
- `limit` (integer, default 20, max 100): Number of tasks to return per page

### Request Example

```
GET /users/550e8400-e29b-41d4-a716-446655440000/tasks?skip=0&limit=20
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Response

**Success (200 OK)**:
```json
{
  "items": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "completed": false,
      "created_at": "2026-02-09T10:30:00Z",
      "updated_at": "2026-02-09T10:30:00Z"
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440002",
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Complete project proposal",
      "description": "Add chapter 3, review figures",
      "completed": true,
      "created_at": "2026-02-08T14:00:00Z",
      "updated_at": "2026-02-09T09:15:00Z"
    }
  ],
  "total": 25,
  "skip": 0,
  "limit": 20
}
```

**Field Descriptions**:
- `items` (array): List of task objects
- `total` (integer): Total number of user's tasks
- `skip` (integer): Number of tasks skipped
- `limit` (integer): Number of tasks returned

### Errors

**401 Unauthorized** - Missing or invalid token:
```json
{
  "detail": "Missing authentication"
}
```

**403 Forbidden** - Authenticated user doesn't match path parameter:
```json
{
  "detail": "You do not have permission to access this resource"
}
```

Example: Token user_id = 'AAA', path user_id = 'BBB' → 403

**500 Internal Server Error**:
```json
{
  "detail": "An error occurred"
}
```

### Example Usage

```bash
curl -X GET 'http://localhost:8000/api/v1/users/550e8400-e29b-41d4-a716-446655440000/tasks?skip=0&limit=20' \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Security Notes

- Only returns tasks owned by authenticated user
- Other users' tasks are never visible (403 if accessing another user's user_id)
- Query filtering happens at database level: `WHERE user_id = $1`

---

## POST /users/{user_id}/tasks

**Purpose**: Create a new task for the authenticated user

**Method**: POST

**Path**: `/users/{user_id}/tasks`

**Authentication**: Required (Bearer token)

### Path Parameters

- `user_id` (string, required): User ID to create task for. Must match the authenticated user's ID.

### Request

**Headers**:
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Body** (application/json):
```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}
```

**Field Descriptions**:
- `title` (string, required): Task title. Max 500 characters, cannot be empty.
- `description` (string, optional): Task description. Max 5000 characters.

### Response

**Success (201 Created)**:
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2026-02-09T10:30:00Z",
  "updated_at": "2026-02-09T10:30:00Z"
}
```

### Errors

**400 Bad Request** - Invalid input:
```json
{
  "detail": "Title is required"
}
```

**401 Unauthorized** - Missing or invalid token:
```json
{
  "detail": "Missing authentication"
}
```

**403 Forbidden** - User mismatch:
```json
{
  "detail": "You do not have permission to create tasks for this user"
}
```

**500 Internal Server Error**:
```json
{
  "detail": "An error occurred"
}
```

### Example Usage

```bash
curl -X POST 'http://localhost:8000/api/v1/users/550e8400-e29b-41d4-a716-446655440000/tasks' \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, eggs, bread"
  }'
```

### Implementation Notes

- `user_id` in request body is automatically set from authenticated user's token
- Frontend passes user_id from JWT, not from untrusted user input
- `completed` defaults to `false`
- `created_at` and `updated_at` are set by backend

---

## GET /users/{user_id}/tasks/{task_id}

**Purpose**: Get a specific task by ID

**Method**: GET

**Path**: `/users/{user_id}/tasks/{task_id}`

**Authentication**: Required (Bearer token)

### Path Parameters

- `user_id` (string, required): User ID (must match authenticated user)
- `task_id` (string, required): Task ID to fetch

### Request Example

```
GET /users/550e8400-e29b-41d4-a716-446655440000/tasks/660e8400-e29b-41d4-a716-446655440001
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Response

**Success (200 OK)**:
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2026-02-09T10:30:00Z",
  "updated_at": "2026-02-09T10:30:00Z"
}
```

### Errors

**401 Unauthorized** - Missing or invalid token:
```json
{
  "detail": "Missing authentication"
}
```

**403 Forbidden** - User mismatch:
```json
{
  "detail": "You do not have permission to access this resource"
}
```

**404 Not Found** - Task doesn't exist or belongs to different user:
```json
{
  "detail": "Task not found"
}
```

---

## PUT /users/{user_id}/tasks/{task_id}

**Purpose**: Update an existing task

**Method**: PUT

**Path**: `/users/{user_id}/tasks/{task_id}`

**Authentication**: Required (Bearer token)

### Path Parameters

- `user_id` (string, required): User ID (must match authenticated user)
- `task_id` (string, required): Task ID to update

### Request

**Headers**:
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Body** (application/json):
```json
{
  "title": "Buy groceries and cook dinner",
  "description": "Milk, eggs, bread, chicken",
  "completed": false
}
```

**Field Descriptions** (all optional):
- `title` (string): New task title. Max 500 characters.
- `description` (string): New task description. Max 5000 characters.
- `completed` (boolean): New completion status.

### Response

**Success (200 OK)**:
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Buy groceries and cook dinner",
  "description": "Milk, eggs, bread, chicken",
  "completed": false,
  "created_at": "2026-02-09T10:30:00Z",
  "updated_at": "2026-02-09T11:45:00Z"
}
```

**Note**: `updated_at` is automatically updated to current time

### Errors

**400 Bad Request** - Invalid input:
```json
{
  "detail": "Title cannot be empty"
}
```

**401 Unauthorized** - Missing or invalid token:
```json
{
  "detail": "Missing authentication"
}
```

**403 Forbidden** - User mismatch:
```json
{
  "detail": "You do not have permission to update this task"
}
```

**404 Not Found** - Task doesn't exist:
```json
{
  "detail": "Task not found"
}
```

### Example Usage

```bash
curl -X PUT 'http://localhost:8000/api/v1/users/550e8400-e29b-41d4-a716-446655440000/tasks/660e8400-e29b-41d4-a716-446655440001' \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries and cook dinner",
    "completed": false
  }'
```

---

## DELETE /users/{user_id}/tasks/{task_id}

**Purpose**: Delete a task

**Method**: DELETE

**Path**: `/users/{user_id}/tasks/{task_id}`

**Authentication**: Required (Bearer token)

### Path Parameters

- `user_id` (string, required): User ID (must match authenticated user)
- `task_id` (string, required): Task ID to delete

### Request

**Headers**:
```
Authorization: Bearer <token>
```

**Body**: Empty

### Response

**Success (204 No Content)**:
```
(empty body)
```

### Errors

**401 Unauthorized** - Missing or invalid token:
```json
{
  "detail": "Missing authentication"
}
```

**403 Forbidden** - User mismatch:
```json
{
  "detail": "You do not have permission to delete this task"
}
```

**404 Not Found** - Task doesn't exist:
```json
{
  "detail": "Task not found"
}
```

### Example Usage

```bash
curl -X DELETE 'http://localhost:8000/api/v1/users/550e8400-e29b-41d4-a716-446655440000/tasks/660e8400-e29b-41d4-a716-446655440001' \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## Authorization Rules Summary

| Endpoint | Check | Failure Response |
|----------|-------|-----------------|
| GET /users/{id}/tasks | `token.user_id == {id}` | 403 |
| POST /users/{id}/tasks | `token.user_id == {id}` | 403 |
| GET /users/{id}/tasks/{tid} | `token.user_id == {id}` AND `task.user_id == {id}` | 403 or 404 |
| PUT /users/{id}/tasks/{tid} | `token.user_id == {id}` AND `task.user_id == {id}` | 403 or 404 |
| DELETE /users/{id}/tasks/{tid} | `token.user_id == {id}` AND `task.user_id == {id}` | 403 or 404 |

**Pattern**: Every endpoint validates that:
1. Token is present and valid
2. Token user_id matches path user_id
3. For specific tasks, task.user_id matches token user_id

---

## HTTP Status Codes

| Code | Meaning | When |
|------|---------|------|
| 200 | OK | GET, PUT successful |
| 201 | Created | POST successful |
| 204 | No Content | DELETE successful |
| 400 | Bad Request | Invalid input (missing/empty title) |
| 401 | Unauthorized | Missing or invalid token |
| 403 | Forbidden | User doesn't own resource |
| 404 | Not Found | Task doesn't exist |
| 500 | Server Error | Database error |

---

**Status**: ✅ Ready for implementation
