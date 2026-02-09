# Implementation Plan: Phase I - MVP Console Todo Application

**Branch**: `001-phase-i-mvp` | **Date**: 2026-01-02 | **Spec**: [specs/001-phase-i-mvp/spec.md](spec.md)
**Input**: Feature specification from `/specs/001-phase-i-mvp/spec.md`

## Summary

Implement an in-memory Python console application that provides basic task management (CRUD operations) through an interactive menu-driven CLI. Tasks are stored entirely in runtime memory and are lost on application exit. The design prioritizes simplicity, clarity, and independence from external dependencies (no databases, files, or web frameworks). The application will demonstrate all functionality specified in Phase I user stories and acceptance criteria.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: None (standard library only; optional: tabulate for formatted output)
**Storage**: In-memory Python dictionary and list data structures (no database, no files)
**Testing**: pytest, pytest-cov (80%+ coverage required by constitution)
**Target Platform**: Linux, macOS, Windows console/terminal
**Project Type**: Single console application (not web, not mobile)
**Performance Goals**: Response time <1 second for all operations (100+ tasks); handles up to 100 tasks without degradation
**Constraints**: Strictly in-memory (no persistence beyond session); single-user (no concurrency); no external dependencies beyond Python stdlib
**Scale/Scope**: Single MVP application (~500-1000 LOC); 5 user stories; 12 functional requirements

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

✅ **Spec-Driven Development**: Plan is derived entirely from specification; no new features introduced
✅ **Test-First Development**: All code will be preceded by pytest tests (TDD required); 80%+ coverage enforced
✅ **Clean Architecture**: Separation of concerns with distinct modules (data/models, business logic, CLI interface)
✅ **Phase I Boundaries**: Strictly limited to basic CRUD; no reminders, scheduling, persistence, authentication, or web concepts
✅ **No Future-Phase Leakage**: No multi-user support, no authentication structure, no database schemas, no API design
✅ **Technology Stack Alignment**: Python 3.11+ confirmed as backend language per constitution; no prohibited dependencies

**Status**: PASS - Plan is compliant and ready for Phase 1 design artifacts

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
src/
├── main.py              # Application entry point; CLI menu loop
├── models/
│   └── task.py          # Task data class with validation and state management
├── services/
│   ├── task_manager.py  # Business logic: CRUD operations on tasks
│   └── id_generator.py  # Auto-incrementing ID generation strategy
└── ui/
    └── cli_interface.py # User input/output handling; menu rendering

tests/
├── unit/
│   ├── test_task.py                  # Task model validation and behavior
│   ├── test_task_manager.py          # CRUD operations and business logic
│   ├── test_id_generator.py          # ID generation edge cases
│   └── test_cli_interface.py         # Input parsing and output formatting
├── integration/
│   └── test_cli_workflow.py          # End-to-end menu flows; all user stories
└── conftest.py                       # pytest fixtures for test data

pyproject.toml                        # Project metadata, Python 3.11+ requirement, test config
```

**Structure Decision**: Single console application with clear separation of concerns:
- **models/**: Data representation (Task class) with validation
- **services/**: Business logic (TaskManager for CRUD, ID generation strategy)
- **ui/**: User interaction layer (CLI menu, input parsing, formatted output)
- **tests/**: Unit tests (models, services), integration tests (complete workflows)

This structure enables independent testing of each layer and clear responsibility boundaries, supporting the Clean Architecture principle from the constitution.

## Architectural Approach

### 1. Data Structures

**TaskStore**: Dictionary mapping task ID → Task object

```python
tasks: Dict[int, Task] = {}
next_id: int = 1
```

**Task Class**: Dataclass or NamedTuple with fields: id, title, description, status, created_at

### 2. Task Identification Strategy

- **ID Generation**: Auto-incrementing counter (next_id variable)
- **ID Immutability**: Task ID never changes once assigned
- **ID Reuse**: NOT reused when task deleted (next_id continues incrementing)
- **ID Validation**: Must be positive integer; reject non-numeric input with error message

### 3. CLI Control Flow

```
Main Loop:
├── Display Menu
├── Get User Input (case-insensitive)
└── Dispatch to Handler:
    ├── Add Task → Prompt for title/description → Create → Display ID
    ├── View Tasks → Format and display all tasks (or "no tasks" message)
    ├── Toggle Status → Prompt for ID → Toggle → Display confirmation
    ├── Update Task → Prompt for ID, field, new value → Update → Display confirmation
    ├── Delete Task → Prompt for ID → Confirm → Delete → Display confirmation
    └── Exit → Graceful shutdown

Error Handling:
├── Empty title → "Task title cannot be empty"
├── Invalid ID → "Invalid ID: must be a positive integer"
├── Task not found → "Error: Task ID {id} not found"
├── Invalid menu choice → "Please enter a valid option (add, view, toggle, update, delete, exit)"
```

### 4. Separation of Responsibilities

**TaskManager (Business Logic)**:
- Add task (validates title, auto-generates ID)
- Get all tasks
- Get task by ID
- Update task (title or description)
- Toggle task status
- Delete task
- List management (no direct user interaction)

**CLIInterface (User Interaction)**:
- Display menu
- Parse user input (case-insensitive menu options, task ID as integer)
- Format output (table or list display for tasks)
- Handle input validation (empty strings, non-numeric IDs)
- Display error messages and confirmations

**Task (Data Model)**:
- Immutable ID
- Mutable title, description, status
- Auto-set created_at
- Status enumeration (incomplete/complete)
- Validation (title required and non-empty)

### 5. Error Handling Strategy

All error conditions from spec edge cases are handled:
- Invalid input (non-numeric task ID, empty title)
- Non-existent task references
- Empty task list
- Case sensitivity (all menu options and IDs are case-insensitive)

Error messages follow pattern: "Error: [specific issue]" for consistency and clarity.

## Design Decisions (No ADRs Required)

These decisions are straightforward implementations of spec requirements with no viable alternatives:

1. **In-memory storage**: Spec explicitly requires no persistence; dictionary + list is simplest Python approach
2. **ID counter strategy**: Auto-incrementing counter is standard and aligns with spec "unique, auto-incrementing"
3. **CLI menu loop**: Spec defines menu-based interaction; standard console loop is only viable approach
4. **pytest for testing**: Constitution mandates 80%+ test coverage; pytest is Python standard and satisfies TDD requirement
5. **No external dependencies**: Spec constraints (no databases, files, web) mean only Python stdlib needed; optional tabulate for formatted output only
