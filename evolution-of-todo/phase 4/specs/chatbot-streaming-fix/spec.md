# Specification: ChatBot Streaming Response Bug Fix

## Metadata
- **Feature**: ChatBot Streaming Response Handler
- **Type**: Bug Fix
- **Priority**: Critical
- **Status**: Implemented
- **Date**: 2026-02-15

## Problem Statement

### Current Behavior
When a user sends a message to the AI chatbot (e.g., "hi"), the system fails with an `AttributeError`:

```
AttributeError: 'AsyncStream' object has no attribute 'choices'
```

The error occurs in `backend/src/agents/llm_interceptor.py` at line 49.

### Expected Behavior
The chatbot should:
1. Accept user messages without errors
2. Stream responses back to the frontend
3. Log request/response information for debugging
4. Handle both streaming and non-streaming LLM responses correctly

### Impact
- **Severity**: Critical - chatbot is completely non-functional
- **Scope**: All chatbot interactions fail
- **User Experience**: Users see "There was an error while generating the assistant's response"
- **Other Features**: Task CRUD operations work fine (isolated issue)

## Root Cause Analysis

### Technical Details
The `llm_interceptor.py` module wraps the OpenAI client to log LLM requests and responses. The interceptor attempts to access `response.choices` on all responses:

```python
if response.choices:  # Line 49
    message = response.choices[0].message
    # ... inspection logic
```

### Why It Fails
When the Agents SDK calls the LLM with `stream=True`:
- The API returns an `AsyncStream` object for streaming responses
- `AsyncStream` objects don't have a `choices` attribute
- The code doesn't differentiate between streaming and non-streaming responses
- This causes an `AttributeError` when trying to access `response.choices`

### Affected Code Path
1. User sends message → ChatKit server
2. `chatkit_server.py:respond()` → Creates agent and runs streaming execution
3. `Runner.run_streamed()` → Calls model with `stream=True`
4. `model_factory.py` → Creates OpenAI client with interceptor
5. `llm_interceptor.py:logged_create()` → Tries to access `response.choices` ❌

## Requirements

### Functional Requirements
1. **FR-1**: Interceptor must detect streaming vs non-streaming requests
2. **FR-2**: For non-streaming requests, inspect `response.choices` as before
3. **FR-3**: For streaming requests, skip response inspection and return stream
4. **FR-4**: Log appropriate messages for both request types
5. **FR-5**: Chatbot must respond to simple messages like "hi"

### Non-Functional Requirements
1. **NFR-1**: No performance degradation
2. **NFR-2**: Maintain existing logging for non-streaming requests
3. **NFR-3**: No breaking changes to other components
4. **NFR-4**: Clear log messages indicating streaming vs non-streaming

### Constraints
- Must work with both Cerebras and OpenAI models
- Must maintain compatibility with Agents SDK streaming
- Cannot modify the Agents SDK or ChatKit libraries
- Must preserve existing debugging capabilities

## Acceptance Criteria

### Success Criteria
- [ ] User can send "hi" to chatbot without errors
- [ ] Backend logs show "Streaming response - skipping response inspection"
- [ ] No `AttributeError` appears in backend terminal
- [ ] Assistant responds with appropriate message
- [ ] Frontend displays response without errors
- [ ] Non-streaming requests (if any) still log response details

### Test Cases

#### TC-1: Streaming Request (Primary Use Case)
**Given**: User is on dashboard with chatbot open
**When**: User types "hi" and sends message
**Then**:
- Backend logs show streaming detection
- No AttributeError occurs
- Assistant responds successfully
- Frontend displays response

#### TC-2: Tool Calling with Streaming
**Given**: User asks to "list my tasks"
**When**: Agent makes tool calls during streaming
**Then**:
- Tool calls execute successfully
- Response streams back to user
- No errors in logs

#### TC-3: Non-Streaming Request (Edge Case)
**Given**: System makes non-streaming LLM call (if applicable)
**When**: Request completes
**Then**:
- Response inspection logs appear
- Tool calls are logged if present
- No errors occur

## Out of Scope
- Modifying streaming behavior of Agents SDK
- Changing model selection logic
- Altering tool registration mechanism
- Frontend UI changes
- Authentication flow modifications

## Dependencies
- Agents SDK streaming implementation
- ChatKit server integration
- OpenAI/Cerebras API compatibility
- Existing logging infrastructure

## Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Streaming detection fails | High | Low | Test with both Cerebras and OpenAI |
| Logging becomes too verbose | Low | Medium | Keep streaming logs concise |
| Non-streaming requests break | Medium | Low | Add hasattr() checks for safety |
| Performance overhead | Low | Low | Minimal - just boolean check |

## References
- Error traceback from user report
- `backend/src/agents/llm_interceptor.py`
- `backend/src/agents/chatkit_server.py`
- Agents SDK documentation on streaming
