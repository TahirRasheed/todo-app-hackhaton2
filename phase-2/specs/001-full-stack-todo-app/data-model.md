# Data Model: Phase II Todo Full-Stack Web Application

**Date**: 2026-02-09 | **Plan**: [plan.md](./plan.md)

## Entity Relationship Diagram

```
┌─────────────────────┐
│       User          │
├─────────────────────┤
│ id (UUID, PK)       │
│ email (string,UNQ)  │◄──┐
│ name (string)       │   │ owns (1:N)
│ password_hash (str) │   │
│ created_at (ts)     │   │
└─────────────────────┘   │
                          │
                    ┌─────────────────────┐
                    │       Task          │
                    ├─────────────────────┤
                    │ id (UUID, PK)       │
                    │ user_id (UUID, FK)──┘
                    │ title (string)      │
                    │ description (text)  │
                    │ completed (bool)    │
                    │ created_at (ts)     │
                    │ updated_at (ts)     │
                    └─────────────────────┘
```

## User Entity

### Table Definition

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) NOT NULL UNIQUE,
  name VARCHAR(255),
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
```

### Attributes

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| **id** | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique identifier, generated on creation |
| **email** | VARCHAR(255) | NOT NULL, UNIQUE | User login identifier; must be unique across all users |
| **name** | VARCHAR(255) | Optional | User display name; can be null initially |
| **password_hash** | VARCHAR(255) | NOT NULL | bcrypt hash (cost 12); never store plaintext passwords |
| **created_at** | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Account creation timestamp (UTC) |

### Relationships

- **User → Task**: One-to-Many (one user owns many tasks)
- Enforced via: Task.user_id FOREIGN KEY users.id ON DELETE CASCADE

### Validation Rules

- **email**: Must match regex `/^[^\s@]+@[^\s@]+\.[^\s@]+$/` (basic email validation)
- **email**: Must be unique (database constraint + application check)
- **password**: Minimum 8 characters (enforced on signup/update)
- **password_hash**: Must be valid bcrypt hash (verified on creation)
- **name**: Optional; if provided, max 255 characters

### State Transitions

```
NOT_EXISTS
    ↓ (signup with valid email/password)
CREATED
    ↓ (never deleted in this spec)
ACTIVE
```

Users are never soft-deleted (not in Phase II scope); accounts are permanent once created.

### Sample Record

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "alice@example.com",
  "name": "Alice Smith",
  "password_hash": "$2b$12$...", // bcrypt hash
  "created_at": "2026-02-09T10:15:30Z"
}
```

## Task Entity

### Table Definition

```sql
CREATE TABLE tasks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title VARCHAR(500) NOT NULL,
  description TEXT,
  completed BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_user_created ON tasks(user_id, created_at DESC);
```

### Attributes

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| **id** | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique task identifier |
| **user_id** | UUID | NOT NULL, FOREIGN KEY users.id | Owner of this task; enforces data isolation |
| **title** | VARCHAR(500) | NOT NULL | Task name; max 500 characters |
| **description** | TEXT | Optional | Extended task details; max 5000 characters |
| **completed** | BOOLEAN | DEFAULT FALSE | Completion status; true = task done |
| **created_at** | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Task creation timestamp (UTC) |
| **updated_at** | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last modification timestamp (UTC) |

### Relationships

- **Task → User**: Many-to-One (many tasks belong to one user)
- **Cascade delete**: If user is deleted, all their tasks are deleted automatically
- **No task can exist without a user** (enforced by NOT NULL + FK constraint)

### Indexes

| Index Name | Columns | Purpose |
|------------|---------|---------|
| **PRIMARY** | id | Fast lookup by task ID |
| **idx_tasks_user_id** | user_id | Fast filtering by user (WHERE user_id = $1) |
| **idx_tasks_user_created** | (user_id, created_at DESC) | Optimizes "fetch all user tasks ordered by creation" query |

The composite index covers both the WHERE and ORDER BY clauses in the most common query:
```sql
SELECT * FROM tasks WHERE user_id = $1 ORDER BY created_at DESC LIMIT $2 OFFSET $3;
```
Execution without index: O(n log n) = slow for 10k+ tasks
Execution with index: O(log n + k) = fast regardless of scale

### Validation Rules

- **title**: NOT NULL, max 500 characters (enforced at database and application level)
- **title**: Minimum 1 character (enforced at application level; error: "Task title is required")
- **description**: Optional; if provided, max 5000 characters
- **completed**: Boolean (true/false); defaults to false
- **user_id**: Must reference an existing user (FK constraint); cannot be null

### State Transitions

```
NOT_EXISTS
    ↓ (POST /api/v1/users/{user_id}/tasks with valid title)
CREATED (completed = false)
    ↓ (PUT endpoint with completed = true)
COMPLETED (completed = true)
    ↓ (PUT endpoint with completed = false)
CREATED (completed = false)
    ↓ (DELETE endpoint)
DELETED (removed from database)
```

Tasks transition between CREATED and COMPLETED via the completion toggle. Delete is permanent (no soft delete).

### Sample Records

**Task 1 (Created, not completed)**:
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread, coffee",
  "completed": false,
  "created_at": "2026-02-09T10:30:00Z",
  "updated_at": "2026-02-09T10:30:00Z"
}
```

**Task 2 (Completed)**:
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Review PR #42",
  "description": null,
  "completed": true,
  "created_at": "2026-02-09T08:15:00Z",
  "updated_at": "2026-02-09T11:45:00Z"
}
```

## Multi-User Data Isolation

### Database Constraints

1. **Foreign Key Enforcement**: Task.user_id must reference a valid User.id
2. **NOT NULL Constraint**: Task.user_id cannot be null (every task must belong to someone)
3. **ON DELETE CASCADE**: If a user is deleted, their tasks are automatically deleted

### API-Layer Enforcement

Every task operation verifies ownership:

```python
# Example (FastAPI)
@router.get("/api/v1/users/{user_id}/tasks")
async def list_tasks(user_id: str, current_user: User = Depends(get_current_user)):
    # CRUCIAL: Verify current_user.id == user_id parameter
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Filter all tasks by current_user.id
    tasks = await db.query(Task).filter(Task.user_id == current_user.id).all()
    return tasks
```

### Isolation Test Cases

| Scenario | Expected Outcome | Why Critical |
|----------|------------------|-------------|
| User A views User B's tasks via direct URL | 403 Forbidden | Prevents cross-user access |
| User A creates task → User B cannot see it in list | Task invisible to User B | Data ownership respected |
| User A tries to edit User B's task | 403 Forbidden | Prevents unauthorized modification |
| User A deletes task → User B's list unaffected | User B's tasks unchanged | Isolation at delete operation |
| Token for User A used to access User B's endpoint | 403 Forbidden | JWT user_id doesn't match URL |

## Migration Strategy

### Alembic Migrations

**Initial migration** (`versions/001_initial_schema.py`):
```python
"""Initial schema: users and tasks tables"""

def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Uuid(), primary_key=True, default=sa.func.gen_random_uuid()),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('name', sa.String(255)),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), default=sa.func.now())
    )
    op.create_index('idx_users_email', 'users', ['email'])

    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('id', sa.Uuid(), primary_key=True, default=sa.func.gen_random_uuid()),
        sa.Column('user_id', sa.Uuid(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('completed', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), default=sa.func.now())
    )
    op.create_index('idx_tasks_user_id', 'tasks', ['user_id'])
    op.create_index('idx_tasks_user_created', 'tasks', ['user_id', sa.desc('created_at')])

def downgrade():
    op.drop_table('tasks')
    op.drop_table('users')
```

**Rollback**: Reverting to previous version drops both tables (only acceptable for development; production migrations must preserve data).

## SQLModel Definitions

### User Model

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    name: Optional[str] = None
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    tasks: List["Task"] = Relationship(back_populates="user")
```

### Task Model

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime

class Task(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    title: str = Field(max_length=500, index=False)
    description: Optional[str] = None
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    user: User = Relationship(back_populates="tasks")
```

### Pydantic Schemas (Request/Response)

```python
from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str  # Min 8 chars (validated)
    name: Optional[str] = None

class UserResponse(BaseModel):
    id: UUID
    email: str
    name: Optional[str]
    created_at: datetime

class TaskCreate(BaseModel):
    title: str  # Min 1, Max 500
    description: Optional[str] = None  # Max 5000

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

class TaskResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime
```

## Constraints Summary

| Constraint | Type | Entity | Purpose |
|-----------|------|--------|---------|
| `id` PRIMARY KEY | Database | User, Task | Unique identification |
| `email` UNIQUE | Database | User | Prevent duplicate accounts |
| `email` NOT NULL | Database | User | Required for login |
| `password_hash` NOT NULL | Database | User | Required for authentication |
| `user_id` NOT NULL | Database | Task | Every task must belong to a user |
| `user_id` FOREIGN KEY | Database | Task | Referential integrity; cascade delete |
| `title` NOT NULL | Database | Task | Required task name |
| `title` max 500 chars | Application | Task | Prevent overflow; validated in schema |
| `description` max 5000 chars | Application | Task | Prevent overflow; validated in schema |
| `password` min 8 chars | Application | User | Security requirement |
| `email` format validation | Application | User | Valid email format (regex) |

## Data Consistency Rules

1. **No orphaned tasks**: If a user is deleted, their tasks are deleted (cascade delete)
2. **No duplicate emails**: Database unique constraint + application check
3. **No null user_id**: Every task must belong to a user (NOT NULL + FK)
4. **No invalid passwords**: Minimum 8 chars, bcrypt hashed (no plaintext)
5. **Updated timestamps**: `updated_at` is modified on every PUT request
6. **Created timestamps**: Immutable once set (never updated on modifications)

---

**Status**: ✅ DRAFT (Phase 1 design complete)
**Next**: Generate API contracts (openapi.yaml) and quickstart guide
