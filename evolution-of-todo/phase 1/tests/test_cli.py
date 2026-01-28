"""
Unit tests for the CLI functions in the Todo application.

These tests verify that the CLI functions work correctly:
- Displaying tasks in tabular format
- Getting user input
- CLI operation handlers
"""

import unittest
from unittest.mock import patch, MagicMock
from io import StringIO
import sys
from src.cli import (
    display_tasks,
    get_task_input,
    get_task_id,
    add_task_cli,
    update_task_cli,
    delete_task_cli,
    toggle_completion_cli,
    show_help,
    display_menu,
    get_user_choice,
    handle_user_choice
)
from src.todo import TaskManager
from src.models import Task


class TestCLI(unittest.TestCase):
    """Test cases for the CLI functions."""

    def test_display_tasks_empty(self):
        """Test displaying an empty task list."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            display_tasks([])
            output = mock_stdout.getvalue()
            self.assertIn("No tasks found.", output)

    def test_display_tasks_single(self):
        """Test displaying a single task."""
        task = Task(id=1, title="Test Task", description="Test Description", completed=False)
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            display_tasks([task])
            output = mock_stdout.getvalue()
            self.assertIn("Current Tasks:", output)
            self.assertIn("1", output)
            self.assertIn("Test Task", output)
            self.assertIn("Test Description", output)
            self.assertIn("[ ]", output)

    def test_display_tasks_completed(self):
        """Test displaying a completed task."""
        task = Task(id=1, title="Test Task", description="Test Description", completed=True)
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            display_tasks([task])
            output = mock_stdout.getvalue()
            self.assertIn("[x]", output)

    @patch('builtins.input')
    def test_get_task_input(self, mock_input):
        """Test getting task input from user."""
        mock_input.side_effect = ["Test Title", "Test Description"]
        title, description = get_task_input()

        self.assertEqual(title, "Test Title")
        self.assertEqual(description, "Test Description")

    @patch('builtins.input')
    def test_get_task_id_valid(self, mock_input):
        """Test getting a valid task ID from user."""
        mock_input.return_value = "5"
        task_id = get_task_id()

        self.assertEqual(task_id, 5)

    @patch('builtins.input')
    def test_get_task_id_invalid_then_valid(self, mock_input):
        """Test getting a task ID when user enters invalid input first."""
        mock_input.side_effect = ["abc", "5"]

        with patch('sys.stdout', new_callable=StringIO):
            task_id = get_task_id()

        self.assertEqual(task_id, 5)

    @patch('builtins.input')
    def test_get_task_id_negative_then_valid(self, mock_input):
        """Test getting a task ID when user enters negative number first."""
        mock_input.side_effect = ["-1", "5"]

        with patch('sys.stdout', new_callable=StringIO):
            task_id = get_task_id()

        self.assertEqual(task_id, 5)

    @patch('builtins.input')
    def test_add_task_cli_success(self, mock_input):
        """Test adding a task through CLI."""
        mock_input.side_effect = ["New Task", "New Description"]
        task_manager = TaskManager()

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            add_task_cli(task_manager)
            output = mock_stdout.getvalue()

        self.assertIn("Task added successfully", output)
        tasks = task_manager.get_all_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].title, "New Task")
        self.assertEqual(tasks[0].description, "New Description")

    @patch('builtins.input')
    def test_add_task_cli_empty_title(self, mock_input):
        """Test adding a task with empty title through CLI."""
        mock_input.side_effect = ["", "Any Description"]
        task_manager = TaskManager()

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            add_task_cli(task_manager)
            output = mock_stdout.getvalue()

        self.assertIn("Error:", output)

    @patch('builtins.input')
    def test_get_user_choice_valid(self, mock_input):
        """Test getting a valid user choice."""
        mock_input.return_value = "1"
        choice = get_user_choice()

        self.assertEqual(choice, 1)

    @patch('builtins.input')
    def test_get_user_choice_invalid_then_valid(self, mock_input):
        """Test getting user choice when invalid input is provided first."""
        mock_input.side_effect = ["10", "1"]

        with patch('sys.stdout', new_callable=StringIO):
            choice = get_user_choice()

        self.assertEqual(choice, 1)

    def test_handle_user_choice_exit(self):
        """Test handling the exit choice."""
        task_manager = TaskManager()
        result = handle_user_choice(0, task_manager)
        self.assertFalse(result)  # Should return False to exit

    def test_handle_user_choice_view_tasks(self):
        """Test handling the view tasks choice."""
        task_manager = TaskManager()
        task_manager.add_task("Test Task", "Test Description")

        with patch('sys.stdout', new_callable=StringIO):
            result = handle_user_choice(2, task_manager)
            self.assertTrue(result)  # Should return True to continue

    @patch('builtins.input')
    def test_handle_user_choice_add_task(self, mock_input):
        """Test handling the add task choice."""
        mock_input.side_effect = ["Test Title", "Test Description"]
        task_manager = TaskManager()

        with patch('sys.stdout', new_callable=StringIO):
            result = handle_user_choice(1, task_manager)
            self.assertTrue(result)  # Should return True to continue

    def test_show_help(self):
        """Test displaying help information."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            show_help()
            output = mock_stdout.getvalue()

        self.assertIn("Todo Application Help:", output)
        self.assertIn("Add Task", output)
        self.assertIn("View Tasks", output)
        self.assertIn("Tips:", output)

    def test_display_menu(self):
        """Test displaying the main menu."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            display_menu()
            output = mock_stdout.getvalue()

        self.assertIn("Main Menu", output)
        self.assertIn("1. Add Task", output)
        self.assertIn("2. View Tasks", output)
        self.assertIn("0. Exit", output)


if __name__ == "__main__":
    unittest.main()