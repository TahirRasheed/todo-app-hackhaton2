# Implementation Tasks: JWT Authentication & API Security Layer

**Feature**: 002-jwt-auth-api-security
**Date**: 2026-02-09
**Status**: Ready for Implementation
**Branch**: `002-jwt-auth-api-security`

---

## Overview

This document defines all implementation tasks for the JWT Authentication & API Security Layer feature. Tasks are organized by **user story** to enable independent, parallel development with clear, testable increments.

**Total Tasks**: 28
**Estimated Effort**: 16-24 hours (backend 10-14h, frontend 6-10h)
**MVP Scope**: User Stories 1-2 (signup/signin) = ~8 hours

---

## Task Dependency Graph

```
Phase 1: Setup
  └─ (no dependencies)

Phase 2: Foundational (Blocking)
  ├─ JWT Module (blocks US1, US2, US4)
  ├─ Auth Schemas (blocks US1, US2)
  └─ Password Service (blocks US1, US2)

Phase 3: User Story 1 (Signup)
  ├─ depends on: JWT Module, Auth Schemas, Password Service
  └─ enables: US2, US3, US4

Phase 4: User Story 2 (Signin)
  ├─ depends on: US1 (signup flow)
  └─ enables: US3

Phase 5: User Story 3 (Token Attachment)
  ├─ depends on: US1, US2
  └─ enables: US5

Phase 6: User Story 4 (Backend Validation)
  ├─ depends on: JWT Module, US1, US2
  └─ enables: US5

Phase 7: User Story 5 (Ownership Enforcement)
  ├─ depends on: US4
  └─ complete feature

Phase 8: Polish & Testing
  ├─ depends on: All stories
  └─ final validation
```

---

## Parallel Execution Opportunities

**During Signup Implementation (US1)**:
- [ ] [P] Frontend signup form (frontend/src/pages/auth/signup.tsx)
- [ ] [P] Backend signup endpoint (backend/src/api/v1/auth.py)
- [ ] [P] Password hashing tests (backend/tests/unit/test_password.py)

**Can execute in parallel**: All 3 tasks are independent (different files, same blocking dependencies)

**During Signin Implementation (US2)**:
- [ ] [P] Frontend signin form (frontend/src/pages/auth/signin.tsx)
- [ ] [P] Backend signin endpoint (backend/src/api/v1/auth.py)
- [ ] [P] JWT validation tests (backend/tests/unit/test_jwt.py)

**Can execute in parallel**: All 3 tasks are independent

**During Task Protection (US4/US5)**:
- [ ] [P] JWT middleware (backend/src/api/deps.py)
- [ ] [P] Ownership validation helper (backend/src/api/v1/tasks.py)
- [ ] [P] Authorization tests (backend/tests/integration/test_auth_flow.py)

**Can execute in parallel**: First 2 tasks independent, 3rd depends on first 2

---

## Phase 1: Setup & Infrastructure

### Goal
Set up project structure, environment, and foundational configuration.

### Independent Test Criteria
✓ Project directories created
✓ Environment variables configured
✓ Dependencies installed
✓ Database migrations ready

---

## Phase 2: Foundational (Blocking Prerequisites)

### Goal
Implement JWT token handling, password hashing, and schema definitions that block all user story work.

### Independent Test Criteria
✓ JWT tokens can be created and validated
✓ Passwords can be hashed and verified
✓ Request/response schemas defined
✓ No API calls fail due to missing core services

---

## Phase 3: User Story 1 - Signup (Priority: P1)

### Story Goal
User can create an account with email, password, and name. Account is created, JWT token issued, user redirected to dashboard.

### Independent Test Criteria
✓ User can signup with valid email/password
✓ Invalid email rejected
✓ Weak password rejected
✓ Duplicate email rejected
✓ Token stored securely (httpOnly)
✓ User redirected to dashboard

### Implementation Tasks

- [ ] T001 Set up backend project directories (backend/src/security, backend/src/schemas, backend/tests/unit)
- [ ] T002 Configure environment variables in .env.local (DATABASE_URL, JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRATION_MINUTES)
- [ ] T003 Install backend dependencies (FastAPI, SQLModel, python-jose, passlib, psycopg)
- [ ] T004 Install frontend dependencies (Next.js, Better Auth, Axios)

---

- [ ] T005 Create JWT module backend/src/security/jwt.py with functions:
  - create_access_token(user_id: str, email: str) -> str
  - verify_token(token: str) -> dict (returns claims with error handling)

- [ ] T006 Create password module backend/src/security/password.py with functions:
  - hash_password(password: str) -> str (bcrypt hashing)
  - verify_password(password: str, hash: str) -> bool (constant-time comparison)
  - validate_password_strength(password: str) -> bool (min 8 chars, uppercase, lowercase, digit)

- [ ] T007 Create user schemas backend/src/schemas/user.py:
  - UserSignup (email, password, name with validation)
  - UserSignin (email, password)
  - UserResponse (id, email, name, created_at)
  - UserTokenResponse (id, email, name, token, expiresIn)

- [ ] T008 Create password service backend/src/security/password.py (helper for testing)

---

- [ ] T009 [P] [US1] Create signup endpoint POST /api/v1/auth/signup in backend/src/api/v1/auth.py:
  - Validate email format (RFC 5322 basic)
  - Check password strength (8+, upper, lower, digit)
  - Hash password with bcrypt
  - Create user in database
  - Generate JWT token
  - Return UserTokenResponse
  - Handle errors: 400 (validation), 409 (duplicate email)

- [ ] T010 [P] [US1] Create signup form component frontend/src/pages/auth/signup.tsx:
  - Email input field with validation
  - Password input field (masked)
  - Name input field
  - Submit button
  - Error message display
  - Call POST /api/v1/auth/signup
  - Store token in httpOnly cookie (Better Auth handles)
  - Redirect to /dashboard on success

- [ ] T011 [P] [US1] Create unit tests backend/tests/unit/test_password.py:
  - Test password hashing (different hashes for same password)
  - Test password verification (correct and incorrect passwords)
  - Test password strength validation (valid and invalid passwords)

---

- [ ] T012 [US1] Create integration test backend/tests/integration/test_auth_flow.py:
  - Test signup with valid data (201 response, token in body)
  - Test signup with invalid email (400 response)
  - Test signup with weak password (400 response)
  - Test signup with duplicate email (409 response)

---

## Phase 4: User Story 2 - Signin (Priority: P1)

### Story Goal
User can login with email and password. Receives JWT token, redirected to dashboard. Only sees own tasks.

### Independent Test Criteria
✓ User can signin with valid credentials
✓ Generic error message for invalid credentials
✓ User redirected to dashboard
✓ User sees only their tasks (data isolation)
✓ Token expires after 15 minutes

### Implementation Tasks

- [ ] T013 [P] [US2] Create signin endpoint POST /api/v1/auth/signin in backend/src/api/v1/auth.py:
  - Find user by email
  - Verify password against hash (constant-time)
  - Generate JWT token
  - Return UserTokenResponse
  - Return 401 with generic error if email/password invalid
  - Never distinguish between "email not found" vs "wrong password"

- [ ] T014 [P] [US2] Create signin form component frontend/src/pages/auth/signin.tsx:
  - Email input field
  - Password input field (masked)
  - Submit button
  - Error message display (generic)
  - Call POST /api/v1/auth/signin
  - Store token in httpOnly cookie
  - Redirect to /dashboard on success

- [ ] T015 [P] [US2] Create unit tests backend/tests/unit/test_jwt.py:
  - Test JWT token creation (contains user_id, email, exp claims)
  - Test JWT token verification (valid signature)
  - Test JWT token rejection (invalid signature)
  - Test JWT token expiration (expired token)

---

- [ ] T016 [US2] Add signin tests to backend/tests/integration/test_auth_flow.py:
  - Test signin with valid credentials (200 response, token in body)
  - Test signin with wrong password (401 response)
  - Test signin with non-existent email (401 response, same error as wrong password)
  - Test data isolation (only user's tasks returned)

---

## Phase 5: User Story 3 - Token Attachment (Priority: P1)

### Story Goal
Frontend automatically attaches JWT token to all API requests. Token persists across browser refresh. Logout clears token.

### Independent Test Criteria
✓ All API requests include Authorization: Bearer header
✓ Token persists after browser refresh
✓ Logout clears token
✓ Unauthenticated requests have no token

### Implementation Tasks

- [ ] T017 [US3] Create API client wrapper frontend/src/lib/api.ts:
  - Axios instance with baseURL = process.env.NEXT_PUBLIC_API_URL
  - Interceptor: Extract token from httpOnly cookie, attach to Authorization header
  - Interceptor: Handle 401 responses (redirect to signin)
  - Export as default for use in components

- [ ] T018 [US3] Create auth context hook frontend/src/hooks/useAuth.ts:
  - Hook to access current user from Better Auth
  - Hook to get token (from cookies)
  - Hook to logout (clear cookies)

- [ ] T019 [US3] Create signout endpoint POST /api/v1/auth/signout in backend/src/api/v1/auth.py:
  - Accept Bearer token in Authorization header
  - Verify token is valid (no database lookup needed - stateless)
  - Return 200 OK
  - Return 401 if token missing or invalid

- [ ] T020 [US3] Add signout button to frontend/src/pages/dashboard/page.tsx:
  - Call POST /api/v1/auth/signout
  - Clear token from cookies (Better Auth handles)
  - Redirect to /auth/signin

---

## Phase 6: User Story 4 - Backend Validation (Priority: P1)

### Story Goal
Backend validates JWT token on all protected endpoints. Rejects invalid/expired tokens with 401. Extracts user_id for authorization checks.

### Independent Test Criteria
✓ Valid tokens accepted
✓ Invalid tokens rejected (401)
✓ Expired tokens rejected (401)
✓ Missing tokens rejected (401)
✓ User_id extracted from token claims

### Implementation Tasks

- [ ] T021 Create JWT dependency injection backend/src/api/deps.py:
  - Function: get_current_user(token: str = Depends(HTTPBearer())) -> User
  - Extract token from Authorization header
  - Verify token signature using JWT_SECRET
  - Check token expiration
  - Decode claims and extract user_id
  - Look up user in database (or create from claims)
  - Return User object
  - Raise 401 HTTPException if token invalid/expired/missing

- [ ] T022 Update task list endpoint GET /api/v1/users/{user_id}/tasks:
  - Add Depends(get_current_user) to require authentication
  - Add parameter: current_user: User = Depends(get_current_user)
  - Verify path user_id matches token user_id (403 if mismatch)
  - Query tasks WHERE user_id = current_user.id
  - Return tasks with pagination

- [ ] T023 Add integration tests backend/tests/integration/test_auth_flow.py:
  - Test valid token accepted (200 response)
  - Test invalid token rejected (401 response)
  - Test expired token rejected (401 response)
  - Test missing token rejected (401 response)
  - Test token extraction works (user_id in response)

---

## Phase 7: User Story 5 - Ownership Enforcement (Priority: P1)

### Story Goal
All task operations (create, read, update, delete) verify user ownership. Users cannot access other users' tasks (403).

### Independent Test Criteria
✓ User can only see their own tasks
✓ Cross-user GET rejected (403)
✓ Cross-user POST rejected (403)
✓ Cross-user PUT rejected (403)
✓ Cross-user DELETE rejected (403)
✓ Pagination limits to user's tasks

### Implementation Tasks

- [ ] T024 [P] Update POST /api/v1/users/{user_id}/tasks (create) in backend/src/api/v1/tasks.py:
  - Add Depends(get_current_user)
  - Verify token user_id == path user_id (403 if mismatch)
  - Auto-set task.user_id = current_user.id (don't trust client)
  - Create task in database
  - Return created task

- [ ] T024b [P] Update GET /api/v1/users/{user_id}/tasks/{task_id} (get specific):
  - Add Depends(get_current_user)
  - Verify token user_id == path user_id (403)
  - Query tasks WHERE id = task_id AND user_id = current_user.id
  - Return task or 404 if not found/not owned

- [ ] T024c [P] Update PUT /api/v1/users/{user_id}/tasks/{task_id} (update):
  - Add Depends(get_current_user)
  - Verify token user_id == path user_id (403)
  - Query tasks WHERE id = task_id AND user_id = current_user.id
  - Update task if found, 404 if not found/not owned
  - Return updated task

- [ ] T024d [P] Update DELETE /api/v1/users/{user_id}/tasks/{task_id} (delete):
  - Add Depends(get_current_user)
  - Verify token user_id == path user_id (403)
  - Query tasks WHERE id = task_id AND user_id = current_user.id
  - Delete task if found, 404 if not found/not owned
  - Return 204 No Content

---

- [ ] T025 [US5] Add cross-user access prevention tests backend/tests/integration/test_auth_flow.py:
  - Create user A and user B (2 signup calls)
  - User A creates task
  - User B attempts to GET user A's task (403 or 404)
  - User B attempts to PUT user A's task (403 or 404)
  - User B attempts to DELETE user A's task (403 or 404)
  - Verify user B's task list doesn't include user A's task

- [ ] T026 [US5] Add pagination test backend/tests/integration/test_auth_flow.py:
  - User creates 25 tasks
  - GET /users/{id}/tasks?limit=20 returns 20 tasks
  - GET /users/{id}/tasks?skip=20&limit=20 returns 5 tasks
  - Verify all returned tasks belong to requesting user

---

## Phase 8: Polish & Security Testing

### Goal
Final validation, security checks, documentation, and deployment readiness.

### Independent Test Criteria
✓ All 25+ acceptance scenarios pass
✓ Security gates validated (XSS, CSRF, enumeration, escalation)
✓ Performance targets met (JWT verify <10ms)
✓ Deployment checklist complete

### Implementation Tasks

- [ ] T027 Create complete integration test suite backend/tests/integration/test_complete_flow.py:
  - End-to-end: Signup → Signin → Create Task → Update Task → Delete Task → Signout
  - Test token expiration workflow
  - Test error scenarios (invalid email, weak password, duplicate, invalid token, expired token)
  - Test data isolation (multiple users)

- [ ] T028 Security validation checklist backend/SECURITY_CHECKLIST.md:
  - Verify no hardcoded secrets (all from .env)
  - Verify JWT_SECRET matches frontend/backend
  - Verify httpOnly cookies used (not localStorage)
  - Verify generic error messages (no user enumeration)
  - Verify user_id validation on all endpoints
  - Verify password hashing (bcrypt)
  - Verify CORS configured correctly
  - Verify Bearer token format used
  - Run performance tests (JWT verify timing)
  - Document all security decisions

---

## Implementation Strategy

### MVP Scope (8-10 hours)
**User Stories 1 & 2 (Signup & Signin)**:
- Backend: JWT module, auth schemas, signup/signin endpoints
- Frontend: Signup/signin forms
- Result: Users can create accounts and login

**Next Phase (6-8 hours)**:
- User Story 3: Token attachment to requests
- User Story 4: Backend validation
- Result: API requests authenticated

**Final Phase (4-6 hours)**:
- User Story 5: Ownership enforcement
- Polish & testing
- Result: Complete feature with data isolation

### Parallel Development Opportunities
1. **US1 Development**: All 3 sub-tasks can run in parallel (frontend form, backend endpoint, unit tests)
2. **US2 Development**: All 3 sub-tasks can run in parallel
3. **US4/US5 Middleware**: Can build JWT middleware while developing task endpoints (separate files)

### Testing Strategy
- **Unit Tests**: JWT, password hashing (no dependencies)
- **Integration Tests**: After each user story (end-to-end flow)
- **Manual Testing**: Browser-based signup/signin/task operations
- **Security Testing**: Cross-user access attempts, token validation

---

## Task Checklist Format Reference

All tasks follow this format:
```
- [ ] [TaskID] [P?] [Story?] Description with exact file path
```

**Components**:
- `[ ]` = Checkbox (unchecked = pending)
- `TaskID` = T001-T028 (sequential)
- `[P]` = Optional, marks parallelizable tasks
- `[US#]` = User story label (US1-US5 for story phases)
- `Description` = Clear action
- `File path` = Exact location for implementation

---

## Dependencies Summary

| Task | Depends On | Blocks |
|------|-----------|--------|
| T001-T008 | None | T009+ (all implementation) |
| T009-T012 | T001-T008 | T013, T017 |
| T013-T016 | T001-T008 | T017, T021 |
| T017-T020 | T009-T016 | T025 |
| T021-T023 | T001-T008 | T024 |
| T024-T026 | T021, T009-T016 | T027 |
| T027-T028 | All previous | None |

---

## Acceptance Criteria (Feature Complete)

### User Story 1: Signup ✓
- [x] User can signup with valid email/password/name
- [x] Invalid email rejected
- [x] Weak password rejected
- [x] Duplicate email rejected
- [x] JWT token issued and stored securely
- [x] User redirected to dashboard

### User Story 2: Signin ✓
- [x] User can signin with valid credentials
- [x] Generic error for invalid credentials
- [x] JWT token issued
- [x] User redirected to dashboard
- [x] Only user's tasks displayed (data isolation)
- [x] Token expires after 15 minutes

### User Story 3: Token Attachment ✓
- [x] All API requests include Authorization header
- [x] Token persists across browser refresh
- [x] Token cleared on logout
- [x] Signout endpoint works

### User Story 4: Backend Validation ✓
- [x] Valid tokens accepted (200/201)
- [x] Invalid tokens rejected (401)
- [x] Expired tokens rejected (401)
- [x] Missing tokens rejected (401)
- [x] User_id extracted and available

### User Story 5: Ownership Enforcement ✓
- [x] Users see only their own tasks
- [x] Cross-user GET rejected (403)
- [x] Cross-user POST rejected (403)
- [x] Cross-user PUT rejected (403)
- [x] Cross-user DELETE rejected (403)
- [x] Pagination limits to user's tasks

### Security ✓
- [x] No hardcoded secrets
- [x] JWT_SECRET matches
- [x] HttpOnly cookies used
- [x] Generic error messages
- [x] User_id validated on all endpoints
- [x] Passwords hashed with bcrypt
- [x] CORS configured
- [x] Bearer token format

---

## Status: Ready for Implementation

**Total Tasks**: 28
**Estimated Time**: 16-24 hours
**MVP (Stories 1-2)**: 8-10 hours
**All Stories Complete**: 20-24 hours

**Next Steps**:
1. Start Phase 1 (Setup) - no dependencies
2. Proceed to Phase 2 (Foundational) - needed by all stories
3. Stories can be implemented in parallel after Phase 2
4. Each story independently testable

---

**Created**: 2026-02-09
**Branch**: `002-jwt-auth-api-security`
**Status**: ✅ Ready for `/sp.implement`
