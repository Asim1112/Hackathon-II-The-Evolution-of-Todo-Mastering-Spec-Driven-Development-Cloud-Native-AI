# Tasks: ChatBot Message Replacement Bug Fix

## Metadata
- **Feature**: ChatBot Message Flow
- **Type**: Bug Fix
- **Date**: 2026-02-15
- **Status**: In Progress

## Task List

### Task 1: Add Unique ID Generation for Assistant Messages
**Status**: ⏳ Pending
**Priority**: Critical
**Estimated Effort**: 15 minutes
**Dependencies**: None

**Description**:
Modify `add_thread_item()` to detect assistant messages with non-unique IDs (like `__fake_id__`) and replace them with unique IDs before saving to database.

**Location**: `backend/src/agents/store_adapter.py:278-305`

**Implementation**:
```python
async def add_thread_item(self, thread_id: str, item, context: RequestContext) -> None:
    conversation_id = self._parse_thread_id(thread_id, context.user_id)

    item_id = getattr(item, "id", "no-id")
    item_type = getattr(item, "type", "unknown")

    # [NEW] Generate unique ID for assistant messages with placeholder IDs
    if item_type == "assistant_message":
        if item_id in ("__fake_id__", "no-id", "") or item_id.startswith("__"):
            thread_meta = ThreadMetadata(
                id=thread_id,
                created_at=datetime.now(timezone.utc)
            )
            unique_id = self.generate_item_id("message", thread_meta, context)
            item.id = unique_id
            item_id = unique_id
            logger.info(f"[STORE] Generated unique ID for assistant message: {unique_id}")

    logger.info(f"[STORE] Saving item: id={item_id}, type={item_type}, thread={thread_id}")

    # [UNCHANGED] Rest of method
    with Session(self._get_engine()) as session:
        if item_type == "user_message":
            role = MessageRole.USER
        else:
            role = MessageRole.ASSISTANT

        message = Message(
            conversation_id=conversation_id,
            user_id=context.user_id,
            role=role,
            content=json.dumps(serialize_thread_item(item)),
            created_at=datetime.utcnow(),
        )
        session.add(message)
        session.commit()
        session.refresh(message)

        logger.info(f"[STORE] Saved to DB: message.id={message.id}, item.id={item_id}")
```

**Acceptance Criteria**:
- [ ] Assistant messages with `__fake_id__` get unique IDs
- [ ] User messages keep their original IDs
- [ ] Unique IDs follow format: `message_{12_char_hex}`
- [ ] Logging shows ID generation
- [ ] No errors during ID generation

**Test Cases**:
- TC1.1: Assistant message with `__fake_id__` → Gets unique ID
- TC1.2: Assistant message with `no-id` → Gets unique ID
- TC1.3: User message with existing ID → Keeps original ID
- TC1.4: Generated IDs are unique across multiple messages

---

### Task 2: Add Required Import for datetime.timezone
**Status**: ⏳ Pending
**Priority**: Critical
**Estimated Effort**: 2 minutes
**Dependencies**: Task 1

**Description**:
Add `timezone` import from datetime module to support `datetime.now(timezone.utc)` call.

**Location**: `backend/src/agents/store_adapter.py:14`

**Implementation**:
```python
from datetime import datetime, timezone
```

**Acceptance Criteria**:
- [ ] Import statement added
- [ ] No import errors
- [ ] Code uses `timezone.utc` correctly

**Test Cases**:
- TC2.1: Backend starts without import errors
- TC2.2: `datetime.now(timezone.utc)` executes successfully

---

### Task 3: Restart Backend and Verify Startup
**Status**: ⏳ Pending
**Priority**: Critical
**Estimated Effort**: 3 minutes
**Dependencies**: Tasks 1, 2

**Description**:
Restart the backend server and verify it starts without errors and the changes are loaded.

**Steps**:
1. Stop backend server (Ctrl+C)
2. Start backend: `uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload`
3. Check logs for successful startup
4. Verify no import or syntax errors

**Acceptance Criteria**:
- [ ] Backend starts without errors
- [ ] No Python syntax errors
- [ ] All imports resolve correctly
- [ ] Database connection successful
- [ ] ChatKit session manager starts

**Test Cases**:
- TC3.1: Server starts successfully
- TC3.2: No import errors in logs
- TC3.3: Health check endpoint responds

---

### Task 4: Test Multi-Turn Conversation
**Status**: ⏳ Pending
**Priority**: Critical
**Estimated Effort**: 10 minutes
**Dependencies**: Task 3

**Description**:
Test that multiple assistant messages create separate messages instead of replacing each other.

**Steps**:
1. Open http://localhost:3000/dashboard
2. Send message: "show me all tasks"
3. Wait for response
4. Send message: "create task for groceries"
5. Wait for response
6. Send message: "list all tasks"
7. Verify all 6 messages visible (3 user + 3 assistant)

**Acceptance Criteria**:
- [ ] First message: Bot responds to "show me all tasks"
- [ ] Second message: Bot creates task and responds
- [ ] Third message: Bot lists tasks including new one
- [ ] All 3 assistant messages visible in chat
- [ ] No messages replaced
- [ ] Backend logs show unique ID generation

**Test Cases**:
- TC4.1: Send 3 messages → 6 total messages visible
- TC4.2: Each assistant message has different content
- TC4.3: Chat history preserved
- TC4.4: No errors in browser console or backend

**Expected Backend Logs**:
```
[STORE] Generated unique ID for assistant message: message_abc123def456
[STORE] Saving item: id=message_abc123def456, type=assistant_message
[STORE] Saved to DB: message.id=203, item.id=message_abc123def456
```

---

### Task 5: Verify Database Integrity
**Status**: ⏳ Pending
**Priority**: High
**Estimated Effort**: 5 minutes
**Dependencies**: Task 4

**Description**:
Query the database to verify that new assistant messages have unique IDs and no `__fake_id__` values.

**Steps**:
1. Run database query to check recent assistant messages
2. Verify each has unique ID
3. Verify no `__fake_id__` in new messages
4. Verify ID format matches `message_{hex}`

**SQL Query**:
```sql
SELECT id,
       substring(content::text from '"id":\s*"([^"]+)"') as item_id,
       substring(content::text from '"text":\s*"([^"]+)"') as text_preview,
       created_at
FROM message
WHERE conversation_id = 36 AND role = 'ASSISTANT'
ORDER BY created_at DESC
LIMIT 5;
```

**Acceptance Criteria**:
- [ ] All new messages have unique IDs
- [ ] No `__fake_id__` in new messages
- [ ] ID format: `message_{12_char_hex}`
- [ ] Old messages still have `__fake_id__` (unchanged)

**Test Cases**:
- TC5.1: Query returns 5 messages
- TC5.2: Latest 3 messages have unique IDs
- TC5.3: No two messages share the same item_id
- TC5.4: ID format is correct

---

### Task 6: Test Streaming Functionality
**Status**: ⏳ Pending
**Priority**: High
**Estimated Effort**: 5 minutes
**Dependencies**: Task 4

**Description**:
Verify that streaming updates within a single response still work correctly and don't create duplicate messages.

**Steps**:
1. Send message: "add 3 tasks: groceries, laundry, homework"
2. Observe streaming response
3. Verify single assistant message created
4. Verify all 3 tasks created successfully

**Acceptance Criteria**:
- [ ] Response streams progressively
- [ ] Only ONE assistant message created
- [ ] Message shows all 3 tasks created
- [ ] No duplicate messages
- [ ] Tool calls execute correctly

**Test Cases**:
- TC6.1: Streaming updates visible during response
- TC6.2: Final message is complete
- TC6.3: Only 1 assistant message in chat
- TC6.4: All 3 tasks created in database

---

### Task 7: Test Tool Calling
**Status**: ⏳ Pending
**Priority**: Medium
**Estimated Effort**: 5 minutes
**Dependencies**: Task 4

**Description**:
Test that tool calling works correctly with unique message IDs.

**Steps**:
1. Send: "list my tasks"
2. Verify tool is called
3. Send: "complete the first task"
4. Verify tool is called and task updated
5. Verify both responses are separate messages

**Acceptance Criteria**:
- [ ] "list my tasks" calls list_tasks tool
- [ ] "complete task" calls complete_task tool
- [ ] Both responses create separate messages
- [ ] Tool results included in responses
- [ ] No errors in logs

**Test Cases**:
- TC7.1: List tasks → Tool called, results shown
- TC7.2: Complete task → Tool called, task updated
- TC7.3: Both messages visible in chat
- TC7.4: No message replacement

---

### Task 8: Test Edge Cases
**Status**: ⏳ Pending
**Priority**: Medium
**Estimated Effort**: 5 minutes
**Dependencies**: Task 4

**Description**:
Test edge cases to ensure robustness.

**Steps**:
1. Send very long message
2. Send message with special characters
3. Send rapid sequence of messages
4. Verify all handled correctly

**Acceptance Criteria**:
- [ ] Long messages handled correctly
- [ ] Special characters don't break ID generation
- [ ] Rapid messages all get unique IDs
- [ ] No race conditions or ID collisions

**Test Cases**:
- TC8.1: Long message → Unique ID generated
- TC8.2: Special chars → Unique ID generated
- TC8.3: 5 rapid messages → 5 unique IDs

---

### Task 9: Create Prompt History Record (PHR)
**Status**: ⏳ Pending
**Priority**: High
**Estimated Effort**: 10 minutes
**Dependencies**: Tasks 1-8

**Description**:
Document this debugging session as a PHR following the SDD framework requirements.

**Location**: `history/prompts/chatbot-message-replacement/`

**Content Requirements**:
- Full user prompt (error description)
- Root cause analysis
- Solution approach
- Code changes made
- Testing results
- Lessons learned

**Acceptance Criteria**:
- [ ] PHR created in correct directory
- [ ] All required fields filled
- [ ] User prompt captured verbatim
- [ ] Solution documented clearly
- [ ] Links to spec.md and plan.md included
- [ ] Testing results documented

---

## Summary

**Total Tasks**: 9
**Completed**: 0
**Pending**: 9
**Blocked**: 0

**Critical Path**: Tasks 1 → 2 → 3 → 4 → 5 → 9

**Next Actions**:
1. Implement ID generation in `add_thread_item()` (Task 1)
2. Add timezone import (Task 2)
3. Restart backend (Task 3)
4. Test multi-turn conversation (Task 4)
5. Verify database (Task 5)
6. Create PHR (Task 9)

**Risk Assessment**:
- **Low Risk**: Core fix is straightforward
- **Medium Risk**: Need to verify streaming still works
- **Low Risk**: Performance impact is negligible

**Rollback Plan**:
If any task fails, revert `store_adapter.py`:
```bash
git checkout HEAD -- backend/src/agents/store_adapter.py
```
