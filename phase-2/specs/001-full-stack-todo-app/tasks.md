---
description: "Task list for Phase II Todo Full-Stack Web Application"
---

# Tasks: Phase II Todo Full-Stack Web Application

**Input**: Design documents from `/specs/001-full-stack-todo-app/`
**Prerequisites**: plan.md (✅), spec.md (✅), data-model.md (✅), contracts/ (✅)

**Organization**: Tasks are grouped by user story priority to enable independent implementation and testing of each feature slice.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`, `backend/tests/`
- **Frontend**: `frontend/src/`, `frontend/tests/`
- **Database**: `backend/src/db/migrations/`
- **Documentation**: `specs/001-full-stack-todo-app/`

---

## Dependency Graph

```
Phase 1: Setup
  ↓
Phase 2: Foundational (Database + Core Auth)
  ├─→ Phase 3: US1 (User Registration & Signin)
  │    ├─→ Phase 4: US2 (Create & View Tasks)
  │    │    ├─→ Phase 5: US3 (Mark Complete) [P]
  │    │    ├─→ Phase 5: US4 (Edit Tasks) [P]
  │    │    └─→ Phase 5: US5 (Delete Tasks) [P]
  │    └─→ Phase 6: Polish & Cross-Cutting
```

**Key Dependencies**:
- Phase 1 must complete before all other phases
- Phase 2 (database) must complete before Phase 3 (auth)
- Phase 3 (auth) must complete before Phase 4-5 (task CRUD)
- Phase 4-5 can run in parallel (independent features)

**MVP Scope**: Phases 1-4 (setup + auth + create/view tasks)
**Full Scope**: Phases 1-6 (all user stories + polish)

---

## Phase 1: Project Setup & Environment

**Purpose**: Initialize frontend and backend project structures, install dependencies, configure environment.

- [ ] T001 Create backend project structure with pyproject.toml dependencies in `backend/`
- [ ] T002 [P] Create Next.js 16+ frontend app with App Router structure in `frontend/`
- [ ] T003 [P] Create `.env.example` with placeholder DATABASE_URL, JWT_SECRET, BETTER_AUTH_SECRET in repository root
- [ ] T004 [P] Create `.env.local` with actual values for local development in repository root
- [ ] T005 [P] Configure backend Neon PostgreSQL connection string in `backend/src/config.py`
- [ ] T006 [P] Setup Alembic migration system in `backend/src/db/migrations/`
- [ ] T007 [P] Create FastAPI app initialization in `backend/src/main.py` with CORS middleware configured for localhost:3000
- [ ] T008 [P] Configure Next.js TypeScript, routing, and CSS (Tailwind recommended) in `frontend/`
- [ ] T009 [P] Create `frontend/.env.local` with API_URL=http://localhost:8000

**Test Criteria**: Both `uvicorn src.main:app --reload` (backend) and `npm run dev` (frontend) start without errors

---

## Phase 2: Database & Core Infrastructure

**Purpose**: Create database schema, establish ORM models, setup dependency injection and utilities.

### Database Schema & ORM

- [ ] T010 Create User SQLModel in `backend/src/models/user.py` with fields: id (UUID), email (unique, indexed), name, password_hash, created_at
- [ ] T011 [P] Create Task SQLModel in `backend/src/models/task.py` with fields: id (UUID), user_id (FK), title (max 500), description (max 5000), completed (bool), created_at, updated_at, indexes for (user_id) and (user_id, created_at DESC)
- [ ] T012 [P] Create Alembic migration `versions/001_initial_schema.py` to create users and tasks tables with proper constraints and indexes
- [ ] T013 Run `alembic upgrade head` to verify migration succeeds and schema is created in Neon PostgreSQL

### Pydantic Schemas & Validation

- [ ] T014 Create UserCreate, UserResponse Pydantic schemas in `backend/src/schemas/user.py`
- [ ] T015 [P] Create TaskCreate, TaskUpdate, TaskResponse Pydantic schemas in `backend/src/schemas/task.py` with field validation (title required, max lengths)
- [ ] T016 [P] Create request/response wrapper schema in `backend/src/utils/response.py`: `{ "data": {...}, "meta": {...}, "error": null }`

### Database & Session Management

- [ ] T017 Create SQLAlchemy session factory in `backend/src/db/session.py` using SQLModel
- [ ] T018 [P] Create database engine setup in `backend/src/db/engine.py` with Neon connection pooling
- [ ] T019 [P] Create `backend/src/db/__init__.py` to export session and engine

### Security & JWT Utilities

- [ ] T020 Create password hashing utilities (bcrypt cost 12) in `backend/src/security/password.py` with hash_password() and verify_password()
- [ ] T021 [P] Create JWT encode/decode utilities in `backend/src/security/jwt.py` using python-jose, JWT_SECRET from config, token expiration (15 min access, 7 days refresh)
- [ ] T022 [P] Create get_current_user dependency in `backend/src/api/deps.py` to extract and verify JWT from Authorization header, return User object or raise 401

### Utilities

- [ ] T023 Create response formatter utility in `backend/src/utils/response.py` to wrap all responses in standard format

**Test Criteria**:
- Database schema created in Neon (verify with `\d users`, `\d tasks`)
- `from backend.src.models import User, Task` imports successfully
- `from backend.src.schemas import UserCreate, TaskResponse` imports successfully
- `get_current_user` dependency can be imported

---

## Phase 3: User Registration & Signin (Priority: P1)

**Purpose**: Implement user signup and signin with JWT token issuance. Independent test: create account → signin → access dashboard.

**User Story Goal**: Users can register accounts with email/password and sign in to access authenticated sections.

**Independent Test**: Navigate to signup → create account with email/password → signin with credentials → JWT issued → can access protected endpoint

### Backend: User Service & Endpoints

- [x] T024 [US1] Create UserService in `backend/src/services/user_service.py` with:
  - create_user(email, password, name) → hashes password, checks email uniqueness, creates User in DB
  - get_user_by_email(email) → returns User or None
  - authenticate(email, password) → verifies password, returns User or raises 401
- [x] T025 [US1] Create POST /auth/signup endpoint in `backend/src/api/v1/auth.py`:
  - Accepts UserCreate (email, password, name)
  - Validates email format, password min 8 chars
  - Calls UserService.create_user()
  - Returns 201 Created with UserResponse + JWT token in Set-Cookie header (httpOnly, Secure, SameSite=Strict)
  - Returns 400 if email exists or validation fails

- [x] T026 [US1] Create POST /auth/signin endpoint in `backend/src/api/v1/auth.py`:
  - Accepts email and password
  - Calls UserService.authenticate()
  - Returns 200 OK with UserResponse + JWT token in Set-Cookie header
  - Returns 401 "Invalid credentials" if authentication fails (generic message for security)

- [x] T027 [US1] Create POST /auth/signout endpoint in `backend/src/api/v1/auth.py`:
  - Clears JWT cookie (Set-Cookie: jwt=; Max-Age=0;)
  - Returns 200 OK with empty data
  - Returns 401 if no valid JWT provided

- [x] T028 [US1] [P] Wire up auth routes in `backend/src/api/v1/routers.py` and include in FastAPI app in `backend/src/main.py`

### Backend: Authentication Tests

- [x] T029 [US1] Create auth integration tests in `backend/tests/integration/test_auth_flow.py`:
  - Test signup with valid email/password → 201 Created, user in DB, JWT issued
  - Test signup with existing email → 400 Bad Request
  - Test signup with weak password (<8 chars) → 400 Bad Request
  - Test signin with correct credentials → 200 OK, JWT issued
  - Test signin with wrong password → 401 Unauthorized
  - Test signin with non-existent email → 401 Unauthorized
  - Test signout clears JWT cookie → 200 OK

### Frontend: Authentication UI & Integration

- [x] T030 [US1] Create Better Auth setup in `frontend/src/lib/auth.ts`:
  - Initialize Better Auth client with JWT plugin enabled
  - Configure API endpoint (backend /auth/*)
  - Setup JWT secret sharing with backend

- [x] T031 [US1] [P] Create signup form component in `frontend/src/components/AuthForm.tsx`:
  - Email input with validation
  - Password input with strength indicator (min 8 chars)
  - Name input (optional)
  - Submit button
  - Error display
  - Link to signin page

- [x] T032 [US1] [P] Create signin form component in `frontend/src/components/AuthForm.tsx` (same component, variant for signin):
  - Email input
  - Password input
  - "Remember me" checkbox (optional for MVP)
  - Submit button
  - Error display
  - Link to signup page

- [x] T033 [US1] [P] Create signup page in `frontend/src/app/auth/signup/page.tsx`:
  - Render AuthForm in signup mode
  - Redirect to dashboard on successful signup

- [x] T034 [US1] [P] Create signin page in `frontend/src/app/auth/signin/page.tsx`:
  - Render AuthForm in signin mode
  - Redirect to dashboard on successful signin

- [x] T035 [US1] [P] Create authenticated layout in `frontend/src/app/dashboard/layout.tsx`:
  - Render header with user name and "Sign Out" button
  - Protect routes: redirect to signin if no JWT

- [x] T036 [US1] [P] Create dashboard page in `frontend/src/app/dashboard/page.tsx`:
  - Display message "Authenticated as {user.email}"
  - Verify JWT is being sent in Authorization header to protected endpoint

- [x] T037 [US1] [P] Create API client wrapper in `frontend/src/lib/api-client.ts`:
  - Fetch wrapper that attaches JWT from cookie to Authorization header
  - Handle 401 errors → redirect to signin
  - Handle 403 errors → display "Access Denied"

### Frontend: Authentication Tests

- [x] T038 [US1] Create auth workflow tests in `frontend/tests/integration/workflows/auth.test.ts`:
  - Test signup form submission → POST /auth/signup called
  - Test signin form submission → POST /auth/signin called
  - Test successful signin redirects to dashboard
  - Test signout clears session and redirects to signin

**Acceptance Criteria**:
- [ ] User can signup with email, password, name
- [ ] User receives JWT token in httpOnly cookie
- [ ] User can signin with email and password
- [ ] JWT is automatically sent with subsequent requests
- [ ] User can signout and session is terminated
- [ ] Cannot access dashboard without signin (redirects to signin)

---

## Phase 4: Create & View Tasks (Priority: P1)

**Purpose**: Implement task creation and list display. Independent test: signup → signin → create task → view in list.

**User Story Goal**: Users can create tasks with title/description and view all their tasks in a list.

**Independent Test**: Login → click "Add Task" → enter title → task appears in list

### Backend: Task Service & Endpoints

- [x] T039 [US2] Create TaskService in `backend/src/services/task_service.py` with:
  - create_task(user_id, title, description) → validates title (required, max 500), validates description (max 5000), creates Task in DB, returns created Task
  - list_tasks_for_user(user_id, skip=0, limit=20) → returns tasks ordered by created_at DESC (paginated)
  - get_task(task_id, user_id) → returns task or raises 404, verifies user_id ownership before returning
  - All methods verify user_id ownership (raise 403 if mismatch)

- [x] T040 [US2] Create POST /api/v1/users/{user_id}/tasks endpoint in `backend/src/api/v1/tasks.py`:
  - Requires JWT (use get_current_user dependency)
  - Verifies current_user.id == user_id (raise 403 if mismatch)
  - Accepts TaskCreate (title, description)
  - Validates title required and max 500 chars, description max 5000
  - Calls TaskService.create_task()
  - Returns 201 Created with TaskResponse
  - Returns 400 if validation fails, 403 if user_id mismatch

- [x] T041 [US2] [P] Create GET /api/v1/users/{user_id}/tasks endpoint in `backend/src/api/v1/tasks.py`:
  - Requires JWT
  - Verifies current_user.id == user_id (raise 403 if mismatch)
  - Accepts query params: skip (default 0), limit (default 20, max 100)
  - Calls TaskService.list_tasks_for_user()
  - Returns 200 OK with array of TaskResponse in data field + pagination meta
  - Returns 403 if user_id mismatch

- [x] T042 [US2] [P] Create GET /api/v1/users/{user_id}/tasks/{task_id} endpoint in `backend/src/api/v1/tasks.py`:
  - Requires JWT
  - Verifies current_user.id == user_id (raise 403 if mismatch)
  - Calls TaskService.get_task()
  - Returns 200 OK with single TaskResponse
  - Returns 403 if user_id mismatch, 404 if task doesn't exist

- [x] T043 [US2] [P] Wire up task routes in `backend/src/api/v1/routers.py` and include in FastAPI app

### Backend: Task CRUD Tests

- [x] T044 [US2] Create task CRUD tests in `backend/tests/integration/test_task_crud.py`:
  - Test POST /api/v1/users/{user_id}/tasks with valid title → 201 Created
  - Test POST with missing title → 400 Bad Request
  - Test POST with title > 500 chars → 400 Bad Request
  - Test GET /api/v1/users/{user_id}/tasks → 200 OK, returns task list ordered by created_at DESC
  - Test GET /api/v1/users/{user_id}/tasks/{task_id} → 200 OK, returns single task
  - Test GET non-existent task → 404 Not Found
  - Test without JWT → 401 Unauthorized
  - Test with expired JWT → 401 Unauthorized

### Backend: Multi-User Isolation Tests

- [x] T045 [US2] Create isolation tests in `backend/tests/integration/test_isolation.py`:
  - Test User A cannot GET User B's task list (user_id mismatch) → 403 Forbidden
  - Test User A cannot GET User B's specific task → 403 Forbidden
  - Test User A POST to User B's endpoint → 403 Forbidden
  - Verify tasks created by User A are invisible to User B's list query

### Frontend: Task Management UI

- [x] T046 [US2] Create TaskForm component in `frontend/src/components/TaskForm.tsx`:
  - Title input (required, placeholder "Task title")
  - Description input (optional, placeholder "Add details...")
  - Submit button ("Create Task" or "Update Task" based on mode)
  - Validation feedback (title required, max lengths)
  - Cancel button (if edit mode)

- [x] T047 [US2] [P] Create TaskList component in `frontend/src/components/TaskList.tsx`:
  - Display list of tasks
  - Each task shows: title, description (truncated), created_at formatted
  - Edit and delete buttons for each task
  - "Add Task" button above list
  - Empty state message "No tasks yet. Create one to get started!"
  - Pagination controls if total > 20 tasks

- [x] T048 [US2] [P] Create TaskItem component in `frontend/src/components/TaskItem.tsx`:
  - Display single task: title, description
  - Edit button → opens edit form or navigates to edit page
  - Delete button → opens delete confirmation dialog
  - Completion checkbox (for US3)
  - Visual styling for truncated text

- [x] T049 [US2] [P] Create dashboard task list page in `frontend/src/app/dashboard/page.tsx`:
  - Render TaskList component
  - Fetch tasks from GET /api/v1/users/{user_id}/tasks on mount
  - Handle loading state ("Loading tasks...")
  - Handle error state ("Failed to load tasks. Please try again.")
  - Render TaskForm in modal or separate form section for creating new task

- [x] T050 [US2] [P] Create useTasks hook in `frontend/src/hooks/useTasks.ts`:
  - useState: tasks (array), loading (bool), error (string)
  - useEffect: fetch tasks on mount
  - fetchTasks() → GET /api/v1/users/{user_id}/tasks, set tasks state
  - createTask(title, description) → POST /api/v1/users/{user_id}/tasks, refresh tasks
  - Error handling: catch errors, set error state, handle 403 (access denied)

- [x] T051 [US2] [P] Create API client methods in `frontend/src/lib/api-client.ts`:
  - GET /api/v1/users/{user_id}/tasks (with pagination)
  - POST /api/v1/users/{user_id}/tasks (create)
  - GET /api/v1/users/{user_id}/tasks/{task_id} (detail)
  - All methods attach JWT, handle errors (401 → redirect signin, 403 → show access denied)

### Frontend: Task CRUD Tests

- [x] T052 [US2] Create task component tests in `frontend/tests/unit/components/TaskForm.test.ts`:
  - Test form renders with title and description inputs
  - Test submit button calls onSubmit with form data
  - Test validation: empty title shows error
  - Test cancel button closes form

- [x] T053 [US2] [P] Create task integration tests in `frontend/tests/integration/workflows/task-crud.test.ts`:
  - Test create task: fill form → submit → task appears in list
  - Test fetch task list on dashboard load
  - Test error handling (403 access denied, 404 not found)

**Acceptance Criteria**:
- [ ] Authenticated user can create task with title and optional description
- [ ] Created task immediately appears in task list
- [ ] Task list is paginated (20 per page)
- [ ] User cannot create task without title
- [ ] User A cannot see User B's tasks
- [ ] Tasks are persisted to database and survive page refresh

---

## Phase 5: Mark Complete, Edit, Delete Tasks (Priority: P2-P3)

**Purpose**: Implement task completion, editing, and deletion. These three features are independent and can be developed in parallel.

### US3: Mark Tasks Complete (Priority: P2)

#### Backend: Completion Endpoint

- [x] T054 [US3] Create PUT /api/v1/users/{user_id}/tasks/{task_id} endpoint in `backend/src/api/v1/tasks.py`:
  - Requires JWT
  - Verifies current_user.id == user_id (raise 403)
  - Accepts TaskUpdate (title, description, completed) - all optional
  - Updates task fields provided, sets updated_at
  - Calls TaskService.update_task()
  - Returns 200 OK with updated TaskResponse
  - Returns 403 if user_id mismatch, 404 if task doesn't exist

- [x] T055 [US3] Extend TaskService with update_task() method: accepts task_id, user_id, updated fields

- [x] T056 [US3] [P] Create task update tests in `backend/tests/integration/test_task_crud.py`:
  - Test PUT with completed: true → 200 OK, task marked complete
  - Test PUT with completed: false → 200 OK, task marked incomplete
  - Test PUT with new title → 200 OK, title updated
  - Test PUT without title (but other fields provided) → 200 OK
  - Test PUT with empty title when updating other fields → 400 Bad Request (title required if provided)

#### Frontend: Completion UI

- [x] T057 [US3] Extend TaskItem component with completion checkbox:
  - Checkbox toggles task.completed state
  - On change: call API updateTask(task_id, { completed: !completed })
  - Visual feedback: strikethrough text when completed, normal style when incomplete
  - Show loading state during API call

- [x] T058 [US3] [P] Extend useTasks hook with updateTask() method:
  - PUT /api/v1/users/{user_id}/tasks/{task_id} with partial update
  - Refresh tasks after update
  - Handle errors

- [x] T059 [US3] [P] Create task completion tests in `frontend/tests/integration/workflows/task-crud.test.ts`:
  - Test click checkbox → task marked complete → strikethrough appears
  - Test click completed task → reverts to incomplete → strikethrough removed

**Acceptance Criteria for US3**:
- [x] Authenticated user can toggle task completion status
- [x] Completed tasks display visual indicator (strikethrough)
- [x] Completion state persists in database
- [x] User A cannot mark User B's task as complete

---

### US4: Edit Tasks (Priority: P2)

#### Backend: Edit Endpoint (Shared with US3)

- [x] T060 [US4] Extend PUT endpoint from US3 to support title and description updates
  - Validation: title required if provided, max 500 chars; description max 5000 chars
  - Tests already covered in T056

#### Frontend: Edit UI

- [x] T061 [US4] Create edit task page in `frontend/src/app/dashboard/tasks/[id]/edit/page.tsx`:
  - Fetch task details (GET /api/v1/users/{user_id}/tasks/{task_id})
  - Render TaskForm in edit mode (pre-filled with task data)
  - Submit calls updateTask() with new title/description
  - Cancel button returns to dashboard
  - Handle 404 (task not found) and 403 (access denied) errors

- [x] T062 [US4] [P] Extend TaskForm component to support edit mode:
  - Accept task object as prop (for pre-filling)
  - Change submit button text: "Create Task" → "Update Task" in edit mode
  - Pre-fill title and description fields with existing values

- [x] T063 [US4] [P] Extend TaskItem component with edit button:
  - Click edit → navigate to /dashboard/tasks/{task_id}/edit OR open inline edit modal
  - Load task details if not already in state

- [x] T064 [US4] [P] Extend useTasks hook:
  - getTaskDetail(task_id) → GET /api/v1/users/{user_id}/tasks/{task_id}
  - updateTask() method already exists from US3

- [x] T065 [US4] [P] Create edit workflow tests in `frontend/tests/integration/workflows/task-crud.test.ts`:
  - Test click edit → form populated with existing data → update title → save → list updated
  - Test empty title on update → validation error

**Acceptance Criteria for US4**:
- [x] Authenticated user can edit task title and description
- [x] Edit form pre-fills with current values
- [x] Updated values persist in database
- [x] User A cannot edit User B's task

---

### US5: Delete Tasks (Priority: P3)

#### Backend: Delete Endpoint

- [x] T066 [US5] Create DELETE /api/v1/users/{user_id}/tasks/{task_id} endpoint in `backend/src/api/v1/tasks.py`:
  - Requires JWT
  - Verifies current_user.id == user_id (raise 403)
  - Calls TaskService.delete_task()
  - Returns 204 No Content (no body)
  - Returns 403 if user_id mismatch, 404 if task doesn't exist

- [x] T067 [US5] Extend TaskService with delete_task() method

- [x] T068 [US5] [P] Create delete endpoint tests in `backend/tests/integration/test_task_crud.py`:
  - Test DELETE valid task → 204 No Content, task removed from DB
  - Test DELETE non-existent task → 404 Not Found
  - Test DELETE another user's task → 403 Forbidden

#### Frontend: Delete UI

- [x] T069 [US5] Create DeleteConfirm component in `frontend/src/components/DeleteConfirm.tsx`:
  - Modal/dialog with message: "Are you sure? This action cannot be undone."
  - Cancel button (close dialog, preserve task)
  - Delete button (confirm deletion)
  - Show loading state during API call

- [x] T070 [US5] [P] Extend TaskItem component with delete button:
  - Click delete → open DeleteConfirm modal
  - Confirm → call deleteTask(task_id)
  - Modal closes, task removed from list

- [x] T071 [US5] [P] Extend useTasks hook with deleteTask() method:
  - DELETE /api/v1/users/{user_id}/tasks/{task_id}
  - Refresh tasks after delete
  - Handle errors

- [x] T072 [US5] [P] Create delete workflow tests in `frontend/tests/integration/workflows/task-crud.test.ts`:
  - Test click delete → confirmation dialog appears → click Cancel → task preserved
  - Test click delete → confirmation dialog appears → click Delete → task removed from list

**Acceptance Criteria for US5**:
- [x] Authenticated user can delete task
- [x] Delete confirmation prevents accidental deletion
- [x] Deleted task removed from database
- [x] User A cannot delete User B's task

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Responsive design, loading states, error handling, pagination, accessibility.

### Responsiveness & Mobile UX

- [ ] T073 Test signup/signin forms on mobile viewport (375x667) → no horizontal scrolling
- [ ] T074 [P] Test dashboard task list on mobile → responsive layout, buttons usable on touch
- [ ] T075 [P] Test task form on mobile → inputs are appropriately sized
- [ ] T076 [P] Add responsive CSS/Tailwind classes to all components (mobile-first approach)

### Loading & Error States

- [ ] T077 Create Loading component in `frontend/src/components/Loading.tsx` → spinner
- [ ] T078 [P] Add loading state to task list page: "Loading tasks..." while fetching
- [ ] T079 [P] Add error state to task list page: "Failed to load tasks. Retry?" with error message
- [ ] T080 [P] Add error messages to auth forms: display API errors (email exists, invalid credentials, etc.)
- [ ] T081 [P] Add error boundary in `frontend/src/app/error.tsx` to catch unhandled exceptions

### Pagination

- [ ] T082 Implement pagination in task list: display page controls if total > 20 tasks
- [ ] T083 [P] Add prev/next button handlers in TaskList: fetch next/prev page of tasks

### Token Expiration & Refresh

- [ ] T084 Implement token refresh flow: if access token expires (401), request refresh token
- [ ] T085 [P] Redirect to signin if refresh token also expired: "Session expired. Please log in again."

### Accessibility

- [ ] T086 Add ARIA labels to form inputs (email, password, title, description)
- [ ] T087 [P] Add keyboard navigation: Tab through forms, Enter to submit, Escape to close modals
- [ ] T088 [P] Test with screen reader: task list, buttons, error messages readable

### Documentation

- [ ] T089 Update `specs/001-full-stack-todo-app/quickstart.md` with any new setup steps discovered
- [ ] T090 [P] Create `backend/README.md` with local dev instructions, migration guide, API docs link
- [ ] T091 [P] Create `frontend/README.md` with local dev instructions, component overview

---

## Task Summary

| Phase | Count | Purpose |
|-------|-------|---------|
| **Phase 1: Setup** | 9 | Project initialization, dependencies, configuration |
| **Phase 2: Foundational** | 14 | Database, ORM, schemas, security utilities |
| **Phase 3: US1 (Auth)** | 15 | Signup, signin, signout + tests |
| **Phase 4: US2 (Create/View)** | 14 | Task creation, listing, API integration + tests |
| **Phase 5: US3-5 (Complete/Edit/Delete)** | 23 | Task state management + tests (parallel) |
| **Phase 6: Polish** | 18 | Responsiveness, loading, errors, accessibility, docs |
| **TOTAL** | **93** | Full-stack implementation |

---

## Parallel Execution Opportunities

### Phase 3 (Auth) - Sequential (Frontend depends on Backend)
1. T024-T028: Backend service + endpoints
2. T029: Backend tests
3. T030-T037: Frontend UI + integration
4. T038: Frontend tests

### Phase 4 (Create/View) - Mostly Parallel
- **Backend** (T039-T043): Can run in parallel with frontend setup
  - T039-T041: Service + GET/POST endpoints (parallel)
  - T042-T043: GET detail + wire routes (parallel)
- **Frontend** (T046-T051): Can run in parallel with backend (T031-T040 can run ~simultaneously with backend)
  - T046-T048: Components (parallel)
  - T049-T051: Pages + hooks (parallel)

### Phase 5 (Complete/Edit/Delete) - Fully Parallel
- **US3 Backend** (T054-T056): Parallel with US4/US5 backend
- **US3 Frontend** (T057-T059): Parallel with US4/US5 frontend
- **US4 & US5**: Completely independent, all tasks can run in parallel

### Phase 6 (Polish) - Mostly Parallel
All 18 tasks can run in parallel (different components, no dependencies)

---

## MVP Scope (Recommended for Phase II)

**Minimum Viable Product**: Phases 1-4 (93 - 23 - 18 = **52 tasks**)

Delivers:
- ✅ User registration & signin (US1)
- ✅ Create & view tasks (US2)
- ✅ Full-stack architecture validated
- ✅ Multi-user isolation verified
- ✅ JWT authentication working end-to-end

Can be extended with US3-5 (mark complete, edit, delete) in Phase II continuation.

---

## Implementation Strategy

1. **Phase 1**: Execute sequentially (4-6 hours)
   - Setup frontend and backend projects
   - Configure environment

2. **Phase 2**: Execute sequentially (6-8 hours)
   - Database schema first (blocks all other phases)
   - ORM models + migrations
   - Security utilities

3. **Phase 3**: Execute sequentially (8-12 hours)
   - Backend auth (blocks frontend auth)
   - Frontend auth
   - Integration tests

4. **Phase 4**: Execute with parallelization (8-12 hours)
   - Backend task endpoints (T039-T043) in parallel with Frontend setup
   - Frontend components once backend endpoints defined

5. **Phase 5**: Execute fully in parallel (12-16 hours)
   - All three features (complete, edit, delete) independent
   - Frontend and backend for each feature can run in parallel

6. **Phase 6**: Execute in parallel (6-10 hours)
   - Styling, accessibility, documentation can run independently

**Estimated Total**: 44-64 hours (depending on agent parallelization)

---

## Success Validation

After each phase, validate against spec acceptance criteria:

**Phase 3 Complete**:
- ✅ Signup form works end-to-end
- ✅ Signin form works end-to-end
- ✅ JWT tokens issued and validated
- ✅ Signout clears session

**Phase 4 Complete**:
- ✅ Create task works end-to-end
- ✅ View task list works
- ✅ Multi-user isolation enforced
- ✅ Data persists

**Phase 5 Complete**:
- ✅ Toggle completion works
- ✅ Edit task works
- ✅ Delete task works with confirmation

**Phase 6 Complete**:
- ✅ UI responsive on mobile (375x667) and desktop (1920x1080)
- ✅ All errors handled gracefully
- ✅ Token expiration handled
- ✅ Accessibility compliance

---

**Status**: ✅ READY FOR IMPLEMENTATION
**Next Step**: Execute tasks via Claude Code agents (frontend-skill, fastapi-backend-api, auth-secure-handler, neon-db-ops)
