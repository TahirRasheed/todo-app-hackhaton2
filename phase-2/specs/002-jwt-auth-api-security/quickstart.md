# Quick Start: JWT Authentication Implementation

**Feature**: 002-jwt-auth-api-security
**Date**: 2026-02-09
**Status**: Implementation ready

---

## 5-Minute Setup

### Prerequisites

- Python 3.10+ (backend)
- Node.js 18+ (frontend)
- Neon PostgreSQL (already configured)
- Tables created (users, tasks)

### Step 1: Backend Configuration

```bash
# Set JWT secret in .env.local (if not already set)
echo "JWT_SECRET=your-32-character-random-secret-key-here" >> backend/.env.local

# Backend already has JWT dependencies in pyproject.toml:
# - python-jose[cryptography]
# - passlib[bcrypt]
```

### Step 2: Start Backend

```bash
cd backend

# Install JWT dependencies (if not already)
pip install python-jose passlib bcrypt

# Start server
python -m uvicorn src.main:app --reload
```

**Expected output**:
```
🚀 Starting Todo API...
✅ Database schema initialized successfully
INFO: Uvicorn running on http://127.0.0.1:8000
```

### Step 3: Test Authentication Endpoint

```bash
# Signup
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123",
    "name": "Test User"
  }'

# Response includes JWT token
# {
#   "id": "uuid-...",
#   "email": "test@example.com",
#   "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "expiresIn": 900
# }
```

### Step 4: Start Frontend

```bash
cd frontend

# Install Better Auth (if not already)
npm install better-auth

# Start dev server
npm run dev
```

**Expected output**:
```
▲ Next.js 16.x.x
- Local: http://localhost:3000
✓ Ready
```

### Step 5: Test Full Flow

1. Visit http://localhost:3000
2. Click "Sign Up"
3. Fill in email, password, name
4. Click "Create Account"
5. Should be redirected to dashboard
6. Create a task
7. Task should appear in list
8. Refresh page (should stay logged in)
9. Click "Sign Out"
10. Should be redirected to signin page

---

## Implementation Checklist

### Backend (FastAPI)

- [ ] **JWT Module** (`backend/src/security/jwt.py`):
  - `create_access_token(user_id: str, email: str) -> str`
  - `verify_token(token: str) -> dict` (returns claims)
  - `get_current_user(token: str) -> User` (dependency)

- [ ] **Auth Endpoints** (`backend/src/api/v1/auth.py`):
  - `POST /auth/signup` - create user, return token
  - `POST /auth/signin` - authenticate, return token
  - `POST /auth/signout` - clear token (frontend clears cookie)

- [ ] **Task Endpoint Protection** (`backend/src/api/v1/tasks.py`):
  - Protect all endpoints with `Depends(get_current_user)`
  - Add ownership check: `if task.user_id != current_user.id: raise 403`
  - Filter list queries: `WHERE user_id = current_user.id`

### Frontend (Next.js + Better Auth)

- [ ] **Better Auth Setup** (`frontend/src/lib/auth.ts`):
  - Initialize Better Auth with signup/signin
  - Configure JWT plugin (if available)
  - Set shared JWT_SECRET from env

- [ ] **Auth Pages** (`frontend/src/pages/auth/`):
  - `signup.tsx` - form component
  - `signin.tsx` - form component
  - Form validation (email, password strength)

- [ ] **API Client** (`frontend/src/lib/api.ts`):
  - Wrapper around Axios/Fetch
  - Attach Bearer token to all requests
  - Handle 401 (expired token) → redirect to signin

- [ ] **Auth Context** (`frontend/src/hooks/useAuth.ts`):
  - Hook for accessing current user
  - Hook for logout

- [ ] **Protected Routes** (`frontend/src/app/layout.tsx`):
  - Redirect unauthenticated users to signin
  - Pass auth context to components

---

## Environment Variables

### Backend (.env.local)

```env
# Existing variables
DATABASE_URL=postgresql://neondb_owner:npg_...@ep-holy-butterfly-ai4lnkq4-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require

# JWT Configuration (ADD THESE)
JWT_SECRET=dev-secret-key-please-change-in-production-min32chars
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=15

# Existing
ENVIRONMENT=development
DEBUG=true
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_JWT_SECRET=dev-secret-key-please-change-in-production-min32chars
```

**Note**: JWT_SECRET must match between frontend and backend!

---

## Testing Flows

### 1. Signup Flow

```bash
# 1. Create account
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "password": "AlicePass123",
    "name": "Alice"
  }'

# Response (save token):
# TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
# USER_ID=550e8400-e29b-41d4-a716-446655440000

# 2. Verify token works
TOKEN=<from-response>
curl -X GET http://localhost:8000/api/v1/users/550e8400-e29b-41d4-a716-446655440000/tasks \
  -H "Authorization: Bearer $TOKEN"

# Should return empty task list (201 response, items: [])
```

### 2. Task Creation Flow

```bash
# 1. Create task
curl -X POST http://localhost:8000/api/v1/users/550e8400-e29b-41d4-a716-446655440000/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, eggs, bread"
  }'

# Response (save task_id):
# TASK_ID=660e8400-e29b-41d4-a716-446655440001

# 2. Verify task appears in list
curl -X GET http://localhost:8000/api/v1/users/550e8400-e29b-41d4-a716-446655440000/tasks \
  -H "Authorization: Bearer $TOKEN"

# Should return 1 item with the created task
```

### 3. Cross-User Access Prevention

```bash
# 1. Create second user (Bob)
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "bob@example.com",
    "password": "BobPass123",
    "name": "Bob"
  }'

# Response (save Bob's token and ID):
# BOB_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
# BOB_ID=550e8400-e29b-41d4-a716-446655440111

# 2. Bob tries to access Alice's tasks
curl -X GET http://localhost:8000/api/v1/users/550e8400-e29b-41d4-a716-446655440000/tasks \
  -H "Authorization: Bearer $BOB_TOKEN"

# Should return 403 Forbidden (user_id mismatch)

# 3. Bob tries to access Alice's specific task
curl -X GET http://localhost:8000/api/v1/users/550e8400-e29b-41d4-a716-446655440000/tasks/660e8400-e29b-41d4-a716-446655440001 \
  -H "Authorization: Bearer $BOB_TOKEN"

# Should return 403 Forbidden
```

### 4. Token Expiration

```bash
# 1. Wait for token to expire (15 minutes = 900 seconds)
sleep 901

# 2. Try to use expired token
curl -X GET http://localhost:8000/api/v1/users/550e8400-e29b-41d4-a716-446655440000/tasks \
  -H "Authorization: Bearer $TOKEN"

# Should return 401 Unauthorized (token expired)

# 3. Sign in again to get new token
curl -X POST http://localhost:8000/api/v1/auth/signin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "password": "AlicePass123"
  }'

# Response contains new token
```

### 5. Invalid Token

```bash
# Try with invalid token
curl -X GET http://localhost:8000/api/v1/users/550e8400-e29b-41d4-a716-446655440000/tasks \
  -H "Authorization: Bearer invalid-token-12345"

# Should return 401 Unauthorized (invalid signature)
```

### 6. Missing Token

```bash
# Try without token
curl -X GET http://localhost:8000/api/v1/users/550e8400-e29b-41d4-a716-446655440000/tasks

# Should return 401 Unauthorized (missing authentication)
```

---

## Frontend Implementation Details

### Better Auth Configuration

```typescript
// frontend/src/lib/auth.ts
import BetterAuth from 'better-auth';

export const auth = new BetterAuth({
  baseURL: 'http://localhost:8000',
  jwt: {
    secret: process.env.NEXT_PUBLIC_JWT_SECRET,
    expiresIn: 900, // 15 minutes
  },
});
```

### API Client with Token Attachment

```typescript
// frontend/src/lib/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  withCredentials: true, // Send cookies automatically
});

// Automatically attach token to all requests
api.interceptors.request.use((config) => {
  // Token is in httpOnly cookie, sent automatically by browser
  return config;
});

// Handle 401 → redirect to signin
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      window.location.href = '/auth/signin';
    }
    return Promise.reject(error);
  }
);

export default api;
```

---

## Debugging Tips

### Backend Logs

```bash
# Enable debug logging
export DEBUG=true
python -m uvicorn src.main:app --reload --log-level debug
```

**Look for**:
- Token generation: "Issued token for user..."
- Token validation: "Validating token..."
- Authorization failures: "User mismatch: token_user != resource_user"

### Frontend Logs

```typescript
// Add to API client
api.interceptors.request.use((config) => {
  console.log('Request:', config.method, config.url);
  return config;
});
```

### Check Token Claims

```bash
# Decode JWT (use jwt.io or jq)
TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Extract and decode payload (Base64)
echo $TOKEN | cut -d'.' -f2 | base64 -d | jq
```

### Verify Database State

```bash
# Check users
SELECT id, email, name, created_at FROM users;

# Check tasks
SELECT id, user_id, title, completed FROM tasks;

# Check task ownership
SELECT t.title, u.email
FROM tasks t
JOIN users u ON t.user_id = u.id;
```

---

## Common Issues

### Issue: 401 Unauthorized on all requests

**Cause**: JWT_SECRET mismatch between frontend and backend

**Fix**:
```bash
# Verify same secret in both .env files
grep JWT_SECRET backend/.env.local
grep JWT_SECRET frontend/.env.local

# Should be identical!
```

### Issue: 403 Forbidden when accessing own tasks

**Cause**: Token user_id doesn't match URL user_id

**Fix**:
```bash
# Extract user_id from token
TOKEN=eyJ...
echo $TOKEN | cut -d'.' -f2 | base64 -d | jq .sub

# Use that ID in request
USER_ID=<from-token>
curl http://localhost:8000/api/v1/users/$USER_ID/tasks \
  -H "Authorization: Bearer $TOKEN"
```

### Issue: CORS error in browser console

**Cause**: Frontend and backend not configured for CORS

**Fix**: Backend already has CORS middleware, ensure:
```python
# backend/src/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],  # http://localhost:3000
    allow_credentials=True,  # Allow cookies
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: Token not being sent with requests

**Cause**: Frontend not attaching token or credentials not set

**Fix**:
```typescript
// Ensure credentials included in fetch/axios
fetch('...', {
  credentials: 'include', // Send cookies
})

// Or in axios
const api = axios.create({
  withCredentials: true, // Send cookies
});
```

---

## Next Steps After Implementation

1. ✅ Backend JWT module and auth endpoints
2. ✅ Frontend signup/signin forms
3. ✅ Task endpoint protection
4. ⏭️ Run integration tests (pytest)
5. ⏭️ Manual end-to-end testing
6. ⏭️ Deploy to production (generate new JWT_SECRET)

---

**Status**: ✅ Ready to implement!
