# BUG-005: Agent Not Calling MCP Tools (Hallucinating Responses)

**Date**: 2026-02-12
**Status**: Root cause analysis

## Symptoms

1. User asks "show me tasks list" → Agent responds "I don't see any tasks for you" (12 tasks exist in DB)
2. Agent never calls MCP tools (list_tasks, add_task, etc.)
3. Messages overwrite previous response instead of appending new ones

## Root Cause Analysis

### Issue 1: Agent Doesn't Know User ID

All 5 MCP tools require `user_id` as the first parameter:
```python
@mcp.tool()
async def list_tasks(user_id: str, status: str = "all") -> list:
```

The LLM needs to provide `user_id` when calling tools, but it has no way to know the current user's ID. The `context.user_id` is available in `respond()` but is never communicated to the LLM.

**Fix**: Inject the user_id into the input messages so the LLM can pass it to MCP tools.

### Issue 2: Singleton Agent May Have Stale MCP Connection

The `get_agent()` function uses a singleton pattern. If the first MCP connection attempt failed (which it did — the 500 error), the exception propagates and `_agent_instance` stays `None`. On the next request, it retries. But if the MCP tools aren't properly discovered, the agent runs without tools and hallucinates.

**Fix**: Add error handling and logging to verify MCP tool discovery.

## Fix Plan

1. In `chatkit_server.py`, prepend a context message to `input_items` with the user's ID
2. Add debug logging to verify MCP tools are discovered
3. Reset singleton state on connection failure so retries work cleanly
