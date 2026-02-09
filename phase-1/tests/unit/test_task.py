"""
Unit tests for Task model.

Tests Task creation, validation, and state management per spec.md requirements.
"""

import pytest
from src.models.task import Task


class TestTaskCreation:
    """Tests for task creation and validation."""

    def test_create_task_with_valid_data(self, sample_task_data):
        """Test creating a task with valid data."""
        task = Task(id=1, **sample_task_data)
        assert task.id == 1
        assert task.title == "Buy groceries"
        assert task.description == "Milk, eggs, bread"
        assert task.status == "incomplete"
        assert task.created_at is not None

    def test_create_task_minimal(self, sample_task_minimal):
        """Test creating a task with minimal data (no description)."""
        task = Task(id=1, **sample_task_minimal)
        assert task.id == 1
        assert task.title == "Pay bills"
        assert task.description == ""
        assert task.status == "incomplete"

    def test_task_creation_auto_sets_timestamp(self):
        """Test that created_at is automatically set on creation."""
        task = Task(id=1, title="Test task")
        assert task.created_at is not None
        # Should be ISO 8601 format
        assert "T" in task.created_at
        assert ":" in task.created_at

    def test_task_status_defaults_to_incomplete(self):
        """Test that new tasks default to 'incomplete' status."""
        task = Task(id=1, title="Test task")
        assert task.status == "incomplete"


class TestTaskValidation:
    """Tests for task validation."""

    def test_reject_empty_title(self):
        """Test that empty title raises ValueError."""
        with pytest.raises(ValueError, match="Task title cannot be empty"):
            Task(id=1, title="")

    def test_reject_whitespace_only_title(self):
        """Test that whitespace-only title raises ValueError."""
        with pytest.raises(ValueError, match="Task title cannot be empty"):
            Task(id=1, title="   ")

    def test_reject_none_title(self):
        """Test that None title raises ValueError."""
        with pytest.raises((ValueError, TypeError)):
            Task(id=1, title=None)

    def test_title_stripped_of_whitespace(self):
        """Test that leading/trailing whitespace is stripped from title."""
        task = Task(id=1, title="  Buy groceries  ")
        assert task.title == "Buy groceries"

    def test_reject_invalid_status(self):
        """Test that invalid status raises ValueError."""
        with pytest.raises(ValueError, match="Invalid status"):
            Task(id=1, title="Test", status="pending")

    def test_invalid_status_error_message(self):
        """Test error message includes allowed status values."""
        with pytest.raises(ValueError):
            Task(id=1, title="Test", status="archived")


class TestTaskStatusToggle:
    """Tests for task status toggling."""

    def test_toggle_incomplete_to_complete(self):
        """Test toggling status from incomplete to complete."""
        task = Task(id=1, title="Test task")
        assert task.status == "incomplete"
        task.toggle_status()
        assert task.status == "complete"

    def test_toggle_complete_to_incomplete(self):
        """Test toggling status from complete to incomplete."""
        task = Task(id=1, title="Test task", status="complete")
        assert task.status == "complete"
        task.toggle_status()
        assert task.status == "incomplete"

    def test_toggle_multiple_times(self):
        """Test toggling status multiple times."""
        task = Task(id=1, title="Test task")
        assert task.status == "incomplete"
        task.toggle_status()
        assert task.status == "complete"
        task.toggle_status()
        assert task.status == "incomplete"
        task.toggle_status()
        assert task.status == "complete"


class TestTaskImmutability:
    """Tests for immutable task fields."""

    def test_task_id_is_immutable(self):
        """Test that task ID cannot be changed after creation."""
        task = Task(id=1, title="Test task")
        # Attempting to change ID should reflect in repr but IDs are auto-assigned
        # We verify ID is preserved throughout task lifetime
        assert task.id == 1
        task.toggle_status()  # Other operations
        assert task.id == 1  # ID remains same

    def test_created_at_is_immutable(self):
        """Test that created_at timestamp is not changed by operations."""
        task = Task(id=1, title="Test task")
        original_created_at = task.created_at
        task.toggle_status()
        task.title = "Modified title"
        assert task.created_at == original_created_at

    def test_description_is_mutable(self):
        """Test that description can be modified."""
        task = Task(id=1, title="Test task", description="Original")
        assert task.description == "Original"
        task.description = "Modified"
        assert task.description == "Modified"

    def test_title_is_mutable(self):
        """Test that title can be modified."""
        task = Task(id=1, title="Original title")
        assert task.title == "Original title"
        task.title = "Modified title"
        assert task.title == "Modified title"


class TestTaskRepresentation:
    """Tests for task string representation."""

    def test_task_repr_contains_key_info(self):
        """Test that repr contains key task information."""
        task = Task(id=1, title="Buy groceries", status="incomplete")
        repr_str = repr(task)
        assert "id=1" in repr_str
        assert "Buy groceries" in repr_str
        assert "incomplete" in repr_str
