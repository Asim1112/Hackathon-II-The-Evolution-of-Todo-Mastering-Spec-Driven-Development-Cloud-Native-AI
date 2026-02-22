# LLM Interceptor Enhancement Specification

## Problem Statement

During debugging of tool calling issues, there was insufficient observability into the LLM's streaming responses. The original interceptor only logged non-streaming requests, making it impossible to debug tool calling behavior with Cerebras's streaming API.

**Evidence:**
- Tool calling failures were difficult to diagnose
- No visibility into streaming tool calls from Cerebras
- Logs only showed request parameters, not streaming responses
- Could not verify if Cerebras was actually calling tools

**Root Cause:**
The original `llm_interceptor.py` implementation only logged non-streaming responses. When `stream=True`, the interceptor returned the stream without any tracking, providing zero visibility into:
- Whether tool calls were being made
- What tool names were being called
- What arguments were being passed
- When tool calls completed

**Technical Details:**
- Cerebras uses streaming Chat Completions API
- Tool calls arrive incrementally in delta chunks
- Original interceptor: logged request, returned stream unmodified
- No way to observe tool call lifecycle in streaming mode
- Debugging required blind guessing

## Requirements

### Functional Requirements
1. **Streaming Tool Call Tracking**: Log tool calls as they arrive in streaming responses
2. **Request Logging**: Continue logging request parameters (tools, messages, tool_choice)
3. **Non-Streaming Support**: Maintain existing non-streaming logging
4. **Transparent Wrapping**: Stream wrapper must not interfere with SDK processing
5. **Incremental Logging**: Log tool call detection, name, arguments, and completion

### Non-Functional Requirements
1. **Performance**: Minimal overhead on streaming responses
2. **Transparency**: Must not break Agents SDK stream processing
3. **Debuggability**: Clear, structured log output
4. **Maintainability**: Clean, well-documented code

## Solution Approach

### Architecture
Create a `StreamingToolCallTracker` class that wraps async streams to intercept and log tool call chunks without modifying the stream data.

### Stream Wrapping Pattern
1. **Wrap** the original stream in `StreamingToolCallTracker`
2. **Intercept** each chunk via `__anext__`
3. **Inspect** chunk for tool call deltas
4. **Accumulate** tool call data (name, arguments, id)
5. **Log** tool call lifecycle events
6. **Forward** unmodified chunk to SDK

### Components
- `StreamingToolCallTracker` class: Async stream wrapper
- `intercept_llm_requests()` function: Client patching
- Tool call accumulation: Track by index
- Lifecycle logging: Detection, name, arguments, completion

### Data Flow
```
1. Model generates streaming response
2. Interceptor wraps stream in StreamingToolCallTracker
3. Agents SDK iterates over wrapped stream
4. For each chunk:
   a. Tracker inspects for tool call deltas
   b. Accumulates tool call data by index
   c. Logs lifecycle events
   d. Returns unmodified chunk to SDK
5. SDK processes stream normally
6. Tracker logs completion when finish_reason arrives
```

## Acceptance Criteria
- [ ] Streaming tool calls are logged as they arrive
- [ ] Tool call name, arguments, and ID are captured
- [ ] Request parameters continue to be logged
- [ ] Non-streaming responses continue to work
- [ ] Stream processing is not disrupted
- [ ] Performance overhead is minimal
- [ ] Logs are clear and structured

## Constraints
- Must not modify stream data
- Must implement full async stream interface
- Must forward all stream methods/properties
- Cannot break Agents SDK stream consumption
- Must work with both Cerebras and OpenAI

## Risks
- Stream wrapper might not implement all required methods
- Performance overhead from inspection
- Logging might be too verbose
- Future SDK changes might break wrapper

## Implementation Notes

### Files to Modify
- `backend/src/agents/llm_interceptor.py`: Complete rewrite with `StreamingToolCallTracker`

### Key Components

#### StreamingToolCallTracker Class
```python
class StreamingToolCallTracker:
    """Wraps an async stream to log tool calls as they arrive from Cerebras."""

    def __init__(self, stream):
        self._stream = stream
        self._tool_calls = {}  # index -> {name, arguments, id}
        self._has_content = False

    def __aiter__(self):
        return self

    async def __anext__(self):
        chunk = await self._stream.__anext__()

        # Track tool calls from streaming chunks
        if hasattr(chunk, 'choices') and chunk.choices:
            delta = chunk.choices[0].delta
            if delta:
                # Track text content
                if hasattr(delta, 'content') and delta.content:
                    if not self._has_content:
                        self._has_content = True
                        logger.info("[LLM STREAM] Text content started")

                # Track tool calls
                if hasattr(delta, 'tool_calls') and delta.tool_calls:
                    for tc in delta.tool_calls:
                        idx = tc.index
                        if idx not in self._tool_calls:
                            self._tool_calls[idx] = {"name": "", "arguments": "", "id": ""}
                            logger.info(f"[LLM STREAM] New tool call detected at index {idx}")

                        if tc.function:
                            if tc.function.name:
                                self._tool_calls[idx]["name"] = tc.function.name
                                logger.info(f"[LLM STREAM] Tool call [{idx}] name: {tc.function.name}")
                            if tc.function.arguments:
                                self._tool_calls[idx]["arguments"] += tc.function.arguments

                        if tc.id:
                            self._tool_calls[idx]["id"] = tc.id

            # Check for finish_reason
            if hasattr(chunk.choices[0], 'finish_reason') and chunk.choices[0].finish_reason:
                finish = chunk.choices[0].finish_reason
                logger.info(f"[LLM STREAM] Finish reason: {finish}")
                if self._tool_calls:
                    logger.info(f"[LLM STREAM] Tool calls completed: {len(self._tool_calls)}")
                    for idx, tc in self._tool_calls.items():
                        logger.info(f"  [{idx}] {tc['name']}(id={tc['id']}) args={tc['arguments'][:200]}")
                elif self._has_content:
                    logger.info("[LLM STREAM] Response was text-only (no tool calls)")

        return chunk

    # Forward all other async stream methods
    async def aclose(self):
        if hasattr(self._stream, 'aclose'):
            await self._stream.aclose()

    async def __aenter__(self):
        if hasattr(self._stream, '__aenter__'):
            await self._stream.__aenter__()
        return self

    async def __aexit__(self, *args):
        if hasattr(self._stream, '__aexit__'):
            await self._stream.__aexit__(*args)

    @property
    def response(self):
        """Forward the response property for OpenAI stream compatibility."""
        return self._stream.response if hasattr(self._stream, 'response') else None
```

#### Interceptor Function
```python
def intercept_llm_requests(client):
    """Intercept OpenAI client requests to log parameters and streaming tool calls."""
    original_create = client.chat.completions.create

    async def logged_create(*args, **kwargs):
        is_streaming = kwargs.get('stream', False)

        # Log request parameters
        logger.info("=" * 70)
        logger.info(f"[LLM REQUEST] stream={is_streaming}")
        logger.info("=" * 70)

        if 'tools' in kwargs and kwargs['tools']:
            tool_names = [t.get('function', {}).get('name', '?') for t in kwargs['tools']]
            logger.info(f"[OK] Tools: {tool_names}")
        else:
            logger.warning("[WARN] NO TOOLS in request!")

        # Call original
        response = await original_create(*args, **kwargs)

        if not is_streaming:
            # Non-streaming: log response directly
            logger.info("[LLM RESPONSE - non-streaming]")
            if hasattr(response, 'choices') and response.choices:
                message = response.choices[0].message
                if hasattr(message, 'tool_calls') and message.tool_calls:
                    logger.info(f"[OK] Tool calls: {len(message.tool_calls)}")
                    for tc in message.tool_calls:
                        logger.info(f"  - {tc.function.name}({tc.function.arguments[:100]})")
        else:
            # Streaming: wrap to track tool calls
            logger.info("[LLM RESPONSE - streaming, tracking tool calls...]")
            response = StreamingToolCallTracker(response)

        return response

    client.chat.completions.create = logged_create
    return client
```

### Logging Output Example
```
======================================================================
[LLM REQUEST] stream=True
======================================================================
[OK] Tools: ['add_task', 'list_tasks', 'complete_task', 'update_task', 'delete_task']
Messages: 3 total
  Last msg: role=user, content=create a task with title 'playing cricket'...
======================================================================
[LLM RESPONSE - streaming, tracking tool calls...]
[LLM STREAM] New tool call detected at index 0
[LLM STREAM] Tool call [0] name: add_task
[LLM STREAM] Finish reason: tool_calls
[LLM STREAM] Tool calls completed: 1
  [0] add_task(id=call_abc123) args={"title":"playing cricket","description":""}
```

## Testing Strategy
1. Test with streaming tool calls (Cerebras)
2. Test with non-streaming responses
3. Test with text-only responses (no tools)
4. Test with multiple tool calls in one response
5. Verify stream processing is not disrupted
6. Verify Agents SDK receives unmodified chunks
7. Test performance impact

## Observability Benefits

### Before
- No visibility into streaming tool calls
- Blind debugging of tool calling issues
- Could not verify Cerebras tool calling support

### After
- Real-time tool call detection logging
- Tool name and arguments visible as they arrive
- Completion status clearly logged
- Easy to diagnose tool calling failures

## Related Issues
- Bug #3: user_id extraction (this logging helped diagnose the issue)
- Bug #5: Tool result injection (logging showed tools were executing)