# Failure Analysis Spec: Tool Execution Not Triggered

**Date**: 2026-02-12
**Feature**: 017-migrate-official-sdks
**Document Type**: Failure Analysis

## Observed Behavior

**User Input**: "delete all my tasks"

**Expected Behavior**:
1. Agent calls `list_tasks(user_id, status="all")`
2. Agent calls `delete_task(user_id, task_id)` for each task
3. Agent calls `list_tasks` again to verify
4. Agent responds: "I've deleted all 12 tasks. Verified: Your task list is now empty."

**Actual Behavior**:
- Agent responded with a generic help message
- No tool calls were issued
- Agent behaved as if in "chat mode" rather than "action mode"

## Failure Hypothesis Tree

### Hypothesis 1: MCP Tools Not Discovered
**Symptoms**: Agent doesn't know tools exist
**Possible Causes**:
- MCP server connection established but tools not listed
- `cache_tools_list=True` cached an empty list from a failed earlier connection
- Tool discovery happens at connection time, but connection succeeded after tools were registered
- Agent SDK doesn't automatically query MCP server for tools

**Verification Needed**:
- Check backend logs for "MCP server connected" message
- Check if there's a "tools discovered" or "tools listed" log message
- Verify MCP server's tool registry is populated at connection time
- Check if Agent SDK requires explicit tool listing vs automatic discovery

### Hypothesis 2: Tool Schemas Not Exposed to LLM
**Symptoms**: Agent knows tools exist but doesn't use them
**Possible Causes**:
- Tools are discovered but not passed to the LLM in the correct format
- Cerebras API expects a different tool schema format than OpenAI
- The `model` parameter needs explicit `tools=` argument
- Runner.run_streamed doesn't automatically include MCP tools in the LLM context

**Verification Needed**:
- Check if OpenAIChatCompletionsModel needs explicit tools parameter
- Verify Cerebras API supports function calling / tool use
- Check Runner.run_streamed implementation for how it passes tools to the model

### Hypothesis 3: System Prompt Insufficient
**Symptoms**: Agent prefers chat responses over tool calls
**Possible Causes**:
- System prompt doesn't explicitly instruct to use tools for task operations
- System prompt is too verbose, LLM ignores tool-use instructions
- System prompt focuses on verification AFTER tool use, not WHEN to use tools
- LLM interprets "delete all my tasks" as a question rather than a command

**Verification Needed**:
- Review system prompt for explicit tool-use triggers
- Check if prompt says "ALWAYS use tools for task operations"
- Verify prompt doesn't have conflicting instructions

### Hypothesis 4: Model Doesn't Support Tool Calling
**Symptoms**: Model generates text responses instead of tool calls
**Possible Causes**:
- Cerebras llama-3.3-70b doesn't support function calling
- Model supports tools but requires specific prompt format
- Model needs explicit "tool_choice" parameter to force tool use
- OpenAI-compatible API doesn't mean tool-calling compatible

**Verification Needed**:
- Check Cerebras documentation for llama-3.3-70b tool calling support
- Verify if model needs special prompt format for tools
- Check if ModelSettings needs tool_choice parameter

### Hypothesis 5: Agent Configuration Missing Tools Parameter
**Symptoms**: Agent created but tools not wired to model
**Possible Causes**:
- Agent class needs explicit `tools=` parameter separate from `mcp_servers=`
- MCP servers provide tools but Agent doesn't automatically expose them to the model
- Agent.instructions is used but tools need to be in a different field
- Runner.run_streamed needs explicit tools parameter

**Verification Needed**:
- Check Agent class constructor signature for tools parameter
- Verify if mcp_servers automatically makes tools available to model
- Check Runner.run_streamed signature for tools parameter

## Most Likely Root Cause

Based on the architecture, the most likely issue is **Hypothesis 2 or 5**: The tools are discovered from the MCP server, but they're not being passed to the LLM in the format it expects.

**Reasoning**:
1. MCP connection is working (we fixed timeouts, agent responds)
2. Tools are registered in mcp_server.py with @mcp.tool() decorators
3. Agent has mcp_servers=[_mcp_server] parameter
4. BUT: The Agents SDK might not automatically pass MCP tools to the underlying LLM
5. The model might need explicit tools parameter in the API call

## Investigation Steps Required

### Step 1: Verify Tool Discovery
Add logging to `get_agent()` after agent creation:
```python
logger.info("Agent initialized with MCP server at %s", MCP_SERVER_URL)
# ADD THIS:
if _mcp_server:
    tools = await _mcp_server.list_tools()
    logger.info("MCP tools discovered: %s", [t.name for t in tools])
```

### Step 2: Check Model Tool Support
Verify Cerebras llama-3.3-70b supports function calling:
- Check Cerebras API documentation
- Test with a simple tool call example
- Verify API response format matches OpenAI's tool calling format

### Step 3: Inspect Agent SDK Tool Wiring
Check how Agent class exposes MCP tools to the model:
- Read Agent class source code
- Check if tools need to be explicitly passed to model
- Verify Runner.run_streamed includes tools in LLM context

### Step 4: Test Tool Schema Format
Log the actual tool schemas being sent to the LLM:
- Capture the API request to Cerebras
- Verify tools are in the request payload
- Check schema format matches Cerebras expectations

## Expected Findings

If tools are NOT in the LLM request payload, we need to:
1. Explicitly extract tools from MCP server
2. Pass them to the model in the correct format
3. Possibly modify Agent or Runner configuration

If tools ARE in the payload but model ignores them:
1. Check if Cerebras model supports function calling
2. Verify prompt format for tool use
3. Consider switching to a different model or API
