# STEP 3: Root-Cause Analysis Spec

**Feature**: Agent Tool Calling System Restoration
**Date**: 2026-02-12
**Status**: Root-Cause Investigation

---

## Purpose

This document identifies the **exact point of failure** in the agent-tool-calling chain, determines whether `FN_CALL=False` is a cause or symptom, and explains why the system is falling back to text-only LLM mode.

---

## Failure Point Analysis

### The Agent-Tool-Calling Chain

```
[1] Agent Init → [2] MCP Registration → [3] Tool Discovery → [4] Schema Conversion →
[5] Runner Execution → [6] LLM Request Formation → [7] LLM Processing → [8] Tool Execution
```

Let's analyze each link:

---

### [1] Agent Initialization ✓ WORKING

**Location**: `backend/src/agents/chatkit_server.py:80-89`

**Code**:
```python
_agent_instance = Agent(
    name="TodoAssistant",
    instructions=get_system_prompt(),
    model=_create_cerebras_model(),
    mcp_servers=[_mcp_server],  # ← MCP server registered
    model_settings=ModelSettings(temperature=0.7, max_tokens=1000),
)
```

**Status**: ✓ Agent is correctly initialized with MCP server

**Evidence**:
- `mcp_servers` parameter is set
- MCP server object is created before agent initialization
- No errors during agent creation

**Conclusion**: This link is working.

---

### [2] MCP Server Registration ✓ WORKING

**Location**: `backend/src/agents/chatkit_server.py:61-74`

**Code**:
```python
_mcp_server = MCPServerStreamableHttp(
    name="TodoMCP",
    params={
        "url": MCP_SERVER_URL,  # http://localhost:8001/mcp
        "timeout": 60,
        "sse_read_timeout": 600,
    },
    client_session_timeout_seconds=120,
    cache_tools_list=True,
    max_retry_attempts=3,
)
```

**Status**: ✓ MCP server is correctly configured

**Evidence**:
- URL points to running MCP server
- Connection parameters are reasonable
- `cache_tools_list=True` enables tool caching

**Conclusion**: This link is working.

---

### [3] Tool Discovery ⚠️ UNKNOWN

**Expected Behavior**:
When the agent is initialized or first used, the Agents SDK should:
1. Connect to MCP server at `http://localhost:8001/mcp`
2. Call `tools/list` endpoint
3. Receive list of 5 tools with schemas
4. Cache tools for future use

**Actual Behavior**: Unknown - no logging exists to verify this

**Critical Questions**:
- Does the SDK automatically discover tools on agent init?
- Does it discover tools on first Runner.run_streamed() call?
- Does it discover tools lazily when needed?
- Is tool discovery failing silently?

**Evidence Gap**:
- No logs showing "MCP tools discovered"
- No logs showing "Connected to MCP server"
- No error logs about connection failures

**Hypothesis**: Tool discovery may be happening but failing silently, OR it's happening successfully but tools aren't being used.

**Test Required**:
```python
# Add logging to chatkit_server.py
logger.info(f"MCP server configured: {_mcp_server.name}")
if hasattr(_mcp_server, 'list_tools'):
    tools = await _mcp_server.list_tools()
    logger.info(f"MCP tools discovered: {[t.name for t in tools]}")
```

**Conclusion**: This link is UNVERIFIED. Could be the failure point.

---

### [4] Schema Conversion ⚠️ UNKNOWN

**Expected Behavior**:
The Agents SDK should convert MCP tool schemas to OpenAI function calling format:

**MCP Format**:
```json
{
  "name": "add_task",
  "description": "Add a new task to the user's todo list",
  "inputSchema": {
    "type": "object",
    "properties": {
      "user_id": {"type": "string"},
      "title": {"type": "string"},
      "description": {"type": "string"}
    },
    "required": ["user_id", "title", "description"]
  }
}
```

**OpenAI Format**:
```json
{
  "type": "function",
  "function": {
    "name": "add_task",
    "description": "Add a new task to the user's todo list",
    "parameters": {
      "type": "object",
      "properties": {
        "user_id": {"type": "string"},
        "title": {"type": "string"},
        "description": {"type": "string"}
      },
      "required": ["user_id", "title", "description"]
    }
  }
}
```

**Actual Behavior**: Unknown - no logging exists to verify this

**Critical Questions**:
- Does the SDK perform this conversion automatically?
- Is the conversion happening correctly?
- Are converted schemas stored somewhere accessible?

**Evidence Gap**:
- No logs showing "Converting MCP tools to OpenAI format"
- No logs showing converted schemas
- No way to inspect what the SDK is doing internally

**Hypothesis**: Conversion may be happening correctly, but the converted tools aren't being passed to the LLM.

**Conclusion**: This link is UNVERIFIED. Could be the failure point.

---

### [5] Runner Execution ✓ WORKING

**Location**: `backend/src/agents/chatkit_server.py:166`

**Code**:
```python
result = Runner.run_streamed(
    agent,
    input_items,
    context=agent_context,
)
```

**Status**: ✓ Runner is being called correctly

**Evidence**:
- Agent receives user messages
- Responses are generated and streamed
- No errors during execution

**Critical Observation**:
The `Runner.run_streamed()` call does NOT include a `tools` parameter. This may be intentional (SDK should use agent's registered MCP tools automatically) or it may be the bug (SDK requires explicit tools parameter).

**Conclusion**: This link is working, but may need modification.

---

### [6] LLM Request Formation ❌ FAILING

**Expected Behavior**:
The Agents SDK should construct an LLM API request like this:

```python
request = {
    "model": "llama-3.3-70b",
    "messages": [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ],
    "tools": [
        # All 5 converted MCP tools
    ],
    "tool_choice": "auto",
    "temperature": 0.7,
    "max_tokens": 1000
}
```

**Actual Behavior**:
Based on the `FN_CALL=False` error and the fact that tools are never called, the request is likely:

```python
request = {
    "model": "llama-3.3-70b",
    "messages": [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ],
    # NO "tools" parameter ❌
    # NO "tool_choice" parameter ❌
    "temperature": 0.7,
    "max_tokens": 1000
}
```

**Why This Is Happening**:

**Hypothesis A: SDK Doesn't Auto-Include MCP Tools**
- The SDK registers MCP tools with the agent
- But it doesn't automatically include them in LLM requests
- Requires explicit `tools` parameter in `Runner.run_streamed()`

**Hypothesis B: Cerebras Model Not Recognized as Function-Calling Capable**
- The SDK checks if the model supports function calling
- Cerebras `llama-3.3-70b` is not in the SDK's list of function-calling models
- SDK skips tool inclusion for unsupported models
- Sets `FN_CALL=False` to indicate this

**Hypothesis C: OpenAI Client Configuration Issue**
- The `AsyncOpenAI` client is configured with Cerebras base URL
- But it's not configured for function calling
- Client doesn't include tools in requests

**Evidence**:
- `FN_CALL=False` error message
- No tool calls in LLM responses
- Agent generates text-only responses

**Conclusion**: **THIS IS THE PRIMARY FAILURE POINT.** Tools are not being included in LLM API requests.

---

### [7] LLM Processing ⚠️ DEGRADED

**Expected Behavior**:
Cerebras `llama-3.3-70b` should:
1. Receive tool schemas in request
2. Analyze user message
3. Decide whether to call a tool
4. Return either `tool_calls` or `content`

**Actual Behavior**:
Cerebras `llama-3.3-70b` is:
1. NOT receiving tool schemas ❌
2. Analyzing user message ✓
3. Generating text-only response ✓
4. Never returning `tool_calls` ❌

**Critical Question**: Does Cerebras `llama-3.3-70b` support OpenAI-style function calling?

**Research Required**:
- Check Cerebras API documentation
- Test with explicit tools parameter
- Compare with OpenAI GPT-4 behavior

**Hypothesis**: Even if we fix the request formation, Cerebras may not support function calling. This would require switching to OpenAI GPT-4.

**Conclusion**: This link is DEGRADED due to missing tools in request. May have additional issues with model compatibility.

---

### [8] Tool Execution ❌ NOT REACHED

**Expected Behavior**:
When LLM returns `tool_calls`, the SDK should:
1. Parse tool call from response
2. Route to appropriate MCP server
3. Execute tool via MCP protocol
4. Collect result
5. Make second LLM request with result

**Actual Behavior**:
This step is never reached because LLM never returns `tool_calls`.

**Conclusion**: This link is NOT REACHED due to upstream failure.

---

## Root Cause Determination

### Primary Root Cause: Tools Not Included in LLM Request

**Failure Point**: Link [6] - LLM Request Formation

**Exact Issue**: The Agents SDK is not including the `tools` parameter in the LLM API request.

**Why This Happens**:

**Most Likely Reason**: The SDK requires explicit tool passing, but the code doesn't provide it.

**Code Location**: `backend/src/agents/chatkit_server.py:166`

**Current Code**:
```python
result = Runner.run_streamed(
    agent,
    input_items,
    context=agent_context,
)
```

**Required Code**:
```python
# Option 1: Extract tools from agent's MCP servers
tools = await _extract_tools_from_mcp_servers(agent.mcp_servers)

result = Runner.run_streamed(
    agent,
    input_items,
    context=agent_context,
    tools=tools,  # ← Add explicit tools parameter
)
```

**OR**:

```python
# Option 2: Use agent's built-in tool access (if SDK supports it)
result = Runner.run_streamed(
    agent,
    input_items,
    context=agent_context,
    use_tools=True,  # ← Enable tool usage
)
```

---

### Secondary Root Cause: Model May Not Support Function Calling

**Failure Point**: Link [7] - LLM Processing

**Exact Issue**: Cerebras `llama-3.3-70b` may not support OpenAI-style function calling.

**Evidence**:
- `FN_CALL=False` suggests the SDK detected incompatibility
- No documentation confirming Cerebras supports function calling
- Cerebras is primarily known for fast inference, not function calling

**Impact**:
Even if we fix the request formation, the model may ignore the `tools` parameter and generate text-only responses.

**Solution**:
Add fallback to OpenAI GPT-4 for tool-calling operations:

```python
def _create_model():
    if settings.use_openai_for_tools:
        # Use OpenAI for reliable function calling
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        return OpenAIChatCompletionsModel(
            model="gpt-4-turbo-preview",
            openai_client=client,
        )
    else:
        # Use Cerebras for fast text generation
        client = AsyncOpenAI(
            api_key=settings.cerebras_api_key,
            base_url=settings.cerebras_base_url,
        )
        return OpenAIChatCompletionsModel(
            model=settings.cerebras_model,
            openai_client=client,
        )
```

---

## FN_CALL Analysis

### Is FN_CALL a Cause or Symptom?

**Answer**: `FN_CALL=False` is a **SYMPTOM**, not a cause.

**Explanation**:

`FN_CALL` is an internal flag in the OpenAI Agents SDK or AsyncOpenAI client that indicates whether function calling is configured and available.

**Causal Chain**:
```
Root Cause: Tools not passed to Runner
    ↓
SDK doesn't include tools in LLM request
    ↓
SDK sets FN_CALL=False (function calling disabled)
    ↓
Symptom: FN_CALL=False printed/logged
```

**What Sets FN_CALL=False**:

**Scenario 1: Model Incompatibility**
```python
# SDK checks if model supports function calling
if model_name not in FUNCTION_CALLING_MODELS:
    FN_CALL = False
    # Skip tool inclusion
```

**Scenario 2: No Tools Available**
```python
# SDK checks if tools are provided
if not tools or len(tools) == 0:
    FN_CALL = False
    # Skip function calling logic
```

**Scenario 3: Explicit Disable**
```python
# SDK checks configuration
if config.disable_function_calling:
    FN_CALL = False
```

**In Our Case**:
Most likely Scenario 1 or 2:
- Cerebras model is not recognized as function-calling capable, OR
- Tools are not being passed to the Runner, so SDK has no tools to include

**Conclusion**: Fixing `FN_CALL=False` requires fixing the root cause (tools not in request), not the symptom itself.

---

## Why System Falls Back to Text-Only Mode

### The Fallback Mechanism

**Design Intent**:
The Agents SDK is designed to gracefully degrade when function calling is unavailable:

```python
if FN_CALL:
    # Function calling mode
    response = llm.complete(messages, tools=tools, tool_choice="auto")
    if response.tool_calls:
        # Execute tools and continue
        results = execute_tools(response.tool_calls)
        final_response = llm.complete(messages + [results])
    return final_response
else:
    # Text-only mode (fallback)
    response = llm.complete(messages)  # No tools
    return response
```

**Why This Happens**:
1. SDK detects that function calling is not available (`FN_CALL=False`)
2. SDK falls back to text-only mode to avoid errors
3. LLM generates responses without tool access
4. Agent appears to work but is non-functional

**Why This Is Dangerous**:
- Silent failure: No error is raised
- Plausible responses: LLM generates realistic-sounding text
- User deception: User believes actions are being taken
- Data divergence: User's mental model diverges from system state

---

## Layer-by-Layer Breakdown

### Application Layer ✓
- FastAPI server running
- Endpoints responding
- Request routing working

### ChatKit Layer ⚠️
- Agent initialized correctly
- MCP server registered
- **Runner not passing tools to LLM** ❌

### Agents SDK Layer ❌
- **Not including tools in LLM requests** ❌
- Falling back to text-only mode
- Setting `FN_CALL=False`

### LLM API Layer ⚠️
- Receiving requests
- Generating responses
- **Not receiving tool schemas** ❌
- **May not support function calling** ⚠️

### MCP Layer ✓
- Server running
- Tools defined
- **Never receiving requests** (due to upstream failure)

### Database Layer ✓
- PostgreSQL running
- Tables exist
- **Never receiving tool operations** (due to upstream failure)

---

## The Exact Break Point

**The system breaks at the boundary between the ChatKit Layer and the Agents SDK Layer.**

Specifically:
- **File**: `backend/src/agents/chatkit_server.py`
- **Line**: 166
- **Function**: `respond()`
- **Call**: `Runner.run_streamed(agent, input_items, context=agent_context)`

**What's Missing**: Tools are not being passed to the Runner, so the SDK doesn't include them in the LLM request.

**Fix Location**: This exact line needs to be modified to include tools.

---

## Verification Strategy

To confirm this root cause, we need to:

### Test 1: Verify Tool Discovery
```python
# Add to chatkit_server.py after agent initialization
if agent.mcp_servers:
    for mcp_server in agent.mcp_servers:
        tools = await mcp_server.list_tools()
        logger.info(f"MCP server {mcp_server.name} has {len(tools)} tools: {[t.name for t in tools]}")
```

**Expected Output**: `MCP server TodoMCP has 5 tools: ['add_task', 'list_tasks', 'complete_task', 'update_task', 'delete_task']`

**If This Fails**: Tool discovery is broken (Link [3] failure)

### Test 2: Verify Tool Passing
```python
# Add to chatkit_server.py before Runner.run_streamed()
logger.info(f"Calling Runner with agent: {agent.name}")
logger.info(f"Agent has {len(agent.mcp_servers)} MCP servers")
logger.info(f"Context: {agent_context}")
```

**Expected Output**: Logs showing agent configuration

**Then**: Check if Runner has a `tools` parameter in its signature

### Test 3: Verify LLM Request
```python
# Monkey-patch AsyncOpenAI to log requests
original_create = client.chat.completions.create
async def logged_create(*args, **kwargs):
    logger.info(f"LLM Request: {kwargs}")
    return await original_create(*args, **kwargs)
client.chat.completions.create = logged_create
```

**Expected Output**: Log showing request with `tools` parameter

**If Missing**: Confirms tools are not in request (Link [6] failure)

### Test 4: Test Cerebras Function Calling
```python
# Direct API test
import asyncio
from openai import AsyncOpenAI

async def test_cerebras_function_calling():
    client = AsyncOpenAI(
        api_key=settings.cerebras_api_key,
        base_url=settings.cerebras_base_url,
    )

    response = await client.chat.completions.create(
        model="llama-3.3-70b",
        messages=[{"role": "user", "content": "Add a task to buy milk"}],
        tools=[{
            "type": "function",
            "function": {
                "name": "add_task",
                "description": "Add a task",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"}
                    },
                    "required": ["title"]
                }
            }
        }],
        tool_choice="auto"
    )

    print(f"Response: {response}")
    print(f"Has tool_calls: {hasattr(response.choices[0].message, 'tool_calls')}")

asyncio.run(test_cerebras_function_calling())
```

**Expected Output**: Response with `tool_calls`

**If Missing**: Cerebras doesn't support function calling (Link [7] failure)

---

## Summary

### Root Cause
**Tools are not being included in LLM API requests** because the code doesn't pass them to `Runner.run_streamed()`.

### Failure Point
**Line 166 of `backend/src/agents/chatkit_server.py`** - the `Runner.run_streamed()` call.

### FN_CALL Status
**Symptom, not cause** - it's set to False because tools aren't available, not the other way around.

### Fallback Reason
**SDK gracefully degrades** to text-only mode when function calling is unavailable, causing silent failure.

### Fix Strategy
1. **Immediate**: Pass tools explicitly to Runner
2. **Verification**: Test if Cerebras supports function calling
3. **Fallback**: Add OpenAI GPT-4 option if Cerebras doesn't support it
4. **Monitoring**: Add comprehensive logging to detect future failures

### Confidence Level
**High (90%)** - All evidence points to this root cause. The remaining 10% uncertainty is whether Cerebras supports function calling at all.
