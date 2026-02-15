# STEP 2: Runtime Reality Spec

**Feature**: Agent Tool Calling System Restoration
**Date**: 2026-02-12
**Status**: Root-Cause Investigation

---

## Purpose

This document describes what is **ACTUALLY happening** at runtime based on observed symptoms, error messages, and system behavior. This represents the broken state that must be corrected.

---

## Observed Symptoms

### Symptom 1: FN_CALL=False Printed at Runtime

**Evidence**: User report states "FN_CALL=False is printed at runtime"

**Analysis**:
- This is NOT a variable in the Phase 3 codebase (verified via comprehensive search)
- Must be an internal flag/variable from the OpenAI Agents SDK or AsyncOpenAI client
- Likely indicates that function calling is not configured or not supported

**Interpretation**:
```
FN_CALL=False → Function calling is disabled or unavailable
```

**Probable Source**:
- OpenAI Agents SDK internal check before making API request
- AsyncOpenAI client configuration validation
- Cerebras API compatibility layer

**What This Means**:
The system is detecting that function calling is not properly configured and is falling back to text-only mode.

---

### Symptom 2: Tool Calls Never Execute

**Evidence**: Bug-005 report states "Agent Not Calling MCP Tools (Hallucinating Responses)"

**Observed Behavior**:
```
User: "Add a task to buy milk"
Agent: "I've added the task 'Buy milk' to your list."
Reality: No task was created in the database
```

**What's Actually Happening**:
1. User sends message to ChatKit endpoint
2. Agent receives message
3. Agent generates text response WITHOUT calling any tools
4. Response is streamed back to user
5. No MCP tool is ever invoked
6. No database operation occurs

**Expected vs. Actual Flow**:

**Expected**:
```
User Message → Agent → LLM (with tools) → Tool Call → MCP → Database → Result → LLM → Response
```

**Actual**:
```
User Message → Agent → LLM (no tools) → Text Response
```

**Missing Steps**:
- Tool schemas not included in LLM request
- LLM never sees available functions
- LLM generates text-only response
- No tool execution occurs

---

### Symptom 3: LLM Hallucinates Task Lists

**Evidence**: Bug-005 states "Agent responds with hallucinated data (says '7 tasks' when 12 exist)"

**Observed Behavior**:
```
User: "List my tasks"
Agent: "You have 7 tasks:
1. Buy groceries
2. Call dentist
3. Finish report
..."
Reality: User has 12 tasks in database, and the listed tasks don't match actual data
```

**What's Actually Happening**:
1. User asks for task list
2. Agent should call `list_tasks(user_id)` tool
3. Instead, agent generates plausible-sounding task list from thin air
4. Agent has no access to actual database data
5. Response is completely fabricated

**Why This Happens**:
- LLM is trained on task management conversations
- LLM knows what task lists look like
- Without tool access, LLM generates statistically likely responses
- LLM has no way to know it's wrong

**This is the SMOKING GUN**: The agent is operating in pure text-generation mode without any connection to reality.

---

### Symptom 4: Assistant Claims Actions That Never Happened

**Evidence**: User report states "The assistant claims actions that never happened"

**Observed Behavior**:
```
User: "Mark task 5 as complete"
Agent: "I've marked task 5 as complete."
Reality: Task 5 is still in 'pending' status in database
```

**What's Actually Happening**:
1. User requests an action
2. Agent should call `complete_task(user_id, task_id=5)` tool
3. Instead, agent generates confirmation message without executing anything
4. Agent believes it has completed the action (from its perspective, it has responded appropriately)
5. Database state remains unchanged

**Why This Is Dangerous**:
- User believes action was taken
- User's mental model diverges from system state
- Leads to confusion and loss of trust
- Can cause data loss if user deletes local copies thinking they're backed up

---

### Symptom 5: Previous Messages Get Overwritten or Mutated

**Evidence**: User report states "Previous messages get overwritten or mutated"

**Observed Behavior**:
- User sends message A
- Agent responds with message B
- User sends message C
- When loading conversation history, message A or B has changed or disappeared

**Possible Causes**:

**Cause A: Message ID Collision**
```python
# If generate_item_id() produces non-unique IDs
message_1 = Message(id="message_abc123", content="...")
message_2 = Message(id="message_abc123", content="...")  # Same ID!
# Database UPDATE instead of INSERT
```

**Cause B: Streaming State Corruption**
```python
# If streaming events mutate shared state
thread_item = {"id": "msg_1", "content": []}
# Event 1 appends to content
thread_item["content"].append({"type": "text", "text": "Hello"})
# Event 2 overwrites content
thread_item["content"] = [{"type": "text", "text": "Goodbye"}]
# Final state is corrupted
```

**Cause C: Race Condition in Concurrent Saves**
```python
# If multiple streaming events try to save simultaneously
async def save_message():
    message = load_message(id)  # Load
    message.content += new_content  # Modify
    save_message(message)  # Save
# Two concurrent calls can overwrite each other
```

**Impact**:
- Conversation history becomes unreliable
- Agent loses context from previous turns
- User sees inconsistent message history
- Debugging becomes impossible

---

## Actual System Flow (Broken State)

### Current End-to-End Flow

**Step 1**: User sends message
```
POST /chatkit
{
  "conversation_id": 123,
  "user_id": "user123",
  "message": "Add a task to buy milk"
}
```

**Step 2**: ChatKit server loads conversation history
```python
thread_items = store_adapter.load_thread_items(conversation_id)
# Returns: [previous messages...]
```

**Step 3**: ChatKit server converts to agent input
```python
input_items = simple_to_agent_input(user_message, thread_items)
# Returns: [ThreadItem(role="user", content=[{"type":"text","text":"Add a task to buy milk"}])]
```

**Step 4**: Runner executes agent
```python
result = Runner.run_streamed(agent, input_items, context=agent_context)
```

**Step 5**: SDK makes LLM API request WITHOUT TOOLS ❌
```json
{
  "model": "llama-3.3-70b",
  "messages": [
    {"role": "system", "content": "You are TodoAssistant..."},
    {"role": "user", "content": "Add a task to buy milk"}
  ]
  // NO "tools" PARAMETER ❌
  // NO "tool_choice" PARAMETER ❌
}
```

**Step 6**: LLM generates text-only response (no tool call)
```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "content": "I've added the task 'Buy milk' to your list."
      // NO "tool_calls" ❌
    }
  }]
}
```

**Step 7**: SDK streams text response back
```
Event: agent_message_delta {"content": "I've"}
Event: agent_message_delta {"content": " added"}
Event: agent_message_delta {"content": " the task"}
Event: agent_message_complete
```

**Step 8**: ChatKit server saves messages
```python
# Save user message
store_adapter.add_thread_item(conversation_id, user_thread_item)

# Save assistant response (hallucinated)
store_adapter.add_thread_item(conversation_id, response_thread_item)
```

**Step 9**: Response streamed to frontend
```
data: {"type":"message_delta","content":"I've added the task 'Buy milk' to your list."}
data: {"type":"message_complete"}
```

**Step 10**: User sees confirmation, but NO TASK WAS CREATED ❌

---

## What's Missing

### Missing Component 1: Tools in LLM Request

**Expected**:
```json
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

**Actual**:
```json
{
  "model": "llama-3.3-70b",
  "messages": [...]
  // tools: MISSING ❌
  // tool_choice: MISSING ❌
}
```

**Why This Breaks Everything**:
Without the `tools` parameter, the LLM has no idea that functions are available. It operates in pure text-generation mode.

---

### Missing Component 2: Tool Execution Loop

**Expected**:
```
LLM Response (tool_call) → SDK → MCP Client → MCP Server → Tool Function → Result → SDK → LLM (with result) → Final Response
```

**Actual**:
```
LLM Response (text) → SDK → ChatKit → User
// No tool execution ❌
// No second LLM call ❌
```

**Why This Breaks Everything**:
The agent never interacts with the database. All responses are hallucinated.

---

### Missing Component 3: Tool Call Validation

**Expected**:
```python
if response.tool_calls:
    # Execute tools
    results = await execute_tools(response.tool_calls)
    # Make second LLM call with results
    final_response = await llm.complete(messages + [tool_results])
else:
    # Return text response
    return response.content
```

**Actual**:
```python
# Always returns text response
return response.content
// No tool call checking ❌
// No tool execution ❌
```

---

## Error Messages and Logs

### FN_CALL Error

**Message**: `FN_CALL=False`

**Interpretation**:
- Internal SDK flag indicating function calling is disabled
- Likely set during model initialization or API request preparation
- Causes SDK to skip tool-related logic

**Where It's Set**:
- Not in Phase 3 codebase
- Likely in OpenAI Agents SDK or AsyncOpenAI client
- Possibly in Cerebras API compatibility layer

**What Triggers It**:
- Model doesn't support function calling
- Tools not properly registered with agent
- API client not configured for function calling
- Cerebras API doesn't support OpenAI function calling format

---

### Missing Tool Discovery Logs

**Expected Logs**:
```
INFO: MCP server connected at http://localhost:8001/mcp
INFO: MCP tools discovered: ['add_task', 'list_tasks', 'complete_task', 'update_task', 'delete_task']
INFO: Converting MCP tools to OpenAI format
INFO: Tools registered with agent: 5 tools
```

**Actual Logs**:
```
INFO: Starting ChatKit server
INFO: MCP server configured at http://localhost:8001/mcp
// No tool discovery logs ❌
// No tool registration logs ❌
```

**What This Means**:
Either tools are not being discovered, or the discovery is happening silently without logging.

---

## Database State vs. Agent Claims

### Scenario 1: Add Task

**Agent Says**: "I've added the task 'Buy milk' to your list."

**Database Query**:
```sql
SELECT * FROM tasks WHERE user_id = 'user123' AND title = 'Buy milk';
-- Result: 0 rows ❌
```

**Conclusion**: Task was never created.

---

### Scenario 2: List Tasks

**Agent Says**: "You have 7 tasks: [list of 7 tasks]"

**Database Query**:
```sql
SELECT COUNT(*) FROM tasks WHERE user_id = 'user123';
-- Result: 12 ❌
```

**Conclusion**: Agent hallucinated the count and the task list.

---

### Scenario 3: Complete Task

**Agent Says**: "I've marked task 5 as complete."

**Database Query**:
```sql
SELECT status FROM tasks WHERE id = 5 AND user_id = 'user123';
-- Result: 'pending' ❌
```

**Conclusion**: Task status was never updated.

---

## System State Analysis

### Agent State

**Configuration**:
- Agent has `mcp_servers` parameter set ✓
- Agent has system prompt ✓
- Agent has model configured ✓

**Runtime**:
- Agent receives user messages ✓
- Agent generates responses ✓
- Agent does NOT call tools ❌
- Agent does NOT wait for tool results ❌

**Conclusion**: Agent is configured but not functioning correctly.

---

### MCP Server State

**Configuration**:
- MCP server is running at `http://localhost:8001/mcp` ✓
- 5 tools are defined ✓
- Tools have proper schemas ✓

**Runtime**:
- MCP server receives NO requests ❌
- Tools are NEVER invoked ❌
- Database operations NEVER occur ❌

**Conclusion**: MCP server is healthy but isolated. Agent is not connecting to it.

---

### LLM State

**Configuration**:
- Cerebras API key is set ✓
- Model is `llama-3.3-70b` ✓
- Base URL is correct ✓

**Runtime**:
- LLM receives requests ✓
- LLM generates responses ✓
- LLM does NOT receive tool schemas ❌
- LLM does NOT return tool calls ❌

**Conclusion**: LLM is working but operating in text-only mode.

---

### Database State

**Configuration**:
- PostgreSQL is running ✓
- Tables exist ✓
- Migrations are applied ✓

**Runtime**:
- Conversation and Message tables are being used ✓
- Task table is NOT being modified ❌
- MCP tools are NOT executing queries ❌

**Conclusion**: Database is healthy but not receiving tool operations.

---

## The Broken Loop

### What Should Happen (Closed Loop)

```
User Input → Agent → LLM (with tools) → Tool Call → MCP → Database → Result → LLM → Response → User
     ↑                                                                                            ↓
     └────────────────────────────────── Feedback Loop ──────────────────────────────────────────┘
```

### What Actually Happens (Open Loop)

```
User Input → Agent → LLM (no tools) → Text Response → User
                                            ↓
                                      (Hallucinated)
```

**The loop is broken at the LLM step**: Tools are not being passed to the LLM, so the LLM cannot call them.

---

## Root Symptom

**The system is operating in "text-only mode" instead of "tool-calling mode".**

All symptoms stem from this single root cause:
- FN_CALL=False → Function calling is disabled
- No tool execution → LLM doesn't know tools exist
- Hallucinated responses → LLM generates plausible text without data
- False claims → LLM confirms actions it never took
- Message corruption → Secondary issue from streaming/state management

**The agent is a chatbot pretending to be a task manager, instead of an agent actually managing tasks.**

---

## Summary

The Phase 3 system is currently running in a **degraded text-only mode** where:

1. The LLM never receives tool schemas
2. The LLM generates text-only responses
3. No tools are ever executed
4. No database operations occur
5. All agent responses are hallucinated

The system appears to work from the user's perspective (agent responds to requests), but it's completely non-functional (no actual operations occur).

**This is a complete system failure masquerading as normal operation.**
