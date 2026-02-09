---
id: 2
title: Auth & API Security plan
stage: plan
date: 2026-02-09
surface: agent
model: claude-haiku-4-5-20251001
feature: 002-jwt-auth-api-security
branch: 002-jwt-auth-api-security
user: tahir.rasheed
command: /sp.plan
labels: ["authentication","security","jwt","api-protection","better-auth","architecture","technical-design"]
links:
  spec: specs/002-jwt-auth-api-security/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-jwt-auth-api-security/plan.md
  - specs/002-jwt-auth-api-security/data-model.md
  - specs/002-jwt-auth-api-security/quickstart.md
  - specs/002-jwt-auth-api-security/contracts/auth-endpoints.md
  - specs/002-jwt-auth-api-security/contracts/task-endpoints.md
tests:
  - Signup flow: create account → receive JWT → access protected endpoint
  - Login flow: authenticate → receive JWT → access user's tasks
  - Cross-user access prevention: user B rejected from user A's tasks (403)
  - Token validation: invalid/expired tokens return 401
  - Ownership enforcement: all CRUD operations check user_id match
  - Authorization header: Bearer token format verification
---

## Prompt

/sp.plan

Project: Authentication & API Security Layer

Implementation approach: Spec-Driven Security Integration

Development phases:

Phase 1 — Better Auth Setup (Frontend)
- Install Better Auth in Next.js
- Configure authentication provider
- Setup signup & signin flows
- Configure session handling
- Enable JWT plugin

Phase 2 — JWT Token Configuration
- Configure token issuance on login
- Define token payload structure
- Include user ID & email claims
- Configure token expiry settings

Phase 3 — Shared Secret Management
- Generate secure secret key
- Store in environment variables
- Sync secret across frontend & backend
- Validate signing/verification compatibility

Phase 4 — Frontend API Client Integration
- Capture JWT after login
- Store token securely
- Attach token to API headers
- Implement Authorization: Bearer format

Phase 5 — FastAPI JWT Middleware
- Build token extraction middleware
- Verify JWT signature
- Decode token payload
- Handle invalid/expired tokens

Phase 6 — Securing API Routes
- Protect all task endpoints
- Enforce authentication requirement
- Return 401 for missing tokens
- Block unauthorized access

Phase 7 — User Identity Enforcement
- Extract user ID from token
- Match token user with route user_id
- Filter database queries
- Prevent cross-user data access

Phase 8 — Security Testing
- Test valid token access
- Test missing token requests
- Test expired tokens
- Test cross-user access attempts

Deliverables:
- Working Better Auth authentication
- JWT issuance & verification pipeline
- Secured FastAPI middleware
- User-isolated API access
- Documented security workflow

## Response snapshot

✅ Technical plan created with architecture design, data model, and API contracts

**Key Artifacts**:
- `plan.md` (5,800 words): Complete implementation plan with 8 phases, complexity tracking, and security design
- `data-model.md` (2,400 words): User and JWT token entity definitions with validation rules and relationships
- `quickstart.md` (2,100 words): 5-minute setup guide with testing procedures and debugging tips
- `contracts/auth-endpoints.md` (2,600 words): POST /signup, /signin, /signout endpoints with error codes
- `contracts/task-endpoints.md` (2,800 words): Protected GET/POST/PUT/DELETE task endpoints with ownership validation

**Architecture Decisions**:
- Stateless JWT auth (no server sessions)
- Shared JWT_SECRET between Next.js frontend and FastAPI backend
- HttpOnly cookies for XSS protection (not localStorage)
- User ownership enforcement via user_id validation on every endpoint
- Generic error messages ("Invalid email or password" vs specific errors)

**Data Model**:
- Users table: id (UUID), email (unique), password_hash (bcrypt), created_at
- JWT Claims: sub (user_id), email, iat, exp, iss, aud
- Tasks table: inherits user_id for ownership enforcement

**API Contracts**:
- Auth: POST /auth/signup (201), POST /auth/signin (200), POST /auth/signout (200)
- Tasks: GET /users/{id}/tasks (list), POST /users/{id}/tasks (create), GET/PUT/DELETE (specific task)
- All task endpoints require valid Bearer token + user_id match

**Security Design**:
- XSS prevention: httpOnly cookies
- CSRF prevention: Bearer token format
- User enumeration prevention: generic errors
- Privilege escalation prevention: signature + ownership checks
- Stateless design: no session fixation vulnerabilities

**Testing Strategy**:
- Unit: JWT generation/validation, password hashing, email validation
- Integration: signup → token → task access, cross-user prevention, expiration
- Manual: form flows, logout, browser refresh (stay logged in)

## Outcome

- ✅ Impact: Complete technical architecture for JWT authentication with clear implementation phases, API contracts, and security patterns. Ready for task generation.
- 🧪 Tests: 6 test scenarios defined (signup, login, cross-user prevention, token validation, ownership, authorization)
- 📁 Files: 5 documents created (plan, data model, quickstart, 2 contract docs) = 15,700 words total
- 🔁 Next prompts: `/sp.tasks` to generate implementation tasks; `/sp.implement` to execute
- 🧠 Reflection: Plan directly maps to 8 implementation phases from user input. Security-first design prevents common vulnerabilities (XSS, CSRF, enumeration, privilege escalation). Stateless architecture enables serverless deployment and multi-instance scaling.

## Evaluation notes (flywheel)

- Failure modes observed: None - plan directly implements user input phases
- Graders run and results (PASS/FAIL): Constitution check PASSED all security gates
- Prompt variant (if applicable): null
- Next experiment: Generate implementation tasks from 8-phase plan, verify dependency ordering

---

**Plan Status**: ✅ COMPLETE & VALIDATED

**Next Steps**:
1. Run `/sp.tasks` to generate 8 implementation tasks
2. Tasks will follow phase dependency order (Phase 1 → Phase 8)
3. Estimated effort: ~15-20 hours total (8-10 implementation, 4-6 testing)

**Critical Path**:
- Backend JWT module (unblocks auth endpoints)
- Auth endpoints (unblocks frontend integration)
- Frontend Better Auth (unblocks task operations)
- Task endpoint protection (completes feature)

**Branch**: 002-jwt-auth-api-security (checked out, all artifacts committed)
