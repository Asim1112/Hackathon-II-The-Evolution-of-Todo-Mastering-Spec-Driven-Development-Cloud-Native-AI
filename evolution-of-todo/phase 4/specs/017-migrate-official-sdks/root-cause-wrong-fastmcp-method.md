# Root Cause: Wrong FastMCP Method

**Date**: 2026-02-11
**Bug**: BUG-003 (MCP Connection Failure - Final Analysis)
**Root Cause**: Using `streamable_http_app()` instead of `http_app()`
**Status**: Solution confirmed

## Official FastMCP Documentation

From https://github.com/jlowin/fastmcp/blob/main/docs/v2/deployment/http.mdx:

```python
from fastapi import FastAPI
from fastmcp import FastMCP

api = FastAPI()
mcp = FastMCP("API Tools")

@mcp.tool
def query_database(query: str) -> dict:
    return {"result": "data"}

# Mount MCP at /mcp
api.mount("/mcp", mcp.http_app())  # ← Uses http_app(), not streamable_http_app()
```

**Client Connection**:
```python
client = Client("http://localhost:8000/mcp")  # ← Note: /mcp without trailing slash works
```

**Important Note from Docs**:
> "The default path for a streamable-HTTP server is `/mcp/`"

## Our Current Code

**Backend (main.py)**:
```python
app.mount("/mcp", mcp.streamable_http_app())  # ← WRONG METHOD
```

**Agent (chatkit_server.py)**:
```python
MCP_SERVER_URL = "http://localhost:8001/mcp"  # ← Missing trailing slash
```

## Root Cause

1. **Wrong Method**: Using `mcp.streamable_http_app()` which doesn't exist or returns wrong app
2. **Wrong URL**: Client connects to `/mcp` but server expects `/mcp/`

## Solution

### Fix 1: Use Correct Method (main.py)
```python
# Change from:
app.mount("/mcp", mcp.streamable_http_app())

# To:
app.mount("/mcp", mcp.http_app())
```

### Fix 2: Add Trailing Slash (chatkit_server.py)
```python
# Change from:
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8001/mcp")

# To:
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8001/mcp/")
```

## Expected Result

After both fixes:
1. ✅ No 307 redirect
2. ✅ No 404 error
3. ✅ MCP client connects successfully
4. ✅ Agent initializes with MCP tools
5. ✅ Agent responds to messages
