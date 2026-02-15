# Tool Wrapper Parameter Handling Fix Specification

## Problem Statement

The `delete_task` tool was failing with a TypeError indicating duplicate `user_id` keyword arguments. This prevented users from deleting tasks through the chat interface.

**Evidence:**
- Error: `TypeError: src.mcp.mcp_server.delete_task() got multiple values for keyword argument 'user_id'`
- Occurred in `chatkit_server.py` line 98 in the tool wrapper
- All MCP tools were potentially affected (add_task, list_tasks, complete_task, update_task, delete_task)

**Root Cause:**
The `tool_wrapper` function in `chatkit_server.py` was passing `user_id` explicitly as a keyword argument while also spreading `**parsed_args` which contained `user_id` from the LLM's tool call. This resulted in the function receiving `user_id` twice, causing a Python TypeError.

**Technical Details:**
- Tool schemas had `user_id` removed from the LLM-visible schema (security measure)
- Tool wrapper injected `user_id` from authenticated context
- However, LLM sometimes included `user_id` in its arguments despite schema stripping
- Both explicit injection and spread operator passed `user_id` to the handler

## Requirements

### Functional Requirements
1. **Single user_id Parameter**: Tool handlers must receive exactly one `user_id` parameter
2. **Security Enforcement**: `user_id` must come from authenticated context, not LLM output
3. **LLM Flexibility**: System must handle cases where LLM includes `user_id` in arguments
4. **All Tools Working**: Fix must apply to all 5 MCP tools consistently

### Non-Functional Requirements
1. **Security**: `user_id` injection must be tamper-proof
2. **Reliability**: No tool call failures due to parameter conflicts
3. **Maintainability**: Solution must be clear and easy to understand

## Solution Approach

### Architecture
Add parameter sanitization in the tool wrapper to remove any LLM-provided `user_id` before spreading arguments to the tool handler.

### Parameter Handling Pattern
1. **Parse** LLM arguments from JSON string
2. **Extract** authenticated `user_id` from context
3. **Remove** any `user_id` from parsed arguments (sanitization)
4. **Inject** authenticated `user_id` as explicit parameter
5. **Spread** remaining arguments to tool handler

### Security Model
- **Trust Boundary**: Context (authenticated) vs LLM output (untrusted)
- **Injection Point**: Tool wrapper (after authentication, before execution)
- **Sanitization**: Strip untrusted `user_id` before use
- **Enforcement**: Explicit parameter takes precedence

### Components
- `tool_wrapper` function in `chatkit_server.py`
- `parsed_args.pop("user_id", None)`: Sanitization step
- Context navigation: `ctx.context.request_context.user_id`

### Data Flow
```
1. LLM generates tool call with arguments (may include user_id)
2. Tool wrapper receives RunContextWrapper and args string
3. Parse args to dictionary
4. Extract authenticated user_id from context
5. Remove any user_id from parsed_args (sanitization)
6. Call handler with user_id=<authenticated> + **parsed_args
7. Handler receives exactly one user_id parameter
```

## Acceptance Criteria
- [ ] delete_task works without TypeError
- [ ] All 5 MCP tools work correctly
- [ ] user_id always comes from authenticated context
- [ ] LLM-provided user_id is ignored (security)
- [ ] No parameter conflicts occur
- [ ] Error handling is robust

## Constraints
- Must maintain security boundary
- Cannot modify MCP tool signatures
- Must work with all tool types
- Must handle malicious LLM attempts to override user_id

## Risks
- Other parameters might have similar conflicts
- Future tools might have different parameter patterns
- Schema stripping might not be sufficient

## Implementation Notes

### Files to Modify
- `backend/src/agents/chatkit_server.py`: Modify `tool_wrapper` function in `_create_function_tools()`

### Key Code Pattern
```python
async def tool_wrapper(ctx: RunContextWrapper, args: str) -> str:
    import json

    # Parse LLM-provided arguments
    parsed_args = json.loads(args)

    # Extract user_id from authenticated context (security boundary)
    agent_ctx = ctx.context
    if hasattr(agent_ctx, 'request_context') and hasattr(agent_ctx.request_context, 'user_id'):
        user_id = agent_ctx.request_context.user_id
    else:
        user_id = "unknown"
        logger.warning("[TOOL] Could not extract user_id from context")

    # CRITICAL: Strip any LLM-provided user_id (sanitization)
    parsed_args.pop("user_id", None)

    # Call handler with authenticated user_id
    result = await tool_handler(user_id=user_id, **parsed_args)
    return json.dumps(result)
```

### Security Considerations
1. **Never trust LLM output for authentication**: user_id must come from context
2. **Explicit sanitization**: Always remove untrusted user_id before spreading args
3. **Fail-safe default**: Use "unknown" if context extraction fails
4. **Logging**: Warn when context extraction fails for debugging

## Testing Strategy
1. Test delete_task with valid task_id
2. Test all 5 MCP tools for parameter conflicts
3. Test with LLM attempting to provide user_id
4. Test with missing context (edge case)
5. Verify security: LLM cannot override user_id

## Related Issues
- Bug #1: Message ID collision (fixed in same session)
- Bug #3: user_id extraction failure (related context navigation issue)