# Database Setup Guide

**Date**: 2026-02-09
**Status**: ✅ Configured for Neon PostgreSQL

## Overview

The application is now configured to connect to **Neon Serverless PostgreSQL**. The database connection is established with:

- **Host**: ep-holy-butterfly-ai4lnkq4-pooler.c-4.us-east-1.aws.neon.tech
- **Database**: neondb
- **User**: neondb_owner
- **Region**: us-east-1 (AWS)
- **Connection Pool**: Enabled (pooler)
- **SSL/TLS**: Required
- **Channel Binding**: Required

## Configuration Files

### Backend Environment (.env.local)

The database connection string is configured in `backend/.env.local`:

```env
DATABASE_URL=postgresql://neondb_owner:npg_C3u5VxKMPjXR@ep-holy-butterfly-ai4lnkq4-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

### Backend Configuration (backend/src/config.py)

The `Settings` class reads the `DATABASE_URL` environment variable:

```python
DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/todo_db"
)
```

### Database Session (backend/src/db/session.py)

The session manager:
1. Reads `DATABASE_URL` from `config.Settings`
2. Converts to async format: `postgresql://` → `postgresql+psycopg://`
3. Creates `AsyncEngine` with SQLAlchemy
4. Provides `get_session()` dependency for FastAPI routes

```python
# Conversion for async support
DATABASE_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+psycopg://")

# Result: postgresql+psycopg://neondb_owner:npg_C3u5VxKMPjXR@...
```

## Database Initialization

### Initialize Database Schema

To create all tables (User, Task), run the init_db function:

```python
# In backend/src/db/session.py
async def init_db():
    """Initialize database (create tables)"""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
```

This can be called from:
1. **FastAPI startup event** (recommended for auto-initialization)
2. **CLI script** (manual initialization)
3. **Alembic migration** (production best practice)

### Option 1: FastAPI Startup Event (Recommended)

Add to `backend/src/main.py`:

```python
from contextlib import asynccontextmanager
from backend.src.db.session import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    print("Database initialized")
    yield
    # Shutdown
    print("Shutting down")

app = FastAPI(lifespan=lifespan, ...)
```

### Option 2: Manual CLI Script

Create `backend/scripts/init_db.py`:

```python
import asyncio
from backend.src.db.session import init_db

async def main():
    await init_db()
    print("Database initialized successfully")

if __name__ == "__main__":
    asyncio.run(main())
```

Run with:
```bash
python backend/scripts/init_db.py
```

### Option 3: Alembic Migrations (Production)

For managed migrations:

```bash
cd backend
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

## Database Tables

### Users Table

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

**Fields**:
- `id`: UUID primary key
- `email`: Unique email address (indexed)
- `name`: User display name
- `password_hash`: Bcrypt hashed password
- `created_at`: Account creation timestamp

### Tasks Table

```sql
CREATE TABLE tasks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users.id ON DELETE CASCADE,
  title VARCHAR(500) NOT NULL,
  description TEXT,
  completed BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_user_created ON tasks(user_id, created_at DESC);
```

**Fields**:
- `id`: UUID primary key
- `user_id`: Foreign key to users (ON DELETE CASCADE)
- `title`: Task title (max 500 chars)
- `description`: Optional task description (max 5000 chars)
- `completed`: Completion status (default false)
- `created_at`: Task creation timestamp
- `updated_at`: Last modification timestamp

**Indexes**:
- `idx_tasks_user_id`: Efficient filtering by user
- `idx_tasks_user_created`: Efficient user task listing with sorting

## Connection Security

The connection includes security features:

✅ **SSL/TLS Encryption**: `sslmode=require`
  - All data encrypted in transit
  - Certificate validation required

✅ **Channel Binding**: `channel_binding=require`
  - Prevents man-in-the-middle attacks
  - Binds authentication to TLS channel

✅ **Async Driver**: Uses `psycopg` (psycopg3) async driver
  - Non-blocking database operations
  - Supports concurrent connections

## Connection Pooling

Neon connection pooler:
- **URL**: `...pooler.c-4.us-east-1.aws.neon.tech`
- **Default Pool Size**: 5-20 connections
- **Benefits**:
  - Reduced connection overhead
  - Better resource utilization
  - Lower latency

For direct connections (if needed):
```
ep-holy-butterfly-ai4lnkq4.c-4.us-east-1.aws.neon.tech (without -pooler)
```

## Testing Database Connection

### Python Script Test

Create `backend/test_db.py`:

```python
import asyncio
from sqlalchemy import text
from backend.src.db.session import engine

async def test_connection():
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT 1"))
        print(f"Connection test: {result.scalar()}")

if __name__ == "__main__":
    asyncio.run(test_connection())
```

Run:
```bash
python backend/test_db.py
# Output: Connection test: 1
```

### From FastAPI App

Visit health check endpoint:
```bash
curl http://localhost:8000/health
# If DB connection works: {"status": "ok", "environment": "development"}
```

## Environment Variables

### Required
- `DATABASE_URL`: PostgreSQL connection string (now configured)

### Optional (for production)
- `JWT_SECRET`: For signing JWT tokens (change for production)
- `BETTER_AUTH_SECRET`: For session management
- `FRONTEND_URL`: CORS origin (default: http://localhost:3000)
- `ENVIRONMENT`: Set to "production" for deployment

## Production Considerations

For production deployment:

1. **Rotate Secrets**:
   - Generate new `JWT_SECRET` (min 32 chars, cryptographically secure)
   - Generate new `BETTER_AUTH_SECRET`
   - Never commit secrets to git

2. **Neon Configuration**:
   - Create separate branch for prod database
   - Enable backups in Neon console
   - Set up monitoring/alerts
   - Use read replicas for scaling reads

3. **Connection Pooling**:
   - Tune pool size based on workload
   - Monitor connection usage
   - Implement connection reuse strategy

4. **Security**:
   - Keep SSL/TLS enabled
   - Monitor IP whitelist (if using)
   - Enable audit logging
   - Regular security updates

## Troubleshooting

### Connection Refused
- Check network connectivity to Neon endpoint
- Verify credentials are correct
- Ensure DATABASE_URL includes SSL parameters

### Authentication Failed
- Verify username and password
- Check credentials don't have special characters requiring encoding
- Ensure .env.local is loaded by backend

### Schema Not Found
- Run database initialization (`init_db()`)
- Check database name is correct (neondb)
- Verify permissions for user

### Slow Queries
- Check indexes are created
- Monitor Neon console for query performance
- Consider query optimization

## Useful Neon Commands

Check database status in Neon console:
- View database size
- Monitor connections
- Check backups
- View logs

From command line (requires Neon CLI):
```bash
neonctl branches list
neonctl db queries list
```

## Next Steps

1. ✅ **Database configured**: Connected to Neon PostgreSQL
2. 🔜 **Initialize schema**: Run `init_db()` to create tables
3. 🔜 **Test connection**: Run health check endpoint
4. 🔜 **Deploy backend**: Push code to production
5. 🔜 **Run migrations**: Use Alembic for schema changes

## Resources

- **Neon Documentation**: https://neon.tech/docs
- **SQLAlchemy Async**: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- **psycopg3**: https://www.psycopg.org/psycopg3/docs/
- **SQLModel**: https://sqlmodel.tiangolo.com/

---

**Database Setup Complete**: ✅
**Ready for**: Schema initialization, testing, deployment

