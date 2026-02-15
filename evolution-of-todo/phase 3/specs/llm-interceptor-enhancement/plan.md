# LLM Interceptor Enhancement Implementation Plan

## Scope and Dependencies

### In Scope
- Create StreamingToolCallTracker class for stream wrapping
- Implement tool call accumulation and logging
- Handle both streaming and non-streaming responses
- Maintain transparent stream interface
- Add comprehensive logging for debugging

### Out of Scope
- Modifying Agents SDK stream processing
- Changing OpenAI client behavior
- Modifying tool execution logic
- Adding persistent logging storage

### External Dependencies
- OpenAI Python SDK (AsyncStream, ChatCompletionChunk)
- Cerebras API (streaming Chat Completions)
- Python asyncio (async stream protocol)
- Logging infrastructure

## Key Decisions and Rationale

### Decision 1: Stream Wrapping vs Direct Logging
**Option 1**: Log directly in interceptor without wrapping
**Option 2**: Wrap stream in custom class
**Option 3**: Monkey-patch stream methods
**Chosen**: Option 2 - Wrap stream in custom class
**Rationale**:
- Clean separation of concerns
- Doesn't modify original stream
- Easy to enable/disable
- Maintains async stream protocol

### Decision 2: Tool Call Accumulation Strategy
**Option 1**: Log each delta immediately
**Option 2**: Accumulate and log on completion
**Option 3**: Hybrid - log detection and completion
**Chosen**: Option 3 - Hybrid approach
**Rationale**:
- Immediate feedback on tool call detection
- Complete information on completion
- Balances verbosity and usefulness
- Helps diagnose streaming issues

### Decision 3: Stream Interface Implementation
**Option 1**: Implement minimal interface (__aiter__, __anext__)
**Option 2**: Implement full async stream protocol
**Option 3**: Proxy all methods dynamically
**Chosen**: Option 2 - Full async stream protocol
**Rationale**:
- Ensures compatibility with Agents SDK
- Handles all stream operations correctly
- Explicit about what's supported
- Easier to debug than dynamic proxying

### Decision 4: Logging Verbosity
**Option 1**: Log everything (all deltas)
**Option 2**: Log only tool calls
**Option 3**: Log tool calls + finish reasons
**Chosen**: Option 3 - Tool calls + finish reasons
**Rationale**:
- Focused on debugging tool calling
- Not too verbose for production
- Includes completion status
- Easy to find in logs

## Implementation Details

### StreamingToolCallTracker Class

#### Core Structure
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
        # Get next chunk from original stream
        chunk = await self._stream.__anext__()

        # Inspect and log tool calls
        self._process_chunk(chunk)

        # Return unmodified chunk
        return chunk

    # Implement full async stream protocol
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
        """Forward response property for OpenAI compatibility."""
        return self._stream.response if hasattr(self._stream, 'response') else None
```

#### Tool Call Processing
```python
def _process_chunk(self, chunk):
    """Process chunk and log tool call information."""
    if not hasattr(chunk, 'choices') or not chunk.choices:
        return

    delta = chunk.choices[0].delta
    if not delta:
        return

    # Track text content
    if hasattr(delta, 'content') and delta.content:
        if not self._has_content:
            self._has_content = True
            logger.info("[LLM STREAM] Text content started")

    # Track tool calls
    if hasattr(delta, 'tool_calls') and delta.tool_calls:
        for tc in delta.tool_calls:
            self._process_tool_call_delta(tc)

    # Check for finish_reason
    if hasattr(chunk.choices[0], 'finish_reason') and chunk.choices[0].finish_reason:
        self._log_completion(chunk.choices[0].finish_reason)

def _process_tool_call_delta(self, tc_delta):
    """Process a single tool call delta."""
    idx = tc_delta.index
    if idx not in self._tool_calls:
        self._tool_calls[idx] = {"name": "", "arguments": "", "id": ""}
        logger.info(f"[LLM STREAM] New tool call detected at index {idx}")

    if tc_delta.function:
        if tc_delta.function.name:
            self._tool_calls[idx]["name"] = tc_delta.function.name
            logger.info(f"[LLM STREAM] Tool call [{idx}] name: {tc_delta.function.name}")
        if tc_delta.function.arguments:
            self._tool_calls[idx]["arguments"] += tc_delta.function.arguments

    if tc_delta.id:
        self._tool_calls[idx]["id"] = tc_delta.id

def _log_completion(self, finish_reason):
    """Log completion status and tool call summary."""
    logger.info(f"[LLM STREAM] Finish reason: {finish_reason}")
    if self._tool_calls:
        logger.info(f"[LLM STREAM] Tool calls completed: {len(self._tool_calls)}")
        for idx, tc in self._tool_calls.items():
            # Truncate arguments for readability
            args_preview = tc['arguments'][:200]
            logger.info(f"  [{idx}] {tc['name']}(id={tc['id']}) args={args_preview}")
    elif self._has_content:
        logger.info("[LLM STREAM] Response was text-only (no tool calls)")
```

### Interceptor Function

#### Request Logging
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

        # Log tools
        if 'tools' in kwargs and kwargs['tools']:
            tool_names = [t.get('function', {}).get('name', '?') for t in kwargs['tools']]
            logger.info(f"[OK] Tools: {tool_names}")
        else:
            logger.warning("[WARN] NO TOOLS in request!")

        # Log message count and last message
        if 'messages' in kwargs and kwargs['messages']:
            msgs = kwargs['messages']
            logger.info(f"Messages: {len(msgs)} total")
            if msgs:
                last = msgs[-1]
                role = last.get('role', '?')
                content = str(last.get('content', ''))[:100]
                logger.info(f"  Last msg: role={role}, content={content}...")

        # Log tool_choice if present
        if 'tool_choice' in kwargs:
            logger.info(f"Tool choice: {kwargs['tool_choice']}")

        logger.info("=" * 70)

        # Call original
        response = await original_create(*args, **kwargs)

        # Handle response based on streaming mode
        if not is_streaming:
            self._log_non_streaming_response(response)
        else:
            logger.info("[LLM RESPONSE - streaming, tracking tool calls...]")
            response = StreamingToolCallTracker(response)

        return response

    client.chat.completions.create = logged_create
    return client
```

## Non-Functional Requirements

### Performance
- **Target**: <1ms overhead per chunk
- **Measurement**: Minimal inspection logic
- **Impact**: Negligible compared to network latency

### Transparency
- **Requirement**: Must not modify stream data
- **Guarantee**: Only inspect, never modify chunks
- **Verification**: Agents SDK receives identical chunks

### Debuggability
- **Requirement**: Clear, structured log output
- **Format**: Consistent prefixes ([LLM STREAM])
- **Content**: Tool names, arguments preview, completion status

## Testing Strategy

### Unit Tests
```python
def test_stream_wrapper_transparency():
    # Create mock stream with chunks
    # Wrap in StreamingToolCallTracker
    # Verify chunks are unmodified
    pass

def test_tool_call_accumulation():
    # Create chunks with tool call deltas
    # Verify accumulation is correct
    # Verify logging occurs
    pass

def test_async_stream_protocol():
    # Verify __aiter__, __anext__ work
    # Verify aclose, __aenter__, __aexit__ work
    # Verify response property works
    pass
```

### Integration Tests
```python
async def test_with_cerebras():
    # Make real request to Cerebras
    # Verify tool calls are logged
    # Verify stream processing works
    pass

async def test_with_openai():
    # Make real request to OpenAI
    # Verify compatibility
    pass
```

### Manual Testing
1. Enable interceptor
2. Make tool calling request
3. Check logs for tool call detection
4. Verify tool execution works
5. Verify no errors in stream processing

## Risk Analysis

### Top 3 Risks

1. **Stream Protocol Incompatibility**
   - Risk: Missing required stream methods
   - Impact: High - Agents SDK fails to process stream
   - Mitigation: Implement full async stream protocol
   - Monitoring: Watch for AttributeError in logs

2. **Performance Degradation**
   - Risk: Inspection adds latency
   - Impact: Medium - slower streaming responses
   - Mitigation: Minimal inspection logic, no heavy processing
   - Monitoring: Track streaming latency metrics

3. **Log Verbosity**
   - Risk: Too much logging in production
   - Impact: Low - log storage costs
   - Mitigation: Focused logging, truncate arguments
   - Monitoring: Review log volume

## Rollback Plan

### If Issues Occur
1. **Immediate**: Disable stream wrapping
2. **Fallback**: Return original stream unmodified
3. **Investigation**: Review specific failure mode
4. **Fix**: Adjust wrapper implementation
5. **Redeploy**: Test thoroughly

### Rollback Code
```python
# Disable stream wrapping (emergency rollback)
if not is_streaming:
    # ... log non-streaming ...
else:
    # Skip wrapping
    # response = StreamingToolCallTracker(response)
    pass

return response
```

## Deployment Strategy

### Pre-Deployment
1. Review code changes
2. Run unit tests
3. Test with mock streams
4. Test with real Cerebras requests

### Deployment
1. Deploy to staging
2. Make test requests
3. Verify logging works
4. Verify no stream errors
5. Deploy to production

### Post-Deployment
1. Monitor logs for tool call tracking
2. Verify no stream processing errors
3. Check performance metrics
4. Review log volume

## Success Criteria

- [ ] Streaming tool calls are logged
- [ ] Tool names and arguments visible
- [ ] Completion status logged
- [ ] Stream processing works correctly
- [ ] No performance degradation
- [ ] Logs are clear and useful