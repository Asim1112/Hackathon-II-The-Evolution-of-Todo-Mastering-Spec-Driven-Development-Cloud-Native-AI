"""
Command Line Interface functions for the Todo application.

Provides user interaction functions for all operations:
- Adding tasks
- Viewing tasks
- Updating tasks
- Deleting tasks
- Toggling completion status
- Displaying help
"""

from typing import Optional
from tabulate import tabulate
from todo import TaskManager
from models import Task
from exceptions import TodoException, TaskNotFoundError, InvalidTaskDataError


def display_tasks(tasks: list[Task]) -> None:
    """
    Displays all tasks in a clear, tabular format with ID, title, description, and completion status.

    Args:
        tasks (list[Task]): List of tasks to display
    """
    if not tasks:
        print("\nNo tasks found.")
        return

    # Prepare data for tabulation
    headers = ["ID", "Title", "Description", "Status"]
    table_data = []

    for task in tasks:
        status = "[x]" if task.completed else "[ ]"
        table_data.append([task.id, task.title, task.description, status])

    # Display the table
    print("\nCurrent Tasks:")
    print(tabulate(table_data, headers=headers, tablefmt="grid"))


def get_task_input() -> tuple[str, str]:
    """
    Gets task input from the user.

    Returns:
        tuple[str, str]: A tuple containing the title and description
    """
    title = input("Enter task title: ").strip()
    description = input("Enter task description (optional): ").strip()
    return title, description


def get_task_id() -> int:
    """
    Gets a task ID from the user.

    Returns:
        int: The task ID entered by the user
    """
    while True:
        try:
            task_id_str = input("Enter task ID: ").strip()
            task_id = int(task_id_str)
            if task_id <= 0:
                print("Task ID must be a positive integer.")
                continue
            return task_id
        except ValueError:
            print("Invalid input. Please enter a valid integer for task ID.")


def add_task_cli(task_manager: TaskManager) -> None:
    """
    Handles the CLI flow for adding a new task.

    Args:
        task_manager (TaskManager): The task manager instance to use
    """
    try:
        title, description = get_task_input()

        # Validate input
        if not title:
            print("Error: Task title cannot be empty.")
            return

        task_id = task_manager.add_task(title, description)
        print(f"Task added successfully with ID: {task_id}")

    except InvalidTaskDataError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def update_task_cli(task_manager: TaskManager) -> None:
    """
    Handles the CLI flow for updating an existing task.

    Args:
        task_manager (TaskManager): The task manager instance to use
    """
    try:
        task_id = get_task_id()

        # Check if task exists before asking for new data
        try:
            current_task = task_manager.get_task(task_id)
            print(f"Current task: {current_task.title} - {current_task.description}")
        except TaskNotFoundError:
            print(f"Error: Task with ID {task_id} not found.")
            return

        # Get new data
        print("Enter new values (press Enter to keep current value):")
        new_title_input = input(f"New title (current: '{current_task.title}'): ").strip()
        new_description_input = input(f"New description (current: '{current_task.description}'): ").strip()

        # Prepare updates (only update if user provided new values)
        new_title = new_title_input if new_title_input != "" else None
        new_description = new_description_input if new_description_input != "" else None

        # If both are None, nothing to update
        if new_title is None and new_description is None:
            print("No changes made.")
            return

        # Use current values if new values weren't provided
        if new_title is None:
            new_title = current_task.title
        if new_description is None:
            new_description = current_task.description

        success = task_manager.update_task(task_id, new_title, new_description)
        if success:
            print(f"Task with ID {task_id} updated successfully.")
        else:
            print(f"Failed to update task with ID {task_id}.")

    except InvalidTaskDataError as e:
        print(f"Error: {e}")
    except TaskNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def delete_task_cli(task_manager: TaskManager) -> None:
    """
    Handles the CLI flow for deleting a task.

    Args:
        task_manager (TaskManager): The task manager instance to use
    """
    try:
        task_id = get_task_id()

        success = task_manager.delete_task(task_id)
        if success:
            print(f"Task with ID {task_id} deleted successfully.")
        else:
            print(f"Failed to delete task with ID {task_id}.")

    except TaskNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def toggle_completion_cli(task_manager: TaskManager) -> None:
    """
    Handles the CLI flow for toggling a task's completion status.

    Args:
        task_manager (TaskManager): The task manager instance to use
    """
    try:
        task_id = get_task_id()

        success = task_manager.toggle_completion(task_id)
        if success:
            task = task_manager.get_task(task_id)
            status = "completed" if task.completed else "incomplete"
            print(f"Task with ID {task_id} marked as {status}.")
        else:
            print(f"Failed to toggle completion status for task with ID {task_id}.")

    except TaskNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def show_help() -> None:
    """
    Displays help information for the application.
    """
    print("\nTodo Application Help:")
    print("1. Add Task: Add a new task with title and description")
    print("2. View Tasks: Display all tasks in a tabular format")
    print("3. Update Task: Modify an existing task's title or description")
    print("4. Delete Task: Remove a task by its ID")
    print("5. Mark Complete/Incomplete: Toggle a task's completion status")
    print("6. Help: Show this help message")
    print("0. Exit: Close the application")
    print("\nTips:")
    print("- Task IDs are auto-incrementing integers assigned when created")
    print("- Use the View Tasks option to see all available task IDs")
    print("- Empty titles are not allowed for tasks")


def display_menu() -> None:
    """
    Displays the main menu options.
    """
    print("\n" + "="*40)
    print("Todo Application - Main Menu")
    print("="*40)
    print("1. Add Task")
    print("2. View Tasks")
    print("3. Update Task")
    print("4. Delete Task")
    print("5. Mark Complete/Incomplete")
    print("6. Help")
    print("0. Exit")
    print("="*40)


def get_user_choice() -> int:
    """
    Gets the user's menu choice.

    Returns:
        int: The menu option selected by the user
    """
    while True:
        try:
            choice = int(input("Choose an option (0-6): "))
            if 0 <= choice <= 6:
                return choice
            else:
                print("Please enter a number between 0 and 6.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def handle_user_choice(choice: int, task_manager: TaskManager) -> bool:
    """
    Handles the user's menu choice.

    Args:
        choice (int): The menu option selected by the user
        task_manager (TaskManager): The task manager instance to use

    Returns:
        bool: True if the application should continue, False to exit
    """
    if choice == 1:
        add_task_cli(task_manager)
    elif choice == 2:
        tasks = task_manager.get_all_tasks()
        display_tasks(tasks)
    elif choice == 3:
        update_task_cli(task_manager)
    elif choice == 4:
        delete_task_cli(task_manager)
    elif choice == 5:
        toggle_completion_cli(task_manager)
    elif choice == 6:
        show_help()
    elif choice == 0:
        print("Thank you for using the Todo Application. Goodbye!")
        return False

    return True