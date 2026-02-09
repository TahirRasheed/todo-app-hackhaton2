# Quickstart Guide: Phase I - MVP Console Todo Application

**Target Audience**: Developers implementing Phase I
**Purpose**: Rapid onboarding to architecture, design, and testing strategy

## Overview

Phase I delivers a menu-driven, in-memory Python console application for basic task management. No databases, files, or external services. Single-user, single-session operation. All data lost on exit.

## Architecture at a Glance

```
┌─────────────────────────────────────────┐
│  CLI Interface (User Interaction)       │  main.py + cli_interface.py
│  • Menu display                         │
│  • Input parsing (case-insensitive)     │
│  • Error messages                       │
└────────────┬────────────────────────────┘
             │ calls
┌────────────▼────────────────────────────┐
│  Task Manager (Business Logic)          │  task_manager.py
│  • Add task (validation, ID generation) │
│  • Get task / Get all tasks             │
│  • Update task (title/description)      │
│  • Toggle status (complete/incomplete)  │
│  • Delete task                          │
└────────────┬────────────────────────────┘
             │ manages
┌────────────▼────────────────────────────┐
│  Task Model (Data Representation)       │  task.py
│  • id (auto-incrementing, immutable)    │
│  • title (required)                     │
│  • description (optional)               │
│  • status (incomplete/complete)         │
│  • created_at (timestamp)               │
└─────────────────────────────────────────┘
```

## File Structure

```
src/
├── main.py                           # Entry point; CLI main loop
├── models/
│   └── task.py                      # Task dataclass + validation
├── services/
│   ├── task_manager.py              # CRUD logic + ID generation
│   └── id_generator.py              # Auto-incrementing ID strategy (optional)
└── ui/
    └── cli_interface.py             # Menu rendering + input/output

tests/
├── unit/
│   ├── test_task.py                 # Task model tests
│   ├── test_task_manager.py         # CRUD operation tests
│   ├── test_id_generator.py         # ID generation tests
│   └── test_cli_interface.py        # Input parsing + output tests
├── integration/
│   └── test_cli_workflow.py         # Full user story workflows
└── conftest.py                      # Pytest fixtures

pyproject.toml                       # Python 3.11+ requirement, test config
```

## Implementation Strategy

### Phase 1: Models & Data

1. **Implement Task class** (`src/models/task.py`):
   - Dataclass or NamedTuple
   - Fields: id, title, description, status, created_at
   - Validation: title required + non-empty
   - Method: toggle_status()

2. **Write unit tests first** (`tests/unit/test_task.py`):
   - Create task with valid data
   - Reject empty/invalid titles
   - Toggle status (incomplete → complete → incomplete)
   - Immutable ID

### Phase 2: Business Logic

1. **Implement TaskManager class** (`src/services/task_manager.py`):
   - add_task(title, description) → Task
   - get_task(id) → Task or None
   - get_all_tasks() → List[Task]
   - update_task(id, field, value) → Task
   - toggle_task_status(id) → Task
   - delete_task(id) → None
   - Error handling for all operations

2. **Write unit tests** (`tests/unit/test_task_manager.py`):
   - Add task; verify ID increments correctly
   - Retrieve task by ID (found/not found)
   - Update title/description; verify immutable ID
   - Toggle status multiple times
   - Delete task; verify not reused
   - Error messages for invalid inputs

### Phase 3: User Interface

1. **Implement CLIInterface class** (`src/ui/cli_interface.py`):
   - display_menu() → formatted menu text
   - get_user_input(prompt) → user input (case-insensitive)
   - parse_menu_choice(input) → validated option
   - validate_task_id(input) → validated ID or error
   - display_tasks(tasks) → formatted table
   - display_message(msg, type) → success/error/info message

2. **Write unit tests** (`tests/unit/test_cli_interface.py`):
   - Parse menu options (case-insensitive)
   - Format task table (empty, single, multiple tasks)
   - Validate task ID input
   - Format error messages

### Phase 4: Integration & Main Loop

1. **Implement main.py**:
   - Create TaskManager instance
   - Create CLIInterface instance
   - Main loop:
     - Display menu
     - Get user choice
     - Dispatch to handler
     - Execute operation
     - Display result
     - Loop until exit

2. **Write integration tests** (`tests/integration/test_cli_workflow.py`):
   - Complete user story workflows (add → view → toggle → update → delete)
   - Error handling flows (invalid ID, empty title)
   - Menu loop behavior (multiple operations)

## Testing Strategy (Test-First)

### Test Hierarchy

```
Integration Tests (5 workflows covering all user stories)
├── Full workflow: Create → View → Toggle → Update → Delete
├── Error workflow: Invalid IDs, empty titles
├── Status workflow: Toggle multiple times
└── ...

Unit Tests (modules in isolation)
├── Task model (validation, state)
├── TaskManager (CRUD operations)
├── ID generation (sequence, no reuse)
└── CLI interface (parsing, formatting)
```

### Coverage Requirements

- **Unit**: 80%+ coverage (constitution requirement)
- **Integration**: All 5 user stories + error cases
- **Key paths**: Add, View, Toggle, Update, Delete (P1/P2/P3 priority)

### Example Test (Pytest)

```python
def test_add_task_increments_id():
    """ID should increment for each task (no reuse)."""
    manager = TaskManager()

    task1 = manager.add_task("First task")
    task2 = manager.add_task("Second task")
    task3 = manager.add_task("Third task")

    assert task1.id == 1
    assert task2.id == 2
    assert task3.id == 3

def test_delete_task_does_not_reuse_id():
    """Next task after deletion should get next sequential ID."""
    manager = TaskManager()

    task1 = manager.add_task("Task 1")
    task2 = manager.add_task("Task 2")
    manager.delete_task(1)  # Delete first task
    task3 = manager.add_task("Task 3")

    assert task3.id == 3  # NOT 1 (no reuse)
    assert len(manager.get_all_tasks()) == 2
```

## Key Design Decisions

### In-Memory Storage

Why: Spec explicitly forbids persistence; dictionary + list is simplest and fastest

```python
tasks: Dict[int, Task] = {}  # O(1) lookup by ID
next_id: int = 1             # O(1) ID generation
```

### ID Immutability

Why: User expects consistent, stable task references

```python
# ID assigned at creation; never changes
task.id  # Always the same; final
```

### ID No-Reuse Policy

Why: Spec requires sequential IDs; reusing IDs confuses users and breaks references

```python
# Delete task 2, then create new task
# New task gets ID 3 (not 2)
next_id = 3  # Continues incrementing; never reset
```

### Status Toggle (Not Direct Set)

Why: Spec emphasizes toggle operation; this design is clearer

```python
# Instead of: task.status = "complete"
# Use: task.toggle_status()
```

### Error Message Format

Why: Consistency; helps users understand and correct input

```
Error: Task ID 999 not found
Error: Task title cannot be empty
Error: Invalid ID: must be a positive integer
```

## Dependency Injection (Optional for Phase I)

For testing flexibility, pass dependencies to functions/classes:

```python
# Instead of:
class CLIInterface:
    def __init__(self):
        self.manager = TaskManager()

# Use:
class CLIInterface:
    def __init__(self, manager: TaskManager):
        self.manager = manager

# Then in main:
manager = TaskManager()
cli = CLIInterface(manager)
```

This enables mocking in tests without side effects.

## Running the Application

### Start

```bash
python src/main.py
```

### Tests

```bash
pytest tests/ -v --cov=src --cov-report=term-missing
```

Requirements:
- 80%+ coverage
- All tests pass before merge
- Integration tests validate all 5 user stories

## Common Implementation Pitfalls

1. **Resetting next_id on delete**: Don't reset counter; break ID immutability
2. **Modifying created_at**: Keep immutable; users depend on accurate creation time
3. **Allowing invalid status values**: Restrict to "incomplete"/"complete" enum
4. **Case-sensitive menu input**: Always normalize to lowercase for comparison
5. **Missing input validation**: Validate at TaskManager level; don't rely on CLI
6. **No error messages in exceptions**: Include actionable messages (see contract)
7. **Silent failures**: Log and display all errors; never silently skip operations

## Acceptance Criteria Mapping

| Spec Requirement | Implementation Location | Test File |
|------------------|----------------------|-----------|
| Add Task (US1) | TaskManager.add_task() | test_task_manager.py, test_cli_workflow.py |
| View Tasks (US2) | CLIInterface.display_tasks() | test_cli_interface.py, test_cli_workflow.py |
| Toggle Status (US3) | TaskManager.toggle_task_status() | test_task_manager.py, test_cli_workflow.py |
| Update Task (US4) | TaskManager.update_task() | test_task_manager.py, test_cli_workflow.py |
| Delete Task (US5) | TaskManager.delete_task() | test_task_manager.py, test_cli_workflow.py |
| Input Validation | TaskManager + CLIInterface | test_task_manager.py, test_cli_interface.py |
| Error Messages | CLIInterface | test_cli_interface.py, test_cli_workflow.py |
| Menu Loop | main.py | test_cli_workflow.py (integration) |

## Next Steps

1. Create pyproject.toml with Python 3.11+ requirement
2. Set up pytest configuration in pyproject.toml
3. Create source directory structure
4. Begin with Task model + tests (Phase 1)
5. Move to TaskManager + tests (Phase 2)
6. Move to CLIInterface + tests (Phase 3)
7. Integrate in main.py + integration tests (Phase 4)
8. Validate 80%+ coverage; all tests passing
9. Code review against spec and data-model.md contracts
10. PR submission with reference to tasks.md
