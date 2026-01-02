# Phase I - MVP Console Todo Application

A simple, in-memory console-based todo application built with Python 3.11+.

## Overview

Phase I delivers the MVP for the Evolution of Todo project with the following features:

- **Add Task**: Create new tasks with title and optional description
- **View Tasks**: Display all tasks in a formatted table
- **Toggle Status**: Mark tasks as complete or incomplete
- **Update Task**: Modify task title or description
- **Delete Task**: Remove tasks from the list
- **Menu-Driven CLI**: Simple text-based menu interface
- **In-Memory Storage**: Tasks are stored in memory and lost on exit
- **Input Validation**: Clear error messages for invalid input
- **No Persistence**: Phase I is single-session only (no database, no files)

## Requirements

- Python 3.11 or higher
- No external dependencies (uses Python standard library only)

## Installation

1. Clone or download the repository
2. Navigate to the project directory
3. (Optional) Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. (Optional) Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

## Running the Application

### Basic Usage

```bash
python src/main.py
```

The application will start with an interactive menu:

```
========================================
    TODO APPLICATION - MAIN MENU
========================================

What would you like to do?

1. Add Task
2. View Tasks
3. Toggle Task Status
4. Update Task
5. Delete Task
6. Exit

Please choose an option (1-6) or type the option name:
```

### Menu Options

#### 1. Add Task
- Enter a task title (required, 1-500 characters)
- Enter optional description (press Enter to skip)
- System assigns unique ID and confirms creation

Example:
```
Enter task title: Buy groceries
Enter task description (optional, press Enter to skip): Milk, eggs, bread
Task created successfully (ID: 1)
```

#### 2. View Tasks
- Displays all tasks in a formatted table
- Shows: ID | Title | Status
- Shows empty message if no tasks exist

Example:
```
ID | Title                        | Status
--------------------------------------------------
1  | Buy groceries                | incomplete
2  | Pay bills                    | complete
```

#### 3. Toggle Task Status
- Enter task ID to toggle
- Changes status between "incomplete" and "complete"

Example:
```
Enter task ID to toggle: 1
Task 1 marked complete
```

#### 4. Update Task
- Enter task ID to update
- Choose field: "title" or "description"
- Enter new value

Example:
```
Enter task ID to update: 1
What would you like to update? (title or description): title
Enter new title: Buy groceries and cook dinner
Task 1 updated successfully
```

#### 5. Delete Task
- Enter task ID to delete
- Confirm with "yes" or "no"
- ID is NOT reused (next task gets next sequential ID)

Example:
```
Enter task ID to delete: 2
Are you sure? (yes or no): yes
Task 2 deleted successfully
```

#### 6. Exit
- Gracefully exit the application
- Note: All tasks are lost (no persistence in Phase I)

## Testing

### Run All Tests

```bash
pytest tests/ -v --cov=src --cov-report=term-missing
```

### Run Specific Test Suites

```bash
# Unit tests for models
pytest tests/unit/test_task.py -v

# Unit tests for services
pytest tests/unit/test_task_manager.py -v

# Unit tests for CLI
pytest tests/unit/test_cli_interface.py -v

# Integration tests
pytest tests/integration/test_cli_workflow.py -v
```

### Coverage Report

```bash
pytest tests/ --cov=src --cov-report=html
# Open htmlcov/index.html in browser for detailed report
```

## Project Structure

```
src/
├── __init__.py
├── main.py                    # Application entry point
├── models/
│   ├── __init__.py
│   └── task.py               # Task data class with validation
├── services/
│   ├── __init__.py
│   └── task_manager.py       # Business logic (CRUD operations)
└── ui/
    ├── __init__.py
    └── cli_interface.py      # CLI user interface

tests/
├── __init__.py
├── conftest.py               # Pytest fixtures
├── unit/
│   ├── __init__.py
│   ├── test_task.py          # Task model tests
│   ├── test_task_manager.py  # TaskManager tests
│   └── test_cli_interface.py # CLI tests
└── integration/
    ├── __init__.py
    └── test_cli_workflow.py  # End-to-end workflow tests

pyproject.toml               # Project configuration
README.md                    # This file
```

## Features

### Task Model
- **ID**: Unique auto-incrementing integer (immutable, never reused)
- **Title**: Required task description (1-500 characters)
- **Description**: Optional additional details (0-2000 characters)
- **Status**: "incomplete" (default) or "complete"
- **CreatedAt**: Timestamp automatically set at creation (immutable)

### Business Logic
- Validates all input (title required, status enum, ID type)
- Auto-generates unique IDs starting at 1
- Never reuses task IDs (even after deletion)
- Stores tasks in memory (lost on exit)
- Single-user, single-session operation

### CLI Features
- Case-insensitive menu options
- Friendly error messages with suggestions
- Confirmation dialogs for destructive operations (delete)
- Formatted table display with proper alignment
- Clear indication of task status

## Error Handling

All error messages follow the format: `Error: [specific issue]`

Common errors:

```
Error: Task title cannot be empty
Error: Invalid ID: must be a positive integer
Error: Task ID 999 not found
Error: Invalid field. Please choose 'title' or 'description'
Error: Please enter a valid option (1-6, add, view, toggle, update, delete, exit)
```

## Limitations (Phase I Only)

- **No Persistence**: Data is lost when application exits
- **No Database**: All data stored in memory only
- **No Files**: No file storage or backup capabilities
- **Single User**: No multi-user support or authentication
- **No API**: CLI interface only, no REST or GraphQL APIs
- **No Scheduling**: No reminders or scheduled tasks
- **No Categories**: All tasks in one flat list
- **No Priorities**: Tasks have no priority levels
- **No Deadlines**: No due dates or time-based organization

These features are planned for future phases (Phase II-V).

## Acceptance Criteria

✅ **SC-001**: User can complete all operations in <5 minutes without documentation
✅ **SC-002**: Application handles 100+ tasks without performance degradation (<1 second response)
✅ **SC-003**: All error messages are clear and actionable
✅ **SC-004**: Application is stable through complete user session

## Test Coverage

- **Unit Tests**: ~50 test cases across 4 test modules
- **Integration Tests**: Complete user workflows for all features
- **Code Coverage**: 80%+ across all source modules

## Development Notes

### Architecture
- 3-layer architecture: UI (CLI) → Services (Business Logic) → Models (Data)
- Clear separation of concerns
- Each component independently testable
- Test-driven development (TDD) throughout

### Key Design Decisions
1. **In-Memory Storage**: Simplest approach for MVP (Dict + counter)
2. **No ID Reuse**: Maintains consistency and predictability
3. **Status Toggle**: Dedicated method (not direct assignment)
4. **Input Validation**: At TaskManager level (defensive design)
5. **TDD Approach**: Tests written before implementation

### Standards Compliance
- **PEP 8**: Python style guide followed
- **Type Hints**: Used for clarity (Python 3.11+)
- **Docstrings**: Module, class, and method level documentation
- **Error Handling**: Explicit error messages with context

## Future Phases

See main project documentation for Phase II-V roadmap including:
- Database persistence (Phase II)
- Web UI with Next.js (Phase II)
- Multi-user support with authentication (Phase II)
- Advanced scheduling with Kafka (Phase III)
- Workflow orchestration (Phase IV)
- Enterprise features (Phase V)

## License

MIT License - See LICENSE file for details

## Contact

For questions or issues, refer to the project specification documents in `specs/001-phase-i-mvp/`
