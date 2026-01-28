"""
Main entry point for the Todo Application.

This module implements the main CLI loop that allows users to interact with
the task management system through a menu interface.
"""

from todo import TaskManager
from cli import display_menu, get_user_choice, handle_user_choice


def main():
    """
    Main function that runs the Todo application.

    Initializes the TaskManager and runs the main menu loop until the user chooses to exit.
    """
    print("Welcome to the Todo Application!")

    # Initialize the task manager
    task_manager = TaskManager()

    # Main application loop
    running = True
    while running:
        display_menu()
        choice = get_user_choice()
        running = handle_user_choice(choice, task_manager)


if __name__ == "__main__":
    main()