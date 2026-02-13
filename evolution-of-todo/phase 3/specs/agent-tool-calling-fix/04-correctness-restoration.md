# STEP 4: Correctness Restoration Spec

**Feature**: Agent Tool Calling System Restoration
**Date**: 2026-02-12
**Status**: Root-Cause Investigation

---

## Purpose

This document defines precisely what must be true for the system to be correct, what flags/configs/wiring must exist, and what invariants must be enforced to prevent this failure from recurring.

---

## Correctness Criteria

### Definition of Correct Behavior

The system is **correct** when:

1. **Tool Availability**: Agent has access to all 5 MCP tools at runtime
2. **Tool Invocation**: Agent calls tools instead of hallucinating responses
3. **Tool Execution**: Tools execute successfully and return results
4. **Result Integration**: Agent incorporates tool results into responses
5. **State Consistency**: Database state matches agent claims
6. **Message Integrity**: Conversation history is preserved without corruption

---

## Required System Properties

### Property 1: Tool Schemas in LLM Requests

**Requirement**: Every LLM API request MUST include tool schemas when the agent might need to call tools.

**Implementation**:
```python
# LLM request MUST contain:
{
    "model": "llama-3.3-70b",
    "messages": [...],
    "tools": [
        {"type": "function", "function": {"name": "add_task", ...}},
        {"type": "function", "function": {"name": "list_tasks", ...}},
        {"type": "function", "function": {"name": "complete_task", ...}},
        {"type": "function", "function": {"name": "update_task", ...}},
        {"type": "function", "function": {"name": "delete_task", ...}}
    ],
    "tool_choice": "auto"
}
```

**Verification**:
```python
# Add assertion before LLM call
assert "tools" in request_params, "Tools must be included in LLM request"
assert len(request_params["tools"]) == 5, "All 5 tools must be available"
```

**Monitoring**:
```python
# Log every LLM request
logger.info(f"LLM request: model={model}, tools={len(tools)}, tool_choice={tool_choice}")
```

---

### Property 2: Tool Call Detection and Execution

**Requirement**: When LLM returns tool calls, they MUST be executed before generating final response.

**Implementation**:
```python
response = await llm.complete(messages, tools=tools)

if response.tool_calls:
    # MUST execute tools
    tool_results = []
    for tool_call in response.tool_calls:
        result = await execute_tool(tool_call)
        tool_results.append(result)

    # MUST make second LLM call with results
    final_response = await llm.complete(
        messages + [response] + tool_results
    )
    return final_response
else:
    return response
```

**Verification**:
```python
# Add assertion after tool execution
if tool_calls:
    assert len(tool_results) == len(tool_calls), "All tools must be executed"
    assert all(r.success for r in tool_results), "All tools must succeed"
```

**Monitoring**:
```python
# Log tool execution
logger.info(f"Executing {len(tool_calls)} tool calls")
for tool_call in tool_calls:
    logger.info(f"Tool: {tool_call.function.name}, Args: {tool_call.function.arguments}")
```

---

### Property 3: MCP Server Connectivity

**Requirement**: MCP server MUST be reachable and responsive at all times.

**Implementation**:
```python
# Health check on startup
async def verify_mcp_connection():
    try:
        tools = await mcp_server.list_tools()
        assert len(tools) == 5, f"Expected 5 tools, got {len(tools)}"
        logger.info(f"✓ MCP server connected: {len(tools)} tools available")
        return True
    except Exception as e:
        logger.error(f"✗ MCP server connection failed: {e}")
        raise RuntimeError("Cannot start without MCP server") from e

# Call during app startup
await verify_mcp_connection()
```

**Verification**:
```python
# Periodic health check
async def mcp_health_check():
    while True:
        try:
            await mcp_server.list_tools()
            logger.debug("MCP server health check: OK")
        except Exception as e:
            logger.error(f"MCP server health check: FAILED - {e}")
            # Alert or restart
        await asyncio.sleep(60)  # Check every minute
```

**Monitoring**:
```python
# Track MCP request metrics
mcp_request_count = 0
mcp_error_count = 0
mcp_latency_sum = 0

async def execute_tool_with_metrics(tool_call):
    global mcp_request_count, mcp_error_count, mcp_latency_sum
    mcp_request_count += 1
    start = time.time()
    try:
        result = await mcp_server.call_tool(tool_call)
        latency = time.time() - start
        mcp_latency_sum += latency
        logger.info(f"Tool {tool_call.name} executed in {latency:.3f}s")
        return result
    except Exception as e:
        mcp_error_count += 1
        logger.error(f"Tool {tool_call.name} failed: {e}")
        raise
```

---

### Property 4: Model Function Calling Support

**Requirement**: The LLM model MUST support OpenAI-style function calling.

**Implementation**:
```python
# Test function calling on startup
async def verify_model_function_calling():
    test_tools = [{
        "type": "function",
        "function": {
            "name": "test_tool",
            "description": "Test tool",
            "parameters": {"type": "object", "properties": {}}
        }
    }]

    try:
        response = await llm.complete(
            messages=[{"role": "user", "content": "Call test_tool"}],
            tools=test_tools,
            tool_choice="required"
        )

        if not response.tool_calls:
            raise RuntimeError("Model did not return tool calls")

        logger.info("✓ Model supports function calling")
        return True
    except Exception as e:
        logger.error(f"✗ Model function calling test failed: {e}")
        return False

# Call during app startup
supports_function_calling = await verify_model_function_calling()
if not supports_function_calling:
    logger.warning("Falling back to OpenAI GPT-4 for tool calling")
    # Switch to OpenAI model
```

**Verification**:
```python
# Verify every response has expected format
def verify_response_format(response):
    if response.tool_calls:
        for tool_call in response.tool_calls:
            assert tool_call.id, "Tool call must have ID"
            assert tool_call.function.name, "Tool call must have function name"
            assert tool_call.function.arguments, "Tool call must have arguments"
    else:
        assert response.content, "Response must have content if no tool calls"
```

---

### Property 5: Database State Consistency

**Requirement**: Database state MUST match agent claims.

**Implementation**:
```python
# Verify tool execution results
async def add_task_with_verification(user_id: str, title: str, description: str):
    # Execute tool
    task = await add_task(user_id, title, description)

    # Verify in database
    db_task = await session.get(Task, task.id)
    assert db_task is not None, f"Task {task.id} not found in database"
    assert db_task.title == title, f"Title mismatch: {db_task.title} != {title}"
    assert db_task.user_id == user_id, f"User ID mismatch: {db_task.user_id} != {user_id}"

    logger.info(f"✓ Task {task.id} verified in database")
    return task
```

**Verification**:
```python
# Post-response verification
async def verify_agent_claims(conversation_id: int):
    # Load last assistant message
    messages = await load_messages(conversation_id)
    last_message = messages[-1]

    if "added" in last_message.content.lower():
        # Verify task was actually added
        # Extract task details from message
        # Query database
        # Assert task exists
        pass

    if "completed" in last_message.content.lower():
        # Verify task was actually completed
        pass
```

**Monitoring**:
```python
# Track database operations
db_operations = {
    "add_task": 0,
    "list_tasks": 0,
    "complete_task": 0,
    "update_task": 0,
    "delete_task": 0
}

def track_db_operation(operation: str):
    db_operations[operation] += 1
    logger.info(f"DB operation: {operation} (total: {db_operations[operation]})")
```

---

### Property 6: Message Integrity

**Requirement**: Messages MUST have unique IDs and MUST NOT be overwritten.

**Implementation**:
```python
# Generate guaranteed-unique message IDs
import uuid

def generate_message_id() -> str:
    return f"msg_{uuid.uuid4().hex}"

# Verify uniqueness before saving
async def save_message(conversation_id: int, message: Message):
    # Check if ID already exists
    existing = await session.execute(
        select(Message).where(Message.id == message.id)
    )
    if existing.scalar_one_or_none():
        raise ValueError(f"Message ID {message.id} already exists")

    # Save with INSERT (not UPDATE)
    session.add(message)
    await session.commit()

    logger.info(f"✓ Message {message.id} saved")
```

**Verification**:
```python
# Verify message order and integrity
async def verify_conversation_integrity(conversation_id: int):
    messages = await load_messages(conversation_id)

    # Check for duplicate IDs
    ids = [m.id for m in messages]
    assert len(ids) == len(set(ids)), "Duplicate message IDs detected"

    # Check chronological order
    timestamps = [m.created_at for m in messages]
    assert timestamps == sorted(timestamps), "Messages out of order"

    # Check role alternation (user → assistant → user → ...)
    roles = [m.role for m in messages]
    for i in range(len(roles) - 1):
        if roles[i] == "user":
            assert roles[i+1] == "assistant", f"Expected assistant after user at index {i}"

    logger.info(f"✓ Conversation {conversation_id} integrity verified")
```

---

## Required Configuration

### Config 1: Model Selection

**Purpose**: Allow switching between Cerebras and OpenAI based on function calling support.

**Implementation**:
```python
# backend/src/config/settings.py
class Settings(BaseSettings):
    # Existing
    cerebras_api_key: str = ""
    cerebras_base_url: str = "https://api.cerebras.ai/v1"
    cerebras_model: str = "llama-3.3-70b"

    # New
    openai_api_key: str = ""
    openai_model: str = "gpt-4-turbo-preview"
    use_openai_for_tools: bool = False  # Feature flag

    # Auto-detection
    auto_detect_function_calling: bool = True
```

**Environment Variables**:
```bash
# .env
CEREBRAS_API_KEY=csk-...
OPENAI_API_KEY=sk-...
USE_OPENAI_FOR_TOOLS=false
AUTO_DETECT_FUNCTION_CALLING=true
```

---

### Config 2: Tool Calling Settings

**Purpose**: Control tool calling behavior.

**Implementation**:
```python
class ToolCallingSettings(BaseSettings):
    enabled: bool = True
    tool_choice: str = "auto"  # auto | required | none
    max_tool_calls_per_turn: int = 5
    tool_timeout_seconds: int = 30
    retry_failed_tools: bool = True
    max_tool_retries: int = 3
```

---

### Config 3: Logging and Monitoring

**Purpose**: Enable comprehensive logging for debugging.

**Implementation**:
```python
class LoggingSettings(BaseSettings):
    log_level: str = "INFO"
    log_llm_requests: bool = True
    log_llm_responses: bool = True
    log_tool_calls: bool = True
    log_tool_results: bool = True
    log_mcp_requests: bool = True
    log_database_operations: bool = True
```

---

## Required Wiring

### Wiring 1: Tool Extraction from MCP Servers

**Purpose**: Extract tools from agent's MCP servers and convert to OpenAI format.

**Implementation**:
```python
# backend/src/agents/tool_utils.py
async def extract_tools_from_agent(agent: Agent) -> list[dict]:
    """Extract and convert MCP tools to OpenAI format."""
    all_tools = []

    for mcp_server in agent.mcp_servers:
        # List tools from MCP server
        mcp_tools = await mcp_server.list_tools()

        # Convert each tool to OpenAI format
        for mcp_tool in mcp_tools:
            openai_tool = {
                "type": "function",
                "function": {
                    "name": mcp_tool.name,
                    "description": mcp_tool.description,
                    "parameters": mcp_tool.inputSchema
                }
            }
            all_tools.append(openai_tool)

    logger.info(f"Extracted {len(all_tools)} tools from {len(agent.mcp_servers)} MCP servers")
    return all_tools
```

---

### Wiring 2: Tool Passing to Runner

**Purpose**: Ensure tools are passed to Runner.run_streamed().

**Implementation**:
```python
# backend/src/agents/chatkit_server.py
async def respond(self, request: ChatRequest) -> StreamingResponse:
    # ... existing code ...

    # Extract tools from agent
    tools = await extract_tools_from_agent(self.agent)

    # Pass tools to Runner
    result = Runner.run_streamed(
        self.agent,
        input_items,
        context=agent_context,
        tools=tools,  # ← ADD THIS
    )

    # ... rest of code ...
```

**Note**: This assumes Runner.run_streamed() accepts a `tools` parameter. If not, we need to investigate the SDK's API.

---

### Wiring 3: Model Factory with Fallback

**Purpose**: Create model with automatic fallback to OpenAI if Cerebras doesn't support function calling.

**Implementation**:
```python
# backend/src/agents/model_factory.py
async def create_model_with_function_calling() -> OpenAIChatCompletionsModel:
    """Create LLM model with function calling support."""

    # Try Cerebras first
    if not settings.use_openai_for_tools:
        cerebras_client = AsyncOpenAI(
            api_key=settings.cerebras_api_key,
            base_url=settings.cerebras_base_url,
        )
        cerebras_model = OpenAIChatCompletionsModel(
            model=settings.cerebras_model,
            openai_client=cerebras_client,
        )

        # Test function calling
        if settings.auto_detect_function_calling:
            supports_fc = await test_function_calling(cerebras_model)
            if supports_fc:
                logger.info("✓ Using Cerebras with function calling")
                return cerebras_model
            else:
                logger.warning("✗ Cerebras doesn't support function calling, falling back to OpenAI")
        else:
            return cerebras_model

    # Fallback to OpenAI
    if not settings.openai_api_key:
        raise RuntimeError("OpenAI API key required for function calling")

    openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
    openai_model = OpenAIChatCompletionsModel(
        model=settings.openai_model,
        openai_client=openai_client,
    )

    logger.info("✓ Using OpenAI GPT-4 for function calling")
    return openai_model
```

---

## Invariants to Enforce

### Invariant 1: Tools Always Available

**Statement**: If agent has MCP servers, tools MUST be available in LLM requests.

**Enforcement**:
```python
def enforce_tools_available(agent: Agent, request_params: dict):
    if agent.mcp_servers and len(agent.mcp_servers) > 0:
        assert "tools" in request_params, "Tools must be in request when agent has MCP servers"
        assert len(request_params["tools"]) > 0, "Tools array cannot be empty"
```

---

### Invariant 2: Tool Calls Always Executed

**Statement**: If LLM returns tool calls, they MUST be executed before final response.

**Enforcement**:
```python
def enforce_tool_execution(response, tool_results):
    if response.tool_calls:
        assert tool_results is not None, "Tool results must exist when tool calls are made"
        assert len(tool_results) == len(response.tool_calls), "All tool calls must be executed"
```

---

### Invariant 3: Database Matches Claims

**Statement**: If agent claims an action was taken, database MUST reflect that action.

**Enforcement**:
```python
async def enforce_database_consistency(agent_message: str, user_id: str):
    # Parse agent message for claims
    if "added" in agent_message.lower() and "task" in agent_message.lower():
        # Extract task title from message
        # Verify task exists in database
        tasks = await list_tasks(user_id)
        # Assert task is in list
        pass
```

---

### Invariant 4: Message IDs Unique

**Statement**: No two messages can have the same ID.

**Enforcement**:
```python
# Database constraint
class Message(SQLModel, table=True):
    id: str = Field(primary_key=True)  # Enforces uniqueness
    # ... other fields ...

# Application-level check
async def enforce_unique_message_id(message_id: str):
    existing = await session.get(Message, message_id)
    if existing:
        raise ValueError(f"Message ID {message_id} already exists")
```

---

### Invariant 5: No Silent Failures

**Statement**: All failures MUST be logged and/or raised as exceptions.

**Enforcement**:
```python
# Wrap all critical operations
async def safe_execute_tool(tool_call):
    try:
        result = await execute_tool(tool_call)
        return result
    except Exception as e:
        logger.error(f"Tool execution failed: {tool_call.function.name} - {e}")
        raise  # Re-raise, don't swallow

# Never catch and ignore
# BAD:
try:
    await execute_tool(tool_call)
except:
    pass  # ❌ Silent failure

# GOOD:
try:
    await execute_tool(tool_call)
except Exception as e:
    logger.error(f"Tool failed: {e}")
    raise  # ✓ Failure is visible
```

---

## Testing Requirements

### Test 1: End-to-End Tool Calling

**Purpose**: Verify complete tool calling flow.

**Implementation**:
```python
async def test_end_to_end_tool_calling():
    # Setup
    user_id = "test_user"
    conversation_id = await create_conversation(user_id)

    # Send message that requires tool call
    response = await chat(
        conversation_id=conversation_id,
        user_id=user_id,
        message="Add a task to buy milk"
    )

    # Verify tool was called
    tasks = await list_tasks(user_id)
    assert any(t.title == "Buy milk" for t in tasks), "Task was not created"

    # Verify response mentions the task
    assert "milk" in response.lower(), "Response doesn't mention the task"

    logger.info("✓ End-to-end tool calling test passed")
```

---

### Test 2: Model Function Calling Support

**Purpose**: Verify model supports function calling.

**Implementation**:
```python
async def test_model_function_calling():
    model = await create_model_with_function_calling()

    response = await model.complete(
        messages=[{"role": "user", "content": "Call test_function"}],
        tools=[{
            "type": "function",
            "function": {
                "name": "test_function",
                "description": "Test",
                "parameters": {"type": "object", "properties": {}}
            }
        }],
        tool_choice="required"
    )

    assert response.tool_calls, "Model did not return tool calls"
    assert response.tool_calls[0].function.name == "test_function"

    logger.info("✓ Model function calling test passed")
```

---

### Test 3: MCP Server Connectivity

**Purpose**: Verify MCP server is reachable.

**Implementation**:
```python
async def test_mcp_connectivity():
    tools = await mcp_server.list_tools()
    assert len(tools) == 5, f"Expected 5 tools, got {len(tools)}"

    expected_tools = ["add_task", "list_tasks", "complete_task", "update_task", "delete_task"]
    actual_tools = [t.name for t in tools]
    assert set(actual_tools) == set(expected_tools), f"Tool mismatch: {actual_tools}"

    logger.info("✓ MCP connectivity test passed")
```

---

## Summary

For the system to be correct, the following MUST be true:

1. **Tools in Requests**: Every LLM request includes tool schemas
2. **Tool Execution**: Tool calls are detected and executed
3. **MCP Connectivity**: MCP server is reachable and responsive
4. **Model Support**: LLM model supports function calling
5. **State Consistency**: Database matches agent claims
6. **Message Integrity**: Messages have unique IDs and aren't corrupted

These properties are enforced through:
- Configuration (model selection, tool settings, logging)
- Wiring (tool extraction, passing to Runner, model factory)
- Invariants (runtime assertions and checks)
- Testing (end-to-end, unit, integration)

**No system should go to production without all these properties verified and enforced.**
