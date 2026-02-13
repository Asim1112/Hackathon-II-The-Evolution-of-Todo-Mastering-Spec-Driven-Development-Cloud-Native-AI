# Data Model: ChatKit Types ↔ Database Models

**Feature**: Migrate to Official OpenAI SDKs for Phase III Compliance
**Date**: 2026-02-11
**Purpose**: Document entity mappings and serialization strategy

## Overview

This document defines how ChatKit SDK types map to existing database models without requiring schema changes. The Store adapter pattern provides a clean abstraction layer.

## Entity Mappings

### ThreadMetadata ↔ Conversation

**ChatKit Type**:
```python
from chatkit.types import ThreadMetadata

ThreadMetadata(
    id: str,              # Unique thread identifier
    created_at: datetime  # Thread creation timestamp
)
```

**Existing Database Model** (UNCHANGED):
```python
from sqlmodel import SQLModel, Field
from datetime import datetime

class Conversation(SQLModel, table=True):
    __tablename__ = "conversation"

    id: str = Field(primary_key=True)
    user_id: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**Mapping Strategy**:
- `ThreadMetadata.id` → `Conversation.id` (direct mapping)
- `ThreadMetadata.created_at` → `Conversation.created_at` (direct mapping)
- `Conversation.user_id` → Stored in RequestContext (not in ThreadMetadata)

**Conversion Functions**:
```python
def conversation_to_thread_metadata(conversation: Conversation) -> ThreadMetadata:
    return ThreadMetadata(
        id=conversation.id,
        created_at=conversation.created_at
    )

def thread_metadata_to_conversation(thread: ThreadMetadata, user_id: str) -> Conversation:
    return Conversation(
        id=thread.id,
        user_id=user_id,
        created_at=thread.created_at
    )
```

### ThreadItem ↔ Message

**ChatKit Types** (Union of 3 types):

```python
from chatkit.types import UserMessageItem, AssistantMessageItem, ToolCallItem

# Type 1: User Message
UserMessageItem(
    id: str,
    thread_id: str,
    created_at: datetime,
    content: List[MessageContent],  # Text, images, etc.
    attachments: List[Attachment] = [],
    quoted_text: str | None = None
)

# Type 2: Assistant Message
AssistantMessageItem(
    id: str,
    thread_id: str,
    created_at: datetime,
    content: List[AssistantMessageContent]  # Text, tool calls
)

# Type 3: Tool Call Result
ToolCallItem(
    id: str,
    thread_id: str,
    created_at: datetime,
    name: str,           # Tool name
    arguments: dict,     # Tool arguments
    output: Any          # Tool result
)
```

**Existing Database Model** (UNCHANGED):
```python
class Message(SQLModel, table=True):
    __tablename__ = "message"

    id: str = Field(primary_key=True)
    conversation_id: str = Field(foreign_key="conversation.id", index=True)
    role: str  # "user", "assistant", "tool"
    content: str  # JSON-serialized ThreadItem
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**Mapping Strategy**:
- Store entire `ThreadItem` as JSON in `Message.content` field
- `ThreadItem.id` → `Message.id`
- `ThreadItem.thread_id` → `Message.conversation_id`
- `ThreadItem.created_at` → `Message.created_at`
- `ThreadItem` type → `Message.role` ("user", "assistant", "tool")

**Serialization Strategy**:

```python
from chatkit.types import ThreadItem
import json

def serialize_thread_item(item: ThreadItem) -> Message:
    """Convert ThreadItem to Message (for database storage)."""
    # Determine role from item type
    if isinstance(item, UserMessageItem):
        role = "user"
    elif isinstance(item, AssistantMessageItem):
        role = "assistant"
    elif isinstance(item, ToolCallItem):
        role = "tool"
    else:
        raise ValueError(f"Unknown ThreadItem type: {type(item)}")

    # Serialize to JSON
    content_json = item.model_dump_json()

    return Message(
        id=item.id,
        conversation_id=item.thread_id,
        role=role,
        content=content_json,
        created_at=item.created_at
    )

def deserialize_thread_item(message: Message) -> ThreadItem:
    """Convert Message to ThreadItem (from database)."""
    # Parse JSON
    data = json.loads(message.content)

    # Determine type from role
    if message.role == "user":
        return UserMessageItem.model_validate(data)
    elif message.role == "assistant":
        return AssistantMessageItem.model_validate(data)
    elif message.role == "tool":
        return ToolCallItem.model_validate(data)
    else:
        raise ValueError(f"Unknown message role: {message.role}")
```

**Benefits**:
- ✅ Zero schema changes (uses existing `content` TEXT field)
- ✅ Preserves all ThreadItem fields (attachments, quoted_text, tool arguments)
- ✅ Type-safe with Pydantic validation
- ✅ Supports all ThreadItem types
- ✅ Easy to add new ThreadItem types in future

## Store Adapter Interface

### RequestContext

**Purpose**: Carry request-specific data (user_id) for multi-tenancy isolation.

```python
from dataclasses import dataclass

@dataclass
class RequestContext:
    user_id: str  # For WHERE user_id = ? filtering
```

**Usage**:
```python
context = RequestContext(user_id="user_123")
thread = await store.load_thread("thread_456", context)
# Query: SELECT * FROM conversation WHERE id = 'thread_456' AND user_id = 'user_123'
```

### Store Methods (13 total)

#### Thread Operations

**1. load_thread(thread_id, context) → ThreadMetadata**
```python
async def load_thread(self, thread_id: str, context: RequestContext) -> ThreadMetadata:
    """Load thread metadata by ID."""
    # Query: SELECT * FROM conversation WHERE id = ? AND user_id = ?
    conversation = db.query(Conversation).filter_by(
        id=thread_id,
        user_id=context.user_id
    ).first()

    if not conversation:
        raise NotFoundError(f"Thread {thread_id} not found")

    return conversation_to_thread_metadata(conversation)
```

**2. save_thread(thread, context) → None**
```python
async def save_thread(self, thread: ThreadMetadata, context: RequestContext) -> None:
    """Save or update thread metadata."""
    # INSERT or UPDATE conversation
    conversation = thread_metadata_to_conversation(thread, context.user_id)
    db.merge(conversation)
    db.commit()
```

**3. load_threads(limit, after, order, context) → Page[ThreadMetadata]**
```python
async def load_threads(
    self, limit: int, after: str | None, order: str, context: RequestContext
) -> Page[ThreadMetadata]:
    """Load threads with pagination."""
    # Query: SELECT * FROM conversation WHERE user_id = ?
    #        AND created_at > (SELECT created_at FROM conversation WHERE id = ?)
    #        ORDER BY created_at DESC LIMIT ?
    pass
```

**4. delete_thread(thread_id, context) → None**
```python
async def delete_thread(self, thread_id: str, context: RequestContext) -> None:
    """Delete thread and all its items."""
    # DELETE FROM conversation WHERE id = ? AND user_id = ?
    # CASCADE deletes messages automatically (foreign key)
    pass
```

#### Thread Item Operations

**5. load_thread_items(thread_id, after, limit, order, context) → Page[ThreadItem]**
```python
async def load_thread_items(
    self, thread_id: str, after: str | None, limit: int, order: str, context: RequestContext
) -> Page[ThreadItem]:
    """Load thread items with cursor-based pagination."""
    # Query: SELECT * FROM message WHERE conversation_id = ?
    #        AND created_at > (SELECT created_at FROM message WHERE id = ?)
    #        ORDER BY created_at ASC LIMIT ?

    # Deserialize each message to ThreadItem
    messages = db.query(Message).filter_by(conversation_id=thread_id)

    if after:
        cursor_time = db.query(Message.created_at).filter_by(id=after).scalar()
        messages = messages.filter(Message.created_at > cursor_time)

    if order == "asc":
        messages = messages.order_by(Message.created_at.asc())
    else:
        messages = messages.order_by(Message.created_at.desc())

    messages = messages.limit(limit).all()

    # Deserialize
    items = [deserialize_thread_item(msg) for msg in messages]

    return Page(data=items, has_more=len(items) == limit)
```

**6. add_thread_item(thread_id, item, context) → None**
```python
async def add_thread_item(
    self, thread_id: str, item: ThreadItem, context: RequestContext
) -> None:
    """Add new item to thread."""
    # INSERT INTO message
    message = serialize_thread_item(item)
    db.add(message)
    db.commit()
```

**7. save_item(thread_id, item, context) → None**
```python
async def save_item(
    self, thread_id: str, item: ThreadItem, context: RequestContext
) -> None:
    """Update existing item."""
    # UPDATE message SET content = ? WHERE id = ?
    message = serialize_thread_item(item)
    db.merge(message)
    db.commit()
```

**8. load_item(thread_id, item_id, context) → ThreadItem**
```python
async def load_item(
    self, thread_id: str, item_id: str, context: RequestContext
) -> ThreadItem:
    """Load single item by ID."""
    # Query: SELECT * FROM message WHERE id = ? AND conversation_id = ?
    message = db.query(Message).filter_by(
        id=item_id,
        conversation_id=thread_id
    ).first()

    if not message:
        raise NotFoundError(f"Item {item_id} not found")

    return deserialize_thread_item(message)
```

**9. delete_thread_item(thread_id, item_id, context) → None**
```python
async def delete_thread_item(
    self, thread_id: str, item_id: str, context: RequestContext
) -> None:
    """Delete single item."""
    # DELETE FROM message WHERE id = ? AND conversation_id = ?
    db.query(Message).filter_by(
        id=item_id,
        conversation_id=thread_id
    ).delete()
    db.commit()
```

#### Attachment Operations (Stub Implementation)

**10. save_attachment(attachment, context) → None**
**11. load_attachment(attachment_id, context) → Attachment**
**12. delete_attachment(attachment_id, context) → None**

```python
# Not implemented in Phase III (no attachment support yet)
# Return empty/no-op for now
async def save_attachment(self, attachment, context):
    pass  # No-op

async def load_attachment(self, attachment_id, context):
    raise NotFoundError("Attachments not supported")

async def delete_attachment(self, attachment_id, context):
    pass  # No-op
```

#### ID Generation

**13. generate_item_id(item_type, thread, context) → str**
```python
async def generate_item_id(
    self, item_type: str, thread: ThreadMetadata, context: RequestContext
) -> str:
    """Generate unique ID for new item."""
    import uuid
    return f"{item_type}_{uuid.uuid4().hex[:12]}"
```

## Pagination Details

### Cursor-Based Pagination

**Why cursor-based?**
- ✅ Efficient at any page depth (no OFFSET)
- ✅ Consistent results even with concurrent inserts
- ✅ Recommended by ChatKit documentation

**How it works**:
1. Client requests first page: `after=None, limit=20`
2. Server returns 20 items + `has_more=True`
3. Client requests next page: `after=last_item_id, limit=20`
4. Server queries items with `created_at > cursor_time`

**Implementation**:
```sql
-- First page (after=None)
SELECT * FROM message
WHERE conversation_id = 'thread_123'
ORDER BY created_at ASC
LIMIT 20;

-- Next page (after='msg_xyz')
SELECT * FROM message
WHERE conversation_id = 'thread_123'
AND created_at > (SELECT created_at FROM message WHERE id = 'msg_xyz')
ORDER BY created_at ASC
LIMIT 20;
```

## Database Schema (UNCHANGED)

**No schema changes required**. Existing schema supports all ChatKit operations:

```sql
-- Existing schema (PRESERVED)
CREATE TABLE conversation (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id)
);

CREATE TABLE message (
    id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL,
    role TEXT NOT NULL,  -- 'user', 'assistant', 'tool'
    content TEXT NOT NULL,  -- JSON-serialized ThreadItem
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversation(id) ON DELETE CASCADE,
    INDEX idx_conversation_created (conversation_id, created_at)
);
```

**Key Points**:
- `content` TEXT field stores JSON (no size limit in PostgreSQL)
- `role` field distinguishes ThreadItem types
- Foreign key CASCADE deletes messages when conversation deleted
- Indexes support efficient queries (user_id, conversation_id + created_at)

## Summary

| Aspect | Strategy |
|--------|----------|
| ThreadMetadata | Direct mapping to Conversation model |
| ThreadItem | JSON serialization in Message.content |
| User Isolation | RequestContext.user_id in WHERE clauses |
| Pagination | Cursor-based with created_at + id |
| Schema Changes | Zero (adapter pattern preserves schema) |
| Type Safety | Pydantic validation on serialization/deserialization |

This data model design achieves 100% functional parity with zero schema changes.
