# Bug Investigation: MCP Server Connection Failure

**Date**: 2026-02-11
**Bug ID**: BUG-003
**Severity**: Critical (P0) - Blocks agent functionality
**Status**: Investigating

## Symptom

**User Action**: Sent "hi" in ChatKit UI
**Expected Result**: Agent responds using MCP tools
**Actual Result**: Error "There was an error while generating the assistant's response"

## Backend Error Analysis

### Error Sequence
```
1. POST http://localhost:8001/mcp → 307 Temporary Redirect
2. POST http://localhost:8001/mcp/ → 404 Not Found
3. McpError: Timed out while waiting for response (5.0 seconds)
4. McpError: Session terminated
```

### Stack Trace
```python
File "chatkit_server.py", line 105, in respond
    agent = await get_agent()
File "chatkit_server.py", line 67, in get_agent
    await _mcp_server.__aenter__()
File "agents/mcp/server.py", line 249, in __aenter__
    await self.connect()
File "agents/mcp/server.py", line 320, in connect
    server_result = await session.initialize()
```

### Root Cause

**Agent tries to connect to MCP server at**: `http://localhost:8001/mcp`
**Result**: 307 redirect to `/mcp/` → 404 Not Found

**Issue**: MCP endpoint configuration mismatch between:
1. How we mounted the MCP server in FastAPI
2. What URL the Agent SDK expects

## Current Configuration

**Backend (main.py)**:
```python
app.router.routes.append(
    Mount("/mcp", app=mcp.streamable_http_app())
)
```

**Agent (chatkit_server.py)**:
```python
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8001/mcp")

_mcp_server = MCPServerStreamableHttp(
    name="TodoMCP",
    params={"url": MCP_SERVER_URL},
    cache_tools_list=True,
    max_retry_attempts=3,
)
```

## Spec Violation

**FR-003**: System MUST integrate all 5 existing MCP tools with OpenAI Agents SDK using MCPServerStreamableHttp pattern

**Current State**: Agent cannot connect to MCP server, tools unavailable

## Investigation Needed

Need to determine:
1. What is the correct endpoint structure for `streamable_http_app()`?
2. Does it expect requests at `/mcp` or a sub-path like `/mcp/sse`?
3. Is the mounting in main.py correct?
4. Should we use a different mounting method?

## Next Steps (SDD)

1. ⏳ Query context7 for MCP Streamable HTTP endpoint structure
2. → Identify correct endpoint configuration
3. → Document fix
4. → Implement fix
5. → Test agent connection
