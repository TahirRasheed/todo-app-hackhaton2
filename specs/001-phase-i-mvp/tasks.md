---
description: "Task list for Phase I MVP console todo application implementation"
---

# Tasks: Phase I - MVP Console Todo Application

**Input**: Design documents from `/specs/001-phase-i-mvp/`
**Prerequisites**: plan.md ✅, spec.md ✅, data-model.md ✅, contracts/cli-interface.md ✅, quickstart.md ✅

**Organization**: Tasks are grouped by user story (US1-US5) to enable independent implementation and testing of each story.

**Testing Strategy**: Test-First Development (TDD) - tests MUST be written before implementation and MUST PASS before merging

**Test Coverage**: 80%+ required per global constitution

## Implementation Strategy

Phase I follows incremental delivery with clear user story boundaries:

1. **Phase 1: Setup** - Project structure, dependencies, test infrastructure
2. **Phase 2: Foundational** - Task model + TaskManager (blocking prerequisite for all stories)
3. **Phase 3: US1 (P1)** - Add Task - Core creation functionality
4. **Phase 4: US2 (P1)** - View Tasks - Display all tasks (parallel with US1 possible post-foundation)
5. **Phase 5: US3 (P2)** - Toggle Status - Mark tasks complete/incomplete
6. **Phase 6: US4 (P2)** - Update Task - Modify existing task details
7. **Phase 7: US5 (P3)** - Delete Task - Remove tasks from list
8. **Phase 8: Polish** - CLI integration, error handling edge cases, final testing

**MVP Scope**: US1 (Add Task) alone is viable MVP with basic list display

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and test framework configuration

- [ ] T001 Create project structure per plan.md (src/, tests/, pyproject.toml)
- [ ] T002 Initialize pyproject.toml with Python 3.11+ requirement and pytest configuration
- [ ] T003 [P] Configure pytest with coverage targets (80%+ minimum)
- [ ] T004 [P] Create pytest fixtures (conftest.py) for task test data

**Artifacts Created**:
- `src/` directory
- `tests/unit/`, `tests/integration/` directories
- `pyproject.toml` with Python 3.11+, pytest, pytest-cov
- `tests/conftest.py` with task fixtures

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core Task model and TaskManager that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Data Model Implementation

- [ ] T005 Create Task class in src/models/task.py with fields (id, title, description, status, created_at)
- [ ] T006 [P] Implement Task validation in __post_init__ (title required, non-empty, status enum)
- [ ] T007 [P] Implement Task.toggle_status() method (incomplete ↔ complete)

### Unit Tests for Task Model

- [ ] T008 [P] Write unit tests in tests/unit/test_task.py:
  - [ ] Task creation with valid data
  - [ ] Task creation rejects empty title
  - [ ] Task.toggle_status() toggles between incomplete/complete
  - [ ] Task.created_at is immutable (read-only)
  - [ ] Task.id is immutable (read-only)

### Business Logic Implementation

- [ ] T009 Create TaskManager class in src/services/task_manager.py with:
  - [ ] __init__() - Initialize empty tasks dict and next_id counter
  - [ ] add_task(title, description) - Create task, validate title, return Task with auto-generated ID
  - [ ] get_task(task_id) - Return Task if exists, None otherwise
  - [ ] get_all_tasks() - Return list of all tasks in ID order
  - [ ] update_task(task_id, field, value) - Update "title" or "description", validate, return Task
  - [ ] toggle_task_status(task_id) - Toggle task status, return Task
  - [ ] delete_task(task_id) - Remove task from storage (do NOT reset next_id)

### Unit Tests for TaskManager

- [ ] T010 [P] Write unit tests in tests/unit/test_task_manager.py:
  - [ ] add_task() increments ID sequentially (1, 2, 3...)
  - [ ] add_task() validates title (rejects empty)
  - [ ] get_task() returns task if exists
  - [ ] get_task() returns None if task not found
  - [ ] get_all_tasks() returns empty list initially
  - [ ] get_all_tasks() returns all tasks after adding
  - [ ] update_task() updates title and description independently
  - [ ] update_task() rejects empty title
  - [ ] update_task() raises error for non-existent task
  - [ ] toggle_task_status() toggles status (complete ↔ incomplete)
  - [ ] toggle_task_status() raises error for non-existent task
  - [ ] delete_task() removes task from storage
  - [ ] delete_task() does NOT reuse ID (next_id continues incrementing)
  - [ ] delete_task() raises error for non-existent task

### ID Generation Strategy

- [ ] T011 [P] Create ID generator logic in TaskManager (or separate id_generator.py module):
  - [ ] Auto-incrementing counter starting at 1
  - [ ] Increment on each task creation
  - [ ] No reuse on deletion
  - [ ] Validation: must be positive integer

**Checkpoint**: Foundation phase complete - Task model and TaskManager fully tested and working. User story implementation can now proceed.

---

## Phase 3: User Story 1 - Add a New Task (Priority: P1) 🎯 MVP

**Goal**: Users can create new tasks with title and optional description; system assigns unique ID and confirms creation.

**Independent Test Criteria**: Add 3 tasks via add_task() → verify all exist in task list with sequential IDs (1, 2, 3) and "incomplete" status

**Spec Reference**: [spec.md US1](spec.md#user-story-1---add-a-new-task-priority-p1)
**Plan Reference**: [plan.md Data Structures](plan.md#1-data-structures)

### CLI Interface for Add Task

- [ ] T012 [P] [US1] Create CLIInterface class in src/ui/cli_interface.py with method:
  - [ ] get_user_input(prompt) - Prompt user, return input (strip whitespace)
  - [ ] display_message(msg, msg_type) - Display success/error/info message

- [ ] T013 [US1] Implement add_task_flow() in CLIInterface:
  - [ ] Prompt for task title
  - [ ] Prompt for task description (optional; default to empty)
  - [ ] Call TaskManager.add_task(title, description)
  - [ ] Display: "Task created successfully (ID: {id})"
  - [ ] Handle validation error (empty title): "Task title cannot be empty"
  - [ ] Per contract: [contracts/cli-interface.md Add Task](contracts/cli-interface.md#1-add-task)

### Unit Tests for Add Task CLI

- [ ] T014 [P] [US1] Write unit tests in tests/unit/test_cli_interface.py:
  - [ ] get_user_input() strips whitespace from input
  - [ ] display_message() formats success message correctly
  - [ ] display_message() formats error message with "Error: " prefix

### Integration Tests for Add Task

- [ ] T015 [US1] Write integration test in tests/integration/test_cli_workflow.py:
  - [ ] "Add single task" workflow: Prompt for title → Display confirmation with ID
  - [ ] "Add multiple tasks" workflow: Create 3 tasks → Verify IDs 1, 2, 3
  - [ ] "Reject empty title" workflow: Attempt empty title → Display error → Return to menu

**Checkpoint**: User Story 1 (Add Task) fully functional and testable independently. MVP deliverable.

---

## Phase 4: User Story 2 - View All Tasks (Priority: P1)

**Goal**: Users can see all tasks in readable format (table) with ID, title, and status visible.

**Independent Test Criteria**: Create 3 tasks with different titles → View Tasks → Verify all 3 appear in table format with ID, title, status columns

**Spec Reference**: [spec.md US2](spec.md#user-story-2---view-all-tasks-priority-p1)
**Contract Reference**: [contracts/cli-interface.md View Tasks](contracts/cli-interface.md#2-view-tasks)

### CLI Display Implementation

- [ ] T016 [P] [US2] Implement display_all_tasks() in CLIInterface:
  - [ ] Get all tasks from TaskManager
  - [ ] If empty: Display "No tasks. Use 'Add Task' to create one."
  - [ ] If tasks exist: Format as table with columns: ID | Title | Status
  - [ ] Align columns (ID right-aligned, Title/Status left-aligned)
  - [ ] Per contract: [contracts/cli-interface.md View Tasks format](contracts/cli-interface.md#with-tasks-table-format)

### Unit Tests for View Tasks

- [ ] T017 [P] [US2] Write unit tests in tests/unit/test_cli_interface.py:
  - [ ] display_all_tasks() returns "No tasks" message for empty list
  - [ ] display_all_tasks() formats table with header row
  - [ ] display_all_tasks() displays all tasks with correct columns
  - [ ] display_all_tasks() handles long titles (full display or truncate with "...")

### Integration Tests for View Tasks

- [ ] T018 [US2] Write integration test in tests/integration/test_cli_workflow.py:
  - [ ] "View empty list" workflow: View Tasks → Display empty message
  - [ ] "View multiple tasks" workflow: Add 3 tasks → View → Verify table with all 3 tasks, correct status

**Checkpoint**: User Stories 1 AND 2 both complete. Basic MVP with Create + Read operations fully functional.

---

## Phase 5: User Story 3 - Mark Task Complete/Incomplete (Priority: P2)

**Goal**: Users can toggle task status between incomplete and complete to track progress.

**Independent Test Criteria**: Create task (incomplete) → Toggle → Verify "complete" → Toggle → Verify "incomplete"

**Spec Reference**: [spec.md US3](spec.md#user-story-3---mark-task-complete-or-incomplete-priority-p2)
**Contract Reference**: [contracts/cli-interface.md Toggle Task Status](contracts/cli-interface.md#3-toggle-task-status)

### CLI Interface for Toggle Status

- [ ] T019 [P] [US3] Implement toggle_task_status_flow() in CLIInterface:
  - [ ] Prompt for task ID
  - [ ] Validate ID is positive integer
  - [ ] Call TaskManager.toggle_task_status(task_id)
  - [ ] Display: "Task {id} marked complete" (or "marked incomplete")
  - [ ] Handle error (invalid ID): "Invalid ID: must be a positive integer"
  - [ ] Handle error (task not found): "Error: Task ID {id} not found"
  - [ ] Per contract: [contracts/cli-interface.md Toggle Task Status section](contracts/cli-interface.md#3-toggle-task-status)

### Unit Tests for Toggle Status

- [ ] T020 [P] [US3] Write unit tests in tests/unit/test_cli_interface.py:
  - [ ] validate_task_id() accepts positive integers
  - [ ] validate_task_id() rejects non-numeric input
  - [ ] validate_task_id() rejects zero and negative numbers
  - [ ] display_message() shows correct "marked complete" or "marked incomplete" message

### Integration Tests for Toggle Status

- [ ] T021 [US3] Write integration test in tests/integration/test_cli_workflow.py:
  - [ ] "Toggle incomplete to complete" workflow: Create task → Toggle → View → Verify status change
  - [ ] "Toggle complete to incomplete" workflow: Create → Toggle → Toggle → View → Verify reverted
  - [ ] "Toggle non-existent task" workflow: Toggle ID 999 → Display error → Return to menu

**Checkpoint**: User Stories 1, 2, AND 3 complete. Core CRUD functionality (Create, Read, Update status) fully operational.

---

## Phase 6: User Story 4 - Update Task Details (Priority: P2)

**Goal**: Users can modify task title or description without deleting the task.

**Independent Test Criteria**: Create task "Old title" → Update to "New title" → View → Verify title changed, ID unchanged, status unchanged

**Spec Reference**: [spec.md US4](spec.md#user-story-4---update-task-details-priority-p2)
**Contract Reference**: [contracts/cli-interface.md Update Task](contracts/cli-interface.md#4-update-task)

### CLI Interface for Update Task

- [ ] T022 [P] [US4] Implement update_task_flow() in CLIInterface:
  - [ ] Prompt for task ID
  - [ ] Prompt for field to update ("title" or "description")
  - [ ] Prompt for new value
  - [ ] Call TaskManager.update_task(task_id, field, value)
  - [ ] Display: "Task {id} updated successfully"
  - [ ] Handle errors:
    - [ ] Invalid ID: "Invalid ID: must be a positive integer"
    - [ ] Task not found: "Error: Task ID {id} not found"
    - [ ] Invalid field: "Invalid field. Please choose 'title' or 'description'"
    - [ ] Empty title: "Task title cannot be empty"
  - [ ] Per contract: [contracts/cli-interface.md Update Task section](contracts/cli-interface.md#4-update-task)

### Unit Tests for Update Task

- [ ] T023 [P] [US4] Write unit tests in tests/unit/test_cli_interface.py:
  - [ ] parse_field_choice() accepts "title" and "description" (case-insensitive)
  - [ ] parse_field_choice() rejects invalid field names
  - [ ] Update UI correctly formats success message with task ID

### Integration Tests for Update Task

- [ ] T024 [US4] Write integration test in tests/integration/test_cli_workflow.py:
  - [ ] "Update task title" workflow: Create "Buy milk" → Update to "Buy milk and eggs" → View → Verify
  - [ ] "Update task description" workflow: Create with no description → Update description → View → Verify
  - [ ] "Update non-existent task" workflow: Update ID 999 → Display error → Return to menu
  - [ ] "Reject empty title update" workflow: Update title to empty → Display error → No change

**Checkpoint**: User Stories 1, 2, 3, AND 4 complete. Full CRUD (Create, Read, Update, Delete-status) functional.

---

## Phase 7: User Story 5 - Delete a Task (Priority: P3)

**Goal**: Users can remove tasks from their list to clean up completed or unwanted tasks.

**Independent Test Criteria**: Create 3 tasks → Delete task ID 2 → View → Verify task 2 removed, IDs 1 and 3 remain, next new task gets ID 4

**Spec Reference**: [spec.md US5](spec.md#user-story-5---delete-a-task-priority-p3)
**Contract Reference**: [contracts/cli-interface.md Delete Task](contracts/cli-interface.md#5-delete-task)

### CLI Interface for Delete Task

- [ ] T025 [P] [US5] Implement delete_task_flow() in CLIInterface:
  - [ ] Prompt for task ID
  - [ ] Prompt for confirmation ("yes" or "no", case-insensitive)
  - [ ] If "yes": Call TaskManager.delete_task(task_id), display "Task {id} deleted successfully"
  - [ ] If "no": Display "Delete cancelled.", return to menu
  - [ ] Handle errors:
    - [ ] Invalid ID: "Invalid ID: must be a positive integer"
    - [ ] Task not found: "Error: Task ID {id} not found"
  - [ ] Per contract: [contracts/cli-interface.md Delete Task section](contracts/cli-interface.md#5-delete-task)

### Unit Tests for Delete Task

- [ ] T026 [P] [US5] Write unit tests in tests/unit/test_cli_interface.py:
  - [ ] parse_confirmation() accepts "yes", "Yes", "YES" as true
  - [ ] parse_confirmation() accepts "no", "No", "NO" as false
  - [ ] parse_confirmation() rejects invalid input
  - [ ] display_message() shows correct "deleted successfully" message

### Integration Tests for Delete Task

- [ ] T027 [US5] Write integration test in tests/integration/test_cli_workflow.py:
  - [ ] "Delete task with confirmation" workflow: Create task → Delete with "yes" → View → Task removed
  - [ ] "Cancel delete operation" workflow: Create task → Delete with "no" → View → Task still present
  - [ ] "Delete non-existent task" workflow: Delete ID 999 → Display error → Return to menu
  - [ ] "Verify no ID reuse" workflow: Create 3 tasks (IDs 1, 2, 3) → Delete task 2 → Create new task → Verify ID 4 (not 2)

**Checkpoint**: All 5 user stories (US1-US5) complete. Full feature set (Create, Read, Update, Toggle Status, Delete) fully functional and tested.

---

## Phase 8: CLI Integration & Main Loop

**Purpose**: Connect all components; implement main menu loop and application startup/exit

### Main Application Loop

- [ ] T028 Implement main() function in src/main.py:
  - [ ] Create TaskManager instance
  - [ ] Create CLIInterface instance (pass TaskManager)
  - [ ] Main loop:
    - [ ] Display main menu
    - [ ] Get user menu choice (case-insensitive)
    - [ ] Parse menu choice: "1"/"add"/"add task" → add_task_flow, etc.
    - [ ] Execute corresponding flow
    - [ ] Loop until "6"/"exit"/"quit" selected
  - [ ] Exit gracefully: "Goodbye!" → exit code 0
  - [ ] Per contract: [contracts/cli-interface.md Main Menu](contracts/cli-interface.md#main-menu)

- [ ] T029 [P] Implement display_main_menu() in CLIInterface:
  - [ ] Display formatted menu with 6 options (Add, View, Toggle, Update, Delete, Exit)
  - [ ] Per contract: [contracts/cli-interface.md Main Menu layout](contracts/cli-interface.md#main-menu)

- [ ] T030 [P] Implement menu_choice_handler() in CLIInterface:
  - [ ] Parse menu choice (case-insensitive): "1"/"add"/"add task" all → "add"
  - [ ] Validate choice is one of: add, view, toggle, update, delete, exit
  - [ ] Handle invalid choice: "Error: Please enter a valid option (1-6, add, view, toggle, update, delete, exit)"

### Input Validation & Error Handling

- [ ] T031 [P] Implement input validation functions (consolidate validation):
  - [ ] normalize_menu_choice(input) → lowercase, strip whitespace
  - [ ] validate_menu_choice(choice) → return error if invalid
  - [ ] validate_task_id(input) → parse to int, reject non-numeric, zero, negative
  - [ ] validate_title(input) → reject empty/whitespace-only
  - [ ] validate_field_choice(input) → accept "title" or "description" (case-insensitive)
  - [ ] validate_confirmation(input) → accept "yes"/"no" (case-insensitive)
  - [ ] All error messages match contract format: "Error: [message]"

### Integration Tests for Main Loop

- [ ] T032 [US1+US2+US3+US4+US5] Write complete end-to-end integration tests in tests/integration/test_cli_workflow.py:
  - [ ] "Complete user workflow" workflow:
    - [ ] Start application
    - [ ] Add task "Buy groceries"
    - [ ] Add task "Pay bills"
    - [ ] View tasks (verify 2 tasks displayed)
    - [ ] Toggle task 1 to complete
    - [ ] Update task 2 description to "Due Friday"
    - [ ] Delete task 1
    - [ ] View tasks (verify 1 task remains)
    - [ ] Exit application
  - [ ] "Invalid input handling" workflow:
    - [ ] Add with empty title → Error → Return to menu
    - [ ] Toggle ID "abc" → Error → Return to menu
    - [ ] Delete ID 999 → Error → Return to menu
    - [ ] Invalid menu choice → Error → Redisplay menu
  - [ ] "Menu case-insensitivity" workflow:
    - [ ] "ADD" → Add task flow
    - [ ] "View" → View tasks
    - [ ] "exit" → Exit application

### Unit Tests for Main Loop

- [ ] T033 [P] Write unit tests in tests/unit/test_cli_interface.py:
  - [ ] normalize_menu_choice() normalizes case and whitespace
  - [ ] validate_menu_choice() accepts all valid options
  - [ ] validate_menu_choice() rejects invalid options
  - [ ] menu_choice_handler() returns correct flow function for each choice

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Edge cases, error recovery, test coverage, and final validation

### Error Handling & Edge Cases

- [ ] T034 [P] Handle edge cases from spec:
  - [ ] Rapid successive commands (add, delete, view, etc. in quick succession)
  - [ ] Long task titles (>100 chars) → Display full or truncate correctly
  - [ ] Unicode/special characters in titles and descriptions
  - [ ] Task IDs as strings with leading zeros ("001") → Normalize or reject
  - [ ] Menu input with extra whitespace ("  add task  ") → Parse correctly

- [ ] T035 [P] Add user-friendly error recovery:
  - [ ] All error messages follow "Error: [specific issue]" format
  - [ ] Suggestions in errors: "Invalid ID: must be a positive integer"
  - [ ] After error, return to menu (don't crash or hang)
  - [ ] Per contract: [contracts/cli-interface.md Error Message Format](contracts/cli-interface.md#error-message-format)

### Test Coverage & Validation

- [ ] T036 [P] Verify 80%+ test coverage:
  - [ ] Run: `pytest tests/ -v --cov=src --cov-report=term-missing`
  - [ ] Confirm coverage >= 80% for all modules (models, services, ui)
  - [ ] Identify and cover any gaps

- [ ] T037 [P] Verify all acceptance scenarios from spec are testable:
  - [ ] Run all 13 acceptance scenarios from spec.md (US1-US5)
  - [ ] Each scenario passes end-to-end
  - [ ] Run all 4 success criteria (SC-001 through SC-004)

- [ ] T038 Perform manual acceptance testing (per spec success criteria):
  - [ ] SC-001: Complete all 5 operations in <5 minutes without documentation
  - [ ] SC-002: Handle 100 tasks without degradation (<1s response)
  - [ ] SC-003: All error messages clear and actionable
  - [ ] SC-004: Stable session with 10 creates, 5 updates, 2 deletes, exit

### Final Validation & Documentation

- [ ] T039 Validate all code against spec and plan:
  - [ ] No new features introduced (spec-driven only)
  - [ ] All 12 functional requirements (FR-001 → FR-012) implemented
  - [ ] All 5 user stories (US1-US5) fully functional
  - [ ] No persistence (confirm data lost on exit)
  - [ ] Single-user, no concurrency
  - [ ] Menu-based CLI only

- [ ] T040 [P] Update README or QUICKSTART with:
  - [ ] How to run: `python src/main.py`
  - [ ] How to test: `pytest tests/ -v --cov=src`
  - [ ] Brief usage examples (per contract workflows)

---

## Dependencies & Parallel Execution

### Dependency Graph

```
Phase 1 (Setup)
  ↓
Phase 2 (Foundation: Task + TaskManager)
  ├→ Phase 3 (US1: Add Task)
  │    ├→ Phase 4 (US2: View Tasks) [parallel possible after Phase 2]
  │    ├→ Phase 5 (US3: Toggle Status)
  │    ├→ Phase 6 (US4: Update Task)
  │    └→ Phase 7 (US5: Delete Task)
  ├→ (All user stories can be parallelized post-Foundation)
  └→ Phase 8 (CLI Integration & Main Loop)
       └→ Phase 9 (Polish & Edge Cases)
```

### Parallel Execution Opportunities

**After Phase 2 (Foundation) completes**, these can run in parallel:

- T012-T015 (US1 CLI + tests) can run in parallel with T016-T018 (US2 display + tests)
- T019-T021 (US3 toggle + tests) can run in parallel with T022-T024 (US4 update + tests)
- T025-T027 (US5 delete + tests) can run independent after Foundation
- T031 (Input validation) can start during US implementation, complete by Phase 8

**Sequential (Must Complete in Order)**:

1. T001-T004 (Phase 1 Setup)
2. T005-T011 (Phase 2 Foundation - Task model, TaskManager)
3. Phase 8 (T028-T030) requires all 5 user stories functional

---

## Task Summary

| Phase | Name | Task Count | Status |
|-------|------|-----------|--------|
| 1 | Setup | T001-T004 (4 tasks) | Foundational |
| 2 | Foundation | T005-T011 (7 tasks) | **BLOCKING** |
| 3 | US1: Add Task | T012-T015 (4 tasks) | P1 - MVP |
| 4 | US2: View Tasks | T016-T018 (3 tasks) | P1 |
| 5 | US3: Toggle Status | T019-T021 (3 tasks) | P2 |
| 6 | US4: Update Task | T022-T024 (3 tasks) | P2 |
| 7 | US5: Delete Task | T025-T027 (3 tasks) | P3 |
| 8 | CLI Integration | T028-T033 (6 tasks) | Integrating |
| 9 | Polish | T034-T040 (7 tasks) | Hardening |
| **TOTAL** | | **40 tasks** | |

---

## Test Coverage Summary

**Total Tests to Write**: ~50 test cases across unit and integration

| Category | Location | Test Count |
|----------|----------|-----------|
| Task Model Unit | tests/unit/test_task.py | ~5 tests |
| TaskManager Unit | tests/unit/test_task_manager.py | ~14 tests |
| CLI Interface Unit | tests/unit/test_cli_interface.py | ~20+ tests |
| Integration Workflows | tests/integration/test_cli_workflow.py | ~15 tests |
| **Total** | | **~50 tests** |

**Coverage Target**: 80%+ across src/ modules

---

## Acceptance Criteria Verification

Each user story maps to spec acceptance scenarios:

| User Story | Spec Scenarios | Implementation Tasks | Tests |
|-----------|----------------|----------------------|-------|
| US1: Add Task | 3 scenarios (SC1-SC3) | T012-T015 | T014-T015 |
| US2: View Tasks | 3 scenarios (SC1-SC3) | T016-T018 | T017-T018 |
| US3: Toggle Status | 3 scenarios (SC1-SC3) | T019-T021 | T020-T021 |
| US4: Update Task | 3 scenarios (SC1-SC3) | T022-T024 | T023-T024 |
| US5: Delete Task | 3 scenarios (SC1-SC3) | T025-T027 | T026-T027 |

All 13 acceptance scenarios testable via integration tests (T015, T018, T021, T024, T027, T032).

---

## Success Criteria (from spec.md)

- **SC-001**: User completes all operations in <5 minutes → Verified by T038 manual testing
- **SC-002**: Handles 100 tasks <1s response → Verified by T032 (load test) + T038
- **SC-003**: Clear error messages, 90% first-attempt recovery → Verified by T032 + T038
- **SC-004**: Stable session (10 creates, 5 updates, 2 deletes, exit) → Verified by T032 + T038

---

## Notes

- **Test-First**: All tests written BEFORE implementation code
- **TDD Cycle**: Red (test fails) → Green (implement) → Refactor (clean up)
- **80%+ Coverage**: Constitution requirement; use `pytest --cov=src` to verify
- **Atomic Tasks**: Each task should be completable in 1-2 hours by an agent
- **Phase I Only**: No persistence, authentication, web frameworks, or future features
- **Integration**: Main loop (T028) depends on all 5 user stories functional
