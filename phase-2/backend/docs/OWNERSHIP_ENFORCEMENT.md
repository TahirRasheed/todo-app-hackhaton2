# Ownership Enforcement & Data Isolation

## Overview

This document describes the ownership enforcement and data isolation mechanisms implemented in the Todo application to ensure users can only access their own tasks.

## Security Architecture

### Multi-Layer Defense

1. **JWT Authentication Layer** (middleware)
   - Validates JWT token signature and expiration
   - Extracts `user_id` from token claims (`sub`)
   - Injects `current_user` into request context

2. **URL-Level Ownership Check** (endpoint validation)
   - Verifies `user_id` in URL matches `current_user.id`
   - Returns 403 Forbidden if mismatch detected
   - Prevents cross-user access at routing level

3. **Database-Level Filtering** (query constraints)
   - All queries filter by `user_id`
   - Uses `WHERE user_id = ?` in SQL
   - Ensures database-level isolation

4. **Ownership Verification** (service layer)
   - GET/UPDATE/DELETE operations verify task ownership
   - Uses `WHERE task_id = ? AND user_id = ?`
   - Atomic ownership check with data retrieval

## Implementation Details

### 1. Task Endpoints

All 5 task endpoints enforce ownership:

#### GET /api/v1/users/{user_id}/tasks (List Tasks)
```python
# Validation:
if current_user.id != user_id:
    raise HTTPException(403, "Not authorized to access this resource")

# Database query:
SELECT * FROM tasks
WHERE user_id = ?
ORDER BY created_at DESC
LIMIT ? OFFSET ?
```

**Security:**
- Only returns tasks owned by authenticated user
- Pagination scoped to user's tasks
- Total count reflects user's tasks only

#### POST /api/v1/users/{user_id}/tasks (Create Task)
```python
# Validation:
if current_user.id != user_id:
    raise HTTPException(403, "Not authorized to access this resource")

# Database insert:
INSERT INTO tasks (user_id, title, description, completed)
VALUES (?, ?, ?, ?)
```

**Security:**
- User can only create tasks for themselves
- `user_id` set from authenticated user
- Prevents creating tasks for other users

#### GET /api/v1/users/{user_id}/tasks/{task_id} (Get Task)
```python
# Validation:
if current_user.id != user_id:
    raise HTTPException(403, "Not authorized to access this resource")

# Database query:
SELECT * FROM tasks
WHERE id = ? AND user_id = ?
```

**Security:**
- Returns 403 if task not owned (even if exists)
- Returns 403 if task doesn't exist (no info leak)
- Generic error message prevents enumeration

#### PUT /api/v1/users/{user_id}/tasks/{task_id} (Update Task)
```python
# Validation:
if current_user.id != user_id:
    raise HTTPException(403, "Not authorized to access this resource")

# Database query:
SELECT * FROM tasks WHERE id = ? AND user_id = ?
UPDATE tasks SET ... WHERE id = ?
```

**Security:**
- Verifies ownership before update
- Returns 403 if not owned or doesn't exist
- `user_id` immutable (not in update schema)

#### DELETE /api/v1/users/{user_id}/tasks/{task_id} (Delete Task)
```python
# Validation:
if current_user.id != user_id:
    raise HTTPException(403, "Not authorized to access this resource")

# Database query:
SELECT * FROM tasks WHERE id = ? AND user_id = ?
DELETE FROM tasks WHERE id = ?
```

**Security:**
- Verifies ownership before deletion
- Returns 403 if not owned or doesn't exist
- No cascade deletion of other users' data

### 2. Database Optimization

#### Composite Index
```sql
CREATE INDEX ix_tasks_user_id_created_at
ON tasks (user_id, created_at);
```

**Benefits:**
- Optimizes list queries with ORDER BY created_at
- Single index covers filtering + sorting
- Reduces query time for paginated lists

#### Efficient Count Query
```python
# Before (inefficient):
result = await session.execute(select(Task).where(Task.user_id == user_id))
return len(result.scalars().all())  # Loads all records

# After (efficient):
from sqlalchemy import func
result = await session.execute(
    select(func.count(Task.id)).where(Task.user_id == user_id)
)
return result.scalar_one()  # Database COUNT
```

**Benefits:**
- Database-side aggregation
- No memory overhead for large task lists
- Faster pagination metadata

### 3. Security Against Information Disclosure

#### Problem: 404 vs 403 Leaks Task Existence
If GET/UPDATE/DELETE return:
- 404 → Task doesn't exist (reveals task_id is invalid)
- 403 → Task exists but not owned (reveals task_id is valid)

Attacker can enumerate valid task IDs.

#### Solution: Generic 403 for All Ownership Failures
```python
try:
    task = await TaskService.get_task(session, task_id, user_id)
except ValueError:
    # Return 403 for both "not found" and "not owned"
    raise HTTPException(403, "Not authorized to access this resource")
```

**Benefits:**
- Same error for "not found" and "not owned"
- Prevents task enumeration attacks
- Generic error message ("Not authorized...")

### 4. Data Model Constraints

#### Foreign Key Constraint
```python
user_id: UUID = Field(
    foreign_key="users.id",
    description="Owner of this task"
)
```

**Benefits:**
- Referential integrity enforced
- Cascade delete options (if needed)
- Database-level constraint

#### User-Task Relationship
```python
# User model
tasks: List["Task"] = Relationship(back_populates="user")

# Task model
user: Optional["User"] = Relationship(back_populates="tasks")
```

**Benefits:**
- ORM-level relationship
- Prevents N+1 query problems (eager loading)
- Type-safe access

## Test Coverage

### Integration Tests (test_isolation.py)
- ✅ Users see only own tasks
- ✅ Cross-user list returns empty
- ✅ User cannot GET other's task (403)
- ✅ User cannot CREATE for other (403)
- ✅ Task lists are independent

### Ownership Tests (test_auth_flow.py)
- ✅ User can only see own tasks (pagination)
- ✅ User cannot view other's task (403)
- ✅ User cannot update other's task (403)
- ✅ User cannot delete other's task (403)
- ✅ Generic 403 prevents info leak
- ✅ Pagination limits to user tasks
- ✅ Task user_id is immutable

## Security Checklist

### ✅ Authorization
- [x] All endpoints require valid JWT token
- [x] JWT middleware validates signature and expiration
- [x] User can only access own resources

### ✅ Data Isolation
- [x] Database queries filter by user_id
- [x] List endpoint pagination scoped to user
- [x] Cross-user access blocked (403)

### ✅ Error Handling
- [x] Generic 403 error messages
- [x] No information leakage about task existence
- [x] Consistent error responses

### ✅ Database Performance
- [x] Composite index on (user_id, created_at)
- [x] Efficient SQL COUNT for pagination
- [x] No N+1 query problems

### ✅ Input Validation
- [x] user_id in URL matches authenticated user
- [x] task_id validated before database access
- [x] user_id immutable after creation

## Attack Scenarios & Mitigations

### Scenario 1: User A tries to access User B's task
**Attack:** User A provides valid JWT but tries GET /users/{user_b_id}/tasks/{task_id}

**Mitigation:**
1. JWT middleware validates User A's token → current_user = User A
2. Endpoint checks: `user_b_id != current_user.id` → 403 Forbidden
3. Database query never executed

**Result:** ✅ Blocked at URL-level check

### Scenario 2: User A tries to enumerate task IDs
**Attack:** User A tries GET /users/{user_b_id}/tasks/{random_task_id} repeatedly

**Mitigation:**
1. URL-level check: `user_b_id != current_user.id` → 403
2. Same error message for all attempts
3. No distinction between "not found" and "not owned"

**Result:** ✅ Generic 403 prevents enumeration

### Scenario 3: User A tries to create task for User B
**Attack:** User A POST /users/{user_b_id}/tasks with valid JWT

**Mitigation:**
1. URL-level check: `user_b_id != current_user.id` → 403
2. Task creation blocked before database access

**Result:** ✅ Blocked at validation layer

### Scenario 4: User A tries to modify User B's task
**Attack:** User A PUT /users/{user_b_id}/tasks/{task_id} with valid JWT

**Mitigation:**
1. URL-level check: `user_b_id != current_user.id` → 403
2. Update blocked before database access

**Result:** ✅ Blocked at validation layer

### Scenario 5: SQL injection to bypass user_id filter
**Attack:** User A tries to inject SQL in task_id parameter

**Mitigation:**
1. SQLAlchemy parameterized queries (no string interpolation)
2. UUID type validation (invalid UUIDs rejected)
3. ORM escapes all inputs

**Result:** ✅ Parameterized queries prevent injection

## Performance Considerations

### Query Optimization
- Composite index reduces query time from O(n log n) to O(log n)
- Database COUNT avoids loading all records into memory
- Pagination LIMIT/OFFSET efficient with index

### Connection Pooling
- Async SQLAlchemy sessions reuse connections
- Neon serverless pooling reduces cold starts
- No connection exhaustion with proper session management

### N+1 Query Prevention
- Relationships configured with `back_populates`
- Eager loading available via `selectinload`
- Single query for list operations

## Monitoring & Alerts

### Recommended Metrics
1. **403 Error Rate:** Spike indicates unauthorized access attempts
2. **Query Latency:** Slow list queries may indicate missing index
3. **Cross-User Attempts:** Log and alert on 403 errors

### Query Analysis
```sql
-- Verify index usage
EXPLAIN ANALYZE
SELECT * FROM tasks
WHERE user_id = 'some-uuid'
ORDER BY created_at DESC
LIMIT 20;

-- Should show: Index Scan using ix_tasks_user_id_created_at
```

## Future Enhancements

### Potential Improvements
1. **Rate Limiting:** Prevent brute-force task enumeration
2. **Audit Logging:** Track all ownership violation attempts
3. **Resource Quotas:** Limit tasks per user
4. **Soft Deletes:** Add `deleted_at` for recovery
5. **Row-Level Security:** PostgreSQL RLS for defense-in-depth

## References

- Task Model: `backend/src/models/task.py`
- Task Endpoints: `backend/src/api/v1/tasks.py`
- Task Service: `backend/src/services/task_service.py`
- Isolation Tests: `backend/tests/integration/test_isolation.py`
- Ownership Tests: `backend/tests/integration/test_auth_flow.py`
