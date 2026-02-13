"""
Agent system prompts for the Todo Assistant.

This module defines the personality, capabilities, and behavior guidelines
for the AI todo assistant agent.
"""

TODO_ASSISTANT_PROMPT = """You are a helpful todo assistant. You have access to these tools:
- add_task: Create a new task
- list_tasks: Show all tasks (or filter by status: pending/completed)
- complete_task: Mark a task as done
- update_task: Modify task title or description
- delete_task: Remove a task

When the user asks about tasks, call the appropriate tool.
For greetings or casual conversation, respond naturally and offer to help with tasks.
Always be concise and helpful."""

ERROR_HANDLING_PROMPT = ""

CONTEXT_AWARENESS_PROMPT = ""


def get_system_prompt() -> str:
    """
    Returns the complete system prompt for the todo assistant agent.

    This combines all prompt components into a single comprehensive system message.
    """
    return "\n\n".join([
        TODO_ASSISTANT_PROMPT,
        ERROR_HANDLING_PROMPT,
        CONTEXT_AWARENESS_PROMPT
    ])


def get_base_prompt() -> str:
    """
    Returns just the base assistant prompt without error handling or context awareness.

    Useful for testing or when you want to customize the additional prompt components.
    """
    return TODO_ASSISTANT_PROMPT
