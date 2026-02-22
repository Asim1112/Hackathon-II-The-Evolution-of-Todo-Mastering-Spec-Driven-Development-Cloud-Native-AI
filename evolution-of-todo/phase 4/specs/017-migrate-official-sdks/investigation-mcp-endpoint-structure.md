# Investigation: MCP Streamable HTTP Endpoint Structure

**Date**: 2026-02-11
**Bug**: BUG-003 (MCP Connection Failure - Continued)
**Status**: Investigating endpoint structure

## Problem

The fix using `app.mount()` did not resolve the issue. Still getting:
```
POST /mcp → 307 Temporary Redirect
POST /mcp/ → 404 Not Found
```

## Analysis

### Why 307 Redirect Happens

FastAPI/Starlette automatically redirects:
- `/mcp` → `/mcp/` (adds trailing slash)

This is standard behavior for mounted sub-applications.

### Why 404 After Redirect

The mounted `mcp.streamable_http_app()` returns 404 at `/mcp/`, which means:
- The MCP app doesn't have a route at its root path (`/`)
- The MCP app likely has routes at specific sub-paths

## Hypothesis

The `streamable_http_app()` from FastMCP probably exposes endpoints at specific paths like:
- `/sse` - for Server-Sent Events
- `/messages` - for message handling
- Or other MCP protocol-specific paths

**Not at the root** (`/`).

## Investigation Needed

Need to determine the actual endpoint structure of FastMCP's streamable_http_app().

### Option 1: Check FastMCP Source/Docs

Look at FastMCP library to see what routes `streamable_http_app()` defines.

### Option 2: Test Different URLs

Try connecting the MCP client to:
- `http://localhost:8001/mcp/sse`
- `http://localhost:8001/mcp/messages`
- Other potential paths

### Option 3: Inspect the Mounted App

Add logging to see what routes the MCP app actually has.

### Option 4: Use Different Transport

If Streamable HTTP is problematic, consider using SSE transport instead (if available).

## Next Steps (SDD)

1. Query context7 for FastMCP streamable HTTP endpoint structure
2. Or inspect the mcp object to see what routes it defines
3. Update client URL to match actual endpoint
4. Test connection
