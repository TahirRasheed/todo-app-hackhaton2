# Data Model: JWT Authentication & API Security

**Date**: 2026-02-09
**Feature**: 002-jwt-auth-api-security
**Status**: Approved for implementation

---

## Entity: User

**Purpose**: Represents a registered user account with authentication credentials

**Table**: `users`

### Fields

| Field | Type | Constraints | Description |
|-------|------|------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique user identifier (auto-generated) |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL, INDEX | User login identifier (required, must be unique) |
| `name` | VARCHAR(255) | NULLABLE | User display name (optional) |
| `password_hash` | VARCHAR(255) | NOT NULL | Bcrypt-hashed password (never stored plain) |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Account creation timestamp (immutable) |

### Validation Rules

**Email**:
- Must be unique across all users
- Must be valid email format (RFC 5322 subset)
- Cannot be empty
- Case-insensitive comparison for uniqueness (normalize to lowercase)

**Password** (at signup):
- Minimum 8 characters
- Must contain at least one uppercase letter (A-Z)
- Must contain at least one lowercase letter (a-z)
- Must contain at least one digit (0-9)
- Examples:
  - ✅ Valid: `MyPassword123`, `SecurePass99`
  - ❌ Invalid: `password123` (no uppercase), `PASSWORD123` (no lowercase), `Pass123` (too short)

**Password Storage**:
- Never store plain text passwords
- Use bcrypt hashing with cost factor 10 (default)
- Generate salt automatically
- Store hashed result in `password_hash` field

**Name**:
- Optional field (can be NULL)
- Maximum 255 characters
- Can contain spaces, Unicode characters
- Examples: `John Doe`, `李明`, `María García-López`

### Relationships

**User → Tasks** (one-to-many):
- A user can have zero or many tasks
- Each task has exactly one owner (user_id foreign key)
- ON DELETE CASCADE: if user is deleted, all their tasks are also deleted
- Used for data isolation (show only user's own tasks)

### Indexes

| Index | Columns | Purpose |
|-------|---------|---------|
| PRIMARY | `id` | Fast lookup by user ID |
| UNIQUE | `email` | Fast email lookup (login), prevent duplicates |

### Example Row

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "john@example.com",
  "name": "John Doe",
  "password_hash": "$2b$10$abcdefghijklmnopqrstuvwxyz...",
  "created_at": "2026-02-09T10:30:00+00:00"
}
```

---

## Entity: JWT Token (Claims)

**Purpose**: Represents an authenticated session token (not stored in database)

**Storage**: Issued to frontend, stored in httpOnly cookie or secure storage

**Format**: JWT (JSON Web Token) using HS256 algorithm

### Claims (Payload)

| Claim | Type | Required | Description |
|-------|------|----------|-------------|
| `sub` | String (UUID) | YES | Subject = user ID (maps to User.id) |
| `email` | String | YES | User email (for display/context) |
| `iat` | Number | YES | Issued at (Unix timestamp in seconds) |
| `exp` | Number | YES | Expiration (Unix timestamp in seconds) |
| `iss` | String | YES | Issuer (identifies token source) |
| `aud` | String | YES | Audience (identifies intended recipient) |

### Example Token Payload

```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",
  "email": "john@example.com",
  "iat": 1707528000,
  "exp": 1707528900,
  "iss": "todo-app",
  "aud": "todo-app-users"
}
```

### Token Signing

| Property | Value | Notes |
|----------|-------|-------|
| Algorithm | HS256 | HMAC with SHA-256 |
| Secret | JWT_SECRET (from env) | 32+ random characters |
| Encoding | Base64URL | Standard JWT encoding |

### Token Lifecycle

1. **Issuance** (signup/signin):
   - Backend creates payload with user_id, email, current time
   - Sets expiration = current time + 15 minutes
   - Signs with JWT_SECRET using HS256
   - Returns encoded token to frontend

2. **Storage** (frontend):
   - Frontend receives token
   - Stores in httpOnly cookie (managed by Better Auth)
   - Cookie sent automatically with CORS credentials

3. **Transmission** (API requests):
   - Frontend extracts token from cookie (automatically by browser)
   - Attaches to Authorization header: `Bearer <token>`
   - Sends with HTTP request to protected endpoint

4. **Verification** (backend):
   - Backend receives request
   - Extracts token from Authorization header
   - Verifies signature using JWT_SECRET
   - Checks expiration time
   - Decodes payload
   - Proceeds with request or returns 401/403

5. **Expiration**:
   - Token valid for 15 minutes after issuance
   - After expiration, backend returns 401 Unauthorized
   - Frontend prompts user to re-authenticate
   - User submits login form again, gets new token

### Token Security

- **Not Stored in Database**: Tokens are ephemeral, verified via signature
- **Signature Verification**: Backend never needs to look up token in DB
- **Expiration Enforcement**: Time-based validation (no state needed)
- **User Identification**: `sub` claim identifies authenticated user
- **Claim Validation**: `exp`, `iss`, `aud` checked on every request

---

## Entity: Task (Protected by User)

**Purpose**: Represents a to-do task with automatic user ownership

**Table**: `tasks`

### Fields

| Field | Type | Constraints | Description |
|-------|------|------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique task identifier |
| `user_id` | UUID | NOT NULL, FOREIGN KEY users(id) ON DELETE CASCADE | Task owner (must be valid user) |
| `title` | VARCHAR(500) | NOT NULL | Task title (required) |
| `description` | TEXT | NULLABLE | Task description (optional) |
| `completed` | BOOLEAN | NOT NULL, DEFAULT FALSE | Completion status |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Creation time |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last modified time |

### Validation Rules

**user_id**:
- Must reference existing user (foreign key constraint)
- Set automatically from authenticated token (user_id claim)
- Cannot be changed after creation
- Used to enforce data isolation

**title**:
- Required (not null)
- Maximum 500 characters
- Cannot be empty
- Examples: `Buy groceries`, `Complete project proposal`

**description**:
- Optional (can be NULL)
- Maximum 5000 characters
- Can contain multiline text
- Examples: `Milk, eggs, bread, cheese`, `Add chapter 3, review figures`

**completed**:
- Boolean flag (true/false)
- Default is false (new tasks start incomplete)
- Toggled by task owner
- No permission change required (owner can toggle own task)

### Relationships

**Task → User** (many-to-one):
- Many tasks belong to one user
- Each task has exactly one owner (user_id)
- Enforced via foreign key constraint
- Cascade delete: deleting user deletes all their tasks

### Indexes

| Index | Columns | Purpose |
|-------|---------|---------|
| PRIMARY | `id` | Fast lookup by task ID |
| FOREIGN KEY | `user_id` | Prevent orphaned tasks |
| INDEX | `user_id` | Filter tasks by owner (fast queries) |
| INDEX | `(user_id, created_at DESC)` | Sort user's tasks by creation date |

### Example Rows

```json
[
  {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread, cheese",
    "completed": false,
    "created_at": "2026-02-09T10:30:00+00:00",
    "updated_at": "2026-02-09T10:30:00+00:00"
  },
  {
    "id": "660e8400-e29b-41d4-a716-446655440002",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Complete project proposal",
    "description": "Add chapter 3, review figures, get approval",
    "completed": true,
    "created_at": "2026-02-08T14:00:00+00:00",
    "updated_at": "2026-02-09T09:15:00+00:00"
  }
]
```

---

## Data Isolation & Security

### User Ownership Enforcement

**Principle**: Every task operation must verify the authenticated user owns the task

**Implementation Pattern**:
1. Extract `user_id` from JWT token claims (user_id = `sub` claim)
2. Get resource being accessed (e.g., task record from database)
3. Compare: `token.user_id == resource.user_id`
4. If match: proceed, if mismatch: return 403 Forbidden

**Applied to All Task Operations**:

| Operation | Ownership Check |
|-----------|-----------------|
| GET /users/{user_id}/tasks | `token.user_id == path.user_id` |
| POST /users/{user_id}/tasks | `token.user_id == path.user_id` AND set task.user_id = token.user_id |
| GET /users/{user_id}/tasks/{task_id} | `token.user_id == path.user_id` AND `task.user_id == path.user_id` |
| PUT /users/{user_id}/tasks/{task_id} | `token.user_id == path.user_id` AND `task.user_id == path.user_id` |
| DELETE /users/{user_id}/tasks/{task_id} | `token.user_id == path.user_id` AND `task.user_id == path.user_id` |

### Cross-User Access Prevention

**Scenarios**:
1. User A tries to view User B's task → Check fails → 403 Forbidden
2. User A tries to modify User B's task → Check fails → 403 Forbidden
3. User A tries to delete User B's task → Check fails → 403 Forbidden
4. User A lists tasks → SQL query includes WHERE user_id = A → Only A's tasks returned

**Query Pattern** (database level):
```sql
SELECT * FROM tasks
WHERE user_id = $1 AND id = $2
```
Where `$1` = token.user_id (from JWT), `$2` = task_id (from URL)

If token.user_id doesn't own task_id, query returns 0 rows → 404 or 403

---

## Schema Evolution

**Current State** (2026-02-09):
- Users table with email/password
- Tasks table with user_id foreign key
- No schema migrations needed for Phase II

**Future Considerations** (not in scope):
- Password reset tokens (requires token_type field)
- Email verification (requires verified_at field)
- Session tokens (requires sessions table - violates stateless constraint)
- Role-based access control (requires roles/permissions tables)

---

## Validation Rules Summary

### At Signup
```
email:    Must be unique, valid format, not empty
password: Min 8 chars, uppercase, lowercase, digit
name:     Optional, max 255 chars
```

### At Login
```
email:    Must exist, case-insensitive match
password: Must match bcrypt hash (constant-time comparison)
```

### At Task Creation
```
user_id:  Auto-set from token, verified user exists
title:    Required, max 500 chars, not empty
description: Optional, max 5000 chars
completed: Default false, must be boolean
```

### At Task Update
```
user_id:  Immutable (same as created)
title:    Max 500 chars, not empty if provided
description: Max 5000 chars if provided
completed: Must be boolean if provided
updated_at: Auto-updated to current time
```

---

**Status**: ✅ Ready for implementation
