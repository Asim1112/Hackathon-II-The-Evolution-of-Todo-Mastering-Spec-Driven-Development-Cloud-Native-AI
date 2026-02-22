# Message ID Collision Fix Implementation Plan

## Scope and Dependencies

### In Scope
- Implement ID remapping layer in TodoChatKitServer.respond()
- Handle ThreadItemAddedEvent, ThreadItemUpdatedEvent, ThreadItemDoneEvent
- Generate unique IDs using store.generate_item_id()
- Maintain ID mapping dictionary for event consistency

### Out of Scope
- Modifying Agents SDK or ChatKit library code
- Changing FAKE_RESPONSES_ID behavior in upstream libraries
- Modifying frontend ChatKit React components
- Changing database schema or persistence layer

### External Dependencies
- OpenAI Agents SDK (OpenAIChatCompletionsModel)
- ChatKit Python SDK (stream_agent_response, event types)
- Cerebras backend (Chat Completions API)
- PostgreSQL database (for ID generation)

## Key Decisions and Rationale

### Decision 1: ID Remapping vs Upstream Fix
**Option 1**: Fix FAKE_RESPONSES_ID in Agents SDK
**Option 2**: Implement ID remapping layer in our code
**Option 3**: Modify ChatKit React to handle duplicate IDs
**Chosen**: Option 2 - ID remapping layer
**Rationale**:
- We don't control Agents SDK or ChatKit library
- Remapping is non-invasive and maintainable
- Works with any backend (Cerebras, OpenAI, etc.)
- Can be removed if upstream fixes the issue

### Decision 2: ID Generation Strategy
**Option 1**: Use UUID.uuid4() directly
**Option 2**: Use store.generate_item_id() utility
**Option 3**: Use timestamp-based IDs
**Chosen**: Option 2 - store.generate_item_id()
**Rationale**:
- Consistent with existing codebase patterns
- Handles thread and context properly
- Guaranteed uniqueness across sessions
- Proper format for ChatKit

### Decision 3: Event Interception Approach
**Option 1**: Wrap stream_agent_response()
**Option 2**: Intercept events in async for loop
**Option 3**: Modify event objects after yielding
**Chosen**: Option 2 - Intercept in async for loop
**Rationale**:
- Clean and readable
- Easy to debug
- Minimal performance overhead
- Maintains streaming semantics

### Decision 4: ID Mapping Scope
**Option 1**: Global mapping across all requests
**Option 2**: Per-request mapping dictionary
**Option 3**: Per-thread persistent mapping
**Chosen**: Option 2 - Per-request mapping
**Rationale**:
- No memory leaks
- Thread-safe by design
- Simpler implementation
- Sufficient for preventing collisions

## Implementation Details

### Code Structure
```python
async def respond(self, thread, input_user_message, context):
    # ... existing setup code ...

    # ID remapping dictionary (per-request scope)
    id_remap: dict[str, str] = {}

    async for event in stream_agent_response(agent_context, result):
        # Intercept and remap assistant message IDs
        if isinstance(event, ThreadItemAddedEvent):
            if hasattr(event.item, 'type') and event.item.type == "assistant_message":
                old_id = event.item.id
                new_id = self.store.generate_item_id("message", thread, context)
                id_remap[old_id] = new_id
                event.item.id = new_id
                logger.info(f"[STREAM] Remapped assistant message ID: {old_id} -> {new_id}")

        # Remap IDs in update events
        elif isinstance(event, ThreadItemUpdatedEvent):
            if event.item_id in id_remap:
                event = event.model_copy(update={"item_id": id_remap[event.item_id]})

        # Remap IDs in done events
        elif isinstance(event, ThreadItemDoneEvent):
            if hasattr(event.item, 'id') and event.item.id in id_remap:
                event.item.id = id_remap[event.item.id]

        yield event
```

### Event Types to Handle
1. **ThreadItemAddedEvent**: Initial message creation - remap here
2. **ThreadItemUpdatedEvent**: Streaming text updates - use remapped ID
3. **ThreadItemDoneEvent**: Message completion - use remapped ID

### ID Generation Pattern
```python
new_id = self.store.generate_item_id("message", thread, context)
# Returns format: "message_<uuid_hex_12_chars>"
# Example: "message_a1b2c3d4e5f6"
```

## Non-Functional Requirements

### Performance
- **Target**: <1ms overhead per event
- **Measurement**: Log timing for ID generation
- **Optimization**: Use dict lookup (O(1)) for remapping

### Memory
- **Target**: <1KB per request for id_remap dict
- **Cleanup**: Dict is garbage collected after request completes
- **Monitoring**: No persistent state, no memory leaks

### Reliability
- **Target**: 100% ID uniqueness
- **Guarantee**: UUID-based generation ensures uniqueness
- **Fallback**: None needed - generation cannot fail

## Testing Strategy

### Unit Tests
```python
def test_id_remapping():
    # Create mock events with FAKE_RESPONSES_ID
    # Verify new IDs are unique
    # Verify mapping consistency across event types
    pass

def test_concurrent_requests():
    # Simulate multiple concurrent requests
    # Verify no ID collisions
    # Verify per-request isolation
    pass
```

### Integration Tests
```python
async def test_conversation_flow():
    # Send multiple messages
    # Verify each appears as separate message in UI
    # Verify no message contamination
    pass
```

### Manual Testing
1. Start conversation with chatbot
2. Send 5 consecutive messages
3. Verify each appears as separate message bubble
4. Check browser DevTools for unique item IDs
5. Verify no console errors

## Risk Analysis

### Top 3 Risks

1. **Event Type Coverage**
   - Risk: Missing some event types that need remapping
   - Impact: High - could cause ID collisions for those events
   - Mitigation: Review all ChatKit event types, add logging for unhandled events
   - Monitoring: Watch logs for FAKE_RESPONSES_ID in production

2. **Performance Degradation**
   - Risk: ID generation or dict lookup adds latency
   - Impact: Medium - could slow streaming responses
   - Mitigation: Benchmark ID generation, optimize if needed
   - Monitoring: Track p95 latency for streaming responses

3. **Future SDK Changes**
   - Risk: Agents SDK or ChatKit changes event structure
   - Impact: Medium - remapping might break
   - Mitigation: Pin SDK versions, test before upgrading
   - Monitoring: Integration tests will catch breakage

## Rollback Plan

### If Issues Occur
1. **Immediate**: Comment out ID remapping code
2. **Fallback**: Return to FAKE_RESPONSES_ID (accept message contamination)
3. **Investigation**: Review logs for specific failure mode
4. **Fix**: Adjust remapping logic based on findings
5. **Redeploy**: Test thoroughly before re-enabling

### Rollback Code
```python
# Disable ID remapping (emergency rollback)
# id_remap: dict[str, str] = {}

async for event in stream_agent_response(agent_context, result):
    # Skip all remapping logic
    yield event
```

## Deployment Strategy

### Pre-Deployment
1. Review code changes
2. Run unit tests
3. Run integration tests
4. Test manually in development

### Deployment
1. Deploy to staging environment
2. Test with real conversations
3. Monitor logs for errors
4. Deploy to production
5. Monitor for 24 hours

### Post-Deployment
1. Verify no message contamination
2. Check performance metrics
3. Review error logs
4. Collect user feedback

## Success Criteria

- [ ] No message contamination in UI
- [ ] Each message has unique ID
- [ ] Streaming performance maintained
- [ ] No errors in logs
- [ ] User conversations work correctly
- [ ] All event types handled properly