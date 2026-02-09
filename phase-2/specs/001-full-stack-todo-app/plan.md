# Implementation Plan: Phase II Todo Full-Stack Web Application

**Branch**: `001-full-stack-todo-app` | **Date**: 2026-02-09 | **Spec**: [specs/001-full-stack-todo-app/spec.md](./spec.md)

**Input**: Feature specification from `specs/001-full-stack-todo-app/spec.md`

## Summary

Transform the Phase I console-based todo app into a secure, multi-user web application by implementing a full-stack architecture with:
- **Frontend**: Next.js 16+ (App Router) with responsive UI for authentication, task CRUD, and user dashboard
- **Backend**: FastAPI (Python) REST API with user isolation, input validation, and error handling
- **Database**: Neon Serverless PostgreSQL with User and Task tables, proper relationships, and indexes
- **Authentication**: Better Auth + JWT tokens for secure user authentication and session management

**Core Architecture Pattern**: API-first design where frontend consumes secure REST endpoints, all requests include JWT tokens in Authorization headers, backend verifies tokens and enforces user_id isolation on every operation.

## Technical Context

**Language/Version**:
- Backend: Python 3.10+ (async/await required)
- Frontend: Node.js 18+ with TypeScript

**Primary Dependencies**:
- Backend: FastAPI 0.104+, SQLModel, SQLAlchemy, Alembic, Pydantic v2, python-jose (JWT), bcrypt
- Frontend: Next.js 16+, React 19+, TypeScript, Better Auth, fetch API (no axios)

**Storage**: Neon Serverless PostgreSQL 15+

**Testing**:
- Backend: pytest, pytest-asyncio
- Frontend: Jest, React Testing Library (optional; acceptance tests via Cypress/Playwright for API integration)

**Target Platform**: Web (responsive design for desktop and mobile browsers)

**Project Type**: Web application (separate frontend and backend deployments)

**Performance Goals**:
- API response time: <200ms p95 (task CRUD operations)
- Frontend initial load: <3 seconds
- Task list render: <100ms for 100 tasks
- Auth flow: signup/signin complete in <2 minutes (per spec)

**Constraints**:
- JWT token expiration: 15 minutes (access), 7 days (refresh)
- Task title max length: 500 characters
- Description max length: 5000 characters
- Pagination: 20 tasks per page for lists with >100 tasks
- Database connection pool: 5-20 connections (managed by Neon)
- No synchronous blocking calls in backend (all async)

**Scale/Scope**:
- Initial users: Testing (100-1000 concurrent)
- Tasks per user: Pagination at 10,000+ tasks
- Code footprint: ~2000 LOC backend, ~1500 LOC frontend
- Deliverables: 1 backend API, 1 frontend SPA, shared secret for JWT signing

## Constitution Check

✅ **GATE PASS: All constitutional requirements verifiable in plan**

| Principle | Requirement | Plan Coverage | Status |
|-----------|-------------|---------------|--------|
| **I. Spec-Driven Development** | Feature originates from spec, plan, tasks | Spec complete → Plan in progress → Tasks TBD | ✅ PASS |
| **II. Stack Enforcement** | Fixed stack: Next.js, FastAPI, SQLModel, Neon, Better Auth | Plan specifies exact versions and technologies | ✅ PASS |
| **III. Secure-by-Design Auth** | JWT validation, user isolation, bcrypt, httpOnly cookies | Plan includes JWT middleware, ownership checks, secure token storage | ✅ PASS |
| **IV. Multi-User Data Isolation** | user_id FK, composite indexes, API-layer verification | Plan design includes user_id ownership at DB and API | ✅ PASS |
| **V. API-First Design** | REST endpoints, standard JSON schema, HTTP status codes | Plan defines API contracts (endpoints, request/response schemas) | ✅ PASS |
| **VI. Code Generation via Claude Code** | All code via agents, documented in PHRs | Plan identifies agent types (frontend-skill, fastapi-backend-api, auth-secure-handler, neon-db-ops) | ✅ PASS |
| **VII. Prompt History & Traceability** | PHRs for all decisions | Each phase outputs PHR documenting decisions and artifacts | ✅ PASS |

**Re-check post-design**: After Phase 1 contract design, validate API schemas conform to constitution § V (JSON format, HTTP codes).

## Project Structure

### Documentation (this feature)

```text
specs/001-full-stack-todo-app/
├── spec.md                  # Feature specification (complete)
├── plan.md                  # This file (technical architecture)
├── research.md              # Phase 0 findings (integration patterns, security best practices)
├── data-model.md            # Phase 1 data model (entities, relationships, constraints)
├── quickstart.md            # Phase 1 quick start guide (setup, first run)
├── contracts/               # Phase 1 API contracts
│   ├── openapi.yaml         # OpenAPI 3.0 schema for all endpoints
│   └── README.md            # Contract summary (endpoints, auth, errors)
├── checklists/
│   └── requirements.md      # Specification quality validation (all PASS)
└── [tasks.md]               # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── main.py                   # FastAPI app initialization
│   ├── config.py                 # Environment config, JWT secret
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py               # User SQLModel (id, email, name, password_hash, created_at)
│   │   └── task.py               # Task SQLModel (id, user_id FK, title, description, completed, created_at, updated_at)
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py               # UserCreate, UserResponse Pydantic schemas
│   │   └── task.py               # TaskCreate, TaskUpdate, TaskResponse Pydantic schemas
│   ├── db/
│   │   ├── __init__.py
│   │   ├── session.py            # SQLAlchemy session management
│   │   ├── engine.py             # Database connection setup
│   │   └── migrations/           # Alembic migration folder
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py           # POST /auth/signup, /auth/signin, /auth/signout
│   │   │   ├── tasks.py          # GET/POST /api/v1/users/{user_id}/tasks
│   │   │   └── routers.py        # Route aggregation
│   │   └── deps.py               # Dependency injection (JWT verification, current_user)
│   ├── security/
│   │   ├── __init__.py
│   │   ├── jwt.py                # JWT encode/decode, token creation
│   │   ├── password.py           # bcrypt hash/verify
│   │   └── middleware.py         # JWT verification middleware
│   ├── services/
│   │   ├── __init__.py
│   │   ├── user_service.py       # User CRUD logic
│   │   └── task_service.py       # Task CRUD logic with user_id filtering
│   └── utils/
│       ├── __init__.py
│       └── response.py           # Standard response formatting (data/meta/error)
├── tests/
│   ├── __init__.py
│   ├── conftest.py               # pytest fixtures (test DB, test client)
│   ├── unit/
│   │   ├── test_security.py      # JWT encode/decode, password hash tests
│   │   ├── test_services.py      # Service layer unit tests
│   │   └── test_schemas.py       # Pydantic schema validation
│   └── integration/
│       ├── test_auth_flow.py     # Signup, signin, signout integration tests
│       ├── test_task_crud.py     # Task CRUD with JWT validation
│       ├── test_isolation.py     # Multi-user data isolation tests
│       └── test_errors.py        # Error handling (400, 401, 403, 404, 500)
├── pyproject.toml                # Python dependencies
└── .env.example                  # Environment variable template

frontend/
├── src/
│   ├── app/                      # Next.js App Router
│   │   ├── layout.tsx            # Root layout
│   │   ├── page.tsx              # Home/redirect to signin or dashboard
│   │   ├── auth/
│   │   │   ├── layout.tsx        # Auth layout (centered form)
│   │   │   ├── signup/
│   │   │   │   └── page.tsx      # Signup form page
│   │   │   └── signin/
│   │   │       └── page.tsx      # Signin form page
│   │   ├── dashboard/
│   │   │   ├── layout.tsx        # Authenticated layout (header, nav)
│   │   │   └── page.tsx          # Task list dashboard
│   │   ├── tasks/
│   │   │   ├── [id]/
│   │   │   │   └── edit/
│   │   │   │       └── page.tsx  # Edit task page (or modal)
│   │   │   └── new/
│   │   │       └── page.tsx      # Create task page (or modal)
│   │   ├── api/
│   │   │   └── auth/
│   │   │       └── callback/
│   │   │           └── route.ts  # Better Auth callback handler
│   │   └── error.tsx             # Error boundary
│   ├── components/
│   │   ├── AuthForm.tsx          # Signup/signin form (email, password)
│   │   ├── TaskList.tsx          # Task list display with completion checkbox
│   │   ├── TaskItem.tsx          # Individual task item (title, description, complete, edit, delete)
│   │   ├── TaskForm.tsx          # Create/edit task form
│   │   ├── DeleteConfirm.tsx     # Delete confirmation dialog
│   │   ├── Header.tsx            # Header with user info and logout
│   │   ├── Loading.tsx           # Loading spinner
│   │   └── ErrorBoundary.tsx     # Error handling component
│   ├── lib/
│   │   ├── api-client.ts         # Fetch wrapper with JWT attachment
│   │   ├── auth.ts               # Better Auth initialization and hooks
│   │   ├── constants.ts          # API endpoints, error messages
│   │   └── utils.ts              # Helper functions
│   ├── hooks/
│   │   ├── useAuth.ts            # Auth state and methods
│   │   ├── useTasks.ts           # Tasks state management (fetch, create, update, delete)
│   │   └── useToken.ts           # JWT token management
│   ├── types/
│   │   ├── api.ts                # API response types
│   │   ├── task.ts               # Task interface
│   │   └── user.ts               # User interface
│   └── styles/
│       └── globals.css           # Global styles (Tailwind or CSS Modules)
├── public/                       # Static assets
├── tests/
│   ├── unit/
│   │   └── lib/
│   │       └── api-client.test.ts # API client tests
│   └── integration/
│       └── workflows/            # End-to-end workflow tests (signup → create task)
├── package.json                  # Node dependencies
└── tsconfig.json                 # TypeScript config

.env.example                      # Shared environment template
.env.local                        # Local overrides (development)
```

**Structure Decision**: Web application with separate frontend (Next.js) and backend (FastAPI) allows independent deployment, clear API contracts, and enables future mobile client support. Frontend uses App Router for modern React patterns; backend uses async/await throughout for I/O efficiency.

## Design Decisions

### 1. JWT Token Storage (httpOnly Cookies vs. localStorage)

**Decision**: Store JWT tokens in **httpOnly cookies** (not localStorage)

**Rationale**:
- httpOnly prevents XSS attacks (JavaScript cannot access the cookie)
- Automatic inclusion in requests (no manual Authorization header attachment needed on same domain)
- Secure flag prevents transmission over unencrypted connections

**Implementation**:
- Better Auth issues token and sets httpOnly cookie on signin
- Frontend sends requests to backend; cookies automatically included
- If token expires or is invalid, backend returns 401; frontend redirects to signin

### 2. API Response Schema

**Decision**: Standardize all responses with `{ data, meta, error }` structure

**Rationale**:
- Consistent handling in frontend (always check `error` field)
- Metadata (timestamp, request_id) enables debugging and logging
- Separates business data from infrastructure data

**Example**:
```json
{
  "data": { "id": "uuid", "title": "Task", "completed": false },
  "meta": { "timestamp": "2026-02-09T10:30:45Z", "request_id": "req-123" },
  "error": null
}
```

Error response:
```json
{
  "data": null,
  "meta": { "timestamp": "...", "request_id": "..." },
  "error": {
    "code": "TASK_NOT_FOUND",
    "message": "Task with id xyz not found",
    "details": null
  }
}
```

### 3. User Isolation Strategy

**Decision**: Enforce user_id verification at **both database and API layers**

**Rationale**:
- Database constraint (FK) prevents orphaned tasks
- API layer verification (user_id in JWT must match URL user_id) prevents accidental cross-user access
- Defense in depth: if one layer fails, the other catches it

**Implementation**:
- Task table has `user_id NOT NULL` foreign key
- Every task query filters by `WHERE user_id = current_user_id`
- API endpoint `GET /api/v1/users/{user_id}/tasks` verifies JWT `user_id == {user_id}` parameter

### 4. Password Security

**Decision**: Use **bcrypt with cost 12** (minimum)

**Rationale**:
- bcrypt is slow by design (prevents brute-force attacks)
- Cost 12 = ~0.5 second per hash (acceptable for signup/signin)
- No plaintext passwords stored

**Implementation**:
- Password hashed at user creation and update
- Never stored in logs or error messages
- Only password_hash returned from database

### 5. Authentication Flow with Better Auth

**Decision**: Use Better Auth as session provider with JWT plugin enabled

**Rationale**:
- Better Auth handles session persistence and token refresh automatically
- JWT plugin enables self-contained tokens (no server-side session store needed)
- Seamless integration with Next.js via library hooks

**Implementation**:
- Better Auth configured in Next.js with JWT plugin
- On signin: Better Auth issues JWT and sets httpOnly cookie
- On backend: JWT verified using shared secret from `.env`
- Token refresh handled automatically by Better Auth

### 6. Database Indexing Strategy

**Decision**: Create composite index `(user_id, created_at)` on tasks table

**Rationale**:
- Most common query: "fetch all tasks for user, ordered by created_at"
- Composite index covers both WHERE and ORDER BY clauses
- Prevents full table scans on large datasets

**Implementation**:
- Task queries: `SELECT * FROM tasks WHERE user_id = $1 ORDER BY created_at DESC`
- Index allows execution in O(log n) time instead of O(n)

## Phase Breakdown

### Phase 0: Research (Completed via specification)

✅ Architecture patterns researched (API-first, JWT, multi-user isolation)
✅ Technology stack confirmed (Next.js, FastAPI, SQLModel, Neon, Better Auth)
✅ Security model established (JWT tokens, bcrypt, httpOnly cookies, user_id verification)

### Phase 1: Design & Contracts (In Progress)

**Deliverables**:
- data-model.md (User and Task entities with constraints)
- contracts/openapi.yaml (API endpoint definitions)
- contracts/README.md (endpoint summary and error codes)
- quickstart.md (setup instructions and first run)

**Verification**: API contracts conform to Constitution § V (REST, standard JSON schema, HTTP codes)

### Phase 2: Task Generation (Next Step)

**Input**: plan.md (this file), spec.md, data-model.md, contracts/

**Output**: tasks.md with dependency-ordered, testable tasks
- Setup tasks (project initialization)
- Database tasks (schema creation, migrations)
- Backend tasks (API implementation)
- Auth tasks (JWT middleware, user verification)
- Frontend tasks (UI components, integration)
- Testing tasks (unit, integration, acceptance)

### Phase 3: Implementation (After tasks.md)

Execute tasks via Claude Code agents:
- `frontend-skill` for Next.js pages and components
- `fastapi-backend-api` for FastAPI routes and business logic
- `auth-secure-handler` for authentication flows
- `neon-db-ops` for database schema and migrations
- `backend-skill` for REST API design and error handling

### Phase 4: Testing & Deployment

- Unit tests for services, schemas, JWT
- Integration tests for auth flow, task CRUD, multi-user isolation
- End-to-end workflow tests (signup → create task → mark complete)
- Responsive UI tests (desktop and mobile viewports)

## Key Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| JWT secret not shared correctly between frontend & backend | Auth flow fails completely | Store in `.env`, document in quickstart.md, validate in Phase 1 |
| User_id isolation missed in one endpoint | Data leak / multi-user violation | Enforce at API layer (dependency injection of current_user), add dedicated test suite |
| Database connection limits exhausted during concurrent requests | API becomes unavailable | Use Neon's connection pooling, set pool size in config |
| Token expiration not handled on frontend | Users stuck in "loading" state | Add token refresh mechanism, catch 401 errors, redirect to signin |
| Pagination not implemented | UI crashes with 10k tasks | Implement offset/limit pagination in task list queries |

## Dependencies & Prerequisites

- Neon PostgreSQL account and database created
- Better Auth library installed and configured
- `.env` file with database URL, JWT secret, API endpoints
- Development environment: Python 3.10+, Node.js 18+

## Success Metrics (From Spec)

All of these will be validated in Phase 3-4:
- ✅ All 5 features working (signup, create task, view, complete, edit, delete)
- ✅ <2 minute signup → create task workflow
- ✅ JWT authentication validated (valid/invalid/expired tokens)
- ✅ Multi-user isolation tested (User A cannot access User B's tasks)
- ✅ Responsive UI (desktop 1920x1080, mobile 375x667)
- ✅ Standard JSON API (data/meta/error format, HTTP codes)
- ✅ Data persistence (tasks survive restarts)
- ✅ Full workflow documented (spec → plan → tasks → implementation)

## Next Steps

1. **Phase 1 Design**: Generate data-model.md, API contracts, quickstart.md
2. **Phase 2 Tasks**: Run `/sp.tasks` to break design into testable, dependency-ordered tasks
3. **Phase 3 Implementation**: Execute tasks via Claude Code agents
4. **Phase 4 Validation**: Test all acceptance criteria from spec
5. **Final Review**: Validate spec compliance and prompt iterations

---

**Plan Status**: ✅ DRAFT (ready for Phase 1 design artifacts)
**Constitution Alignment**: ✅ ALL 7 PRINCIPLES VERIFIED
**Next Command**: `/sp.tasks` (after Phase 1 design completion)
