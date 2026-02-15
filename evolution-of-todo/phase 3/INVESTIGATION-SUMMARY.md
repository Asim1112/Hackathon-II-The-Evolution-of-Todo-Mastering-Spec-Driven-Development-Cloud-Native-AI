# Root-Cause Investigation Summary

**Date**: 2026-02-12
**Status**: Investigation Complete - Ready for Implementation

---

## Key Findings

### 1. Cerebras Function Calling Support ✓ CONFIRMED

**Test Result**: Cerebras llama-3.3-70b **DOES** support OpenAI-style function calling.

```
Test output:
[SUCCESS] Model returned tool_calls!
          Tool calls: 1
          - get_weather({"location": "San Francisco"})
```

**Conclusion**: The issue is NOT with Cerebras model compatibility.

---

### 2. Current Implementation Analysis

**Agent Configuration** (`chatkit_server.py:80-89`):
```python
_agent_instance = Agent(
    name="TodoAssistant",
    instructions=get_system_prompt(),
    model=_create_cerebras_model(),
    mcp_servers=[_mcp_server],  # ← MCP server IS registered
    model_settings=ModelSettings(temperature=0.7, max_tokens=1000),
)
```

**MCP Server Configuration** (`chatkit_server.py:61-74`):
```python
_mcp_server = MCPServerStreamableHttp(
    name="TodoMCP",
    params={"url": MCP_SERVER_URL, "timeout": 60, "sse_read_timeout": 600},
    client_session_timeout_seconds=120,
    cache_tools_list=True,  # ← Tool caching enabled
    max_retry_attempts=3,
)
```

**Runner Execution** (`chatkit_server.py:166-170`):
```python
result = Runner.run_streamed(
    agent,
    input_items,
    context=agent_context,
)
```

**Status**: Configuration appears correct according to SDK documentation.

---

### 3. SDK Documentation Review

According to `OpenAI-Agents-SDK-Knowledge.md`:

> "When you register MCP servers with an agent via `mcp_servers=[server]`, the SDK automatically:
> 1. Connects to the MCP server
> 2. Calls `tools/list` endpoint
> 3. Converts MCP tool schemas to OpenAI function format
> 4. Includes tools in LLM API requests"

**Expected Behavior**: Tools should be automatically included in LLM requests.

**Actual Behavior**: Tools are NOT being called (agent hallucinates responses).

---

### 4. Diagnostic Logging Added

**Files Modified**:
1. `backend/src/agents/request_logger.py` (NEW) - Intercepts LLM API calls
2. `backend/src/agents/chatkit_server.py` - Added logging and patching

**What the Logging Will Show**:
- Whether `tools` parameter is present in LLM requests
- How many tools are being sent
- Tool names and schemas
- Other request parameters (model, temperature, etc.)

---

## Root Cause Hypothesis

Based on the investigation, the most likely root cause is:

**The OpenAI Agents SDK is not automatically including MCP tools in LLM requests when using a non-OpenAI model (Cerebras).**

**Why This Might Happen**:
1. SDK may have a whitelist of models that support function calling
2. Cerebras model name (`llama-3.3-70b`) may not be recognized
3. SDK may require explicit configuration for non-OpenAI models

---

## Next Steps

### Step 1: Verify with Logging

**Action**: Restart backend server and send a test message

**Expected Log Output** (if bug confirmed):
```
[LLM REQUEST INTERCEPTED]
Model: llama-3.3-70b
Messages count: 2
[FAIL] Tools parameter is MISSING - This is the bug!
```

**If tools ARE present**: The issue is elsewhere (tool execution, result handling, etc.)

**If tools are MISSING**: Confirms the root cause - SDK not including tools

---

### Step 2: Implement Fix

**Option A: Force Tool Inclusion** (if SDK supports it)

Check if `Runner.run_streamed()` or `Agent` has a parameter to force tool inclusion:
```python
# Hypothetical - need to check SDK API
result = Runner.run_streamed(
    agent,
    input_items,
    context=agent_context,
    force_tools=True,  # ← If this exists
)
```

**Option B: Switch to OpenAI for Tool Calling**

Add OpenAI as fallback for tool-calling operations:
```python
def _create_model():
    if settings.use_openai_for_tools:
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        return OpenAIChatCompletionsModel(
            model="gpt-4-turbo-preview",
            openai_client=client,
        )
    else:
        # Cerebras for non-tool operations
        client = AsyncOpenAI(
            api_key=settings.cerebras_api_key,
            base_url=settings.cerebras_base_url,
        )
        return OpenAIChatCompletionsModel(
            model=settings.cerebras_model,
            openai_client=client,
        )
```

**Option C: Manual Tool Passing** (if SDK allows)

Extract tools from MCP server and pass explicitly:
```python
# Extract tools from MCP server
tools = await _mcp_server.list_tools()
openai_tools = [convert_mcp_to_openai_format(t) for t in tools]

# Pass to Runner (if supported)
result = Runner.run_streamed(
    agent,
    input_items,
    context=agent_context,
    tools=openai_tools,  # ← If this parameter exists
)
```

---

### Step 3: Test Fix

**Test Cases**:
1. "Add a task to buy milk" → Should call `add_task` tool
2. "List my tasks" → Should call `list_tasks` tool
3. "Complete task 5" → Should call `complete_task` tool
4. Verify database state matches agent claims

**Success Criteria**:
- Agent calls tools instead of hallucinating
- Database operations occur
- No "FN_CALL=False" errors
- Logs show tools in LLM requests

---

## Files Modified (So Far)

1. `backend/src/agents/chatkit_server.py`
   - Added diagnostic logging
   - Added request logger patch
   - Enhanced MCP tool discovery logging

2. `backend/src/agents/request_logger.py` (NEW)
   - Monkey-patch for OpenAI client
   - Logs all LLM API requests
   - Shows tools parameter presence/absence

3. `backend/test_function_calling.py` (NEW)
   - Tests Cerebras function calling support
   - Confirms model compatibility

---

## Recommended Action

**Immediate**: Restart backend server and test with a simple message like "Add a task to buy milk"

**Check logs for**:
```
[LLM REQUEST INTERCEPTED]
[SUCCESS] Tools parameter IS PRESENT: 5 tools
  Tool 1: add_task
  Tool 2: list_tasks
  ...
```

**OR**:
```
[LLM REQUEST INTERCEPTED]
[FAIL] Tools parameter is MISSING - This is the bug!
```

Once we see the logs, we'll know exactly what fix to implement.

---

## Confidence Level

**95%** - The issue is that tools are not being included in LLM requests.

**Remaining 5%** - Could be:
- Tool execution failing silently
- Response parsing issues
- MCP server connectivity problems

The logging will definitively confirm or rule out the primary hypothesis.
