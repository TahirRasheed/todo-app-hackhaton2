"""
Unit tests for TaskManager service.

Tests CRUD operations, ID generation, validation, and error handling.
Per spec.md requirements and data-model.md specifications.
"""

import pytest
from src.services.task_manager import TaskManager
from src.models.task import Task


class TestTaskManagerCreation:
    """Tests for task creation."""

    def test_create_empty_manager(self):
        """Test creating an empty TaskManager."""
        manager = TaskManager()
        assert len(manager.get_all_tasks()) == 0
        assert manager.get_next_id() == 1

    def test_add_single_task(self, sample_task_data):
        """Test adding a single task."""
        manager = TaskManager()
        task = manager.add_task(**sample_task_data)
        assert task.id == 1
        assert task.title == "Buy groceries"
        assert task.status == "incomplete"

    def test_add_task_returns_task_object(self):
        """Test that add_task returns a Task object."""
        manager = TaskManager()
        task = manager.add_task("Test task")
        assert isinstance(task, Task)
        assert task.id == 1

    def test_task_stored_in_manager(self):
        """Test that added task is stored in manager."""
        manager = TaskManager()
        task = manager.add_task("Test task")
        retrieved = manager.get_task(task.id)
        assert retrieved is task

    def test_add_multiple_tasks_increments_id(self):
        """Test that multiple tasks get sequential IDs."""
        manager = TaskManager()
        task1 = manager.add_task("First task")
        task2 = manager.add_task("Second task")
        task3 = manager.add_task("Third task")
        assert task1.id == 1
        assert task2.id == 2
        assert task3.id == 3

    def test_add_task_with_description(self):
        """Test adding task with description."""
        manager = TaskManager()
        task = manager.add_task("Buy groceries", "Milk, eggs, bread")
        assert task.description == "Milk, eggs, bread"

    def test_add_task_without_description(self):
        """Test adding task without description (defaults to empty)."""
        manager = TaskManager()
        task = manager.add_task("Pay bills")
        assert task.description == ""

    def test_add_task_validates_title(self):
        """Test that add_task validates title."""
        manager = TaskManager()
        with pytest.raises(ValueError, match="Task title cannot be empty"):
            manager.add_task("")

    def test_add_task_validates_whitespace_title(self):
        """Test that whitespace-only title is rejected."""
        manager = TaskManager()
        with pytest.raises(ValueError, match="Task title cannot be empty"):
            manager.add_task("   ")


class TestTaskManagerRetrieval:
    """Tests for task retrieval."""

    def test_get_nonexistent_task_returns_none(self):
        """Test that getting non-existent task returns None."""
        manager = TaskManager()
        task = manager.get_task(999)
        assert task is None

    def test_get_existing_task(self):
        """Test retrieving an existing task by ID."""
        manager = TaskManager()
        added = manager.add_task("Test task")
        retrieved = manager.get_task(added.id)
        assert retrieved is added

    def test_get_all_tasks_empty(self):
        """Test getting all tasks from empty manager."""
        manager = TaskManager()
        tasks = manager.get_all_tasks()
        assert isinstance(tasks, list)
        assert len(tasks) == 0

    def test_get_all_tasks_after_adding(self):
        """Test getting all tasks after adding some."""
        manager = TaskManager()
        manager.add_task("First")
        manager.add_task("Second")
        manager.add_task("Third")
        tasks = manager.get_all_tasks()
        assert len(tasks) == 3

    def test_get_all_tasks_returns_sorted_by_id(self):
        """Test that get_all_tasks returns tasks sorted by ID."""
        manager = TaskManager()
        task1 = manager.add_task("First")
        task3 = manager.add_task("Third")
        task2 = manager.add_task("Second")
        manager.delete_task(task2.id)
        tasks = manager.get_all_tasks()
        assert [t.id for t in tasks] == sorted([t.id for t in tasks])


class TestTaskManagerUpdate:
    """Tests for task updates."""

    def test_update_task_title(self):
        """Test updating task title."""
        manager = TaskManager()
        task = manager.add_task("Original title")
        updated = manager.update_task(task.id, "title", "New title")
        assert updated.title == "New title"
        assert task.title == "New title"  # Same object

    def test_update_task_description(self):
        """Test updating task description."""
        manager = TaskManager()
        task = manager.add_task("Test task", "Original description")
        updated = manager.update_task(task.id, "description", "New description")
        assert updated.description == "New description"

    def test_update_nonexistent_task_raises_error(self):
        """Test that updating non-existent task raises ValueError."""
        manager = TaskManager()
        with pytest.raises(ValueError, match="Task ID 999 not found"):
            manager.update_task(999, "title", "New title")

    def test_update_with_invalid_field_raises_error(self):
        """Test that invalid field name raises ValueError."""
        manager = TaskManager()
        task = manager.add_task("Test task")
        with pytest.raises(ValueError, match="Invalid field"):
            manager.update_task(task.id, "priority", "high")

    def test_update_title_to_empty_raises_error(self):
        """Test that updating title to empty raises ValueError."""
        manager = TaskManager()
        task = manager.add_task("Test task")
        with pytest.raises(ValueError, match="Task title cannot be empty"):
            manager.update_task(task.id, "title", "")

    def test_update_title_to_whitespace_raises_error(self):
        """Test that updating title to whitespace raises ValueError."""
        manager = TaskManager()
        task = manager.add_task("Test task")
        with pytest.raises(ValueError, match="Task title cannot be empty"):
            manager.update_task(task.id, "title", "   ")

    def test_update_description_to_empty_allowed(self):
        """Test that updating description to empty is allowed."""
        manager = TaskManager()
        task = manager.add_task("Test task", "Original description")
        updated = manager.update_task(task.id, "description", "")
        assert updated.description == ""


class TestTaskManagerToggle:
    """Tests for task status toggling."""

    def test_toggle_incomplete_to_complete(self):
        """Test toggling task from incomplete to complete."""
        manager = TaskManager()
        task = manager.add_task("Test task")
        assert task.status == "incomplete"
        toggled = manager.toggle_task_status(task.id)
        assert toggled.status == "complete"

    def test_toggle_complete_to_incomplete(self):
        """Test toggling task from complete to incomplete."""
        manager = TaskManager()
        task = manager.add_task("Test task")
        manager.toggle_task_status(task.id)
        toggled = manager.toggle_task_status(task.id)
        assert toggled.status == "incomplete"

    def test_toggle_nonexistent_task_raises_error(self):
        """Test that toggling non-existent task raises ValueError."""
        manager = TaskManager()
        with pytest.raises(ValueError, match="Task ID 999 not found"):
            manager.toggle_task_status(999)

    def test_toggle_returns_same_task_object(self):
        """Test that toggle returns the same task object."""
        manager = TaskManager()
        task = manager.add_task("Test task")
        toggled = manager.toggle_task_status(task.id)
        assert toggled is task


class TestTaskManagerDelete:
    """Tests for task deletion."""

    def test_delete_existing_task(self):
        """Test deleting an existing task."""
        manager = TaskManager()
        task = manager.add_task("Test task")
        manager.delete_task(task.id)
        assert manager.get_task(task.id) is None

    def test_delete_nonexistent_task_raises_error(self):
        """Test that deleting non-existent task raises ValueError."""
        manager = TaskManager()
        with pytest.raises(ValueError, match="Task ID 999 not found"):
            manager.delete_task(999)

    def test_delete_does_not_reset_id_counter(self):
        """Test that ID counter continues incrementing after deletion."""
        manager = TaskManager()
        task1 = manager.add_task("First")
        task2 = manager.add_task("Second")
        task3 = manager.add_task("Third")
        assert task3.id == 3
        manager.delete_task(task2.id)
        task4 = manager.add_task("Fourth")
        assert task4.id == 4  # NOT 2

    def test_delete_does_not_reuse_id(self):
        """Test that deleted task ID is never reused."""
        manager = TaskManager()
        task1 = manager.add_task("First")
        task2 = manager.add_task("Second")
        task3 = manager.add_task("Third")
        manager.delete_task(task1.id)
        manager.delete_task(task2.id)
        task4 = manager.add_task("Fourth")
        assert task4.id == 4  # Not 1 or 2

    def test_delete_task_reduces_list_size(self):
        """Test that deleting task reduces total task count."""
        manager = TaskManager()
        manager.add_task("First")
        manager.add_task("Second")
        manager.add_task("Third")
        assert len(manager.get_all_tasks()) == 3
        manager.delete_task(2)
        assert len(manager.get_all_tasks()) == 2


class TestTaskManagerIDGeneration:
    """Tests for ID generation strategy."""

    def test_first_task_gets_id_1(self):
        """Test that first task gets ID 1."""
        manager = TaskManager()
        task = manager.add_task("First task")
        assert task.id == 1

    def test_next_id_increments(self):
        """Test that next_id increments after each addition."""
        manager = TaskManager()
        assert manager.get_next_id() == 1
        manager.add_task("First")
        assert manager.get_next_id() == 2
        manager.add_task("Second")
        assert manager.get_next_id() == 3

    def test_sequential_ids_no_gaps(self):
        """Test that IDs are always sequential without gaps."""
        manager = TaskManager()
        ids = []
        for i in range(10):
            task = manager.add_task(f"Task {i+1}")
            ids.append(task.id)
        assert ids == list(range(1, 11))

    def test_ids_never_reused_after_multiple_deletes(self):
        """Test that IDs are never reused even after multiple deletions."""
        manager = TaskManager()
        # Create 5 tasks
        for i in range(5):
            manager.add_task(f"Task {i+1}")
        # Delete all except task 3
        for task_id in [1, 2, 4, 5]:
            manager.delete_task(task_id)
        # Add new task
        task6 = manager.add_task("Task 6")
        assert task6.id == 6  # NOT 1, 2, 4, or 5
