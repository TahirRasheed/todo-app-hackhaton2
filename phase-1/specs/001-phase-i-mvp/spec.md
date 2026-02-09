# Feature Specification: Phase I - MVP Console Todo Application

**Feature Branch**: `001-phase-i-mvp`
**Created**: 2026-01-02
**Status**: Draft
**Input**: User description: "Create the Phase I specification for the Evolution of Todo project with in-memory Python console application, single user, no persistence."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Add a New Task (Priority: P1)

A user wants to add a new task to their todo list. The user launches the application, selects the "Add Task" option from the menu, enters a task title and optional description, and the system confirms the task has been created and is ready to track.

**Why this priority**: Creating tasks is the foundational feature of a todo application. Without the ability to add tasks, no other feature has value. This is essential for an MVP.

**Independent Test**: Can be fully tested by launching the application, selecting "Add Task," entering a task title, and verifying the task appears in the task list with a unique ID and "incomplete" status. This demonstrates a complete end-to-end flow and delivers immediate value.

**Acceptance Scenarios**:

1. **Given** the application is running with an empty task list, **When** the user selects "Add Task" and enters title "Buy groceries", **Then** the system displays "Task created successfully (ID: 1)" and the task list now contains 1 task.
2. **Given** the application is running with 2 existing tasks, **When** the user selects "Add Task" and enters title "Write report" with description "Quarterly report", **Then** the system displays "Task created successfully (ID: 3)" with the next available ID, and the task is added to the list.
3. **Given** the "Add Task" dialog is open, **When** the user submits an empty task title, **Then** the system displays an error message "Task title cannot be empty" and returns to the menu without creating a task.

---

### User Story 2 - View All Tasks (Priority: P1)

A user wants to see all their current tasks organized in a readable format. The user selects the "View Tasks" option from the menu and the system displays a complete list of all tasks with their current status, allowing the user to review everything at a glance.

**Why this priority**: Viewing the task list is equally critical to creating tasks. The user must be able to see what they've created in order to take action. This directly supports the primary use case of task tracking.

**Independent Test**: Can be fully tested by adding 3 tasks via "Add Task" feature, then selecting "View Tasks" and verifying all 3 tasks are displayed with their IDs, titles, status (complete/incomplete), and in a clear, readable format. This works independently of the Add Task feature.

**Acceptance Scenarios**:

1. **Given** an empty task list, **When** the user selects "View Tasks", **Then** the system displays "No tasks. Use 'Add Task' to create one."
2. **Given** the task list contains 3 tasks (ID 1: "Buy milk" incomplete, ID 2: "Pay bills" complete, ID 3: "Read book" incomplete), **When** the user selects "View Tasks", **Then** the system displays all 3 tasks in a table format with columns: ID, Title, Status, and each task is clearly visible.
3. **Given** the task list contains tasks with long titles, **When** the user selects "View Tasks", **Then** the system displays the full title (or truncates with "..." if necessary) and all information remains readable.

---

### User Story 3 - Mark Task Complete or Incomplete (Priority: P2)

A user wants to mark tasks as complete when finished or incomplete if they need to redo them. The user selects a task ID and toggles its status, and the system confirms the status change. This allows the user to track which tasks are done.

**Why this priority**: Status tracking is core to task management and directly impacts the user's ability to see progress. However, it's slightly lower than viewing tasks because the application can function with tasks stuck in "incomplete" status during initial MVP testing.

**Independent Test**: Can be fully tested by creating a task (via US1), then using the "Toggle Task Status" feature to mark it complete, then viewing the task list (via US2) to verify the status changed. The feature is independently functional.

**Acceptance Scenarios**:

1. **Given** task ID 1 exists with status "incomplete", **When** the user selects "Toggle Task Status" and enters ID 1, **Then** the system displays "Task 1 marked complete" and the task status changes to "complete".
2. **Given** task ID 2 exists with status "complete", **When** the user toggles its status, **Then** the system displays "Task 2 marked incomplete" and status reverts to "incomplete".
3. **Given** the user enters a task ID that does not exist, **When** they try to toggle the status, **Then** the system displays "Error: Task ID 999 not found" and no action occurs.

---

### User Story 4 - Update Task Details (Priority: P2)

A user wants to modify the title or description of an existing task without deleting it. The user selects a task ID, chooses what to update (title or description), enters the new value, and the system confirms the update and reflects the change immediately.

**Why this priority**: Editing tasks is important for correcting mistakes or refining task details, but it's not as critical as creating, viewing, and marking tasks complete. An MVP can function without edit capability for an initial user test.

**Independent Test**: Can be fully tested by creating a task with title "Incomplete task" (US1), then updating the title to "Complete task" using the "Update Task" feature, and verifying the change via "View Tasks" (US2). Works independently.

**Acceptance Scenarios**:

1. **Given** task ID 1 exists with title "Buy groceries", **When** the user selects "Update Task" and changes the title to "Buy groceries and cook dinner", **Then** the system displays "Task 1 updated successfully" and the new title is visible.
2. **Given** task ID 2 exists with description "None", **When** the user selects "Update Task" and adds description "Deadline: Friday", **Then** the system confirms the update and the description is now stored.
3. **Given** the user attempts to update a task ID that doesn't exist, **When** they enter ID 999, **Then** the system displays "Error: Task ID 999 not found" and no update occurs.

---

### User Story 5 - Delete a Task (Priority: P3)

A user wants to remove a task permanently from their list. The user selects a task ID, confirms deletion, and the system removes the task. This allows the user to clean up their task list.

**Why this priority**: Deletion is useful but not essential for an MVP. Users can still track tasks even if old ones accumulate. However, it's a common task management feature and adds polish to the application.

**Independent Test**: Can be fully tested by creating 3 tasks (US1), then deleting task ID 2, and verifying via "View Tasks" (US2) that only 2 tasks remain (IDs 1 and 3). Works independently of other features.

**Acceptance Scenarios**:

1. **Given** task ID 2 exists, **When** the user selects "Delete Task" and enters ID 2, **Then** the system displays "Task 2 deleted successfully" and the task no longer appears in the task list.
2. **Given** the task list contains 3 tasks, **When** the user deletes task ID 1, **Then** tasks with IDs 2 and 3 remain, and IDs are not reused (next new task gets ID 4, not ID 1).
3. **Given** the user attempts to delete a task ID that doesn't exist, **When** they enter ID 999, **Then** the system displays "Error: Task ID 999 not found" and no deletion occurs.

---

### Edge Cases

- What happens when the user enters invalid input (non-numeric task ID, extremely long task title)?
- How does the system handle rapid successive commands (e.g., add and immediately delete)?
- What is the behavior if the user exits the application and restarts it (no persistence, so all tasks are lost)?
- How does the menu handle case sensitivity (should "ADD TASK", "add task", and "Add Task" all work)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display an interactive menu with options: "Add Task", "View Tasks", "Toggle Task Status", "Update Task", "Delete Task", and "Exit".
- **FR-002**: System MUST allow users to add a new task with a required title and optional description.
- **FR-003**: System MUST assign a unique, auto-incrementing ID to each task (starting at 1).
- **FR-004**: System MUST store tasks in memory with at least the following properties: ID, title, description, status (complete/incomplete), creation timestamp.
- **FR-005**: System MUST display all tasks in a readable format (table or list) with ID, title, status, and description visible.
- **FR-006**: System MUST allow users to toggle a task's status between "complete" and "incomplete" by providing the task ID.
- **FR-007**: System MUST allow users to update a task's title or description by providing the task ID and new value.
- **FR-008**: System MUST allow users to delete a task by providing the task ID with a confirmation prompt.
- **FR-009**: System MUST validate all user input (reject empty titles, non-numeric IDs, non-existent task references) and display clear error messages.
- **FR-010**: System MUST handle the "Exit" command gracefully and terminate the application.
- **FR-011**: System MUST treat task IDs as case-insensitive numeric values; all menu options should be case-insensitive.
- **FR-012**: System MUST NOT persist data to disk or database; all tasks are lost when the application exits.

### Key Entities

- **Task**: Represents a single todo item with properties:
  - **ID**: Unique auto-incrementing integer (1, 2, 3, ...). Immutable once created.
  - **Title**: Required string (1-500 characters). The main description of the task.
  - **Description**: Optional string (0-2000 characters). Additional details about the task.
  - **Status**: Enum with two values: "incomplete" (default) or "complete". Can be toggled.
  - **CreatedAt**: Timestamp of when the task was created (ISO format). Set automatically.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can create a task, view it in the list, toggle its status, update it, and delete it within 5 minutes without documentation, demonstrating all core features work intuitively.
- **SC-002**: The application correctly handles 100 tasks in memory without performance degradation (response time remains under 1 second for any user action).
- **SC-003**: All error messages are clear and actionable (e.g., "Task ID not found" rather than a generic error), allowing users to correct invalid input on the first attempt 90% of the time.
- **SC-004**: The application runs without crashes for a complete user session (create 10 tasks, modify 5, delete 2, exit) demonstrating stability.

### Assumptions

- "In-memory" means tasks are stored in a Python data structure (list, dictionary) during runtime and are completely lost when the application exits.
- "Single user" means only one person interacts with the application at a time; no multi-user or concurrency concerns.
- "No persistence" confirms no database, file storage, or any data recovery mechanism beyond the current session.
- Task IDs are immutable: deleting task 2 does not renumber remaining tasks.
- The menu is text-based, presented in a loop until the user selects "Exit".
- Case-insensitivity applies to menu options and task ID input (both accept lowercase and uppercase).

### Constraints

- **Phase I Scope**: Strictly limited to basic CRUD operations for tasks. No reminders, scheduling, subtasks, categories, priorities, deadlines, or any advanced features.
- **No Future-Phase Features**: Multi-user support, authentication, persistence, web/API interfaces, and integration with other systems are explicitly excluded from Phase I.
- **Technology-Agnostic Spec**: This specification does not prescribe Python, FastAPI, or any implementation details; those are for the Plan phase.
