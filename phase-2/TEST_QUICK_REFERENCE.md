# Testing Quick Reference

## Application Status

✅ **All 5 Phases Complete**
- Phase 1: Project Setup
- Phase 2: Database & Infrastructure (Neon PostgreSQL configured)
- Phase 3: User Authentication (Signup/Signin/Signout)
- Phase 4: Task CRUD (Create, Read, Update, Delete)
- Phase 5: Task Features (Complete toggle, Edit, Delete with confirmation)

---

## 5-Minute Quick Test

### Terminal 1: Start Backend

```bash
cd backend
pip install -e .
python -m uvicorn src.main:app --reload
```

**Wait for**: `✅ Database schema initialized successfully`

### Terminal 2: Start Frontend

```bash
cd frontend
npm install
npm run dev
```

**Wait for**: `✓ Ready in X.Xs`

### Browser: Open Application

**URL**: http://localhost:3000

---

## One-Command API Test (after backend starts)

```bash
# 1. Sign up
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!",
    "name": "Test"
  }' | jq -r '.access_token')

USER_ID=$(curl -s -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test2@example.com",
    "password": "Test123!",
    "name": "Test2"
  }' | jq -r '.data.id')

# 2. Create task
curl -s -X POST http://localhost:8000/api/v1/users/$USER_ID/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Task", "description": "API Test"}' | jq .

# 3. Get tasks
curl -s http://localhost:8000/api/v1/users/$USER_ID/tasks \
  -H "Authorization: Bearer $TOKEN" | jq .
```

---

## Test Scenarios

### Authentication ✅
- [x] Sign up with valid credentials
- [x] Sign in returns JWT token
- [x] Invalid password returns 401
- [x] Missing auth header returns 401

### Tasks ✅
- [x] Create task with title + description
- [x] List tasks with pagination (20 per page)
- [x] Get single task by ID
- [x] Update task (complete toggle, edit)
- [x] Delete task with 204 No Content
- [x] Deleted task returns 404

### Security ✅
- [x] User A cannot access User B's tasks (403)
- [x] Invalid JWT rejected
- [x] Token validation on protected routes
- [x] CORS headers for frontend origin

### UI ✅
- [x] Sign up form with validation
- [x] Sign in form with validation
- [x] Dashboard after authentication
- [x] Add task form with character count
- [x] Task list with strikethrough on complete
- [x] Edit and delete task with confirmation
- [x] Pagination controls for 20+ tasks
- [x] Sign out clears session

---

## Expected Response Examples

### Sign Up Success (201)
```json
{
  "data": {"id": "uuid", "email": "test@example.com", "name": "Test"},
  "access_token": "eyJ...",
  "error": null
}
```

### Sign In Success (200)
```json
{
  "data": {"id": "uuid", "email": "test@example.com"},
  "access_token": "eyJ...",
  "error": null
}
```

### Create Task Success (201)
```json
{
  "data": {
    "id": "uuid",
    "user_id": "uuid",
    "title": "Test",
    "description": "Description",
    "completed": false,
    "created_at": "2026-02-09T12:00:00Z"
  }
}
```

### List Tasks Success (200)
```json
{
  "data": [{"id": "uuid", "title": "Task 1", ...}],
  "meta": {"total": 5, "skip": 0, "limit": 20}
}
```

### Unauthorized (401)
```json
{
  "data": null,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid token"
  }
}
```

### Forbidden (403)
```json
{
  "data": null,
  "error": {
    "code": "FORBIDDEN",
    "message": "Access denied"
  }
}
```

---

## Endpoints Reference

### Auth
- `POST /api/v1/auth/signup` - Create account
- `POST /api/v1/auth/signin` - Login
- `POST /api/v1/auth/signout` - Logout

### Tasks
- `POST /api/v1/users/{user_id}/tasks` - Create task
- `GET /api/v1/users/{user_id}/tasks?skip=0&limit=20` - List tasks
- `GET /api/v1/users/{user_id}/tasks/{task_id}` - Get task
- `PUT /api/v1/users/{user_id}/tasks/{task_id}` - Update task
- `DELETE /api/v1/users/{user_id}/tasks/{task_id}` - Delete task

### Health
- `GET /health` - Server health check
- `GET /docs` - Swagger UI
- `GET /redoc` - ReDoc documentation

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Backend won't start | Check Python 3.10+: `python --version` |
| Database connection error | Verify .env.local has DATABASE_URL |
| Frontend won't start | Clear cache: `rm -rf .next node_modules` |
| Port already in use | Use different port: `--port 8001` or `-p 3001` |
| Token not working | Verify it has 3 parts separated by dots |
| CORS error | Ensure FRONTEND_URL=http://localhost:3000 in .env |

---

## Files You Need to Run

✅ **Backend** (`backend/`)
- pyproject.toml - Dependencies
- src/main.py - FastAPI app
- src/config.py - Configuration
- src/db/session.py - Database
- .env.local - Environment variables

✅ **Frontend** (`frontend/`)
- package.json - Dependencies
- src/app/ - Pages and layouts
- src/components/ - React components
- next.config.js - Next.js config

✅ **Config** (Root)
- .env.local - Neon connection, JWT secrets

---

## Success Indicators

✅ Backend starts without errors
✅ Database initializes automatically
✅ Frontend loads at http://localhost:3000
✅ Can sign up and see dashboard
✅ Can create, complete, edit, delete tasks
✅ Cannot access other users' tasks
✅ Pagination works with 20+ tasks
✅ Sign out clears session

---

## Full Testing Guide

For comprehensive testing with all curl commands and detailed verification steps, see: **TEST_APPLICATION.md**

---

**Status**: Ready to test! Follow instructions above to validate the complete Todo application.
