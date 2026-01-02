# Evolution of Todo - Global Constitution (Phases I-V)

<!--
  SYNC IMPACT REPORT
  ==================
  Version: 0.1.0 → 1.0.0 (MAJOR - Complete constitution for multi-phase project)

  Modified Principles:
  - Added: I. Spec-Driven Development (Mandatory Workflow)
  - Added: II. Agent-Only Development
  - Added: III. Test-First Development (NON-NEGOTIABLE)
  - Added: IV. Clean Architecture & Separation of Concerns
  - Added: V. Cloud-Native & Scalability

  Added Sections:
  - Phase Governance (Scope isolation across Phase I-V)
  - Technology Stack (Python backend, Next.js frontend, etc.)
  - Quality Standards (testing, observability, versioning)
  - Compliance & Review

  No sections removed.

  Templates Updated:
  - ✅ spec-template.md (no changes required - already SDD-aligned)
  - ✅ plan-template.md (Constitution Check section ready)
  - ✅ tasks-template.md (task grouping supports SDD flow)

  Status: Constitution 1.0.0 ready for all agents across Phases I-V
-->

## Core Principles

### I. Spec-Driven Development (Mandatory Workflow)

All work across all phases MUST follow this immutable workflow:

**Constitution → Feature Specification → Technical Plan → Task List → Implementation**

- NO code may be written before an approved specification exists
- NO features may be implemented that deviate from their specification
- NO code refinement occurs at implementation time; all refinement happens at specification level
- Agents MUST validate every specification against the constitution before proceeding
- Feature scope is frozen at specification approval; expansion requires a new specification

**Rationale**: Maintains clear separation between user requirements (specs) and technical execution (code). Prevents scope creep, feature invention, and unplanned complexity at the code level.

### II. Agent-Only Development

All code generation and implementation MUST be performed by agents—humans initiate but do not write code.

- Human developers create specifications and provide domain context
- All code changes MUST be authored by agents following approved task lists
- Humans MUST NOT manually edit code or bypass agent workflows
- Agents have exclusive authority over implementation details within approved tasks
- Code reviews validate conformance to spec and plan, not manual code quality judgments

**Rationale**: Ensures consistency, auditability, and traceability. Maintains clear accountability and prevents ad-hoc changes that violate specifications.

### III. Test-First Development (NON-NEGOTIABLE)

Test-Driven Development is mandatory for all code across all phases.

- Tests MUST be written and approved BEFORE implementation begins
- Implementation occurs only when tests fail and require code to pass
- Red-Green-Refactor cycle is strictly enforced in all tasks
- Unit tests, integration tests, and end-to-end tests are required per specification
- Test coverage MUST exceed 80% for all production code; exceptions require explicit justification
- Failing tests block deployment; all tests MUST pass in the default branch

**Rationale**: Ensures correctness, maintainability, and confidence in system behavior. Catches bugs early and provides live documentation of intended behavior.

### IV. Clean Architecture & Separation of Concerns

All services MUST be architecturally clean with strict boundaries.

- Stateless services wherever applicable (Phase II+)
- API contracts clearly defined and versioned
- Internal implementation details hidden from consumers
- Data models isolated from business logic
- Cross-cutting concerns (logging, observability, error handling) are centralized
- No circular dependencies; dependency graphs MUST be acyclic

**Rationale**: Enables independent scaling, testing, and modification. Reduces coupling and simplifies onboarding, debugging, and operational support.

### V. Cloud-Native & Scalability

All architecture MUST be designed for cloud deployment and horizontal scaling.

- Services MUST be containerizable (Docker)
- State MUST be externalized (databases, caches, message queues)
- No hardcoded configuration or secrets in code
- Graceful shutdown and startup patterns required
- Support for orchestration (Kubernetes in Phase III+)
- Observable and monitorable in production

**Rationale**: Ensures the system can scale with demand, survive node failures, and be deployed reliably across environments.

## Phase Governance

Phases are strictly scoped by their specifications. Features planned for later phases MUST NOT leak into earlier phases.

### Phase I: MVP Todo Backend (Current)

**Scope**: Python FastAPI backend with SQLModel ORM, SQLite/Neon database, task CRUD operations, reminders.

**Constraints**:
- Backend-only; no UI
- Single-server deployment
- No distributed systems
- No authentication/authorization beyond basic structure

**Future features (Phases II-V) are explicitly excluded**: Multi-user support, frontend applications, advanced scheduling, event streaming, workflow orchestration.

### Phase II: Next.js Frontend & Multi-User Support

**Scope**: Next.js web application, user authentication, multi-user task isolation, real-time updates.

**Constraints**:
- Extends Phase I backend (backward compatible)
- Single-region deployment
- No event streaming or distributed workers

**Excluded**: Mobile apps, advanced AI features, complex workflows.

### Phase III: Advanced Scheduling & MCP Integration

**Scope**: OpenAI Agents SDK, MCP servers, advanced reminder scheduling with Kafka, distributed job processing.

**Constraints**:
- Multi-region aware
- Kubernetes-ready
- Externalized state management

**Excluded**: Custom AI model training, supply chain features, advanced DAGs.

### Phase IV: Workflow Orchestration & Dapr

**Scope**: Dapr integration, state management, pub/sub messaging, multi-step workflows, resilience patterns.

**Excluded**: Mobile applications, third-party integrations beyond standard APIs.

### Phase V: Enterprise & Multi-Tenant Architecture

**Scope**: Multi-tenant isolation, enterprise authentication (SAML), audit logging, SLA guarantees, mobile SDKs.

**Requirements**: All prior phases complete and stable.

## Technology Stack

Locked across all phases to ensure consistency and vendor stability.

### Backend (Phases I-V)

- **Language**: Python 3.11+
- **Framework**: FastAPI
- **ORM**: SQLModel (Pydantic + SQLAlchemy)
- **Database**: Neon PostgreSQL (primary), SQLite (development)
- **Async Runtime**: asyncio
- **Task Scheduling**: APScheduler (Phase I), Kafka + custom workers (Phase III+)
- **Observability**: Structured logging (Python `logging` with JSON), optional Prometheus metrics
- **Testing**: pytest, pytest-asyncio, pytest-cov
- **Package Management**: Poetry
- **Containerization**: Docker

### Frontend (Phases II-V)

- **Framework**: Next.js 14+
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: TanStack Query + Context API or Redux (TBD at Phase II)
- **Testing**: Vitest, React Testing Library
- **Package Management**: npm/pnpm
- **Build**: Next.js native (Webpack/Turbopack)

### Agent & Integration (Phases III-V)

- **Agent Framework**: OpenAI Agents SDK
- **MCP Servers**: Claude MCP protocol (custom + standard)
- **Message Queue**: Apache Kafka (Phase III+)
- **Workflow Engine**: Dapr (Phase IV+)
- **Orchestration**: Kubernetes (Phase III+)

### Development Tooling (All Phases)

- **VCS**: Git + GitHub
- **CI/CD**: GitHub Actions
- **Secrets Management**: `.env` files (dev), GitHub Secrets (CI/CD), cloud provider vaults (production)
- **Documentation**: Markdown in repository; deployed via GitHub Pages or similar

## Quality Standards

All code MUST meet these standards in every phase.

### Testing Discipline

- Unit tests cover all business logic (80%+ coverage required)
- Integration tests verify API contracts, database interactions, and inter-service communication
- End-to-end tests validate user scenarios from spec.md
- Tests are organized by feature and can run independently
- Test data is immutable and deterministic (no real external service calls; use mocks)
- CI/CD MUST fail if any test fails; manual override requires justification and ADR

### Observability Requirements

- All services log structured JSON with: timestamp, level, context (user_id, task_id, request_id), message
- Error logs include stack traces and remediation hints
- Metrics tracked: request latency (p50, p95, p99), error rate, queue depth (if applicable)
- Logs and metrics are queryable and retained per compliance (Phase V minimum 1 year)

### Versioning & Breaking Changes

- All APIs follow semantic versioning: MAJOR.MINOR.PATCH
- MAJOR: Breaking changes (requires migration plan, coordinated release)
- MINOR: New features, backward compatible
- PATCH: Bug fixes, no behavioral changes
- Breaking changes require:
  - Advance announcement (2+ weeks)
  - Migration documentation
  - Deprecation period (if applicable)
  - Explicit ADR documenting rationale and alternatives

### Code Quality & Standards

- All code reviewed against specification and plan (not subjective style)
- Linting enforced: `black` (Python), `eslint` + `prettier` (TypeScript)
- Type checking enforced: `mypy` (Python), TypeScript compiler (strict mode)
- Docstrings/comments required for non-obvious logic (spec already documents intent)
- No dead code, unused imports, or TODO comments without associated ADR/issue
- Commits are atomic and reference ticket/feature; commit messages follow conventional commits

### Security Standards

- No secrets (API keys, passwords, tokens) in code or logs
- All inputs validated at system boundaries (user input, external APIs)
- SQL injection, XSS, CSRF protections enabled by default in frameworks
- Sensitive data encrypted at rest and in transit (TLS 1.2+)
- Authentication/authorization tested before Phase II launch
- Security review required for any crypto or auth changes (ADR mandatory)
- Dependencies pinned and regularly audited; CVEs addressed within SLA

## Development Workflow

All development MUST follow this workflow to maintain SDD and architectural integrity.

### 1. Specification Phase

- User submits feature request or bug report
- Architect creates specification using `/sp.specify` command
- Spec answers: What is the problem? Who are the users? What outcomes are expected?
- Spec EXPLICITLY excludes: How will we build it? What technology? What data structures?
- Spec validated against constitution and approved before proceeding
- Ambiguities clarified via `/sp.clarify` command

### 2. Planning Phase

- Architect creates technical plan using `/sp.plan` command
- Plan answers: What is our technical approach? What are the data models? What are the API contracts?
- Plan validated against spec and constitution
- Architecture significant decisions documented in ADR (one ADR per major decision)
- No code written during planning; only documentation and design artifacts

### 3. Task Generation Phase

- Tasks generated from plan using `/sp.tasks` command
- Each task is independent, testable, and verifiable
- Tasks organized by user story; each story can be implemented independently
- Task descriptions include exact file paths, test cases, and acceptance criteria
- Max task complexity: implementable in 1-2 hours (4-hour blocks acceptable for Phase I only)

### 4. Implementation Phase

- Agents execute tasks from task list in dependency order
- Each task follows Red-Green-Refactor:
  - RED: Write failing tests
  - GREEN: Implement minimum code to pass tests
  - REFACTOR: Improve code without changing behavior
- Code is pushed to feature branch; must pass CI/CD (all tests, linting, type checking)
- PR created with reference to task; human reviews for spec/plan conformance only
- Merge only after approval and all CI/CD checks pass

### 5. Review & Merge

- Reviewers verify:
  - Specification is implemented correctly (not overly, not under)
  - Tests pass and cover expected cases
  - Code follows constitutional standards (clean architecture, security, etc.)
  - No unexpected changes or scope creep
- Approval MUST reference the completed tasks
- Merge to main branch; feature branch can be deleted

## Compliance & Review

Constitution compliance is non-negotiable.

### Validation Gates

- **Pre-Specification**: Does the feature respect phase boundaries? Is scope clear?
- **Pre-Plan**: Does the plan align with the specification? Does it respect architectural constraints?
- **Pre-Task**: Can each task be independently implemented and tested?
- **Pre-Code**: Are tests written and failing? Are they aligned with the task?
- **Pre-Merge**: Do all tests pass? Does code match the specification?

### Violation Response

- Specification violations: Reject PR; clarify spec before reimplementing
- Plan violations: Reject PR; create ADR for architectural deviations
- Constitutional violations: Freeze branch; require governance review before proceeding
- Security violations: Immediate remediation required; all downstream features paused

### Amendment Procedure

- Amendments to this constitution require:
  - Clear problem statement (why is the current principle insufficient?)
  - Proposed change with rationale and trade-offs
  - Impact analysis on all phases (backward compatibility?)
  - ADR documenting the decision
  - All stakeholders (Architect, Agent team, user) acknowledge
  - Version bump per semantic versioning
  - All affected templates and documentation updated
  - Retroactive compliance assessment for affected features

### Periodic Review

- Constitution reviewed quarterly (once per phase) or when a new phase begins
- Review checklist:
  - Are principles still aligned with project goals?
  - Have new constraints emerged?
  - Do templates need updating?
  - Are agents and humans following the workflow?
- Review outcomes documented in meeting notes; amendments formalized if needed

## Guidance Files

This constitution is strategic. For tactical development guidance, see:

- **Agent Behavior**: `.claude/agents/todo-manager.md`, `.claude/agents/todo-remind-scheduler.md`
- **Skills**: `.claude/skills/` (agent-invocable operations)
- **Commands**: `.claude/commands/` (sp.specify, sp.plan, sp.tasks, etc.)
- **Templates**: `.specify/templates/` (spec, plan, tasks, ADR templates)
- **Phase-Specific Docs**: `specs/[###-phase-name]/` (in-feature documentation)

Agents prioritize this constitution over guidance files in case of conflict.

---

**Version**: 1.0.0 | **Ratified**: 2026-01-02 | **Last Amended**: 2026-01-02
