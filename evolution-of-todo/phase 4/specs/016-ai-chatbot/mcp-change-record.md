# MCP Change Record

**Feature**: 016-ai-chatbot
**Date**: 2026-02-11
**Status**: PENDING APPROVAL
**Purpose**: Document what existed before, what MCP replaces, what was removed, and why.

---

## 1. What Existed Before

### 1.1 Architecture (Custom MCP-Compatible Pattern)

The project used a **custom tool registry pattern** that mimicked MCP schemas without using the Official MCP SDK server:

```
backend/src/mcp/
├── __init__.py          # Package exports
├── schemas.py           # Manual JSON Schema definitions (247 lines)
├── server.py            # Custom tool registry (104 lines)
└── tools/
    ├── __init__.py      # Handler aggregation (70 lines)
    ├── add_task.py      # Add task handler (120 lines)
    ├── list_tasks.py    # List tasks handler (111 lines)
    ├── complete_task.py # Complete task handler (122 lines)
    ├── update_task.py   # Update task handler (160 lines)
    └── delete_task.py   # Delete task handler (111 lines)
```

**Total**: 8 files, ~1,045 lines

### 1.2 How It Worked

**Tool Registration** (`server.py`):
```python
_tool_handlers = {}    # {name: handler_function}
_tool_definitions = {} # {name: schema_dict}

def register_tool(name, handler, schema):
    _tool_handlers[name] = handler
    _tool_definitions[name] = schema

def initialize_tools():
    # Called at FastAPI startup
    # Registers all 5 tools from handlers + schemas
```

**Schema Definition** (`schemas.py`):
```python
ADD_TASK_SCHEMA = {
    "name": "add_task",
    "description": "Create a new task for the user",
    "input_schema": {
        "type": "object",
        "properties": {
            "user_id": {"type": "string", ...},
            "title": {"type": "string", ...},
            "description": {"type": "string", ...}
        },
        "required": ["user_id", "title"]
    },
    "output_schema": {...},
    "errors": {...}
}
# Repeated for all 5 tools
ALL_SCHEMAS = [ADD_TASK_SCHEMA, LIST_TASKS_SCHEMA, ...]
```

**Tool Handler** (e.g., `tools/add_task.py`):
```python
async def add_task_handler(user_id: str, title: str, description: str = "") -> Dict:
    session_gen = get_session()
    session = next(session_gen)
    try:
        task = Task(title=title, owner_id=user_id, ...)
        session.add(task)
        session.commit()
        return {"task_id": str(task.id), "status": "created", ...}
    finally:
        try: next(session_gen)
        except StopIteration: pass
```

**Chat Integration** (`chat.py`):
```python
from src.mcp.schemas import ALL_SCHEMAS
from src.mcp.server import get_all_tool_handlers

agent_tools = _convert_mcp_schemas_to_agent_tools(ALL_SCHEMAS)
tool_handlers = get_all_tool_handlers()
```

### 1.3 Why It Was Built This Way

From `research.md` R2:
> "Use MCP-compatible tool patterns WITHOUT running a full MCP server. Define tool schemas manually following MCP JSON Schema format, implement tool handlers as async functions, and invoke them directly from the agent orchestrator."

**Original rationale**:
- FastAPI REST endpoints don't need MCP stdio/HTTP transport
- Direct function invocation is simpler than MCP protocol overhead
- Tool schemas remain compatible with MCP spec

### 1.4 Why It Must Change

**Hackathon Phase 3 Requirement**:
> "Build MCP server with Official MCP SDK that exposes task operations as tools"

The current implementation is **functionally equivalent** but **technically non-compliant** — it uses MCP-compatible schemas without the Official SDK.

---

## 2. What MCP Replaces

### 2.1 Replacement Mapping

| Before (Custom) | After (Official MCP SDK) | Change Type |
|---|---|---|
| `server.py` - Custom `_tool_handlers` dict | `FastMCP` internal tool registry | REPLACED |
| `server.py` - `register_tool()` function | `@mcp.tool()` decorator | REPLACED |
| `server.py` - `get_all_tool_handlers()` | `get_mcp_tool_handlers()` wrapper | REPLACED |
| `server.py` - `initialize_tools()` | Decorator-based (auto at import) | REMOVED |
| `schemas.py` - Manual JSON schemas | Auto-generated from type hints | REPLACED |
| `schemas.py` - `ALL_SCHEMAS` list | `get_mcp_tool_schemas()` wrapper | REPLACED |
| `tools/add_task.py` | `@mcp.tool() async def add_task()` | MIGRATED |
| `tools/list_tasks.py` | `@mcp.tool() async def list_tasks()` | MIGRATED |
| `tools/complete_task.py` | `@mcp.tool() async def complete_task()` | MIGRATED |
| `tools/update_task.py` | `@mcp.tool() async def update_task()` | MIGRATED |
| `tools/delete_task.py` | `@mcp.tool() async def delete_task()` | MIGRATED |
| `tools/__init__.py` | Not needed (tools on server instance) | REMOVED |

### 2.2 What Stays the Same

| Component | Status | Why |
|---|---|---|
| Tool business logic | PRESERVED | Same queries, validation, error handling |
| Database session pattern | PRESERVED | `get_session()` generator still used |
| User ID injection | PRESERVED | Same strip-from-schema + inject-at-execution pattern |
| Orchestrator tool calling | PRESERVED | Same `handle_tool_calls()` interface |
| Chat endpoint flow | PRESERVED | Same request cycle, different tool source |
| Groq API integration | PRESERVED | Independent of tool registry |
| Frontend | PRESERVED | No API contract changes |

---

## 3. What Was Removed

### 3.1 Removed Files (7 files, ~975 lines)

| File | Lines | Reason |
|---|---|---|
| `backend/src/mcp/server.py` | ~104 | Replaced by FastMCP internal registry |
| `backend/src/mcp/schemas.py` | ~247 | Replaced by auto-generated schemas from type hints |
| `backend/src/mcp/tools/__init__.py` | ~70 | Handler aggregation no longer needed |
| `backend/src/mcp/tools/add_task.py` | ~120 | Logic migrated to mcp_server.py |
| `backend/src/mcp/tools/list_tasks.py` | ~111 | Logic migrated to mcp_server.py |
| `backend/src/mcp/tools/complete_task.py` | ~122 | Logic migrated to mcp_server.py |
| `backend/src/mcp/tools/update_task.py` | ~160 | Logic migrated to mcp_server.py |
| `backend/src/mcp/tools/delete_task.py` | ~111 | Logic migrated to mcp_server.py |

### 3.2 Removed Directory

- `backend/src/mcp/tools/` (entire directory)

### 3.3 Removed Functions

| Function | File | Reason |
|---|---|---|
| `register_tool()` | server.py | Replaced by `@mcp.tool()` decorator |
| `get_tool_handler()` | server.py | Replaced by FastMCP internal lookup |
| `get_all_tool_handlers()` | server.py | Replaced by `get_mcp_tool_handlers()` |
| `get_tool_schema()` | server.py / schemas.py | Replaced by MCP auto-generated schemas |
| `get_all_tool_schemas()` | server.py | Replaced by `get_mcp_tool_schemas()` |
| `initialize_tools()` | server.py | Not needed (decorator registration) |
| `get_all_tool_handlers()` | tools/__init__.py | Not needed (tools on server instance) |
| `get_tool_metadata()` | tools/__init__.py | Not needed |

---

## 4. Why the Change Was Made

### 4.1 Primary Reason
**Hackathon compliance.** Phase 3 explicitly requires "Build MCP server with Official MCP SDK." The custom implementation was functionally equivalent but did not use the Official SDK.

### 4.2 Secondary Benefits
- **Reduced code**: ~975 lines removed, ~350 lines added (net reduction of ~625 lines)
- **Single source of truth**: Tool schemas generated from code (no manual JSON to maintain)
- **External access**: MCP server mounted at `/mcp` enables external MCP clients
- **Standards compliance**: Follows MCP protocol specification
- **Future interoperability**: Tools accessible via standard MCP protocol (not just internal)

### 4.3 Trade-offs Accepted
- **Dependency on MCP SDK**: Tied to `mcp` package API
- **Slightly different schema format**: Auto-generated schemas may differ from hand-crafted ones (mitigated by schema sanitization in chat.py)

---

## 5. Verification Checklist

After migration, all of the following must pass:

- [ ] Backend starts without errors
- [ ] MCP server accessible at `/mcp` endpoint
- [ ] Chatbot: "Create a task to buy groceries" → Task created
- [ ] Chatbot: "Show me all my tasks" → Tasks listed
- [ ] Chatbot: "Mark task X as complete" → Task completed
- [ ] Chatbot: "Update task X to new title" → Task updated
- [ ] Chatbot: "Delete task X" → Task deleted
- [ ] Dashboard: Tasks page loads correctly
- [ ] No old files remain (server.py, schemas.py, tools/ directory)
- [ ] No import errors referencing removed files

---

**STATUS: PENDING APPROVAL — No changes will be made until this record is approved.**
