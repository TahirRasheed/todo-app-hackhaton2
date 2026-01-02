"""
Task model for Phase I Todo Application.

Represents a single todo item with full lifecycle management.
Implements validation and state management per data-model.md.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal


@dataclass
class Task:
    """
    Represents a single todo item.

    Fields:
        id: Unique auto-incrementing integer (immutable)
        title: Required task description (1-500 characters)
        description: Optional additional details (0-2000 characters)
        status: Task status - "incomplete" or "complete"
        created_at: ISO 8601 timestamp (immutable, auto-set)

    Validation:
        - title: Required, non-empty, non-whitespace-only
        - status: Must be "incomplete" or "complete"
    """

    id: int
    title: str
    description: str = ""
    status: Literal["incomplete", "complete"] = "incomplete"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def __post_init__(self) -> None:
        """
        Validate task fields after initialization.

        Raises:
            ValueError: If title is empty or whitespace-only
            ValueError: If status is not "incomplete" or "complete"
        """
        # Validate title
        if not self.title or not self.title.strip():
            raise ValueError("Task title cannot be empty")

        # Strip whitespace from title
        self.title = self.title.strip()

        # Validate status
        if self.status not in ("incomplete", "complete"):
            raise ValueError(
                f"Invalid status '{self.status}'. Must be 'incomplete' or 'complete'."
            )

        # Ensure created_at is set
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

    def toggle_status(self) -> None:
        """
        Toggle task status between "incomplete" and "complete".

        This is the only way to change task status (except creation).
        """
        if self.status == "incomplete":
            self.status = "complete"
        else:
            self.status = "incomplete"

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"Task(id={self.id}, title='{self.title}', "
            f"status='{self.status}', created_at='{self.created_at}')"
        )
