# Root Cause Analysis: MCP Mount Order Breaks All Routes

**Date**: 2026-02-12
**Bug**: BUG-003 (MCP Connection Failure - Root Cause Found)
**Status**: Root cause identified, fix designed

## Investigation: MCP SDK Source Code Analysis

**Source file inspected**: `C:\Users\asimh\AppData\Local\Programs\Python\Python311\Lib\site-packages\mcp\server\fastmcp\server.py`

### Key Finding

`FastMCP.streamable_http_app()` returns a **complete Starlette application** with an internal route at the path specified by `streamable_http_path` (default: `"/mcp"`).

The returned Starlette app has:
- `Route("/mcp", endpoint=streamable_http_app)` - handles POST, GET, DELETE
- Optional auth routes (if configured)
- Optional custom routes

### Why Previous Fixes Failed

| Attempt | Code | Effective Endpoint | Why It Failed |
|---|---|---|---|
| 1 | `app.mount("/mcp", mcp_app)` | `/mcp/mcp` | Double prefix: FastAPI prefix `/mcp` + internal route `/mcp` |
| 2 | URL with trailing slash `/mcp/` | `/mcp/` | MCP app has no route at `/` (only at `/mcp`) |
| 3 | `mcp.http_app()` | N/A | Method doesn't exist in official SDK (confused with jlowin/fastmcp) |
| 4 | `app.mount("", mcp_app)` at line 35 | `/mcp` (correct!) | BUT Mount("") at line 35 catches ALL requests before `@app.get` decorators at lines 91-97 |

### Root Cause: Route Registration Order

In Starlette/FastAPI, `app.router.routes` is a list checked sequentially. The first match wins.

**Current order in `app.router.routes`**:
1. APIRoutes from `tasks.router` (via `include_router` at line 29)
2. APIRoutes from `chat.router` (via `include_router` at line 30)
3. APIRoutes from `chatkit.router` (via `include_router` at line 31)
4. **`Mount("", mcp_app)`** at line 35 -- catches EVERYTHING not matched above
5. `Route("/")` from `@app.get("/")` at line 91 -- NEVER REACHED
6. `Route("/health")` from `@app.get("/health")` at line 97 -- NEVER REACHED

Since `Mount("")` matches all paths (empty string prefix matches everything), requests to `/` and `/health` are forwarded to the MCP app, which returns 404 because it only has a route at `/mcp`.

### The Fix

Move `app.mount("", mcp.streamable_http_app())` to the **very end of the file**, after all `@app.get()` decorator routes.

**Fixed order in `app.router.routes`**:
1. APIRoutes from `tasks.router` -- matches `/api/v1/*`
2. APIRoutes from `chat.router` -- matches `/api/*`
3. APIRoutes from `chatkit.router` -- matches chatkit paths
4. `Route("/")` from `@app.get("/")` -- matches `/`
5. `Route("/health")` from `@app.get("/health")` -- matches `/health`
6. **`Mount("", mcp_app)`** -- catches remaining paths, including `/mcp`

**Request flow for `/mcp`**:
1. tasks router? No match
2. chat router? No match
3. chatkit router? No match
4. Route("/")? No match
5. Route("/health")? No match
6. Mount("") matches → MCP app → internal Route("/mcp") matches → MCP handler responds

### Client URL

The `MCPServerStreamableHttp` client URL should be `http://localhost:8001/mcp` (no trailing slash), matching the MCP app's internal route path exactly.
