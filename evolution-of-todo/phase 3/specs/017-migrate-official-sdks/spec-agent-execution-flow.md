# Agent Execution Spec: Expected Behavior

**Date**: 2026-02-12
**Feature**: 017-migrate-official-sdks
**Document Type**: Execution Specification

## Purpose

Define the expected execution flow for the Todo AI Assistant agent when processing user requests through the ChatKit UI.

## Architecture Overview

```
User Input (ChatKit UI)
    ↓
ChatKit Frontend (React)
    ↓
POST /chatkit (FastAPI)
    ↓
TodoChatKitServer.respond()
    ↓
OpenAI Agents SDK (Runner.run_streamed)
    ↓
Agent (instructions + model + mcp_servers)
    ↓
MCPServerStreamableHttp (tool discovery + execution)
    ↓
MCP Server Tools (add_task, list_tasks, complete_task, update_task, delete_task)
    ↓
Database (SQLModel/SQLite)
```

## Expected Execution Flow

### Phase 1: Request Reception
1. User types message in ChatKit UI (e.g., "delete all my tasks")
2. Frontend sends POST to `/chatkit` with message payload
3. `chatkit_endpoint()` extracts `user_id` from headers
4. Creates `RequestContext(user_id=user_id)`
5. Calls `TodoChatKitServer.process()`

### Phase 2: Context Assembly
1. `TodoChatKitServer.respond()` is invoked
2. Loads recent conversation history (20 items, ascending order)
3. Converts history to agent input format via `simple_to_agent_input()`
4. Injects system message with user_id context
5. Creates `AgentContext` bridging ChatKit and Agents SDK

### Phase 3: Agent Invocation
1. `Runner.run_streamed(agent, input_items, context)` is called
2. Agent receives:
   - System prompt from `get_system_prompt()` (instructions)
   - User_id context message (system role)
   - Conversation history
   - Current user message
3. Agent has access to MCP tools via `mcp_servers=[_mcp_server]`

### Phase 4: Intent Understanding
**Expected behavior for "delete all my tasks":**

1. Agent parses intent: User wants to delete ALL tasks
2. Agent recognizes this requires multi-step execution:
   - Step 1: Call `list_tasks(user_id, status="all")` to get all task IDs
   - Step 2: For each task, call `delete_task(user_id, task_id)`
   - Step 3: Call `list_tasks` again to verify deletion (per system prompt verification mandate)
3. Agent formulates tool call plan

### Phase 5: Tool Discovery
1. Agent queries available tools from MCP server
2. MCP server returns tool schemas:
   ```json
   [
     {
       "name": "list_tasks",
       "description": "Retrieve tasks for the user with optional status filter",
       "input_schema": {
         "type": "object",
         "properties": {
           "user_id": {"type": "string"},
           "status": {"type": "string", "enum": ["all", "pending", "completed"]}
         },
         "required": ["user_id"]
       }
     },
     {
       "name": "delete_task",
       "description": "Permanently delete a task",
       "input_schema": {
         "type": "object",
         "properties": {
           "user_id": {"type": "string"},
           "task_id": {"type": "integer"}
         },
         "required": ["user_id", "task_id"]
       }
     }
   ]
   ```
3. Agent matches intent to available tools

### Phase 6: Tool Execution
1. Agent issues first tool call: `list_tasks(user_id="user123", status="all")`
2. MCP client sends request to MCP server at `/mcp`
3. MCP server executes tool handler
4. Returns result: `[{id: 1, title: "..."}, {id: 2, title: "..."}, ...]`
5. Agent receives result and plans next calls
6. Agent issues delete calls: `delete_task(user_id="user123", task_id=1)`, etc.
7. Agent issues verification call: `list_tasks(user_id="user123", status="all")`
8. Agent confirms deletion succeeded

### Phase 7: Response Generation
1. Agent generates natural language response:
   - "I've deleted all 12 of your tasks. Verified: Your task list is now empty."
2. Response is streamed back via `stream_agent_response()`
3. ChatKit events are yielded to frontend
4. User sees response in UI

## Tool Call Format

**Expected format from Agent to MCP:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "list_tasks",
    "arguments": {
      "user_id": "user123",
      "status": "all"
    }
  }
}
```

## Success Criteria

1. ✅ Agent correctly interprets user intent
2. ✅ Agent discovers available MCP tools
3. ✅ Agent issues tool calls with correct parameters (including user_id)
4. ✅ MCP server executes tools and returns results
5. ✅ Agent processes results and plans next steps
6. ✅ Agent follows verification mandate from system prompt
7. ✅ Agent generates accurate natural language response
8. ✅ Response streams back to user in real-time

## Multi-Step Operation Requirements

For operations requiring multiple tool calls (like "delete all tasks"):
1. Agent MUST call list_tasks first to discover task IDs
2. Agent MUST iterate through results and call delete_task for each
3. Agent MUST verify the operation by calling list_tasks again
4. Agent MUST report accurate counts (before/after)

## Error Handling

If any tool call fails:
1. Agent receives error from MCP server
2. Agent reports error to user in friendly language
3. Agent suggests alternatives or next steps
4. Partial operations are communicated clearly
