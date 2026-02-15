# Tasks for Message ID Collision Fix

## Overview
Fix message history contamination where new bot responses append to previous responses instead of appearing as separate messages in the ChatKit UI.

## Dependencies
- ChatKit Python SDK working
- Agents SDK streaming responses
- PostgreSQL database for ID generation
- Frontend ChatKit React component

## Tasks

### 1. Implement ID Remapping Layer in respond() Method
**Description:** Add ID remapping logic to intercept streaming events and replace synthetic IDs with unique UUIDs
**Acceptance Criteria:**
- id_remap dictionary created per request
- ThreadItemAddedEvent intercepted for assistant messages
- Unique IDs generated using store.generate_item_id()
- Old ID mapped to new ID in dictionary
- Event item.id replaced with new ID
- Logging shows ID remapping

**Implementation:**
- [ ] Add id_remap dict initialization in respond() method
- [ ] Intercept ThreadItemAddedEvent in async for loop
- [ ] Check if event.item.type == "assistant_message"
- [ ] Generate new ID using store.generate_item_id("message", thread, context)
- [ ] Store mapping: id_remap[old_id] = new_id
- [ ] Replace event.item.id with new_id
- [ ] Add logging for remapping

**Test Cases:**
```python
# Test 1: Single message
send_message("Hello")
response = get_response()
assert response.id != "__fake_id__"
assert response.id.startswith("message_")

# Test 2: Multiple consecutive messages
send_message("Message 1")
send_message("Message 2")
send_message("Message 3")
responses = get_all_responses()
ids = [r.id for r in responses]
assert len(ids) == len(set(ids))  # All unique

# Test 3: ID format
response = get_response()
assert len(response.id) > 10  # UUID-based
assert "_" in response.id  # Contains separator
```

### 2. Handle ThreadItemUpdatedEvent ID Remapping
**Description:** Ensure update events use remapped IDs for consistency
**Acceptance Criteria:**
- ThreadItemUpdatedEvent intercepted
- event.item_id checked against id_remap
- Event recreated with remapped ID if found
- Original event yielded if not in remap

**Implementation:**
- [ ] Add elif branch for ThreadItemUpdatedEvent
- [ ] Check if event.item_id in id_remap
- [ ] Use model_copy to create new event with remapped ID
- [ ] Yield modified event
- [ ] Test with streaming text updates

**Test Cases:**
```python
# Test 1: Update event uses remapped ID
start_message()
update_message("partial text")
update_message("more text")
events = get_all_events()
update_events = [e for e in events if e.type == "updated"]
assert all(e.item_id in id_remap.values() for e in update_events)

# Test 2: Multiple updates to same message
start_message()
for i in range(10):
    update_message(f"chunk {i}")
events = get_all_events()
item_ids = [e.item_id for e in events if e.type == "updated"]
assert len(set(item_ids)) == 1  # All updates to same ID
```

### 3. Handle ThreadItemDoneEvent ID Remapping
**Description:** Ensure completion events use remapped IDs
**Acceptance Criteria:**
- ThreadItemDoneEvent intercepted
- event.item.id checked against id_remap
- Item ID replaced with remapped ID if found
- Event yielded with correct ID

**Implementation:**
- [ ] Add elif branch for ThreadItemDoneEvent
- [ ] Check if hasattr(event.item, 'id')
- [ ] Check if event.item.id in id_remap
- [ ] Replace event.item.id with remapped ID
- [ ] Yield modified event
- [ ] Test with message completion

**Test Cases:**
```python
# Test 1: Done event uses remapped ID
send_message("Complete message")
wait_for_completion()
done_event = get_done_event()
assert done_event.item.id != "__fake_id__"
assert done_event.item.id in id_remap.values()

# Test 2: Done event matches previous events
send_message("Test")
events = get_all_events()
added_id = events[0].item.id
done_id = events[-1].item.id
assert added_id == done_id
```

### 4. Verify No Message Contamination in UI
**Description:** Test that messages appear as separate bubbles in the ChatKit UI
**Acceptance Criteria:**
- Each response appears as separate message
- No text appending to previous messages
- Message history displays correctly
- No console errors in browser

**Implementation:**
- [ ] Start fresh conversation
- [ ] Send 5 consecutive messages
- [ ] Verify each appears as separate bubble
- [ ] Check browser DevTools for unique IDs
- [ ] Verify no React errors in console
- [ ] Test with rapid consecutive messages

**Test Cases:**
```python
# Test 1: Visual separation
messages = ["Hello", "How are you?", "Tell me a joke", "Thanks", "Goodbye"]
for msg in messages:
    send_message(msg)
    wait_for_response()

ui_messages = get_ui_messages()
assert len(ui_messages) == len(messages) * 2  # User + assistant for each

# Test 2: No contamination
send_message("First")
first_response = get_last_response()
send_message("Second")
second_response = get_last_response()
assert first_response.text != second_response.text
assert "First" not in second_response.text

# Test 3: Rapid messages
for i in range(10):
    send_message(f"Message {i}")
time.sleep(0.1)  # Brief pause
ui_messages = get_ui_messages()
assert len(ui_messages) >= 20  # At least 10 pairs
```

### 5. Test ID Uniqueness Across Sessions
**Description:** Verify IDs are unique across different user sessions
**Acceptance Criteria:**
- IDs unique within single session
- IDs unique across multiple sessions
- No ID collisions in database
- Concurrent requests handled correctly

**Implementation:**
- [ ] Test with single user, multiple messages
- [ ] Test with multiple users simultaneously
- [ ] Test with concurrent requests
- [ ] Query database for duplicate IDs
- [ ] Verify UUID generation is working

**Test Cases:**
```python
# Test 1: Single session uniqueness
session = create_session()
ids = []
for i in range(100):
    response = session.send_message(f"Message {i}")
    ids.append(response.id)
assert len(ids) == len(set(ids))

# Test 2: Multi-session uniqueness
sessions = [create_session() for _ in range(10)]
all_ids = []
for session in sessions:
    for i in range(10):
        response = session.send_message(f"Message {i}")
        all_ids.append(response.id)
assert len(all_ids) == len(set(all_ids))

# Test 3: Concurrent requests
import asyncio
async def send_concurrent():
    tasks = [send_message_async(f"Msg {i}") for i in range(50)]
    responses = await asyncio.gather(*tasks)
    ids = [r.id for r in responses]
    assert len(ids) == len(set(ids))
```

### 6. Performance Testing
**Description:** Verify ID remapping doesn't impact streaming performance
**Acceptance Criteria:**
- Latency increase <5ms per message
- No memory leaks from id_remap dict
- Streaming speed maintained
- No performance degradation over time

**Implementation:**
- [ ] Benchmark message latency before fix
- [ ] Benchmark message latency after fix
- [ ] Compare results
- [ ] Test with long conversations (100+ messages)
- [ ] Monitor memory usage
- [ ] Profile ID generation overhead

**Test Cases:**
```python
# Test 1: Latency measurement
import time
latencies = []
for i in range(100):
    start = time.time()
    send_message(f"Message {i}")
    wait_for_response()
    latencies.append(time.time() - start)

avg_latency = sum(latencies) / len(latencies)
assert avg_latency < 1.0  # Less than 1 second average

# Test 2: Memory leak check
import psutil
process = psutil.Process()
initial_memory = process.memory_info().rss
for i in range(1000):
    send_message(f"Message {i}")
    wait_for_response()
final_memory = process.memory_info().rss
memory_increase = final_memory - initial_memory
assert memory_increase < 10 * 1024 * 1024  # Less than 10MB increase

# Test 3: Streaming speed
start = time.time()
send_message("Generate a long response")
chunks = []
for chunk in stream_response():
    chunks.append(chunk)
duration = time.time() - start
assert duration < 5.0  # Complete within 5 seconds
```

## Testing
- [ ] Unit tests for ID remapping logic
- [ ] Integration tests with ChatKit
- [ ] UI tests for message separation
- [ ] Performance benchmarks
- [ ] Concurrent request tests

## Risks
- ID generation might be slow
- Memory leaks from id_remap dict
- Event types might be missed
- Future SDK changes might break remapping

## Mitigation
- Benchmark ID generation performance
- Ensure id_remap is garbage collected per request
- Review all ChatKit event types
- Pin SDK versions, test before upgrading