"""
Task Manager service for Phase I Todo Application.

Implements CRUD operations and business logic for task management.
Manages in-memory task storage and auto-incrementing ID generation.
Per data-model.md and plan.md specifications.
"""

from typing import Dict, List, Optional
from src.models.task import Task


class TaskManager:
    """
    Manages all task operations and in-memory storage.

    Implements Create, Read, Update, Delete, and Toggle operations.
    Maintains auto-incrementing task IDs that are never reused.

    Attributes:
        tasks: Dictionary mapping task ID to Task object
        next_id: Auto-incrementing counter for task ID generation
    """

    def __init__(self) -> None:
        """Initialize empty task storage and ID counter."""
        self.tasks: Dict[int, Task] = {}
        self.next_id: int = 1

    def add_task(self, title: str, description: str = "") -> Task:
        """
        Create and store a new task.

        Validates title and auto-generates ID. Task starts with "incomplete" status.

        Args:
            title: Required task title (1-500 characters)
            description: Optional task description (0-2000 characters)

        Returns:
            Created Task with auto-assigned ID

        Raises:
            ValueError: If title is empty or invalid
        """
        # Create task with next auto-generated ID
        task = Task(id=self.next_id, title=title, description=description)

        # Store task
        self.tasks[task.id] = task

        # Increment ID counter for next task (never reset)
        self.next_id += 1

        return task

    def get_task(self, task_id: int) -> Optional[Task]:
        """
        Retrieve a task by ID.

        Args:
            task_id: Task ID to retrieve

        Returns:
            Task if found, None otherwise
        """
        return self.tasks.get(task_id)

    def get_all_tasks(self) -> List[Task]:
        """
        Retrieve all tasks in ID order.

        Returns:
            List of all Task objects sorted by ID
        """
        return sorted(self.tasks.values(), key=lambda t: t.id)

    def update_task(self, task_id: int, field: str, value: str) -> Task:
        """
        Update a task field.

        Args:
            task_id: Task ID to update
            field: Field to update ("title" or "description")
            value: New value for field

        Returns:
            Updated Task

        Raises:
            ValueError: If task not found, field invalid, or value invalid
        """
        # Get task or raise error
        task = self.tasks.get(task_id)
        if task is None:
            raise ValueError(f"Task ID {task_id} not found")

        # Validate field
        if field not in ("title", "description"):
            raise ValueError(f"Invalid field '{field}'. Must be 'title' or 'description'.")

        # Update field with validation
        if field == "title":
            # Validate new title (must not be empty)
            if not value or not value.strip():
                raise ValueError("Task title cannot be empty")
            task.title = value.strip()
        elif field == "description":
            task.description = value

        return task

    def toggle_task_status(self, task_id: int) -> Task:
        """
        Toggle a task's status between "incomplete" and "complete".

        Args:
            task_id: Task ID to toggle

        Returns:
            Task with toggled status

        Raises:
            ValueError: If task not found
        """
        task = self.tasks.get(task_id)
        if task is None:
            raise ValueError(f"Task ID {task_id} not found")

        task.toggle_status()
        return task

    def delete_task(self, task_id: int) -> None:
        """
        Delete a task from storage.

        Does NOT reset next_id counter. Next created task gets next sequential ID.

        Args:
            task_id: Task ID to delete

        Raises:
            ValueError: If task not found
        """
        if task_id not in self.tasks:
            raise ValueError(f"Task ID {task_id} not found")

        del self.tasks[task_id]

    def get_next_id(self) -> int:
        """
        Get the ID that will be assigned to the next task (without creating one).

        Returns:
            Next available task ID
        """
        return self.next_id
