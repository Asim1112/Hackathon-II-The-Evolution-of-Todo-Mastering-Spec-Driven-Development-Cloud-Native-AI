"""
Custom exception classes for the Todo application.

These exceptions provide clear feedback to users when operations fail
and maintain application stability during error conditions.
"""


class TodoException(Exception):
    """Base exception class for the Todo application."""
    pass


class TaskNotFoundError(TodoException):
    """Raised when a task with the specified ID is not found."""

    def __init__(self, task_id: int):
        self.task_id = task_id
        super().__init__(f"Task with ID {task_id} not found")


class InvalidTaskDataError(TodoException):
    """Raised when task data is invalid (e.g., empty title)."""

    def __init__(self, message: str = "Invalid task data provided"):
        super().__init__(message)


class TaskAlreadyExistsError(TodoException):
    """Raised when attempting to create a task that already exists."""

    def __init__(self, task_id: int):
        self.task_id = task_id
        super().__init__(f"Task with ID {task_id} already exists")