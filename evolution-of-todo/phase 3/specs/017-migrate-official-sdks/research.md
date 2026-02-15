# Research: OpenAI Agents SDK & ChatKit SDK Patterns

**Feature**: Migrate to Official OpenAI SDKs for Phase III Compliance
**Date**: 2026-02-11
**Purpose**: Extract all relevant implementation patterns from knowledge base files

## Overview

This document consolidates all implementation patterns, code examples, and best practices extracted from:
- OpenAI-Agents-SDK-Knowledge.md (1,788 lines)
- Chatkit-SDK-Documentation.md (3,427 lines)

Total knowledge base analyzed: 5,215 lines

## OpenAI Agents SDK Patterns

### Pattern 1: Agent Initialization with MCP Integration

**Source**: OpenAI-Agents-SDK-Knowledge.md (lines 450-470)

**Pattern**:
```python
from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp

async with MCPServerStreamableHttp(
    name="TodoMCP",
    params={"url": "http://localhost:8001/mcp", "timeout": 10},
    cache_tools_list=True,  # RECOMMENDED: Cache tool definitions
    max_retry_attempts=3,
) as server:
    agent = Agent(
        name="TodoAssistant",
        instructions="Use MCP tools to manage tasks",
        model="llama-3.3-70b",
        mcp_servers=[server]  # NOT Agent.tools parameter
    )
```

**Key Points**:
- Use `MCPServerStreamableHttp` for HTTP-based MCP server connection
- `cache_tools_list=True` caches tool definitions for performance
- `mcp_servers` parameter (NOT `tools` parameter)
- Async context manager handles lifecycle correctly
- HTTP URL format: "http://localhost:PORT/mcp"

**Alternatives Considered**:
- Direct tool registration via `Agent.tools`: Rejected (not MCP-compliant, requires rewriting tool definitions)
- Custom MCP client: Rejected (reinventing the wheel, not official pattern)

**Decision**: Use MCPServerStreamableHttp pattern exactly as documented

### Pattern 2: Runner Execution with Streaming

**Source**: OpenAI-Agents-SDK-Knowledge.md (lines 500-520)

**Pattern**:
```python
from agents import Runner

# Streaming execution
result = Runner.run_streamed(agent, input_items, context=agent_context)

# Process streaming events
async for event in result:
    if event.type == "text_delta":
        print(event.delta, end="")
    elif event.type == "tool_call":
        print(f"Calling tool: {event.tool_name}")
```

**Key Points**:
- `Runner.run_streamed()` for streaming responses
- Returns async iterator of events
- `context` parameter passes AgentContext for ChatKit integration
- Automatic tool calling loop (no manual iteration needed)

**Alternatives Considered**:
- `Runner.run()` (non-streaming): Rejected (no real-time feedback)
- Manual tool calling loop: Rejected (error-prone, not official pattern)

**Decision**: Use Runner.run_streamed() with AgentContext

### Pattern 3: Session Management (NOT NEEDED)

**Source**: OpenAI-Agents-SDK-Knowledge.md (lines 600-650)

**Pattern**:
```python
from agents import SQLiteSession

# Session for conversation history
session = SQLiteSession("user_123", "conversations.db")
result = Runner.run(agent, input, session=session)
```

**Key Points**:
- SQLiteSession stores conversation history
- **NOT NEEDED for ChatKit integration** (ChatKit Store handles persistence)
- Only use if NOT using ChatKit

**Decision**: Do NOT use SQLiteSession (ChatKit Store replaces it)

## ChatKit SDK Patterns

### Pattern 4: ChatKitServer Implementation

**Source**: Chatkit-SDK-Documentation.md (lines 2850-2900)

**Pattern**:
```python
from chatkit.server import ChatKitServer
from chatkit.agents import AgentContext, simple_to_agent_input, stream_agent_response
from agents import Agent, Runner

class TodoChatKitServer(ChatKitServer[dict]):
    async def respond(self, thread, input_user_message, context):
        # Load recent history (20 items, ascending order)
        items_page = await self.store.load_thread_items(
            thread.id, after=None, limit=20, order="asc", context=context
        )

        # Convert ChatKit items to agent input
        input_items = await simple_to_agent_input(items_page.data)

        # Create agent context
        agent_context = AgentContext(
            thread=thread,
            store=self.store,
            request_context=context
        )

        # Run agent with streaming
        result = Runner.run_streamed(assistant, input_items, context=agent_context)

        # Stream ChatKit events
        async for event in stream_agent_response(agent_context, result):
            yield event
```

**Key Points**:
- `respond()` method yields `ThreadStreamEvent` objects
- `simple_to_agent_input()` converts ChatKit items to agent format
- `stream_agent_response()` converts agent output to ChatKit events
- `AgentContext` bridges ChatKit and Agents SDK
- Load history with pagination (limit=20-50 recommended)

**Alternatives Considered**:
- Manual event conversion: Rejected (error-prone, helper functions provided)
- Load all history: Rejected (token limit issues, slow queries)

**Decision**: Use helper functions exactly as documented

### Pattern 5: Store Interface Implementation

**Source**: Chatkit-SDK-Documentation.md (lines 2680-2750)

**Pattern**:
```python
from chatkit.store import Store, NotFoundError
from chatkit.types import ThreadMetadata, ThreadItem, Page
from dataclasses import dataclass

@dataclass
class RequestContext:
    user_id: str

class PostgresStore(Store[RequestContext]):
    async def load_thread(self, thread_id: str, context: RequestContext) -> ThreadMetadata:
        with psycopg.connect(self._conninfo) as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT data FROM threads WHERE id = %s AND user_id = %s",
                (thread_id, context.user_id)
            )
            row = cur.fetchone()
            if not row:
                raise NotFoundError(f"Thread {thread_id} not found")
            return ThreadMetadata.model_validate(row[0])

    async def load_thread_items(
        self, thread_id: str, after: str | None, limit: int, order: str, context: RequestContext
    ) -> Page[ThreadItem]:
        # Cursor-based pagination
        query = """
            SELECT data FROM items
            WHERE thread_id = %s AND user_id = %s
            AND created_at > (SELECT created_at FROM items WHERE id = %s)
            ORDER BY created_at ASC
            LIMIT %s
        """
        # Execute query, deserialize items, return Page
        pass
```

**Key Points**:
- 13 methods required: load_thread, save_thread, load_threads, load_thread_items, add_thread_item, save_item, load_item, delete_thread, delete_thread_item, save_attachment, load_attachment, delete_attachment, generate_item_id
- Context parameter carries user_id for multi-tenancy
- Cursor-based pagination (NOT offset-based)
- Store ThreadItem as JSON in database
- Filter all queries by context.user_id

**Alternatives Considered**:
- Offset-based pagination: Rejected (performance issues at scale)
- Separate tables for ChatKit: Rejected (data duplication, sync complexity)

**Decision**: Implement Store as adapter over existing Conversation/Message models

### Pattern 6: FastAPI Integration

**Source**: Chatkit-SDK-Documentation.md (lines 2920-2935)

**Pattern**:
```python
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse, Response
from chatkit.server import StreamingResult

@app.post("/chatkit")
async def chatkit_endpoint(request: Request):
    result = await server.process(await request.body(), context={})

    if isinstance(result, StreamingResult):
        return StreamingResponse(result, media_type="text/event-stream")
    return Response(content=result.json, media_type="application/json")
```

**Key Points**:
- Single endpoint handles all ChatKit operations
- `server.process()` method handles request routing
- Returns `StreamingResult` (SSE) or `JSONResult`
- Context parameter passes request-specific data (user_id, etc.)

**Alternatives Considered**:
- Separate endpoints for each operation: Rejected (not ChatKit pattern)
- WebSocket instead of SSE: Rejected (ChatKit uses SSE)

**Decision**: Use single /chatkit endpoint with server.process()

### Pattern 7: Frontend ChatKit Component

**Source**: Chatkit-SDK-Documentation.md (lines 2940-2950)

**Pattern**:
```typescript
import { ChatKit } from '@openai/chatkit-react';
import '@openai/chatkit-react/styles.css';

export function ChatKitChat() {
  return (
    <ChatKit
      apiUrl="http://localhost:8000/chatkit"
      threadId="user_123"
      placeholder="Ask me about your tasks..."
    />
  );
}
```

**Key Points**:
- Import from `@openai/chatkit-react`
- Include styles: `@openai/chatkit-react/styles.css`
- Props: `apiUrl`, `threadId`, `placeholder`
- Automatic message rendering and streaming

**Alternatives Considered**:
- Custom chat UI: Rejected (not Phase III compliant)
- Other chat libraries: Rejected (must use official ChatKit)

**Decision**: Use ChatKit React component exactly as documented

## Serialization Strategy

### ThreadItem ↔ Message.content Mapping

**Strategy**: Store entire ThreadItem as JSON in Message.content field

**Serialization**:
```python
# ThreadItem → JSON string
thread_item = UserMessageItem(
    id="msg_123",
    thread_id="thread_456",
    created_at=datetime.now(),
    content=[{"text": "Hello"}]
)
json_content = thread_item.model_dump_json()

# Store in database
message = Message(
    id=thread_item.id,
    conversation_id=thread_item.thread_id,
    role="user",
    content=json_content,  # JSON string
    created_at=thread_item.created_at
)
```

**Deserialization**:
```python
# JSON string → ThreadItem
message = db.query(Message).filter_by(id="msg_123").first()
thread_item = UserMessageItem.model_validate_json(message.content)
```

**Key Points**:
- Preserves all ThreadItem fields (attachments, quoted_text, tool arguments)
- No schema changes required
- Type-safe with Pydantic validation
- Supports all ThreadItem types (UserMessageItem, AssistantMessageItem, ToolCallItem)

## Pagination Strategy

### Cursor-Based Pagination

**Pattern**: Use `after` parameter with item ID as cursor

**Implementation**:
```python
async def load_thread_items(
    self, thread_id: str, after: str | None, limit: int, order: str, context: RequestContext
) -> Page[ThreadItem]:
    if after:
        # Get created_at of cursor item
        cursor_query = "SELECT created_at FROM message WHERE id = %s"
        cursor_time = db.execute(cursor_query, (after,)).fetchone()[0]

        # Load items after cursor
        query = """
            SELECT * FROM message
            WHERE conversation_id = %s AND user_id = %s
            AND created_at > %s
            ORDER BY created_at ASC
            LIMIT %s
        """
        items = db.execute(query, (thread_id, context.user_id, cursor_time, limit))
    else:
        # Load from beginning
        query = """
            SELECT * FROM message
            WHERE conversation_id = %s AND user_id = %s
            ORDER BY created_at ASC
            LIMIT %s
        """
        items = db.execute(query, (thread_id, context.user_id, limit))

    # Deserialize and return Page
    thread_items = [deserialize_thread_item(item) for item in items]
    return Page(data=thread_items, has_more=len(items) == limit)
```

**Key Points**:
- Cursor = last item ID from previous page
- Query items with created_at > cursor_time
- Efficient at any page depth (no OFFSET)
- Recommended limit: 20-50 items

## Decision Summary

| Decision | Chosen Option | Rationale |
|----------|---------------|-----------|
| MCP Integration | MCPServerStreamableHttp | Official pattern, preserves MCP server, cache_tools_list=True |
| Store Implementation | Adapter pattern | Zero schema changes, clean separation |
| Agent Lifecycle | Singleton | Stateless agent, better performance |
| History Loading | Fixed limit (20 items) | Predictable tokens, fast queries |
| Thread ID Strategy | user_id as thread_id | Matches current behavior, simple |
| Error Handling | Let ChatKit SDK handle | Consistent format, less code |

## References

- OpenAI-Agents-SDK-Knowledge.md: Lines 450-470 (MCP integration), 500-520 (Runner), 600-650 (Session)
- Chatkit-SDK-Documentation.md: Lines 2850-2900 (ChatKitServer), 2680-2750 (Store), 2920-2935 (FastAPI), 2940-2950 (Frontend)

## Next Steps

Proceed to Phase 1: Design & Contracts
- Create data-model.md with entity mappings
- Create contracts/chatkit-endpoint.yaml
- Create quickstart.md with setup instructions
