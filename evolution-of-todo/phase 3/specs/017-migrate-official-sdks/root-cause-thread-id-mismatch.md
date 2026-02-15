# Bug Root Cause: Thread ID Type Mismatch

**Date**: 2026-02-11
**Bug**: BUG-002 (Agent Not Responding)
**Root Cause**: Store adapter cannot convert ChatKit string thread IDs to integer Conversation IDs
**Status**: Solution identified

## Error Analysis

### Backend Error
```
ValueError: invalid literal for int() with base 10: 'thread_af04060baaba'

File "backend/src/agents/store_adapter.py", line 152, in save_thread
    Conversation.id == int(thread.id),
                       ^^^^^^^^^^^^^^
```

### Root Cause

**ChatKit generates string thread IDs**: `'thread_af04060baaba'`
**Our database uses integer IDs**: `Conversation.id` is `int` (auto-increment)

**Store adapter line 152** tries to convert thread.id to int:
```python
Conversation.id == int(thread.id)  # FAILS when thread.id = 'thread_af04060baaba'
```

### Spec Violation

**FR-015**: System MUST support the same conversation flows (ChatKit thread_id maps to existing conversation_id)

**Current State**: Store adapter fails to map ChatKit thread IDs to Conversation IDs

**SC-008**: Zero modifications to database models (Store interface adapts to existing schema)

**Current State**: Adapter doesn't properly adapt ChatKit's string IDs to our integer schema

## Architecture Mismatch

**ChatKit Behavior**:
- Frontend config: `initialThread: userId` (string)
- ChatKit may generate new thread IDs: `'thread_<random>'` (string)
- All thread IDs are strings

**Our Database**:
- `Conversation.id` is `int` (auto-increment primary key)
- Cannot store string IDs like `'thread_af04060baaba'`

## Solution Design

The store adapter must handle two cases:

### Case 1: Numeric String (Existing Conversation)
```python
thread.id = "123"  # Our existing conversation ID as string
→ Convert to int(123) and query database
```

### Case 2: ChatKit-Generated String (New Thread)
```python
thread.id = "thread_af04060baaba"  # ChatKit generated
→ Create new Conversation, return its integer ID
→ Store mapping: ChatKit thread ID → Conversation ID
```

### Case 3: User ID as Thread ID (Initial Thread)
```python
thread.id = "zPM4ZZzcmxCCB2cWJ15FD8MFBuXSMWvJ"  # userId
→ Find or create conversation for this user
→ Use user's existing conversation or create new one
```

## Proposed Fix

**File**: `backend/src/agents/store_adapter.py`

**Method**: `save_thread()` (line 152)

**Change**: Add thread ID parsing logic before conversion:

```python
def _parse_thread_id(self, thread_id: str, user_id: str) -> int:
    """
    Parse ChatKit thread ID to database Conversation ID.

    Handles:
    - Numeric strings: "123" → 123
    - User ID: "user_xxx" → find/create conversation for user
    - ChatKit generated: "thread_xxx" → create new conversation
    """
    # Try numeric conversion first (existing conversation)
    try:
        return int(thread_id)
    except ValueError:
        pass

    # If thread_id is user_id, find or create conversation
    with Session(self._get_engine()) as session:
        # Check if conversation exists for this user
        stmt = select(Conversation).where(
            Conversation.user_id == user_id
        ).order_by(Conversation.created_at.desc()).limit(1)

        existing = session.exec(stmt).first()
        if existing:
            return existing.id

        # Create new conversation
        new_conv = Conversation(user_id=user_id)
        session.add(new_conv)
        session.commit()
        session.refresh(new_conv)
        return new_conv.id
```

**Then update save_thread**:
```python
async def save_thread(self, thread: ThreadMetadata, context: RequestContext) -> None:
    conversation_id = self._parse_thread_id(thread.id, context.user_id)

    with Session(self._get_engine()) as session:
        stmt = select(Conversation).where(
            Conversation.id == conversation_id,  # Use parsed ID
            Conversation.user_id == context.user_id,
        )
        # ... rest of method
```

## Verification Steps

After fix:
1. ✅ ChatKit sends message with thread_id = userId
2. ✅ Store adapter finds/creates conversation
3. ✅ Agent processes message
4. ✅ Response streams back to frontend
5. ✅ No ValueError

## Next Steps (SDD)

1. ✅ Document root cause (this file)
2. → Implement _parse_thread_id helper
3. → Update save_thread to use helper
4. → Update load_thread to use helper
5. → Test with ChatKit UI
6. → Verify agent responds
