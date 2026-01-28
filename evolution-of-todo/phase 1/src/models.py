from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Task:
    """
    Represents a user's todo item with unique ID, title, description, and completion status.

    Attributes:
        id (int): Unique auto-incrementing identifier for the task
        title (str): Title/description of the task (required)
        description (str): Detailed description of the task (optional)
        completed (bool): Completion status of the task (default: False)
        created_at (datetime): Timestamp when the task was created (optional)
    """
    id: int
    title: str
    description: Optional[str] = ""
    completed: bool = False
    created_at: datetime = None

    def __post_init__(self):
        """Initialize the created_at timestamp if not provided."""
        if self.created_at is None:
            self.created_at = datetime.now()

    def __str__(self) -> str:
        """Return a string representation of the task."""
        status = "[x]" if self.completed else "[ ]"
        return f"{self.id}. {status} {self.title} - {self.description}"

    def mark_complete(self) -> None:
        """Mark the task as complete."""
        self.completed = True

    def mark_incomplete(self) -> None:
        """Mark the task as incomplete."""
        self.completed = False