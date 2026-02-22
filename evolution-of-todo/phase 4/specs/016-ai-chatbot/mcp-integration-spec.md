# MCP Integration Spec

**Feature**: 016-ai-chatbot
**Date**: 2026-02-11
**Status**: PENDING APPROVAL
**Purpose**: Define how the Official MCP Python SDK will be used to expose task operations as tools, replacing the current custom tool registry.

---

## 1. Objective

Replace the current custom MCP-compatible tool registry with the **Official MCP Python SDK** (`mcp` package v1.25.0+) to satisfy Phase 3 hackathon requirement:

> "Build MCP server with Official MCP SDK that exposes task operations as tools"

---

## 2. MCP SDK Usage

### 2.1 Package

- **Package**: `mcp` (already installed as v1.25.0 in requirements.txt)
- **Import**: `from mcp.server.fastmcp import FastMCP`
- **API Level**: FastMCP (high-level Pythonic API)

### 2.2 Why FastMCP (not low-level MCPServer)

- Simpler decorator-based tool registration
- Auto-generates JSON schemas from Python type hints and docstrings
- Built on top of MCPServer internally (same SDK)
- Less boilerplate, same compliance

---

## 3. MCP Server Definition

### 3.1 Server Instance

A single `FastMCP` server instance will be created to host all 5 task operation tools.

**File**: `backend/src/mcp/mcp_server.py` (NEW)

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("TodoMCP")
```

### 3.2 Tool Definitions

All 5 tools will be registered using `@mcp.tool()` decorators. Tool names, parameters, and return types are derived directly from Python function signatures and type hints.

| Tool Name | Parameters (after user_id injection) | Return Type | Description |
|-----------|--------------------------------------|-------------|-------------|
| `add_task` | `user_id: str, title: str, description: str = ""` | `dict` | Create a new task |
| `list_tasks` | `user_id: str, status: str = "all"` | `list[dict]` | List tasks with optional status filter |
| `complete_task` | `user_id: str, task_id: int` | `dict` | Mark a task as complete |
| `update_task` | `user_id: str, task_id: int, title: str = None, description: str = None` | `dict` | Update task title or description |
| `delete_task` | `user_id: str, task_id: int` | `dict` | Delete a task |

### 3.3 Tool Handler Pattern

Each tool handler will:
1. Use `@mcp.tool()` decorator for registration
2. Use Python type hints for automatic schema generation
3. Use docstrings for tool descriptions (shown to LLM)
4. Manage its own database session (same pattern as current handlers)
5. Return Python dicts/lists (MCP SDK handles serialization)

**Example**:
```python
@mcp.tool()
async def add_task(user_id: str, title: str, description: str = "") -> dict:
    """Create a new task for the user.

    Args:
        user_id: The unique identifier for the user
        title: The title of the task (1-200 characters)
        description: Optional detailed description (max 1000 characters)
    """
    # Same database logic as current add_task_handler
    session_gen = get_session()
    session = next(session_gen)
    try:
        # ... create task in database ...
        return {"task_id": str(task.id), "status": "created", "title": task.title}
    finally:
        try:
            next(session_gen)
        except StopIteration:
            pass
```

### 3.4 Transport & Mounting

The MCP server will be **mounted inside the existing FastAPI app** using Starlette's Mount pattern:

```python
# In backend/src/api/main.py
from starlette.routing import Mount
from src.mcp.mcp_server import mcp

app.router.routes.append(
    Mount("/mcp", app=mcp.streamable_http_app())
)
```

This exposes the MCP server at `http://localhost:8001/mcp` for:
- External MCP clients (Claude Desktop, other agents)
- Demonstrating hackathon compliance
- Future interoperability

### 3.5 Internal Tool Execution

For the chat endpoint's orchestrator, tools will be executed by:
1. Getting tool schemas from the MCP server instance
2. Converting schemas to OpenAI function calling format (for Groq API)
3. When Groq returns tool_calls, calling tool handlers directly from the MCP server's internal registry

**Why not MCP client for internal calls**: Avoids circular HTTP (same process calling itself). The MCP server IS the Official SDK — tools registered with it satisfy the requirement. External access via `/mcp` endpoint demonstrates full protocol support.

---

## 4. What the MCP Server Replaces

| Current Component | Replaced By | Rationale |
|---|---|---|
| `server.py` registry functions (`register_tool`, `get_tool_handler`, etc.) | `FastMCP` internal registry | Official SDK manages tool registration |
| `schemas.py` manual JSON schemas | Auto-generated from type hints | MCP SDK generates schemas from decorators |
| `tools/__init__.py` handler aggregation | `@mcp.tool()` decorators | Tools registered directly on server instance |
| Individual tool files (`add_task.py`, etc.) | Tool functions in `mcp_server.py` | Consolidated into single MCP server file |

---

## 5. What Stays Unchanged

| Component | Why |
|---|---|
| `orchestrator.py` (Groq API calls) | LLM interaction is separate from tool definition |
| `chat.py` (endpoint logic) | Request flow stays the same; only tool source changes |
| `prompts.py` (system prompt) | No impact from tool registry change |
| Database models (Task, Conversation, Message) | No schema changes |
| Frontend (ChatInterface, hooks, etc.) | No API contract changes |
| `settings.py` (Groq config) | LLM config unchanged |

---

## 6. Integration Points

### 6.1 Chat Endpoint (chat.py)

**Current flow**:
```
ALL_SCHEMAS → _convert_mcp_schemas_to_agent_tools() → agent_tools
get_all_tool_handlers() → tool_handlers dict
orchestrator.handle_tool_calls(tool_calls, tool_handlers, inject_args)
```

**New flow**:
```
mcp.list_tools() → extract schemas → _convert_mcp_schemas_to_agent_tools() → agent_tools
mcp server internal handlers → tool_handlers dict
orchestrator.handle_tool_calls(tool_calls, tool_handlers, inject_args)
```

### 6.2 User ID Injection

The existing user_id injection pattern stays identical:
- Strip user_id from schemas before sending to Groq
- Inject user_id when executing tool calls

### 6.3 Startup Initialization

**Current**: `initialize_tools()` in `main.py` startup event
**New**: MCP server tools are registered at import time via decorators (no explicit init needed). Mount in FastAPI startup.

---

## 7. Acceptance Criteria

- [ ] MCP server created using `from mcp.server.fastmcp import FastMCP`
- [ ] All 5 tools registered via `@mcp.tool()` decorator
- [ ] MCP server mounted in FastAPI at `/mcp` endpoint
- [ ] Tool schemas auto-generated from type hints (no manual JSON schemas)
- [ ] All chatbot operations work: create, list, complete, update, delete
- [ ] Existing user_id injection pattern preserved
- [ ] No breaking changes to frontend API contract
- [ ] Old custom registry code removed

---

## 8. Risks

| Risk | Mitigation |
|---|---|
| MCP SDK version incompatibility | Already installed v1.25.0; test before removing old code |
| Schema generation differs from current | Verify generated schemas match expected format |
| Database session handling in MCP context | Keep existing session generator pattern inside tool handlers |
| Groq tool calling compatibility | Keep schema sanitization (strip defaults, empty required arrays) |

---

**STATUS: PENDING APPROVAL — No code will be written until this spec is approved.**
