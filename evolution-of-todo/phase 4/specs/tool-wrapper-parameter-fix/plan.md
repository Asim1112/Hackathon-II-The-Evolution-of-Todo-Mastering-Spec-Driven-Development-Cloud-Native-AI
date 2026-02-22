# Tool Wrapper Parameter Handling Fix Implementation Plan

## Scope and Dependencies

### In Scope
- Add parameter sanitization in tool_wrapper function
- Remove LLM-provided user_id before spreading arguments
- Maintain security boundary between context and LLM output
- Apply fix to all 5 MCP tools consistently

### Out of Scope
- Modifying MCP tool signatures
- Changing tool schema generation
- Modifying Agents SDK tool execution
- Changing authentication mechanism

### External Dependencies
- OpenAI Agents SDK (FunctionTool, RunContextWrapper)
- MCP tools (add_task, list_tasks, complete_task, update_task, delete_task)
- Authentication context (RequestContext with user_id)

## Key Decisions and Rationale

### Decision 1: Sanitization vs Schema Enforcement
**Option 1**: Rely on schema stripping to prevent user_id in LLM output
**Option 2**: Add explicit sanitization in tool wrapper
**Option 3**: Validate and reject if user_id present
**Chosen**: Option 2 - Explicit sanitization
**Rationale**:
- Defense in depth - don't trust schema stripping alone
- LLM might include user_id despite schema
- Silent removal is safer than rejection (no user-facing errors)
- Maintains security boundary

### Decision 2: Sanitization Method
**Option 1**: Filter parsed_args before spreading
**Option 2**: Catch TypeError and retry without user_id
**Option 3**: Validate each parameter individually
**Chosen**: Option 1 - Filter before spreading
**Rationale**:
- Proactive prevention vs reactive handling
- Cleaner code, easier to understand
- No exception handling overhead
- Clear security intent

### Decision 3: Fallback Behavior
**Option 1**: Fail hard if user_id extraction fails
**Option 2**: Use "unknown" as fallback
**Option 3**: Skip tool execution
**Chosen**: Option 2 - "unknown" fallback with warning
**Rationale**:
- Graceful degradation
- Allows debugging without breaking system
- Clear logging for investigation
- Can be tightened later if needed

## Implementation Details

### Code Changes

#### Before (Broken)
```python
async def tool_wrapper(ctx: RunContextWrapper, args: str) -> str:
    import json
    parsed_args = json.loads(args)

    # BROKEN: ctx.context doesn't have user_id directly
    user_id = ctx.context.user_id if hasattr(ctx.context, 'user_id') else "unknown"

    # BROKEN: user_id might be in parsed_args, causing duplicate
    result = await tool_handler(user_id=user_id, **parsed_args)
    return json.dumps(result)
```

#### After (Fixed)
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

    logger.info(f"[TOOL] Executing {tool_handler.__name__}: user_id={user_id}, args={parsed_args}")

    # Call handler with authenticated user_id
    try:
        result = await tool_handler(user_id=user_id, **parsed_args)
        logger.info(f"[TOOL] {tool_handler.__name__} succeeded: {result}")
        return json.dumps(result)
    except Exception as e:
        logger.error(f"[TOOL] {tool_handler.__name__} failed: {e}")
        return json.dumps({"error": str(e), "status": "failed"})
```

### Security Model

#### Trust Boundaries
```
TRUSTED:
- RequestContext.user_id (from authentication)
- AgentContext (wraps RequestContext)
- RunContextWrapper (wraps AgentContext)

UNTRUSTED:
- LLM output (args string)
- parsed_args dictionary
- Any user_id in parsed_args
```

#### Sanitization Flow
```
1. LLM generates tool call (may include user_id)
2. Parse args to dictionary (untrusted)
3. Extract user_id from context (trusted)
4. Remove user_id from parsed_args (sanitization)
5. Call handler with trusted user_id + sanitized args
```

### Error Handling

#### Scenarios
1. **Normal case**: user_id extracted, args sanitized, tool succeeds
2. **Missing context**: user_id="unknown", log warning, continue
3. **Tool execution error**: Catch exception, return error JSON
4. **JSON parse error**: Let it propagate (indicates SDK issue)

#### Logging Strategy
```python
# Success
logger.info(f"[TOOL] Executing {tool_name}: user_id={user_id}, args={args}")
logger.info(f"[TOOL] {tool_name} succeeded: {result}")

# Warning
logger.warning("[TOOL] Could not extract user_id from context")

# Error
logger.error(f"[TOOL] {tool_name} failed: {error}")
```

## Non-Functional Requirements

### Security
- **Requirement**: user_id must always come from authenticated context
- **Enforcement**: Explicit sanitization removes untrusted user_id
- **Validation**: Log user_id source for audit trail
- **Testing**: Attempt to override user_id via LLM, verify it's ignored

### Reliability
- **Target**: 100% success rate for parameter handling
- **Guarantee**: pop() with default never raises exception
- **Fallback**: "unknown" user_id allows debugging
- **Monitoring**: Track "unknown" user_id occurrences

### Performance
- **Target**: <0.1ms overhead for sanitization
- **Measurement**: dict.pop() is O(1)
- **Impact**: Negligible compared to tool execution time

## Testing Strategy

### Unit Tests
```python
def test_user_id_sanitization():
    # Mock LLM args with user_id
    args = '{"user_id": "malicious", "title": "Test"}'
    # Verify user_id is removed
    # Verify authenticated user_id is used
    pass

def test_missing_context():
    # Mock context without request_context
    # Verify fallback to "unknown"
    # Verify warning is logged
    pass

def test_all_tools():
    # Test each of 5 MCP tools
    # Verify no TypeError
    # Verify correct user_id used
    pass
```

### Integration Tests
```python
async def test_delete_task():
    # Create task as user A
    # Attempt to delete as user A
    # Verify success
    pass

async def test_user_isolation():
    # Create task as user A
    # Attempt to delete as user B
    # Verify PermissionError
    pass
```

### Security Tests
```python
async def test_user_id_override_attempt():
    # LLM tries to include user_id in args
    # Verify it's ignored
    # Verify authenticated user_id is used
    pass
```

## Risk Analysis

### Top 3 Risks

1. **Other Parameters with Similar Issues**
   - Risk: Other parameters might have similar conflicts
   - Impact: Medium - could cause similar TypeErrors
   - Mitigation: Review all tool schemas, test thoroughly
   - Monitoring: Watch for TypeError in tool execution

2. **Context Structure Changes**
   - Risk: Future SDK updates change context structure
   - Impact: High - user_id extraction would break
   - Mitigation: Pin SDK versions, test before upgrading
   - Monitoring: Track "unknown" user_id in logs

3. **Security Bypass**
   - Risk: LLM finds way to override user_id
   - Impact: Critical - could access other users' data
   - Mitigation: Explicit sanitization, security testing
   - Monitoring: Audit logs for suspicious user_id patterns

## Rollback Plan

### If Issues Occur
1. **Immediate**: Revert to previous tool_wrapper code
2. **Fallback**: Accept TypeError for delete_task (document workaround)
3. **Investigation**: Review logs for specific failure
4. **Fix**: Adjust sanitization logic
5. **Redeploy**: Test thoroughly

### Rollback Code
```python
# Emergency rollback - remove sanitization
# parsed_args.pop("user_id", None)  # DISABLED

# Accept potential TypeError
result = await tool_handler(user_id=user_id, **parsed_args)
```

## Deployment Strategy

### Pre-Deployment
1. Review code changes
2. Run unit tests (all tools)
3. Run security tests
4. Test manually with all 5 tools

### Deployment
1. Deploy to staging
2. Test delete_task specifically
3. Test all other tools
4. Monitor logs for errors
5. Deploy to production

### Post-Deployment
1. Verify all tools work
2. Check for "unknown" user_id in logs
3. Monitor error rates
4. Test user isolation

## Success Criteria

- [ ] delete_task works without TypeError
- [ ] All 5 MCP tools work correctly
- [ ] No "unknown" user_id in normal operation
- [ ] User isolation maintained
- [ ] Security tests pass
- [ ] No parameter conflicts