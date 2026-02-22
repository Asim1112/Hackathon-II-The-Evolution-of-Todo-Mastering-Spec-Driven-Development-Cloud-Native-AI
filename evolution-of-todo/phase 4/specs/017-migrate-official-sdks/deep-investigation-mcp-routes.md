# Deep Investigation: MCP App Route Structure

**Date**: 2026-02-11
**Bug**: BUG-003 (MCP Connection Failure - Deep Analysis)
**Status**: Investigating actual routes

## Current Error (Clear and Direct)

```
POST /mcp/ HTTP/1.1" 404 Not Found
```

**Meaning**: The MCP client successfully connects to `/mcp/`, but the mounted app returns 404 because it has no route at `/`.

## Core Problem

The `mcp.streamable_http_app()` returns a Starlette app, but we don't know what routes it actually exposes.

**Hypothesis**: The app might have routes like:
- `/sse` for Server-Sent Events
- `/messages` for message handling
- Or other specific paths

**Not** at the root `/`.

## Investigation Plan

### Step 1: Inspect the MCP App

Add debug code to see what routes the MCP app actually has:

```python
# In main.py, after creating the mcp app
mcp_app = mcp.streamable_http_app()

# Inspect routes
print("MCP App type:", type(mcp_app))
print("MCP App routes:", getattr(mcp_app, 'routes', 'No routes attribute'))

# Then mount
app.mount("/mcp", mcp_app)
```

### Step 2: Alternative - Don't Use HTTP Transport

Since the MCP server and Agent are in the same Python process, we might not need HTTP transport at all.

**Option**: Use MCP tools directly without MCPServerStreamableHttp.

### Step 3: Check MCP SDK Documentation

Need to find official documentation for `mcp.server.fastmcp.FastMCP.streamable_http_app()` to understand its expected usage.

## Proposed Immediate Action

Let me add inspection code to see what the MCP app actually contains, then we can fix the routing properly.
