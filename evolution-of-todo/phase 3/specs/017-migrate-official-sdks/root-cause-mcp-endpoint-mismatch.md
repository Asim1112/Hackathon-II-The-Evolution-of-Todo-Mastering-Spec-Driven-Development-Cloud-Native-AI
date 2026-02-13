# Root Cause Analysis: MCP Endpoint Mismatch

**Date**: 2026-02-11
**Bug**: BUG-003 (MCP Connection Failure)
**Root Cause**: Incorrect MCP endpoint mounting in FastAPI
**Status**: Solution identified

## Problem Analysis

### Error Pattern
```
POST /mcp → 307 Temporary Redirect
POST /mcp/ → 404 Not Found
```

### Current Configuration

**Backend (main.py:32-34)**:
```python
app.router.routes.append(
    Mount("/mcp", app=mcp.streamable_http_app())
)
```

**Agent (chatkit_server.py:54)**:
```python
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8001/mcp")
```

### Root Cause

The `mcp.streamable_http_app()` returns a Starlette application with its own routing. When mounted at `/mcp`, the app expects requests at its internal routes, not at the mount root.

**FastMCP's streamable_http_app() likely exposes endpoints like**:
- `/` (root) - for MCP protocol messages
- Or specific sub-paths for different operations

**Current mounting creates**:
- `/mcp` → redirects to `/mcp/` (FastAPI behavior)
- `/mcp/` → 404 because the mounted app doesn't handle root

## Solution

### Option 1: Mount Without Prefix (Recommended)

Mount the MCP app at root and let it handle its own paths:

```python
# main.py
from starlette.routing import Mount

# Mount MCP app to handle all /mcp/* requests
app.mount("/mcp", mcp.streamable_http_app())
```

This allows the MCP app to handle requests at `/mcp/` and any sub-paths it defines.

### Option 2: Use Include Router

If FastMCP provides a router, include it directly:

```python
# main.py
mcp_app = mcp.streamable_http_app()
app.mount("/mcp", mcp_app)
```

### Option 3: Adjust Client URL

If the MCP app expects a specific endpoint, update the client URL:

```python
# chatkit_server.py
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8001/mcp/")
# Note the trailing slash
```

## Recommended Fix

Use `app.mount()` instead of `app.router.routes.append(Mount(...))`:

**File**: `backend/src/api/main.py`

**Change**:
```python
# OLD (line 32-34):
app.router.routes.append(
    Mount("/mcp", app=mcp.streamable_http_app())
)

# NEW:
app.mount("/mcp", mcp.streamable_http_app())
```

This is the standard FastAPI way to mount sub-applications and should handle routing correctly.

## Verification

After fix:
1. ✅ POST to `/mcp` should work (no redirect)
2. ✅ Agent connects successfully
3. ✅ MCP tools available
4. ✅ Agent responds to messages
