# Implementation Plan: ChatBot Streaming Response Bug Fix

## Metadata
- **Feature**: ChatBot Streaming Response Handler
- **Type**: Bug Fix
- **Date**: 2026-02-15
- **Status**: Implemented

## Overview

This plan addresses the critical bug in `llm_interceptor.py` where the code attempts to access `response.choices` on streaming responses, causing an `AttributeError`. The fix involves detecting streaming requests and handling them differently from non-streaming requests.

## Architecture Analysis

### Current Architecture

```
User Message
    ↓
ChatKit Server (chatkit_server.py)
    ↓
Agent + Runner.run_streamed()
    ↓
Model Factory (model_factory.py)
    ↓
OpenAI Client (with interceptor)
    ↓
LLM Interceptor (llm_interceptor.py) ← BUG HERE
    ↓
Cerebras/OpenAI API (stream=True)
    ↓
AsyncStream object (no .choices attribute)
```

### Problem Location

**File**: `backend/src/agents/llm_interceptor.py`
**Function**: `logged_create()` (lines 21-61)
**Issue**: Lines 49-59 assume all responses have `.choices` attribute

### Key Insights

1. **Streaming vs Non-Streaming**: The OpenAI API returns different object types:
   - Non-streaming: `ChatCompletion` object with `.choices` attribute
   - Streaming: `AsyncStream` object without `.choices` attribute

2. **Detection Method**: The `stream` parameter in `kwargs` indicates request type:
   ```python
   is_streaming = kwargs.get('stream', False)
   ```

3. **Logging Strategy**:
   - Non-streaming: Can inspect full response immediately
   - Streaming: Cannot inspect until stream is consumed (would break streaming)

4. **Minimal Change**: Only modify response inspection logic, not request logging

## Design Decisions

### Decision 1: Detection Strategy
**Options Considered**:
1. Check `isinstance(response, AsyncStream)` - requires importing AsyncStream type
2. Check `hasattr(response, 'choices')` - defensive but doesn't explain why
3. Check `kwargs.get('stream', False)` - explicit and clear

**Chosen**: Option 3 - Check kwargs for stream parameter
**Rationale**:
- Most explicit and maintainable
- Matches the actual request configuration
- No additional imports needed
- Clear intent in code

### Decision 2: Streaming Response Handling
**Options Considered**:
1. Skip all logging for streaming requests
2. Log request only, skip response inspection
3. Attempt to peek at stream (complex, breaks streaming)

**Chosen**: Option 2 - Log request, skip response inspection
**Rationale**:
- Maintains request logging (tools, parameters)
- Avoids breaking the stream
- Simple and safe
- Clear log message explains why response not inspected

### Decision 3: Safety Checks
**Options Considered**:
1. Trust that non-streaming responses have `.choices`
2. Add `hasattr(response, 'choices')` check
3. Add try-except around response inspection

**Chosen**: Option 2 - Add hasattr check
**Rationale**:
- Defensive programming
- Minimal overhead
- Prevents future similar issues
- Explicit about what we're checking

## Implementation Strategy

### Phase 1: Add Streaming Detection
**Location**: `llm_interceptor.py:43` (after response is received)
**Change**: Add boolean flag to detect streaming
```python
is_streaming = kwargs.get('stream', False)
```

### Phase 2: Conditional Response Inspection
**Location**: `llm_interceptor.py:45-59`
**Change**: Wrap existing inspection logic in `if not is_streaming:`
**Add**: Else clause with streaming log message

### Phase 3: Add Safety Check
**Location**: Within non-streaming block
**Change**: Add `hasattr(response, 'choices')` before accessing
**Rationale**: Defense against unexpected response types

### Code Structure

```python
async def logged_create(*args, **kwargs):
    # [UNCHANGED] Log request parameters (lines 22-40)

    # Call original
    response = await original_create(*args, **kwargs)

    # [NEW] Detect streaming
    is_streaming = kwargs.get('stream', False)

    # [MODIFIED] Conditional response inspection
    if not is_streaming:
        logger.info("=" * 70)
        logger.info("[LLM RESPONSE]")
        logger.info("=" * 70)
        # [NEW] Safety check
        if hasattr(response, 'choices') and response.choices:
            # [UNCHANGED] Existing inspection logic
            message = response.choices[0].message
            # ... rest of inspection
        logger.info("=" * 70)
    else:
        # [NEW] Streaming log message
        logger.info("Streaming response - skipping response inspection")
        logger.info("=" * 70)

    return response
```

## File Changes

### Modified Files
1. **backend/src/agents/llm_interceptor.py**
   - Lines 21-61: `logged_create()` function
   - Add streaming detection
   - Add conditional response inspection
   - Add safety checks

### No Changes Required
- `chatkit_server.py` - Works correctly with streaming
- `model_factory.py` - Correctly passes stream parameter
- `store_adapter.py` - Already fixed for MessageOutputItem
- Frontend files - No changes needed

## Testing Strategy

### Unit Testing Approach
**Challenge**: Interceptor is a wrapper, hard to unit test in isolation
**Approach**: Integration testing through actual chatbot usage

### Integration Test Cases

#### Test 1: Basic Streaming Message
```
Input: "hi"
Expected:
- Backend logs show streaming detection
- No AttributeError
- Response streams successfully
```

#### Test 2: Tool Calling with Streaming
```
Input: "list my tasks"
Expected:
- Tools are called during streaming
- Response includes task list
- No errors
```

#### Test 3: Multiple Messages
```
Input: Send 3 messages in sequence
Expected:
- All messages process successfully
- Consistent logging pattern
- No memory leaks
```

### Verification Checklist
- [ ] Backend starts without errors
- [ ] First message "hi" works
- [ ] Tool calls work (list tasks, add task)
- [ ] Multiple messages in sequence work
- [ ] Logs show streaming detection
- [ ] No AttributeError in logs
- [ ] Frontend displays responses correctly

## Rollback Plan

### If Fix Fails
1. Revert `llm_interceptor.py` to previous version
2. Temporarily disable interceptor by removing from `model_factory.py`
3. Investigate alternative approaches

### Rollback Command
```bash
git checkout HEAD -- backend/src/agents/llm_interceptor.py
```

## Performance Considerations

### Impact Analysis
- **Added Operations**: 1 dictionary lookup (`kwargs.get`)
- **Overhead**: Negligible (~1 microsecond)
- **Memory**: No additional allocations
- **Latency**: No impact on streaming performance

### Monitoring
- Watch for any latency increase in chatbot responses
- Monitor memory usage during extended conversations
- Check log file sizes (streaming logs are shorter)

## Security Considerations

### No Security Impact
- Fix is purely defensive (prevents crashes)
- No changes to authentication or authorization
- No exposure of sensitive data
- No changes to API surface

## Dependencies

### Internal Dependencies
- Agents SDK streaming behavior (unchanged)
- ChatKit integration (unchanged)
- Model factory configuration (unchanged)

### External Dependencies
- OpenAI API streaming protocol (stable)
- Cerebras API compatibility (confirmed working)

## Deployment

### Deployment Steps
1. Apply code changes to `llm_interceptor.py`
2. Restart backend server (uvicorn auto-reloads)
3. Test with simple message
4. Verify logs show streaming detection
5. Test tool calling functionality

### No Database Changes
- No migrations required
- No schema changes
- No data modifications

### No Frontend Changes
- No rebuild required
- No cache clearing needed
- No user action required

## Success Metrics

### Immediate Success Indicators
- Backend starts without errors
- First chatbot message succeeds
- Logs show "Streaming response - skipping response inspection"
- No AttributeError in logs

### Long-term Success Indicators
- Zero chatbot errors over 24 hours
- Consistent response times
- No memory leaks
- Clean error logs

## Documentation Updates

### Code Documentation
- Added inline comments explaining streaming detection
- Updated function docstring (if needed)

### User Documentation
- No user-facing documentation changes needed
- Internal debugging guide updated with streaming info

## Future Improvements

### Potential Enhancements
1. Add streaming response inspection (consume stream, log, re-stream)
2. Add metrics for streaming vs non-streaming requests
3. Add configurable logging levels
4. Add request/response timing measurements

### Not Planned
- Changing streaming behavior
- Modifying Agents SDK integration
- Altering model selection logic
