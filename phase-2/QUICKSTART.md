# Quick Start Guide

**Status**: ✅ Ready to Run
**Date**: 2026-02-09

## Overview

The Todo application is fully implemented (5 phases complete) and configured to use Neon PostgreSQL. This guide will help you get the application running locally.

## Prerequisites

- **Python 3.10+** (for backend)
- **Node.js 18+** (for frontend)
- **PostgreSQL** connection (already configured to Neon)
- **.env.local** configured with Neon database credentials ✅

## Quick Start (5 minutes)

### Step 1: Start Backend (Auto-initializes Database)

```bash
cd backend

# Install dependencies (first time only)
pip install -e .
# or
pip install fastapi uvicorn sqlmodel sqlalchemy psycopg

# Start FastAPI server
python -m uvicorn src.main:app --reload

# Expected output:
# 🚀 Starting Todo API...
# 📊 Environment: development
# 📦 Initializing database schema...
# ✅ Database schema initialized successfully
# Uvicorn running on http://127.0.0.1:8000
```

**What happens automatically**:
- ✅ Database schema created (users, tasks tables)
- ✅ Indexes created for performance
- ✅ Server ready to accept requests

### Step 2: Start Frontend (New Terminal)

```bash
cd frontend

# Install dependencies (first time only)
npm install

# Start Next.js dev server
npm run dev

# Expected output:
# ▲ Next.js 16.x.x
# - Local: http://localhost:3000
# ✓ Ready in 2.5s
```

### Step 3: Access Application

Open browser: **http://localhost:3000**

- **Sign Up**: Click "Create Account" button
- **Sign In**: Use your created credentials
- **Create Task**: Click "Add Task" in dashboard
- **Manage Tasks**: Toggle complete, edit, delete

## Detailed Backend Setup

### Installation

```bash
# Navigate to backend
cd backend

# Create virtual environment (optional but recommended)
python -m venv venv

# Windows: Activate virtual environment
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -e .
```

### Running Backend

```bash
# Development mode (with auto-reload)
python -m uvicorn src.main:app --reload

# Production mode (no reload)
python -m uvicorn src.main:app

# Custom host/port
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### Database Initialization

The database schema is **automatically created** on server startup:

1. Server starts and calls `lifespan(app)` context manager
2. `init_db()` creates all tables (users, tasks)
3. Indexes are created for performance
4. Server ready for requests

**If you need manual initialization**:

Create `manual_init.py` in project root:

```python
import asyncio
import sys
sys.path.insert(0, 'backend')

from backend.src.db.session import init_db, engine

async def main():
    try:
        print("Initializing database...")
        await init_db()
        print("✅ Database initialized!")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await engine.dispose()

asyncio.run(main())
```

Run with:
```bash
python manual_init.py
```

### Backend Endpoints

```bash
# Health check
curl http://localhost:8000/health

# API Docs (interactive)
http://localhost:8000/docs

# Auth endpoints
POST /api/v1/auth/signup
POST /api/v1/auth/signin
POST /api/v1/auth/signout

# Task endpoints
POST /api/v1/users/{user_id}/tasks
GET /api/v1/users/{user_id}/tasks
GET /api/v1/users/{user_id}/tasks/{task_id}
PUT /api/v1/users/{user_id}/tasks/{task_id}
DELETE /api/v1/users/{user_id}/tasks/{task_id}
```

## Detailed Frontend Setup

### Installation

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Install with specific Node version (if needed)
# nvm use 18
# npm install
```

### Running Frontend

```bash
# Development mode (with hot reload)
npm run dev

# Production build
npm run build
npm start

# Lint code
npm run lint

# Type check
npm run type-check
```

### Frontend Routes

```
/                      # Landing page with Sign Up / Sign In links
/auth/signup          # Sign up form
/auth/signin          # Sign in form
/dashboard            # Main dashboard (protected)
/dashboard/page.tsx   # Task management interface
```

## Testing Application

### Manual Testing

1. **Sign Up**:
   ```
   Email: test@example.com
   Password: testpassword123
   Name: Test User
   ```

2. **Sign In**: Use same credentials

3. **Create Task**:
   ```
   Title: My First Task
   Description: This is a test task
   Click "Create Task"
   ```

4. **Task Actions**:
   - ☑️ Toggle completion (strikethrough)
   - ✏️ Edit task (update title/description)
   - 🗑️ Delete task (with confirmation)

### Curl Testing

```bash
# Sign up
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123",
    "name": "Test User"
  }'

# Sign in (get JWT token)
curl -X POST http://localhost:8000/api/v1/auth/signin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123"
  }'

# Create task (replace {user_id} and {jwt_token})
curl -X POST http://localhost:8000/api/v1/users/{user_id}/tasks \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Task",
    "description": "Task description"
  }'

# List tasks
curl -X GET http://localhost:8000/api/v1/users/{user_id}/tasks \
  -H "Authorization: Bearer {jwt_token}"
```

## Troubleshooting

### Backend Issues

**Port 8000 already in use**:
```bash
# Use different port
python -m uvicorn src.main:app --port 8001

# Kill process using port (Windows PowerShell)
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process
```

**Database connection error**:
```
Error: timeout: Server closed the connection
```
- Check .env.local has correct DATABASE_URL
- Verify network connection to Neon
- Check Neon console for connection limits

**Module not found error**:
```bash
# Ensure you're in backend directory
cd backend

# Or install editable package
pip install -e .
```

**Import errors**:
```bash
# Make sure you're using Python 3.10+
python --version

# Reinstall dependencies
pip install --upgrade -e .
```

### Frontend Issues

**Port 3000 already in use**:
```bash
# Use different port
npm run dev -- -p 3001
```

**Module not found**:
```bash
# Clear dependencies and reinstall
rm -r node_modules package-lock.json
npm install
```

**Build fails**:
```bash
# Clear Next.js cache
rm -r .next

# Reinstall dependencies
npm install

# Try build again
npm run build
```

### Database Issues

**Schema not created on startup**:
1. Check backend logs for initialization messages
2. Verify DATABASE_URL in .env.local
3. Try manual initialization script

**Tables don't exist**:
```bash
# Create initialization script and run manually
# See "Manual Initialization" section above
```

## Running Tests

### Backend Integration Tests

```bash
cd backend

# Run all tests
pytest

# Run specific test file
pytest tests/integration/test_auth_flow.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=src
```

### Frontend Tests

```bash
cd frontend

# Run tests
npm test

# Run with watch mode
npm test -- --watch

# Run with coverage
npm test -- --coverage
```

## Environment Variables

### Backend (.env.local)

```env
# Database
DATABASE_URL=postgresql://neondb_owner:npg_C3u5VxKMPjXR@ep-holy-butterfly-ai4lnkq4-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require

# JWT
JWT_SECRET=dev-secret-key-please-change-in-production-min32chars

# Auth
BETTER_AUTH_SECRET=dev-auth-secret-please-change-in-production

# API
API_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000

# Environment
ENVIRONMENT=development
DEBUG=true
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
```

## Production Deployment

### Before Deploying

1. **Generate secure secrets**:
   ```bash
   # Generate new JWT_SECRET (64 chars)
   openssl rand -base64 32

   # Generate new BETTER_AUTH_SECRET
   openssl rand -base64 32
   ```

2. **Update environment**:
   - Set `ENVIRONMENT=production`
   - Set `DEBUG=false`
   - Use strong JWT and Auth secrets
   - Update FRONTEND_URL if using custom domain

3. **Database**:
   - Database already on Neon (production-ready)
   - Enable backups in Neon console
   - Test connection string with prod credentials

4. **Frontend**:
   - Set `NEXT_PUBLIC_API_URL` to production API URL
   - Build: `npm run build`
   - Test build: `npm run build && npm start`

### Deploy Backend

```bash
# Using Vercel (recommended for Node/Python)
vercel

# Using Railway
railway up

# Using Render
# Connect GitHub repo in Render dashboard
```

### Deploy Frontend

```bash
# Using Vercel (built-in support for Next.js)
npm install -g vercel
vercel

# Or connect GitHub to Vercel dashboard
```

## API Documentation

### Interactive Docs

Once server is running:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### API Reference

See `specs/001-full-stack-todo-app/contracts/README.md` for:
- Request/response schemas
- HTTP status codes
- Error handling
- Authentication

## Application Architecture

```
┌─────────────────────────────────────────┐
│         Frontend (Next.js)              │
│  - /dashboard: Task management          │
│  - /auth: Signup/Signin forms           │
│  - Tailwind CSS: Responsive design      │
└────────────┬────────────────────────────┘
             │ HTTP/JSON
             ↓
┌─────────────────────────────────────────┐
│    Backend (FastAPI)                    │
│  - /api/v1/auth: Authentication         │
│  - /api/v1/users: Task CRUD             │
│  - JWT validation                       │
└────────────┬────────────────────────────┘
             │ Async SQL
             ↓
┌─────────────────────────────────────────┐
│  Database (Neon PostgreSQL)             │
│  - users table                          │
│  - tasks table                          │
│  - SSL/TLS encrypted                    │
└─────────────────────────────────────────┘
```

## Features Implemented

✅ **Phase 1**: Project Setup
✅ **Phase 2**: Database & Infrastructure
✅ **Phase 3**: User Authentication (Signup/Signin/Signout)
✅ **Phase 4**: Task CRUD (Create, Read, Update, Delete)
✅ **Phase 5**: Task Features (Complete, Edit, Delete)
🔜 **Phase 6**: Polish & Responsive Design

## Key Features Working

- ✅ User registration with secure password hashing
- ✅ JWT-based authentication
- ✅ Task creation with title and description
- ✅ Task completion toggle with strikethrough
- ✅ Task editing (title/description)
- ✅ Task deletion with confirmation
- ✅ Paginated task list (20 per page)
- ✅ Complete user data isolation
- ✅ Responsive UI (works on desktop, tablet)
- ✅ 60+ integration tests

## Next Steps

1. ✅ Run backend and frontend
2. ✅ Test signup/signin
3. ✅ Create and manage tasks
4. ✅ Verify database persistence
5. 🔜 Deploy to production
6. 🔜 Phase 6: Polish (mobile responsive, accessibility)

## Support

- **Backend Docs**: http://localhost:8000/docs
- **Database**: https://console.neon.tech
- **Frontend Code**: See `frontend/src/`
- **Backend Code**: See `backend/src/`

---

**Ready to go!** 🚀

Start the backend and frontend, then open http://localhost:3000

