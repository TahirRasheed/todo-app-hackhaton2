"""
Phase I Todo Application - Main Entry Point

In-memory console-based todo application with menu-driven CLI interface.
Per spec.md and plan.md specifications.

Usage:
    python src/main.py
"""

from src.services.task_manager import TaskManager
from src.ui.cli_interface import CLIInterface


def main() -> None:
    """
    Main application loop.

    Initializes task manager and CLI, displays menu,
    processes user commands until exit.
    """
    # Initialize application components
    task_manager = TaskManager()
    cli = CLIInterface(task_manager)

    # Main loop
    while True:
        try:
            # Display menu
            cli.display_main_menu()

            # Get user choice
            choice = cli.get_user_input("Please choose an option (1-6) or type the option name: ")

            # Parse menu choice
            try:
                command = cli.parse_menu_choice(choice)
            except ValueError as e:
                print(f"Error: {e}")
                continue

            # Dispatch to appropriate command handler
            if command == "add":
                cli.add_task_flow()
            elif command == "view":
                cli.view_tasks_flow()
            elif command == "toggle":
                cli.toggle_task_status_flow()
            elif command == "update":
                cli.update_task_flow()
            elif command == "delete":
                cli.delete_task_flow()
            elif command == "exit":
                print("Goodbye!")
                break

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            continue


if __name__ == "__main__":
    main()
