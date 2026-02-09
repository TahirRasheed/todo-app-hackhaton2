"""
Integration tests for CLI workflows.

Tests complete user journeys covering all 5 user stories and error cases.
Per spec.md acceptance scenarios and contracts/cli-interface.md.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.services.task_manager import TaskManager
from src.ui.cli_interface import CLIInterface


@pytest.fixture
def manager():
    """Create a TaskManager instance for testing."""
    return TaskManager()


@pytest.fixture
def cli(manager):
    """Create a CLIInterface instance for testing."""
    return CLIInterface(manager)


class TestAddTaskWorkflow:
    """Integration tests for adding tasks (US1)."""

    def test_add_single_task(self, cli):
        """Test adding a single task via CLI."""
        with patch("builtins.input", side_effect=["Buy groceries", ""]):
            with patch("builtins.print"):
                cli.add_task_flow()

        tasks = cli.task_manager.get_all_tasks()
        assert len(tasks) == 1
        assert tasks[0].title == "Buy groceries"
        assert tasks[0].status == "incomplete"

    def test_add_task_with_description(self, cli):
        """Test adding task with description."""
        with patch("builtins.input", side_effect=["Buy groceries", "Milk, eggs, bread"]):
            with patch("builtins.print"):
                cli.add_task_flow()

        tasks = cli.task_manager.get_all_tasks()
        assert tasks[0].description == "Milk, eggs, bread"

    def test_add_multiple_tasks_increments_id(self, cli):
        """Test that multiple tasks get sequential IDs."""
        with patch("builtins.input", side_effect=["Task 1", ""]):
            with patch("builtins.print"):
                cli.add_task_flow()

        with patch("builtins.input", side_effect=["Task 2", ""]):
            with patch("builtins.print"):
                cli.add_task_flow()

        tasks = cli.task_manager.get_all_tasks()
        assert len(tasks) == 2
        assert tasks[0].id == 1
        assert tasks[1].id == 2

    def test_add_task_rejects_empty_title(self, cli):
        """Test that empty title is rejected."""
        with patch("builtins.input", return_value=""):
            with patch("builtins.print"):
                cli.add_task_flow()

        # No task should be added
        assert len(cli.task_manager.get_all_tasks()) == 0


class TestViewTasksWorkflow:
    """Integration tests for viewing tasks (US2)."""

    def test_view_empty_task_list(self, cli):
        """Test viewing empty task list."""
        with patch("builtins.print") as mock_print:
            cli.view_tasks_flow()
            # Should print "No tasks" message
            calls = [str(call) for call in mock_print.call_args_list]
            assert any("No tasks" in str(call) for call in calls)

    def test_view_tasks_displays_all(self, cli):
        """Test that view displays all tasks."""
        # Add 3 tasks
        cli.task_manager.add_task("Task 1")
        cli.task_manager.add_task("Task 2")
        cli.task_manager.add_task("Task 3")

        with patch("builtins.print") as mock_print:
            cli.view_tasks_flow()

        # Check that all tasks are displayed
        calls_str = str(mock_print.call_args_list)
        assert "Task 1" in calls_str
        assert "Task 2" in calls_str
        assert "Task 3" in calls_str

    def test_view_tasks_shows_status(self, cli):
        """Test that view shows task status."""
        task = cli.task_manager.add_task("Test task")
        assert task.status == "incomplete"

        with patch("builtins.print") as mock_print:
            cli.view_tasks_flow()

        calls_str = str(mock_print.call_args_list)
        assert "incomplete" in calls_str


class TestToggleStatusWorkflow:
    """Integration tests for toggling task status (US3)."""

    def test_toggle_incomplete_to_complete(self, cli):
        """Test toggling task from incomplete to complete."""
        task = cli.task_manager.add_task("Test task")
        assert task.status == "incomplete"

        with patch("builtins.input", return_value="1"):
            with patch("builtins.print"):
                cli.toggle_task_status_flow()

        updated_task = cli.task_manager.get_task(1)
        assert updated_task.status == "complete"

    def test_toggle_complete_to_incomplete(self, cli):
        """Test toggling task from complete to incomplete."""
        task = cli.task_manager.add_task("Test task")
        cli.task_manager.toggle_task_status(task.id)
        assert task.status == "complete"

        with patch("builtins.input", return_value="1"):
            with patch("builtins.print"):
                cli.toggle_task_status_flow()

        assert task.status == "incomplete"

    def test_toggle_nonexistent_task_shows_error(self, cli):
        """Test that toggling non-existent task shows error."""
        with patch("builtins.input", return_value="999"):
            with patch("builtins.print") as mock_print:
                cli.toggle_task_status_flow()

        calls_str = str(mock_print.call_args_list)
        assert "Error" in calls_str
        assert "not found" in calls_str.lower()


class TestUpdateTaskWorkflow:
    """Integration tests for updating tasks (US4)."""

    def test_update_task_title(self, cli):
        """Test updating task title."""
        task = cli.task_manager.add_task("Original title")

        with patch("builtins.input", side_effect=["1", "title", "New title"]):
            with patch("builtins.print"):
                cli.update_task_flow()

        updated = cli.task_manager.get_task(1)
        assert updated.title == "New title"

    def test_update_task_description(self, cli):
        """Test updating task description."""
        task = cli.task_manager.add_task("Test task")

        with patch("builtins.input", side_effect=["1", "description", "New description"]):
            with patch("builtins.print"):
                cli.update_task_flow()

        updated = cli.task_manager.get_task(1)
        assert updated.description == "New description"

    def test_update_nonexistent_task_shows_error(self, cli):
        """Test that updating non-existent task shows error."""
        with patch("builtins.input", side_effect=["999", "title", "New title"]):
            with patch("builtins.print") as mock_print:
                cli.update_task_flow()

        calls_str = str(mock_print.call_args_list)
        assert "Error" in calls_str


class TestDeleteTaskWorkflow:
    """Integration tests for deleting tasks (US5)."""

    def test_delete_task_with_confirmation(self, cli):
        """Test deleting a task with confirmation."""
        task = cli.task_manager.add_task("Test task")
        assert len(cli.task_manager.get_all_tasks()) == 1

        with patch("builtins.input", side_effect=["1", "yes"]):
            with patch("builtins.print"):
                cli.delete_task_flow()

        assert len(cli.task_manager.get_all_tasks()) == 0

    def test_delete_task_cancel(self, cli):
        """Test cancelling delete operation."""
        task = cli.task_manager.add_task("Test task")

        with patch("builtins.input", side_effect=["1", "no"]):
            with patch("builtins.print") as mock_print:
                cli.delete_task_flow()

        # Task should still exist
        assert len(cli.task_manager.get_all_tasks()) == 1
        calls_str = str(mock_print.call_args_list)
        assert "cancelled" in calls_str.lower()

    def test_delete_nonexistent_task_shows_error(self, cli):
        """Test that deleting non-existent task shows error."""
        with patch("builtins.input", side_effect=["999", "yes"]):
            with patch("builtins.print") as mock_print:
                cli.delete_task_flow()

        calls_str = str(mock_print.call_args_list)
        assert "Error" in calls_str

    def test_delete_does_not_reuse_id(self, cli):
        """Test that deleted task ID is not reused."""
        cli.task_manager.add_task("Task 1")
        cli.task_manager.add_task("Task 2")
        cli.task_manager.add_task("Task 3")

        # Delete task 2
        with patch("builtins.input", side_effect=["2", "yes"]):
            with patch("builtins.print"):
                cli.delete_task_flow()

        # Add new task
        with patch("builtins.input", side_effect=["Task 4", ""]):
            with patch("builtins.print"):
                cli.add_task_flow()

        # New task should have ID 4, not 2
        new_task = cli.task_manager.get_task(4)
        assert new_task is not None
        assert new_task.title == "Task 4"


class TestCompleteUserWorkflow:
    """Integration tests for complete user journeys."""

    def test_complete_workflow_all_operations(self, cli):
        """Test complete workflow: Add → View → Toggle → Update → Delete."""
        # Add task
        with patch("builtins.input", side_effect=["Buy groceries", ""]):
            with patch("builtins.print"):
                cli.add_task_flow()

        assert len(cli.task_manager.get_all_tasks()) == 1
        task = cli.task_manager.get_task(1)
        assert task.status == "incomplete"

        # Toggle status
        with patch("builtins.input", return_value="1"):
            with patch("builtins.print"):
                cli.toggle_task_status_flow()

        task = cli.task_manager.get_task(1)
        assert task.status == "complete"

        # Update task
        with patch("builtins.input", side_effect=["1", "description", "Milk, eggs, bread"]):
            with patch("builtins.print"):
                cli.update_task_flow()

        task = cli.task_manager.get_task(1)
        assert task.description == "Milk, eggs, bread"

        # Delete task
        with patch("builtins.input", side_effect=["1", "yes"]):
            with patch("builtins.print"):
                cli.delete_task_flow()

        assert len(cli.task_manager.get_all_tasks()) == 0

    def test_multiple_tasks_workflow(self, cli):
        """Test workflow with multiple tasks."""
        # Add 3 tasks
        for i in range(1, 4):
            with patch("builtins.input", side_effect=[f"Task {i}", ""]):
                with patch("builtins.print"):
                    cli.add_task_flow()

        assert len(cli.task_manager.get_all_tasks()) == 3

        # Toggle task 2
        with patch("builtins.input", return_value="2"):
            with patch("builtins.print"):
                cli.toggle_task_status_flow()

        # View should show all with task 2 complete
        with patch("builtins.print") as mock_print:
            cli.view_tasks_flow()

        calls_str = str(mock_print.call_args_list)
        assert "Task 1" in calls_str
        assert "Task 2" in calls_str
        assert "Task 3" in calls_str

    def test_error_recovery_workflow(self, cli):
        """Test that CLI recovers from errors gracefully."""
        # Try to toggle non-existent task (should error but not crash)
        with patch("builtins.input", return_value="999"):
            with patch("builtins.print"):
                cli.toggle_task_status_flow()

        # Should still be able to add a task
        with patch("builtins.input", side_effect=["Test task", ""]):
            with patch("builtins.print"):
                cli.add_task_flow()

        tasks = cli.task_manager.get_all_tasks()
        assert len(tasks) == 1
        assert tasks[0].title == "Test task"
