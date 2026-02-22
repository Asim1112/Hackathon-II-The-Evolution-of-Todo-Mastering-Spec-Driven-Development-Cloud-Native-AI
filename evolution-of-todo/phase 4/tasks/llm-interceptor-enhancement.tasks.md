# Tasks for LLM Interceptor Enhancement

## Overview
Enhance LLM interceptor to provide visibility into streaming tool calls from Cerebras, enabling better debugging of tool calling issues.

## Dependencies
- OpenAI Python SDK (AsyncStream)
- Cerebras API (streaming Chat Completions)
- Python asyncio
- Logging infrastructure

## Tasks

### 1. Create StreamingToolCallTracker Class
**Description:** Implement async stream wrapper class to intercept and log tool calls
**Acceptance Criteria:**
- Class wraps original stream
- Implements full async stream protocol
- Tracks tool calls by index
- Logs tool call lifecycle events
- Returns unmodified chunks to SDK

**Implementation:**
- [ ] Create StreamingToolCallTracker class
- [ ] Add __init__ to store stream and initialize tracking dicts
- [ ] Implement __aiter__ to return self
- [ ] Implement __anext__ to intercept chunks
- [ ] Add _tool_calls dict: index -> {name, arguments, id}
- [ ] Add _has_content flag for text tracking
- [ ] Implement async stream methods (aclose, __aenter__, __aexit__)
- [ ] Add response property for OpenAI compatibility

**Test Cases:**
```python
# Test 1: Stream wrapper transparency
original_stream = create_mock_stream()
wrapped_stream = StreamingToolCallTracker(original_stream)

original_chunks = []
async for chunk in original_stream:
    original_chunks.append(chunk)

wrapped_chunks = []
async for chunk in wrapped_stream:
    wrapped_chunks.append(chunk)

assert original_chunks == wrapped_chunks  # Chunks unmodified

# Test 2: Async stream protocol
wrapped = StreamingToolCallTracker(mock_stream)
assert hasattr(wrapped, '__aiter__')
assert hasattr(wrapped, '__anext__')
assert hasattr(wrapped, 'aclose')
assert hasattr(wrapped, '__aenter__')
assert hasattr(wrapped, '__aexit__')
assert hasattr(wrapped, 'response')

# Test 3: Tool call tracking initialization
tracker = StreamingToolCallTracker(mock_stream)
assert tracker._tool_calls == {}
assert tracker._has_content == False
```

### 2. Implement Tool Call Delta Processing
**Description:** Add logic to accumulate tool call information from streaming deltas
**Acceptance Criteria:**
- Detects new tool calls by index
- Accumulates tool name
- Accumulates arguments incrementally
- Captures tool call ID
- Logs detection and name

**Implementation:**
- [ ] Check if chunk has choices and delta
- [ ] Check if delta has tool_calls
- [ ] Iterate over tool call deltas
- [ ] Initialize tracking dict for new indices
- [ ] Accumulate function name (set once)
- [ ] Accumulate function arguments (append)
- [ ] Capture tool call ID
- [ ] Log new tool call detection
- [ ] Log tool call name when available

**Test Cases:**
```python
# Test 1: New tool call detection
tracker = StreamingToolCallTracker(mock_stream)
chunk = create_chunk_with_tool_call(index=0, name="add_task")
await tracker.__anext__()  # Process chunk

assert 0 in tracker._tool_calls
assert tracker._tool_calls[0]["name"] == "add_task"
# Verify log: "[LLM STREAM] New tool call detected at index 0"
# Verify log: "[LLM STREAM] Tool call [0] name: add_task"

# Test 2: Argument accumulation
tracker = StreamingToolCallTracker(mock_stream)
chunks = [
    create_chunk_with_args(index=0, args='{"title"'),
    create_chunk_with_args(index=0, args=': "Test"'),
    create_chunk_with_args(index=0, args='}'),
]
for chunk in chunks:
    await tracker.__anext__()

assert tracker._tool_calls[0]["arguments"] == '{"title": "Test"}'

# Test 3: Multiple tool calls
tracker = StreamingToolCallTracker(mock_stream)
chunk1 = create_chunk_with_tool_call(index=0, name="add_task")
chunk2 = create_chunk_with_tool_call(index=1, name="list_tasks")
await tracker.__anext__()  # Process chunk1
await tracker.__anext__()  # Process chunk2

assert len(tracker._tool_calls) == 2
assert tracker._tool_calls[0]["name"] == "add_task"
assert tracker._tool_calls[1]["name"] == "list_tasks"
```

### 3. Implement Completion Logging
**Description:** Log tool call summary when finish_reason arrives
**Acceptance Criteria:**
- Detects finish_reason in chunk
- Logs finish reason value
- Logs tool call count if any
- Logs each tool call with name, ID, and arguments preview
- Logs text-only response if no tool calls

**Implementation:**
- [ ] Check if chunk has finish_reason
- [ ] Log finish reason value
- [ ] Check if tool calls were accumulated
- [ ] Log tool call count
- [ ] Iterate over tool calls
- [ ] Log each: index, name, ID, arguments (truncated to 200 chars)
- [ ] If no tool calls but has content, log text-only
- [ ] Format logs clearly with indentation

**Test Cases:**
```python
# Test 1: Tool call completion
tracker = StreamingToolCallTracker(mock_stream)
# Add tool call
chunk1 = create_chunk_with_tool_call(index=0, name="add_task", args='{"title":"Test"}')
await tracker.__anext__()
# Add finish reason
chunk2 = create_chunk_with_finish_reason("tool_calls")
await tracker.__anext__()

# Verify logs:
# "[LLM STREAM] Finish reason: tool_calls"
# "[LLM STREAM] Tool calls completed: 1"
# "  [0] add_task(id=...) args={\"title\":\"Test\"}"

# Test 2: Text-only response
tracker = StreamingToolCallTracker(mock_stream)
chunk1 = create_chunk_with_content("Hello")
await tracker.__anext__()
chunk2 = create_chunk_with_finish_reason("stop")
await tracker.__anext__()

# Verify logs:
# "[LLM STREAM] Text content started"
# "[LLM STREAM] Finish reason: stop"
# "[LLM STREAM] Response was text-only (no tool calls)"

# Test 3: Long arguments truncation
tracker = StreamingToolCallTracker(mock_stream)
long_args = '{"description": "' + "x" * 500 + '"}'
chunk = create_chunk_with_tool_call(index=0, name="add_task", args=long_args)
await tracker.__anext__()
chunk2 = create_chunk_with_finish_reason("tool_calls")
await tracker.__anext__()

# Verify: arguments truncated to 200 chars in log
```

### 4. Update intercept_llm_requests Function
**Description:** Modify interceptor to wrap streaming responses with StreamingToolCallTracker
**Acceptance Criteria:**
- Detects streaming mode from kwargs
- Wraps streaming responses in tracker
- Maintains non-streaming logging
- Returns wrapped stream to SDK
- Logs request parameters

**Implementation:**
- [ ] Check if stream=True in kwargs
- [ ] Log request parameters (tools, messages, tool_choice)
- [ ] Call original create method
- [ ] If not streaming: log response directly
- [ ] If streaming: wrap in StreamingToolCallTracker
- [ ] Return wrapped stream
- [ ] Test with both streaming and non-streaming

**Test Cases:**
```python
# Test 1: Streaming request wrapping
client = create_mock_client()
intercepted_client = intercept_llm_requests(client)

response = await intercepted_client.chat.completions.create(
    model="llama-3.3-70b",
    messages=[{"role": "user", "content": "test"}],
    tools=[{"function": {"name": "add_task"}}],
    stream=True
)

assert isinstance(response, StreamingToolCallTracker)
assert hasattr(response, '_stream')  # Wraps original

# Test 2: Non-streaming request (no wrapping)
response = await intercepted_client.chat.completions.create(
    model="llama-3.3-70b",
    messages=[{"role": "user", "content": "test"}],
    stream=False
)

assert not isinstance(response, StreamingToolCallTracker)
# Verify: response logged directly

# Test 3: Request parameter logging
with capture_logs() as logs:
    await intercepted_client.chat.completions.create(
        model="llama-3.3-70b",
        messages=[{"role": "user", "content": "create task"}],
        tools=[{"function": {"name": "add_task"}}, {"function": {"name": "list_tasks"}}],
        tool_choice="auto",
        stream=True
    )

log_text = "\n".join(logs)
assert "[LLM REQUEST] stream=True" in log_text
assert "[OK] Tools: ['add_task', 'list_tasks']" in log_text
assert "Tool choice: auto" in log_text
```

### 5. Test with Real Cerebras Requests
**Description:** Verify interceptor works with actual Cerebras streaming API
**Acceptance Criteria:**
- Works with Cerebras llama-3.3-70b model
- Logs tool calls correctly
- Doesn't break stream processing
- Agents SDK receives correct chunks
- Tool execution works end-to-end

**Implementation:**
- [ ] Configure Cerebras client with interceptor
- [ ] Make request with tool calling
- [ ] Verify tool calls are logged
- [ ] Verify Agents SDK processes stream correctly
- [ ] Verify tools execute successfully
- [ ] Check logs for complete tool call information
- [ ] Test with multiple tool calls in one response

**Test Cases:**
```python
# Test 1: Single tool call
with capture_logs() as logs:
    response = await chat_with_tools("create a task with title 'test'")

log_text = "\n".join(logs)
assert "[LLM STREAM] New tool call detected" in log_text
assert "[LLM STREAM] Tool call [0] name: add_task" in log_text
assert "[LLM STREAM] Finish reason: tool_calls" in log_text
assert "add_task" in log_text

# Test 2: Multiple tool calls
with capture_logs() as logs:
    response = await chat_with_tools("create 3 tasks")

log_text = "\n".join(logs)
assert "[LLM STREAM] Tool calls completed: 3" in log_text

# Test 3: Text response (no tools)
with capture_logs() as logs:
    response = await chat_with_tools("hello")

log_text = "\n".join(logs)
assert "[LLM STREAM] Text content started" in log_text
assert "[LLM STREAM] Response was text-only" in log_text
```

### 6. Verify No Stream Processing Disruption
**Description:** Ensure wrapper doesn't interfere with Agents SDK stream consumption
**Acceptance Criteria:**
- Agents SDK receives all chunks
- Chunks are unmodified
- Stream methods work correctly
- No AttributeError or stream errors
- Tool execution completes successfully

**Implementation:**
- [ ] Test stream iteration completes
- [ ] Verify all chunks received by SDK
- [ ] Test aclose() method
- [ ] Test context manager (__aenter__, __aexit__)
- [ ] Test response property
- [ ] Verify tool execution works
- [ ] Monitor for any stream-related errors

**Test Cases:**
```python
# Test 1: Complete stream iteration
wrapped_stream = StreamingToolCallTracker(original_stream)
chunk_count = 0
async for chunk in wrapped_stream:
    chunk_count += 1
    assert chunk is not None

assert chunk_count > 0  # Stream not empty

# Test 2: Context manager
async with StreamingToolCallTracker(original_stream) as stream:
    async for chunk in stream:
        pass
# No errors

# Test 3: Response property
wrapped = StreamingToolCallTracker(mock_stream_with_response)
assert wrapped.response is not None
assert wrapped.response == mock_stream_with_response.response

# Test 4: Tool execution after streaming
with capture_logs() as logs:
    result = await execute_tool_with_streaming("add_task", {"title": "Test"})

assert result["status"] == "created"
# Verify: tool call was logged
# Verify: tool executed successfully
```

### 7. Performance Testing
**Description:** Verify interceptor doesn't add significant latency
**Acceptance Criteria:**
- Overhead <5ms per chunk
- No memory leaks
- Streaming speed maintained
- No performance degradation over time

**Implementation:**
- [ ] Benchmark streaming without interceptor
- [ ] Benchmark streaming with interceptor
- [ ] Compare latencies
- [ ] Test with long conversations
- [ ] Monitor memory usage
- [ ] Profile inspection overhead

**Test Cases:**
```python
# Test 1: Latency measurement
import time

# Without interceptor
start = time.time()
async for chunk in original_stream:
    pass
baseline_duration = time.time() - start

# With interceptor
start = time.time()
async for chunk in StreamingToolCallTracker(original_stream):
    pass
intercepted_duration = time.time() - start

overhead = intercepted_duration - baseline_duration
assert overhead < 0.1  # Less than 100ms total overhead

# Test 2: Memory leak check
import psutil
process = psutil.Process()
initial_memory = process.memory_info().rss

for i in range(100):
    wrapped = StreamingToolCallTracker(create_stream())
    async for chunk in wrapped:
        pass

final_memory = process.memory_info().rss
memory_increase = final_memory - initial_memory
assert memory_increase < 5 * 1024 * 1024  # Less than 5MB

# Test 3: Sustained performance
durations = []
for i in range(50):
    start = time.time()
    async for chunk in StreamingToolCallTracker(create_stream()):
        pass
    durations.append(time.time() - start)

# Verify no degradation over time
first_half_avg = sum(durations[:25]) / 25
second_half_avg = sum(durations[25:]) / 25
assert abs(first_half_avg - second_half_avg) < 0.05  # Within 50ms
```

## Testing
- [ ] Unit tests for StreamingToolCallTracker
- [ ] Integration tests with Cerebras API
- [ ] Stream protocol compliance tests
- [ ] Performance benchmarks
- [ ] Memory leak tests
- [ ] End-to-end tool execution tests

## Risks
- Stream wrapper might not implement all required methods
- Performance overhead from inspection
- Log verbosity in production
- Future SDK changes might break wrapper

## Mitigation
- Implement full async stream protocol
- Minimize inspection logic
- Truncate arguments in logs
- Pin SDK versions, test before upgrading
- Monitor performance metrics