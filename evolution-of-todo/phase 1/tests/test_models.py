"""
Unit tests for the Task model in the Todo application.

These tests verify that the Task dataclass functions correctly:
- Proper initialization of all fields
- String representation
- Marking tasks as complete/incomplete
"""

import unittest
from datetime import datetime
from src.models import Task


class TestTask(unittest.TestCase):
    """Test cases for the Task data model."""

    def test_task_initialization(self):
        """Test that a task is properly initialized with all required fields."""
        task = Task(id=1, title="Test Task", description="Test Description")

        self.assertEqual(task.id, 1)
        self.assertEqual(task.title, "Test Task")
        self.assertEqual(task.description, "Test Description")
        self.assertFalse(task.completed)
        self.assertIsInstance(task.created_at, datetime)

    def test_task_initialization_optional_fields(self):
        """Test that a task can be initialized with optional fields omitted."""
        task = Task(id=1, title="Test Task")

        self.assertEqual(task.id, 1)
        self.assertEqual(task.title, "Test Task")
        self.assertEqual(task.description, "")
        self.assertFalse(task.completed)
        self.assertIsInstance(task.created_at, datetime)

    def test_task_mark_complete(self):
        """Test that a task can be marked as complete."""
        task = Task(id=1, title="Test Task")

        self.assertFalse(task.completed)
        task.mark_complete()
        self.assertTrue(task.completed)

    def test_task_mark_incomplete(self):
        """Test that a completed task can be marked as incomplete."""
        task = Task(id=1, title="Test Task", completed=True)

        self.assertTrue(task.completed)
        task.mark_incomplete()
        self.assertFalse(task.completed)

    def test_task_string_representation(self):
        """Test the string representation of a task."""
        task = Task(id=1, title="Test Task", description="Test Description")

        expected_str = "1. [ ] Test Task - Test Description"
        self.assertEqual(str(task), expected_str)

    def test_completed_task_string_representation(self):
        """Test the string representation of a completed task."""
        task = Task(id=1, title="Test Task", description="Test Description", completed=True)

        expected_str = "1. [x] Test Task - Test Description"
        self.assertEqual(str(task), expected_str)


if __name__ == "__main__":
    unittest.main()