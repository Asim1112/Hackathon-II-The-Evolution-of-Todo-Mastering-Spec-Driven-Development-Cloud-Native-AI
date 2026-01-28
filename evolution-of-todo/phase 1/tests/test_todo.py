"""
Unit tests for the TaskManager service in the Todo application.

These tests verify that the TaskManager functions correctly:
- Adding tasks with auto-incrementing IDs
- Retrieving tasks by ID
- Retrieving all tasks
- Updating task details
- Deleting tasks
- Toggling completion status
- Handling edge cases and errors
"""

import unittest
from src.todo import TaskManager
from src.exceptions import TaskNotFoundError, InvalidTaskDataError


class TestTaskManager(unittest.TestCase):
    """Test cases for the TaskManager service."""

    def setUp(self):
        """Set up a fresh TaskManager for each test."""
        self.task_manager = TaskManager()

    def test_add_task_success(self):
        """Test that a task can be added successfully with auto-incremented ID."""
        task_id = self.task_manager.add_task("Test Title", "Test Description")

        self.assertEqual(task_id, 1)
        task = self.task_manager.get_task(task_id)
        self.assertEqual(task.title, "Test Title")
        self.assertEqual(task.description, "Test Description")
        self.assertFalse(task.completed)

    def test_add_task_without_description(self):
        """Test that a task can be added without a description."""
        task_id = self.task_manager.add_task("Test Title")

        self.assertEqual(task_id, 1)
        task = self.task_manager.get_task(task_id)
        self.assertEqual(task.title, "Test Title")
        self.assertEqual(task.description, "")

    def test_add_task_empty_title_error(self):
        """Test that adding a task with an empty title raises an error."""
        with self.assertRaises(InvalidTaskDataError):
            self.task_manager.add_task("")

        with self.assertRaises(InvalidTaskDataError):
            self.task_manager.add_task("   ")  # Only whitespace

    def test_get_task_success(self):
        """Test that a task can be retrieved by its ID."""
        task_id = self.task_manager.add_task("Test Title", "Test Description")
        task = self.task_manager.get_task(task_id)

        self.assertEqual(task.id, task_id)
        self.assertEqual(task.title, "Test Title")
        self.assertEqual(task.description, "Test Description")

    def test_get_task_not_found_error(self):
        """Test that retrieving a non-existent task raises an error."""
        with self.assertRaises(TaskNotFoundError):
            self.task_manager.get_task(999)

    def test_get_all_tasks_empty(self):
        """Test that getting all tasks returns an empty list when no tasks exist."""
        tasks = self.task_manager.get_all_tasks()

        self.assertEqual(len(tasks), 0)
        self.assertEqual(tasks, [])

    def test_get_all_tasks_multiple(self):
        """Test that getting all tasks returns all tasks."""
        task_id_1 = self.task_manager.add_task("Title 1", "Description 1")
        task_id_2 = self.task_manager.add_task("Title 2", "Description 2")
        task_id_3 = self.task_manager.add_task("Title 3", "Description 3")

        tasks = self.task_manager.get_all_tasks()

        self.assertEqual(len(tasks), 3)
        self.assertEqual(tasks[0].id, task_id_1)
        self.assertEqual(tasks[1].id, task_id_2)
        self.assertEqual(tasks[2].id, task_id_3)

    def test_update_task_success(self):
        """Test that a task can be updated successfully."""
        task_id = self.task_manager.add_task("Original Title", "Original Description")

        result = self.task_manager.update_task(task_id, "New Title", "New Description")

        self.assertTrue(result)
        updated_task = self.task_manager.get_task(task_id)
        self.assertEqual(updated_task.title, "New Title")
        self.assertEqual(updated_task.description, "New Description")

    def test_update_task_partial(self):
        """Test that a task can be updated with only title or description."""
        task_id = self.task_manager.add_task("Original Title", "Original Description")

        # Update only title
        result = self.task_manager.update_task(task_id, title="New Title")
        self.assertTrue(result)
        updated_task = self.task_manager.get_task(task_id)
        self.assertEqual(updated_task.title, "New Title")
        self.assertEqual(updated_task.description, "Original Description")

        # Update only description
        result = self.task_manager.update_task(task_id, description="New Description")
        self.assertTrue(result)
        updated_task = self.task_manager.get_task(task_id)
        self.assertEqual(updated_task.title, "New Title")
        self.assertEqual(updated_task.description, "New Description")

    def test_update_task_not_found_error(self):
        """Test that updating a non-existent task raises an error."""
        with self.assertRaises(TaskNotFoundError):
            self.task_manager.update_task(999, "New Title")

    def test_update_task_empty_title_error(self):
        """Test that updating a task with an empty title raises an error."""
        task_id = self.task_manager.add_task("Original Title")

        with self.assertRaises(InvalidTaskDataError):
            self.task_manager.update_task(task_id, title="")

        with self.assertRaises(InvalidTaskDataError):
            self.task_manager.update_task(task_id, title="   ")

    def test_delete_task_success(self):
        """Test that a task can be deleted successfully."""
        task_id = self.task_manager.add_task("Test Title", "Test Description")

        result = self.task_manager.delete_task(task_id)

        self.assertTrue(result)
        self.assertEqual(len(self.task_manager.get_all_tasks()), 0)

        # Verify the task no longer exists
        with self.assertRaises(TaskNotFoundError):
            self.task_manager.get_task(task_id)

    def test_delete_task_not_found_error(self):
        """Test that deleting a non-existent task raises an error."""
        with self.assertRaises(TaskNotFoundError):
            self.task_manager.delete_task(999)

    def test_toggle_completion_success(self):
        """Test that a task's completion status can be toggled."""
        task_id = self.task_manager.add_task("Test Title", "Test Description")

        # Initially incomplete
        task = self.task_manager.get_task(task_id)
        self.assertFalse(task.completed)

        # Toggle to complete
        result = self.task_manager.toggle_completion(task_id)
        self.assertTrue(result)
        task = self.task_manager.get_task(task_id)
        self.assertTrue(task.completed)

        # Toggle back to incomplete
        result = self.task_manager.toggle_completion(task_id)
        self.assertTrue(result)
        task = self.task_manager.get_task(task_id)
        self.assertFalse(task.completed)

    def test_toggle_completion_not_found_error(self):
        """Test that toggling completion of a non-existent task raises an error."""
        with self.assertRaises(TaskNotFoundError):
            self.task_manager.toggle_completion(999)

    def test_auto_increment_ids(self):
        """Test that task IDs are auto-incremented correctly."""
        id_1 = self.task_manager.add_task("Title 1")
        id_2 = self.task_manager.add_task("Title 2")
        id_3 = self.task_manager.add_task("Title 3")

        self.assertEqual(id_1, 1)
        self.assertEqual(id_2, 2)
        self.assertEqual(id_3, 3)


if __name__ == "__main__":
    unittest.main()