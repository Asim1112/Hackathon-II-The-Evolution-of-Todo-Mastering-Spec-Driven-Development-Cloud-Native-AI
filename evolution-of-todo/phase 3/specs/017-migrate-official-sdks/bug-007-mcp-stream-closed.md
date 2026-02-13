# BUG-007: MCP Client Stream Closed Prematurely

**Date**: 2026-02-12
**Status**: Root cause identified, fix ready

## Symptoms

- Chatbot shows "searching" (thinking) indefinitely, never responds
- User message: "hi"
- Backend error: `anyio.ClosedResourceError` in MCP client SSE handler

## Error Details

```
Error parsing SSE message
Traceback (most recent call last):
  File "mcp/client/streamable_http.py", line 229, in _handle_sse_event
    await read_stream_writer.send(session_message)
  File "anyio/streams/memory.py", line 249, in send
    self.send_nowait(item)
  File "anyio/streams/memory.py", line 218, in send_nowait
    raise ClosedResourceError
anyio.ClosedResourceError
```

## Root Cause

`MCPServerStreamableHttp` has a default `client_session_timeout_seconds=5` (only 5 seconds). When the LLM takes longer than 5 seconds to process and respond, the MCP client session times out and closes its internal stream. When the MCP server tries to send SSE events after this timeout, it hits the closed stream and raises `ClosedResourceError`.

**From `agents/mcp/server.py` line 314**:
```python
ClientSession(
    read,
    write,
    timedelta(seconds=self.client_session_timeout_seconds)  # Default: 5 seconds!
    if self.client_session_timeout_seconds
    else None,
    message_handler=self.message_handler,
)
```

## Fix

Increase timeout parameters in `chatkit_server.py`:

```python
_mcp_server = MCPServerStreamableHttp(
    name="TodoMCP",
    params={
        "url": MCP_SERVER_URL,
        "timeout": 60,  # HTTP request timeout
        "sse_read_timeout": 600,  # SSE read timeout (10 minutes)
    },
    client_session_timeout_seconds=120,  # Increase from 5 to 120 seconds
    cache_tools_list=True,
    max_retry_attempts=3,
)
```

This gives the LLM enough time to:
1. Receive the request
2. Call MCP tools
3. Process results
4. Generate response
5. Stream back to client
