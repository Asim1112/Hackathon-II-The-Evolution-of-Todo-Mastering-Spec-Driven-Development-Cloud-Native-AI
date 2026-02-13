"""
Official MCP Server for Todo Application

Built with the Official MCP Python SDK (FastMCP).
Exposes 5 task operation tools: add_task, list_tasks, complete_task, update_task, delete_task.

All tool schemas are auto-generated from Python type hints and docstrings.
Tools are registered via @mcp.tool() decorators following MCP protocol.
"""

import logging
from typing import Optional
from datetime import datetime
from sqlmodel import select

from mcp.server.fastmcp import FastMCP

from src.models.task import Task
from src.database.session import get_session

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# MCP Server Instance (Official MCP SDK)
# ---------------------------------------------------------------------------

mcp = FastMCP("TodoMCP")


# ---------------------------------------------------------------------------
# Helper: Database session context manager
# ---------------------------------------------------------------------------

class _SessionContext:
    """Manages database session lifecycle for MCP tool handlers.

    Uses SQLModel's Session context manager which auto-commits on successful exit.
    Manual session.commit() calls are NOT needed - use session.flush() to persist
    changes within the transaction, then let the context manager commit on exit.
    """

    def __enter__(self):
        self._gen = get_session()
        self.session = next(self._gen)
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Exception occurred - rollback
            self.session.rollback()
        # Exit the Session context manager (auto-commits if no exception)
        try:
            next(self._gen)
        except StopIteration:
            pass
        return False


# ---------------------------------------------------------------------------
# MCP Tool: add_task
# ---------------------------------------------------------------------------

@mcp.tool()
async def add_task(user_id: str, title: str, description: str = "") -> dict:
    """Create a new task for the user.

    Args:
        user_id: The unique identifier for the user
        title: The title of the task (1-200 characters)
        description: Optional detailed description of the task (max 1000 characters)
    """
    # Log tool call (CR-106)
    logger.info(f"[TOOL] add_task called: user_id={user_id}, title={title[:50]}")

    # Validation
    if not user_id or not user_id.strip():
        raise ValueError("user_id cannot be empty")

    if not title or not title.strip():
        raise ValueError("title cannot be empty")

    title_clean = title.strip()
    if len(title_clean) > 200:
        raise ValueError("title cannot exceed 200 characters")

    description_clean = description.strip() if description else ""
    if len(description_clean) > 1000:
        raise ValueError("description cannot exceed 1000 characters")

    # Database operation
    with _SessionContext() as session:
        new_task = Task(
            title=title_clean,
            description=description_clean if description_clean else None,
            owner_id=user_id.strip(),
            is_completed=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        session.add(new_task)
        session.flush()  # Flush to get the ID without committing

        logger.info(f"add_task: Created task {new_task.id} for user {user_id}")

        return {
            "task_id": new_task.id,
            "status": "created",
            "title": new_task.title
        }


# ---------------------------------------------------------------------------
# MCP Tool: list_tasks
# ---------------------------------------------------------------------------

@mcp.tool()
async def list_tasks(user_id: str, status: str = "all") -> list:
    """Retrieve tasks for the user with optional status filter.

    Args:
        user_id: The unique identifier for the user
        status: Filter by status - 'all', 'pending', or 'completed'
    """
    # Log tool call (CR-106)
    logger.info(f"[TOOL] list_tasks called: user_id={user_id}, status={status}")

    # Validation
    if not user_id or not user_id.strip():
        raise ValueError("user_id cannot be empty")

    valid_statuses = ["all", "pending", "completed"]
    if status not in valid_statuses:
        raise ValueError(f"status must be one of: {', '.join(valid_statuses)}")

    # Database operation
    with _SessionContext() as session:
        query = select(Task).where(Task.owner_id == user_id.strip())

        if status == "pending":
            query = query.where(Task.is_completed == False)
        elif status == "completed":
            query = query.where(Task.is_completed == True)

        query = query.order_by(Task.created_at.desc())
        results = session.exec(query).all()

        tasks = [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description or "",
                "completed": task.is_completed,
                "created_at": task.created_at.isoformat()
            }
            for task in results
        ]

        logger.info(f"list_tasks: Retrieved {len(tasks)} tasks for user {user_id} (status: {status})")
        return tasks


# ---------------------------------------------------------------------------
# MCP Tool: complete_task
# ---------------------------------------------------------------------------

@mcp.tool()
async def complete_task(user_id: str, task_id: int) -> dict:
    """Mark a task as complete. This operation is idempotent.

    Args:
        user_id: The unique identifier for the user
        task_id: The ID of the task to mark as completed
    """
    # Log tool call (CR-106)
    logger.info(f"[TOOL] complete_task called: user_id={user_id}, task_id={task_id}")

    # Validation
    if not user_id or not user_id.strip():
        raise ValueError("user_id cannot be empty")

    if not isinstance(task_id, int) or task_id <= 0:
        raise ValueError("task_id must be a positive integer")

    # Database operation
    with _SessionContext() as session:
        query = select(Task).where(
            Task.id == task_id,
            Task.owner_id == user_id.strip()
        )
        task = session.exec(query).first()

        if not task:
            raise PermissionError(
                f"Task {task_id} not found or you don't have permission to complete it"
            )

        # Idempotent - already completed is success
        if task.is_completed:
            logger.info(f"complete_task: Task {task_id} already completed (idempotent)")
            return {
                "task_id": task.id,
                "status": "completed",
                "title": task.title
            }

        task.is_completed = True
        task.updated_at = datetime.utcnow()

        session.add(task)
        session.flush()  # Flush changes without committing

        logger.info(f"complete_task: Marked task {task_id} as completed for user {user_id}")

        return {
            "task_id": task.id,
            "status": "completed",
            "title": task.title
        }


# ---------------------------------------------------------------------------
# MCP Tool: update_task
# ---------------------------------------------------------------------------

@mcp.tool()
async def update_task(
    user_id: str,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None
) -> dict:
    """Update task title or description. At least one field must be provided.

    Args:
        user_id: The unique identifier for the user
        task_id: The ID of the task to update
        title: New title for the task (1-200 characters)
        description: New description for the task (max 1000 characters)
    """
    # Log tool call (CR-106)
    logger.info(f"[TOOL] update_task called: user_id={user_id}, task_id={task_id}")

    # Validation
    if not user_id or not user_id.strip():
        raise ValueError("user_id cannot be empty")

    if not isinstance(task_id, int) or task_id <= 0:
        raise ValueError("task_id must be a positive integer")

    if title is None and description is None:
        raise ValueError("at least one of title or description must be provided")

    title_clean = None
    if title is not None:
        if not title.strip():
            raise ValueError("title cannot be empty if provided")
        title_clean = title.strip()
        if len(title_clean) > 200:
            raise ValueError("title cannot exceed 200 characters")

    description_clean = None
    if description is not None:
        description_clean = description.strip()
        if len(description_clean) > 1000:
            raise ValueError("description cannot exceed 1000 characters")

    # Database operation
    with _SessionContext() as session:
        query = select(Task).where(
            Task.id == task_id,
            Task.owner_id == user_id.strip()
        )
        task = session.exec(query).first()

        if not task:
            raise PermissionError(
                f"Task {task_id} not found or you don't have permission to update it"
            )

        if title_clean is not None:
            task.title = title_clean

        if description_clean is not None:
            task.description = description_clean if description_clean else None

        task.updated_at = datetime.utcnow()

        session.add(task)
        session.flush()  # Flush changes without committing

        logger.info(f"update_task: Updated task {task_id} for user {user_id}")

        return {
            "task_id": task.id,
            "status": "updated",
            "title": task.title
        }


# ---------------------------------------------------------------------------
# MCP Tool: delete_task
# ---------------------------------------------------------------------------

@mcp.tool()
async def delete_task(user_id: str, task_id: int) -> dict:
    """Permanently delete a task. Returns the deleted task title for confirmation.

    Args:
        user_id: The unique identifier for the user
        task_id: The ID of the task to delete
    """
    # Log tool call (CR-106)
    logger.info(f"[TOOL] delete_task called: user_id={user_id}, task_id={task_id}")

    # Validation
    if not user_id or not user_id.strip():
        raise ValueError("user_id cannot be empty")

    if not isinstance(task_id, int) or task_id <= 0:
        raise ValueError("task_id must be a positive integer")

    # Database operation
    with _SessionContext() as session:
        query = select(Task).where(
            Task.id == task_id,
            Task.owner_id == user_id.strip()
        )
        task = session.exec(query).first()

        if not task:
            raise PermissionError(
                f"Task {task_id} not found or you don't have permission to delete it"
            )

        task_title = task.title

        session.delete(task)
        session.flush()  # Flush deletion without committing

        logger.info(f"delete_task: Deleted task {task_id} ('{task_title}') for user {user_id}")

        return {
            "task_id": task_id,
            "status": "deleted",
            "title": task_title
        }


# ---------------------------------------------------------------------------
# Integration helpers for chat endpoint
# ---------------------------------------------------------------------------

def get_mcp_tool_handlers() -> dict:
    """Get tool handler functions for the orchestrator.

    Returns a dict mapping tool names to their async handler functions.
    These are the same functions registered with @mcp.tool() decorators.
    """
    return {
        "add_task": add_task,
        "list_tasks": list_tasks,
        "complete_task": complete_task,
        "update_task": update_task,
        "delete_task": delete_task,
    }


def get_mcp_tool_schemas() -> list:
    """Get tool schemas auto-generated by the MCP SDK from type hints.

    Extracts schemas from the MCP server's internal tool registry.
    These schemas are generated automatically when tools are registered
    via @mcp.tool() decorators - no manual JSON schemas required.

    Returns list of dicts with name, description, and input_schema.
    """
    schemas = []

    # Access FastMCP's internal tool manager
    tool_manager = getattr(mcp, '_tool_manager', None)
    if tool_manager is not None:
        tools_dict = getattr(tool_manager, '_tools', {})
        for name, tool in tools_dict.items():
            schemas.append({
                "name": tool.name,
                "description": tool.description or "",
                "input_schema": tool.parameters
            })

    return schemas
