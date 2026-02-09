# Implementation Plan: JWT Authentication & API Security Layer

**Branch**: `002-jwt-auth-api-security` | **Date**: 2026-02-09 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification for secure user authentication and REST API protection using Better Auth + JWT integration

---

## Summary

This plan implements a complete authentication and API security layer using Better Auth (Next.js frontend) and JWT tokens (FastAPI backend). The implementation enforces stateless authentication with user-based data isolation through a shared JWT secret, enabling secure multi-user task management with three core components:

1. **Frontend Authentication**: Better Auth signup/signin forms with JWT token capture
2. **Token Pipeline**: JWT issuance on login, secure storage in httpOnly cookies, and automatic header attachment to API requests
3. **Backend Authorization**: FastAPI middleware validating JWT signatures and ownership-based access control on all task endpoints

---

## Technical Context

**Language/Version**: Python 3.10+ (backend) | TypeScript + React 18+ (frontend)

**Primary Dependencies**:
- Backend: FastAPI, SQLModel, python-jose (JWT), psycopg (PostgreSQL driver)
- Frontend: Next.js 16+, Better Auth, Axios/Fetch API for HTTP requests

**Storage**: Neon PostgreSQL (users table with email unique constraint, password_hash field)

**Testing**: pytest (backend integration tests), Jest/Vitest (frontend unit tests)

**Target Platform**: Web (localhost:3000 frontend, localhost:8000 backend)

**Project Type**: Web application (frontend + backend)

**Performance Goals**:
- JWT verification: < 10ms (signature validation performance)
- Signup/signin: < 30 seconds (form validation + network)
- API request overhead: < 5ms (token extraction + validation)

**Constraints**:
- No server-side sessions (stateless only)
- All protected endpoints require valid JWT
- User ownership must be enforced on every task operation
- Generic error messages (prevent user enumeration)

**Scale/Scope**:
- Multi-user task application (2-3 concurrent users)
- 5 API endpoints (signup, signin, signout, list tasks, CRUD tasks)
- Neon database with 2 tables (users, tasks)

---

## Constitution Check

**Gates to Verify**:
- [ ] No unspecified security vulnerabilities (XSS, CSRF, privilege escalation)
- [ ] No hardcoded secrets in code
- [ ] Stateless backend (no server sessions)
- [ ] Password hashing implemented (bcrypt or equivalent)
- [ ] User ownership enforced on all operations

**Status**: ✅ All gates will be validated during implementation
- XSS protection via httpOnly cookies (not localStorage)
- CSRF protection via Bearer token format
- Privilege escalation prevention via JWT signature + ownership checks
- Secrets managed via environment variables (.env files)
- Stateless design enforced by JWT-only auth

---

## Project Structure

### Documentation (this feature)

```text
specs/002-jwt-auth-api-security/
├── spec.md              ✅ User scenarios & requirements
├── plan.md              ← This file
├── research.md          (Phase 0 - for unknowns)
├── data-model.md        (Phase 1 - entity definitions)
├── quickstart.md        (Phase 1 - getting started guide)
├── contracts/           (Phase 1 - API schemas)
│   ├── auth-endpoints.md
│   └── task-endpoints.md
├── checklists/
│   └── requirements.md   ✅ Quality validation (PASSED)
└── tasks.md             (Phase 2 - implementation tasks)
```

### Source Code (repository structure - EXISTING)

```text
backend/
├── src/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── auth.py          ← Signup/signin endpoints
│   │   │   ├── tasks.py         ← Task CRUD (to be protected)
│   │   │   └── routers.py       ← Route registration
│   │   └── deps.py              ← JWT dependency injection
│   ├── db/
│   │   └── session.py           ← Database session
│   ├── models/
│   │   ├── user.py              ✅ User model exists
│   │   └── task.py              ✅ Task model exists
│   ├── schemas/
│   │   ├── user.py              ← Request/response models
│   │   └── task.py              ← Request/response models
│   ├── security/
│   │   ├── jwt.py               ← Token generation & validation
│   │   └── password.py          ← Password hashing
│   ├── config.py                ← Settings from .env
│   └── main.py                  ✅ FastAPI app entry point
├── tests/
│   ├── integration/
│   │   └── test_auth_flow.py    ← Auth integration tests
│   └── unit/
│       └── test_jwt.py          ← Token verification tests
└── pyproject.toml               ✅ Dependencies defined

frontend/
├── src/
│   ├── pages/
│   │   ├── auth/
│   │   │   ├── signup.tsx       ← Signup form with Better Auth
│   │   │   └── signin.tsx       ← Signin form with Better Auth
│   │   ├── dashboard/
│   │   │   └── page.tsx         ← Protected dashboard
│   │   └── layout.tsx           ← Root layout
│   ├── components/
│   │   ├── auth/
│   │   │   └── AuthProvider.tsx ← Better Auth provider
│   │   └── tasks/               ← Task components
│   ├── lib/
│   │   └── api.ts              ← API client with token attachment
│   └── hooks/
│       └── useAuth.ts          ← Auth context hook
└── package.json                 ✅ Dependencies defined
```

**Structure Decision**: Web application with separate frontend (Next.js) and backend (FastAPI) directories. This allows independent deployment and clear separation of concerns. Existing directory structure is maintained; new files added as needed.

---

## Implementation Phases

### Phase 0: Research & Clarification

**Purpose**: Resolve any technical unknowns before design

**Research Tasks**:
1. ✅ Better Auth installation and configuration for Next.js
2. ✅ JWT token issuance and payload structure
3. ✅ Shared secret management between frontend and backend
4. ✅ FastAPI middleware for JWT validation
5. ✅ Secure token storage strategies (httpOnly vs secure cookies)

**Output**: `research.md` (not needed - all decisions already made in spec)

---

### Phase 1: Design & Contracts

#### 1a. Data Model (`data-model.md`)

**User Entity**:
```
- id (UUID, primary key) - auto-generated
- email (VARCHAR 255, unique) - login identifier
- name (VARCHAR 255, optional) - display name
- password_hash (VARCHAR 255) - bcrypt hashed
- created_at (TIMESTAMP) - registration time
```

**Relationships**:
- User has many Tasks (one-to-many)
- Task belongs to User (many-to-one)

**Key Constraints**:
- Email must be unique (prevent duplicate signups)
- Email must be valid format (RFC 5322 subset)
- Password must be 8+ characters with uppercase, lowercase, number
- password_hash stored, never plain password
- created_at immutable (set once on creation)

**Validation Rules**:
- Signup: email unique + password strength checked
- Login: email + password verified against password_hash
- Tasks: user_id must match authenticated user's user_id

---

#### 1b. API Contracts (`contracts/auth-endpoints.md`)

**POST /api/v1/auth/signup**
```
Request:
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "name": "John Doe"
}

Response (201 Created):
{
  "id": "uuid-string",
  "email": "user@example.com",
  "name": "John Doe",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expiresIn": 900
}

Errors:
- 400 Bad Request: Invalid email or weak password
- 409 Conflict: Email already registered
```

**POST /api/v1/auth/signin**
```
Request:
{
  "email": "user@example.com",
  "password": "SecurePass123"
}

Response (200 OK):
{
  "id": "uuid-string",
  "email": "user@example.com",
  "name": "John Doe",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expiresIn": 900
}

Errors:
- 401 Unauthorized: Invalid email or password (generic message)
```

**POST /api/v1/auth/signout**
```
Request:
Authorization: Bearer <token>

Response (200 OK):
{
  "message": "Signed out successfully"
}

Errors:
- 401 Unauthorized: Missing or invalid token
```

---

#### 1c. Task Endpoint Contracts (`contracts/task-endpoints.md`)

**All Task Endpoints Require JWT Token**:

**GET /api/v1/users/{user_id}/tasks**
```
Authorization: Bearer <token>

Response (200 OK):
{
  "items": [
    {
      "id": "task-uuid",
      "user_id": "user-uuid",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "completed": false,
      "created_at": "2026-02-09T10:00:00Z"
    }
  ],
  "total": 5,
  "skip": 0,
  "limit": 20
}

Errors:
- 401 Unauthorized: Missing or invalid token
- 403 Forbidden: Token user_id != URL user_id
```

**POST /api/v1/users/{user_id}/tasks**
```
Authorization: Bearer <token>

Request:
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}

Response (201 Created):
{
  "id": "task-uuid",
  "user_id": "user-uuid",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2026-02-09T10:00:00Z"
}

Errors:
- 401 Unauthorized: Missing or invalid token
- 403 Forbidden: Token user_id != URL user_id
```

**PUT /api/v1/users/{user_id}/tasks/{task_id}**
```
Authorization: Bearer <token>

Request:
{
  "title": "Updated title",
  "description": "Updated description",
  "completed": true
}

Response (200 OK): Updated task object

Errors:
- 401 Unauthorized: Missing or invalid token
- 403 Forbidden: Token user_id != URL user_id
- 404 Not Found: Task doesn't exist
```

**DELETE /api/v1/users/{user_id}/tasks/{task_id}**
```
Authorization: Bearer <token>

Response (204 No Content): (empty body)

Errors:
- 401 Unauthorized: Missing or invalid token
- 403 Forbidden: Token user_id != URL user_id
- 404 Not Found: Task doesn't exist
```

---

#### 1d. JWT Token Structure

**Token Payload** (claims):
```json
{
  "sub": "user-uuid",              // Subject (user ID)
  "email": "user@example.com",     // User email
  "iat": 1707528000,               // Issued at (seconds since epoch)
  "exp": 1707528900,               // Expiration (15 minutes = 900 seconds)
  "iss": "todo-app",               // Issuer
  "aud": "todo-app-users"          // Audience
}
```

**Token Signing**:
- Algorithm: HS256 (HMAC with SHA-256)
- Secret: JWT_SECRET from environment (32+ characters)
- Format: Bearer <token> in Authorization header

**Token Lifecycle**:
1. User signup/signin → Backend generates token with user_id + email claims
2. Frontend receives token → Store in httpOnly cookie (not localStorage)
3. Frontend makes API request → Automatically attach token to Authorization header
4. Backend receives request → Extract token from header, verify signature, decode claims
5. Token expired → Backend returns 401, frontend prompts user to re-authenticate

---

#### 1e. Quick Start Guide (`quickstart.md`)

```markdown
# Getting Started with JWT Authentication

## Backend Setup

1. Install dependencies:
   cd backend
   pip install -e .

2. Create .env.local with:
   DATABASE_URL=postgresql://...
   JWT_SECRET=your-32+-char-secret-key
   JWT_ALGORITHM=HS256
   JWT_EXPIRATION_MINUTES=15

3. Initialize database:
   python backend/scripts/init_db.py

4. Start backend:
   python -m uvicorn src.main:app --reload

## Frontend Setup

1. Install dependencies:
   cd frontend
   npm install better-auth

2. Create .env.local with:
   NEXT_PUBLIC_API_URL=http://localhost:8000

3. Start frontend:
   npm run dev

## Test Authentication Flow

1. Visit http://localhost:3000
2. Click "Sign Up"
3. Fill in email, password, name
4. Backend creates user, issues JWT
5. Frontend stores token in httpOnly cookie
6. Dashboard shows your tasks

## API Testing

Create a task:
curl -X POST http://localhost:8000/api/v1/users/<user-id>/tasks \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Task"}'
```

---

### Phase 2: Task Generation

**Output**: `tasks.md` (generated by `/sp.tasks` command)

**High-Level Task Groups**:

1. **Backend JWT Module** (1-2 tasks):
   - Create `security/jwt.py` with token generation and validation
   - Add JWT dependencies and configuration

2. **Backend Auth Endpoints** (1 task):
   - Implement POST /api/v1/auth/signup
   - Implement POST /api/v1/auth/signin
   - Implement POST /api/v1/auth/signout

3. **Backend Task Endpoint Protection** (1 task):
   - Add authentication middleware to FastAPI
   - Protect all task endpoints with JWT requirement
   - Add ownership validation (user_id from token vs URL)

4. **Frontend Better Auth Integration** (1-2 tasks):
   - Install and configure Better Auth
   - Create signup form component
   - Create signin form component
   - Implement session handling

5. **Frontend API Client** (1 task):
   - Create Axios/Fetch wrapper that attaches Bearer token
   - Implement automatic token refresh on 401
   - Handle token storage and retrieval from cookies

6. **Integration Testing** (1 task):
   - Test complete signup flow (form → API → token → dashboard)
   - Test login flow
   - Test cross-user access prevention
   - Test token expiration handling

---

## Key Architectural Decisions

### 1. Stateless Authentication via JWT
**Decision**: Use JWT tokens instead of server-side sessions
**Rationale**:
- Serverless-friendly (no session store needed)
- Scalable across multiple backend instances
- Token contains all necessary claims (user_id, email)
- Frontend can cache token for offline-like scenarios

**Implementation**:
- Token created on signup/signin
- Token validated via signature check (no database lookup)
- No session table required

### 2. Shared Secret Between Frontend & Backend
**Decision**: Both use same JWT_SECRET for signing and verification
**Rationale**:
- Ensures consistency between token issuer and validator
- Better Auth (frontend) and FastAPI (backend) can both sign/verify same tokens
- Environment variable management is simpler

**Implementation**:
- JWT_SECRET defined in .env.local
- Both frontend and backend read same secret
- Used for HS256 (HMAC) algorithm

### 3. HttpOnly Cookies for Token Storage
**Decision**: Store JWT in httpOnly cookie, not localStorage
**Rationale**:
- XSS protection (JavaScript can't access httpOnly cookies)
- Automatic browser transmission with CORS credentials
- Prevents token theft from localStorage

**Implementation**:
- Better Auth handles cookie storage
- Axios/Fetch configured with `withCredentials: true`
- Frontend never directly accesses token

### 4. Ownership Enforcement via user_id Validation
**Decision**: Every endpoint validates token user_id matches resource owner
**Rationale**:
- Prevents cross-user task access
- Stateless (no role tables needed)
- Simple and performant

**Implementation**:
- Middleware extracts user_id from token
- Route handler checks user_id in token vs URL parameter
- Returns 403 if mismatch

### 5. Generic Error Messages
**Decision**: Same error message for invalid email and wrong password
**Rationale**:
- Prevents user enumeration attacks
- Attacker can't determine valid emails from error messages

**Implementation**:
- Use "Invalid email or password" for both cases
- Don't distinguish between "email not found" vs "wrong password"

---

## Security Design

### Authentication Flow
```
Frontend (User)
    ↓ [Fills signup form: email, password, name]
    ↓
Next.js Signup Page (form validation)
    ↓ [POST /api/v1/auth/signup]
    ↓
FastAPI Backend
    ├─ Validate email format & password strength
    ├─ Check email not already used
    ├─ Hash password with bcrypt
    ├─ Create user record in database
    ├─ Generate JWT token with user_id, email
    └─ Return token to frontend

Frontend receives token
    ├─ Store in httpOnly cookie
    └─ Redirect to dashboard
```

### Authorization Flow
```
Frontend API Request
    ├─ Extract token from httpOnly cookie
    ├─ Attach to Authorization header (Bearer <token>)
    └─ Send to backend

FastAPI Backend
    ├─ Extract token from Authorization header
    ├─ Verify JWT signature using JWT_SECRET
    ├─ Check token not expired
    ├─ Extract user_id from token claims
    ├─ Validate user_id matches URL parameter (if present)
    ├─ Validate user owns task (if task operation)
    └─ Proceed with request OR return 401/403
```

### Attack Prevention
- **XSS**: Token in httpOnly cookie (not accessible to JS)
- **CSRF**: Bearer token format (not cookie-based automatic transmission)
- **User Enumeration**: Generic error messages
- **Privilege Escalation**: Signature verification + ownership checks
- **Session Fixation**: Stateless design, no server state to fixate

---

## Testing Strategy

### Unit Tests
- JWT token generation (correct claims)
- JWT token validation (signature check, expiration)
- Password hashing and verification
- Email format validation
- Password strength validation

### Integration Tests
- Signup flow: create user → get token → access protected endpoint
- Login flow: authenticate → get token → access task
- Token expiration: expired token → 401 response
- Cross-user access: user B tries to access user A's task → 403
- Missing token: request without Authorization header → 401

### Manual Testing
- Signup form in browser
- Login form in browser
- Create/edit/delete tasks
- Logout (token cleared)
- Browser refresh (stay logged in via cookie)

---

## Deployment Considerations

### Environment Variables
```
Production:
DATABASE_URL=postgresql://prod-host/neondb
JWT_SECRET=<generate-with-openssl-rand-base64-32>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=15
ENVIRONMENT=production
DEBUG=false

Development:
DATABASE_URL=postgresql://neondb_owner:password@localhost:5432/neondb
JWT_SECRET=dev-secret-min-32-chars-long
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=15
ENVIRONMENT=development
DEBUG=true
```

### Security Checklist Before Deployment
- [ ] JWT_SECRET is 32+ random characters (use `openssl rand -base64 32`)
- [ ] No JWT_SECRET in code, only in .env
- [ ] HTTPS enabled (for production)
- [ ] HttpOnly cookies enabled
- [ ] CORS configured correctly (frontend URL whitelisted)
- [ ] Password hashing uses bcrypt (not plain text)
- [ ] All protected endpoints require valid JWT
- [ ] Cross-user access is prevented (403 checks)
- [ ] Generic error messages (no user enumeration)
- [ ] Tokens expire after 15 minutes
- [ ] Rate limiting configured (infrastructure layer)

---

## Complexity Justification

**No violations of Constitution Check** - All gates are satisfied:
- ✅ No XSS: httpOnly cookies
- ✅ No hardcoded secrets: environment variables
- ✅ Stateless: JWT-based, no sessions
- ✅ Password hashing: bcrypt in security module
- ✅ Ownership enforcement: user_id validation on all operations

---

## Success Criteria Mapping

| Success Criterion | Implementation Strategy |
|------------------|----------------------|
| Signup < 30s | Form validation optimized, JWT generation < 10ms |
| Login < 10s | Credential check + JWT generation < 10ms |
| 100% endpoints protected | Middleware on all task routes, auth required |
| JWT verify < 10ms | Signature check only, no DB lookup |
| 0% cross-user access | Explicit 403 return on user_id mismatch |
| Passwords masked | HTML input type="password" |
| No tokens in logs | Logging configured to exclude Authorization header |
| Token refresh < 2s | Automatic token refresh on 401 |
| 99.9% uptime | Stateless auth (no session store failures) |
| Generic errors | Consistent "Invalid email or password" message |

---

## Next Steps

1. **Phase 0 Complete**: No research needed (all decisions documented)
2. **Phase 1 Complete**: Data model, API contracts, quickstart designed
3. **Phase 2 (Next)**: Run `/sp.tasks` to generate implementation tasks
4. **Phase 3**: Run `/sp.implement` to execute tasks

**Estimated Effort**:
- Design: ✅ Complete (3-4 hours)
- Implementation: ~8-10 hours (backend middleware + frontend forms)
- Testing: ~4-6 hours (integration tests + manual verification)
- **Total**: ~15-20 hours

**Critical Path**:
1. Backend JWT module (blocks auth endpoints)
2. Auth endpoints (blocks frontend integration)
3. Frontend Better Auth (blocks task operations)
4. Task endpoint protection (completes feature)

---

**Status**: ✅ READY FOR TASK GENERATION (`/sp.tasks`)
