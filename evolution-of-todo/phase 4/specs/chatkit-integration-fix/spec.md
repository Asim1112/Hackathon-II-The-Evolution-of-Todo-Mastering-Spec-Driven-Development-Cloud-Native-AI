# ChatKit Integration Fix - Specification

**ID**: chatkit-integration-fix
**Status**: red
**Created**: 2026-02-13
**Priority**: critical

## Problem Statement

Current ChatKit server implementation does not follow the official ChatKit + Agents SDK integration pattern, causing:
1. Agent returns "FN_CALL=False" instead of natural responses
2. `AttributeError: 'MessageOutputItem' object has no attribute 'model_dump'`
3. Non-streaming execution instead of proper streaming

## Root Cause

**Architectural Mismatch:**
- Using `Runner.run()` (non-streaming) instead of `Runner.run_streamed()`
- Not creating `AgentContext` for ChatKit integration
- Not using `stream_agent_response()` helper for event conversion
- Manually creating events instead of proper ChatKit event streaming

**Reference**: Chatkit-SDK-Documentation.md lines 1536-1558 shows correct pattern

## Requirements

### Functional Requirements

**FR-1**: Agent must respond naturally to greetings
- Input: "hi"
- Expected: "Hello! I'm your todo assistant. How can I help you manage your tasks today?"
- Current: "FN_CALL=False"

**FR-2**: Agent must call tools for task operations
- Input: "show me all tasks"
- Expected: Calls `list_tasks` tool and returns results
- Current: Not tested due to FR-1 failure

**FR-3**: Streaming responses must work
- Events must stream to frontend in real-time
- No serialization errors

### Technical Requirements

**TR-1**: Use `Runner.run_streamed()` for agent execution
**TR-2**: Create `AgentContext` with thread, store, and request_context
**TR-3**: Use `stream_agent_response()` helper for event conversion
**TR-4**: Import from `chatkit.agents`: `AgentContext`, `simple_to_agent_input`, `stream_agent_response`

## Implementation Pattern (from documentation)

```python
from chatkit.agents import AgentContext, simple_to_agent_input, stream_agent_response

class TodoChatKitServer(ChatKitServer[RequestContext]):
    async def respond(self, thread, input_user_message, context):
        # Load history
        items_page = await self.store.load_thread_items(
            thread.id, after=None, limit=20, order="asc", context=context
        )

        # Convert to agent input
        input_items = await simple_to_agent_input(items_page.data)

        # Create AgentContext
        agent_context = AgentContext(
            thread=thread,
            store=self.store,
            request_context=context
        )

        # Get agent
        agent = await get_agent()

        # Run with STREAMING
        result = Runner.run_streamed(agent, input_items, context=agent_context)

        # Stream ChatKit events
        async for event in stream_agent_response(agent_context, result):
            yield event
```

## Files to Modify

1. `backend/src/agents/chatkit_server.py` - Complete rewrite of `respond()` method

## Acceptance Criteria

- [ ] Agent responds naturally to "hi" greeting
- [ ] Agent calls tools for task operations
- [ ] No AttributeError on MessageOutputItem
- [ ] Events stream properly to frontend
- [ ] Backend logs show proper tool calling
- [ ] Frontend displays responses without errors

## Non-Goals

- Fixing prompt engineering (separate concern)
- Optimizing performance
- Adding new features

## Dependencies

- chatkit.agents module (already installed)
- AgentContext, simple_to_agent_input, stream_agent_response helpers

## Risks

- May need to adjust prompt after fixing architecture
- Cerebras model behavior with streaming unknown
