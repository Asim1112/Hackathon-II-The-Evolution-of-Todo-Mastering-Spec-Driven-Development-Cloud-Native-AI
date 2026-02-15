# Change Record: Agent Tool Execution & Message Integrity Fix

**Date**: 2026-02-12
**Feature**: 017-migrate-official-sdks
**Document Type**: Change Record
**Status**: Awaiting Approval

## Overview

This change record documents all modifications required to fix two critical issues:
1. **Agent not calling tools** - hallucinating state and false execution claims
2. **Message corruption** - new messages overwriting previous messages

## Changes Required

---

### CR-101: Add Message ID Tracking Logging (Store Layer)

**File**: `backend/src/agents/store_adapter.py`
**Priority**: P0 (Critical for diagnosis)
**Type**: Diagnostic Addition
**Status**: Ready for implementation

**Location 1**: `add_thread_item()` method, line 263

**Current Code** (lines 263-280):
```python
async def add_thread_item(self, thread_id: str, item, context: RequestContext) -> None:
    conversation_id = self._parse_thread_id(thread_id, context.user_id)
    with Session(self._get_engine()) as session:
        item_type = getattr(item, "type", "")
        if item_type == "user_message":
            role = MessageRole.USER
        else:
            role = MessageRole.ASSISTANT

        message = Message(
            conversation_id=conversation_id,
            user_id=context.user_id,
            role=role,
            content=json.dumps(serialize_thread_item(item)),
            created_at=datetime.utcnow(),
        )
        session.add(message)
        session.commit()
```

**New Code**:
```python
async def add_thread_item(self, thread_id: str, item, context: RequestContext) -> None:
    conversation_id = self._parse_thread_id(thread_id, context.user_id)

    # Log incoming item (CR-101)
    logger.info(f"[STORE] Saving item: id={item.id}, type={item.type}, thread={thread_id}")

    with Session(self._get_engine()) as session:
        item_type = getattr(item, "type", "")
        if item_type == "user_message":
            role = MessageRole.USER
        else:
            role = MessageRole.ASSISTANT

        message = Message(
            conversation_id=conversation_id,
            user_id=context.user_id,
            role=role,
            content=json.dumps(serialize_thread_item(item)),
            created_at=datetime.utcnow(),
        )
        session.add(message)
        session.commit()
        session.refresh(message)

        # Log saved message (CR-101)
        logger.info(f"[STORE] Saved to DB: message.id={message.id}, item.id={item.id}")
```

**Location 2**: `load_thread_items()` method, line 255

**Current Code** (lines 255-261):
```python
items = [deserialize_thread_item(msg) for msg in data]

return Page(
    data=items,
    has_more=has_more,
    after=str(data[-1].id) if data else None,
)
```

**New Code**:
```python
items = [deserialize_thread_item(msg) for msg in data]

# Log loaded items (CR-101)
logger.info(f"[STORE] Loaded {len(items)} items from thread {thread_id}")
for item in items:
    logger.info(f"[STORE]   - id={item.id}, type={item.type}")

return Page(
    data=items,
    has_more=has_more,
    after=str(data[-1].id) if data else None,
)
```

**Rationale**: Track message IDs at the storage layer to identify where duplication occurs.

---

### CR-102: Add Streaming Event Logging

**File**: `backend/src/agents/chatkit_server.py`
**Priority**: P0 (Critical for diagnosis)
**Type**: Diagnostic Addition
**Status**: Ready for implementation

**Location**: `respond()` method, line 151

**Current Code** (lines 151-153):
```python
# Stream ChatKit events
async for event in stream_agent_response(agent_context, result):
    yield event
```

**New Code**:
```python
# Stream ChatKit events with ID tracking (CR-102)
logger.info(f"[RESPOND] Starting response stream for thread={thread.id}")
seen_message_ids = set()

async for event in stream_agent_response(agent_context, result):
    event_type = type(event).__name__
    event_id = getattr(event, 'id', None)

    logger.info(f"[STREAM] Event: {event_type}, id={event_id}")

    # Detect ID collision
    if event_id and event_id in seen_message_ids:
        logger.error(f"[STREAM] ⚠️  DUPLICATE MESSAGE ID: {event_id}")

    if event_id:
        seen_message_ids.add(event_id)

    yield event

logger.info(f"[RESPOND] Stream completed. Unique message IDs: {len(seen_message_ids)}")
```

**Rationale**: Track message IDs in the streaming layer to detect duplication at the source.

---

### CR-103: Investigate and Fix Tool Passing to LLM

**File**: `backend/src/agents/chatkit_server.py`
**Priority**: P0 (Critical - blocks all tool functionality)
**Type**: Functional Change
**Status**: Requires investigation first

**Investigation Required**:
1. Check if `Runner.run_streamed()` accepts a `tools` parameter
2. Check Agents SDK documentation for how MCP tools are passed to the model
3. Verify if tools need to be explicitly extracted and passed

**Option A: If Runner needs explicit tools parameter**

**Location**: `respond()` method, line 144

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
# Extract and pass tools explicitly (CR-103 Option A)
tools = None
if agent.mcp_servers:
    mcp_server = agent.mcp_servers[0]
    try:
        mcp_tools = await mcp_server.list_tools()

        # Convert MCP tools to OpenAI function format
        tools = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema,
                }
            }
            for tool in mcp_tools
        ]
        logger.info(f"[TOOLS] Passing {len(tools)} tools to Runner: {[t['function']['name'] for t in tools]}")
    except Exception as e:
        logger.error(f"[TOOLS] Failed to extract tools: {e}")

# Run agent with streaming and explicit tools
result = Runner.run_streamed(
    agent,
    input_items,
    context=agent_context,
    tools=tools,  # ← Explicitly pass tools
)
```

**Option B: If tools are automatically passed but model doesn't support them**

See CR-104 (Switch to OpenAI model)

**Rationale**: The most likely cause of tool failure is that tools aren't being passed to the LLM in the API request.

---

### CR-104: Switch to OpenAI Model for Tool Calling Support

**File**: `backend/src/agents/chatkit_server.py`
**Priority**: P0 (Critical if Cerebras doesn't support tools)
**Type**: Functional Change
**Status**: Conditional - only if Cerebras doesn't support function calling

**Location 1**: Rename function, line 41

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
    """Create model with function calling support."""

    # Use OpenAI for reliable tool calling support
    if settings.use_openai_for_tools:
        logger.info("[MODEL] Using OpenAI GPT-4 for tool calling support")
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        return OpenAIChatCompletionsModel(
            model="gpt-4-turbo-preview",
            openai_client=client,
        )
    else:
        logger.info("[MODEL] Using Cerebras llama-3.3-70b")
        client = AsyncOpenAI(
            api_key=settings.cerebras_api_key,
            base_url=settings.cerebras_base_url,
        )
        return OpenAIChatCompletionsModel(
            model=settings.cerebras_model,
            openai_client=client,
        )
```

**Location 2**: Update function call, line 83

**Current Code**:
```python
model=_create_cerebras_model(),
```

**New Code**:
```python
model=_create_model(),
```

**File**: `backend/src/config/settings.py`
**Location**: Add new settings, line 24

**Current Code** (lines 20-24):
```python
# Cerebras API (OpenAI-compatible)
cerebras_api_key: str = ""  # Set via CEREBRAS_API_KEY environment variable
cerebras_base_url: str = "https://api.cerebras.ai/v1"
cerebras_model: str = "llama-3.3-70b"
```

**New Code**:
```python
# Cerebras API (OpenAI-compatible)
cerebras_api_key: str = ""  # Set via CEREBRAS_API_KEY environment variable
cerebras_base_url: str = "https://api.cerebras.ai/v1"
cerebras_model: str = "llama-3.3-70b"

# OpenAI API (for tool calling if Cerebras doesn't support it)
openai_api_key: str = ""  # Set via OPENAI_API_KEY environment variable
use_openai_for_tools: bool = True  # Default to OpenAI for reliable tool calling
```

**Environment Variables Required**:
```bash
# Add to .env file
OPENAI_API_KEY=sk-...
USE_OPENAI_FOR_TOOLS=true
```

**Rationale**: If Cerebras llama-3.3-70b doesn't support function calling, we need a fallback to a model that does. OpenAI GPT-4 has proven, reliable tool calling support.

**Trade-off**: OpenAI is more expensive than Cerebras, but tool calling is critical for agent functionality.

---

### CR-105: Enhance System Prompt with Tool Mandate

**File**: `backend/src/agents/prompts.py`
**Priority**: P1 (High - improves tool usage)
**Type**: Functional Change
**Status**: Ready for implementation

**Location**: Beginning of `TODO_ASSISTANT_PROMPT`, line 8

**Current Code** (lines 8-16):
```python
TODO_ASSISTANT_PROMPT = """You are a helpful AI assistant for managing todo tasks.

**Your Capabilities:**
- Create new tasks with titles and optional descriptions
- View all tasks or specific tasks by ID
- Update task details (title, description, status)
- Mark tasks as complete or incomplete
- Delete tasks
```

**New Code**:
```python
TODO_ASSISTANT_PROMPT = """You are a helpful AI assistant for managing todo tasks.

**CRITICAL: You MUST use tools for ALL task operations.**

You have 5 tools available:
1. list_tasks(user_id, status) - View tasks (ALWAYS call this first for any task query)
2. add_task(user_id, title, description) - Create new tasks
3. complete_task(user_id, task_id) - Mark tasks as done
4. update_task(user_id, task_id, title, description) - Modify task details
5. delete_task(user_id, task_id) - Remove tasks

**MANDATORY RULES - You MUST follow these:**
- NEVER mention tasks without calling list_tasks first
- NEVER claim to perform actions without calling the appropriate tool
- NEVER make up task data - ALWAYS query the actual database via tools
- ALWAYS verify mutations by calling list_tasks after changes

**Examples of REQUIRED tool use:**
- User: "show me my tasks" → MUST call list_tasks(user_id, status="all")
- User: "delete all tasks" → MUST call list_tasks first, then delete_task for each, then list_tasks to verify
- User: "add buy milk" → MUST call add_task(user_id, title="buy milk")
- User: "hello" → Respond normally (no tools needed for greetings)

If you respond about tasks without calling tools, you are FAILING your primary function.

**Your Capabilities:**
- Create new tasks with titles and optional descriptions
- View all tasks or specific tasks by ID
- Update task details (title, description, status)
- Mark tasks as complete or incomplete
- Delete tasks
```

**Rationale**: Make tool-use mandate impossible to miss. The LLM sees this critical instruction before any other content.

---

### CR-106: Add Tool Call Verification Logging

**File**: `backend/src/mcp/mcp_server.py`
**Priority**: P1 (High - helps verify tools are being called)
**Type**: Diagnostic Addition
**Status**: Ready for implementation

**Location**: Each tool handler, add logging at the beginning

**Example for list_tasks** (line 115):

**Current Code** (lines 115-154):
```python
@mcp.tool()
async def list_tasks(user_id: str, status: str = "all") -> list:
    """Retrieve tasks for the user with optional status filter.

    Args:
        user_id: The unique identifier for the user
        status: Filter by status - 'all', 'pending', or 'completed'
    """
    # Validation
    if not user_id or not user_id.strip():
        raise ValueError("user_id cannot be empty")
```

**New Code**:
```python
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
```

**Apply same pattern to all 5 tools**:
- add_task (line 64)
- list_tasks (line 115)
- complete_task (line 162)
- update_task (line 218)
- delete_task (line 294)

**Rationale**: Verify that tools are actually being called when the agent processes requests.

---

## Implementation Sequence

### Phase 1: Diagnostic Logging (Already Completed)
- ✅ CR-001: Tool discovery logging (DONE)
- ✅ CR-002: Request context logging (DONE)
- ✅ CR-004: Diagnostic test script (DONE)

### Phase 2: Additional Diagnostics (Do First)
1. **CR-101**: Message ID tracking in store layer
2. **CR-102**: Streaming event logging
3. **CR-106**: Tool call verification logging

**Action**: Implement these, restart backend, run test, analyze logs

### Phase 3: Tool Access Fix (Based on Diagnostics)

**Decision Point**: Run diagnostic test script first
```bash
cd backend
python test_agent_tools.py
```

**If Test 1 PASS (tools discovered) but Test 2 FAIL (tools not called)**:
→ Implement CR-103 (explicit tool passing) OR CR-104 (switch to OpenAI)

**If Test 1 FAIL (tools not discovered)**:
→ Debug MCP server connection (unlikely, we fixed this)

**Always implement**:
→ CR-105 (enhanced prompt) - helps regardless of other fixes

### Phase 4: Message ID Fix (Based on Logs)

**After implementing CR-101 and CR-102**, analyze logs:

**If logs show duplicate IDs in streaming layer**:
→ Investigate ChatKit SDK behavior
→ Potentially add ID regeneration logic

**If logs show unique IDs but UI still corrupts**:
→ Frontend issue or ChatKit SDK bug
→ May need to file issue with ChatKit

### Phase 5: Validation

Run all four test scenarios:
1. Greeting test (no tools)
2. Task query test (calls list_tasks)
3. Task deletion test (calls multiple tools)
4. Follow-up test (message append, not overwrite)

## Files Modified

| File | Changes | Type | Priority |
|------|---------|------|----------|
| `backend/src/agents/store_adapter.py` | CR-101 | Diagnostic | P0 |
| `backend/src/agents/chatkit_server.py` | CR-102, CR-103, CR-104 | Diagnostic + Functional | P0 |
| `backend/src/agents/prompts.py` | CR-105 | Functional | P1 |
| `backend/src/config/settings.py` | CR-104 | Configuration | P0 |
| `backend/src/mcp/mcp_server.py` | CR-106 | Diagnostic | P1 |
| `backend/.env` | CR-104 | Configuration | P0 |

## Environment Setup Required

If implementing CR-104 (OpenAI fallback):

```bash
# Add to backend/.env
OPENAI_API_KEY=sk-proj-...
USE_OPENAI_FOR_TOOLS=true
```

## Success Criteria

After implementation:
1. ✅ Backend logs show "MCP tools available to agent: [add_task, list_tasks, ...]"
2. ✅ Backend logs show "[TOOL] list_tasks called: ..." when user asks about tasks
3. ✅ Agent responds to greetings without calling tools
4. ✅ Agent calls list_tasks when asked about tasks
5. ✅ Task counts match database exactly (12 tasks, not 7)
6. ✅ Agent never claims actions without calling tools
7. ✅ Database changes match agent claims
8. ✅ Each message has unique ID in logs
9. ✅ New messages append in UI, never overwrite
10. ✅ No hallucinated state or false execution claims

## Rollback Procedure

If changes cause regressions:
1. **Keep all diagnostic logging** (CR-101, CR-102, CR-106) - useful for debugging
2. **Revert CR-104** if OpenAI causes issues - restore Cerebras-only model
3. **Revert CR-105** if prompt causes confusion - restore original prompt
4. **Revert CR-103** if explicit tool passing breaks functionality
5. Document findings and try alternative approach

## Approval Required

**Awaiting user approval to proceed with Phase 2 implementation.**

Please confirm:
- ✅ "Yes, proceed with Phase 2 (CR-101, CR-102, CR-106)"
- OR provide feedback if changes are needed
