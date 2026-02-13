# ChatKit Python SDK - Complete Implementation Guide

**Version**: Based on openai-chatkit Python SDK
**Documentation Source**: https://openai.github.io/chatkit-python
**Last Updated**: 2026-02-11
**Purpose**: Comprehensive reference for implementing ChatKit Python SDK in Phase III Todo AI Chatbot

---

## Table of Contents

### 1. Overview & Core Concepts
- 1.1 What is ChatKit Python SDK
- 1.2 Design Philosophy
- 1.3 Core Architecture
- 1.4 Key Features
- 1.5 Installation & Setup

### 2. ChatKitServer - Core Integration
- 2.1 ChatKitServer Class
- 2.2 Implementing the respond Method
- 2.3 Server Lifecycle & Context
- 2.4 FastAPI Integration
- 2.5 Request Processing Flow

### 3. Store Interface - Data Persistence
- 3.1 Store Abstract Interface
- 3.2 Store Methods Reference
  - load_thread
  - save_thread
  - load_threads
  - load_thread_items
  - add_thread_item
  - save_item
  - load_item
  - delete_thread
  - delete_thread_item
  - save_attachment
  - load_attachment
  - delete_attachment
- 3.3 InMemoryStore Implementation
- 3.4 PostgreSQL Store Implementation
- 3.5 Custom Store Implementation

### 4. Thread & Item Types
- 4.1 ThreadMetadata
- 4.2 ThreadItem Types
  - UserMessageItem
  - AssistantMessageItem
  - ToolCallItem
  - ClientToolCallItem
  - WidgetItem
  - HiddenContextItem
- 4.3 ThreadStreamEvent Types
  - ThreadItemDoneEvent
  - ThreadItemDeltaEvent
- 4.4 Page & Pagination

### 5. OpenAI Agents SDK Integration
- 5.1 AgentContext
- 5.2 simple_to_agent_input Helper
- 5.3 stream_agent_response Helper
- 5.4 ThreadItemConverter
- 5.5 Custom Conversion Logic
- 5.6 Complete Integration Example

### 6. Widget System
- 6.1 Widget Concepts
- 6.2 Widget Components Reference
  - Card
  - Text
  - Button
  - Row
  - Column
  - Form
  - Title
  - Image
- 6.3 Widget Styling & Properties
- 6.4 Interactive Widgets & Actions
- 6.5 Widget Templates
- 6.6 Streaming Widgets

### 7. Tool Integration
- 7.1 Server Tools
- 7.2 Client Tools
- 7.3 Tool Calling Patterns
- 7.4 Tool Execution Flow
- 7.5 StopAtTools Behavior

### 8. Action Handling
- 8.1 Action Types
- 8.2 Implementing action Method
- 8.3 Widget Actions
- 8.4 Form Submission Actions
- 8.5 Action Payload Structure

### 9. Complete Implementation Examples
- 9.1 Basic ChatKit Server
- 9.2 ChatKit with Agents SDK
- 9.3 Interactive Widgets Example
- 9.4 Custom Store Implementation
- 9.5 Tool Integration Example
- 9.6 Production-Ready Server

### 10. Phase III Migration Guide
- 10.1 Current Architecture Analysis
- 10.2 Migration Strategy
- 10.3 Step-by-Step Migration
- 10.4 Code Comparison
- 10.5 Testing & Verification

### 11. Best Practices
- 11.1 Store Implementation
- 11.2 Thread Management
- 11.3 Widget Design
- 11.4 Error Handling
- 11.5 Performance Optimization

### 12. API Reference Quick Lookup
- 12.1 Core Classes
- 12.2 Common Patterns
- 12.3 Type Signatures

---

## 1. Overview & Core Concepts

### 1.1 What is ChatKit Python SDK

ChatKit Python SDK is a batteries-included framework for building high-quality, AI-powered chat experiences with deep UI customization and built-in response streaming. It provides a type-safe Python API for handling chat operations, integrating seamlessly with the ChatKit JavaScript frontend library.

**Key Capabilities:**
- Server-side chat orchestration with streaming responses
- Rich UI components (widgets) for interactive experiences
- Seamless integration with OpenAI Agents SDK
- Flexible data persistence through Store interface
- Tool calling (server-side and client-side)
- Custom action handling for interactive widgets
- File attachment support
- Thread and conversation management

### 1.2 Design Philosophy

ChatKit follows a **server-driven UI** approach where the backend controls what gets displayed in the chat interface. The assistant can stream:
- Text messages
- Interactive widgets (cards, forms, buttons)
- Tool call results
- File attachments
- Custom UI components

This design enables:
- **Rich interactions** beyond plain text
- **Structured data collection** through forms
- **Dynamic UI updates** based on conversation state
- **Consistent UX** across different clients

### 1.3 Core Architecture

**Three Main Components:**

1. **ChatKitServer** - Your server implementation that defines response logic
2. **Store** - Data persistence layer for threads, messages, and attachments
3. **Widgets** - Structured UI elements streamed to the client

**Request Flow:**
```
Client Request → FastAPI Endpoint → ChatKitServer.process()
                                          ↓
                                    respond() method
                                          ↓
                                    Stream Events
                                          ↓
                                    Client (SSE/JSON)
```

### 1.4 Key Features

**Streaming Responses:**
- Server-Sent Events (SSE) for real-time updates
- Token-by-token streaming from LLMs
- Progressive widget rendering

**OpenAI Agents SDK Integration:**
- `AgentContext` for agent execution
- `stream_agent_response()` helper for event conversion
- `simple_to_agent_input()` for quick thread conversion
- `ThreadItemConverter` for custom conversion logic

**Widget System:**
- Pre-built components (Card, Button, Text, Form, etc.)
- Interactive actions and callbacks
- Widget templates from `.widget` files
- Custom styling and layouts

**Tool Integration:**
- Server tools (Python functions)
- Client tools (browser callbacks)
- Automatic tool call handling
- Tool result streaming

### 1.5 Installation & Setup

**Installation:**
```bash
pip install openai-chatkit
```

**Dependencies:**
- Python 3.10+
- FastAPI (for HTTP server)
- OpenAI Agents SDK (optional, for agent integration)
- Database driver (for production Store implementation)

**Basic Project Structure:**
```
project/
├── main.py              # FastAPI server
├── server.py            # ChatKitServer implementation
├── store.py             # Store implementation
├── widgets/             # Widget templates
└── requirements.txt
```

---

## 2. ChatKitServer - Core Integration

### 2.1 ChatKitServer Class

**Base Class Definition:**
```python
from chatkit.server import ChatKitServer
from chatkit.types import ThreadMetadata, UserMessageItem, ThreadStreamEvent
from collections.abc import AsyncIterator

class MyChatKitServer(ChatKitServer[ContextType]):
    """
    Custom ChatKit server implementation.

    Type parameter ContextType defines the request context type
    (e.g., dict, RequestContext, etc.)
    """

    def __init__(self, store: Store[ContextType]):
        super().__init__(store=store)

    async def respond(
        self,
        thread: ThreadMetadata,
        input_user_message: UserMessageItem | None,
        context: ContextType,
    ) -> AsyncIterator[ThreadStreamEvent]:
        """
        Generate assistant response for user message.

        Args:
            thread: Thread metadata (id, created_at, etc.)
            input_user_message: User's message (None for thread initialization)
            context: Request context (user_id, org_id, etc.)

        Yields:
            ThreadStreamEvent: Events to stream to client
        """
        # Your response logic here
        pass
```

**Key Points:**
- Generic type parameter `[ContextType]` for type-safe context
- `respond()` is the core method you implement
- Must yield `ThreadStreamEvent` objects
- Async iterator for streaming responses

### 2.2 Implementing the respond Method

**Basic Implementation (Hardcoded Response):**
```python
from chatkit.types import ThreadItemDoneEvent, AssistantMessageItem, AssistantMessageContent
from datetime import datetime

class MyChatKitServer(ChatKitServer[dict]):
    async def respond(
        self,
        thread: ThreadMetadata,
        input_user_message: UserMessageItem | None,
        context: dict,
    ) -> AsyncIterator[ThreadStreamEvent]:
        # Generate unique ID for the message
        msg_id = self.store.generate_item_id("message", thread, context)

        # Yield a complete assistant message
        yield ThreadItemDoneEvent(
            item=AssistantMessageItem(
                id=msg_id,
                thread_id=thread.id,
                created_at=datetime.now(),
                content=[AssistantMessageContent(text="Hello! How can I help you today?")],
            ),
        )
```

**With OpenAI Agents SDK:**
```python
from agents import Agent, Runner
from chatkit.agents import AgentContext, simple_to_agent_input, stream_agent_response

assistant = Agent(
    name="assistant",
    instructions="You are a helpful assistant.",
    model="gpt-4o-mini",
)

class MyChatKitServer(ChatKitServer[dict]):
    async def respond(
        self,
        thread: ThreadMetadata,
        input_user_message: UserMessageItem | None,
        context: dict,
    ) -> AsyncIterator[ThreadStreamEvent]:
        # Load recent thread history
        items_page = await self.store.load_thread_items(
            thread.id,
            after=None,
            limit=20,  # Tune based on model context budget
            order="asc",
            context=context,
        )

        # Convert ChatKit items to agent input format
        input_items = await simple_to_agent_input(items_page.data)

        # Create agent context for streaming operations
        agent_context = AgentContext(
            thread=thread,
            store=self.store,
            request_context=context
        )

        # Run agent and stream response as ChatKit events
        result = Runner.run_streamed(assistant, input_items, context=agent_context)

        async for event in stream_agent_response(agent_context, result):
            yield event
```

### 2.3 Server Lifecycle & Context

**Context Type:**
The generic type parameter defines what context is passed to all Store methods:

```python
# Simple dict context
class MyChatKitServer(ChatKitServer[dict]):
    pass

# Custom context with user info
from dataclasses import dataclass

@dataclass
class RequestContext:
    user_id: str
    org_id: str
    permissions: list[str]

class MyChatKitServer(ChatKitServer[RequestContext]):
    pass
```

**Store Access:**
```python
# Access store in respond method
async def respond(self, thread, input_user_message, context):
    # Load thread data
    thread_data = await self.store.load_thread(thread.id, context)

    # Load items
    items = await self.store.load_thread_items(
        thread.id, after=None, limit=50, order="asc", context=context
    )

    # Generate IDs
    msg_id = self.store.generate_item_id("message", thread, context)
```

### 2.4 FastAPI Integration

**Complete FastAPI Server:**
```python
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, Response
from chatkit.server import StreamingResult
from chatkit.store import InMemoryStore

app = FastAPI()

# Initialize server
server = MyChatKitServer(store=InMemoryStore())

@app.post("/chatkit")
async def chatkit_endpoint(request: Request):
    """
    Single endpoint handling all ChatKit operations.

    Accepts POST requests and responds with either:
    - JSON response (for non-streaming operations)
    - Server-Sent Events (SSE) for streaming responses
    """
    result = await server.process(await request.body(), context={})

    if isinstance(result, StreamingResult):
        return StreamingResponse(result, media_type="text/event-stream")
    return Response(content=result.json, media_type="application/json")

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**With Custom Context:**
```python
@app.post("/chatkit")
async def chatkit_endpoint(request: Request):
    # Extract user context from request
    user_id = request.headers.get("X-User-ID")
    org_id = request.headers.get("X-Org-ID")

    context = RequestContext(
        user_id=user_id,
        org_id=org_id,
        permissions=["read", "write"]
    )

    result = await server.process(await request.body(), context=context)

    if isinstance(result, StreamingResult):
        return StreamingResponse(result, media_type="text/event-stream")
    return Response(content=result.json, media_type="application/json")
```

### 2.5 Request Processing Flow

**ChatKitServer.process() Method:**
```python
# Called by your FastAPI endpoint
result = await server.process(request_body: bytes, context: ContextType)

# Returns either:
# - StreamingResult (for SSE streaming)
# - JSONResult (for direct JSON response)
```

**Internal Flow:**
1. Parse request body (thread_id, message, action, etc.)
2. Load or create thread
3. Save user message to store
4. Call `respond()` method
5. Stream events to client
6. Save assistant messages to store

**Event Types Streamed:**
- `ThreadItemDoneEvent` - Complete item (message, widget, tool call)
- `ThreadItemDeltaEvent` - Partial item (streaming text)
- `ThreadUpdatedEvent` - Thread metadata changed
- `ErrorEvent` - Error occurred

---

## 3. Store Interface - Data Persistence

### 3.1 Store Abstract Interface

The `Store` interface defines how ChatKit persists threads, messages, and attachments. You must implement this interface to provide data persistence for your ChatKit server.

**Base Interface:**
```python
from chatkit.store import Store
from chatkit.types import ThreadMetadata, ThreadItem, Attachment, Page

class MyStore(Store[ContextType]):
    """
    Custom store implementation.

    Type parameter ContextType must match your ChatKitServer context type.
    """
    pass
```

**Key Concepts:**
- Generic type parameter `[ContextType]` for type-safe context
- All methods receive `context` parameter for user isolation
- Async methods for database operations
- Pagination support through `Page` type
- Thread items stored as JSON for schema flexibility

### 3.2 Store Methods Reference

#### load_thread
```python
async def load_thread(
    self,
    thread_id: str,
    context: ContextType
) -> ThreadMetadata:
    """
    Load thread metadata by ID.

    Args:
        thread_id: Unique thread identifier
        context: Request context (user_id, org_id, etc.)

    Returns:
        ThreadMetadata: Thread metadata object

    Raises:
        NotFoundError: If thread doesn't exist or user lacks access
    """
```

#### save_thread
```python
async def save_thread(
    self,
    thread: ThreadMetadata,
    context: ContextType
) -> None:
    """
    Persist thread metadata.

    Args:
        thread: Thread metadata to save
        context: Request context

    Note:
        Should upsert (insert or update) the thread
    """
```

#### load_threads
```python
async def load_threads(
    self,
    limit: int,
    after: str | None,
    order: str,
    context: ContextType
) -> Page[ThreadMetadata]:
    """
    Load paginated list of threads.

    Args:
        limit: Maximum number of threads to return
        after: Cursor for pagination (thread_id)
        order: Sort order ("asc" or "desc")
        context: Request context

    Returns:
        Page[ThreadMetadata]: Paginated thread list
    """
```

#### load_thread_items
```python
async def load_thread_items(
    self,
    thread_id: str,
    after: str | None,
    limit: int,
    order: str,
    context: ContextType
) -> Page[ThreadItem]:
    """
    Load paginated thread items (messages, tool calls, widgets).

    Args:
        thread_id: Thread identifier
        after: Cursor for pagination (item_id)
        limit: Maximum number of items to return
        order: Sort order ("asc" or "desc" by created_at)
        context: Request context

    Returns:
        Page[ThreadItem]: Paginated item list

    Note:
        Tune limit based on model context budget (typically 20-50)
    """
```

#### add_thread_item
```python
async def add_thread_item(
    self,
    thread_id: str,
    item: ThreadItem,
    context: ContextType
) -> None:
    """
    Append new item to thread.

    Args:
        thread_id: Thread identifier
        item: Thread item to add
        context: Request context

    Note:
        Should append to end of thread (newest item)
    """
```

#### save_item
```python
async def save_item(
    self,
    thread_id: str,
    item: ThreadItem,
    context: ContextType
) -> None:
    """
    Upsert thread item by ID.

    Args:
        thread_id: Thread identifier
        item: Thread item to save
        context: Request context

    Note:
        Should update if item.id exists, otherwise insert
    """
```

#### load_item
```python
async def load_item(
    self,
    thread_id: str,
    item_id: str,
    context: ContextType
) -> ThreadItem:
    """
    Load specific thread item by ID.

    Args:
        thread_id: Thread identifier
        item_id: Item identifier
        context: Request context

    Returns:
        ThreadItem: The requested item

    Raises:
        NotFoundError: If item doesn't exist
    """
```

#### delete_thread
```python
async def delete_thread(
    self,
    thread_id: str,
    context: ContextType
) -> None:
    """
    Delete thread and all associated items.

    Args:
        thread_id: Thread identifier
        context: Request context

    Note:
        Should cascade delete all thread items
    """
```

#### delete_thread_item
```python
async def delete_thread_item(
    self,
    thread_id: str,
    item_id: str,
    context: ContextType
) -> None:
    """
    Delete specific thread item.

    Args:
        thread_id: Thread identifier
        item_id: Item identifier
        context: Request context
    """
```

#### save_attachment
```python
async def save_attachment(
    self,
    attachment: Attachment,
    context: ContextType
) -> None:
    """
    Persist attachment metadata.

    Args:
        attachment: Attachment object with metadata
        context: Request context

    Note:
        Stores metadata only, not file content
        File content typically stored in object storage (S3, etc.)
    """
```

#### load_attachment
```python
async def load_attachment(
    self,
    attachment_id: str,
    context: ContextType
) -> Attachment:
    """
    Load attachment metadata by ID.

    Args:
        attachment_id: Attachment identifier
        context: Request context

    Returns:
        Attachment: Attachment metadata

    Raises:
        NotFoundError: If attachment doesn't exist
    """
```

#### delete_attachment
```python
async def delete_attachment(
    self,
    attachment_id: str,
    context: ContextType
) -> None:
    """
    Delete attachment metadata.

    Args:
        attachment_id: Attachment identifier
        context: Request context

    Note:
        Should also delete file content from storage
    """
```

### 3.3 InMemoryStore Implementation

**Complete Implementation:**
```python
from collections import defaultdict
from chatkit.store import NotFoundError, Store
from chatkit.types import Attachment, Page, ThreadItem, ThreadMetadata

class InMemoryStore(Store[dict]):
    """
    Simple in-memory store for development/testing.

    WARNING: Data is lost on server restart.
    Use database-backed store for production.
    """

    def __init__(self):
        self.threads: dict[str, ThreadMetadata] = {}
        self.items: dict[str, list[ThreadItem]] = defaultdict(list)
        self.attachments: dict[str, Attachment] = {}

    async def load_thread(self, thread_id: str, context: dict) -> ThreadMetadata:
        if thread_id not in self.threads:
            raise NotFoundError(f"Thread {thread_id} not found")
        return self.threads[thread_id]

    async def save_thread(self, thread: ThreadMetadata, context: dict) -> None:
        self.threads[thread.id] = thread

    async def load_threads(
        self, limit: int, after: str | None, order: str, context: dict
    ) -> Page[ThreadMetadata]:
        threads = list(self.threads.values())
        return self._paginate(
            threads, after, limit, order,
            sort_key=lambda t: t.created_at,
            cursor_key=lambda t: t.id
        )

    async def load_thread_items(
        self, thread_id: str, after: str | None, limit: int, order: str, context: dict
    ) -> Page[ThreadItem]:
        items = self.items.get(thread_id, [])
        return self._paginate(
            items, after, limit, order,
            sort_key=lambda i: i.created_at,
            cursor_key=lambda i: i.id
        )

    async def add_thread_item(
        self, thread_id: str, item: ThreadItem, context: dict
    ) -> None:
        self.items[thread_id].append(item)

    async def save_item(
        self, thread_id: str, item: ThreadItem, context: dict
    ) -> None:
        items = self.items[thread_id]
        for idx, existing in enumerate(items):
            if existing.id == item.id:
                items[idx] = item
                return
        items.append(item)

    async def load_item(
        self, thread_id: str, item_id: str, context: dict
    ) -> ThreadItem:
        for item in self.items.get(thread_id, []):
            if item.id == item_id:
                return item
        raise NotFoundError(f"Item {item_id} not found in thread {thread_id}")

    async def delete_thread(self, thread_id: str, context: dict) -> None:
        self.threads.pop(thread_id, None)
        self.items.pop(thread_id, None)

    async def delete_thread_item(
        self, thread_id: str, item_id: str, context: dict
    ) -> None:
        self.items[thread_id] = [
            item for item in self.items.get(thread_id, []) if item.id != item_id
        ]

    async def save_attachment(
        self, attachment: Attachment, context: dict
    ) -> None:
        self.attachments[attachment.id] = attachment

    async def load_attachment(
        self, attachment_id: str, context: dict
    ) -> Attachment:
        if attachment_id not in self.attachments:
            raise NotFoundError(f"Attachment {attachment_id} not found")
        return self.attachments[attachment_id]

    async def delete_attachment(self, attachment_id: str, context: dict) -> None:
        self.attachments.pop(attachment_id, None)

    def _paginate(self, rows: list, after: str | None, limit: int, order: str, sort_key, cursor_key):
        """Helper for cursor-based pagination."""
        sorted_rows = sorted(rows, key=sort_key, reverse=order == "desc")
        start = 0
        if after:
            for idx, row in enumerate(sorted_rows):
                if cursor_key(row) == after:
                    start = idx + 1
                    break
        data = sorted_rows[start : start + limit]
        has_more = start + limit < len(sorted_rows)
        next_after = cursor_key(data[-1]) if has_more and data else None
        return Page(data=data, has_more=has_more, after=next_after)
```

### 3.4 PostgreSQL Store Implementation

**Schema Setup:**
```python
from chatkit.store import Store, NotFoundError
from chatkit.types import ThreadMetadata, ThreadItem, Page
import psycopg

class PostgresStore(Store[RequestContext]):
    def __init__(self, conninfo: str) -> None:
        self._conninfo = conninfo
        self._init_schema()

    def _init_schema(self) -> None:
        """Create tables if they don't exist."""
        with psycopg.connect(self._conninfo) as conn, conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS threads (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL,
                    data JSONB NOT NULL
                );
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id TEXT PRIMARY KEY,
                    thread_id TEXT NOT NULL
                        REFERENCES threads (id)
                        ON DELETE CASCADE,
                    user_id TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL,
                    data JSONB NOT NULL
                );
            """)

            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_items_thread_created
                ON items (thread_id, created_at);
            """)

            conn.commit()

    async def load_thread(
        self, thread_id: str, context: RequestContext
    ) -> ThreadMetadata:
        with psycopg.connect(self._conninfo) as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT data FROM threads WHERE id = %s AND user_id = %s",
                (thread_id, context.user_id),
            )
            row = cur.fetchone()
            if row is None:
                raise NotFoundError(f"Thread {thread_id} not found")
            return ThreadMetadata.model_validate(row[0])

    async def save_thread(
        self, thread: ThreadMetadata, context: RequestContext
    ) -> None:
        payload = thread.model_dump(mode="json")
        with psycopg.connect(self._conninfo) as conn, conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO threads (id, user_id, created_at, data)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET data = EXCLUDED.data
                """,
                (thread.id, context.user_id, thread.created_at, payload),
            )
            conn.commit()

    async def load_thread_items(
        self, thread_id: str, after: str | None, limit: int, order: str, context: RequestContext
    ) -> Page[ThreadItem]:
        with psycopg.connect(self._conninfo) as conn, conn.cursor() as cur:
            # Build query with pagination
            order_clause = "DESC" if order == "desc" else "ASC"

            if after:
                cur.execute(
                    f"""
                    SELECT data FROM items
                    WHERE thread_id = %s AND user_id = %s AND created_at > (
                        SELECT created_at FROM items WHERE id = %s
                    )
                    ORDER BY created_at {order_clause}
                    LIMIT %s
                    """,
                    (thread_id, context.user_id, after, limit + 1),
                )
            else:
                cur.execute(
                    f"""
                    SELECT data FROM items
                    WHERE thread_id = %s AND user_id = %s
                    ORDER BY created_at {order_clause}
                    LIMIT %s
                    """,
                    (thread_id, context.user_id, limit + 1),
                )

            rows = cur.fetchall()
            has_more = len(rows) > limit
            data = [ThreadItem.model_validate(row[0]) for row in rows[:limit]]
            next_after = data[-1].id if has_more and data else None

            return Page(data=data, has_more=has_more, after=next_after)

    # Implement remaining methods following the same pattern...
```

**Key Points:**
- Store thread items as JSONB for schema flexibility
- Use user_id for multi-tenancy isolation
- Add indexes on (thread_id, created_at) for performance
- Use ON CONFLICT for upsert operations
- Implement proper pagination with cursors

### 3.5 Custom Store Implementation

**Best Practices:**

1. **Serialize as JSON:**
```python
# Store thread items as JSON to avoid schema migrations
payload = item.model_dump(mode="json")
# Save payload to database

# Load and deserialize
item = ThreadItem.model_validate(json_data)
```

2. **User Isolation:**
```python
# Always filter by user_id from context
async def load_thread(self, thread_id: str, context: RequestContext):
    # Query: WHERE id = thread_id AND user_id = context.user_id
    pass
```

3. **Pagination:**
```python
# Use cursor-based pagination (not offset)
# Cursor = last item's ID or created_at timestamp
async def load_thread_items(self, thread_id, after, limit, order, context):
    if after:
        # Query: WHERE created_at > (SELECT created_at FROM items WHERE id = after)
        pass
```

4. **Error Handling:**
```python
from chatkit.store import NotFoundError

async def load_thread(self, thread_id, context):
    result = await db.query(...)
    if not result:
        raise NotFoundError(f"Thread {thread_id} not found")
    return result
```

---

## 4. Thread & Item Types

### 4.1 ThreadMetadata

**Structure:**
```python
from chatkit.types import ThreadMetadata
from datetime import datetime

thread = ThreadMetadata(
    id="thread_abc123",
    created_at=datetime.now(),
    # Additional metadata fields...
)
```

**Attributes:**
- `id` (str): Unique thread identifier
- `created_at` (datetime): Thread creation timestamp
- Additional custom fields can be added

### 4.2 ThreadItem Types

Thread items represent different types of content in a conversation:

#### UserMessageItem
```python
from chatkit.types import (
    UserMessageItem,
    UserMessageTextContent,
    UserMessageTagContent
)

user_message = UserMessageItem(
    id="msg_123",
    thread_id="thread_abc",
    created_at=datetime.now(),
    content=[
        UserMessageTextContent(text="Hello, can you help me with "),
        UserMessageTagContent(text="project_x", id="proj_123"),
        UserMessageTextContent(text="?"),
    ],
    attachments=[],  # List of Attachment objects
    quoted_text=None,  # Optional quoted text
)
```

**Content Types:**
- `UserMessageTextContent` - Plain text
- `UserMessageTagContent` - @mentions (resolved entities)

**Attachments:**
```python
from chatkit.types import Attachment

attachment = Attachment(
    id="att_123",
    name="document.pdf",
    mime_type="application/pdf",
    size=1024000,
    preview_url="https://...",
    type="file",  # or "image"
)
```

#### AssistantMessageItem
```python
from chatkit.types import AssistantMessageItem, AssistantMessageContent

assistant_message = AssistantMessageItem(
    id="msg_456",
    thread_id="thread_abc",
    created_at=datetime.now(),
    content=[
        AssistantMessageContent(text="I can help you with that project!")
    ],
)
```

#### ToolCallItem
```python
from chatkit.types import ToolCallItem

tool_call = ToolCallItem(
    id="tool_789",
    thread_id="thread_abc",
    created_at=datetime.now(),
    name="get_weather",
    arguments={"location": "San Francisco"},
    output={"temp": 72, "condition": "Sunny"},
)
```

#### ClientToolCallItem
```python
from chatkit.types import ClientToolCallItem

client_tool_call = ClientToolCallItem(
    id="ctool_101",
    thread_id="thread_abc",
    created_at=datetime.now(),
    name="get_selected_nodes",
    arguments={"project": "proj_123"},
    output={"nodes": ["node1", "node2"]},
)
```

#### WidgetItem
```python
from chatkit.types import WidgetItem
from chatkit.widgets import Card, Text

widget_item = WidgetItem(
    id="widget_202",
    thread_id="thread_abc",
    created_at=datetime.now(),
    widget=Card(
        children=[
            Text(value="Interactive Widget", weight="bold")
        ]
    ),
)
```

#### HiddenContextItem
```python
from chatkit.types import HiddenContextItem

hidden_context = HiddenContextItem(
    id="ctx_303",
    thread_id="thread_abc",
    created_at=datetime.now(),
    content="System context not visible to user",
)
```

### 4.3 ThreadStreamEvent Types

Events yielded from `respond()` method:

#### ThreadItemDoneEvent
```python
from chatkit.types import ThreadItemDoneEvent, AssistantMessageItem, AssistantMessageContent

# Yield complete item
yield ThreadItemDoneEvent(
    item=AssistantMessageItem(
        id=msg_id,
        thread_id=thread.id,
        created_at=datetime.now(),
        content=[AssistantMessageContent(text="Complete message")],
    )
)
```

#### ThreadItemDeltaEvent
```python
from chatkit.types import ThreadItemDeltaEvent

# Yield partial item (streaming)
yield ThreadItemDeltaEvent(
    item_id=msg_id,
    delta={"content": [{"text": "Partial "}]},
)

yield ThreadItemDeltaEvent(
    item_id=msg_id,
    delta={"content": [{"text": "text"}]},
)
```

### 4.4 Page & Pagination

**Page Type:**
```python
from chatkit.types import Page

page = Page[ThreadItem](
    data=[item1, item2, item3],  # List of items
    has_more=True,  # More items available
    after="item3_id",  # Cursor for next page
)

# Access page data
for item in page.data:
    print(item.id)

# Check if more pages
if page.has_more:
    next_page = await store.load_thread_items(
        thread_id, after=page.after, limit=20, order="asc", context=ctx
    )
```

---

## 5. OpenAI Agents SDK Integration

### 5.1 AgentContext

`AgentContext` is the context type used when calling OpenAI Agents SDK from ChatKit. It provides helpers for streaming events, rendering widgets, and initiating client tool calls.

**Structure:**
```python
from chatkit.agents import AgentContext

agent_context = AgentContext(
    thread=thread,              # ThreadMetadata
    store=self.store,           # Store instance
    request_context=context     # Your custom context type
)
```

**Key Methods:**

**stream_widget()** - Stream widget to thread:
```python
from chatkit.widgets import Card, Text

async def my_tool(ctx: RunContextWrapper[AgentContext]):
    widget = Card(
        children=[Text(value="Tool result")]
    )
    await ctx.context.stream_widget(widget)
```

**stream_text()** - Stream text message:
```python
async def my_tool(ctx: RunContextWrapper[AgentContext]):
    await ctx.context.stream_text("Processing your request...")
```

**client_tool_call** - Initiate client tool call:
```python
from chatkit.agents import ClientToolCall

async def get_selection(ctx: RunContextWrapper[AgentContext]):
    ctx.context.client_tool_call = ClientToolCall(
        name="get_selected_nodes",
        arguments={"project": "proj_123"},
    )
```

### 5.2 simple_to_agent_input Helper

Converts ChatKit thread items to OpenAI Agents SDK input format using default conversion logic.

**Usage:**
```python
from chatkit.agents import simple_to_agent_input

# Load thread items
items_page = await self.store.load_thread_items(
    thread.id, after=None, limit=20, order="asc", context=context
)

# Convert to agent input
input_items = await simple_to_agent_input(items_page.data)

# Pass to agent
result = Runner.run_streamed(agent, input_items, context=agent_context)
```

**Default Conversion:**
- `UserMessageItem` → User message with text and attachments
- `AssistantMessageItem` → Assistant message
- `ToolCallItem` → Function call + function output
- `ClientToolCallItem` → Function call + function output
- `WidgetItem` → Skipped (not included in agent input)
- `HiddenContextItem` → System message

**Limitations:**
- Basic conversion only
- No custom tag resolution
- No attachment content extraction
- For advanced use cases, use `ThreadItemConverter`

### 5.3 stream_agent_response Helper

Converts streamed OpenAI Agents SDK run into ChatKit events.

**Usage:**
```python
from chatkit.agents import stream_agent_response
from agents import Runner

# Run agent with streaming
result = Runner.run_streamed(assistant, input_items, context=agent_context)

# Convert to ChatKit events
async for event in stream_agent_response(agent_context, result):
    yield event
```

**Event Conversion:**
- Agent text deltas → `ThreadItemDeltaEvent`
- Complete messages → `ThreadItemDoneEvent`
- Tool calls → `ToolCallItem` events
- Widgets from tools → `WidgetItem` events

**Complete Example:**
```python
from agents import Agent, Runner
from chatkit.agents import AgentContext, simple_to_agent_input, stream_agent_response

assistant = Agent(
    name="assistant",
    instructions="You are a helpful assistant.",
    model="gpt-4o-mini",
)

class MyChatKitServer(ChatKitServer[dict]):
    async def respond(self, thread, input_user_message, context):
        # Load history
        items_page = await self.store.load_thread_items(
            thread.id, after=None, limit=20, order="asc", context=context
        )

        # Convert to agent input
        input_items = await simple_to_agent_input(items_page.data)

        # Create agent context
        agent_context = AgentContext(
            thread=thread,
            store=self.store,
            request_context=context
        )

        # Run and stream
        result = Runner.run_streamed(assistant, input_items, context=agent_context)

        async for event in stream_agent_response(agent_context, result):
            yield event
```

### 5.4 ThreadItemConverter

Abstract class for custom thread item conversion logic. Extend this to customize how ChatKit items are converted to agent input.

**Base Class:**
```python
from chatkit.agents import ThreadItemConverter
from chatkit.types import UserMessageItem, Attachment, UserMessageTagContent
from openai.types.responses import ResponseInputTextParam, ResponseInputImageParam

class CustomConverter(ThreadItemConverter):
    """Custom converter for application-specific thread items."""

    async def attachment_to_message_content(self, attachment: Attachment):
        """Convert file attachments to model input."""
        if attachment.type == "image":
            return ResponseInputImageParam(
                type="input_image",
                image_url=attachment.preview_url,
                detail="auto"
            )
        else:
            return ResponseInputTextParam(
                type="input_text",
                text=f"User uploaded file: {attachment.name} ({attachment.mime_type})"
            )

    async def tag_to_message_content(self, tag: UserMessageTagContent):
        """Convert @mentions to context."""
        # Resolve tag to actual entity data
        entity_data = await lookup_entity(tag.id)

        return ResponseInputTextParam(
            type="input_text",
            text=f"Context for @{tag.text}:\n{entity_data['summary']}"
        )

    async def hidden_context_to_input(self, item: HiddenContextItem):
        """Include hidden context in model input."""
        return Message(
            type="message",
            role="user",
            content=[
                ResponseInputTextParam(
                    type="input_text",
                    text=f"<SystemContext>\n{item.content}\n</SystemContext>"
                )
            ]
        )
```

**Usage:**
```python
# Create custom converter
converter = CustomConverter()

# Load thread items
thread_items = await store.load_thread_items(thread_id, None, 50, "asc", {})

# Convert to agent input
agent_input = await converter.to_agent_input(thread_items.data)

# Pass to agent
result = Runner.run_streamed(agent, agent_input, context=agent_context)
```

### 5.5 Custom Conversion Logic

**Override Methods:**

**user_message_to_input()** - Convert user messages:
```python
async def user_message_to_input(
    self, item: UserMessageItem, is_last_message: bool = True
) -> TResponseInputItem | list[TResponseInputItem] | None:
    # Build user text with tags rendered as @key
    message_text_parts = []
    raw_tags = []

    for part in item.content:
        if isinstance(part, UserMessageTextContent):
            message_text_parts.append(part.text)
        elif isinstance(part, UserMessageTagContent):
            message_text_parts.append(f"@{part.text}")
            raw_tags.append(part)

    user_text_item = Message(
        role="user",
        type="message",
        content=[
            ResponseInputTextParam(
                type="input_text",
                text="".join(message_text_parts)
            ),
            *[await self.attachment_to_message_content(a) for a in item.attachments],
        ],
    )

    # Add context for quoted text and @mentions
    context_items = []

    if item.quoted_text and is_last_message:
        context_items.append(
            Message(
                role="user",
                type="message",
                content=[
                    ResponseInputTextParam(
                        type="input_text",
                        text=f"The user is referring to this in particular:\n{item.quoted_text}",
                    )
                ],
            )
        )

    # Resolve tags to context
    if raw_tags:
        tag_content = [
            await self.tag_to_message_content(tag)
            for tag in raw_tags
        ]
        if tag_content:
            context_items.append(
                Message(
                    role="user",
                    type="message",
                    content=[
                        ResponseInputTextParam(
                            type="input_text",
                            text="# User-provided context for @-mentions",
                        ),
                        *tag_content,
                    ],
                )
            )

    return [user_text_item, *context_items]
```

### 5.6 Complete Integration Example

**Full ChatKit Server with Agents SDK:**
```python
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, Response
from chatkit.server import ChatKitServer, StreamingResult
from chatkit.store import InMemoryStore
from chatkit.agents import AgentContext, simple_to_agent_input, stream_agent_response
from agents import Agent, Runner, function_tool

# Define agent with tools
@function_tool
async def get_tasks(ctx):
    """Get user's tasks."""
    return [
        {"id": 1, "title": "Buy milk", "status": "pending"},
        {"id": 2, "title": "Call dentist", "status": "completed"},
    ]

assistant = Agent(
    name="TodoAssistant",
    instructions="You are a helpful todo assistant. Use tools to manage tasks.",
    model="gpt-4o-mini",
    tools=[get_tasks],
)

# ChatKit server
class TodoChatKitServer(ChatKitServer[dict]):
    async def respond(self, thread, input_user_message, context):
        # Load recent history
        items_page = await self.store.load_thread_items(
            thread.id, after=None, limit=20, order="asc", context=context
        )

        # Convert to agent input
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

# FastAPI app
app = FastAPI()
server = TodoChatKitServer(store=InMemoryStore())

@app.post("/chatkit")
async def chatkit_endpoint(request: Request):
    result = await server.process(await request.body(), context={})

    if isinstance(result, StreamingResult):
        return StreamingResponse(result, media_type="text/event-stream")
    return Response(content=result.json, media_type="application/json")
```

---

## 6. Widget System

### 6.1 Widget Concepts

Widgets are structured UI elements that the assistant can stream into the conversation. They enable:
- **Structured data collection** through forms
- **Rich visualizations** (cards, tables, charts)
- **Interactive controls** (buttons, selects)
- **Multiple-choice options** for user selection
- **Contextual actions** paired with UI elements

**When to Use Widgets:**
- Collecting structured input (forms)
- Presenting rich results (tables, cards)
- Offering multiple-choice options
- Providing interactive controls
- Blending text with interactive elements

### 6.2 Widget Components Reference

#### Card
Container component with padding and background.

```python
from chatkit.widgets import Card, Text

card = Card(
    children=[
        Text(value="Card Title", weight="bold"),
        Text(value="Card content goes here"),
    ],
    padding=4,                    # 0-8 (spacing units)
    background="surface-elevated", # "surface", "surface-elevated", "primary", "secondary"
    asForm=False,                 # Treat as form (enables validation)
    confirmAction=None,           # Action when form submitted
)
```

**Properties:**
- `children` (list): Child widgets
- `padding` (int): Padding in spacing units (0-8)
- `background` (str): Background color variant
- `asForm` (bool): Enable form behavior
- `confirmAction` (Action): Action on form submit

#### Text
Text display with styling options.

```python
from chatkit.widgets import Text

text = Text(
    value="Hello, world!",
    weight="normal",    # "normal", "medium", "bold"
    size="md",          # "xs", "sm", "md", "lg", "xl"
    color="primary",    # "primary", "secondary", "tertiary", "success", "warning", "error"
    editable=None,      # {"name": "field_name", "required": True, "pattern": "regex"}
)
```

**Properties:**
- `value` (str): Text content
- `weight` (str): Font weight
- `size` (str): Font size
- `color` (str): Text color
- `editable` (dict): Make text editable (for forms)
  - `name` (str): Field name in form data
  - `required` (bool): Field is required
  - `pattern` (str): Regex validation pattern

#### Button
Interactive button with action.

```python
from chatkit.widgets import Button
from chatkit.actions import Action

button = Button(
    label="Click Me",
    style="primary",        # "primary", "secondary", "tertiary", "danger"
    onClickAction=Action(
        type="button_clicked",
        data={"button_id": "btn_1"}
    ),
    submit=False,           # Submit form (if inside Form)
    disabled=False,
)
```

**Properties:**
- `label` (str): Button text
- `style` (str): Button style variant
- `onClickAction` (Action): Action when clicked
- `submit` (bool): Submit parent form
- `disabled` (bool): Disable button

#### Row
Horizontal layout container.

```python
from chatkit.widgets import Row, Button

row = Row(
    children=[
        Button(label="Cancel", style="secondary"),
        Button(label="Confirm", style="primary"),
    ],
    gap=2,              # Spacing between children (0-8)
    align="center",     # "start", "center", "end", "stretch"
)
```

**Properties:**
- `children` (list): Child widgets
- `gap` (int): Spacing between children
- `align` (str): Vertical alignment

#### Column
Vertical layout container.

```python
from chatkit.widgets import Column, Text

column = Column(
    children=[
        Text(value="Line 1"),
        Text(value="Line 2"),
        Text(value="Line 3"),
    ],
    gap=2,              # Spacing between children (0-8)
    align="start",      # "start", "center", "end", "stretch"
)
```

**Properties:**
- `children` (list): Child widgets
- `gap` (int): Spacing between children
- `align` (str): Horizontal alignment

#### Form
Form container with automatic data collection.

```python
from chatkit.widgets import Form, Text, Button
from chatkit.actions import Action

form = Form(
    children=[
        Text(value="Name:", color="secondary", size="sm"),
        Text(
            value="",
            editable={"name": "name", "required": True}
        ),
        Text(value="Email:", color="secondary", size="sm"),
        Text(
            value="",
            editable={"name": "email", "required": True, "pattern": r"^[\w\.-]+@[\w\.-]+\.\w+$"}
        ),
        Button(label="Submit", submit=True),
    ],
    direction="col",        # "row" or "col"
    onSubmitAction=Action(
        type="form_submitted",
        data={"form_id": "contact_form"}
    ),
)
```

**Properties:**
- `children` (list): Child widgets (with editable fields)
- `direction` (str): Layout direction
- `onSubmitAction` (Action): Action when form submitted
- Form automatically collects values from editable fields by `name`

**Form Data Structure:**
```python
# When form is submitted, action receives:
{
    "type": "form_submitted",
    "data": {
        "form_id": "contact_form",
        "name": "John Doe",      # From editable field
        "email": "john@example.com"  # From editable field
    }
}
```

#### Title
Heading text with predefined styling.

```python
from chatkit.widgets import Title

title = Title(
    value="Section Title",
    level=1,            # 1-6 (h1-h6)
)
```

**Properties:**
- `value` (str): Title text
- `level` (int): Heading level (1-6)

#### Image
Image display component.

```python
from chatkit.widgets import Image

image = Image(
    url="https://example.com/image.png",
    alt="Image description",
    width=400,          # Optional width in pixels
    height=300,         # Optional height in pixels
)
```

**Properties:**
- `url` (str): Image URL
- `alt` (str): Alt text for accessibility
- `width` (int): Width in pixels
- `height` (int): Height in pixels

### 6.3 Widget Styling & Properties

**Spacing Units:**
- 0 = 0px
- 1 = 4px
- 2 = 8px
- 3 = 12px
- 4 = 16px
- 5 = 20px
- 6 = 24px
- 7 = 28px
- 8 = 32px

**Color Variants:**
- `primary` - Primary brand color
- `secondary` - Secondary/muted color
- `tertiary` - Tertiary/subtle color
- `success` - Success/positive color
- `warning` - Warning/caution color
- `error` - Error/danger color

**Background Variants:**
- `surface` - Default surface
- `surface-elevated` - Elevated surface (card)
- `primary` - Primary brand background
- `secondary` - Secondary background

### 6.4 Interactive Widgets & Actions

**Action Structure:**
```python
from chatkit.actions import Action

action = Action(
    type="action_type",     # String identifier for action
    data={"key": "value"}   # Arbitrary data payload
)
```

**Button with Action:**
```python
from chatkit.widgets import Button, Card, Text
from chatkit.actions import Action

weather_card = Card(
    children=[
        Text(value="Weather in San Francisco", weight="bold"),
        Text(value="Temperature: 72°F"),
        Button(
            label="Refresh",
            onClickAction=Action(
                type="refresh_weather",
                data={"location": "San Francisco"}
            )
        ),
    ]
)
```

**Handling Actions in Server:**
```python
class MyChatKitServer(ChatKitServer[dict]):
    async def action(
        self,
        thread: ThreadMetadata,
        action: Action[str, Any],
        sender: WidgetItem | None,
        context: dict,
    ) -> AsyncIterator[ThreadStreamEvent]:
        """Handle widget actions dispatched from client."""
        if action.type == "refresh_weather":
            location = action.data.get("location")

            # Fetch new data
            weather_data = await fetch_weather(location)

            # Create updated widget
            updated_widget = Card(
                children=[
                    Text(value=f"Weather in {location}", weight="bold"),
                    Text(value=f"Updated: {weather_data['temp']}°F"),
                ]
            )

            # Stream updated widget
            agent_context = AgentContext(
                thread=thread,
                store=self.store,
                request_context=context
            )
            await agent_context.stream_widget(updated_widget)
```

### 6.5 Widget Templates

**Loading from .widget Files:**
```python
from chatkit.widgets import WidgetTemplate

# Load template from file
template = WidgetTemplate.from_file("weather.widget")

# Build widget with data
widget = template.build({
    "location": "San Francisco",
    "temp": 72,
    "condition": "Sunny"
})

# Stream to thread
await agent_context.stream_widget(widget)
```

**Template File Format (.widget):**
```jsx
<Card padding={4}>
  <Text value={`Weather in ${location}`} weight="bold" size="lg" />
  <Text value={`Temperature: ${temp}°F`} />
  <Text value={`Condition: ${condition}`} />
  <Button
    label="Refresh"
    onClickAction={{
      type: "refresh_weather",
      data: { location }
    }}
  />
</Card>
```

### 6.6 Streaming Widgets

**From respond() Method:**
```python
from chatkit.types import ThreadItemDoneEvent, WidgetItem
from chatkit.widgets import Card, Text

async def respond(self, thread, input_user_message, context):
    # Create widget
    widget = Card(
        children=[Text(value="Widget content")]
    )

    # Generate ID
    widget_id = self.store.generate_item_id("widget", thread, context)

    # Yield widget event
    yield ThreadItemDoneEvent(
        item=WidgetItem(
            id=widget_id,
            thread_id=thread.id,
            created_at=datetime.now(),
            widget=widget,
        )
    )
```

**From Agent Tool:**
```python
from agents import function_tool, RunContextWrapper
from chatkit.agents import AgentContext
from chatkit.widgets import Card, Text

@function_tool
async def show_results(ctx: RunContextWrapper[AgentContext]):
    """Display results as a widget."""
    widget = Card(
        children=[
            Text(value="Results", weight="bold"),
            Text(value="Data goes here"),
        ]
    )

    await ctx.context.stream_widget(widget)
    return "Widget displayed"
```

---

## 7. Tool Integration

### 7.1 Server Tools

Server tools are Python functions registered with your agent that the model can call during inference. ChatKit serializes the call, runs your function, and feeds the output back to the model.

**Use Cases:**
- Look up data in APIs or databases
- Kick off long-running jobs with progress updates
- Update domain state (tickets, orders, files)
- Fetch application context dynamically

**Basic Server Tool:**
```python
from agents import function_tool

@function_tool(description_override="Fetch user's tasks from database")
async def get_tasks(user_id: str) -> list[dict]:
    """Get all tasks for a user."""
    tasks = await db.query("SELECT * FROM tasks WHERE user_id = ?", user_id)
    return [{"id": t.id, "title": t.title, "status": t.status} for t in tasks]

# Register with agent
assistant = Agent(
    name="assistant",
    instructions="Use tools to help users manage tasks.",
    tools=[get_tasks],
)
```

**Server Tool with AgentContext:**
```python
from agents import function_tool, RunContextWrapper
from chatkit.agents import AgentContext

@function_tool(description_override="Fetch workspace context")
async def get_workspace_context(ctx: RunContextWrapper[AgentContext]):
    """Fetch the user's workspace context."""
    # Access request context
    org_id = ctx.context.request_context.get("org_id")

    # Fetch workspace data
    workspace = await load_workspace(org_id)

    return {
        "workspace_id": workspace.id,
        "features": workspace.feature_flags,
    }

# Register with agent
assistant = Agent(
    name="assistant",
    tools=[get_workspace_context],
)
```

**Server Tool with Widget Output:**
```python
from agents import function_tool, RunContextWrapper
from chatkit.agents import AgentContext
from chatkit.widgets import Card, Text

@function_tool
async def show_task_summary(ctx: RunContextWrapper[AgentContext]):
    """Display task summary as a widget."""
    tasks = await get_tasks()

    # Create widget
    widget = Card(
        children=[
            Text(value="Task Summary", weight="bold", size="lg"),
            Text(value=f"Total: {len(tasks)}"),
            Text(value=f"Pending: {sum(1 for t in tasks if t['status'] == 'pending')}"),
            Text(value=f"Completed: {sum(1 for t in tasks if t['status'] == 'completed')}"),
        ]
    )

    # Stream widget
    await ctx.context.stream_widget(widget)

    return "Task summary displayed"
```

### 7.2 Client Tools

Client tools let the agent invoke browser/app callbacks mid-inference. The model pauses, ChatKit sends the tool request to the client, and resumes with the returned result.

**Use Cases:**
- Read user's current selection in UI
- Get viewport/scroll position
- Access browser storage
- Trigger client-side actions

**Defining Client Tool:**
```python
from agents import Agent, RunContextWrapper, StopAtTools, function_tool
from chatkit.agents import AgentContext, ClientToolCall

@function_tool(description_override="Read the user's current canvas selection.")
async def get_selected_canvas_nodes(ctx: RunContextWrapper[AgentContext]) -> None:
    """Get nodes selected in canvas."""
    ctx.context.client_tool_call = ClientToolCall(
        name="get_selected_canvas_nodes",
        arguments={"project": "my_project"},
    )

assistant = Agent[AgentContext](
    name="assistant",
    instructions="Use tools to help with canvas operations.",
    tools=[get_selected_canvas_nodes],
    # StopAtTools pauses model generation for client callback
    tool_use_behavior=StopAtTools(stop_at_tool_names=[get_selected_canvas_nodes.name]),
)
```

**Client Tool Flow:**
1. Model decides to call client tool
2. ChatKit emits pending client tool call item
3. Frontend runs registered client tool
4. Client posts tool result back to server
5. ChatKit stores result as `ClientToolCallItem`
6. Server continues inference with tool result

**Client-Side Registration (JavaScript):**
```javascript
// Register client tool handler
chatkit.registerClientTool("get_selected_canvas_nodes", async (args) => {
  const selectedNodes = canvas.getSelectedNodes(args.project);
  return { nodes: selectedNodes };
});
```

### 7.3 Tool Calling Patterns

**Multiple Tools:**
```python
@function_tool
async def get_tasks():
    """Get all tasks."""
    return await db.query_tasks()

@function_tool
async def add_task(title: str, description: str = ""):
    """Add a new task."""
    task = await db.create_task(title, description)
    return {"id": task.id, "title": task.title}

@function_tool
async def complete_task(task_id: int):
    """Mark task as complete."""
    await db.update_task(task_id, status="completed")
    return {"status": "completed"}

assistant = Agent(
    name="assistant",
    instructions="Use tools to manage tasks.",
    tools=[get_tasks, add_task, complete_task],
)
```

**Tool with Streaming Progress:**
```python
@function_tool
async def process_large_file(ctx: RunContextWrapper[AgentContext], file_id: str):
    """Process a large file with progress updates."""
    # Stream progress updates
    await ctx.context.stream_text("Starting file processing...")

    # Process in chunks
    for i in range(10):
        await process_chunk(file_id, i)
        await ctx.context.stream_text(f"Progress: {(i+1)*10}%")

    await ctx.context.stream_text("Processing complete!")

    return {"status": "completed", "chunks": 10}
```

### 7.4 Tool Execution Flow

**Server Tool Execution:**
```
User Message → Agent decides to call tool
              ↓
         Tool call serialized
              ↓
         Python function executed
              ↓
         Tool output returned
              ↓
         Output fed back to model
              ↓
         Agent continues with result
```

**Client Tool Execution:**
```
User Message → Agent decides to call client tool
              ↓
         StopAtTools pauses generation
              ↓
         ClientToolCall emitted to frontend
              ↓
         Frontend executes registered handler
              ↓
         Client posts result back
              ↓
         Server stores ClientToolCallItem
              ↓
         Agent resumes with result
```

### 7.5 StopAtTools Behavior

`StopAtTools` is a tool use behavior that pauses model generation when specific tools are called, allowing client tools to execute and return results.

**Configuration:**
```python
from agents import StopAtTools

assistant = Agent(
    name="assistant",
    tools=[get_selected_nodes, get_viewport],
    tool_use_behavior=StopAtTools(
        stop_at_tool_names=[
            "get_selected_nodes",
            "get_viewport"
        ]
    ),
)
```

**When to Use:**
- Client tools that need to pause inference
- Tools that require user interaction
- Tools with long execution times

**When NOT to Use:**
- Server tools (they execute automatically)
- Tools that don't need to pause generation

---

## 8. Action Handling

### 8.1 Action Types

Actions are dispatched from interactive widgets (buttons, forms) to trigger server-side logic.

**Action Structure:**
```python
from chatkit.actions import Action

action = Action(
    type="action_type",     # String identifier
    data={"key": "value"}   # Arbitrary payload
)
```

**Common Action Types:**
- Button clicks
- Form submissions
- Widget interactions
- Custom application actions

### 8.2 Implementing action Method

Override the `action()` method in your ChatKitServer to handle widget actions.

**Method Signature:**
```python
async def action(
    self,
    thread: ThreadMetadata,
    action: Action[str, Any],
    sender: WidgetItem | None,
    context: ContextType,
) -> AsyncIterator[ThreadStreamEvent]:
    """
    Handle widget actions dispatched from client.

    Args:
        thread: Thread metadata
        action: Action object with type and data
        sender: Widget that sent the action (if applicable)
        context: Request context

    Yields:
        ThreadStreamEvent: Events to stream to client
    """
```

**Basic Implementation:**
```python
class MyChatKitServer(ChatKitServer[dict]):
    async def action(self, thread, action, sender, context):
        if action.type == "refresh_weather":
            location = action.data.get("location")

            # Fetch new data
            weather_data = await fetch_weather(location)

            # Create updated widget
            updated_widget = Card(
                children=[
                    Text(value=f"Weather in {location}", weight="bold"),
                    Text(value=f"Temperature: {weather_data['temp']}°F"),
                    Text(value=f"Condition: {weather_data['condition']}"),
                ]
            )

            # Stream updated widget
            agent_context = AgentContext(
                thread=thread,
                store=self.store,
                request_context=context
            )
            await agent_context.stream_widget(updated_widget)

        elif action.type == "book_appointment":
            date = action.data.get("date")

            # Book appointment
            await book_appointment(date)

            # Send confirmation message
            msg_id = self.store.generate_item_id("message", thread, context)
            yield ThreadItemDoneEvent(
                item=AssistantMessageItem(
                    id=msg_id,
                    thread_id=thread.id,
                    created_at=datetime.now(),
                    content=[AssistantMessageContent(
                        text=f"Appointment booked for {date}"
                    )],
                )
            )
```

### 8.3 Widget Actions

**Button Action:**
```python
from chatkit.widgets import Button
from chatkit.actions import Action

button = Button(
    label="Delete Task",
    style="danger",
    onClickAction=Action(
        type="delete_task",
        data={"task_id": 123}
    )
)
```

**Handling Button Action:**
```python
async def action(self, thread, action, sender, context):
    if action.type == "delete_task":
        task_id = action.data.get("task_id")
        await db.delete_task(task_id)

        # Send confirmation
        await agent_context.stream_text(f"Task {task_id} deleted")
```

### 8.4 Form Submission Actions

**Form with Action:**
```python
from chatkit.widgets import Form, Text, Button
from chatkit.actions import Action

form = Form(
    children=[
        Text(value="Task Title:", color="secondary", size="sm"),
        Text(value="", editable={"name": "title", "required": True}),
        Text(value="Description:", color="secondary", size="sm"),
        Text(value="", editable={"name": "description"}),
        Button(label="Create Task", submit=True),
    ],
    direction="col",
    onSubmitAction=Action(
        type="create_task",
        data={"form_id": "new_task_form"}
    ),
)
```

**Handling Form Submission:**
```python
async def action(self, thread, action, sender, context):
    if action.type == "create_task":
        # Form data is merged into action.data
        title = action.data.get("title")
        description = action.data.get("description", "")

        # Create task
        task = await db.create_task(title, description)

        # Send confirmation
        msg_id = self.store.generate_item_id("message", thread, context)
        yield ThreadItemDoneEvent(
            item=AssistantMessageItem(
                id=msg_id,
                thread_id=thread.id,
                created_at=datetime.now(),
                content=[AssistantMessageContent(
                    text=f"Task '{task.title}' created successfully!"
                )],
            )
        )
```

### 8.5 Action Payload Structure

**Form Data Merging:**
```python
# Form definition
form = Form(
    onSubmitAction=Action(
        type="update_todo",
        data={"todo_id": 123}  # Static data
    ),
    children=[
        Text(value="", editable={"name": "title", "required": True}),
        Text(value="", editable={"name": "description"}),
    ]
)

# When submitted, action.data contains:
{
    "todo_id": 123,        # From Action.data
    "title": "New Title",  # From editable field
    "description": "New Description"  # From editable field
}
```

**Nested Form Data:**
```python
# Form with nested structure
form = Form(
    children=[
        Text(value="", editable={"name": "user.name"}),
        Text(value="", editable={"name": "user.email"}),
    ]
)

# Resulting action.data:
{
    "user": {
        "name": "John Doe",
        "email": "john@example.com"
    }
}
```

---

## 9. Complete Implementation Examples

### 9.1 Basic ChatKit Server

**Minimal Working Server:**
```python
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, Response
from chatkit.server import ChatKitServer, StreamingResult
from chatkit.store import InMemoryStore
from chatkit.types import ThreadMetadata, UserMessageItem, ThreadStreamEvent
from chatkit.types import ThreadItemDoneEvent, AssistantMessageItem, AssistantMessageContent
from datetime import datetime
from collections.abc import AsyncIterator

class BasicChatKitServer(ChatKitServer[dict]):
    async def respond(
        self,
        thread: ThreadMetadata,
        input_user_message: UserMessageItem | None,
        context: dict,
    ) -> AsyncIterator[ThreadStreamEvent]:
        # Generate message ID
        msg_id = self.store.generate_item_id("message", thread, context)

        # Yield assistant message
        yield ThreadItemDoneEvent(
            item=AssistantMessageItem(
                id=msg_id,
                thread_id=thread.id,
                created_at=datetime.now(),
                content=[AssistantMessageContent(
                    text="Hello! I'm a basic ChatKit assistant. How can I help you?"
                )],
            )
        )

# FastAPI app
app = FastAPI()
server = BasicChatKitServer(store=InMemoryStore())

@app.post("/chatkit")
async def chatkit_endpoint(request: Request):
    result = await server.process(await request.body(), context={})

    if isinstance(result, StreamingResult):
        return StreamingResponse(result, media_type="text/event-stream")
    return Response(content=result.json, media_type="application/json")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 9.2 ChatKit with Agents SDK

**Complete Todo Assistant:**
```python
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, Response
from chatkit.server import ChatKitServer, StreamingResult
from chatkit.store import InMemoryStore
from chatkit.agents import AgentContext, simple_to_agent_input, stream_agent_response
from agents import Agent, Runner, function_tool

# Define tools
@function_tool
async def get_tasks():
    """Get all tasks."""
    return [
        {"id": 1, "title": "Buy milk", "status": "pending"},
        {"id": 2, "title": "Call dentist", "status": "completed"},
    ]

@function_tool
async def add_task(title: str, description: str = ""):
    """Add a new task."""
    # Simulate task creation
    new_task = {"id": 3, "title": title, "description": description, "status": "pending"}
    return new_task

@function_tool
async def complete_task(task_id: int):
    """Mark task as complete."""
    return {"id": task_id, "status": "completed"}

# Define agent
assistant = Agent(
    name="TodoAssistant",
    instructions="""You are a helpful todo assistant.

Use the available tools to:
- Get tasks with get_tasks()
- Add new tasks with add_task(title, description)
- Complete tasks with complete_task(task_id)

Be conversational and helpful.""",
    model="gpt-4o-mini",
    tools=[get_tasks, add_task, complete_task],
)

# ChatKit server
class TodoChatKitServer(ChatKitServer[dict]):
    async def respond(self, thread, input_user_message, context):
        # Load recent history
        items_page = await self.store.load_thread_items(
            thread.id, after=None, limit=20, order="asc", context=context
        )

        # Convert to agent input
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

# FastAPI app
app = FastAPI()
server = TodoChatKitServer(store=InMemoryStore())

@app.post("/chatkit")
async def chatkit_endpoint(request: Request):
    result = await server.process(await request.body(), context={})

    if isinstance(result, StreamingResult):
        return StreamingResponse(result, media_type="text/event-stream")
    return Response(content=result.json, media_type="application/json")
```

### 9.3 Interactive Widgets Example

**Server with Widget Actions:**
```python
from chatkit.server import ChatKitServer
from chatkit.store import InMemoryStore
from chatkit.types import ThreadMetadata, Action, ThreadStreamEvent, WidgetItem
from chatkit.widgets import Card, Text, Button, Row
from chatkit.actions import Action as WidgetAction
from chatkit.agents import AgentContext
from collections.abc import AsyncIterator

class InteractiveChatKitServer(ChatKitServer[dict]):
    async def respond(self, thread, input_user_message, context):
        # Create interactive widget
        widget = Card(
            children=[
                Text(value="Task Manager", weight="bold", size="lg"),
                Text(value="What would you like to do?"),
                Row(
                    children=[
                        Button(
                            label="View Tasks",
                            onClickAction=WidgetAction(
                                type="view_tasks",
                                data={}
                            )
                        ),
                        Button(
                            label="Add Task",
                            style="primary",
                            onClickAction=WidgetAction(
                                type="show_add_form",
                                data={}
                            )
                        ),
                    ],
                    gap=2
                ),
            ],
            padding=4
        )

        # Stream widget
        widget_id = self.store.generate_item_id("widget", thread, context)
        yield ThreadItemDoneEvent(
            item=WidgetItem(
                id=widget_id,
                thread_id=thread.id,
                created_at=datetime.now(),
                widget=widget,
            )
        )

    async def action(self, thread, action, sender, context):
        agent_context = AgentContext(
            thread=thread,
            store=self.store,
            request_context=context
        )

        if action.type == "view_tasks":
            # Show tasks widget
            tasks = await get_tasks()

            widget = Card(
                children=[
                    Text(value="Your Tasks", weight="bold", size="lg"),
                    *[Text(value=f"• {t['title']} ({t['status']})") for t in tasks],
                ]
            )

            await agent_context.stream_widget(widget)

        elif action.type == "show_add_form":
            # Show add task form
            form = Form(
                children=[
                    Text(value="Add New Task", weight="bold"),
                    Text(value="Title:", color="secondary", size="sm"),
                    Text(value="", editable={"name": "title", "required": True}),
                    Button(label="Create", submit=True),
                ],
                direction="col",
                onSubmitAction=WidgetAction(
                    type="create_task",
                    data={}
                )
            )

            await agent_context.stream_widget(form)

        elif action.type == "create_task":
            title = action.data.get("title")
            await add_task(title)

            await agent_context.stream_text(f"Task '{title}' created successfully!")
```

### 9.4 Custom Store Implementation

**PostgreSQL Store (Complete):**
```python
import psycopg
from chatkit.store import Store, NotFoundError
from chatkit.types import ThreadMetadata, ThreadItem, Attachment, Page
from dataclasses import dataclass

@dataclass
class RequestContext:
    user_id: str
    org_id: str

class PostgresStore(Store[RequestContext]):
    def __init__(self, conninfo: str):
        self._conninfo = conninfo
        self._init_schema()

    def _init_schema(self):
        with psycopg.connect(self._conninfo) as conn, conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS threads (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    org_id TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL,
                    data JSONB NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_threads_user
                ON threads (user_id, org_id);
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id TEXT PRIMARY KEY,
                    thread_id TEXT NOT NULL REFERENCES threads(id) ON DELETE CASCADE,
                    user_id TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL,
                    data JSONB NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_items_thread_created
                ON items (thread_id, created_at);
            """)

            conn.commit()

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

    async def save_thread(self, thread: ThreadMetadata, context: RequestContext) -> None:
        payload = thread.model_dump(mode="json")
        with psycopg.connect(self._conninfo) as conn, conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO threads (id, user_id, org_id, created_at, data)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET data = EXCLUDED.data
                """,
                (thread.id, context.user_id, context.org_id, thread.created_at, payload)
            )
            conn.commit()

    # Implement remaining methods...
```

---

## 10. Phase III Migration Guide

### 10.1 Current Architecture Analysis

**Current Phase III Implementation (WITHOUT ChatKit SDK):**

The current implementation uses:
- Custom React components for chat UI
- Manual message rendering
- Standard OpenAI client for LLM calls
- Custom conversation state management
- No widget system
- No interactive UI components

**Current Backend Structure:**
```python
# backend/src/agents/orchestrator.py (CURRENT)
from openai import AsyncOpenAI

class AgentOrchestrator:
    def __init__(self):
        self.client = AsyncOpenAI(...)

    async def process_message(self, conversation_id, user_message, history):
        # Manual message formatting
        messages = history + [{"role": "user", "content": user_message}]

        # Call OpenAI
        response = await self.client.chat.completions.create(
            model="llama-3.3-70b",
            messages=messages,
            tools=self._get_tool_definitions(),
        )

        # Manual tool calling logic
        if response.choices[0].message.tool_calls:
            # Execute tools manually
            # Append results to history
            # Call LLM again
            pass

        return {"response": response.choices[0].message.content}
```

**Issues with Current Approach:**
1. No rich UI components (cards, buttons, forms)
2. Manual tool calling logic (error-prone)
3. No widget system for interactive experiences
4. Custom conversation state management
5. No streaming widget support
6. Limited interactivity (text-only)

### 10.2 Migration Strategy

**Benefits of ChatKit SDK:**
- **Rich UI Components**: Cards, buttons, forms, interactive widgets
- **Automatic Tool Handling**: Server and client tools with automatic execution
- **Widget System**: Stream structured UI elements to chat
- **Action Handling**: Interactive buttons and forms with server callbacks
- **Seamless Agents SDK Integration**: Built-in helpers for OpenAI Agents SDK
- **Type-Safe Store Interface**: Flexible data persistence abstraction

**Migration Approach:**

**Phase 1: Add ChatKit Backend (Parallel Implementation)**
- Install ChatKit SDK
- Create ChatKitServer implementation
- Implement Store interface
- Test with subset of features
- Keep existing backend running

**Phase 2: Migrate Frontend**
- Install ChatKit JS library
- Replace custom chat components with ChatKit UI
- Connect to ChatKit backend endpoint
- Test widget rendering

**Phase 3: Enable Advanced Features**
- Add interactive widgets (cards, buttons)
- Implement action handlers
- Add client tools
- Enable streaming widgets

**Phase 4: Deprecate Old System**
- Route all traffic to ChatKit backend
- Remove old orchestrator code
- Update documentation

### 10.3 Step-by-Step Migration

**Step 1: Install ChatKit SDK**

```bash
# Backend
pip install openai-chatkit

# Frontend
npm install @openai/chatkit-react
```

**Step 2: Create ChatKit Server**

```python
# backend/src/chatkit_server.py (NEW)
from chatkit.server import ChatKitServer
from chatkit.store import InMemoryStore
from chatkit.agents import AgentContext, simple_to_agent_input, stream_agent_response
from agents import Agent, Runner

# Import existing tools
from mcp.mcp_server import add_task, list_tasks, complete_task, delete_task, update_task

# Create agent with MCP tools
assistant = Agent(
    name="TodoAssistant",
    instructions="""You are a helpful AI assistant for managing todo tasks.

Use the MCP tools to:
- Create new tasks with add_task
- View tasks with list_tasks
- Update tasks with update_task
- Mark tasks complete with complete_task
- Delete tasks with delete_task

Always verify mutations by re-querying state after changes.""",
    model="llama-3.3-70b",
    tools=[add_task, list_tasks, complete_task, delete_task, update_task],
)

class TodoChatKitServer(ChatKitServer[dict]):
    async def respond(self, thread, input_user_message, context):
        # Load recent history
        items_page = await self.store.load_thread_items(
            thread.id, after=None, limit=20, order="asc", context=context
        )

        # Convert to agent input
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

**Step 3: Add ChatKit Endpoint**

```python
# backend/src/api/chatkit.py (NEW)
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse, Response
from chatkit.server import StreamingResult
from chatkit_server import TodoChatKitServer
from chatkit.store import InMemoryStore

router = APIRouter()

# Initialize server
chatkit_server = TodoChatKitServer(store=InMemoryStore())

@router.post("/chatkit")
async def chatkit_endpoint(request: Request):
    """
    ChatKit endpoint handling all chat operations.

    Accepts POST requests and responds with either:
    - JSON response (for non-streaming operations)
    - Server-Sent Events (SSE) for streaming responses
    """
    result = await chatkit_server.process(await request.body(), context={})

    if isinstance(result, StreamingResult):
        return StreamingResponse(result, media_type="text/event-stream")
    return Response(content=result.json, media_type="application/json")
```

**Step 4: Update Frontend**

```typescript
// frontend/src/components/ChatKitChat.tsx (NEW)
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

**Step 5: Add Interactive Widgets**

```python
# backend/src/chatkit_server.py (ENHANCED)
from chatkit.widgets import Card, Text, Button, Row
from chatkit.actions import Action

# Add widget tool
@function_tool
async def show_task_summary(ctx: RunContextWrapper[AgentContext]):
    """Display task summary as an interactive widget."""
    tasks = await list_tasks()

    widget = Card(
        children=[
            Text(value="Task Summary", weight="bold", size="lg"),
            Text(value=f"Total Tasks: {len(tasks)}"),
            Text(value=f"Pending: {sum(1 for t in tasks if t['status'] == 'pending')}"),
            Text(value=f"Completed: {sum(1 for t in tasks if t['status'] == 'completed')}"),
            Row(
                children=[
                    Button(
                        label="Refresh",
                        onClickAction=Action(type="refresh_summary", data={})
                    ),
                    Button(
                        label="Add Task",
                        style="primary",
                        onClickAction=Action(type="show_add_form", data={})
                    ),
                ],
                gap=2
            ),
        ],
        padding=4
    )

    await ctx.context.stream_widget(widget)
    return "Task summary displayed"

# Add to agent tools
assistant = Agent(
    name="TodoAssistant",
    tools=[..., show_task_summary],
)
```

**Step 6: Implement Action Handlers**

```python
# backend/src/chatkit_server.py (ENHANCED)
class TodoChatKitServer(ChatKitServer[dict]):
    # ... existing respond method ...

    async def action(self, thread, action, sender, context):
        """Handle widget actions."""
        agent_context = AgentContext(
            thread=thread,
            store=self.store,
            request_context=context
        )

        if action.type == "refresh_summary":
            # Refresh task summary
            await show_task_summary(agent_context)

        elif action.type == "show_add_form":
            # Show add task form
            form = Form(
                children=[
                    Text(value="Add New Task", weight="bold"),
                    Text(value="Title:", color="secondary", size="sm"),
                    Text(value="", editable={"name": "title", "required": True}),
                    Text(value="Description:", color="secondary", size="sm"),
                    Text(value="", editable={"name": "description"}),
                    Button(label="Create Task", submit=True),
                ],
                direction="col",
                onSubmitAction=Action(type="create_task", data={})
            )

            await agent_context.stream_widget(form)

        elif action.type == "create_task":
            title = action.data.get("title")
            description = action.data.get("description", "")

            # Create task
            await add_task(title, description)

            # Show confirmation
            await agent_context.stream_text(f"Task '{title}' created successfully!")
```

### 10.4 Code Comparison

**BEFORE (Current Implementation):**

```python
# 100+ lines of manual chat handling
class AgentOrchestrator:
    async def process_message(self, conversation_id, user_message, history):
        # Manual message formatting
        messages = self._format_messages(history, user_message)

        # Manual tool calling
        response = await self.client.chat.completions.create(...)

        if response.choices[0].message.tool_calls:
            for tool_call in response.choices[0].message.tool_calls:
                # Parse tool call
                # Execute tool
                # Append to history
                # Call LLM again
                pass

        # Manual response formatting
        return {"response": response.choices[0].message.content}
```

**AFTER (ChatKit Implementation):**

```python
# 20 lines - automatic tool calling, streaming, widgets
class TodoChatKitServer(ChatKitServer[dict]):
    async def respond(self, thread, input_user_message, context):
        items_page = await self.store.load_thread_items(
            thread.id, after=None, limit=20, order="asc", context=context
        )
        input_items = await simple_to_agent_input(items_page.data)
        agent_context = AgentContext(thread=thread, store=self.store, request_context=context)
        result = Runner.run_streamed(assistant, input_items, context=agent_context)

        async for event in stream_agent_response(agent_context, result):
            yield event
```

**Benefits:**
- **80% less code** for chat handling
- **Automatic** tool calling and streaming
- **Built-in** widget system
- **Type-safe** store interface
- **Interactive** UI components
- **Action** handling for buttons/forms

### 10.5 Testing & Verification

**Test Plan:**

1. **Basic Chat Flow:**
```python
# Test basic message exchange
response = await client.post("/chatkit", json={
    "thread_id": "test_123",
    "message": "Hello"
})
assert response.status_code == 200
```

2. **Tool Calling:**
```python
# Test that agent calls tools
response = await client.post("/chatkit", json={
    "thread_id": "test_123",
    "message": "Show me my tasks"
})
# Verify list_tasks was called
```

3. **Widget Rendering:**
```python
# Test widget streaming
response = await client.post("/chatkit", json={
    "thread_id": "test_123",
    "message": "Show task summary"
})
# Verify widget event in stream
```

4. **Action Handling:**
```python
# Test button action
response = await client.post("/chatkit", json={
    "thread_id": "test_123",
    "action": {
        "type": "refresh_summary",
        "data": {}
    }
})
# Verify action handler executed
```

**Verification Checklist:**
- [ ] ChatKit endpoint responds to requests
- [ ] Agent calls MCP tools correctly
- [ ] Widgets render in frontend
- [ ] Button actions trigger server handlers
- [ ] Forms collect and submit data
- [ ] Streaming works correctly
- [ ] Store persists conversation history
- [ ] No regressions in existing functionality

---

## 11. Best Practices

### 11.1 Store Implementation

**DO:**
- Store thread items as JSON for schema flexibility
- Use cursor-based pagination (not offset)
- Add indexes on (thread_id, created_at)
- Implement user isolation with context.user_id
- Use transactions for multi-item operations

**DON'T:**
- Don't use offset-based pagination (performance issues)
- Don't store sensitive data without encryption
- Don't skip user_id filtering (security risk)
- Don't load entire conversation history (memory issues)

**Example:**
```python
# GOOD: Cursor-based pagination with user isolation
async def load_thread_items(self, thread_id, after, limit, order, context):
    query = """
        SELECT data FROM items
        WHERE thread_id = %s AND user_id = %s
        AND created_at > (SELECT created_at FROM items WHERE id = %s)
        ORDER BY created_at ASC
        LIMIT %s
    """
    return await db.query(query, thread_id, context.user_id, after, limit)

# BAD: Offset-based pagination without user isolation
async def load_thread_items(self, thread_id, offset, limit, order, context):
    query = "SELECT * FROM items WHERE thread_id = %s OFFSET %s LIMIT %s"
    return await db.query(query, thread_id, offset, limit)
```

### 11.2 Thread Management

**DO:**
- Tune limit parameter based on model context budget (20-50 items)
- Load items in ascending order for chronological context
- Use `after` cursor for pagination
- Clear old threads periodically

**DON'T:**
- Don't load all items at once (memory issues)
- Don't use descending order for agent input (confuses model)
- Don't keep threads indefinitely (storage costs)

**Example:**
```python
# GOOD: Load recent history with reasonable limit
items_page = await self.store.load_thread_items(
    thread.id, after=None, limit=20, order="asc", context=context
)

# BAD: Load all items
items_page = await self.store.load_thread_items(
    thread.id, after=None, limit=999999, order="desc", context=context
)
```

### 11.3 Widget Design

**DO:**
- Use widgets for structured data collection
- Provide clear button labels
- Use appropriate color variants (primary, secondary, danger)
- Include helpful text descriptions
- Test widget rendering on mobile

**DON'T:**
- Don't overuse widgets (text is often better)
- Don't create complex nested layouts
- Don't use widgets for simple yes/no questions
- Don't forget accessibility (alt text, labels)

**Example:**
```python
# GOOD: Clear, simple widget
widget = Card(
    children=[
        Text(value="Confirm Deletion", weight="bold"),
        Text(value="Are you sure you want to delete this task?"),
        Row(
            children=[
                Button(label="Cancel", style="secondary"),
                Button(label="Delete", style="danger"),
            ]
        ),
    ]
)

# BAD: Overly complex widget
widget = Card(
    children=[
        Column(
            children=[
                Row(children=[...]),  # Nested layouts
                Column(children=[...]),
                Row(children=[...]),
            ]
        )
    ]
)
```

### 11.4 Error Handling

**DO:**
- Catch and handle tool execution errors
- Provide user-friendly error messages
- Log errors with context (user_id, thread_id)
- Implement retry logic for transient failures

**DON'T:**
- Don't expose internal errors to users
- Don't ignore tool execution failures
- Don't retry indefinitely
- Don't skip error logging

**Example:**
```python
# GOOD: Proper error handling
@function_tool
async def get_tasks():
    try:
        tasks = await db.query_tasks()
        return tasks
    except DatabaseError as e:
        logger.error(f"Failed to fetch tasks: {e}")
        return {"error": "Unable to fetch tasks. Please try again."}

# BAD: No error handling
@function_tool
async def get_tasks():
    tasks = await db.query_tasks()  # May raise exception
    return tasks
```

### 11.5 Performance Optimization

**DO:**
- Cache tool results when appropriate
- Use streaming for long responses
- Implement connection pooling for database
- Monitor token usage and costs
- Set reasonable timeouts

**DON'T:**
- Don't make unnecessary tool calls
- Don't load large datasets without pagination
- Don't use expensive models for simple tasks
- Don't skip performance monitoring

**Example:**
```python
# GOOD: Cached tool results
from functools import lru_cache

@lru_cache(maxsize=100)
async def get_workspace_config(workspace_id: str):
    return await db.load_workspace(workspace_id)

# BAD: Repeated database queries
async def get_workspace_config(workspace_id: str):
    return await db.load_workspace(workspace_id)  # Called every time
```

---

## 12. API Reference Quick Lookup

### 12.1 Core Classes

```python
# ChatKitServer
class MyChatKitServer(ChatKitServer[ContextType]):
    async def respond(self, thread, input_user_message, context) -> AsyncIterator[ThreadStreamEvent]
    async def action(self, thread, action, sender, context) -> AsyncIterator[ThreadStreamEvent]

# Store
class MyStore(Store[ContextType]):
    async def load_thread(self, thread_id, context) -> ThreadMetadata
    async def save_thread(self, thread, context) -> None
    async def load_thread_items(self, thread_id, after, limit, order, context) -> Page[ThreadItem]
    async def add_thread_item(self, thread_id, item, context) -> None
    # ... other methods

# AgentContext
agent_context = AgentContext(thread, store, request_context)
await agent_context.stream_widget(widget)
await agent_context.stream_text(text)

# Helpers
input_items = await simple_to_agent_input(thread_items)
async for event in stream_agent_response(agent_context, result):
    yield event
```

### 12.2 Common Patterns

```python
# Basic ChatKit server with Agents SDK
class MyChatKitServer(ChatKitServer[dict]):
    async def respond(self, thread, input_user_message, context):
        items_page = await self.store.load_thread_items(
            thread.id, after=None, limit=20, order="asc", context=context
        )
        input_items = await simple_to_agent_input(items_page.data)
        agent_context = AgentContext(thread=thread, store=self.store, request_context=context)
        result = Runner.run_streamed(assistant, input_items, context=agent_context)
        async for event in stream_agent_response(agent_context, result):
            yield event

# Widget with action
widget = Card(
    children=[
        Text(value="Title", weight="bold"),
        Button(label="Click", onClickAction=Action(type="button_click", data={}))
    ]
)

# Action handler
async def action(self, thread, action, sender, context):
    if action.type == "button_click":
        await agent_context.stream_text("Button clicked!")

# Server tool
@function_tool
async def my_tool(ctx: RunContextWrapper[AgentContext]):
    await ctx.context.stream_widget(widget)
    return "Tool executed"

# Client tool
@function_tool
async def client_tool(ctx: RunContextWrapper[AgentContext]):
    ctx.context.client_tool_call = ClientToolCall(name="get_selection", arguments={})
```

### 12.3 Type Signatures

```python
# Thread types
ThreadMetadata(id: str, created_at: datetime)
UserMessageItem(id, thread_id, created_at, content, attachments, quoted_text)
AssistantMessageItem(id, thread_id, created_at, content)
ToolCallItem(id, thread_id, created_at, name, arguments, output)
WidgetItem(id, thread_id, created_at, widget)

# Event types
ThreadItemDoneEvent(item: ThreadItem)
ThreadItemDeltaEvent(item_id: str, delta: dict)

# Widget types
Card(children, padding, background, asForm, confirmAction)
Text(value, weight, size, color, editable)
Button(label, style, onClickAction, submit, disabled)
Row(children, gap, align)
Column(children, gap, align)
Form(children, direction, onSubmitAction)

# Action type
Action(type: str, data: dict)
```

---

**Document Status**: ✅ COMPLETE - All phases appended (Overview, Core Integration, Store, Types, Agents SDK, Widgets, Tools, Actions, Examples, Migration, Best Practices, API Reference)
