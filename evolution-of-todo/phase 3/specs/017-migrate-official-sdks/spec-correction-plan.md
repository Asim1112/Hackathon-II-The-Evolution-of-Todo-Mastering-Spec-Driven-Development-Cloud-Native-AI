# Correction Spec: Enable Tool Execution in Agent

**Date**: 2026-02-12
**Feature**: 017-migrate-official-sdks
**Document Type**: Correction Specification

## Problem Statement

The Agent responds with generic chat messages instead of executing MCP tools when user intent requires task operations (e.g., "delete all my tasks").

## Root Cause (Hypothesis)

Based on failure analysis, the most likely causes are:
1. MCP tools are not being passed to the LLM in the API request
2. The model doesn't support function calling or needs specific configuration
3. The system prompt doesn't explicitly trigger tool use

## Required Changes

### Change 1: Verify and Log Tool Discovery

**File**: `backend/src/agents/chatkit_server.py`
**Location**: `get_agent()` function, after agent creation
**Purpose**: Confirm MCP tools are discovered and available

**Add logging**:
```python
_agent_instance = Agent(...)

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

**Expected outcome**: Log should show `["add_task", "list_tasks", "complete_task", "update_task", "delete_task"]`

### Change 2: Verify Model Supports Function Calling

**Investigation Required**: Check if Cerebras llama-3.3-70b supports function calling

**Options**:
- **Option A**: If Cerebras supports function calling → Verify API format matches OpenAI
- **Option B**: If Cerebras doesn't support function calling → Switch to a model that does (e.g., OpenAI GPT-4)

**File**: `backend/src/agents/chatkit_server.py`
**Location**: `_create_cerebras_model()` function

**If Cerebras supports tools**, verify the model is configured correctly:
```python
def _create_cerebras_model() -> OpenAIChatCompletionsModel:
    client = AsyncOpenAI(
        api_key=settings.cerebras_api_key,
        base_url=settings.cerebras_base_url,
    )
    return OpenAIChatCompletionsModel(
        model=settings.cerebras_model,
        openai_client=client,
        # Verify if these parameters are needed:
        # supports_tools=True,
        # tool_choice="auto",
    )
```

**If Cerebras doesn't support tools**, add fallback to OpenAI:
```python
def _create_model() -> OpenAIChatCompletionsModel:
    # Use OpenAI for tool calling support
    if settings.use_openai_for_tools:
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        return OpenAIChatCompletionsModel(
            model="gpt-4-turbo-preview",
            openai_client=client,
        )
    else:
        # Cerebras fallback (no tool support)
        client = AsyncOpenAI(
            api_key=settings.cerebras_api_key,
            base_url=settings.cerebras_base_url,
        )
        return OpenAIChatCompletionsModel(
            model=settings.cerebras_model,
            openai_client=client,
        )
```

### Change 3: Enhance System Prompt for Tool Use

**File**: `backend/src/agents/prompts.py`
**Location**: `TODO_ASSISTANT_PROMPT` constant
**Purpose**: Make tool-use instructions more explicit and prominent

**Add at the very beginning** (before current content):
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
[... rest of existing prompt ...]
```

### Change 4: Verify Runner Passes Tools to Model

**Investigation Required**: Check if `Runner.run_streamed()` automatically includes MCP tools in the model API call

**File**: `backend/src/agents/chatkit_server.py`
**Location**: `respond()` method

**If Runner doesn't automatically pass tools**, we may need to explicitly extract and pass them:
```python
# Run agent with streaming
result = Runner.run_streamed(
    agent,
    input_items,
    context=agent_context,
    # Potentially needed:
    # tools=await _mcp_server.list_tools(),
)
```

### Change 5: Add Request/Response Logging

**File**: `backend/src/agents/chatkit_server.py`
**Location**: `respond()` method
**Purpose**: Debug what's being sent to the LLM

**Add logging before Runner.run_streamed**:
```python
logger.info(f"Running agent for user {context.user_id}")
logger.info(f"Input items count: {len(input_items)}")
logger.info(f"Agent has {len(agent.mcp_servers) if agent.mcp_servers else 0} MCP servers")

# Run agent with streaming
result = Runner.run_streamed(...)
```

### Change 6: Test with Simple Tool Call

**File**: Create `backend/test_agent_tools.py`
**Purpose**: Isolated test to verify tool calling works

```python
import asyncio
from src.agents.chatkit_server import get_agent
from agents import Runner

async def test_tool_call():
    agent = await get_agent()

    # Simple test: ask agent to list tasks
    input_items = [
        {
            "role": "system",
            "content": "The current user's ID is: 'test-user-123'. You MUST use this exact user_id value when calling any tool."
        },
        {
            "role": "user",
            "content": "List all my tasks"
        }
    ]

    result = Runner.run_streamed(agent, input_items)

    async for event in result:
        print(f"Event: {event}")

if __name__ == "__main__":
    asyncio.run(test_tool_call())
```

## Implementation Priority

### Phase 1: Diagnosis (Do First)
1. Add tool discovery logging (Change 1)
2. Add request/response logging (Change 5)
3. Run test and capture logs
4. Verify tools are discovered and passed to model

### Phase 2: Model Verification (If tools not working)
1. Check Cerebras documentation for function calling support
2. Test with simple tool call (Change 6)
3. If Cerebras doesn't support tools, switch to OpenAI (Change 2)

### Phase 3: Prompt Enhancement (If tools discovered but not used)
1. Enhance system prompt (Change 3)
2. Make tool-use instructions more prominent
3. Test with explicit tool-use commands

### Phase 4: Runner Configuration (If still not working)
1. Verify Runner.run_streamed passes tools (Change 4)
2. Explicitly pass tools if needed
3. Check Agent SDK documentation for tool configuration

## Success Criteria

After implementing corrections:
1. ✅ Backend logs show "MCP tools available: [add_task, list_tasks, ...]"
2. ✅ User says "show me my tasks" → Agent calls list_tasks tool
3. ✅ User says "delete all tasks" → Agent calls list_tasks, then delete_task for each
4. ✅ Agent never responds about tasks without calling tools first
5. ✅ Tool calls include correct user_id parameter
6. ✅ Agent follows verification mandate (calls list_tasks after mutations)

## Rollback Plan

If changes break existing functionality:
1. Revert prompt changes (keep original TODO_ASSISTANT_PROMPT)
2. Remove logging additions
3. Restore original model configuration
4. Document findings for alternative approach
