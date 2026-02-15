# STEP 1: Ground-Truth Architecture Spec

**Feature**: Agent Tool Calling System Restoration
**Date**: 2026-02-12
**Status**: Root-Cause Investigation

---

## Purpose

This document defines how the Phase 3 agent-based chat system is **supposed** to work according to its design intent and the capabilities of its constituent technologies.

---

## System Components

### 1. ChatKit (OpenAI Agents SDK)

**Role**: High-level agent orchestration framework

**Responsibilities**:
- Provides `Agent` class for defining AI assistants
- Manages conversation threading and message history
- Handles streaming responses via `Runner.run_streamed()`
- Converts between ChatKit message formats and LLM API formats
- Integrates with MCP servers for tool access

**Expected Behavior**:
- Agent receives user input as `ThreadItem` objects
- Agent processes input with access to registered MCP tools
- Agent decides when to call tools vs. respond with text
- Agent executes tool calls and incorporates results
- Agent streams response events back to client

**Key Classes**:
- `Agent` - Agent definition with instructions, model, and MCP servers
- `Runner` - Executes agent with streaming support
- `ThreadItem` - Message format for conversation history

---

### 2. Agent (TodoAssistant)

**Definition**: `backend/src/agents/chatkit_server.py:80-89`

**Configuration**:
```python
Agent(
    name="TodoAssistant",
    instructions=get_system_prompt(),
    model=OpenAIChatCompletionsModel(cerebras_client),
    mcp_servers=[TodoMCP],
    model_settings=ModelSettings(temperature=0.7, max_tokens=1000)
)
```

**Expected Behavior**:
1. Receives user message about tasks
2. Analyzes intent (add, list, complete, update, delete)
3. Calls appropriate MCP tool with extracted parameters
4. Receives tool result from MCP server
5. Formats result into natural language response
6. Streams response to user

**Tool Access**:
- Agent MUST have access to all 5 MCP tools
- Agent MUST call tools instead of hallucinating data
- Agent MUST wait for tool results before responding

---

### 3. MCP (Model Context Protocol)

**Role**: Standardized protocol for exposing tools to LLMs

**Server Implementation**: `backend/src/mcp/mcp_server.py`

**Transport**: FastMCP with Streamable HTTP
- Server URL: `http://localhost:8001/mcp`
- Protocol: SSE (Server-Sent Events) for streaming
- Format: JSON-RPC 2.0

**Tool Registry**:
1. `add_task(user_id: str, title: str, description: str)` → Task
2. `list_tasks(user_id: str, status: Optional[str])` → List[Task]
3. `complete_task(user_id: str, task_id: int)` → Task
4. `update_task(user_id: str, task_id: int, title: str, description: str)` → Task
5. `delete_task(user_id: str, task_id: int)` → Success message

**Expected Flow**:
```
Agent → MCP Client → HTTP Request → MCP Server → Tool Function → Database → Response
```

**Schema Generation**:
- FastMCP auto-generates JSON schemas from Python type hints
- Schemas include parameter names, types, descriptions, and required fields
- Schemas are exposed via `tools/list` endpoint

---

### 4. LLM (Cerebras llama-3.3-70b)

**API**: OpenAI-compatible endpoint at `https://api.cerebras.ai/v1`

**Model**: `llama-3.3-70b`

**Expected Capabilities**:
- Chat completions with system/user/assistant messages
- **Function calling** (OpenAI-compatible format)
- Streaming responses
- JSON mode (for structured outputs)

**Function Calling Protocol**:
1. API request includes `tools` array with function schemas
2. API request includes `tool_choice` parameter (auto/required/none)
3. LLM analyzes user message and decides whether to call a function
4. If calling function: LLM returns `tool_calls` in response
5. If not calling: LLM returns text `content` in response

**Expected Request Format**:
```json
{
  "model": "llama-3.3-70b",
  "messages": [...],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "add_task",
        "description": "Add a new task",
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
  ],
  "tool_choice": "auto"
}
```

**Expected Response Format (Tool Call)**:
```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "content": null,
      "tool_calls": [{
        "id": "call_abc123",
        "type": "function",
        "function": {
          "name": "add_task",
          "arguments": "{\"user_id\":\"user123\",\"title\":\"Buy milk\",\"description\":\"Get 2% milk\"}"
        }
      }]
    }
  }]
}
```

---

### 5. Tool Registry (Agents SDK Internal)

**Role**: Converts MCP tools to OpenAI function calling format

**Expected Behavior**:
1. Agent initialization registers MCP server via `mcp_servers` parameter
2. SDK connects to MCP server and calls `tools/list` endpoint
3. SDK converts MCP tool schemas to OpenAI function schemas
4. SDK stores converted schemas in agent's tool registry
5. When `Runner.run_streamed()` is called, SDK includes tools in LLM API request

**Conversion Process**:
```
MCP Schema → SDK Converter → OpenAI Function Schema
```

**Critical Requirement**: Tools MUST be included in every LLM API request where the agent might need to call them.

---

### 6. Database (PostgreSQL)

**Models**:
- `Conversation` - Conversation metadata (user_id, timestamps)
- `Message` - Individual messages (conversation_id, role, content, timestamp)
- `Task` - Todo items (user_id, title, description, status, timestamps)

**Expected Behavior**:
- Each conversation has a unique ID
- Messages are stored in order with unique IDs
- Message content is JSON-serialized `ThreadItem` objects
- Tasks are isolated by user_id
- All operations are transactional

**Store Adapter**: `backend/src/agents/store_adapter.py`
- `load_thread_items()` - Loads conversation history from database
- `add_thread_item()` - Saves new messages to database
- `generate_item_id()` - Generates unique message IDs

---

### 7. Conversation Memory

**Format**: List of `ThreadItem` objects

**ThreadItem Structure**:
```python
{
    "id": "message_abc123",
    "role": "user" | "assistant",
    "content": [
        {"type": "text", "text": "..."}
        # OR
        {"type": "tool_call", "tool_call_id": "...", "name": "...", "arguments": "..."}
        # OR
        {"type": "tool_result", "tool_call_id": "...", "content": "..."}
    ]
}
```

**Expected Flow**:
1. User sends message → Saved as USER ThreadItem
2. Agent calls tool → Saved as ASSISTANT ThreadItem with tool_call
3. Tool returns result → Saved as ASSISTANT ThreadItem with tool_result
4. Agent responds → Saved as ASSISTANT ThreadItem with text
5. Next request loads ALL ThreadItems for context

**Critical Invariants**:
- Message IDs MUST be unique and stable
- Message order MUST be preserved
- Tool calls and results MUST be paired correctly
- No messages should be overwritten or mutated after creation

---

## Expected End-to-End Flow

### Scenario: User adds a task

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

**Step 4**: Runner executes agent with tools
```python
result = Runner.run_streamed(agent, input_items, context=agent_context)
```

**Step 5**: SDK makes LLM API request WITH TOOLS
```json
{
  "model": "llama-3.3-70b",
  "messages": [
    {"role": "system", "content": "You are TodoAssistant..."},
    {"role": "user", "content": "Add a task to buy milk"}
  ],
  "tools": [
    {"type": "function", "function": {"name": "add_task", ...}},
    {"type": "function", "function": {"name": "list_tasks", ...}},
    ...
  ],
  "tool_choice": "auto"
}
```

**Step 6**: LLM decides to call tool
```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "tool_calls": [{
        "id": "call_abc123",
        "function": {
          "name": "add_task",
          "arguments": "{\"user_id\":\"user123\",\"title\":\"Buy milk\",\"description\":\"\"}"
        }
      }]
    }
  }]
}
```

**Step 7**: SDK executes tool via MCP
```
POST http://localhost:8001/mcp
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "add_task",
    "arguments": {"user_id": "user123", "title": "Buy milk", "description": ""}
  }
}
```

**Step 8**: MCP server executes tool function
```python
async def add_task(user_id: str, title: str, description: str) -> Task:
    task = Task(user_id=user_id, title=title, description=description, status="pending")
    session.add(task)
    session.commit()
    return task
```

**Step 9**: Tool result returned to SDK
```json
{
  "jsonrpc": "2.0",
  "result": {
    "id": 42,
    "user_id": "user123",
    "title": "Buy milk",
    "description": "",
    "status": "pending",
    "created_at": "2026-02-12T10:30:00Z"
  }
}
```

**Step 10**: SDK makes second LLM request with tool result
```json
{
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "Add a task to buy milk"},
    {"role": "assistant", "tool_calls": [...]},
    {"role": "tool", "tool_call_id": "call_abc123", "content": "{\"id\":42,...}"}
  ]
}
```

**Step 11**: LLM generates natural language response
```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "content": "I've added the task 'Buy milk' to your list."
    }
  }]
}
```

**Step 12**: SDK streams events back to ChatKit server
```
Event: agent_message_delta
Event: agent_message_delta
Event: agent_message_complete
```

**Step 13**: ChatKit server saves messages to database
```python
# Save user message
store_adapter.add_thread_item(conversation_id, user_thread_item)

# Save assistant tool call
store_adapter.add_thread_item(conversation_id, tool_call_thread_item)

# Save assistant response
store_adapter.add_thread_item(conversation_id, response_thread_item)
```

**Step 14**: ChatKit server streams response to frontend
```
data: {"type":"message_delta","content":"I've"}
data: {"type":"message_delta","content":" added"}
data: {"type":"message_complete"}
```

---

## Critical Success Criteria

For the system to work correctly, ALL of the following MUST be true:

1. **MCP Server Connectivity**
   - MCP server is running at `http://localhost:8001/mcp`
   - Agent can connect and list tools
   - Tools are successfully registered with agent

2. **Tool Schema Conversion**
   - MCP schemas are converted to OpenAI function format
   - All 5 tools are available in converted format
   - Schemas include correct parameter types and descriptions

3. **LLM API Request Formation**
   - Every API request includes `tools` array
   - Tools array contains all 5 function schemas
   - `tool_choice` is set to "auto" (or appropriate value)

4. **LLM Function Calling Support**
   - Cerebras llama-3.3-70b supports OpenAI function calling
   - Model correctly interprets tool schemas
   - Model returns `tool_calls` when appropriate

5. **Tool Execution**
   - SDK recognizes tool calls in LLM response
   - SDK routes tool calls to MCP server
   - MCP server executes tool functions
   - Tool results are returned to SDK

6. **Multi-Turn Conversation**
   - SDK makes second LLM request with tool results
   - LLM generates natural language response based on results
   - Response is streamed back to user

7. **State Persistence**
   - All messages are saved to database with unique IDs
   - Message order is preserved
   - Tool calls and results are correctly paired
   - No message corruption or overwriting

---

## Architecture Diagram

```
┌─────────────┐
│   Frontend  │
└──────┬──────┘
       │ HTTP POST /chatkit
       ▼
┌─────────────────────────────────────────┐
│      ChatKit Server (FastAPI)           │
│  ┌──────────────────────────────────┐  │
│  │  TodoChatKitServer                │  │
│  │  - Load conversation history      │  │
│  │  - Convert to agent input         │  │
│  │  - Run agent with Runner          │  │
│  │  - Stream response                │  │
│  │  - Save messages to DB            │  │
│  └───────────────────────────────────┘  │
└──────┬──────────────────────────────────┘
       │ Runner.run_streamed(agent, input)
       ▼
┌─────────────────────────────────────────┐
│   OpenAI Agents SDK (ChatKit)           │
│  ┌───────────────────────────────────┐  │
│  │  Agent Execution                  │  │
│  │  - Load MCP tools                 │  │
│  │  - Convert to OpenAI format       │  │
│  │  - Make LLM API request           │  │
│  │  - Execute tool calls via MCP     │  │
│  │  - Stream events back             │  │
│  └───────────────────────────────────┘  │
└──────┬────────────────────┬──────────────┘
       │                    │
       │ LLM API            │ MCP HTTP
       ▼                    ▼
┌──────────────┐    ┌──────────────────┐
│   Cerebras   │    │   MCP Server     │
│  llama-3.3   │    │   (FastMCP)      │
│              │    │  - add_task      │
│ WITH TOOLS   │    │  - list_tasks    │
│              │    │  - complete_task │
└──────────────┘    │  - update_task   │
                    │  - delete_task   │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   PostgreSQL     │
                    │  - conversations │
                    │  - messages      │
                    │  - tasks         │
                    └──────────────────┘
```

---

## Summary

The Phase 3 system is designed as a **tool-calling agent architecture** where:

1. The LLM receives function schemas in every request
2. The LLM decides when to call functions vs. respond with text
3. Functions are executed via MCP protocol
4. Results are fed back to the LLM for natural language generation
5. All interactions are persisted to maintain conversation state

**The system CANNOT work without proper tool calling configuration.** If tools are not passed to the LLM, the agent will hallucinate responses instead of executing real operations.
