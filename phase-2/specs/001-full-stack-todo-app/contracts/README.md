# API Contracts: Phase II Todo Full-Stack Web Application

**Date**: 2026-02-09 | **Data Model**: [../data-model.md](../data-model.md)

## Overview

All endpoints follow REST conventions with standard HTTP methods and status codes. Responses conform to a unified JSON schema with `data`, `meta`, and `error` fields.

**Base URL**: `http://localhost:8000` (development) | `https://api.example.com` (production)

**Authentication**: JWT token via `Authorization: Bearer <token>` header OR httpOnly cookie (set by Better Auth)

---

## Authentication Endpoints

### POST /auth/signup

Create a new user account and issue JWT token.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123",
  "name": "John Doe"
}
```

**Response** (201 Created):
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "name": "John Doe",
    "created_at": "2026-02-09T10:30:45Z"
  },
  "meta": {
    "timestamp": "2026-02-09T10:30:45Z",
    "request_id": "req-abc123"
  },
  "error": null
}
```

**Headers**: Response includes `Set-Cookie: jwt=<token>; HttpOnly; Secure; SameSite=Strict`

**Error Cases**:
- `400 Bad Request`: Email already exists, password too short, invalid email format
- `422 Unprocessable Entity`: Missing required fields (email, password)

---

### POST /auth/signin

Authenticate user and issue JWT token.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123"
}
```

**Response** (200 OK):
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "name": "John Doe",
    "created_at": "2026-02-09T10:30:45Z"
  },
  "meta": {
    "timestamp": "2026-02-09T10:31:00Z",
    "request_id": "req-def456"
  },
  "error": null
}
```

**Headers**: Response includes `Set-Cookie: jwt=<token>; HttpOnly; Secure; SameSite=Strict`

**Error Cases**:
- `400 Bad Request`: Email not found or password incorrect (generic message for security)
- `401 Unauthorized`: Invalid credentials

---

### POST /auth/signout

Invalidate session and clear JWT cookie.

**Request**: No body required

**Response** (200 OK):
```json
{
  "data": null,
  "meta": {
    "timestamp": "2026-02-09T10:32:00Z",
    "request_id": "req-ghi789"
  },
  "error": null
}
```

**Headers**: Response includes `Set-Cookie: jwt=; Max-Age=0;` (clears cookie)

**Error Cases**:
- `401 Unauthorized`: No valid JWT token provided

---

## Task Endpoints

All task endpoints require JWT authentication. If JWT is invalid or expired, return `401 Unauthorized` with message "Unauthorized".

### GET /api/v1/users/{user_id}/tasks

List all tasks for the authenticated user with pagination.

**Path Parameters**:
- `user_id` (UUID): The user ID from JWT token

**Query Parameters**:
- `skip` (integer, default=0): Number of tasks to skip (for pagination)
- `limit` (integer, default=20): Maximum number of tasks to return (max 100)

**Headers**:
```
Authorization: Bearer <jwt_token>
```

**Response** (200 OK):
```json
{
  "data": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread, coffee",
      "completed": false,
      "created_at": "2026-02-09T10:30:00Z",
      "updated_at": "2026-02-09T10:30:00Z"
    },
    {
      "id": "770e8400-e29b-41d4-a716-446655440002",
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Review PR #42",
      "description": null,
      "completed": true,
      "created_at": "2026-02-09T08:15:00Z",
      "updated_at": "2026-02-09T11:45:00Z"
    }
  ],
  "meta": {
    "timestamp": "2026-02-09T10:35:00Z",
    "request_id": "req-jkl012",
    "pagination": {
      "skip": 0,
      "limit": 20,
      "total": 2
    }
  },
  "error": null
}
```

**Error Cases**:
- `401 Unauthorized`: Missing or invalid JWT token
- `403 Forbidden`: JWT user_id doesn't match `{user_id}` parameter

---

### POST /api/v1/users/{user_id}/tasks

Create a new task for the authenticated user.

**Path Parameters**:
- `user_id` (UUID): The user ID from JWT token

**Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request**:
```json
{
  "title": "New task title",
  "description": "Optional task description"
}
```

**Response** (201 Created):
```json
{
  "data": {
    "id": "880e8400-e29b-41d4-a716-446655440003",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "New task title",
    "description": "Optional task description",
    "completed": false,
    "created_at": "2026-02-09T10:40:00Z",
    "updated_at": "2026-02-09T10:40:00Z"
  },
  "meta": {
    "timestamp": "2026-02-09T10:40:00Z",
    "request_id": "req-mno345"
  },
  "error": null
}
```

**Error Cases**:
- `400 Bad Request`: Missing title, title exceeds 500 chars, description exceeds 5000 chars
- `401 Unauthorized`: Missing or invalid JWT token
- `403 Forbidden`: JWT user_id doesn't match `{user_id}` parameter
- `422 Unprocessable Entity`: Invalid request body

---

### GET /api/v1/users/{user_id}/tasks/{task_id}

Get a single task by ID.

**Path Parameters**:
- `user_id` (UUID): The user ID from JWT token
- `task_id` (UUID): The task ID to retrieve

**Headers**:
```
Authorization: Bearer <jwt_token>
```

**Response** (200 OK):
```json
{
  "data": {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread, coffee",
    "completed": false,
    "created_at": "2026-02-09T10:30:00Z",
    "updated_at": "2026-02-09T10:30:00Z"
  },
  "meta": {
    "timestamp": "2026-02-09T10:45:00Z",
    "request_id": "req-pqr678"
  },
  "error": null
}
```

**Error Cases**:
- `401 Unauthorized`: Missing or invalid JWT token
- `403 Forbidden`: JWT user_id doesn't match `{user_id}` parameter OR task doesn't belong to user
- `404 Not Found`: Task with `{task_id}` doesn't exist

---

### PUT /api/v1/users/{user_id}/tasks/{task_id}

Update a task (title, description, completion status).

**Path Parameters**:
- `user_id` (UUID): The user ID from JWT token
- `task_id` (UUID): The task ID to update

**Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request** (partial update allowed):
```json
{
  "title": "Updated task title",
  "description": "Updated description",
  "completed": true
}
```

**Response** (200 OK):
```json
{
  "data": {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Updated task title",
    "description": "Updated description",
    "completed": true,
    "created_at": "2026-02-09T10:30:00Z",
    "updated_at": "2026-02-09T10:50:00Z"
  },
  "meta": {
    "timestamp": "2026-02-09T10:50:00Z",
    "request_id": "req-stu901"
  },
  "error": null
}
```

**Error Cases**:
- `400 Bad Request`: Title is empty, title exceeds 500 chars, description exceeds 5000 chars
- `401 Unauthorized`: Missing or invalid JWT token
- `403 Forbidden`: JWT user_id doesn't match `{user_id}` parameter OR task doesn't belong to user
- `404 Not Found`: Task with `{task_id}` doesn't exist
- `422 Unprocessable Entity`: Invalid request body

---

### DELETE /api/v1/users/{user_id}/tasks/{task_id}

Delete a task permanently.

**Path Parameters**:
- `user_id` (UUID): The user ID from JWT token
- `task_id` (UUID): The task ID to delete

**Headers**:
```
Authorization: Bearer <jwt_token>
```

**Response** (204 No Content):
```
(empty body)
```

**Error Cases**:
- `401 Unauthorized`: Missing or invalid JWT token
- `403 Forbidden`: JWT user_id doesn't match `{user_id}` parameter OR task doesn't belong to user
- `404 Not Found`: Task with `{task_id}` doesn't exist

---

## Standard Response Format

All responses follow this schema:

### Success Response (2xx)

```json
{
  "data": {
    // Response payload: object, array, or null
  },
  "meta": {
    "timestamp": "ISO8601 datetime",
    "request_id": "unique request identifier"
  },
  "error": null
}
```

### Error Response (4xx, 5xx)

```json
{
  "data": null,
  "meta": {
    "timestamp": "ISO8601 datetime",
    "request_id": "unique request identifier"
  },
  "error": {
    "code": "ERROR_CODE",
    "message": "User-friendly error message",
    "details": {
      "field_name": "field-specific error message"  // optional, only for validation errors
    }
  }
}
```

## HTTP Status Codes

| Code | Meaning | Trigger | Example |
|------|---------|---------|---------|
| **200** | OK | Successful GET, PUT | Retrieve task, update task |
| **201** | Created | Successful POST | Create user, create task |
| **204** | No Content | Successful DELETE | Delete task (no response body) |
| **400** | Bad Request | Invalid input | Missing title, invalid email, title too long |
| **401** | Unauthorized | Missing/invalid JWT | Expired token, malformed token, no token provided |
| **403** | Forbidden | User lacks permission | Cross-user access attempt, task doesn't belong to user |
| **404** | Not Found | Resource doesn't exist | Task ID not found, user not found |
| **422** | Unprocessable Entity | Request body validation failure | Invalid JSON, missing required fields |
| **500** | Internal Server Error | Unexpected server failure | Database connection lost, unhandled exception |
| **503** | Service Unavailable | Service temporarily down | Database unavailable, deployment in progress |

## Common Error Scenarios

### Token Expired (401)
```json
{
  "data": null,
  "meta": { "timestamp": "...", "request_id": "..." },
  "error": {
    "code": "TOKEN_EXPIRED",
    "message": "Your session has expired. Please log in again."
  }
}
```

### Cross-User Access Attempt (403)
```json
{
  "data": null,
  "meta": { "timestamp": "...", "request_id": "..." },
  "error": {
    "code": "FORBIDDEN",
    "message": "You do not have permission to access this resource."
  }
}
```

### Task Not Found (404)
```json
{
  "data": null,
  "meta": { "timestamp": "...", "request_id": "..." },
  "error": {
    "code": "TASK_NOT_FOUND",
    "message": "Task with ID xyz not found."
  }
}
```

### Validation Error (400)
```json
{
  "data": null,
  "meta": { "timestamp": "...", "request_id": "..." },
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed.",
    "details": {
      "title": "Task title is required and must not exceed 500 characters",
      "email": "Invalid email format"
    }
  }
}
```

## Authentication Flow

1. **Signup**: `POST /auth/signup` → Response includes JWT in httpOnly cookie
2. **Signin**: `POST /auth/signin` → Response includes JWT in httpOnly cookie
3. **Authenticated Request**: `GET /api/v1/users/{user_id}/tasks`
   - Include `Authorization: Bearer <jwt>` header OR rely on cookie (automatic with httpOnly)
   - Backend verifies JWT signature and extracts user_id
   - If valid and user_id matches URL parameter: proceed
   - If invalid/expired: return 401 Unauthorized
   - If user_id mismatch: return 403 Forbidden
4. **Signout**: `POST /auth/signout` → Clears JWT cookie

## Testing Checklist

- [ ] Signup with valid email/password → 201, user created
- [ ] Signup with existing email → 400, "Email already exists"
- [ ] Signup with weak password → 400, "Password too short"
- [ ] Signin with valid credentials → 200, JWT issued
- [ ] Signin with invalid password → 401, "Invalid credentials"
- [ ] GET tasks without JWT → 401 Unauthorized
- [ ] GET tasks with expired JWT → 401 Unauthorized
- [ ] GET tasks with valid JWT → 200, task list returned
- [ ] GET tasks for another user → 403 Forbidden
- [ ] POST task without title → 400, validation error
- [ ] POST task with title > 500 chars → 400, validation error
- [ ] POST task with valid title → 201, task created
- [ ] PUT task to mark complete → 200, updated task returned
- [ ] PUT task for another user → 403 Forbidden
- [ ] DELETE task → 204 No Content
- [ ] DELETE non-existent task → 404 Not Found

---

**Status**: ✅ DRAFT (Phase 1 design complete)
**Next**: Generate quickstart.md and OpenAPI schema (openapi.yaml)
