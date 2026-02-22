# User ID Extraction Fix Implementation Plan

## Scope and Dependencies

### In Scope
- Fix context navigation path in tool_wrapper
- Correct object hierarchy traversal from RunContextWrapper to user_id
- Add proper error handling with hasattr checks
- Maintain security boundary for user_id extraction

### Out of Scope
- Modifying AgentContext or RequestContext structure
- Changing Agents SDK or ChatKit library
- Modifying authentication mechanism
- Changing tool execution flow

### External Dependencies
- OpenAI Agents SDK (RunContextWrapper, AgentContext)
- ChatKit Python SDK (AgentContext structure)
- Better Auth (provides user_id in RequestContext)
- PostgreSQL database (for user-specific queries)

## Key Decisions and Rationale

### Decision 1: Context Navigation Approach
**Option 1**: Use direct attribute access (ctx.context.request_context.user_id)
**Option 2**: Use getattr with defaults
**Option 3**: Use hasattr checks with fallback
**Chosen**: Option 3 - hasattr checks with fallback
**Rationale**:
- Defensive programming - handles missing attributes gracefully
- Clear error path with logging
- Allows debugging without breaking system
- Explicit about what we're checking

### Decision 2: Fallback Strategy
**Option 1**: Raise exception if user_id not found
**Option 2**: Use "unknown" with warning
**Option 3**: Use empty string
**Chosen**: Option 2 - "unknown" with warning
**Rationale**:
- Allows system to continue functioning
- Clear signal in logs that something is wrong
- Enables debugging without breaking user experience
- Can be tightened to exception later if needed

### Decision 3: Logging Level
**Option 1**: Error level for missing user_id
**Option 2**: Warning level for missing user_id
**Option 3**: Info level for all extractions
**Chosen**: Option 2 - Warning for missing, Info for success
**Rationale**:
- Warning indicates problem but not critical failure
- Info level for normal operation aids debugging
- Doesn't spam logs with errors in development
- Clear signal for monitoring

## Implementation Details

### Context Object Hierarchy
```
RunContextWrapper (ctx)
  └─ context: AgentContext
      ├─ thread: ThreadMetadata
      ├─ store: Store
      └─ request_context: RequestContext
          └─ user_id: str
```

### Code Changes

#### Before (Broken)
```python
# WRONG: AgentContext doesn't have user_id directly
user_id = ctx.context.user_id if hasattr(ctx.context, 'user_id') else "unknown"
```

#### After (Fixed)
```python
# CORRECT: Navigate through request_context
agent_ctx = ctx.context
if hasattr(agent_ctx, 'request_context') and hasattr(agent_ctx.request_context, 'user_id'):
    user_id = agent_ctx.request_context.user_id
else:
    user_id = "unknown"
    logger.warning("[TOOL] Could not extract user_id from context")
```

### Verification Logic
```python
# Step-by-step verification for debugging
agent_ctx = ctx.context
assert isinstance(agent_ctx, AgentContext), "ctx.context should be AgentContext"

assert hasattr(agent_ctx, 'request_context'), "AgentContext should have request_context"
request_ctx = agent_ctx.request_context
assert isinstance(request_ctx, RequestContext), "request_context should be RequestContext"

assert hasattr(request_ctx, 'user_id'), "RequestContext should have user_id"
user_id = request_ctx.user_id
assert isinstance(user_id, str), "user_id should be string"
assert user_id != "unknown", "user_id should be authenticated value"
```

### Error Handling

#### Scenarios
1. **Normal case**: Full context chain exists, user_id extracted successfully
2. **Missing request_context**: AgentContext doesn't have request_context attribute
3. **Missing user_id**: RequestContext doesn't have user_id attribute
4. **None values**: Attributes exist but are None

#### Handling Strategy
```python
# Defensive checks at each level
agent_ctx = ctx.context
if not hasattr(agent_ctx, 'request_context'):
    logger.warning("[TOOL] AgentContext missing request_context")
    return "unknown"

request_ctx = agent_ctx.request_context
if request_ctx is None:
    logger.warning("[TOOL] request_context is None")
    return "unknown"

if not hasattr(request_ctx, 'user_id'):
    logger.warning("[TOOL] RequestContext missing user_id")
    return "unknown"

user_id = request_ctx.user_id
if user_id is None or user_id == "":
    logger.warning("[TOOL] user_id is None or empty")
    return "unknown"

return user_id
```

## Non-Functional Requirements

### Security
- **Requirement**: user_id must come from authenticated context only
- **Enforcement**: No fallback to LLM-provided values
- **Validation**: Log extraction path for audit
- **Testing**: Verify user isolation with correct user_id

### Reliability
- **Target**: 100% success rate for authenticated requests
- **Guarantee**: hasattr checks prevent AttributeError
- **Fallback**: "unknown" allows debugging
- **Monitoring**: Track "unknown" occurrences

### Performance
- **Target**: <0.1ms for context navigation
- **Measurement**: Attribute access is O(1)
- **Impact**: Negligible overhead

## Testing Strategy

### Unit Tests
```python
def test_correct_user_id_extraction():
    # Mock proper context chain
    # Verify user_id extracted correctly
    # Verify no "unknown" fallback
    pass

def test_missing_request_context():
    # Mock AgentContext without request_context
    # Verify fallback to "unknown"
    # Verify warning logged
    pass

def test_missing_user_id():
    # Mock RequestContext without user_id
    # Verify fallback to "unknown"
    # Verify warning logged
    pass

def test_none_values():
    # Mock context with None values
    # Verify fallback to "unknown"
    # Verify warning logged
    pass
```

### Integration Tests
```python
async def test_add_task_with_correct_user():
    # Authenticate as user A
    # Add task
    # Verify task has correct owner_id
    pass

async def test_list_tasks_user_isolation():
    # User A adds tasks
    # User B lists tasks
    # Verify user B sees only their tasks
    pass

async def test_all_tools_with_user_id():
    # Test all 5 MCP tools
    # Verify correct user_id used
    # Verify no "unknown" in logs
    pass
```

### Debugging Tests
```python
def test_context_structure():
    # Verify AgentContext has request_context
    # Verify RequestContext has user_id
    # Document actual structure
    pass
```

## Risk Analysis

### Top 3 Risks

1. **Context Structure Changes**
   - Risk: Future SDK updates change context hierarchy
   - Impact: Critical - user_id extraction breaks completely
   - Mitigation: Pin SDK versions, test before upgrading
   - Monitoring: Track "unknown" user_id in production logs

2. **Authentication Bypass**
   - Risk: user_id not properly set in RequestContext
   - Impact: Critical - all users see "unknown" data
   - Mitigation: Test authentication flow thoroughly
   - Monitoring: Alert on high "unknown" user_id rate

3. **User Data Leakage**
   - Risk: Wrong user_id causes data exposure
   - Impact: Critical - security breach
   - Mitigation: Test user isolation thoroughly
   - Monitoring: Audit logs for suspicious access patterns

## Rollback Plan

### If Issues Occur
1. **Immediate**: Revert to previous code (accept broken state)
2. **Fallback**: Hard-code test user_id for debugging
3. **Investigation**: Add extensive logging at each context level
4. **Fix**: Adjust navigation path based on findings
5. **Redeploy**: Test thoroughly with real authentication

### Rollback Code
```python
# Emergency rollback - use old broken path
user_id = ctx.context.user_id if hasattr(ctx.context, 'user_id') else "unknown"

# OR: Hard-code for debugging
user_id = "debug_user_id"  # TEMPORARY - REMOVE BEFORE PRODUCTION
```

## Deployment Strategy

### Pre-Deployment
1. Review context structure in debugger
2. Verify authentication flow
3. Run unit tests
4. Run integration tests with real auth
5. Test manually with authenticated requests

### Deployment
1. Deploy to staging
2. Test with real authentication
3. Verify user isolation
4. Monitor logs for "unknown" user_id
5. Deploy to production
6. Monitor closely for 24 hours

### Post-Deployment
1. Verify no "unknown" user_id in logs
2. Test all 5 MCP tools
3. Verify user isolation
4. Check database for correct owner_id values
5. Monitor error rates

## Success Criteria

- [ ] user_id extracted correctly for all authenticated requests
- [ ] No "unknown" user_id in normal operation
- [ ] All 5 MCP tools work correctly
- [ ] User isolation maintained
- [ ] add_task creates tasks with correct owner_id
- [ ] list_tasks returns only user's tasks
- [ ] Model can successfully create and list tasks

## Verification Checklist

### Code Review
- [ ] Context navigation path is correct
- [ ] hasattr checks at each level
- [ ] Fallback to "unknown" with warning
- [ ] Logging is appropriate

### Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing with real auth
- [ ] User isolation verified

### Security
- [ ] user_id comes from authenticated context only
- [ ] No LLM-provided user_id accepted
- [ ] User data properly isolated
- [ ] Audit logging in place

### Monitoring
- [ ] Track "unknown" user_id occurrences
- [ ] Alert on high "unknown" rate
- [ ] Monitor tool execution success rate
- [ ] Track user isolation violations