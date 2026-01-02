# Data Model: Phase I - MVP Console Todo Application

**Created**: 2026-01-02
**Derived From**: [spec.md](spec.md) Requirements, Entities, and Acceptance Criteria

## Entities

### Task

Represents a single todo item with full lifecycle management.

#### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | Unique, auto-incrementing, immutable | Assigned at creation; never changes or reused |
| `title` | String | Required, 1-500 characters | Main task description |
| `description` | String | Optional, 0-2000 characters | Additional details; defaults to empty string |
| `status` | Enum | "incomplete" or "complete" | Defaults to "incomplete"; can be toggled |
| `created_at` | ISO 8601 Timestamp | Set automatically at creation | Read-only; never modified |

#### Validation Rules

- **title**: Must not be empty or whitespace-only; enforced at creation and update
- **description**: Optional; accepts any string including empty
- **status**: Must be one of ("incomplete", "complete"); no other values allowed
- **id**: Must be positive integer; generated sequentially without reuse

#### State Transitions

```
Task Creation:
  → id (auto-assigned)
  → title (user-provided, validated)
  → description (user-provided, optional)
  → status = "incomplete" (default)
  → created_at (current time, auto-set)

Status Transition:
  incomplete ↔ complete (toggle operation)
  (reversible; can switch between states multiple times)

Update Operations:
  title: string (any non-empty value)
  description: string (any value, including empty)
  (status changes via toggle only, not direct update)

Deletion:
  Task removed from storage
  ID NOT reused in same session
```

## Storage Model

### In-Memory Data Structures

**TaskStore** (Dictionary):
```python
tasks: Dict[int, Task] = {}
```

**ID Counter** (Integer):
```python
next_id: int = 1
```

### Operations

| Operation | Input | Output | Behavior |
|-----------|-------|--------|----------|
| Create | title (str), description (str, optional) | Task with assigned ID | Validates title; auto-increments next_id |
| Read (all) | None | List[Task] | Returns all tasks in storage |
| Read (by ID) | id (int) | Task or None | Returns task if exists; None if not found |
| Update | id (int), field ("title" or "description"), value (str) | Task or error | Updates field; validates new value |
| Toggle Status | id (int) | Task or error | Switches incomplete ↔ complete |
| Delete | id (int) | None or error | Removes task from storage; next_id not reset |
| List | None | List[Task] | All tasks; empty list if none exist |

### Lifecycle

- **Creation**: Task instantiated with auto-assigned ID, current timestamp
- **Modification**: Title, description, status can be modified; created_at never changes
- **Deletion**: Task removed from dictionary; ID never reused
- **End of Session**: All tasks lost; next_id reset to 1 on next application launch

## Relationships

- **1:1 mapping** of ID to Task (one task per ID)
- **No cross-references** between tasks (standalone tasks)
- **No hierarchies or dependencies** (Phase I only supports flat task list)

## Constraints & Assumptions

### Business Constraints

- **Phase I Scope**: Only basic task properties (id, title, description, status, created_at)
- **No advanced features**: No reminders, due dates, priorities, categories, subtasks (reserved for future phases)
- **No relationships**: Tasks are independent; no parent-child or linking mechanisms

### Technical Constraints

- **In-memory only**: No database, no files, no external storage
- **Single user session**: No concurrent access; no multi-user state isolation
- **No persistence**: Data lost on exit; designed for single-session use
- **Immutable ID**: Once assigned, task ID never changes

## Example Data

### Valid Task

```python
Task(
  id=1,
  title="Buy groceries",
  description="Milk, eggs, bread",
  status="incomplete",
  created_at="2026-01-02T10:30:00"
)
```

### Valid Task (Minimal)

```python
Task(
  id=2,
  title="Pay bills",
  description="",
  status="incomplete",
  created_at="2026-01-02T10:35:00"
)
```

### Valid Task State Transition

```python
# Initial state
Task(..., status="incomplete")

# After toggle
Task(..., status="complete")

# After toggle again
Task(..., status="incomplete")
```

## Invalid Data (Rejected)

- Title: empty string, None, whitespace-only → **Validation error**
- Title: >500 characters → **Accepted but may truncate in display** (spec allows full title or "...")
- Description: >2000 characters → **Accepted** (spec defines 0-2000 chars as guideline, not hard limit)
- Status: "pending", "done", "archived" → **Invalid**; must be "incomplete" or "complete"
- ID: 0, negative, non-integer, "abc" → **Invalid**; must be positive integer
- created_at: user-modifiable → **Not allowed**; auto-set only

## Implementation Notes

### Python Representation

```python
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Task:
    id: int
    title: str
    description: str = ""
    status: str = "incomplete"  # "incomplete" or "complete"
    created_at: str = None  # ISO 8601 format

    def __post_init__(self):
        if not self.title or not self.title.strip():
            raise ValueError("Task title cannot be empty")
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        self.title = self.title.strip()

    def toggle_status(self) -> None:
        """Toggle between incomplete and complete."""
        self.status = "complete" if self.status == "incomplete" else "incomplete"
```

### TaskManager Class

Manages all task operations with validation and error handling:

```python
class TaskManager:
    def __init__(self):
        self.tasks: Dict[int, Task] = {}
        self.next_id: int = 1

    def add_task(self, title: str, description: str = "") -> Task:
        """Create and store a new task; return the created task."""

    def get_task(self, task_id: int) -> Optional[Task]:
        """Retrieve task by ID; return None if not found."""

    def get_all_tasks(self) -> List[Task]:
        """Return list of all tasks in storage order."""

    def update_task(self, task_id: int, field: str, value: str) -> Task:
        """Update task field; raise error if task or field invalid."""

    def toggle_task_status(self, task_id: int) -> Task:
        """Toggle task status; raise error if task not found."""

    def delete_task(self, task_id: int) -> None:
        """Remove task from storage; raise error if not found."""
```

## Mapping to Spec Requirements

| Spec Requirement | Data Model Implementation |
|------------------|--------------------------|
| FR-003: Auto-incrementing ID | `next_id` counter; assigned sequentially |
| FR-004: Task storage with properties | `Task` dataclass with id, title, description, status, created_at |
| FR-002: Title + optional description | `Task.title` (required), `Task.description` (optional) |
| FR-006: Toggle status | `Task.status` enum; toggle operation |
| FR-007: Update title/description | `TaskManager.update_task()` with field selector |
| FR-008: Delete task | `TaskManager.delete_task()` removes from storage |
| FR-009: Input validation | Validation in `Task.__post_init__()` and `TaskManager` methods |
| SC-002: Handle 100+ tasks | Dictionary lookup is O(1); list operations O(n); acceptable for <1s response |
