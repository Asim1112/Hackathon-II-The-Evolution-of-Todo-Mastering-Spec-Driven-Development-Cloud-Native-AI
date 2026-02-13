# STEP 5: Change Record

**Feature**: Agent Tool Calling System Restoration
**Date**: 2026-02-12
**Status**: Root-Cause Investigation - Awaiting Approval

---

## Purpose

This document lists every required change to restore the agent tool calling system to correct operation. Changes are organized by priority and file location.

**NO CODE IS IMPLEMENTED YET. THIS IS A CHANGE PLAN AWAITING APPROVAL.**

---

## Change Priority Levels

- **P0 (Critical)**: System cannot function without this change
- **P1 (High)**: Required for correct operation
- **P2 (Medium)**: Required for reliability and monitoring
- **P3 (Low)**: Nice-to-have improvements

---

## P0 Changes (Critical - System Blocking)

### P0-1: Add Tool Extraction Utility

**File**: `backend/src/agents/tool_utils.py` (NEW FILE)

**Purpose**: Extract tools from agent's MCP servers and convert to OpenAI format

**Changes**:
1. Create new file `tool_utils.py`
2. Implement `extract_tools_from_agent(agent: Agent) -> list[dict]`
3. Implement `convert_mcp_tool_to_openai_format(mcp_tool) -> dict`
4. Add logging for tool extraction
5. Add error handling for MCP connection failures

**Dependencies**: None

**Rationale**: Tools must be extracted from MCP servers before they can be passed to the LLM.

---

### P0-2: Pass Tools to Runner

**File**: `backend/src/agents/chatkit_server.py`

**Location**: Line 166 in `respond()` method

**Purpose**: Include tools in Runner.run_streamed() call

**Changes**:
1. Import `extract_tools_from_agent` from `tool_utils`
2. Before `Runner.run_streamed()` call, extract tools: `tools = await extract_tools_from_agent(self.agent)`
3. Add tools parameter to Runner call: `Runner.run_streamed(agent, input_items, context=agent_context, tools=tools)`
4. Add logging: `logger.info(f"Running agent with {len(tools)} tools")`
5. Handle case where tool extraction fails

**Dependencies**: P0-1

**Rationale**: This is the exact point where the system breaks. Tools must be passed to Runner.

**CRITICAL NOTE**: This assumes `Runner.run_streamed()` accepts a `tools` parameter. If it doesn't, we need to investigate the SDK's API and potentially use a different approach.

---

### P0-3: Verify MCP Server Connection on Startup

**File**: `backend/src/api/main.py`

**Location**: In `lifespan()` context manager, after database initialization

**Purpose**: Fail fast if MCP server is not reachable

**Changes**:
1. Import MCP server instance from `chatkit_server`
2. Add `verify_mcp_connection()` function
3. Call verification during startup
4. Raise exception if verification fails
5. Log success message if verification passes

**Dependencies**: None

**Rationale**: System should not start if MCP server is unavailable.

---

## P1 Changes (High - Required for Correct Operation)

### P1-1: Add Model Function Calling Test

**File**: `backend/src/agents/model_factory.py` (NEW FILE)

**Purpose**: Test if model supports function calling and provide fallback

**Changes**:
1. Create new file `model_factory.py`
2. Implement `test_function_calling(model) -> bool`
3. Implement `create_model_with_function_calling() -> OpenAIChatCompletionsModel`
4. Add logic to test Cerebras first, fallback to OpenAI if needed
5. Add comprehensive logging

**Dependencies**: P1-2 (settings)

**Rationale**: Cerebras may not support function calling. We need to detect this and fallback to OpenAI.

---

### P1-2: Add OpenAI Configuration Settings

**File**: `backend/src/config/settings.py`

**Location**: In `Settings` class

**Purpose**: Support OpenAI as fallback for function calling

**Changes**:
1. Add `openai_api_key: str = ""`
2. Add `openai_model: str = "gpt-4-turbo-preview"`
3. Add `use_openai_for_tools: bool = False`
4. Add `auto_detect_function_calling: bool = True`
5. Update validation to require either Cerebras or OpenAI key

**Dependencies**: None

**Rationale**: Need configuration to support OpenAI fallback.

---

### P1-3: Update Environment File

**File**: `backend/.env`

**Purpose**: Add OpenAI configuration

**Changes**:
1. Add `OPENAI_API_KEY=` (empty, user will fill)
2. Add `USE_OPENAI_FOR_TOOLS=false`
3. Add `AUTO_DETECT_FUNCTION_CALLING=true`
4. Add comments explaining when to use OpenAI

**Dependencies**: P1-2

**Rationale**: Environment variables needed for new settings.

---

### P1-4: Use Model Factory in ChatKit Server

**File**: `backend/src/agents/chatkit_server.py`

**Location**: In `_create_cerebras_model()` function (line 46)

**Purpose**: Replace direct model creation with factory that supports fallback

**Changes**:
1. Import `create_model_with_function_calling` from `model_factory`
2. Replace `_create_cerebras_model()` implementation with call to factory
3. Remove direct AsyncOpenAI client creation
4. Update logging

**Dependencies**: P1-1

**Rationale**: Use tested model with function calling support.

---

### P1-5: Add Tool Execution Verification

**File**: `backend/src/agents/chatkit_server.py`

**Location**: After `Runner.run_streamed()` call in `respond()` method

**Purpose**: Verify that tools were actually called when expected

**Changes**:
1. Add logic to check if response contains tool calls
2. Log tool call information
3. Add assertion that tools were executed (in debug mode)
4. Track metrics for tool usage

**Dependencies**: P0-2

**Rationale**: Detect if tools are still not being called after fix.

---

## P2 Changes (Medium - Required for Reliability)

### P2-1: Add Comprehensive Logging

**File**: `backend/src/agents/chatkit_server.py`

**Location**: Throughout `respond()` method

**Purpose**: Enable debugging of tool calling flow

**Changes**:
1. Log when conversation history is loaded
2. Log when tools are extracted
3. Log when Runner is called
4. Log when tool calls are detected
5. Log when tool results are received
6. Log when final response is generated

**Dependencies**: None

**Rationale**: Future debugging requires visibility into the flow.

---

### P2-2: Add Logging Configuration

**File**: `backend/src/config/settings.py`

**Location**: In `Settings` class

**Purpose**: Control logging verbosity

**Changes**:
1. Add `log_level: str = "INFO"`
2. Add `log_llm_requests: bool = False` (can be expensive)
3. Add `log_llm_responses: bool = False`
4. Add `log_tool_calls: bool = True`
5. Add `log_tool_results: bool = True`
6. Add `log_mcp_requests: bool = False`

**Dependencies**: None

**Rationale**: Allow fine-grained control over logging.

---

### P2-3: Add MCP Health Check Endpoint

**File**: `backend/src/api/routes/health.py` (NEW FILE)

**Purpose**: Expose MCP server health status

**Changes**:
1. Create new health check router
2. Add `/health/mcp` endpoint
3. Check MCP server connectivity
4. Return tool count and status
5. Mount router in main.py

**Dependencies**: None

**Rationale**: Allow monitoring of MCP server status.

---

### P2-4: Add Tool Calling Metrics

**File**: `backend/src/agents/metrics.py` (NEW FILE)

**Purpose**: Track tool calling statistics

**Changes**:
1. Create metrics module
2. Track tool call count by tool name
3. Track tool execution time
4. Track tool success/failure rate
5. Expose metrics via endpoint

**Dependencies**: None

**Rationale**: Monitor system health and detect issues.

---

### P2-5: Fix Message ID Generation

**File**: `backend/src/agents/store_adapter.py`

**Location**: In `generate_item_id()` method (line 357)

**Purpose**: Ensure message IDs are truly unique

**Changes**:
1. Replace current ID generation with UUID-based approach
2. Add format: `msg_{uuid.uuid4().hex}`
3. Add collision detection (check if ID exists before using)
4. Add logging for ID generation
5. Add retry logic if collision detected

**Dependencies**: None

**Rationale**: Prevent message corruption from ID collisions.

---

### P2-6: Add Message Integrity Verification

**File**: `backend/src/agents/store_adapter.py`

**Location**: In `add_thread_item()` method (line 273)

**Purpose**: Prevent message overwrites

**Changes**:
1. Before saving, check if message ID already exists
2. If exists, raise exception (don't silently overwrite)
3. Use INSERT instead of UPSERT
4. Add logging for save operations
5. Add transaction handling

**Dependencies**: P2-5

**Rationale**: Enforce message immutability.

---

## P3 Changes (Low - Nice-to-Have)

### P3-1: Add Tool Calling Settings

**File**: `backend/src/config/settings.py`

**Location**: In `Settings` class

**Purpose**: Fine-tune tool calling behavior

**Changes**:
1. Add `tool_choice: str = "auto"`
2. Add `max_tool_calls_per_turn: int = 5`
3. Add `tool_timeout_seconds: int = 30`
4. Add `retry_failed_tools: bool = True`
5. Add `max_tool_retries: int = 3`

**Dependencies**: None

**Rationale**: Allow tuning of tool calling behavior.

---

### P3-2: Add Database Consistency Verification

**File**: `backend/src/agents/verification.py` (NEW FILE)

**Purpose**: Verify database state matches agent claims

**Changes**:
1. Create verification module
2. Implement `verify_agent_claims(message: str, user_id: str)`
3. Parse message for action claims
4. Query database to verify claims
5. Log discrepancies
6. Optionally raise exceptions in strict mode

**Dependencies**: None

**Rationale**: Catch future regressions where agent hallucinates.

---

### P3-3: Add End-to-End Test

**File**: `backend/tests/test_tool_calling.py` (NEW FILE)

**Purpose**: Automated test for tool calling flow

**Changes**:
1. Create test file
2. Implement `test_add_task_end_to_end()`
3. Implement `test_list_tasks_end_to_end()`
4. Implement `test_complete_task_end_to_end()`
5. Verify database state after each operation

**Dependencies**: All P0 and P1 changes

**Rationale**: Prevent future regressions.

---

### P3-4: Add System Prompt Enhancement

**File**: `backend/src/agents/prompts.py`

**Location**: In `get_system_prompt()` function

**Purpose**: Explicitly instruct agent to use tools

**Changes**:
1. Add section: "CRITICAL: You MUST use the provided tools to perform actions"
2. Add section: "NEVER claim to perform actions without calling tools"
3. Add section: "ALWAYS call list_tasks before claiming task counts"
4. Add examples of correct tool usage
5. Add examples of incorrect behavior to avoid

**Dependencies**: None

**Rationale**: Reinforce tool usage even if technical fix works.

---

### P3-5: Add Frontend Error Handling

**File**: `frontend/src/components/Chat.tsx` (or equivalent)

**Purpose**: Handle cases where agent fails to execute tools

**Changes**:
1. Add error detection for hallucinated responses
2. Show warning if agent claims action but no state change
3. Add retry button
4. Add feedback mechanism

**Dependencies**: None

**Rationale**: Improve user experience if issues recur.

---

## Investigation Tasks

These are not code changes, but investigations needed to inform implementation:

### INV-1: Verify Runner.run_streamed() API

**Purpose**: Confirm if Runner accepts `tools` parameter

**Actions**:
1. Check OpenAI Agents SDK documentation
2. Inspect Runner class source code
3. Test with explicit tools parameter
4. Document findings

**Outcome**: Determines if P0-2 approach is correct or needs modification

---

### INV-2: Test Cerebras Function Calling Support

**Purpose**: Confirm if Cerebras llama-3.3-70b supports function calling

**Actions**:
1. Create minimal test script
2. Call Cerebras API with tools parameter
3. Check if response includes tool_calls
4. Document findings

**Outcome**: Determines if P1-1 fallback is necessary

---

### INV-3: Analyze FN_CALL Source

**Purpose**: Find where FN_CALL is set and what it means

**Actions**:
1. Search OpenAI Agents SDK source code
2. Search AsyncOpenAI client source code
3. Add debug logging to capture stack trace
4. Document findings

**Outcome**: Better understanding of the error message

---

## Implementation Order

### Phase 1: Critical Fixes (Day 1)
1. INV-1: Verify Runner API
2. INV-2: Test Cerebras function calling
3. P0-1: Add tool extraction utility
4. P0-2: Pass tools to Runner
5. P0-3: Verify MCP connection on startup
6. Test: Verify tools are being called

### Phase 2: Fallback Support (Day 1-2)
1. P1-2: Add OpenAI settings
2. P1-3: Update environment file
3. P1-1: Add model factory
4. P1-4: Use model factory in ChatKit server
5. Test: Verify fallback works

### Phase 3: Verification (Day 2)
1. P1-5: Add tool execution verification
2. P2-1: Add comprehensive logging
3. P2-2: Add logging configuration
4. Test: Verify logging captures all events

### Phase 4: Reliability (Day 2-3)
1. P2-5: Fix message ID generation
2. P2-6: Add message integrity verification
3. P2-3: Add MCP health check
4. P2-4: Add tool calling metrics
5. Test: Verify message integrity

### Phase 5: Polish (Day 3+)
1. P3-1: Add tool calling settings
2. P3-2: Add database consistency verification
3. P3-3: Add end-to-end test
4. P3-4: Enhance system prompt
5. P3-5: Add frontend error handling

---

## Rollback Plan

If changes cause issues:

1. **Immediate Rollback**: Revert P0-2 (remove tools parameter)
2. **Partial Rollback**: Keep logging (P2-1) but revert tool passing
3. **Full Rollback**: Revert all changes, system returns to current (broken) state

**Note**: Current state is already broken, so rollback is not ideal. Better to fix forward.

---

## Testing Strategy

### Unit Tests
- Test tool extraction from MCP servers
- Test MCP tool to OpenAI format conversion
- Test message ID generation uniqueness
- Test model function calling detection

### Integration Tests
- Test full tool calling flow (user message → tool execution → response)
- Test MCP server connectivity
- Test model fallback (Cerebras → OpenAI)
- Test message persistence

### Manual Tests
- Send "Add a task to buy milk" and verify task is created
- Send "List my tasks" and verify correct count
- Send "Complete task 5" and verify status changes
- Check database state matches agent claims

---

## Success Criteria

The changes are successful when:

1. ✓ Agent calls tools instead of hallucinating
2. ✓ Database state matches agent claims
3. ✓ No FN_CALL=False errors
4. ✓ All 5 MCP tools are accessible
5. ✓ Tool execution is logged and visible
6. ✓ Message IDs are unique and stable
7. ✓ System works with either Cerebras or OpenAI
8. ✓ End-to-end tests pass

---

## Risk Assessment

### High Risk Changes
- **P0-2**: Modifying Runner call could break streaming
- **P1-4**: Changing model creation could break authentication

**Mitigation**: Test thoroughly in development before production

### Medium Risk Changes
- **P2-5**: Changing ID generation could break existing conversations
- **P2-6**: Adding integrity checks could reject valid operations

**Mitigation**: Add feature flags to disable if issues occur

### Low Risk Changes
- **P2-1**: Adding logging (read-only)
- **P3-4**: Updating system prompt (easily reversible)

**Mitigation**: None needed

---

## Dependencies

### External Dependencies
- OpenAI Agents SDK (must support tools parameter)
- Cerebras API (may or may not support function calling)
- OpenAI API (fallback option)
- FastMCP (must provide tool listing)

### Internal Dependencies
- MCP server must be running
- Database must be accessible
- Environment variables must be set

---

## Estimated Effort

- **Investigation**: 2-4 hours
- **P0 Changes**: 4-6 hours
- **P1 Changes**: 6-8 hours
- **P2 Changes**: 8-10 hours
- **P3 Changes**: 6-8 hours
- **Testing**: 4-6 hours

**Total**: 30-42 hours (4-5 days)

---

## Summary

This change record identifies **26 changes** across **3 investigations** and **4 priority levels**.

**Critical Path**:
1. Investigate Runner API and Cerebras support
2. Implement tool extraction and passing (P0-1, P0-2)
3. Add model fallback support (P1-1 through P1-4)
4. Verify and test

**The root cause is clear**: Tools are not being passed to the LLM. The fix is straightforward but requires careful implementation and testing.

---

## Approval Required

**This is a change plan, not an implementation.**

Please review and approve before proceeding with implementation.

Questions to answer:
1. Is the priority ordering correct?
2. Are there any changes that should be added or removed?
3. Should we implement all phases or just Phase 1-2?
4. Do you want to see the investigation results before implementation?
5. Should we create a feature branch for this work?
