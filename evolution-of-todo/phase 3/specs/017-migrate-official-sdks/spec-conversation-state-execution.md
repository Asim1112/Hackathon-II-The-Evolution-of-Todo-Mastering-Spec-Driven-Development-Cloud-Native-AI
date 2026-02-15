# Conversation State & Agent Execution Spec

**Date**: 2026-02-12
**Feature**: 017-migrate-official-sdks
**Document Type**: Architecture Specification
**Status**: Diagnostic Analysis

## Purpose

Define the expected conversation state management and agent execution flow to establish a baseline for identifying where the system is failing.

## Architecture: Expected Conversation Flow

### 1. Message Storage Layer

**Database Schema**:
```
Conversation
  - id: int (PK)
  - user_id: str
  - created_at: datetime
  - updated_at: datetime

Message
  - id: int (PK)
  - conversation_id: int (FK)
  - user_id: str
  - role: enum(USER, ASSISTANT)
  - content: text (JSON-serialized ThreadItem)
  - created_at: datetime
```

**Expected Behavior**:
- Each user message creates a new Message record with role=USER
- Each assistant response creates a new Message record with role=ASSISTANT
- Messages are APPEND-ONLY - never updated or overwritten
- Message.content stores full ChatKit ThreadItem as JSON

### 2. Conversation History Replay

**Location**: `TodoChatKitServer.respond()` lines 108-114

**Expected Flow**:
```python
# Load recent history (20 items, ascending order for agent context)
items_page = await self.store.load_thread_items(
    thread.id,
    after=None,
    limit=20,
    order="asc",
    context=context,
)
```

**Expected Result**:
- Returns last 20 messages in chronological order (oldest first)
- Each message is deserialized from JSON to ThreadItem
- User messages become UserMessageItem
- Assistant messages become AssistantMessageItem
- History provides context for the agent

### 3. Agent Input Construction

**Location**: `TodoChatKitServer.respond()` lines 116-135

**Expected Flow**:
```python
# Convert ChatKit items to agent input format
input_items = await simple_to_agent_input(items_page.data)

# Inject user context
user_context_message = {
    "role": "system",
    "content": "The current user's ID is: '{user_id}'..."
}
input_items = [user_context_message] + list(input_items)
```

**Expected Structure**:
```json
[
  {
    "role": "system",
    "content": "The current user's ID is: 'user-123'. You MUST use this exact user_id..."
  },
  {
    "role": "user",
    "content": [{"type": "input_text", "text": "Previous user message"}]
  },
  {
    "role": "assistant",
    "content": [{"type": "output_text", "text": "Previous assistant response"}]
  },
  {
    "role": "user",
    "content": [{"type": "input_text", "text": "Current user message"}]
  }
]
```

### 4. Agent Execution Loop

**Expected Flow**:

```
Runner.run_streamed(agent, input_items, context)
    ↓
Agent receives:
  - System prompt (instructions)
  - User context (user_id)
  - Conversation history
  - Current user message
    ↓
Agent analyzes intent
    ↓
Agent queries available tools from MCP server
    ↓
Agent decides: CHAT or TOOL_CALL
    ↓
IF TOOL_CALL:
  Agent issues tool call → MCP server executes → Returns result
  Agent receives result → Incorporates into response
  Agent may issue more tool calls (multi-step)
    ↓
Agent generates final response
    ↓
Response streams back as ChatKit events
```

**Critical Decision Point**: Agent must decide whether to:
- **CHAT MODE**: Generate text response directly (for greetings, questions about itself)
- **TOOL MODE**: Call MCP tools (for task operations)

**Expected Tool Call Format**:
```json
{
  "type": "function",
  "function": {
    "name": "list_tasks",
    "arguments": {
      "user_id": "user-123",
      "status": "all"
    }
  }
}
```

### 5. Tool Execution & Result Handling

**Expected Flow**:
```
Agent calls list_tasks(user_id="user-123", status="all")
    ↓
MCPServerStreamableHttp sends request to /mcp
    ↓
MCP server routes to @mcp.tool() handler
    ↓
Tool handler queries database
    ↓
Returns: [{"id": 1, "title": "...", "completed": false}, ...]
    ↓
Agent receives tool result
    ↓
Agent incorporates result into response generation
    ↓
Agent generates: "You have 12 tasks: [lists them]"
```

**Critical Requirement**: Tool results MUST be from actual database queries, never hallucinated.

### 6. Response Streaming & Message Creation

**Expected Flow**:
```
stream_agent_response(agent_context, result)
    ↓
Yields ThreadStreamEvent objects
    ↓
Events include:
  - message.created (new assistant message started)
  - message.delta (incremental text chunks)
  - message.completed (message finished)
  - tool_call.started
  - tool_call.completed
    ↓
ChatKit frontend receives SSE events
    ↓
Frontend appends new assistant message to UI
    ↓
Backend saves completed assistant message to database
```

**Critical Requirement**: Each response creates a NEW message, never updates an existing one.

### 7. Message ID & Thread ID Management

**Expected Behavior**:
- Each Message has a unique integer ID (database PK)
- Thread ID maps to Conversation ID
- ChatKit generates string IDs like "thread_xxx" or "message_xxx"
- Store adapter maps these to database integer IDs
- Message IDs are stable - once created, never reused

**Message Lifecycle**:
```
1. User types message in UI
2. Frontend sends to backend
3. Backend creates Message record (gets new ID)
4. Backend processes with agent
5. Agent generates response
6. Backend creates new Message record for response (gets new ID)
7. Frontend displays both messages with their unique IDs
```

## Invariants (Must Always Be True)

1. **Append-Only Messages**: Messages are never updated after creation
2. **Unique IDs**: Each message has a unique, stable ID
3. **Tool Results Are Real**: Any data about tasks MUST come from database via tools
4. **No Hallucinated Actions**: Agent never claims to perform actions without calling tools
5. **Conversation Ordering**: Messages maintain chronological order
6. **User Isolation**: All queries filtered by user_id

## Expected Behavior Examples

### Example 1: Greeting (Chat Mode)
```
User: "hello, how are you?"
Expected Agent Behavior:
  - Recognizes this as a greeting (no task operation)
  - Does NOT call any tools
  - Responds in chat mode: "Hello! I'm doing well, thank you..."
  - Does NOT mention tasks unless asked
```

### Example 2: Task Query (Tool Mode)
```
User: "show me my tasks"
Expected Agent Behavior:
  1. Recognizes this requires task data
  2. Calls list_tasks(user_id="user-123", status="all")
  3. Receives result: 12 tasks
  4. Responds: "You have 12 tasks: [lists them]"
  5. Count and data match database exactly
```

### Example 3: Task Deletion (Tool Mode with Verification)
```
User: "delete all my tasks"
Expected Agent Behavior:
  1. Calls list_tasks to get all task IDs
  2. Calls delete_task for each ID
  3. Calls list_tasks again to verify
  4. Responds: "I've deleted all 12 tasks. Verified: Your task list is now empty."
  5. Database actually has 0 tasks after this
```

### Example 4: Follow-up Question (Chat Mode)
```
User: "what is your name?"
Expected Agent Behavior:
  - Recognizes this as a question about itself
  - Does NOT call any tools
  - Responds: "I'm your Todo AI Assistant..."
  - Creates NEW message, does NOT overwrite previous message
```

## Failure Modes (What Should Never Happen)

❌ **Hallucinated State**: Agent mentions tasks without calling list_tasks
❌ **Wrong Counts**: Agent says "7 tasks" when database has 12
❌ **Fake Actions**: Agent claims to delete tasks without calling delete_task
❌ **Message Corruption**: New response overwrites previous message
❌ **Context Confusion**: Greeting triggers task output
❌ **Tool Bypass**: Agent generates task data from training data instead of tools

## Verification Points

To verify the system is working correctly:

1. ✅ Check backend logs for "MCP tools available to agent: [...]"
2. ✅ Check backend logs for tool call events when task operations requested
3. ✅ Verify database changes match agent claims
4. ✅ Verify each message has unique ID in UI
5. ✅ Verify new messages append, don't overwrite
6. ✅ Verify greetings don't trigger tool calls
7. ✅ Verify task queries DO trigger tool calls
