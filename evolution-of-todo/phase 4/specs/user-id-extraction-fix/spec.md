# User ID Extraction Fix Specification

## Problem Statement

Tool calling was broken because the model could not successfully execute tools. `list_tasks()` was called repeatedly returning "You have no tasks" but `add_task()` was never called when the user requested task creation. This indicated a fundamental issue with tool execution.

**Evidence:**
- User says "create a task with title 'playing cricket'"
- `list_tasks()` called repeatedly (proves Cerebras supports tool calling)
- `add_task()` never called despite user request
- All tools returning empty results or failing silently

**Root Cause:**
The `user_id` extraction in the tool wrapper was completely broken. The code attempted to access `ctx.context.user_id` but `AgentContext` does not have a `user_id` attribute directly. The correct path is `ctx.context.request_context.user_id`.

As a result, ALL tool calls were using `user_id="unknown"`, causing:
- `list_tasks("unknown")` to always return empty (no tasks for unknown user)
- Model confusion: "user has no tasks" → doesn't call add_task
- Circular failure: model keeps checking if tasks exist, never creates them

**Technical Details:**
- `ctx.context` is an `AgentContext` object
- `AgentContext` has a `request_context` attribute of type `RequestContext`
- `RequestContext` has the `user_id` attribute
- Incorrect path: `ctx.context.user_id` → AttributeError (silently caught, defaults to "unknown")
- Correct path: `ctx.context.request_context.user_id`

## Requirements

### Functional Requirements
1. **Correct user_id Extraction**: Tool wrapper must extract authenticated user_id correctly
2. **User Isolation**: Each user must only see their own tasks
3. **Tool Execution**: All MCP tools must work with correct user context
4. **Error Visibility**: Extraction failures must be logged clearly

### Non-Functional Requirements
1. **Security**: user_id must come from authenticated context
2. **Reliability**: 100% success rate for user_id extraction
3. **Debuggability**: Clear logging when extraction fails

## Solution Approach

### Architecture
Fix the context navigation path in the tool wrapper to correctly traverse the object hierarchy from `RunContextWrapper` to `user_id`.

### Context Navigation Pattern
```
RunContextWrapper (ctx)
  └─ context: AgentContext
      └─ request_context: RequestContext
          └─ user_id: str
```

### Correct Implementation
```python
agent_ctx = ctx.context  # AgentContext
if hasattr(agent_ctx, 'request_context') and hasattr(agent_ctx.request_context, 'user_id'):
    user_id = agent_ctx.request_context.user_id
else:
    user_id = "unknown"
    logger.warning("[TOOL] Could not extract user_id from context")
```

### Components
- `tool_wrapper` function in `chatkit_server.py`
- Context navigation: `ctx.context.request_context.user_id`
- Error handling: hasattr checks with fallback
- Logging: Warning when extraction fails

### Data Flow
```
1. Tool call initiated by LLM
2. Agents SDK invokes tool_wrapper with RunContextWrapper
3. Tool wrapper navigates: ctx → context → request_context → user_id
4. Authenticated user_id extracted successfully
5. Tool handler called with correct user_id
6. Database query uses correct user_id
7. Results returned for authenticated user
```

## Acceptance Criteria
- [ ] user_id extraction succeeds for all tool calls
- [ ] add_task creates tasks for correct user
- [ ] list_tasks returns tasks for correct user
- [ ] All tools work with proper user isolation
- [ ] No "unknown" user_id in logs (except error cases)
- [ ] Model can successfully create and list tasks

## Constraints
- Must work with existing AgentContext structure
- Cannot modify Agents SDK or ChatKit library
- Must maintain security boundary
- Must handle edge cases gracefully

## Risks
- Context structure might change in future SDK versions
- hasattr checks might hide other errors
- Fallback to "unknown" might mask issues

## Implementation Notes

### Files to Modify
- `backend/src/agents/chatkit_server.py`: Fix context navigation in `tool_wrapper`

### Before (Broken)
```python
user_id = ctx.context.user_id if hasattr(ctx.context, 'user_id') else "unknown"
```

### After (Fixed)
```python
agent_ctx = ctx.context
if hasattr(agent_ctx, 'request_context') and hasattr(agent_ctx.request_context, 'user_id'):
    user_id = agent_ctx.request_context.user_id
else:
    user_id = "unknown"
    logger.warning("[TOOL] Could not extract user_id from context")
```

### Verification Test
```python
# Test correct path
agent_ctx = ctx.context
assert hasattr(agent_ctx, 'request_context')
assert hasattr(agent_ctx.request_context, 'user_id')
user_id = agent_ctx.request_context.user_id
assert user_id != "unknown"
assert isinstance(user_id, str)
```

## Testing Strategy
1. Create task with authenticated user
2. Verify task appears in list_tasks for same user
3. Verify task does NOT appear for different user
4. Test all 5 MCP tools with correct user_id
5. Monitor logs for "unknown" user_id warnings
6. Test edge case: missing context (should log warning)

## Security Implications

### User Isolation
- **Critical**: Correct user_id ensures data isolation
- **Risk**: Wrong user_id could expose other users' tasks
- **Mitigation**: Proper context navigation + database queries with user_id filter

### Authentication Flow
```
1. User authenticates → Better Auth generates JWT
2. Frontend sends request with X-User-Id header
3. Backend extracts user_id into RequestContext
4. AgentContext wraps RequestContext
5. Tool wrapper extracts from AgentContext.request_context.user_id
6. Database queries filtered by user_id
```

## Related Issues
- Bug #2: Tool wrapper parameter handling (same file, related fix)
- Bug #5: Tool result injection (depends on tools working correctly)