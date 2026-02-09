"""
Unit tests for CLI Interface.

Tests input parsing, validation, menu handling, and output formatting.
Per contracts/cli-interface.md specifications.
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


class TestCLIInputHandling:
    """Tests for user input handling."""

    def test_get_user_input_strips_whitespace(self, cli):
        """Test that get_user_input strips leading/trailing whitespace."""
        with patch("builtins.input", return_value="  test input  "):
            result = cli.get_user_input("Prompt: ")
            assert result == "test input"

    def test_normalize_menu_choice_lowercase(self, cli):
        """Test that menu choice is normalized to lowercase."""
        assert cli.normalize_menu_choice("ADD") == "add"
        assert cli.normalize_menu_choice("VIEW TASKS") == "view tasks"
        assert cli.normalize_menu_choice("EXIT") == "exit"

    def test_normalize_menu_choice_strips_whitespace(self, cli):
        """Test that menu choice whitespace is stripped."""
        assert cli.normalize_menu_choice("  add  ") == "add"


class TestMenuChoiceParsing:
    """Tests for menu choice parsing."""

    def test_parse_numeric_choices(self, cli):
        """Test parsing numeric menu choices."""
        assert cli.parse_menu_choice("1") == "add"
        assert cli.parse_menu_choice("2") == "view"
        assert cli.parse_menu_choice("3") == "toggle"
        assert cli.parse_menu_choice("4") == "update"
        assert cli.parse_menu_choice("5") == "delete"
        assert cli.parse_menu_choice("6") == "exit"

    def test_parse_named_choices(self, cli):
        """Test parsing named menu choices."""
        assert cli.parse_menu_choice("add") == "add"
        assert cli.parse_menu_choice("view") == "view"
        assert cli.parse_menu_choice("toggle") == "toggle"
        assert cli.parse_menu_choice("update") == "update"
        assert cli.parse_menu_choice("delete") == "delete"
        assert cli.parse_menu_choice("exit") == "exit"

    def test_parse_verbose_named_choices(self, cli):
        """Test parsing verbose menu choices."""
        assert cli.parse_menu_choice("add task") == "add"
        assert cli.parse_menu_choice("view tasks") == "view"
        assert cli.parse_menu_choice("toggle task status") == "toggle"
        assert cli.parse_menu_choice("update task") == "update"
        assert cli.parse_menu_choice("delete task") == "delete"

    def test_parse_case_insensitive_choices(self, cli):
        """Test that menu parsing is case-insensitive."""
        assert cli.parse_menu_choice("ADD") == "add"
        assert cli.parse_menu_choice("View Tasks") == "view"
        assert cli.parse_menu_choice("TOGGLE") == "toggle"

    def test_parse_invalid_choice_raises_error(self, cli):
        """Test that invalid menu choice raises ValueError."""
        with pytest.raises(ValueError):
            cli.parse_menu_choice("invalid")

    def test_parse_invalid_choice_error_message(self, cli):
        """Test error message for invalid choice."""
        with pytest.raises(ValueError, match="valid option"):
            cli.parse_menu_choice("xyz")


class TestTaskIDValidation:
    """Tests for task ID validation."""

    def test_validate_valid_task_id(self, cli):
        """Test validating a valid task ID."""
        assert cli.validate_task_id("1") == 1
        assert cli.validate_task_id("42") == 42
        assert cli.validate_task_id("999") == 999

    def test_validate_task_id_strips_whitespace(self, cli):
        """Test that task ID validation strips whitespace."""
        assert cli.validate_task_id("  5  ") == 5

    def test_validate_zero_task_id_raises_error(self, cli):
        """Test that zero task ID raises ValueError."""
        with pytest.raises(ValueError, match="positive integer"):
            cli.validate_task_id("0")

    def test_validate_negative_task_id_raises_error(self, cli):
        """Test that negative task ID raises ValueError."""
        with pytest.raises(ValueError, match="positive integer"):
            cli.validate_task_id("-5")

    def test_validate_non_numeric_task_id_raises_error(self, cli):
        """Test that non-numeric task ID raises ValueError."""
        with pytest.raises(ValueError, match="positive integer"):
            cli.validate_task_id("abc")

    def test_validate_float_task_id_raises_error(self, cli):
        """Test that float task ID raises ValueError."""
        with pytest.raises(ValueError, match="positive integer"):
            cli.validate_task_id("3.14")


class TestTitleValidation:
    """Tests for task title validation."""

    def test_validate_valid_title(self, cli):
        """Test validating a valid task title."""
        assert cli.validate_title("Buy groceries") == "Buy groceries"

    def test_validate_title_strips_whitespace(self, cli):
        """Test that title validation strips whitespace."""
        assert cli.validate_title("  Buy groceries  ") == "Buy groceries"

    def test_validate_empty_title_raises_error(self, cli):
        """Test that empty title raises ValueError."""
        with pytest.raises(ValueError, match="Task title cannot be empty"):
            cli.validate_title("")

    def test_validate_whitespace_only_title_raises_error(self, cli):
        """Test that whitespace-only title raises ValueError."""
        with pytest.raises(ValueError, match="Task title cannot be empty"):
            cli.validate_title("   ")


class TestFieldChoiceValidation:
    """Tests for field choice validation."""

    def test_validate_title_field(self, cli):
        """Test validating 'title' field choice."""
        assert cli.validate_field_choice("title") == "title"

    def test_validate_description_field(self, cli):
        """Test validating 'description' field choice."""
        assert cli.validate_field_choice("description") == "description"

    def test_validate_field_case_insensitive(self, cli):
        """Test that field choice is case-insensitive."""
        assert cli.validate_field_choice("TITLE") == "title"
        assert cli.validate_field_choice("Description") == "description"

    def test_validate_invalid_field_raises_error(self, cli):
        """Test that invalid field choice raises ValueError."""
        with pytest.raises(ValueError, match="Invalid field"):
            cli.validate_field_choice("priority")


class TestConfirmationValidation:
    """Tests for yes/no confirmation validation."""

    def test_validate_yes_confirmation(self, cli):
        """Test validating 'yes' confirmation."""
        assert cli.validate_confirmation("yes") is True
        assert cli.validate_confirmation("y") is True

    def test_validate_no_confirmation(self, cli):
        """Test validating 'no' confirmation."""
        assert cli.validate_confirmation("no") is False
        assert cli.validate_confirmation("n") is False

    def test_validate_confirmation_case_insensitive(self, cli):
        """Test that confirmation is case-insensitive."""
        assert cli.validate_confirmation("YES") is True
        assert cli.validate_confirmation("No") is False

    def test_validate_confirmation_strips_whitespace(self, cli):
        """Test that confirmation whitespace is stripped."""
        assert cli.validate_confirmation("  yes  ") is True
        assert cli.validate_confirmation("  no  ") is False

    def test_validate_invalid_confirmation_raises_error(self, cli):
        """Test that invalid confirmation raises ValueError."""
        with pytest.raises(ValueError):
            cli.validate_confirmation("maybe")


class TestMessageDisplay:
    """Tests for message display."""

    def test_display_error_message(self, cli):
        """Test displaying error message."""
        with patch("builtins.print") as mock_print:
            cli.display_message("Test error", msg_type="error")
            mock_print.assert_called_with("Error: Test error")

    def test_display_success_message(self, cli):
        """Test displaying success message."""
        with patch("builtins.print") as mock_print:
            cli.display_message("Test success", msg_type="success")
            mock_print.assert_called_with("Test success")

    def test_display_info_message(self, cli):
        """Test displaying info message."""
        with patch("builtins.print") as mock_print:
            cli.display_message("Test info", msg_type="info")
            mock_print.assert_called_with("Test info")
