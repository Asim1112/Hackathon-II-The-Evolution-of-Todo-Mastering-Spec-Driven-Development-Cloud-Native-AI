# Root Cause: MCP Session Manager Not Initialized (Task Group)

**Date**: 2026-02-12
**Bug**: BUG-003 continuation (MCP 500 Internal Server Error)
**Status**: Root cause identified, fix designed

## Error

```
RuntimeError: Task group is not initialized. Make sure to use run().
```

At `mcp/server/streamable_http_manager.py`, line 143, in `handle_request`.

## Root Cause

`streamable_http_app()` returns a Starlette app with a `lifespan` parameter:

```python
# In mcp/server/fastmcp/server.py, line 1038:
return Starlette(
    routes=routes,
    lifespan=lambda app: self.session_manager.run(),  # initializes task group
)
```

The `session_manager.run()` is an async context manager that:
1. Creates an `anyio.create_task_group()`
2. Stores it in `self._task_group`
3. Yields while the app is running
4. Cleans up on shutdown

**Problem**: When a sub-app is **mounted** in FastAPI via `app.mount()`, the sub-app's lifespan is **NOT automatically invoked**. This is documented Starlette/FastAPI behavior. So `session_manager.run()` never executes, and `_task_group` remains `None`.

## Fix

Replace `@app.on_event("startup")` with FastAPI's `lifespan` context manager that manually starts the MCP session manager:

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    async with mcp.session_manager.run():
        yield

app = FastAPI(title="Todo API", version="1.0.0", lifespan=lifespan)
```

This ensures `session_manager.run()` is called during FastAPI's startup and properly cleaned up on shutdown.
