# Message ID Collision Fix Specification

## Problem Statement

New bot responses were appending to previous bot responses in the ChatKit UI instead of appearing as separate messages. This caused conversation history to become corrupted, with multiple assistant responses merged into a single message bubble.

**Evidence:**
- User reports: "New bot responses are being APPENDED to previous bot responses"
- ChatKit React frontend was treating new responses as updates to existing messages
- Multiple conversation turns appeared as a single message

**Root Cause:**
The `OpenAIChatCompletionsModel` (used for Cerebras backend) generates synthetic Responses API item IDs using `FAKE_RESPONSES_ID = "__fake_id__"` for all items. When the ChatKit React frontend receives a `ThreadItemUpdatedEvent` with an `item_id` that already exists in its state from a previous response, it appends the new text to the previous message instead of creating a new message.

**Technical Details:**
- Cerebras backend uses Chat Completions API (not native Responses API)
- Agents SDK converts Chat Completions to Responses API format
- Conversion uses placeholder ID `"__fake_id__"` for all synthetic items
- ChatKit React matches items by ID for state management
- ID collision causes message contamination

## Requirements

### Functional Requirements
1. **Unique Message IDs**: Each assistant message must have a globally unique ID
2. **Message Separation**: New responses must appear as separate messages in the UI
3. **State Consistency**: ChatKit React state must correctly track individual messages
4. **Backward Compatibility**: Existing message history must remain intact

### Non-Functional Requirements
1. **Performance**: ID generation must not impact streaming latency
2. **Reliability**: ID uniqueness must be guaranteed across all sessions
3. **Maintainability**: Solution must work with future Agents SDK updates

## Solution Approach

### Architecture
Implement an ID remapping layer in the `TodoChatKitServer.respond()` method that intercepts streaming events and replaces synthetic IDs with guaranteed-unique UUIDs.

### ID Remapping Pattern
1. **Intercept** `ThreadItemAddedEvent` for assistant messages
2. **Generate** unique ID using `store.generate_item_id("message", thread, context)`
3. **Map** old ID to new ID in tracking dictionary
4. **Replace** ID in the event item
5. **Remap** subsequent events (`ThreadItemUpdatedEvent`, `ThreadItemDoneEvent`) using the mapping

### Components
- `TodoChatKitServer.respond()`: Main streaming method
- `id_remap` dictionary: Tracks old ID → new ID mappings
- `store.generate_item_id()`: UUID generation utility

### Data Flow
```
1. Agents SDK generates response with FAKE_RESPONSES_ID
2. stream_agent_response() yields ThreadItemAddedEvent
3. ID remapping layer intercepts event
4. Replace item.id with unique UUID
5. Store mapping in id_remap dict
6. Yield modified event to ChatKit
7. Subsequent events use id_remap for consistency
```

## Acceptance Criteria
- [ ] Each assistant message has a unique ID
- [ ] New responses appear as separate messages in UI
- [ ] No message contamination occurs
- [ ] Existing functionality remains intact
- [ ] ID remapping works for all event types
- [ ] Performance is not degraded

## Constraints
- Must work with Cerebras backend (Chat Completions API)
- Cannot modify Agents SDK or ChatKit library code
- Must maintain streaming performance
- Must be transparent to other system components

## Risks
- ID remapping might miss some event types
- Performance impact from UUID generation
- Potential race conditions in concurrent requests
- Future Agents SDK changes might break remapping

## Implementation Notes

### Files to Modify
- `backend/src/agents/chatkit_server.py`: Add ID remapping logic in `respond()` method

### Key Code Pattern
```python
id_remap: dict[str, str] = {}

async for event in stream_agent_response(agent_context, result):
    if isinstance(event, ThreadItemAddedEvent):
        if hasattr(event.item, 'type') and event.item.type == "assistant_message":
            old_id = event.item.id
            new_id = self.store.generate_item_id("message", thread, context)
            id_remap[old_id] = new_id
            event.item.id = new_id

    elif isinstance(event, ThreadItemUpdatedEvent):
        if event.item_id in id_remap:
            event = event.model_copy(update={"item_id": id_remap[event.item_id]})

    elif isinstance(event, ThreadItemDoneEvent):
        if hasattr(event.item, 'id') and event.item.id in id_remap:
            event.item.id = id_remap[event.item.id]

    yield event
```

## Testing Strategy
1. Create multiple conversation turns
2. Verify each response appears as separate message
3. Test with rapid consecutive messages
4. Verify message history persistence
5. Test with different message types (text, tool calls)

## Related Issues
- Bug #2: delete_task TypeError (fixed in same session)
- Bug #5: Tool result injection (uses similar ID remapping pattern)