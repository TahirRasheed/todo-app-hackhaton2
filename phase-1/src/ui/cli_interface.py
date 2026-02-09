"""
CLI Interface for Phase I Todo Application.

Implements all user-facing CLI operations including menu display,
input handling, and formatted output.
Per contracts/cli-interface.md and plan.md specifications.
"""

from typing import Optional, List
from src.models.task import Task
from src.services.task_manager import TaskManager


class CLIInterface:
    """
    Handles all command-line user interface operations.

    Manages menu display, user input, output formatting, and error messages.
    """

    def __init__(self, task_manager: TaskManager) -> None:
        """
        Initialize CLI interface with task manager.

        Args:
            task_manager: TaskManager instance for business logic
        """
        self.task_manager = task_manager

    def get_user_input(self, prompt: str) -> str:
        """
        Get user input from stdin.

        Args:
            prompt: Prompt text to display to user

        Returns:
            User input with whitespace stripped
        """
        return input(prompt).strip()

    def display_message(self, message: str, msg_type: str = "info") -> None:
        """
        Display a formatted message to user.

        Args:
            message: Message text
            msg_type: Type of message ("info", "success", "error")
        """
        if msg_type == "error":
            print(f"Error: {message}")
        elif msg_type == "success":
            print(f"{message}")
        else:
            print(f"{message}")

    def display_main_menu(self) -> None:
        """Display the main menu."""
        print("\n" + "=" * 40)
        print("    TODO APPLICATION - MAIN MENU")
        print("=" * 40)
        print("\nWhat would you like to do?\n")
        print("1. Add Task")
        print("2. View Tasks")
        print("3. Toggle Task Status")
        print("4. Update Task")
        print("5. Delete Task")
        print("6. Exit")
        print()

    def normalize_menu_choice(self, choice: str) -> str:
        """
        Normalize menu choice to lowercase.

        Args:
            choice: User menu choice

        Returns:
            Normalized choice
        """
        return choice.lower().strip()

    def parse_menu_choice(self, choice: str) -> Optional[str]:
        """
        Parse and validate menu choice.

        Args:
            choice: User menu choice (can be number or name)

        Returns:
            Normalized command ("add", "view", "toggle", "update", "delete", "exit") or None

        Raises:
            ValueError: If choice is invalid
        """
        normalized = self.normalize_menu_choice(choice)

        # Map numeric choices to command names
        menu_map = {
            "1": "add",
            "2": "view",
            "3": "toggle",
            "4": "update",
            "5": "delete",
            "6": "exit",
            "add": "add",
            "add task": "add",
            "view": "view",
            "view tasks": "view",
            "toggle": "toggle",
            "toggle task status": "toggle",
            "update": "update",
            "update task": "update",
            "delete": "delete",
            "delete task": "delete",
            "exit": "exit",
            "quit": "exit",
        }

        if normalized not in menu_map:
            raise ValueError(
                "Please enter a valid option (1-6, add, view, toggle, update, delete, exit)"
            )

        return menu_map[normalized]

    def validate_task_id(self, input_str: str) -> int:
        """
        Validate and parse task ID from user input.

        Args:
            input_str: User input string

        Returns:
            Parsed integer task ID

        Raises:
            ValueError: If input is not a valid positive integer
        """
        try:
            task_id = int(input_str.strip())
            if task_id <= 0:
                raise ValueError("must be a positive integer")
            return task_id
        except ValueError:
            raise ValueError("Invalid ID: must be a positive integer")

    def validate_title(self, title: str) -> str:
        """
        Validate task title.

        Args:
            title: Task title to validate

        Returns:
            Validated title

        Raises:
            ValueError: If title is invalid
        """
        stripped = title.strip()
        if not stripped:
            raise ValueError("Task title cannot be empty")
        return stripped

    def validate_field_choice(self, choice: str) -> str:
        """
        Validate field choice for update operation.

        Args:
            choice: Field choice ("title" or "description")

        Returns:
            Normalized field choice

        Raises:
            ValueError: If choice is invalid
        """
        normalized = choice.lower().strip()
        if normalized not in ("title", "description"):
            raise ValueError("Invalid field. Please choose 'title' or 'description'")
        return normalized

    def validate_confirmation(self, input_str: str) -> bool:
        """
        Validate yes/no confirmation from user.

        Args:
            input_str: User input

        Returns:
            True if "yes", False if "no"

        Raises:
            ValueError: If input is neither "yes" nor "no"
        """
        normalized = input_str.lower().strip()
        if normalized in ("yes", "y"):
            return True
        elif normalized in ("no", "n"):
            return False
        else:
            raise ValueError("Please enter 'yes' or 'no'")

    def add_task_flow(self) -> None:
        """Execute the add task workflow."""
        try:
            title = self.get_user_input("Enter task title: ")
            title = self.validate_title(title)

            description = self.get_user_input(
                "Enter task description (optional, press Enter to skip): "
            )

            task = self.task_manager.add_task(title, description.strip())
            self.display_message(
                f"Task created successfully (ID: {task.id})", msg_type="success"
            )
        except ValueError as e:
            self.display_message(str(e), msg_type="error")

    def display_all_tasks(self) -> None:
        """Display all tasks in table format."""
        tasks = self.task_manager.get_all_tasks()

        if not tasks:
            print("No tasks. Use 'Add Task' to create one.")
            return

        # Print header
        print("\nID | Title                        | Status")
        print("-" * 50)

        # Print tasks
        for task in tasks:
            # Format title (truncate if necessary)
            title = task.title
            if len(title) > 28:
                title = title[:25] + "..."
            print(f"{task.id:<2} | {title:<28} | {task.status}")
        print()

    def view_tasks_flow(self) -> None:
        """Execute the view tasks workflow."""
        self.display_all_tasks()

    def toggle_task_status_flow(self) -> None:
        """Execute the toggle task status workflow."""
        try:
            task_id_input = self.get_user_input("Enter task ID to toggle: ")
            task_id = self.validate_task_id(task_id_input)

            task = self.task_manager.toggle_task_status(task_id)
            status_text = "marked complete" if task.status == "complete" else "marked incomplete"
            self.display_message(f"Task {task_id} {status_text}", msg_type="success")
        except ValueError as e:
            self.display_message(str(e), msg_type="error")

    def update_task_flow(self) -> None:
        """Execute the update task workflow."""
        try:
            task_id_input = self.get_user_input("Enter task ID to update: ")
            task_id = self.validate_task_id(task_id_input)

            field = self.get_user_input("What would you like to update? (title or description): ")
            field = self.validate_field_choice(field)

            value = self.get_user_input(f"Enter new {field}: ")
            if field == "title":
                value = self.validate_title(value)

            self.task_manager.update_task(task_id, field, value)
            self.display_message(f"Task {task_id} updated successfully", msg_type="success")
        except ValueError as e:
            self.display_message(str(e), msg_type="error")

    def delete_task_flow(self) -> None:
        """Execute the delete task workflow."""
        try:
            task_id_input = self.get_user_input("Enter task ID to delete: ")
            task_id = self.validate_task_id(task_id_input)

            confirmation = self.get_user_input("Are you sure? (yes or no): ")
            if not self.validate_confirmation(confirmation):
                print("Delete cancelled.")
                return

            self.task_manager.delete_task(task_id)
            self.display_message(f"Task {task_id} deleted successfully", msg_type="success")
        except ValueError as e:
            self.display_message(str(e), msg_type="error")
