# ADR-003: Streaming Observability Architecture for LLM Tool Calling

**Status:** Accepted
**Date:** 2026-02-15
**Deciders:** Development Team
**Context:** Phase 3 AI Todo Assistant Chatbot

## Context and Problem Statement

During development and debugging of the AI chatbot, we encountered multiple tool calling issues that were difficult to diagnose. The primary challenge was lack of visibility into the LLM's streaming responses, particularly:

1. **Tool Call Detection**: No way to verify if Cerebras was actually calling tools
2. **Tool Arguments**: Couldn't see what arguments the LLM was passing
3. **Completion Status**: No visibility into finish reasons or tool call lifecycle
4. **Debugging Blind Spots**: Had to guess at what was happening in the streaming flow

The original LLM interceptor only logged non-streaming requests, providing zero observability for streaming tool calls, which is the primary mode of operation for our Cerebras backend.

## Decision Drivers

- **Debuggability**: Must be able to diagnose tool calling issues quickly
- **Transparency**: Need visibility into LLM behavior without modifying SDK
- **Performance**: Minimal overhead on streaming responses
- **Non-Invasiveness**: Cannot break Agents SDK stream processing
- **Production Readiness**: Logging must be production-appropriate (not too verbose)

## Considered Options

### Option 1: Add Logging Directly in Tool Handlers
**Pros:**
- Simple to implement
- Shows tool execution

**Cons:**
- ❌ Doesn't show if LLM called the tool
- ❌ No visibility into tool call arguments from LLM
- ❌ Can't diagnose issues before tool execution
- ❌ Doesn't help with streaming issues

### Option 2: Use OpenAI SDK Debug Mode
**Pros:**
- Built-in functionality
- No custom code

**Cons:**
- ❌ Too verbose for production
- ❌ Logs everything, not just tool calls
- ❌ Format not optimized for our use case
- ❌ May not work with Cerebras backend

### Option 3: Implement Custom Stream Wrapper for Tool Call Tracking
**Pros:**
- ✅ Focused on tool calling observability
- ✅ Doesn't modify SDK behavior
- ✅ Can control verbosity
- ✅ Works with any backend (Cerebras, OpenAI)
- ✅ Production-appropriate logging

**Cons:**
- Requires custom implementation
- Need to maintain wrapper
- Must implement full async stream protocol

### Option 4: Use External Observability Platform (e.g., LangSmith)
**Pros:**
- Professional tooling
- Rich features

**Cons:**
- ❌ Additional cost
- ❌ External dependency
- ❌ May not support Cerebras
- ❌ Overkill for current needs
- ❌ Data privacy concerns

## Decision Outcome

**Chosen option: Option 3 - Implement Custom Stream Wrapper for Tool Call Tracking**

We implement a `StreamingToolCallTracker` class that wraps async streams to intercept and log tool call information without modifying the stream data.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              Streaming Observability Architecture            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  LLM Request                                                │
│  ┌──────────────────────────────────────────────┐          │
│  │ intercept_llm_requests()                      │          │
│  │ - Log request parameters                      │          │
│  │ - Log tools available                         │          │
│  │ - Log messages and tool_choice                │          │
│  └──────────────────────────────────────────────┘          │
│                      ↓                                       │
│  ┌──────────────────────────────────────────────┐          │
│  │ OpenAI Client (Cerebras)                      │          │
│  │ - Makes streaming request                     │          │
│  └──────────────────────────────────────────────┘          │
│                      ↓                                       │
│  ┌──────────────────────────────────────────────┐          │
│  │ StreamingToolCallTracker                      │          │
│  │ ┌────────────────────────────────────────┐   │          │
│  │ │ Wraps Original Stream                   │   │          │
│  │ │ - Intercepts each chunk                 │   │          │
│  │ │ - Inspects for tool call deltas         │   │          │
│  │ │ - Accumulates tool call data            │   │          │
│  │ │ - Logs lifecycle events                 │   │          │
│  │ │ - Returns unmodified chunks             │   │          │
│  │ └────────────────────────────────────────┘   │          │
│  └──────────────────────────────────────────────┘          │
│                      ↓                                       │
│  ┌──────────────────────────────────────────────┐          │
│  │ Agents SDK                                    │          │
│  │ - Receives unmodified chunks                  │          │
│  │ - Processes stream normally                   │          │
│  │ - Executes tools                              │          │
│  └──────────────────────────────────────────────┘          │
│                                                              │
│  Logging Output (Structured)                                │
│  ┌──────────────────────────────────────────────┐          │
│  │ [LLM REQUEST] stream=True                     │          │
│  │ [OK] Tools: ['add_task', 'list_tasks', ...]  │          │
│  │ [LLM STREAM] New tool call detected at index 0│          │
│  │ [LLM STREAM] Tool call [0] name: add_task    │          │
│  │ [LLM STREAM] Finish reason: tool_calls        │          │
│  │ [LLM STREAM] Tool calls completed: 1          │          │
│  │   [0] add_task(id=...) args={...}            │          │
│  └──────────────────────────────────────────────┘          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Implementation Pattern

```python
class StreamingToolCallTracker:
    """Wraps an async stream to log tool calls as they arrive."""

    def __init__(self, stream):
        self._stream = stream
        self._tool_calls = {}  # index -> {name, arguments, id}
        self._has_content = False

    async def __anext__(self):
        chunk = await self._stream.__anext__()

        # Inspect chunk for tool calls
        if hasattr(chunk, 'choices') and chunk.choices:
            delta = chunk.choices[0].delta
            if delta and hasattr(delta, 'tool_calls') and delta.tool_calls:
                for tc in delta.tool_calls:
                    idx = tc.index
                    if idx not in self._tool_calls:
                        self._tool_calls[idx] = {"name": "", "arguments": "", "id": ""}
                        logger.info(f"[LLM STREAM] New tool call detected at index {idx}")

                    if tc.function and tc.function.name:
                        self._tool_calls[idx]["name"] = tc.function.name
                        logger.info(f"[LLM STREAM] Tool call [{idx}] name: {tc.function.name}")

                    if tc.function and tc.function.arguments:
                        self._tool_calls[idx]["arguments"] += tc.function.arguments

        # Return unmodified chunk
        return chunk
```

### Rationale

1. **Transparency**: Wraps stream without modifying data
2. **Focused**: Logs only tool calling information, not all content
3. **Incremental**: Logs as information arrives (detection, name, completion)
4. **Production-Ready**: Truncates arguments, structured logging
5. **Maintainable**: Clean class-based design, easy to understand

## Consequences

### Positive

- ✅ **Immediate Visibility**: See tool calls as they happen
- ✅ **Debugging Power**: Can diagnose tool calling issues quickly
- ✅ **Non-Invasive**: Doesn't break SDK stream processing
- ✅ **Backend Agnostic**: Works with Cerebras, OpenAI, or others
- ✅ **Production Appropriate**: Controlled verbosity, structured logs

### Negative

- ⚠️ Minimal performance overhead (~1ms per chunk)
- ⚠️ Requires maintenance if stream protocol changes
- ⚠️ Log volume increases (but focused on tool calls only)

### Neutral

- 📝 Need to implement full async stream protocol
- 📝 Should monitor log volume in production
- 📝 Can be disabled if not needed

## Observability Benefits

### Before (No Streaming Observability)
```
[LLM REQUEST] stream=True
[OK] Tools: ['add_task', 'list_tasks', ...]
... silence ...
[TOOL] Executing add_task: user_id=..., args=...
```
**Problem**: No visibility into whether LLM called the tool or how

### After (With StreamingToolCallTracker)
```
[LLM REQUEST] stream=True
[OK] Tools: ['add_task', 'list_tasks', ...]
[LLM STREAM] New tool call detected at index 0
[LLM STREAM] Tool call [0] name: add_task
[LLM STREAM] Finish reason: tool_calls
[LLM STREAM] Tool calls completed: 1
  [0] add_task(id=call_abc) args={"title":"Test","description":"..."}
[TOOL] Executing add_task: user_id=..., args=...
```
**Benefit**: Complete visibility into tool calling lifecycle

## Performance Considerations

### Overhead Analysis
- **Per-chunk inspection**: ~0.1ms (hasattr checks, dict operations)
- **Logging**: ~0.5ms per log line (I/O bound)
- **Total overhead**: <5ms per tool call (negligible vs network latency)

### Optimization Strategies
1. **Truncate arguments**: Limit to 200 chars in logs
2. **Structured logging**: Use consistent prefixes for easy filtering
3. **Conditional logging**: Could add log level controls if needed

## Implementation Guidelines

### When to Use
- ✅ Development and debugging
- ✅ Production (with appropriate log levels)
- ✅ Investigating tool calling issues
- ✅ Monitoring LLM behavior

### When Not to Use
- ❌ If log volume becomes problematic (can disable)
- ❌ If performance is critical (minimal impact though)

### Configuration
```python
# Enable/disable in model factory
def create_model_with_function_calling():
    client = AsyncOpenAI(...)

    # Enable interceptor for observability
    client = intercept_llm_requests(client)

    return OpenAIChatCompletionsModel(model=..., openai_client=client)
```

## Related Decisions

- Bug #4: LLM Interceptor Enhancement
- Related to debugging and observability strategy
- Complements tool execution logging (ADR-002)

## References

- Spec: `specs/llm-interceptor-enhancement/spec.md`
- Implementation: `backend/src/agents/llm_interceptor.py`
- Model Factory: `backend/src/agents/model_factory.py`

## Notes

This observability architecture proved invaluable during debugging. It helped identify:
- Bug #3: user_id extraction failure (saw tools being called but failing)
- Bug #5: Tool result injection (saw tools executing but results not displayed)

The pattern is reusable for other streaming observability needs and demonstrates the value of transparent instrumentation without modifying upstream libraries.