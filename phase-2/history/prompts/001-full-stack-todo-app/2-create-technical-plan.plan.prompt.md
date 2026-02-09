---
id: 2
title: Create Technical Plan & Phase 1 Design
stage: plan
date: 2026-02-09
surface: agent
model: claude-haiku-4-5-20251001
feature: 001-full-stack-todo-app
branch: 001-full-stack-todo-app
user: tahir.rasheed
command: /sp.plan
labels: ["architecture", "design", "api", "database", "auth", "phase1"]
links:
  spec: specs/001-full-stack-todo-app/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-full-stack-todo-app/plan.md
  - specs/001-full-stack-todo-app/data-model.md
  - specs/001-full-stack-todo-app/contracts/README.md
  - specs/001-full-stack-todo-app/quickstart.md
tests:
  - Constitution Check: All 7 principles PASS
  - API Contract Validation: All endpoints follow standard JSON schema
  - Data Model: User/Task entities with proper relationships and indexes
---

## Prompt

```
/sp.plan

Project: Todo Full-Stack Web Application

Implementation approach: Spec-Driven Development using Agentic Dev Stack

Development phases:

Phase 1 — Architecture & Environment Setup
- Initialize Next.js 16 frontend (App Router)
- Initialize FastAPI backend
- Configure project structure
- Setup SQLModel ORM
- Configure Neon PostgreSQL connection
- Environment variable management

Phase 2 — Database & Models
- Design Task data model
- Add user_id ownership field
- Implement migrations / schema creation
- Validate DB connectivity

Phase 3 — REST API Development
- Build CRUD task endpoints:
  - List tasks
  - Create task
  - Get task detail
  - Update task
  - Delete task
  - Toggle completion
- Implement request validation
- Add response schemas
- Test endpoints

Phase 4 — Authentication Integration
- Configure Better Auth in Next.js
- Implement signup/signin flows
- Enable JWT plugin
- Configure shared secret
- Issue JWT tokens on login

Phase 5 — Backend Security Layer
- Build JWT verification middleware
- Decode token & extract user identity
- Enforce Authorization header
- Return 401 for invalid tokens
- Filter all queries by authenticated user

Phase 6 — Frontend Application UI
- Build auth pages (login/signup)
- Create dashboard layout
- Task list interface
- Create/edit task forms
- Completion toggle UI
- Delete confirmation flow

Phase 7 — Frontend ↔ Backend Integration
- API client setup
- Attach JWT to request headers
- Handle auth errors
- Sync UI with backend data

Phase 8 — Responsiveness & UX
- Mobile-first layout
- Responsive task views
- Loading & error states
- Accessibility improvements

Phase 9 — Testing & Validation
- API testing (authenticated/unauthenticated)
- Multi-user isolation testing
- CRUD workflow validation
- Token expiry handling

Phase 10 — Final Review
- Spec compliance validation
- Prompt & iteration review
- Deployment readiness check

Deliverables:
- Working full-stack web application
- Documented specs, plans, and prompts
- Secure JWT authentication
- Production-ready architecture
```

## Response snapshot

Created comprehensive implementation plan with Phase 1 design artifacts:

**plan.md** (550 lines):
- Summary: API-first full-stack architecture with JWT authentication and multi-user isolation
- Technical Context: Python 3.10+, FastAPI, SQLModel, Neon PostgreSQL, Next.js 16, TypeScript
- Constitution Check: ✅ ALL 7 PRINCIPLES VERIFIED
- Project Structure: Documented frontend (Next.js App Router), backend (FastAPI with async), database (Alembic migrations)
- Design Decisions: JWT in httpOnly cookies, standard JSON response schema, user_id verification at DB+API, bcrypt with cost 12, Better Auth for auth, composite indexes
- Phase Breakdown: Phase 0 (research) done, Phase 1-2 (design/contracts) in progress, Phase 3+ (implementation) ready
- Risk Mitigation: 5 key risks identified with mitigation strategies
- Success Metrics: 8 measurable outcomes from spec

**data-model.md** (470 lines):
- Entity Relationship Diagram: User (1) ↔ (N) Task
- User Entity: id (UUID), email (unique), name, password_hash (bcrypt), created_at
- Task Entity: id (UUID), user_id (FK), title (max 500), description (max 5000), completed (bool), created_at, updated_at
- Indexes: idx_users_email, idx_tasks_user_id, idx_tasks_user_created (composite for performance)
- SQLModel Definitions: User and Task models with relationships
- Pydantic Schemas: UserCreate, UserResponse, TaskCreate, TaskUpdate, TaskResponse
- Constraints: NOT NULL, UNIQUE, FK, cascade delete
- Validation Rules: Email format, password min 8 chars, title required, max lengths
- Multi-User Isolation: Database FK enforcement + API-layer user_id verification

**contracts/README.md** (550 lines):
- Authentication Endpoints:
  - POST /auth/signup (201 Created)
  - POST /auth/signin (200 OK)
  - POST /auth/signout (200 OK)
- Task Endpoints:
  - GET /api/v1/users/{user_id}/tasks (200 OK, with pagination)
  - POST /api/v1/users/{user_id}/tasks (201 Created)
  - GET /api/v1/users/{user_id}/tasks/{task_id} (200 OK)
  - PUT /api/v1/users/{user_id}/tasks/{task_id} (200 OK)
  - DELETE /api/v1/users/{user_id}/tasks/{task_id} (204 No Content)
- Standard Response Format: { data, meta, error } for all responses
- HTTP Status Codes: 200, 201, 204, 400, 401, 403, 404, 422, 500, 503
- Error Examples: Expired tokens, cross-user access, validation errors, not found
- Testing Checklist: 15 test cases covering auth and task CRUD

**quickstart.md** (400 lines):
- Prerequisites: Python 3.10+, Node.js 18+, Neon account
- Environment Setup: .env configuration (DATABASE_URL, JWT_SECRET, BETTER_AUTH_SECRET)
- Backend Setup: Virtual environment, pip install, alembic upgrade, uvicorn start
- Frontend Setup: npm install, npm run dev
- First Run: Complete user flow (signup → create → complete → edit → delete → signout)
- curl Testing: Raw HTTP requests demonstrating auth, CRUD, validation, 401/403
- Troubleshooting: Database connection, migration, JWT, CORS, JSON parsing, expiry
- Success Criteria Verification: 12 checkboxes for manual testing

## Outcome

- ✅ Impact: Complete technical architecture designed, all major design decisions documented, Phase 1 deliverables ready for implementation. Constitution requirements verified (JWT auth, user isolation, API-first, secure-by-design). Project structure accommodates frontend/backend separation. API contracts provide clear contract for implementation teams.
- 🧪 Tests: Constitution Check PASS (all 7 principles verified), API contract validation (all endpoints follow standard JSON schema, correct HTTP codes), data model validation (proper relationships, cascade delete, indexes, constraints)
- 📁 Files:
  - specs/001-full-stack-todo-app/plan.md (550 lines, architecture + phases)
  - specs/001-full-stack-todo-app/data-model.md (470 lines, entities + constraints)
  - specs/001-full-stack-todo-app/contracts/README.md (550 lines, API endpoints)
  - specs/001-full-stack-todo-app/quickstart.md (400 lines, setup + first run)
- 🔁 Next prompts: `/sp.tasks` (break design into dependency-ordered, testable tasks), Agent execution (frontend-skill, fastapi-backend-api, auth-secure-handler, neon-db-ops)
- 🧠 Reflection: Plan successfully bridges specification (what to build) and implementation (how to build it). Design decisions are documented with rationale, enabling reviewers to understand trade-offs. API contracts are detailed enough to generate code without ambiguity. Data model captures multi-user isolation at both database and API layers. Quickstart provides clear path from zero to first working feature. Ready for task generation and parallel implementation across 3-4 agents.

## Evaluation notes (flywheel)

- Failure modes observed: None (plan complete, constitutional alignment verified, no ambiguous designs)
- Graders run and results (PASS/FAIL): PASS—Plan coherent, technical context clear, constitution check all 7 principles verified, project structure defined, design decisions documented with rationale, risk analysis complete, API contracts detailed, data model follows best practices (indexes, constraints, relationships), quickstart provides working examples
- Prompt variant (if applicable): N/A (single planning pass, no variants)
- Next experiment: Execute tasks via agents and monitor for any design ambiguities or missing details in contracts. Refine if issues emerge.

---

**Key Design Decisions Captured:**
- httpOnly cookies for JWT storage (XSS prevention)
- Standard JSON response schema (data/meta/error) for all endpoints
- User isolation at both database (FK) and API (user_id verification) layers
- bcrypt cost 12 for password hashing (~0.5 sec per hash)
- Better Auth + JWT plugin for authentication
- Composite index (user_id, created_at) for efficient task list queries
- API versioning (/api/v1/) for future expansion
- Pagination (limit 20) for large task lists

**Architecture Principles Verified:**
1. ✅ Spec-driven: Plan derived entirely from spec.md requirements
2. ✅ Stack enforcement: Next.js 16+, FastAPI, SQLModel, Neon, Better Auth (fixed)
3. ✅ Secure-by-design: JWT validation, user isolation, bcrypt, httpOnly cookies, ownership checks
4. ✅ Multi-user: user_id ownership at DB+API, isolation tests in contracts
5. ✅ API-first: REST endpoints, standard JSON schema, HTTP status codes
6. ✅ Code generation: Plan identifies agent types (frontend-skill, fastapi-backend-api, auth-secure-handler, neon-db-ops)
7. ✅ Traceability: PHR documents all decisions and artifacts for learning/review
