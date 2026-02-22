# ADR-001: ChatKit ID Remapping Pattern for Cerebras Backend

**Status:** Accepted
**Date:** 2026-02-15
**Deciders:** Development Team
**Context:** Phase 3 AI Todo Assistant Chatbot

## Context and Problem Statement

When using the Cerebras backend (Chat Completions API) with the OpenAI Agents SDK and ChatKit, message history becomes corrupted in the UI. New bot responses append to previous responses instead of appearing as separate messages. This is caused by the Agents SDK's `OpenAIChatCompletionsModel` using a synthetic placeholder ID (`FAKE_RESPONSES_ID = "__fake_id__"`) for all Responses API items when converting from Chat Completions format.

The ChatKit React frontend matches messages by ID for state management. When it receives a `ThreadItemUpdatedEvent` with an `item_id` that already exists in its state, it treats it as an update to the existing message rather than a new message, causing text to be appended.

## Decision Drivers

- **User Experience**: Messages must appear as separate bubbles in the chat UI
- **Backend Compatibility**: Must work with Cerebras (Chat Completions API) without modifying upstream libraries
- **Maintainability**: Solution must be maintainable and not break with SDK updates
- **Performance**: Must not significantly impact streaming latency
- **Reliability**: ID uniqueness must be guaranteed across all sessions

## Considered Options

### Option 1: Fix FAKE_RESPONSES_ID in Agents SDK
**Pros:**
- Fixes root cause at source
- Benefits all users of the SDK

**Cons:**
- We don't control the Agents SDK
- Would require upstream contribution and acceptance
- Takes time to merge and release
- Doesn't help with current deployment

### Option 2: Modify ChatKit React to Handle Duplicate IDs
**Pros:**
- Fixes the issue at the frontend
- Could use timestamp or other heuristics

**Cons:**
- We don't control ChatKit React library
- Heuristics are unreliable
- Doesn't address root cause
- Could break with library updates

### Option 3: Implement ID Remapping Layer in Our Backend
**Pros:**
- We control the implementation
- Non-invasive to upstream libraries
- Can be deployed immediately
- Works with any backend (Cerebras, OpenAI, etc.)
- Can be removed if upstream fixes the issue

**Cons:**
- Adds complexity to our codebase
- Requires maintenance
- Adds minimal overhead to streaming

### Option 4: Switch to OpenAI Backend Only
**Pros:**
- OpenAI might not have this issue
- Simpler integration

**Cons:**
- More expensive (OpenAI vs Cerebras)
- Doesn't solve the architectural problem
- Limits backend flexibility
- Still might have issues with other backends

## Decision Outcome

**Chosen option: Option 3 - Implement ID Remapping Layer in Our Backend**

We will implement an ID remapping layer in the `TodoChatKitServer.respond()` method that intercepts streaming events and replaces synthetic IDs with guaranteed-unique UUIDs.

### Implementation Pattern

```python
async def respond(self, thread, input_user_message, context):
    # ... setup code ...

    # ID remapping dictionary (per-request scope)
    id_remap: dict[str, str] = {}

    async for event in stream_agent_response(agent_context, result):
        # Intercept assistant message creation
        if isinstance(event, ThreadItemAddedEvent):
            if hasattr(event.item, 'type') and event.item.type == "assistant_message":
                old_id = event.item.id
                new_id = self.store.generate_item_id("message", thread, context)
                id_remap[old_id] = new_id
                event.item.id = new_id

        # Remap IDs in subsequent events
        elif isinstance(event, ThreadItemUpdatedEvent):
            if event.item_id in id_remap:
                event = event.model_copy(update={"item_id": id_remap[event.item_id]})

        elif isinstance(event, ThreadItemDoneEvent):
            if hasattr(event.item, 'id') and event.item.id in id_remap:
                event.item.id = id_remap[event.item.id]

        yield event
```

### Rationale

1. **Immediate Solution**: Can be deployed without waiting for upstream changes
2. **Backend Agnostic**: Works with Cerebras, OpenAI, or any other backend
3. **Non-Invasive**: Doesn't modify upstream libraries
4. **Maintainable**: Isolated to one method, easy to understand and modify
5. **Removable**: Can be removed if upstream fixes the issue
6. **Performant**: Minimal overhead (UUID generation + dict lookup)

## Consequences

### Positive

- ✅ Messages appear as separate bubbles in UI
- ✅ Works with Cerebras backend
- ✅ No message history corruption
- ✅ Guaranteed ID uniqueness
- ✅ Can be deployed immediately
- ✅ Doesn't break with SDK updates (as long as event types remain stable)

### Negative

- ⚠️ Adds complexity to our codebase
- ⚠️ Requires maintenance if event types change
- ⚠️ Minimal performance overhead (~1ms per message)
- ⚠️ Need to track which event types require remapping

### Neutral

- 📝 Need to document the pattern for future developers
- 📝 Should monitor for upstream fixes that would make this obsolete
- 📝 Pattern can be reused for other ID collision issues (e.g., tool calls)

## Related Decisions

- This pattern was extended to handle tool call ID remapping (Bug #5)
- Similar approach used for handling other synthetic IDs in the system

## References

- Bug #1: Message ID Collision Fix
- Spec: `specs/message-id-collision-fix/spec.md`
- Implementation: `backend/src/agents/chatkit_server.py`
- Agents SDK: `OpenAIChatCompletionsModel` with `FAKE_RESPONSES_ID`
- ChatKit React: State management by item ID

## Notes

This is a pragmatic solution to an integration issue between three libraries we don't control (Agents SDK, ChatKit, Cerebras). The pattern is clean, maintainable, and can be removed if upstream libraries fix the root cause.

The same pattern has proven useful for other ID collision scenarios (tool calls), validating the architectural decision.