# Implementation Plan: Frontend Application — Todo Web Interface

**Branch**: `003-frontend-ui` | **Date**: 2026-02-10 | **Spec**: [spec.md](spec.md)
**Input**: Building a responsive, authenticated task management interface using Next.js 16 integrated with secured FastAPI APIs

---

## Summary

This plan implements a comprehensive, responsive frontend for the authenticated todo application using Next.js 16 (App Router) integrated with the FastAPI backend (Spec 002: JWT Authentication & API Security Layer). The implementation focuses on user experience, security, and responsive design across all devices, with three core components:

1. **Authentication UI**: Signup/signin pages with form validation, JWT token capture, and secure cookie storage
2. **Task Management Dashboard**: Paginated task list with CRUD operations, real-time UI updates, and optimistic updates
3. **Responsive Layout**: Mobile-first design with breakpoints for tablet and desktop, touch-friendly interactions

---

## Technical Context

**Language/Version**: TypeScript + React 18+ (frontend only) | Node.js 18+

**Primary Dependencies**:
- Frontend: Next.js 16+, React 18+, TailwindCSS (responsive styling), React Hook Form (form management), Fetch API (HTTP client)
- Testing: Jest/Vitest (unit tests), React Testing Library (component tests)
- Development: TypeScript, ESLint, Prettier

**Storage**: JWT tokens in httpOnly cookies (no localStorage), client-side React state for UI

**Target Platform**: Web (localhost:3000 frontend, communicates with localhost:8000 backend)

**Project Type**: Single-Page Application (SPA) with client-side routing via Next.js App Router

**Performance Goals**:
- Signup/signin form: < 3 seconds to submit (includes validation + network)
- Dashboard load: < 2 seconds to display first tasks
- Task create/update/delete: < 1 second UI update after API response
- Mobile render: < 1 second on 3G connection

**Constraints**:
- Client-only (no server-side rendering of user tasks; static pages only)
- No direct database access (all data via API)
- Protected routes must redirect unauthenticated users to signin
- JWT token must be attached to all protected API requests
- No localStorage for tokens (httpOnly cookies only)
- Component-based architecture (React best practices)

**Scale/Scope**:
- Single authenticated user at a time (no multi-session state)
- Support 10,000+ tasks with pagination (20 per page)
- Responsive design: mobile (375px), tablet (768px), desktop (1920px)
- 3 main pages: signup, signin, dashboard
- 10+ reusable components

---

## Constitution Check

**Gates to Verify**:
- [x] Spec-Driven Development: Feature originates from written spec (spec.md complete)
- [x] Stack Enforcement: Next.js 16+ (App Router), TypeScript, TailwindCSS
- [x] Secure-by-Design Authentication: JWT token in httpOnly cookie, attached to all API requests
- [x] Multi-User Data Isolation: Frontend displays only authenticated user's tasks (backend enforces user_id validation)
- [x] API-First Design: Frontend consumes only REST APIs (no database access)
- [x] Code Generation via Claude Code: All code generated via frontend-skill agent
- [x] Prompt History & Traceability: Every major change documented in PHR

**Status**: ✅ All gates will be satisfied during implementation
- ✅ No XSS vulnerabilities: JWT in httpOnly cookie, Fetch API prevents injection
- ✅ No hardcoded secrets: JWT stored in secure cookie, backend secret in .env
- ✅ Data isolation: Frontend only displays authenticated user's tasks (backend enforces per-user filtering)
- ✅ Error handling: Graceful error messages without technical details
- ✅ API contracts: REST endpoints with Bearer token authorization

---

## Project Structure

### Documentation (this feature)

```text
specs/003-frontend-ui/
├── spec.md                  ✅ User scenarios & requirements
├── plan.md                  ← This file
├── research.md              (Phase 0 - for unknowns, if needed)
├── data-model.md            (Phase 1 - entity/component definitions)
├── quickstart.md            (Phase 1 - getting started guide)
├── contracts/               (Phase 1 - API request/response schemas)
│   ├── auth-contracts.md
│   └── task-contracts.md
├── checklists/
│   └── requirements.md       ✅ Quality validation (PASSED)
└── tasks.md                 (Phase 2 - implementation tasks)
```

### Source Code (repository structure - EXISTING + NEW)

```text
frontend/
├── src/
│   ├── pages/               ← Next.js App Router routes
│   │   ├── page.tsx         ← Root landing page (redirect to signin if no token)
│   │   ├── signup/
│   │   │   └── page.tsx     ← Signup form (POST to /api/v1/auth/signup)
│   │   ├── signin/
│   │   │   └── page.tsx     ← Signin form (POST to /api/v1/auth/signin)
│   │   ├── dashboard/
│   │   │   └── page.tsx     ← Protected dashboard (list, create, edit, delete tasks)
│   │   └── layout.tsx       ← Root layout with auth provider, header/nav
│   │
│   ├── components/          ← Reusable React components
│   │   ├── auth/
│   │   │   ├── SignupForm.tsx       ← Form component with validation
│   │   │   ├── SigninForm.tsx       ← Form component with validation
│   │   │   └── LogoutButton.tsx     ← Button to trigger logout
│   │   ├── tasks/
│   │   │   ├── TaskList.tsx         ← Paginated list of tasks
│   │   │   ├── TaskCard.tsx         ← Individual task display
│   │   │   ├── TaskForm.tsx         ← Create/edit task form
│   │   │   └── TaskActions.tsx      ← Buttons for edit/delete/complete
│   │   ├── ui/
│   │   │   ├── Button.tsx           ← Reusable button
│   │   │   ├── Form.tsx             ← Reusable form wrapper
│   │   │   ├── Modal.tsx            ← Modal dialog (confirm delete)
│   │   │   ├── LoadingSpinner.tsx   ← Loading indicator
│   │   │   ├── ErrorAlert.tsx       ← Error message display
│   │   │   └── EmptyState.tsx       ← Empty state for no tasks
│   │   └── common/
│   │       ├── Header.tsx           ← Top navigation with logout button
│   │       └── Footer.tsx           ← Footer
│   │
│   ├── lib/                 ← Utilities & helpers
│   │   ├── api.ts           ← Fetch wrapper with JWT token attachment
│   │   ├── auth.ts          ← Auth helpers (isAuthenticated, getToken, clearToken)
│   │   ├── storage.ts       ← Cookie/localStorage utilities
│   │   └── validation.ts    ← Form validation utilities
│   │
│   ├── hooks/               ← Custom React hooks
│   │   ├── useAuth.ts       ← Auth context hook
│   │   ├── useTask.ts       ← Task list/CRUD hook
│   │   └── useForm.ts       ← Form state management hook
│   │
│   ├── types/               ← TypeScript type definitions
│   │   ├── auth.ts          ← User, JWT, auth response types
│   │   ├── task.ts          ← Task type definitions
│   │   └── api.ts           ← API request/response types
│   │
│   ├── styles/              ← Global styles
│   │   └── globals.css      ← TailwindCSS imports, global styles
│   │
│   └── middleware.ts        ← Route protection middleware (client-side redirect)
│
├── public/                  ← Static assets
├── package.json             ✅ Dependencies defined
├── tsconfig.json            ← TypeScript configuration
├── tailwind.config.js       ← TailwindCSS configuration
├── next.config.js           ← Next.js configuration
└── .env.local               ← Environment variables (NEXT_PUBLIC_API_URL)
```

**Structure Decision**: Single-page app with Next.js App Router, TypeScript for type safety, TailwindCSS for responsive design. Components are organized by feature (auth, tasks, ui) for clarity and maintainability. All API communication goes through a centralized fetch wrapper (`lib/api.ts`) to ensure JWT tokens are attached consistently.

---

## Implementation Phases

### Phase 0: Research & Clarification

**Purpose**: Resolve technical unknowns before design

**Research Tasks** (all clear - no clarifications needed):
1. ✅ Next.js 16 App Router routing patterns
2. ✅ React Hook Form integration with TypeScript
3. ✅ TailwindCSS responsive breakpoints (mobile-first)
4. ✅ Fetch API with custom headers (Authorization: Bearer)
5. ✅ Cookie access in Next.js (document.cookie vs API)
6. ✅ Protected routes in Next.js App Router

**Output**: No `research.md` needed (all decisions documented in this plan)

**Rationale**: Spec clearly defines requirements, backend (Spec 002) is complete, and tech stack is fixed by constitution.

---

### Phase 1: Design & Contracts

#### 1a. Component Data Model (`data-model.md`)

**Component Hierarchy**:
```
App (Root Layout)
├── Header (Navigation, Logout button)
├── Router
│   ├── Page (/) → redirect to signin if no token, else to dashboard
│   ├── SignupPage
│   │   └── SignupForm
│   ├── SigninPage
│   │   └── SigninForm
│   └── DashboardPage (Protected)
│       ├── TaskList
│       │   ├── TaskCard (each item)
│       │   │   └── TaskActions (edit/delete/complete)
│       │   └── Pagination
│       ├── TaskForm (Create/Edit Modal)
│       └── Footer
└── Error Boundary
```

**Key Entities** (React component state):

**User**:
- `id: UUID` - User identifier
- `email: string` - User email
- `name: string` - Display name
- `isAuthenticated: boolean` - Derived from token presence

**Task**:
- `id: UUID` - Task identifier
- `title: string` - Required, non-empty
- `description?: string` - Optional
- `completed: boolean` - Completion status (default false)
- `createdAt: ISO8601` - Timestamp
- `updatedAt: ISO8601` - Timestamp

**JWT Token** (stored in httpOnly cookie):
- `sub: UUID` - User ID (subject)
- `email: string` - User email
- `iat: number` - Issued at (unix timestamp)
- `exp: number` - Expiration (unix timestamp, 15 min from iat)
- `iss: string` - Issuer ("todo-app")
- `aud: string` - Audience ("todo-app-users")

**UI State**:
- Loading: boolean (while fetching data)
- Error: null | ErrorMessage (user-friendly error)
- Tasks: Task[] (paginated list)
- CurrentPage: number (pagination state)
- SelectedTask?: Task (currently editing task)

---

#### 1b. API Contracts (`contracts/auth-contracts.md`)

**Signup Request/Response**:
```http
POST /api/v1/auth/signup
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123",
  "name": "John Doe"
}

--- Response (201 Created) ---
{
  "data": {
    "id": "uuid-string",
    "email": "user@example.com",
    "name": "John Doe",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expiresIn": 900
  },
  "meta": {
    "timestamp": "2026-02-10T12:00:00Z",
    "request_id": "req-abc123"
  },
  "error": null
}

--- Errors ---
400 Bad Request:
{
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid email format",
    "details": { "email": ["Invalid email format"] }
  }
}

409 Conflict (email already registered):
{
  "data": null,
  "error": {
    "code": "EMAIL_EXISTS",
    "message": "Email already registered",
    "details": null
  }
}
```

**Signin Request/Response**:
```http
POST /api/v1/auth/signin
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123"
}

--- Response (200 OK) ---
{
  "data": {
    "id": "uuid-string",
    "email": "user@example.com",
    "name": "John Doe",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expiresIn": 900
  },
  "meta": { ... },
  "error": null
}

--- Error (401 Unauthorized) ---
{
  "data": null,
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Invalid email or password",
    "details": null
  }
}
```

**Task List Request/Response**:
```http
GET /api/v1/users/{user_id}/tasks?skip=0&limit=20
Authorization: Bearer <jwt_token>

--- Response (200 OK) ---
{
  "data": {
    "items": [
      {
        "id": "task-uuid",
        "user_id": "user-uuid",
        "title": "Buy groceries",
        "description": "Milk, eggs, bread",
        "completed": false,
        "createdAt": "2026-02-10T10:00:00Z",
        "updatedAt": "2026-02-10T10:00:00Z"
      }
    ],
    "total": 5,
    "skip": 0,
    "limit": 20
  },
  "meta": { ... },
  "error": null
}

--- Error (401 Unauthorized - token missing or expired) ---
{
  "data": null,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Missing or invalid authentication token",
    "details": null
  }
}

--- Error (403 Forbidden - wrong user) ---
{
  "data": null,
  "error": {
    "code": "FORBIDDEN",
    "message": "You don't have permission to access this resource",
    "details": null
  }
}
```

---

#### 1c. Task Endpoint Contracts (`contracts/task-contracts.md`)

**Create Task**:
```http
POST /api/v1/users/{user_id}/tasks
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}

--- Response (201 Created) ---
{
  "data": {
    "id": "task-uuid",
    "user_id": "user-uuid",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "createdAt": "2026-02-10T10:00:00Z",
    "updatedAt": "2026-02-10T10:00:00Z"
  },
  "meta": { ... },
  "error": null
}
```

**Update Task**:
```http
PUT /api/v1/users/{user_id}/tasks/{task_id}
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "title": "Updated title",
  "description": "Updated description",
  "completed": true
}

--- Response (200 OK) ---
{ /* updated task */ }
```

**Delete Task**:
```http
DELETE /api/v1/users/{user_id}/tasks/{task_id}
Authorization: Bearer <jwt_token>

--- Response (204 No Content) ---
(empty body)
```

---

#### 1d. Frontend API Client (`lib/api.ts`)

**Key functions**:
```typescript
// Fetch wrapper that attaches JWT token automatically
async function apiCall<T>(
  endpoint: string,
  options?: RequestInit & { requiresAuth?: boolean }
): Promise<T>

// Specific helpers
async function signup(email: string, password: string, name: string): Promise<AuthResponse>
async function signin(email: string, password: string): Promise<AuthResponse>
async function getTasks(userId: string, skip: number, limit: number): Promise<TaskListResponse>
async function createTask(userId: string, title: string, description?: string): Promise<TaskResponse>
async function updateTask(userId: string, taskId: string, updates: Partial<Task>): Promise<TaskResponse>
async function deleteTask(userId: string, taskId: string): Promise<void>
```

**Implementation details**:
- Automatically reads JWT token from cookie
- Adds Authorization header: `Authorization: Bearer <token>`
- Handles 401 Unauthorized → redirects to signin
- Handles 403 Forbidden → shows error "You don't have permission"
- Implements retry logic for network failures
- Returns parsed JSON responses

---

#### 1e. Protected Routes & Middleware

**Route Protection** (client-side redirect):
```typescript
// middleware.ts (or components/auth/ProtectedRoute.tsx)
if (!isAuthenticated && currentRoute.requiresAuth) {
  redirect('/signin')
}

// Routes requiring authentication:
- /dashboard/* (all dashboard sub-routes)

// Routes accessible without auth:
- / (root, redirects to signin or dashboard)
- /signup
- /signin
```

---

#### 1f. Quick Start Guide (`quickstart.md`)

```markdown
# Getting Started with Frontend Todo Application

## Prerequisites

- Node.js 18+ and npm/pnpm
- Backend running on http://localhost:8000
- JWT_SECRET configured on backend (shared with frontend if needed)

## Setup

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Create .env.local:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

3. Start development server:
   ```bash
   npm run dev
   ```

4. Open http://localhost:3000

## Testing Authentication Flow

1. Visit http://localhost:3000 → redirects to /signin
2. Click "Sign Up"
3. Fill in email, password (8+ chars, uppercase, lowercase, number), name
4. Click "Create Account"
5. JWT token stored in cookie, redirected to dashboard
6. Dashboard shows "No tasks yet"
7. Click "Create Task" and add a task
8. Task appears in list immediately
9. Click "Sign Out" → redirected to /signin
10. Refresh page → still on signin (token cleared)

## Structure

- `src/pages/` — Next.js App Router routes
- `src/components/` — Reusable React components
- `src/lib/` — Utilities (API client, auth, validation)
- `src/hooks/` — Custom React hooks
- `src/types/` — TypeScript type definitions
- `tailwind.config.js` — Responsive design breakpoints

## API Integration

All API calls go through `lib/api.ts` which automatically:
- Reads JWT token from httpOnly cookie
- Adds Authorization header
- Handles errors (401, 403, 5xx)
- Redirects to signin on 401
```

---

### Phase 2: Task Generation

**Output**: `tasks.md` (generated by `/sp.tasks` command)

**High-Level Task Groups** (estimated):

1. **Setup & Infrastructure** (1-2 tasks):
   - Initialize Next.js 16 project structure
   - Configure TailwindCSS, TypeScript
   - Set up environment variables

2. **Authentication Pages** (2-3 tasks):
   - Create signup page with form validation
   - Create signin page with form validation
   - Implement logout button and session clearing

3. **API Client** (1 task):
   - Create fetch wrapper (`lib/api.ts`) with JWT token attachment
   - Implement error handling (401, 403, 5xx)
   - Add automatic redirect on 401

4. **Protected Routes & Layout** (1 task):
   - Create root layout with authentication check
   - Implement route protection middleware
   - Add header with navigation

5. **Dashboard & Task Management** (3-4 tasks):
   - Create dashboard page with protected layout
   - Build task list component with pagination
   - Implement create task form (modal)
   - Implement edit task form (modal)
   - Implement task delete with confirmation
   - Implement completion toggle

6. **UI Components** (2-3 tasks):
   - Build reusable form components
   - Create loading indicator, error alert
   - Implement responsive layout components

7. **Responsive Design** (1 task):
   - Configure TailwindCSS breakpoints
   - Test mobile, tablet, desktop views
   - Ensure touch-friendly interactions

8. **Testing & QA** (2 tasks):
   - Unit tests for hooks, utilities
   - Integration tests for auth flow, task CRUD
   - Manual testing across devices

---

## Key Architectural Decisions

### 1. Next.js App Router (not Pages Router)
**Decision**: Use Next.js App Router for routing
**Rationale**:
- Modern routing with better layout composition
- Supports middleware for route protection
- Better TypeScript support
- Aligns with Next.js 16 best practices

**Implementation**:
- Routes defined as `src/pages/[route]/page.tsx`
- Layout nesting for shared UI
- Metadata and error handling

### 2. TypeScript for Type Safety
**Decision**: Use TypeScript throughout frontend
**Rationale**:
- Catch errors at compile-time
- Better IDE support and autocomplete
- Easier refactoring and maintenance
- Aligns with constitution requirements

**Implementation**:
- All `.tsx` and `.ts` files with strict type checking
- Type definitions in `src/types/`
- Interfaces for API requests/responses

### 3. TailwindCSS for Responsive Design
**Decision**: TailwindCSS for styling (utility-first)
**Rationale**:
- Mobile-first responsive design (sm, md, lg, xl breakpoints)
- No runtime CSS-in-JS overhead
- Large ecosystem and documentation
- Easy to customize breakpoints

**Implementation**:
- Responsive classes in JSX
- Breakpoints: sm=640px, md=768px, lg=1024px, xl=1280px
- Custom colors via tailwind.config.js

### 4. Fetch API (not Axios)
**Decision**: Use native Fetch API with custom wrapper
**Rationale**:
- No external dependency (modern browsers have Fetch built-in)
- Simpler to understand and debug
- Reduces bundle size
- Sufficient for this use case

**Implementation**:
- Centralized wrapper in `lib/api.ts`
- Consistent error handling
- Automatic JWT token attachment

### 5. React Context for Auth State (not Redux)
**Decision**: React Context + hooks for authentication state
**Rationale**:
- No external state management needed
- Built into React, no extra dependencies
- Simpler for small-to-medium apps
- Sufficient for this feature scope

**Implementation**:
- `useAuth()` hook for accessing auth state
- Context provider in root layout
- Custom hook for login/logout actions

### 6. Client-Side Route Protection
**Decision**: Redirect unauthenticated users client-side via middleware
**Rationale**:
- Simple to implement with App Router
- Prevents rendering protected content before check
- Can verify token is valid before allowing access

**Implementation**:
- Check token on app initialization
- Middleware redirects to /signin if missing
- Loading state while checking

### 7. HttpOnly Cookies for JWT Storage
**Decision**: Store JWT token in httpOnly cookie (not localStorage)
**Rationale**:
- XSS protection: JavaScript cannot access httpOnly cookies
- Automatic transmission with CORS credentials
- More secure than localStorage

**Implementation**:
- Backend sets cookie in response
- Frontend sends cookie automatically with `credentials: 'include'`
- Logout clears cookie

### 8. Optimistic UI Updates
**Decision**: Update UI immediately after user action, revert on error
**Rationale**:
- Perceived performance improvement
- Better UX: user sees action completed immediately
- Revert logic handles failures gracefully

**Implementation**:
- Update state before API call completes
- Show loading indicator
- Revert and show error if API fails

---

## Security Design

### Authentication Flow
```
User on Page (/)
    ↓ [Check token in cookie]
    ├─ Token exists and valid → redirect to /dashboard
    └─ No token → redirect to /signin

User on /signup
    ↓ [Fill form: email, password, name]
    ↓ [Click "Sign Up"]
    ↓ [Client-side validation: email format, password strength]
    ↓ [POST /api/v1/auth/signup]
    ↓
Backend (FastAPI)
    ├─ Validate email & password
    ├─ Hash password with bcrypt
    ├─ Create user in database
    ├─ Issue JWT token
    └─ Return token + Set-Cookie header

Frontend receives token
    ├─ Cookie stored automatically by browser (httpOnly)
    ├─ Redirect to /dashboard
    └─ Request /api/v1/users/{user_id}/tasks (token sent automatically)

User on /dashboard
    ↓ [Token attached to every API request in Authorization header]
    ↓ [Fetch tasks, create task, update task, delete task]
    ↓ [Backend validates JWT signature + user_id ownership]

User clicks "Sign Out"
    ↓ [Logout button clears token]
    ↓ [Delete cookie or set to empty]
    ↓ [Redirect to /signin]
    ↓ [Subsequent requests rejected with 401 → redirect to signin]
```

### Authorization Flow
```
Frontend API Request
    ├─ Check token in cookie
    ├─ Add Authorization header: "Bearer <token>"
    └─ Send to backend

Backend validates (Spec 002)
    ├─ Extract token from Authorization header
    ├─ Verify JWT signature using JWT_SECRET
    ├─ Check token not expired
    ├─ Extract user_id from token claims
    ├─ Validate user_id matches URL parameter
    ├─ Query tasks WHERE user_id = <authenticated_user_id>
    └─ Return user's tasks only

Frontend displays tasks
    ├─ Show user's tasks in list
    ├─ All edit/delete actions update only user's own tasks
    └─ API prevents cross-user access (403 Forbidden)
```

### Attack Prevention
- **XSS**: Token in httpOnly cookie (not accessible to JavaScript)
- **CSRF**: Bearer token format (not cookie-based automatic transmission; CORS validates origin)
- **Network**: HTTPS in production (enforced by CORS)
- **User Enumeration**: Generic error messages ("Invalid email or password")
- **Token Theft**: httpOnly cookie + Secure flag (browser prevents sending over HTTP)
- **Session Fixation**: Stateless JWT (no server session to fixate)

---

## Testing Strategy

### Unit Tests
- Email validation (format, length)
- Password validation (strength, length)
- Task title validation (required, non-empty)
- Token parsing and extraction
- Error message formatting
- URL construction (user_id, task_id parameters)

### Component Tests (React Testing Library)
- SignupForm: render, fill, submit, validation errors
- SigninForm: render, fill, submit, validation errors
- TaskList: render tasks, pagination, empty state
- TaskCard: render task, edit/delete buttons
- LogoutButton: click → logout → redirect

### Integration Tests
- Full signup flow: form → API → token stored → redirect
- Full signin flow: form → API → token stored → redirect
- Task creation: form → API → list updated
- Task update: edit form → API → list updated
- Task deletion: confirm → API → list updated
- Token expiration: old token → 401 → redirect to signin
- Cross-user prevention: attempt to access other user's task → 403

### E2E Tests (optional, can use Playwright/Cypress)
- User signup, signin, create task, logout workflow
- Responsive layout on mobile, tablet, desktop
- Error scenarios (network timeout, 500 error)

---

## Deployment Considerations

### Environment Variables
```
Development:
NEXT_PUBLIC_API_URL=http://localhost:8000

Production:
NEXT_PUBLIC_API_URL=https://api.example.com
```

### Build & Deployment
- Build: `npm run build` → Next.js produces static files
- Runtime: Node.js server or serverless (Vercel, AWS Lambda)
- CORS: Backend must allow requests from frontend origin
- HTTPS: Required for secure cookie transmission (Secure flag)

### Security Checklist Before Deployment
- [ ] JWT_SECRET is securely configured on backend
- [ ] HTTPS enabled for both frontend and backend
- [ ] CORS configured: frontend origin whitelisted on backend
- [ ] HttpOnly + Secure flags set on cookies
- [ ] No JWT tokens logged or exposed in errors
- [ ] Password validation enforced (8+ chars, uppercase, lowercase, number)
- [ ] API errors return generic messages (no user enumeration)
- [ ] Rate limiting configured on login attempts (backend)
- [ ] Content Security Policy (CSP) headers set
- [ ] Monitoring/logging configured for auth failures

---

## Complexity Justification

**No violations of Constitution Check** - All gates are satisfied:
- ✅ Spec-Driven: Originates from spec.md with 10 user stories
- ✅ Stack Enforcement: Next.js 16, TypeScript, TailwindCSS, Fetch API
- ✅ Secure-by-Design: JWT in httpOnly cookie, attached to all API requests, 401 handling
- ✅ Multi-User Data Isolation: Frontend displays only authenticated user's tasks (backend enforces)
- ✅ API-First: No database access, all data via REST API
- ✅ Code Generation: All code generated via frontend-skill agent
- ✅ Traceability: Every major change documented in PHR

---

## Success Criteria Mapping

| Success Criterion | Implementation Strategy |
|------------------|----------------------|
| Signup < 3min | Form validation optimized, async API calls, network efficient |
| Signin < 2min | Simplified form, quick API response, immediate redirect |
| Dashboard < 2sec | Lazy loading, pagination, optimized API response |
| Create task < 30sec | Simple modal, quick submission, optimistic update |
| 100% protected requests with auth | Centralized API wrapper (lib/api.ts) attaches token |
| 0% horizontal scroll on mobile | TailwindCSS responsive classes, tested on 375px width |
| 48px touch targets on mobile | Button/input size using TailwindCSS (h-12, w-12 = 48px) |
| No tokens in logs/URLs | Only in Authorization header and httpOnly cookie |
| Responsive across devices | TailwindCSS breakpoints: sm, md, lg, xl |
| 100% acceptance scenarios pass | Integration tests cover all user stories |

---

## Next Steps

1. **Phase 0 Complete**: No research needed (all decisions documented)
2. **Phase 1 Complete**: Data model, API contracts, quickstart designed
3. **Phase 2 (Next)**: Run `/sp.tasks` to generate implementation tasks
4. **Phase 3**: Run `/sp.implement` to execute tasks

**Estimated Effort**:
- Design: ✅ Complete (2-3 hours)
- Implementation: ~12-16 hours (forms, components, API integration, responsive design)
- Testing: ~4-6 hours (unit, integration, E2E tests)
- **Total**: ~18-25 hours

**Critical Path**:
1. Authentication setup (JWT wrapper, context) - blocks all other work
2. Signup/signin pages - enables dashboard testing
3. Dashboard & task list - core functionality
4. Edit/delete task - completes CRUD
5. Responsive design - polish for all devices

---

**Status**: ✅ READY FOR TASK GENERATION (`/sp.tasks`)
