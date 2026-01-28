"""
Task management service for the Todo application.

This module provides the core functionality for managing tasks:
- Adding new tasks
- Retrieving tasks by ID or all tasks
- Updating task details
- Deleting tasks
- Toggling task completion status
"""

from typing import List, Optional
from models import Task
from exceptions import TaskNotFoundError, InvalidTaskDataError
import itertools


class TaskManager:
    """
    Manages a collection of tasks with CRUD operations and auto-incrementing IDs.
    """

    def __init__(self):
        """Initialize the TaskManager with an empty task list and ID counter."""
        self._tasks: List[Task] = []
        self._id_counter = itertools.count(1)

    def add_task(self, title: str, description: str = "") -> int:
        """
        Creates a new task, assigns an auto-incrementing ID, and returns the assigned ID.

        Args:
            title (str): The title of the task (required)
            description (str): The description of the task (optional)

        Returns:
            int: The assigned ID of the new task

        Raises:
            InvalidTaskDataError: If the title is empty or invalid
        """
        # Validate task data
        if not title or not title.strip():
            raise InvalidTaskDataError("Task title cannot be empty")

        # Create task with next available ID
        task_id = next(self._id_counter)
        task = Task(id=task_id, title=title.strip(), description=description.strip())
        self._tasks.append(task)

        return task_id

    def get_task(self, task_id: int) -> Task:
        """
        Retrieves a task by its ID.

        Args:
            task_id (int): The ID of the task to retrieve

        Returns:
            Task: The task with the specified ID

        Raises:
            TaskNotFoundError: If no task with the given ID exists
        """
        for task in self._tasks:
            if task.id == task_id:
                return task

        raise TaskNotFoundError(task_id)

    def get_all_tasks(self) -> List[Task]:
        """
        Returns all tasks in the system.

        Returns:
            List[Task]: A list of all tasks
        """
        return self._tasks.copy()

    def update_task(self, task_id: int, title: str = None, description: str = None) -> bool:
        """
        Updates task details by ID.

        Args:
            task_id (int): The ID of the task to update
            title (str, optional): New title for the task
            description (str, optional): New description for the task

        Returns:
            bool: True if the task was updated successfully, False otherwise

        Raises:
            TaskNotFoundError: If no task with the given ID exists
            InvalidTaskDataError: If the new title is empty
        """
        task = self.get_task(task_id)

        # Validate new data if provided
        if title is not None and title.strip() == "":
            raise InvalidTaskDataError("Task title cannot be empty")

        # Update task properties if provided
        if title is not None:
            task.title = title.strip()
        if description is not None:
            task.description = description.strip()

        return True

    def delete_task(self, task_id: int) -> bool:
        """
        Removes a task by its ID.

        Args:
            task_id (int): The ID of the task to delete

        Returns:
            bool: True if the task was deleted successfully, False otherwise

        Raises:
            TaskNotFoundError: If no task with the given ID exists
        """
        for i, task in enumerate(self._tasks):
            if task.id == task_id:
                del self._tasks[i]
                return True

        raise TaskNotFoundError(task_id)

    def toggle_completion(self, task_id: int) -> bool:
        """
        Toggles the completion status of a task.

        Args:
            task_id (int): The ID of the task to toggle

        Returns:
            bool: True if the task status was toggled successfully, False otherwise

        Raises:
            TaskNotFoundError: If no task with the given ID exists
        """
        task = self.get_task(task_id)
        task.completed = not task.completed
        return True

    def validate_task_data(self, title: str, description: str = None) -> bool:
        """
        Validates task data.

        Args:
            title (str): The title to validate
            description (str, optional): The description to validate

        Returns:
            bool: True if the data is valid, False otherwise
        """
        if not title or not title.strip():
            return False
        return True