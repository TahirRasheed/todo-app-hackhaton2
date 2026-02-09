# Quick Start Guide: Phase II Todo Full-Stack Web Application

**Date**: 2026-02-09 | **Plan**: [plan.md](./plan.md) | **Contracts**: [contracts/](./contracts/)

## Prerequisites

- Python 3.10+ (backend)
- Node.js 18+ (frontend)
- Neon PostgreSQL account and database created
- Git configured locally

## Environment Setup

### 1. Create `.env` file (repository root)

```bash
# Neon PostgreSQL connection
DATABASE_URL=postgresql://user:password@project.neon.tech/database_name

# JWT Secret (use a strong random string, min 32 chars)
JWT_SECRET=your-super-secret-key-min-32-characters-long

# Better Auth Configuration
BETTER_AUTH_SECRET=another-secret-key-min-32-characters

# API Configuration
API_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000

# Environment
NODE_ENV=development
ENVIRONMENT=development
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create Python virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start FastAPI server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
# or
pnpm install

# Create .env.local for frontend (copy from root .env)
cp ../.env .env.local

# Start Next.js dev server
npm run dev
# or
pnpm dev
```

**Expected output**:
```
> ready started server on 0.0.0.0:3000, url: http://localhost:3000
```

## First Run: Complete User Flow

### 1. Open Application

Navigate to: http://localhost:3000

You should see the signin page.

### 2. Create Account

1. Click "Sign Up" link
2. Enter email: `test@example.com`
3. Enter password: `TestPassword123` (min 8 chars)
4. Enter name: `Test User` (optional)
5. Click "Sign Up"

**Expected result**:
- Account created in database
- JWT token issued and stored in httpOnly cookie
- Redirected to dashboard (empty task list)

### 3. Create First Task

1. Click "Add Task" button
2. Enter title: `Buy groceries`
3. Enter description (optional): `Milk, eggs, bread`
4. Click "Create Task"

**Expected result**:
- Task appears at top of list
- `POST /api/v1/users/{user_id}/tasks` called with JWT
- Backend verifies user ownership
- Task stored in database

### 4. Mark Task Complete

1. Click checkbox next to "Buy groceries"
2. Task should show visual indicator (strikethrough or different color)

**Expected result**:
- `PUT /api/v1/users/{user_id}/tasks/{task_id}` called with `{ "completed": true }`
- Task marked complete in database
- `updated_at` timestamp updated

### 5. Edit Task

1. Click edit icon on task
2. Change title to `Buy groceries and coffee`
3. Click "Save"

**Expected result**:
- `PUT /api/v1/users/{user_id}/tasks/{task_id}` called with updated title
- Task list updated with new title

### 6. Delete Task

1. Click delete icon on task
2. Confirm deletion in dialog
3. Task removed from list

**Expected result**:
- `DELETE /api/v1/users/{user_id}/tasks/{task_id}` called with JWT
- Backend verifies ownership
- Task deleted from database

### 7. Sign Out

1. Click "Sign Out" button
2. Should be redirected to signin page

**Expected result**:
- JWT cookie cleared
- Session terminated
- Cannot access dashboard without logging back in

## Testing with curl (Backend Only)

### 1. Signup

```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "password": "AlicePassword123",
    "name": "Alice Smith"
  }' \
  -v
```

**Response**:
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "alice@example.com",
    "name": "Alice Smith",
    "created_at": "2026-02-09T10:30:45Z"
  },
  "meta": { "timestamp": "...", "request_id": "..." },
  "error": null
}
```

**Note**: Capture the JWT from the `Set-Cookie` header or response payload.

### 2. Create Task (with JWT)

```bash
curl -X POST http://localhost:8000/api/v1/users/550e8400-e29b-41d4-a716-446655440000/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -d '{
    "title": "Learn FastAPI",
    "description": "Complete the FastAPI tutorial"
  }' \
  -v
```

**Response**: 201 Created with task details

### 3. List Tasks (with JWT)

```bash
curl -X GET http://localhost:8000/api/v1/users/550e8400-e29b-41d4-a716-446655440000/tasks \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -v
```

**Response**: 200 OK with task array

### 4. Invalid Token (should fail)

```bash
curl -X GET http://localhost:8000/api/v1/users/550e8400-e29b-41d4-a716-446655440000/tasks \
  -H "Authorization: Bearer invalid-token" \
  -v
```

**Response**: 401 Unauthorized

### 5. Cross-User Access (should fail)

```bash
# Try to access another user's tasks (user_id mismatch)
curl -X GET http://localhost:8000/api/v1/users/different-user-id/tasks \
  -H "Authorization: Bearer <ALICE_JWT>" \
  -v
```

**Response**: 403 Forbidden

## Troubleshooting

### Backend Issues

**Error: "Cannot connect to database"**
- Check DATABASE_URL in `.env`
- Verify Neon credentials and IP whitelist
- Ensure database exists in Neon

**Error: "Table 'users' does not exist"**
- Run migrations: `alembic upgrade head`
- Check migration files in `backend/src/db/migrations/`

**Error: "JWT secret not configured"**
- Ensure JWT_SECRET is set in `.env`
- Restart uvicorn server

**Error: "CORS error in frontend"**
- Check FRONTEND_URL in backend `.env`
- Verify CORS middleware in FastAPI (should allow localhost:3000)

### Frontend Issues

**Error: "Cannot read property 'tasks' of undefined"**
- Ensure backend is running on port 8000
- Check API_URL in `.env.local`
- Verify JWT is being sent in Authorization header

**Error: "Unexpected token < in JSON"**
- Backend returned HTML (500 error page)
- Check backend logs for unhandled exception
- Verify all required environment variables are set

**Error: "Session expired"**
- JWT token has expired (valid for 15 minutes)
- Clear cookies and sign in again
- Check token expiration in JWT payload

### Database Issues

**Error: "Unique violation: duplicate key value"**
- Email already exists in database
- Use different email for testing

**Error: "Foreign key violation"**
- user_id doesn't exist in users table
- Ensure user account was created successfully

## Success Criteria Verification

- [ ] Can create account with email/password
- [ ] Can sign in and receive JWT token
- [ ] Can create task and it appears in list
- [ ] Can mark task complete (visual feedback)
- [ ] Can edit task title/description
- [ ] Can delete task (with confirmation)
- [ ] Can sign out and session is cleared
- [ ] Cannot access tasks without JWT (401)
- [ ] Cannot access another user's tasks (403)
- [ ] UI is responsive on mobile (mobile viewport)
- [ ] All API responses follow standard JSON schema
- [ ] Errors return appropriate HTTP status codes

## Next Steps

1. **Run /sp.tasks** to generate dependency-ordered implementation tasks
2. **Execute via Claude Code agents**:
   - `fastapi-backend-api` for API endpoints
   - `frontend-skill` for UI components
   - `auth-secure-handler` for authentication flows
   - `neon-db-ops` for database schema
3. **Integration testing**: Verify multi-user isolation
4. **Responsive design**: Test on desktop and mobile viewports
5. **Deployment**: Set up CI/CD and production environment

---

**Status**: ✅ READY FOR IMPLEMENTATION
**Next Document**: `/sp.tasks` output (tasks.md)
