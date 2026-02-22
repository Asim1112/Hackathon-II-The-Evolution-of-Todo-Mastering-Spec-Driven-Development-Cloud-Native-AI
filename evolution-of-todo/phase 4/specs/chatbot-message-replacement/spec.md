# Specification: ChatBot Message Replacement Bug Fix

## Metadata
- **Feature**: ChatBot Message Flow
- **Type**: Bug Fix
- **Priority**: Critical
- **Status**: In Progress
- **Date**: 2026-02-15

## Problem Statement

### Current Behavior
When having a conversation with the chatbot:
1. User sends: "show me all tasks"
2. Bot responds: "you don't have any task yet, if you want i can create"
3. User sends: "create task for groceries"
4. Bot REPLACES the previous response instead of appending a new message

### Expected Behavior
Each bot response should be a separate message in the chat history. The conversation should maintain a complete history of all exchanges with messages appending, not replacing.

### Impact
- **Severity**: Critical - conversation history is lost
- **Scope**: All chatbot interactions
- **User Experience**: Users cannot see previous responses, making multi-turn conversations confusing
- **Data Integrity**: Task creation works, but conversation flow is broken

## Root Cause Analysis

### Database Investigation
Query results show all assistant messages have the same ID:
```sql
SELECT id, item_id FROM message WHERE role = 'ASSISTANT'
-- All rows show: item_id = "__fake_id__"
```

### Technical Details

**The Problem Chain:**
1. Agents SDK generates response items with placeholder IDs (e.g., `"__fake_id__"`)
2. ChatKit's `stream_agent_response()` reuses these IDs when creating `AssistantMessageItem`
3. ChatKit calls `store.save_item()` to persist the message
4. Our `save_item()` method (store_adapter.py:306-322) tries to find existing message by `item.id`
5. It finds the FIRST message with `id="__fake_id__"` and UPDATES it
6. Frontend receives update event instead of new message event
7. Frontend replaces the old message instead of appending new one

**Code Path:**
```
Agents SDK → generates item with id="__fake_id__"
    ↓
ChatKit stream_agent_response() → creates AssistantMessageItem(id="__fake_id__")
    ↓
ChatKit → calls store.save_item(item)
    ↓
store_adapter.save_item() → finds existing message with id="__fake_id__"
    ↓
Updates existing message content (line 314)
    ↓
Frontend receives update, replaces message
```

### Why This Happens

**store_adapter.py:306-322 (save_item method):**
```python
async def save_item(self, thread_id: str, item, context: RequestContext) -> None:
    # Try to find by item.id if it looks like an int
    try:
        item_id_int = int(item.id)
        existing = session.get(Message, item_id_int)
        if existing and existing.conversation_id == conversation_id:
            existing.content = json.dumps(serialize_thread_item(item))
            session.add(existing)
            session.commit()
            return  # ← UPDATES instead of creating new
    except (ValueError, TypeError):
        pass  # ← "__fake_id__" fails int() conversion, falls through

    # If not found, add as new
    await self.add_thread_item(thread_id, item, context)
```

The issue: When `item.id` is not a valid integer (like `"__fake_id__"`), it falls through to `add_thread_item()`, which SHOULD create a new message. But there's a subtle bug - the method is being called in a way that causes updates.

Actually, looking more carefully - the `save_item()` method should work correctly because `"__fake_id__"` fails `int()` conversion and falls through to `add_thread_item()`. Let me investigate further...

## Requirements

### Functional Requirements
1. **FR-1**: Each assistant response must create a NEW message in the database
2. **FR-2**: Each message must have a UNIQUE ID
3. **FR-3**: Frontend must receive "message added" events, not "message updated" events
4. **FR-4**: Conversation history must be preserved across multiple turns
5. **FR-5**: Streaming updates within a single response should still work

### Non-Functional Requirements
1. **NFR-1**: No breaking changes to existing conversations
2. **NFR-2**: No performance degradation
3. **NFR-3**: Maintain compatibility with ChatKit SDK
4. **NFR-4**: Clear logging for debugging message flow

### Constraints
- Must work with Agents SDK's ID generation
- Must maintain ChatKit integration patterns
- Cannot modify ChatKit or Agents SDK libraries
- Must preserve streaming functionality

## Acceptance Criteria

### Success Criteria
- [ ] User sends "show me all tasks" → Bot responds
- [ ] User sends "create task for groceries" → Bot creates NEW message (not replace)
- [ ] Both messages visible in chat history
- [ ] Each message has unique ID in database
- [ ] No `__fake_id__` in database for new messages
- [ ] Streaming updates within single response still work

### Test Cases

#### TC-1: Multi-Turn Conversation
**Given**: User is on dashboard with chatbot
**When**: User sends 3 messages in sequence
**Then**:
- 3 user messages + 3 assistant messages = 6 total messages
- All messages visible in chat history
- No messages replaced

#### TC-2: Database Integrity
**Given**: Conversation with multiple exchanges
**When**: Query database for assistant messages
**Then**:
- Each message has unique ID
- No `__fake_id__` values
- All messages have correct conversation_id

#### TC-3: Streaming Still Works
**Given**: User asks question requiring tool calls
**When**: Bot streams response with tool execution
**Then**:
- Response streams progressively
- Final message is complete
- No duplicate messages created

## Out of Scope
- Fixing existing messages with `__fake_id__`
- Migrating historical conversation data
- Changing ChatKit SDK behavior
- Frontend UI changes

## Dependencies
- ChatKit store adapter implementation
- Agents SDK response item generation
- Database Message model
- Frontend ChatKit component

## Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Breaking streaming updates | High | Medium | Test streaming carefully |
| Duplicate messages created | Medium | Low | Add unique constraint checks |
| Frontend doesn't handle new events | High | Low | Verify event types |
| Performance impact | Low | Low | Minimal - just ID generation |

## References
- Database query showing `__fake_id__` pattern
- `backend/src/agents/store_adapter.py:306-322`
- ChatKit `stream_agent_response()` source
- Previous bug fix: chatbot-streaming-fix
