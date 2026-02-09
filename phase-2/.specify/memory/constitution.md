# Todo Full-Stack Web Application Constitution

<!--
  SYNC IMPACT REPORT:
  Version Change: 0.0.0 → 1.0.0 (Initial Constitution for Phase II)
  Modified Principles: (New)
  - Spec-Driven Development (mandatory, all features originate from written specs)
  - Stack Enforcement (Next.js + FastAPI + SQLModel + Neon + Better Auth)
  - Secure-by-Design Authentication (JWT on all protected endpoints)
  - Multi-User Architecture (data isolation enforced at DB/API layer)
  - API-First Design (frontend consumes APIs only)

  Added Sections:
  - Technology Stack & Version Pinning
  - Authentication & Security Standards
  - API & Data Contract Standards
  - Workflow Requirements

  Removed Sections: None (this is initial constitution)

  Templates Updated:
  ✅ .specify/templates/spec-template.md (reference principles)
  ✅ .specify/templates/plan-template.md (reference stack & constraints)
  ✅ .specify/templates/tasks-template.md (reference test & security requirements)
  ⚠ CLAUDE.md already updated with Technology Stack & Agent Mapping

  Follow-up TODOs: None
-->

## Core Principles

### I. Spec-Driven Development (Mandatory)

All features MUST originate from written specifications. No feature implementation begins without:
- A written spec in `specs/<feature>/spec.md` approved by the team
- User stories with explicit priorities (P1, P2, P3)
- Acceptance scenarios in Given-When-Then format
- A technical plan in `specs/<feature>/plan.md` covering architecture, contracts, and constraints
- Dependency-ordered tasks in `specs/<feature>/tasks.md` with testable acceptance criteria

**Rationale**: Specifications prevent scope creep, ensure alignment before coding, and create a auditable history of decisions through Prompt History Records (PHRs).

### II. Stack Enforcement (Mandatory)

The technology stack is FIXED for Phase II and may NOT be substituted without explicit governance approval:

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Frontend** | Next.js 16+ (App Router) | Modern SSR, built-in API routes, excellent developer experience |
| **Backend** | Python FastAPI | Type-safe, async-native, fast development, excellent validation |
| **ORM** | SQLModel | SQLAlchemy-based, Pydantic integration, seamless type checking |
| **Database** | Neon Serverless PostgreSQL | Auto-scaling, ACID compliance, managed backups, git-like branching |
| **Authentication** | Better Auth | Multi-provider support, JWT token issuance, secure session management |

**Constraints**:
- No additional frameworks or libraries may be introduced without a written ADR (Architecture Decision Record)
- All backend code MUST be Python 3.10+ (async support required)
- Frontend MUST use TypeScript for type safety
- Database migrations MUST use SQLAlchemy/Alembic; never manual SQL

**Rationale**: Fixed stack prevents architectural drift, reduces decision overhead, and ensures consistent team experience.

### III. Secure-by-Design Authentication (Mandatory)

All user-facing features MUST enforce authentication and authorization:

- JWT tokens MUST be issued by Better Auth upon successful login
- All protected endpoints MUST validate JWT signature using a shared secret (via `.env`)
- JWT payload MUST include `user_id` and `email` at minimum
- Tokens MUST have reasonable expiration: 15 minutes for access tokens, 7 days for refresh
- Backend MUST verify that `user_id` in the JWT matches the `user_id` in the request URL (prevent cross-user access)
- Frontend MUST use httpOnly cookies to prevent XSS theft of tokens
- Passwords MUST be hashed with bcrypt (minimum cost 12); never stored plaintext

**Testing**: Every protected endpoint MUST include unit/integration tests for:
- Valid token (grants access)
- Expired token (returns 401)
- Invalid signature (returns 401)
- Mismatched user_id (returns 403)

**Rationale**: Multi-user systems are only trustworthy if authentication is rigorous from day one; deferred security leads to breaches.

### IV. Multi-User Data Isolation (Mandatory)

Every data entity MUST be owned by exactly one user, and all queries MUST enforce user isolation:

- `users` table: Primary identity store with unique email, bcrypt-hashed passwords
- `tasks` table: MUST include `user_id` foreign key; all queries MUST filter by `user_id`
- Database schema MUST include composite indexes on `(user_id, created_at)` for efficient filtering
- API MUST NOT expose any user data except the authenticated user's own data
- Backend MUST validate `user_id` on every read/write operation; never trust client-supplied IDs

**Testing**: Every CRUD operation MUST include a test case verifying:
- User A cannot read/modify/delete User B's data
- Queries return only the authenticated user's records

**Rationale**: Data isolation is the foundation of multi-user trust; gaps here are security incidents.

### V. API-First Design (Mandatory)

The frontend MUST consume only REST APIs; no direct database access:

- All state mutations happen via HTTP requests (POST, PUT, DELETE)
- All state reads happen via HTTP GET requests (list, detail)
- Frontend MUST never hardcode database queries or ORM logic
- Backend MUST validate all inputs using Pydantic schemas
- API responses MUST follow a consistent JSON schema with `data`, `error`, and `meta` fields
- API errors MUST use standard HTTP status codes:
  - 400 Bad Request (invalid input)
  - 401 Unauthorized (missing/invalid JWT)
  - 403 Forbidden (user lacks permission)
  - 404 Not Found (resource not found)
  - 500 Internal Server Error (unexpected backend failure)

**Rationale**: API-first design decouples frontend and backend, enables future mobile clients, and provides clear contracts.

### VI. Code Generation via Claude Code (Mandatory)

All code MUST be generated via Claude Code agents; no manual coding:

- Use `frontend-skill` for Next.js pages, components, layouts
- Use `fastapi-backend-api` for FastAPI routes, middleware, business logic
- Use `auth-secure-handler` for authentication flows, JWT validation
- Use `neon-db-ops` for schema design, migrations, query optimization
- Use `backend-skill` for REST API contracts and error handling
- Document every code change via a Prompt History Record (PHR)

**Non-negotiable**: If a developer writes code manually without using Claude Code, it must be replaced with agent-generated code before merging.

**Rationale**: Reproducibility through documented prompts enables review, iteration, and knowledge capture; manual coding introduces unmeasurable technical debt.

### VII. Prompt History & Traceability (Mandatory)

Every significant user input and agent action MUST be recorded in a Prompt History Record:

- **Constitution changes** → `history/prompts/constitution/<ID>-<slug>.constitution.prompt.md`
- **Feature specs** → `history/prompts/<feature-name>/<ID>-<slug>.spec.prompt.md`
- **Planning work** → `history/prompts/<feature-name>/<ID>-<slug>.plan.prompt.md`
- **Implementation** → `history/prompts/<feature-name>/<ID>-<slug>.red/green/refactor.prompt.md`
- **General guidance** → `history/prompts/general/<ID>-<slug>.general.prompt.md`

Each PHR MUST include:
- Full user prompt (verbatim, not truncated)
- Key assistant response/output
- Files created/modified
- Stage (constitution, spec, plan, tasks, red, green, refactor, misc, general)
- Date (ISO 8601: YYYY-MM-DD)

**Rationale**: Traceability enables learning, audit trails, and prevents knowledge loss when team members change.

## Technology Stack & Version Pinning

### Frontend (Next.js)
- **Version**: 16.0.0+
- **Runtime**: Node.js 18+ (async/await required)
- **Package Manager**: npm or pnpm
- **Build**: Next.js App Router (no Pages Router)
- **Styling**: TailwindCSS (or CSS Modules, no runtime CSS-in-JS)
- **HTTP Client**: fetch API (no axios/superagent unless justified via ADR)
- **State Management**: React Context + hooks (no Redux unless justified)

### Backend (FastAPI)
- **Version**: Python 3.10+ with FastAPI 0.104+
- **Async**: All I/O operations MUST be async (no blocking sync calls)
- **Validation**: Pydantic v2 for request/response schemas
- **ORM**: SQLModel (not SQLAlchemy directly)
- **Testing**: pytest + pytest-asyncio
- **Logging**: Standard Python logging (structured logs recommended)

### Database (Neon PostgreSQL)
- **Version**: PostgreSQL 15+
- **Migrations**: Alembic (via SQLAlchemy)
- **Connection Pooling**: PgBouncer (default on Neon)
- **Backups**: Managed by Neon (automatic daily)
- **Branching**: Use Neon's git-like branch feature for development isolation

### Authentication (Better Auth)
- **JWT Issuance**: Better Auth issues tokens on successful login
- **Secret Management**: Via `.env` (never hardcoded)
- **Token Expiration**: 15 min (access), 7 days (refresh)
- **Session Store**: Cookies (httpOnly, Secure flags required)

## API & Data Contract Standards

### REST Endpoint Structure

All endpoints MUST follow this pattern:

```
[METHOD] /api/[resource-version]/[resource-type]/[resource-id]/[sub-resource]
```

Example:
- `GET /api/v1/users/123/tasks` — List user's tasks
- `POST /api/v1/users/123/tasks` — Create task for user
- `PUT /api/v1/users/123/tasks/456` — Update task
- `DELETE /api/v1/users/123/tasks/456` — Delete task

### Request/Response Schema

All endpoints MUST return JSON in this format:

```json
{
  "data": { /* resource or array of resources */ },
  "meta": {
    "timestamp": "2025-01-15T10:30:45Z",
    "request_id": "req-abc123"
  },
  "error": null /* or error object if status >= 400 */
}
```

Error responses:
```json
{
  "data": null,
  "meta": { "timestamp": "...", "request_id": "..." },
  "error": {
    "code": "INVALID_INPUT",
    "message": "User-friendly error message",
    "details": { /* optional field-level errors */ }
  }
}
```

### Idempotency & Safety

- GET requests MUST be idempotent and return no side effects
- POST requests SHOULD include an idempotency key (optional, for duplicate detection)
- PUT requests MUST be idempotent (update same state, same result)
- DELETE requests SHOULD be idempotent (delete already-deleted resource returns 404 or 200)

## Workflow Requirements

### Spec → Plan → Tasks → Implementation

Every feature MUST follow this sequence (no skipping):

1. **Spec Phase**: Write user stories, acceptance scenarios, feature boundaries
2. **Plan Phase**: Research dependencies, design API contracts, data model, security model
3. **Tasks Phase**: Break plan into testable tasks, identify dependencies, assign priorities
4. **Implementation Phase**: Code generation via agents, red-green-refactor, integration testing

### Branching & PRs

- **Branch naming**: `<feature-id>-<slug>` (e.g., `002-user-auth`)
- **Commit messages**: Follow conventional commits (feat:, fix:, docs:, refactor:)
- **PR title**: Same as branch name
- **PR description**: Link to feature spec, plan, and tasks
- **Merge requirement**: All tests passing, all acceptance criteria met

### Testing Discipline

- **Unit tests**: Every function/method (target: >80% coverage)
- **Integration tests**: API endpoints, database operations, auth flows
- **Acceptance tests**: User story validation (Given-When-Then scenarios)
- **Test locations**: `tests/unit/`, `tests/integration/`; mirror source structure

## Governance

### Constitution as Law

This constitution supersedes all other documents, team practices, and informal agreements. If a conflict arises between this constitution and any other guidance, the constitution wins.

### Amendment Procedure

Changes to this constitution MUST:
1. Be proposed in writing with clear rationale and impact analysis
2. Include a version bump (MAJOR.MINOR.PATCH) with justification
3. Be documented in a Prompt History Record with stage `constitution`
4. Reference any dependent template updates or code changes
5. Be approved by the development team before implementation

### Version Policy

- **MAJOR**: Backward-incompatible principle removals, redefinitions, or stack changes (requires team consensus)
- **MINOR**: New principles, new sections, or materially expanded guidance (project lead approval)
- **PATCH**: Clarifications, wording changes, typo fixes (agent-approved)

### Compliance & Review

- Every plan MUST include a "Constitution Check" section verifying alignment with this document
- Every PR MUST reference the constitution principles it satisfies
- Quarterly reviews of constitution adherence; update as lessons learned emerge

### Operational Guidance

For runtime development practices (code style, testing patterns, refactoring heuristics), see `CLAUDE.md` (agent rules and agent-specific guidance).

---

**Version**: 1.0.0 | **Ratified**: 2026-02-09 | **Last Amended**: 2026-02-09
