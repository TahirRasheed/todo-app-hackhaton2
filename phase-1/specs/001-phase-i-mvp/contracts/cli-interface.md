# CLI Interface Contract: Phase I - MVP Console Todo Application

**Created**: 2026-01-02
**Format**: Text-based menu interface contract
**Binding**: All implementation must conform to this contract for acceptance

## User Interface Flow

### Main Menu

Displayed at application start and after each operation:

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
>
```

### Input Handling

- **Case-insensitive**: User can enter "add task", "ADD TASK", "Add Task", "1" → all accepted
- **Whitespace-tolerant**: Leading/trailing spaces trimmed
- **Invalid input**: If user enters invalid menu option, display:
  ```
  Error: Please enter a valid option (1-6, add, view, toggle, update, delete, exit)
  ```

## Operation Contracts

### 1. Add Task

**Menu Selection**: "1", "add", "add task"

**Interaction Flow**:

```
Enter task title: Buy groceries
Enter task description (optional, press Enter to skip):
Task created successfully (ID: 1)
```

**Validation Errors**:

```
Enter task title:
Error: Task title cannot be empty

[Returns to main menu]
```

**Error Messages**:
- Empty title: "Task title cannot be empty"

**Success Message**: "Task created successfully (ID: {id})"

**Next State**: Return to main menu

### 2. View Tasks

**Menu Selection**: "2", "view", "view tasks"

**Empty List**:

```
No tasks. Use 'Add Task' to create one.
```

**With Tasks** (Table Format):

```
ID | Title                        | Status
---+------------------------------+---------
1  | Buy groceries                | incomplete
2  | Pay bills                    | complete
3  | Write quarterly report       | incomplete
```

**Behavior**:
- Display all tasks in order by ID (ascending)
- Show columns: ID, Title, Status
- Align columns for readability
- Long titles: Display full title if possible; truncate with "..." if necessary
- Return to main menu after display

### 3. Toggle Task Status

**Menu Selection**: "3", "toggle", "toggle task status"

**Interaction Flow**:

```
Enter task ID to toggle: 1
Task 1 marked complete

[Returns to main menu]
```

**Error Cases**:

```
Enter task ID to toggle: 999
Error: Task ID 999 not found

[Returns to main menu]
```

```
Enter task ID to toggle: abc
Error: Invalid ID: must be a positive integer

[Returns to main menu]
```

**Success Messages**:
- "Task {id} marked complete" (when toggling to complete)
- "Task {id} marked incomplete" (when toggling to incomplete)

**Error Messages**:
- "Task ID {id} not found"
- "Invalid ID: must be a positive integer"

### 4. Update Task

**Menu Selection**: "4", "update", "update task"

**Interaction Flow**:

```
Enter task ID to update: 1
What would you like to update? (title or description): title
Enter new title: Buy groceries and cook dinner
Task 1 updated successfully

[Returns to main menu]
```

**Error Cases**:

```
Enter task ID to update: 999
Error: Task ID 999 not found

[Returns to main menu]
```

```
Enter task ID to update: 1
What would you like to update? (title or description): priority
Error: Invalid field. Please choose 'title' or 'description'

[Returns to menu/re-prompts]
```

```
Enter task ID to update: 1
What would you like to update? (title or description): title
Enter new title:
Error: Task title cannot be empty

[Returns to main menu without updating]
```

**Success Messages**:
- "Task {id} updated successfully"

**Error Messages**:
- "Task ID {id} not found"
- "Invalid field. Please choose 'title' or 'description'"
- "Task title cannot be empty"

### 5. Delete Task

**Menu Selection**: "5", "delete", "delete task"

**Interaction Flow**:

```
Enter task ID to delete: 2
Are you sure? (yes or no): yes
Task 2 deleted successfully

[Returns to main menu]
```

**Cancel Operation**:

```
Enter task ID to delete: 2
Are you sure? (yes or no): no
Delete cancelled.

[Returns to main menu]
```

**Error Cases**:

```
Enter task ID to delete: 999
Error: Task ID 999 not found

[Returns to main menu]
```

```
Enter task ID to delete: abc
Error: Invalid ID: must be a positive integer

[Returns to main menu]
```

**Success Messages**:
- "Task {id} deleted successfully"

**Error Messages**:
- "Task ID {id} not found"
- "Invalid ID: must be a positive integer"

**Cancellation Message**:
- "Delete cancelled."

### 6. Exit

**Menu Selection**: "6", "exit", "quit"

**Interaction Flow**:

```
Goodbye!
[Application terminates]
```

**Behavior**:
- No tasks are saved
- Application closes cleanly
- Exit code: 0 (success)

## Error Message Format

All error messages follow format:

```
Error: [specific message]
```

Examples:
- "Error: Task title cannot be empty"
- "Error: Task ID 999 not found"
- "Error: Invalid ID: must be a positive integer"

## Display Format Standards

### List Table

```
ID | Title                    | Status
---+---------------------------+---------
```

- Column alignment: ID (right), Title (left), Status (left)
- Min width: ID=4, Title=25, Status=12
- Separator: Pipe (|)
- Header row: Underlined with dashes

### Messages

- Success: "Task created successfully (ID: 1)"
- Errors: "Error: [description]"
- Confirmations: "[Action] completed" or "[Field] [status]"
- Prompts: "Enter [what]: " (with trailing space)

## Input Validation Contract

| Input Type | Constraints | Behavior |
|-----------|------------|----------|
| Menu Option | 1-6, case-insensitive | Invalid → display error; valid → execute |
| Task ID | Positive integer | Invalid → display error; not found → display error |
| Title | Non-empty string, 1-500 chars | Empty → error; over 500 → display as-is or truncate |
| Description | 0-2000 chars | Any string accepted, including empty |
| Status Field | "title" or "description" | Invalid → error; case-insensitive |
| Confirmation | "yes" or "no" (case-insensitive) | Invalid → re-prompt or default to "no" |

## Success Criteria Mapping

| Success Criterion | Interface Requirement |
|------------------|-----------------------|
| SC-001: Intuitive 5-minute usage | Clear menu, numbered options, plain language prompts |
| SC-003: Clear error messages | All errors use "Error: [specific message]" format |
| SC-004: Stability | All operations complete without crashes; menu loops until exit |

## Examples of Complete Workflows

### Workflow 1: Create and View

```
========================================
        TODO APPLICATION - MAIN MENU
========================================

What would you like to do?
> add

Enter task title: Buy milk
Enter task description (optional):
Task created successfully (ID: 1)

========================================
        TODO APPLICATION - MAIN MENU
========================================

What would you like to do?
> view

ID | Title     | Status
---+-----------+----------
1  | Buy milk  | incomplete

========================================
        TODO APPLICATION - MAIN MENU
========================================

What would you like to do?
> exit

Goodbye!
```

### Workflow 2: Toggle Status

```
What would you like to do?
> 3

Enter task ID to toggle: 1
Task 1 marked complete

[Menu redisplayed]

What would you like to do?
> view

ID | Title     | Status
---+-----------+----------
1  | Buy milk  | complete

[Menu redisplayed]

What would you like to do?
> 3

Enter task ID to toggle: 1
Task 1 marked incomplete

[Menu redisplayed]
```

### Workflow 3: Error Handling

```
What would you like to do?
> 3

Enter task ID to toggle: abc
Error: Invalid ID: must be a positive integer

[Menu redisplayed]

What would you like to do?
> toggle

Enter task ID to toggle: 999
Error: Task ID 999 not found

[Menu redisplayed]
```
