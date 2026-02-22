# ADR-002: Tool Execution Security Model with Context-Based user_id Injection

**Status:** Accepted
**Date:** 2026-02-15
**Deciders:** Development Team
**Context:** Phase 3 AI Todo Assistant Chatbot

## Context and Problem Statement

The AI chatbot uses MCP (Model Context Protocol) tools to perform CRUD operations on user tasks. These tools require a `user_id` parameter to ensure data isolation - each user should only access their own tasks. However, the LLM (Large Language Model) generates tool calls with arguments, and we cannot trust the LLM to provide the correct `user_id`.

**Security Risk:** If the LLM could specify `user_id` in tool arguments, it could potentially access or modify other users' data, either through:
1. Malicious prompt injection
2. Model confusion or hallucination
3. Adversarial attacks on the model

We need a security model that ensures `user_id` always comes from the authenticated session context, never from LLM output.

## Decision Drivers

- **Security**: User data isolation must be guaranteed
- **Trust Boundary**: Clear separation between trusted (authentication) and untrusted (LLM) sources
- **Usability**: LLM should not need to know or specify user_id
- **Maintainability**: Pattern should be clear and easy to apply to new tools
- **Defense in Depth**: Multiple layers of protection

## Considered Options

### Option 1: Trust LLM to Provide Correct user_id
**Pros:**
- Simple implementation
- LLM has full control

**Cons:**
- ❌ **CRITICAL SECURITY FLAW**: LLM could access other users' data
- ❌ Vulnerable to prompt injection
- ❌ No defense against model errors
- ❌ Violates principle of least privilege

### Option 2: Remove user_id from Tool Signatures Entirely
**Pros:**
- LLM never sees user_id
- Simple tool schemas

**Cons:**
- Tools need user_id for database queries
- Would require global state or thread-local storage
- Harder to test tools in isolation
- Implicit dependencies are harder to maintain

### Option 3: Dual-Layer Security with Context Injection and Sanitization
**Pros:**
- ✅ user_id always comes from authenticated context
- ✅ LLM-provided user_id is explicitly removed (sanitization)
- ✅ Clear trust boundary
- ✅ Defense in depth
- ✅ Tools remain testable with explicit user_id parameter

**Cons:**
- Requires careful implementation in tool wrapper
- Need to maintain context navigation path
- Slightly more complex than Option 1

### Option 4: Middleware Layer for user_id Injection
**Pros:**
- Centralized security logic
- Could apply to all tools automatically

**Cons:**
- More architectural complexity
- Harder to debug
- Requires framework changes
- Overkill for current scale

## Decision Outcome

**Chosen option: Option 3 - Dual-Layer Security with Context Injection and Sanitization**

We implement a security model where:
1. **user_id is extracted from authenticated context** (trusted source)
2. **Any LLM-provided user_id is explicitly removed** (sanitization)
3. **Tool handler receives only the authenticated user_id**

### Implementation Pattern

```python
async def tool_wrapper(ctx: RunContextWrapper, args: str) -> str:
    import json

    # Parse LLM-provided arguments (UNTRUSTED)
    parsed_args = json.loads(args)

    # Extract user_id from authenticated context (TRUSTED)
    agent_ctx = ctx.context
    if hasattr(agent_ctx, 'request_context') and hasattr(agent_ctx.request_context, 'user_id'):
        user_id = agent_ctx.request_context.user_id  # TRUSTED SOURCE
    else:
        user_id = "unknown"
        logger.warning("[TOOL] Could not extract user_id from context")

    # CRITICAL SECURITY: Strip any LLM-provided user_id (SANITIZATION)
    parsed_args.pop("user_id", None)

    # Call handler with authenticated user_id + sanitized args
    result = await tool_handler(user_id=user_id, **parsed_args)
    return json.dumps(result)
```

### Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Trust Boundaries                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  TRUSTED ZONE                                               │
│  ┌──────────────────────────────────────────────┐          │
│  │ Authentication Layer (Better Auth)            │          │
│  │   ↓                                           │          │
│  │ RequestContext.user_id (from JWT)            │          │
│  │   ↓                                           │          │
│  │ AgentContext.request_context.user_id         │          │
│  │   ↓                                           │          │
│  │ Tool Wrapper Extraction                       │          │
│  └──────────────────────────────────────────────┘          │
│                      ↓                                       │
│  ═══════════════════════════════════════════════           │
│         SECURITY BOUNDARY (Sanitization)                    │
│  ═══════════════════════════════════════════════           │
│                      ↓                                       │
│  UNTRUSTED ZONE                                             │
│  ┌──────────────────────────────────────────────┐          │
│  │ LLM Output (tool call arguments)             │          │
│  │   ↓                                           │          │
│  │ parsed_args (may contain user_id)            │          │
│  │   ↓                                           │          │
│  │ Sanitization: parsed_args.pop("user_id")     │          │
│  └──────────────────────────────────────────────┘          │
│                      ↓                                       │
│  ┌──────────────────────────────────────────────┐          │
│  │ Tool Handler Call                             │          │
│  │ tool_handler(user_id=TRUSTED, **sanitized)   │          │
│  └──────────────────────────────────────────────┘          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Rationale

1. **Defense in Depth**: Two layers of protection (context extraction + sanitization)
2. **Explicit Trust Boundary**: Clear separation between trusted and untrusted sources
3. **Fail-Safe**: Even if LLM tries to provide user_id, it's removed
4. **Auditability**: Logging shows which user_id is used
5. **Testability**: Tools remain testable with explicit user_id parameter

## Consequences

### Positive

- ✅ **Strong Security**: User data isolation guaranteed
- ✅ **Defense Against Prompt Injection**: LLM cannot override user_id
- ✅ **Clear Trust Model**: Explicit about what's trusted vs untrusted
- ✅ **Auditability**: All tool calls logged with authenticated user_id
- ✅ **Maintainable**: Pattern is clear and easy to apply to new tools

### Negative

- ⚠️ Requires careful context navigation (correct path to user_id)
- ⚠️ Need to maintain sanitization for all tools
- ⚠️ Fallback to "unknown" could mask authentication issues

### Neutral

- 📝 Need to document the pattern for new tool implementations
- 📝 Should monitor "unknown" user_id in logs
- 📝 Context structure changes in SDK would require updates

## Security Considerations

### Attack Vectors Mitigated

1. **Prompt Injection**: Attacker cannot trick LLM into accessing other users' data
2. **Model Confusion**: Even if LLM hallucinates wrong user_id, it's ignored
3. **Parameter Tampering**: Explicit sanitization removes any user_id in arguments

### Remaining Risks

1. **Authentication Bypass**: If authentication layer is compromised, this doesn't help
   - Mitigation: Rely on Better Auth security
2. **Context Extraction Failure**: If context path breaks, falls back to "unknown"
   - Mitigation: Monitor logs for "unknown" user_id, alert on high rate
3. **Database Query Injection**: user_id is used in SQL queries
   - Mitigation: Use parameterized queries (SQLModel handles this)

## Implementation Guidelines

### For New Tools

When creating new MCP tools:

1. **Tool Signature**: Include `user_id: str` as first parameter
2. **Schema Stripping**: Remove `user_id` from LLM-visible schema
3. **Tool Wrapper**: Use standard pattern with context extraction + sanitization
4. **Database Queries**: Always filter by `user_id` for user-specific data
5. **Logging**: Log tool execution with authenticated `user_id`

### Example

```python
@mcp.tool()
async def new_tool(user_id: str, other_param: str) -> dict:
    """Tool description."""
    # Validation
    if not user_id or user_id == "unknown":
        raise ValueError("Invalid user_id")

    # Database query with user_id filter
    with _SessionContext() as session:
        query = select(Model).where(Model.owner_id == user_id)
        results = session.exec(query).all()
        return {"results": results}
```

## Related Decisions

- Bug #2: Tool Wrapper Parameter Handling Fix
- Bug #3: User ID Extraction Fix
- Related to authentication architecture (Better Auth integration)

## References

- Spec: `specs/tool-wrapper-parameter-fix/spec.md`
- Spec: `specs/user-id-extraction-fix/spec.md`
- Implementation: `backend/src/agents/chatkit_server.py` (tool_wrapper)
- MCP Tools: `backend/src/mcp/mcp_server.py`

## Notes

This security model is critical for multi-tenant applications where user data isolation is paramount. The dual-layer approach (context extraction + sanitization) provides defense in depth against various attack vectors.

The pattern should be applied consistently to all tools that access user-specific data. Any deviation from this pattern should be carefully reviewed for security implications.