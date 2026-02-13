# Data Model Design

**Feature**: AI-Powered Todo Chatbot (016-ai-chatbot)
**Date**: 2026-02-10
**Purpose**: Define database schema for conversation and message storage

## Overview

This document defines two new database models for Phase 3: **Conversation** and **Message**. These models enable stateless conversation management with database-persisted chat history. All models follow SQLModel patterns established in Phase 2.

## Entity Relationship Diagram

```
User (Phase 2)
  |
  |-- 1:N --> Task (Phase 2)
  |
  |-- 1:N --> Conversation (NEW)
                |
                |-- 1:N --> Message (NEW)
```

## Model Definitions

### Conversation Model

**Purpose**: Represents a chat session between a user and the AI assistant.

**File**: `backend/src/models/conversation.py`

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List

class Conversation(SQLModel, table=True):
    """
    Conversation model for chat sessions.

    Each user can have multiple conversations.
    Conversations persist across sessions and server restarts.
    """
    __tablename__ = "conversation"

    # Primary Key
    id: Optional[int] = Field(default=None, primary_key=True)

    # Foreign Keys
    user_id: str = Field(foreign_key="user.id", index=True, nullable=False)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        nullable=False
    )

    # Relationships
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "user_123",
                "created_at": "2026-02-10T10:00:00Z",
                "updated_at": "2026-02-10T10:30:00Z"
            }
        }
```

**Indexes**:
- `ix_conversation_user_id`: Single-column index on `user_id` for user's conversation list
- `ix_conversation_user_created`: Composite index on `(user_id, created_at DESC)` for recent conversations

**Constraints**:
- `user_id` must reference existing User (foreign key constraint)
- Cascade delete: Deleting conversation deletes all associated messages

**Validation Rules**:
- `user_id` cannot be null or empty
- `created_at` and `updated_at` are auto-managed

---

### Message Model

**Purpose**: Represents a single message in a conversation (user or assistant).

**File**: `backend/src/models/message.py`

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, Literal
from enum import Enum

class MessageRole(str, Enum):
    """Message role enumeration"""
    USER = "user"
    ASSISTANT = "assistant"

class Message(SQLModel, table=True):
    """
    Message model for chat messages.

    Each message belongs to a conversation and has a role (user or assistant).
    Messages are immutable once created.
    """
    __tablename__ = "message"

    # Primary Key
    id: Optional[int] = Field(default=None, primary_key=True)

    # Foreign Keys
    conversation_id: int = Field(
        foreign_key="conversation.id",
        index=True,
        nullable=False
    )
    user_id: str = Field(
        foreign_key="user.id",
        index=True,
        nullable=False
    )  # Denormalized for query optimization

    # Message Data
    role: MessageRole = Field(nullable=False)
    content: str = Field(sa_column_kwargs={"type_": "Text"}, nullable=False)

    # Timestamp
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    conversation: Optional["Conversation"] = Relationship(back_populates="messages")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "conversation_id": 1,
                "user_id": "user_123",
                "role": "user",
                "content": "Add a task to buy groceries",
                "created_at": "2026-02-10T10:00:00Z"
            }
        }
```

**Indexes**:
- `ix_message_conversation_id`: Single-column index on `conversation_id` for conversation history
- `ix_message_conversation_created`: Composite index on `(conversation_id, created_at ASC)` for chronological message retrieval
- `ix_message_user_created`: Composite index on `(user_id, created_at DESC)` for user's recent messages

**Constraints**:
- `conversation_id` must reference existing Conversation (foreign key constraint)
- `user_id` must reference existing User (foreign key constraint)
- `role` must be either "user" or "assistant" (check constraint)
- `content` cannot be null or empty
- Cascade delete: Deleting conversation deletes all messages

**Validation Rules**:
- `conversation_id` and `user_id` cannot be null
- `user_id` must match `conversation.user_id` (enforced in service layer)
- `role` must be valid MessageRole enum value
- `content` must be non-empty string (max length: unlimited for Text type)
- Messages are immutable (no updates after creation)

---

## Data Integrity Rules

### User Isolation
- All queries MUST filter by `user_id`
- Users can only access their own conversations and messages
- Service layer enforces user_id matching between conversation and messages

### Atomic Operations
- User message + assistant message stored together (atomic transaction)
- If either fails, both are rolled back
- Prevents partial conversation state

### Cascade Behavior
- Deleting User → deletes all Conversations → deletes all Messages
- Deleting Conversation → deletes all Messages
- No orphaned messages possible

### Idempotency
- Conversation creation is idempotent (fetch if exists, create if not)
- Message creation is NOT idempotent (each message is unique)

---

## Query Patterns

### Common Queries

#### 1. Get User's Conversations (Recent First)
```python
statement = (
    select(Conversation)
    .where(Conversation.user_id == user_id)
    .order_by(Conversation.created_at.desc())
    .limit(20)
)
conversations = session.exec(statement).all()
```
**Index Used**: `ix_conversation_user_created`

---

#### 2. Get Conversation History (Chronological)
```python
statement = (
    select(Message)
    .where(Message.conversation_id == conversation_id)
    .where(Message.user_id == user_id)  # User isolation
    .order_by(Message.created_at.asc())
    .limit(100)
)
messages = session.exec(statement).all()
```
**Index Used**: `ix_message_conversation_created`

---

#### 3. Get or Create Conversation
```python
if conversation_id:
    # Fetch existing
    conversation = session.get(Conversation, conversation_id)
    if not conversation or conversation.user_id != user_id:
        raise ValueError("Conversation not found or unauthorized")
else:
    # Create new
    conversation = Conversation(user_id=user_id)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
```

---

#### 4. Store Messages Atomically
```python
try:
    user_msg = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role=MessageRole.USER,
        content=user_message
    )
    assistant_msg = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role=MessageRole.ASSISTANT,
        content=assistant_message
    )

    session.add(user_msg)
    session.add(assistant_msg)
    session.commit()
except Exception:
    session.rollback()
    raise
```

---

## Performance Considerations

### Index Strategy
- **Conversation queries**: Indexed on `(user_id, created_at DESC)` for recent conversations
- **Message queries**: Indexed on `(conversation_id, created_at ASC)` for chronological history
- **User isolation**: Both tables indexed on `user_id` for efficient filtering

### Query Optimization
- Limit conversation history to 100 messages (pagination for longer histories)
- Use `select()` with explicit columns to avoid loading unnecessary data
- Leverage relationship loading strategies (lazy vs eager) based on use case

### Denormalization
- `user_id` denormalized in Message table for efficient user-based queries
- Trade-off: Slight storage overhead for significant query performance gain

---

## Migration Strategy

### Migration File
**File**: `backend/alembic/versions/xxx_add_conversation_models.py`

**Operations**:
1. Create `conversation` table with indexes
2. Create `message` table with indexes and check constraint
3. Add foreign key constraints
4. No changes to existing tables (additive only)

**Rollback**:
1. Drop `message` table (must be first due to foreign key)
2. Drop `conversation` table

**Testing**:
1. Apply migration to development database
2. Verify existing Phase 2 functionality (tasks CRUD)
3. Test new conversation/message operations
4. Test rollback
5. Apply to production

---

## State Transitions

### Conversation States
- **Created**: New conversation with no messages
- **Active**: Conversation with at least one message
- **Archived**: (Future enhancement) Conversation marked as archived

**Note**: For MVP, no explicit state field. State is implicit based on message count.

### Message States
- **Created**: Message is created and immutable
- No state transitions (messages are immutable)

---

## Validation Examples

### Valid Operations
```python
# Create conversation
conv = Conversation(user_id="user_123")
session.add(conv)
session.commit()

# Add messages
msg1 = Message(
    conversation_id=conv.id,
    user_id="user_123",
    role=MessageRole.USER,
    content="Hello"
)
msg2 = Message(
    conversation_id=conv.id,
    user_id="user_123",
    role=MessageRole.ASSISTANT,
    content="Hi! How can I help?"
)
session.add_all([msg1, msg2])
session.commit()
```

### Invalid Operations (Will Fail)
```python
# Missing user_id
conv = Conversation()  # ❌ user_id required

# Invalid role
msg = Message(
    conversation_id=1,
    user_id="user_123",
    role="invalid",  # ❌ Must be "user" or "assistant"
    content="Hello"
)

# Mismatched user_id (enforced in service layer)
msg = Message(
    conversation_id=1,  # Belongs to user_123
    user_id="user_456",  # ❌ Different user
    role=MessageRole.USER,
    content="Hello"
)
```

---

## Future Enhancements

### Potential Additions (Post-MVP)
- **Conversation metadata**: Title, tags, archived status
- **Message metadata**: Tool calls, attachments, reactions
- **Soft delete**: Archive instead of hard delete
- **Message editing**: Track edit history
- **Conversation sharing**: Multi-user conversations
- **Search**: Full-text search on message content

### Schema Evolution
All future changes will follow additive-only pattern to maintain backward compatibility.

---

## Summary

**New Tables**: 2 (Conversation, Message)
**New Indexes**: 6 (3 per table)
**Foreign Keys**: 3 (Conversation→User, Message→Conversation, Message→User)
**Constraints**: 1 check constraint (Message.role)
**Impact on Phase 2**: None (additive only)

**Status**: ✅ Data model design complete - Ready for implementation
