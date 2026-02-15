# MCP Migration Spec

**Feature**: 016-ai-chatbot
**Date**: 2026-02-11
**Status**: PENDING APPROVAL
**Purpose**: Define exactly which existing components will be removed, replaced, or modified during the Official MCP SDK migration.

---

## 1. Migration Summary

| Action | File Count | Description |
|--------|-----------|-------------|
| **REMOVE** | 7 files | Old custom registry and individual tool files |
| **CREATE** | 1 file | New MCP server with all tools |
| **MODIFY** | 3 files | Chat endpoint, main.py, mcp/__init__.py |
| **UNCHANGED** | 12+ files | Orchestrator, prompts, models, frontend, settings |

---

## 2. Files to REMOVE

These files contain the old custom MCP-compatible registry pattern that will be fully replaced by the Official MCP SDK.

### 2.1 `backend/src/mcp/server.py` (REMOVE ENTIRELY)

**What it contains**: Custom tool registry with `_tool_handlers` dict, `_tool_definitions` dict, and functions: `register_tool()`, `get_tool_handler()`, `get_all_tool_handlers()`, `get_tool_schema()`, `get_all_tool_schemas()`, `initialize_tools()`.

**Why remove**: Official MCP SDK (`FastMCP`) handles all tool registration, schema management, and handler lookup internally. This custom code is redundant.

**Lines**: ~104 lines

### 2.2 `backend/src/mcp/schemas.py` (REMOVE ENTIRELY)

**What it contains**: 5 manually-defined JSON Schema objects (`ADD_TASK_SCHEMA`, `LIST_TASKS_SCHEMA`, `COMPLETE_TASK_SCHEMA`, `DELETE_TASK_SCHEMA`, `UPDATE_TASK_SCHEMA`, `ALL_SCHEMAS`, `get_tool_schema()`).

**Why remove**: MCP SDK auto-generates JSON schemas from Python type hints and docstrings. Manual schemas become redundant and create a maintenance burden (two sources of truth).

**Lines**: ~247 lines

### 2.3 `backend/src/mcp/tools/add_task.py` (REMOVE ENTIRELY)

**What it contains**: `add_task_handler()` async function with database session management.

**Why remove**: Logic moves into `@mcp.tool()` decorated function in `mcp_server.py`.

**Lines**: ~120 lines

### 2.4 `backend/src/mcp/tools/list_tasks.py` (REMOVE ENTIRELY)

**What it contains**: `list_tasks_handler()` async function with status filtering.

**Why remove**: Logic moves into `@mcp.tool()` decorated function in `mcp_server.py`.

**Lines**: ~111 lines

### 2.5 `backend/src/mcp/tools/complete_task.py` (REMOVE ENTIRELY)

**What it contains**: `complete_task_handler()` async function.

**Why remove**: Logic moves into `@mcp.tool()` decorated function in `mcp_server.py`.

**Lines**: ~122 lines

### 2.6 `backend/src/mcp/tools/update_task.py` (REMOVE ENTIRELY)

**What it contains**: `update_task_handler()` async function with partial update support.

**Why remove**: Logic moves into `@mcp.tool()` decorated function in `mcp_server.py`.

**Lines**: ~160 lines

### 2.7 `backend/src/mcp/tools/delete_task.py` (REMOVE ENTIRELY)

**What it contains**: `delete_task_handler()` async function.

**Why remove**: Logic moves into `@mcp.tool()` decorated function in `mcp_server.py`.

**Lines**: ~111 lines

### Total Removed: ~975 lines across 7 files

---

## 3. Files to CREATE

### 3.1 `backend/src/mcp/mcp_server.py` (CREATE NEW)

**What it will contain**:
- `FastMCP` server instance
- 5 tool functions registered with `@mcp.tool()` decorators
- Same database logic as current tool handlers (migrated, not rewritten)
- Helper function to get tool handlers dict for orchestrator
- Helper function to get tool schemas for chat endpoint

**Estimated lines**: ~350 lines (consolidates 5 files + registry into 1)

**Structure**:
```
mcp_server.py
├── Imports
├── FastMCP instance creation
├── @mcp.tool() add_task (migrated from tools/add_task.py)
├── @mcp.tool() list_tasks (migrated from tools/list_tasks.py)
├── @mcp.tool() complete_task (migrated from tools/complete_task.py)
├── @mcp.tool() update_task (migrated from tools/update_task.py)
├── @mcp.tool() delete_task (migrated from tools/delete_task.py)
├── get_mcp_tool_handlers() - returns {name: handler} dict
├── get_mcp_tool_schemas() - returns schemas from MCP server
└── MCP server export
```

---

## 4. Files to MODIFY

### 4.1 `backend/src/mcp/__init__.py` (MODIFY)

**Current exports**: Imports from `server.py` and `schemas.py` (both being removed)

**New exports**: Import from `mcp_server.py` instead

**Changes**:
- Remove all imports from `.server` and `.schemas`
- Add imports from `.mcp_server`: `mcp` instance, `get_mcp_tool_handlers`, `get_mcp_tool_schemas`

### 4.2 `backend/src/api/routes/chat.py` (MODIFY)

**Current imports**:
```python
from src.mcp.schemas import ALL_SCHEMAS
from src.mcp.server import get_all_tool_handlers
```

**New imports**:
```python
from src.mcp.mcp_server import get_mcp_tool_schemas, get_mcp_tool_handlers
```

**Changes to chat endpoint**:
- Replace `ALL_SCHEMAS` with `get_mcp_tool_schemas()` call
- Replace `get_all_tool_handlers()` with `get_mcp_tool_handlers()` call
- `_convert_mcp_schemas_to_agent_tools()` stays (still needed for Groq format + user_id stripping)
- Tool execution flow stays the same

### 4.3 `backend/src/api/main.py` (MODIFY)

**Current startup**:
```python
from src.mcp.server import initialize_tools

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    initialize_tools()
```

**New startup**:
```python
from starlette.routing import Mount
from src.mcp.mcp_server import mcp

# Mount MCP server for external access
app.router.routes.append(
    Mount("/mcp", app=mcp.streamable_http_app())
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    # No initialize_tools() needed - MCP tools registered via decorators
```

---

## 5. Files to REMOVE (Directory Cleanup)

### 5.1 `backend/src/mcp/tools/` (REMOVE DIRECTORY)

After all individual tool files are removed, the entire `tools/` directory (including `__init__.py`) will be deleted.

**Files in directory**:
- `__init__.py` (~70 lines)
- `add_task.py` (~120 lines)
- `list_tasks.py` (~111 lines)
- `complete_task.py` (~122 lines)
- `update_task.py` (~160 lines)
- `delete_task.py` (~111 lines)

---

## 6. Files UNCHANGED

| File | Why Unchanged |
|---|---|
| `backend/src/agents/orchestrator.py` | Tool execution interface stays the same (receives handlers dict + tool_calls) |
| `backend/src/agents/prompts.py` | System prompt unrelated to tool registry |
| `backend/src/models/task.py` | Database model unchanged |
| `backend/src/models/conversation.py` | Database model unchanged |
| `backend/src/models/message.py` | Database model unchanged |
| `backend/src/database/session.py` | Session factory unchanged |
| `backend/src/services/conversation_service.py` | Conversation logic unchanged |
| `backend/src/config/settings.py` | Groq config unchanged |
| `backend/src/auth/dependencies.py` | Auth unchanged |
| `frontend/**` | No API contract changes |
| `backend/requirements.txt` | `mcp` package already installed |
| `backend/.env` | No new environment variables needed |

---

## 7. Migration Order (Sequential)

To prevent breaking the system at any point:

1. **CREATE** `mcp_server.py` with all 5 tools (new file, nothing breaks)
2. **MODIFY** `chat.py` to import from new file (switch data source)
3. **MODIFY** `main.py` to mount MCP server and remove `initialize_tools()` call
4. **MODIFY** `__init__.py` to update exports
5. **VERIFY** all chatbot operations still work
6. **REMOVE** `server.py` (old registry)
7. **REMOVE** `schemas.py` (old manual schemas)
8. **REMOVE** `tools/` directory (old individual handlers)
9. **FINAL VERIFY** all chatbot operations still work

---

## 8. Rollback Plan

If migration fails:
1. Restore removed files from the spec (logic is documented)
2. Revert import changes in `chat.py` and `main.py`
3. Delete `mcp_server.py`

**Risk level**: LOW - all logic is being migrated (not rewritten). Same database queries, same validation, same error handling.

---

**STATUS: PENDING APPROVAL — No files will be removed or modified until this spec is approved.**
