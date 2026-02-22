# Change Record: Agent Tool Execution Fix

**Date**: 2026-02-12
**Feature**: 017-migrate-official-sdks
**Document Type**: Change Record
**Status**: Awaiting Approval

## Overview

This change record documents all modifications required to enable the Agent to properly discover and execute MCP tools when processing user requests.

## Changes Required

### CR-001: Add Tool Discovery Logging

**File**: `backend/src/agents/chatkit_server.py`
**Function**: `get_agent()`
**Line**: After line 89 (after Agent instantiation)
**Type**: Diagnostic Addition
**Priority**: P0 (Critical for diagnosis)

**Current Code** (lines 80-92):
```python
_agent_instance = Agent(
    name="TodoAssistant",
    instructions=get_system_prompt(),
    model=_create_cerebras_model(),
    mcp_servers=[_mcp_server],
    model_settings=ModelSettings(
        temperature=0.7,
        max_tokens=1000,
    ),
)

logger.info("Agent initialized with MCP server at %s", MCP_SERVER_URL)
return _agent_instance
```

**New Code**:
```python
_agent_instance = Agent(
    name="TodoAssistant",
    instructions=get_system_prompt(),
    model=_create_cerebras_model(),
    mcp_servers=[_mcp_server],
    model_settings=ModelSettings(
        temperature=0.7,
        max_tokens=1000,
    ),
)

# Verify MCP tools are discovered
if _mcp_server:
    try:
        tools = await _mcp_server.list_tools()
        tool_names = [t.name for t in tools] if tools else []
        logger.info(f"MCP tools available to agent: {tool_names}")
        if not tools:
            logger.warning("MCP server connected but no tools discovered!")
    except Exception as e:
        logger.error(f"Failed to list MCP tools: {e}")

logger.info("Agent initialized with MCP server at %s", MCP_SERVER_URL)
return _agent_instance
```

**Rationale**: Verify that MCP tools are being discovered at agent initialization time. This is the first diagnostic step to confirm the tool registry is populated.

**Expected Log Output**:
```
INFO: MCP server connected at http://localhost:8001/mcp
INFO: MCP tools available to agent: ['add_task', 'list_tasks', 'complete_task', 'update_task', 'delete_task']
INFO: Agent initialized with MCP server at http://localhost:8001/mcp
```

---

### CR-002: Add Request Context Logging

**File**: `backend/src/agents/chatkit_server.py`
**Function**: `respond()`
**Line**: After line 123 (before Runner.run_streamed)
**Type**: Diagnostic Addition
**Priority**: P0 (Critical for diagnosis)

**Current Code** (lines 144-149):
```python
# Run agent with streaming
result = Runner.run_streamed(
    agent,
    input_items,
    context=agent_context,
)
```

**New Code**:
```python
# Log request context for debugging
logger.info(f"Processing chat request for user: {context.user_id}")
logger.info(f"Input items count: {len(input_items)}")
logger.info(f"Agent MCP servers: {len(agent.mcp_servers) if agent.mcp_servers else 0}")

# Run agent with streaming
result = Runner.run_streamed(
    agent,
    input_items,
    context=agent_context,
)
```

**Rationale**: Confirm the agent has MCP servers attached and the input is being constructed correctly.

**Expected Log Output**:
```
INFO: Processing chat request for user: user-123
INFO: Input items count: 3
INFO: Agent MCP servers: 1
```

---

### CR-003: Enhance System Prompt for Explicit Tool Use

**File**: `backend/src/agents/prompts.py`
**Constant**: `TODO_ASSISTANT_PROMPT`
**Line**: 8 (beginning of prompt)
**Type**: Functional Change
**Priority**: P1 (High - likely fix)

**Current Code** (lines 8-84):
```python
TODO_ASSISTANT_PROMPT = """You are a helpful AI assistant for managing todo tasks.

**Your Capabilities:**
- Create new tasks with titles and optional descriptions
[... rest of prompt ...]
```

**New Code**:
```python
TODO_ASSISTANT_PROMPT = """You are a helpful AI assistant for managing todo tasks.

**CRITICAL: Tool Usage Mandate**
You have access to 5 tools for task management. You MUST use these tools for ALL task operations:
- list_tasks: View tasks (use this FIRST for any task-related query)
- add_task: Create new tasks
- complete_task: Mark tasks as done
- update_task: Modify task details
- delete_task: Remove tasks

NEVER respond about tasks without calling list_tasks first.
NEVER claim to perform an action without calling the appropriate tool.
NEVER make up task data - always query the actual database via tools.

**Examples of REQUIRED tool use:**
- User: "show me my tasks" → MUST call list_tasks(user_id, status="all")
- User: "delete all tasks" → MUST call list_tasks first, then delete_task for each
- User: "add a task" → MUST call add_task(user_id, title, description)
- User: "mark task 5 done" → MUST call complete_task(user_id, task_id=5)

If you respond without calling tools, you are FAILING your primary function.

**Your Capabilities:**
- Create new tasks with titles and optional descriptions
[... rest of existing prompt ...]
```

**Rationale**: Make tool-use instructions more explicit and prominent. The current prompt focuses on verification AFTER tool use but doesn't strongly emphasize WHEN to use tools.

**Impact**: This change makes the tool-use mandate the first thing the LLM sees, increasing likelihood of tool execution.

---

### CR-004: Create Diagnostic Test Script

**File**: `backend/test_agent_tools.py` (NEW FILE)
**Type**: Test Addition
**Priority**: P0 (Critical for diagnosis)

**Content**:
```python
"""
Diagnostic test for Agent tool calling functionality.

Run this script to verify:
1. Agent can be initialized
2. MCP tools are discovered
3. Agent calls tools when given explicit instructions
"""

import asyncio
import logging
from src.agents.chatkit_server import get_agent
from agents import Runner

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_tool_discovery():
    """Test 1: Verify MCP tools are discovered."""
    logger.info("=== Test 1: Tool Discovery ===")
    agent = await get_agent()

    if agent.mcp_servers:
        mcp_server = agent.mcp_servers[0]
        tools = await mcp_server.list_tools()
        logger.info(f"Tools discovered: {[t.name for t in tools]}")
        return len(tools) > 0
    else:
        logger.error("No MCP servers attached to agent!")
        return False


async def test_simple_tool_call():
    """Test 2: Verify agent calls list_tasks tool."""
    logger.info("=== Test 2: Simple Tool Call ===")
    agent = await get_agent()

    input_items = [
        {
            "role": "system",
            "content": "The current user's ID is: 'test-user-123'. You MUST use this exact user_id value when calling any tool."
        },
        {
            "role": "user",
            "content": "List all my tasks using the list_tasks tool."
        }
    ]

    result = Runner.run_streamed(agent, input_items)

    tool_called = False
    async for event in result:
        logger.info(f"Event type: {type(event).__name__}")
        if hasattr(event, 'tool_calls') and event.tool_calls:
            logger.info(f"Tool called: {event.tool_calls}")
            tool_called = True

    return tool_called


async def main():
    """Run all diagnostic tests."""
    logger.info("Starting Agent Tool Diagnostics")

    test1_passed = await test_tool_discovery()
    logger.info(f"Test 1 (Tool Discovery): {'PASS' if test1_passed else 'FAIL'}")

    if test1_passed:
        test2_passed = await test_simple_tool_call()
        logger.info(f"Test 2 (Tool Call): {'PASS' if test2_passed else 'FAIL'}")
    else:
        logger.error("Skipping Test 2 - tools not discovered")


if __name__ == "__main__":
    asyncio.run(main())
```

**Rationale**: Isolated test to verify tool calling works outside of the full ChatKit flow. This helps isolate whether the issue is in the Agent/Runner or in the ChatKit integration.

**Usage**:
```bash
cd backend
python test_agent_tools.py
```

---

### CR-005: Verify Cerebras Model Tool Support (Investigation)

**File**: N/A (External investigation)
**Type**: Research Task
**Priority**: P0 (Blocking decision)

**Action Required**:
1. Check Cerebras API documentation at https://inference-docs.cerebras.ai/
2. Search for "function calling" or "tool use" support
3. Verify llama-3.3-70b model supports OpenAI-compatible function calling
4. Test with a simple API call to confirm tool schema format

**Decision Point**:
- **If Cerebras supports tools**: Proceed with current model, verify schema format
- **If Cerebras doesn't support tools**: Implement CR-006 (fallback to OpenAI)

---

### CR-006: Add OpenAI Fallback for Tool Support (Conditional)

**File**: `backend/src/agents/chatkit_server.py`
**Function**: `_create_cerebras_model()` → rename to `_create_model()`
**Type**: Functional Change
**Priority**: P1 (High - if Cerebras doesn't support tools)
**Condition**: Only implement if CR-005 confirms Cerebras doesn't support function calling

**Current Code** (lines 41-50):
```python
def _create_cerebras_model() -> OpenAIChatCompletionsModel:
    """Create an OpenAI-compatible model pointing to Cerebras."""
    client = AsyncOpenAI(
        api_key=settings.cerebras_api_key,
        base_url=settings.cerebras_base_url,
    )
    return OpenAIChatCompletionsModel(
        model=settings.cerebras_model,
        openai_client=client,
    )
```

**New Code**:
```python
def _create_model() -> OpenAIChatCompletionsModel:
    """Create model with tool calling support."""
    # Use OpenAI for reliable tool calling support
    # Cerebras llama-3.3-70b may not support function calling
    if settings.use_openai_for_tools:
        logger.info("Using OpenAI GPT-4 for tool calling support")
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        return OpenAIChatCompletionsModel(
            model="gpt-4-turbo-preview",
            openai_client=client,
        )
    else:
        logger.info("Using Cerebras for model inference")
        client = AsyncOpenAI(
            api_key=settings.cerebras_api_key,
            base_url=settings.cerebras_base_url,
        )
        return OpenAIChatCompletionsModel(
            model=settings.cerebras_model,
            openai_client=client,
        )
```

**Also update** `get_agent()` line 83:
```python
model=_create_model(),  # Changed from _create_cerebras_model()
```

**Settings addition** in `backend/src/config/settings.py`:
```python
class Settings(BaseSettings):
    # ... existing fields ...

    # OpenAI API (for tool calling if Cerebras doesn't support it)
    openai_api_key: str = ""  # Set via OPENAI_API_KEY environment variable
    use_openai_for_tools: bool = False  # Set to True if Cerebras doesn't support tools
```

**Rationale**: If Cerebras doesn't support function calling, we need a fallback to a model that does. OpenAI GPT-4 has robust tool calling support.

---

## Implementation Sequence

### Phase 1: Diagnosis (Implement First)
1. **CR-001**: Add tool discovery logging
2. **CR-002**: Add request context logging
3. **CR-004**: Create diagnostic test script
4. **CR-005**: Research Cerebras tool support
5. Run backend, trigger chat request, analyze logs

**Expected Outcome**: Logs will reveal whether tools are discovered and if they're being passed to the model.

### Phase 2: Fix (Based on Diagnosis)
- **If tools NOT discovered**: Debug MCP server connection and tool registration
- **If tools discovered but NOT used**: Implement CR-003 (enhance prompt)
- **If model doesn't support tools**: Implement CR-006 (OpenAI fallback)

### Phase 3: Validation
1. Run diagnostic test script (CR-004)
2. Test in ChatKit UI with "show me my tasks"
3. Test with "delete all tasks"
4. Verify tool calls in logs
5. Verify correct responses in UI

## Files Modified

| File | Changes | Lines Affected | Type |
|------|---------|----------------|------|
| `backend/src/agents/chatkit_server.py` | CR-001, CR-002, CR-006 | 89-92, 144-149, 41-50 | Diagnostic + Functional |
| `backend/src/agents/prompts.py` | CR-003 | 8-84 | Functional |
| `backend/src/config/settings.py` | CR-006 | 24-26 | Configuration |
| `backend/test_agent_tools.py` | CR-004 | NEW FILE | Test |

## Rollback Procedure

If changes cause regressions:
1. Revert CR-003 (prompt changes) - keep original prompt
2. Keep CR-001, CR-002 (logging) - useful for debugging
3. Revert CR-006 if implemented - restore Cerebras-only model
4. Keep CR-004 (test script) - useful for future debugging

## Approval Required

**Awaiting user approval to proceed with implementation.**

Please review:
1. Agent Execution Spec
2. Failure Analysis Spec
3. Correction Spec
4. This Change Record

Confirm approval to implement Phase 1 (Diagnosis) changes.
