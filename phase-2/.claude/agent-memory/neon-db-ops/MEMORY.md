# Neon DB Operations - Agent Memory

## Project: Phase II Todo Full-Stack Web Application

### Database Architecture
- **Database**: Neon Serverless PostgreSQL
- **ORM**: SQLModel (built on SQLAlchemy 2.0)
- **Migration**: No formal migration system yet (using SQLModel.metadata.create_all)
- **Connection**: Async PostgreSQL driver (psycopg3)

### Schema Design Patterns

#### User Model
- `id` (UUID primary key)
- `email` (unique, indexed)
- `password_hash` (bcrypt)
- Relationship: one-to-many with tasks

#### Task Model
- `id` (UUID primary key)
- `user_id` (foreign key → users.id)
- Composite index: `(user_id, created_at)` for efficient list queries
- Timestamps: `created_at` (indexed), `updated_at`

### Ownership Enforcement Strategy

#### Multi-Layer Defense
1. **JWT Middleware**: Validates token, extracts user_id
2. **URL-Level Check**: Verifies user_id in URL matches current_user.id
3. **Database Filtering**: All queries WHERE user_id = ?
4. **Ownership Verification**: Service layer checks task.user_id == user_id

#### Security Best Practices
- Return 403 (not 404) for unauthorized access to prevent task enumeration
- Generic error messages: "Not authorized to access this resource"
- Same error for "not found" and "not owned" scenarios
- user_id immutable after task creation (not in update schema)

### Query Optimization Patterns

#### Composite Index for List Queries
```sql
CREATE INDEX ix_tasks_user_id_created_at ON tasks (user_id, created_at);
```
- Covers filtering (WHERE user_id = ?) + sorting (ORDER BY created_at DESC)
- Single index for common list/pagination queries

#### Efficient COUNT Queries
```python
# Use SQL COUNT, not Python len()
from sqlalchemy import func
result = await session.execute(
    select(func.count(Task.id)).where(Task.user_id == user_id)
)
return result.scalar_one()
```

#### Pagination Pattern
```python
result = await session.execute(
    select(Task)
    .where(Task.user_id == user_id)
    .order_by(desc(Task.created_at))
    .offset(skip)
    .limit(limit)
)
```

### Common Issues & Solutions

#### Issue: N+1 Query Problem
**Solution**: Use composite indexes and avoid loading relationships unnecessarily

#### Issue: Information Leakage via 404 Errors
**Solution**: Return 403 for both "not found" and "not owned" with generic message

#### Issue: Inefficient Count Queries
**Solution**: Use SQL COUNT instead of loading all records and counting in Python

### Testing Patterns

#### Test Database
- In-memory SQLite for fast tests (`sqlite+aiosqlite:///:memory:`)
- Tables created/dropped per test session
- Session rollback after each test

#### Test Fixtures
- `engine`: Async SQLAlchemy engine
- `session`: Database session with rollback
- `async_client`: HTTP client with dependency override

#### Integration Test Coverage
- Cross-user isolation (5+ scenarios)
- Ownership enforcement (7+ scenarios)
- Generic 403 error validation
- Pagination scoped to user

### Database Configuration

#### Connection String Format
```
postgresql+psycopg://user:pass@host/dbname?sslmode=require
```

#### Async Session Factory
```python
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
```

### Files Modified/Created
- `backend/src/models/task.py`: Added composite index
- `backend/src/services/task_service.py`: Optimized COUNT query
- `backend/src/api/v1/tasks.py`: Updated error handling (403 instead of 404)
- `backend/tests/integration/test_auth_flow.py`: Added TestOwnershipEnforcement class
- `backend/docs/OWNERSHIP_ENFORCEMENT.md`: Comprehensive documentation

### Next Steps & Recommendations
1. Consider implementing Alembic migrations for production
2. Add query performance monitoring (log slow queries)
3. Implement rate limiting for 403 errors (brute-force prevention)
4. Consider PostgreSQL Row-Level Security (RLS) for defense-in-depth
5. Add audit logging for unauthorized access attempts
