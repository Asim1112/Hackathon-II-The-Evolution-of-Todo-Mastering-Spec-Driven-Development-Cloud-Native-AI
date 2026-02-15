# Tasks for Tool Wrapper Parameter Handling Fix

## Overview
Fix TypeError in delete_task and other MCP tools caused by duplicate user_id keyword arguments. Implement parameter sanitization to ensure user_id comes only from authenticated context.

## Dependencies
- MCP tools working (add_task, list_tasks, complete_task, update_task, delete_task)
- Authentication context with user_id
- AgentContext and RequestContext structure
- Tool wrapper in chatkit_server.py

## Tasks

### 1. Add Parameter Sanitization in Tool Wrapper
**Description:** Remove any LLM-provided user_id from parsed_args before spreading to tool handler
**Acceptance Criteria:**
- parsed_args.pop("user_id", None) added after parsing
- Sanitization happens before tool handler call
- No TypeError from duplicate user_id
- Logging shows sanitization occurred

**Implementation:**
- [ ] Parse args to dictionary: parsed_args = json.loads(args)
- [ ] Add sanitization: parsed_args.pop("user_id", None)
- [ ] Add logging: logger.info(f"Sanitized args: {parsed_args}")
- [ ] Call handler: await tool_handler(user_id=user_id, **parsed_args)
- [ ] Test with all 5 MCP tools

**Test Cases:**
```python
# Test 1: LLM includes user_id (should be removed)
args = '{"user_id": "malicious", "title": "Test Task"}'
result = await tool_wrapper(ctx, args)
# Verify: authenticated user_id used, not "malicious"

# Test 2: LLM doesn't include user_id (normal case)
args = '{"title": "Test Task", "description": "Test"}'
result = await tool_wrapper(ctx, args)
# Verify: works correctly

# Test 3: Multiple parameters with user_id
args = '{"user_id": "bad", "task_id": 123, "title": "Updated"}'
result = await tool_wrapper(ctx, args)
# Verify: user_id removed, other params passed correctly
```

### 2. Test delete_task Specifically
**Description:** Verify delete_task works without TypeError after sanitization
**Acceptance Criteria:**
- delete_task can be called successfully
- No TypeError about duplicate user_id
- Task is actually deleted from database
- Correct user_id used for permission check

**Implementation:**
- [ ] Create test task as user A
- [ ] Call delete_task as user A
- [ ] Verify no TypeError
- [ ] Verify task deleted from database
- [ ] Test with LLM-provided user_id (should be ignored)
- [ ] Test permission check (user B cannot delete user A's task)

**Test Cases:**
```python
# Test 1: Basic delete
user_id = "test_user_123"
task = add_task(user_id=user_id, title="Test Task")
result = delete_task(user_id=user_id, task_id=task["task_id"])
assert result["status"] == "deleted"
assert list_tasks(user_id=user_id) == []

# Test 2: Delete with LLM trying to override user_id
# Simulate LLM including user_id in args
args = json.dumps({"user_id": "attacker", "task_id": task["task_id"]})
result = await tool_wrapper(ctx_for_user_A, args)
# Verify: uses user_A's context, not "attacker"

# Test 3: Permission check
user_a_task = add_task(user_id="user_a", title="A's Task")
try:
    delete_task(user_id="user_b", task_id=user_a_task["task_id"])
    assert False, "Should raise PermissionError"
except PermissionError:
    pass  # Expected
```

### 3. Test All 5 MCP Tools for Parameter Conflicts
**Description:** Verify all MCP tools work correctly with parameter sanitization
**Acceptance Criteria:**
- add_task works without conflicts
- list_tasks works without conflicts
- complete_task works without conflicts
- update_task works without conflicts
- delete_task works without conflicts
- All tools use authenticated user_id

**Implementation:**
- [ ] Test add_task with various parameters
- [ ] Test list_tasks with status filter
- [ ] Test complete_task with task_id
- [ ] Test update_task with title and description
- [ ] Test delete_task with task_id
- [ ] Verify no TypeError in any tool
- [ ] Verify correct user_id used in all cases

**Test Cases:**
```python
# Test 1: add_task
result = add_task(user_id="user1", title="Task 1", description="Desc 1")
assert result["status"] == "created"

# Test 2: list_tasks
tasks = list_tasks(user_id="user1", status="all")
assert len(tasks) >= 1

# Test 3: complete_task
task_id = tasks[0]["id"]
result = complete_task(user_id="user1", task_id=task_id)
assert result["status"] == "completed"

# Test 4: update_task
result = update_task(user_id="user1", task_id=task_id, title="Updated Title")
assert result["status"] == "updated"

# Test 5: delete_task
result = delete_task(user_id="user1", task_id=task_id)
assert result["status"] == "deleted"

# Test 6: All tools with LLM-provided user_id (should be ignored)
for tool in [add_task, list_tasks, complete_task, update_task, delete_task]:
    # Simulate LLM including user_id
    # Verify authenticated user_id is used
    pass
```

### 4. Verify Security: user_id Cannot Be Overridden
**Description:** Test that LLM cannot override authenticated user_id through arguments
**Acceptance Criteria:**
- LLM-provided user_id is always ignored
- Authenticated user_id is always used
- User isolation is maintained
- Security boundary is enforced

**Implementation:**
- [ ] Create tasks as user A
- [ ] Attempt to access as user B with LLM providing user A's ID
- [ ] Verify user B cannot access user A's tasks
- [ ] Test with all 5 MCP tools
- [ ] Verify logging shows sanitization
- [ ] Test with malicious payloads

**Test Cases:**
```python
# Test 1: Cannot override user_id to access other user's tasks
user_a_task = add_task(user_id="user_a", title="A's Task")

# User B tries to access by providing user_a in args
args = json.dumps({"user_id": "user_a", "status": "all"})
result = await tool_wrapper(ctx_for_user_b, args)
tasks = json.loads(result)
# Verify: returns user_b's tasks, not user_a's

# Test 2: Cannot delete other user's tasks
try:
    args = json.dumps({"user_id": "user_a", "task_id": user_a_task["task_id"]})
    await tool_wrapper(ctx_for_user_b, args)
    assert False, "Should raise PermissionError"
except PermissionError:
    pass  # Expected

# Test 3: Malicious payloads
malicious_payloads = [
    '{"user_id": "admin", "title": "Test"}',
    '{"user_id": "", "title": "Test"}',
    '{"user_id": null, "title": "Test"}',
    '{"user_id": {"nested": "attack"}, "title": "Test"}',
]
for payload in malicious_payloads:
    result = await tool_wrapper(ctx_for_user_a, payload)
    # Verify: uses user_a's context, ignores malicious user_id
```

### 5. Add Comprehensive Logging
**Description:** Ensure tool execution is properly logged for debugging and security auditing
**Acceptance Criteria:**
- Log tool name and authenticated user_id
- Log sanitized arguments
- Log execution success/failure
- Log any security violations

**Implementation:**
- [ ] Add logging before tool execution
- [ ] Log: tool name, user_id, sanitized args
- [ ] Add logging after tool execution
- [ ] Log: success/failure, result summary
- [ ] Add error logging with exception details
- [ ] Test log output format

**Test Cases:**
```python
# Test 1: Success logging
with capture_logs() as logs:
    add_task(user_id="user1", title="Test")
assert "[TOOL] Executing add_task: user_id=user1" in logs
assert "[TOOL] add_task succeeded" in logs

# Test 2: Error logging
with capture_logs() as logs:
    try:
        add_task(user_id="user1", title="")  # Invalid
    except ValueError:
        pass
assert "[TOOL] add_task failed" in logs

# Test 3: Sanitization logging
with capture_logs() as logs:
    args = '{"user_id": "malicious", "title": "Test"}'
    await tool_wrapper(ctx, args)
# Verify: logs show user_id was sanitized
```

### 6. Test Error Handling
**Description:** Verify tool wrapper handles errors gracefully
**Acceptance Criteria:**
- JSON parse errors handled
- Tool execution errors caught
- Error responses returned as JSON
- No unhandled exceptions

**Implementation:**
- [ ] Test with invalid JSON
- [ ] Test with missing required parameters
- [ ] Test with invalid parameter types
- [ ] Test with tool execution failures
- [ ] Verify error responses are JSON formatted
- [ ] Verify errors are logged

**Test Cases:**
```python
# Test 1: Invalid JSON
try:
    result = await tool_wrapper(ctx, "not valid json")
    assert False, "Should raise JSONDecodeError"
except json.JSONDecodeError:
    pass  # Expected

# Test 2: Missing required parameter
args = '{"description": "No title"}'
result = await tool_wrapper_for_add_task(ctx, args)
result_dict = json.loads(result)
assert "error" in result_dict

# Test 3: Invalid parameter type
args = '{"title": 123}'  # Should be string
result = await tool_wrapper_for_add_task(ctx, args)
result_dict = json.loads(result)
assert "error" in result_dict

# Test 4: Tool execution failure
args = '{"task_id": 99999}'  # Non-existent task
result = await tool_wrapper_for_delete_task(ctx, args)
result_dict = json.loads(result)
assert result_dict["status"] == "failed"
```

## Testing
- [ ] Unit tests for parameter sanitization
- [ ] Integration tests with all 5 MCP tools
- [ ] Security tests for user_id override attempts
- [ ] Error handling tests
- [ ] Logging verification tests

## Risks
- Other parameters might have similar conflicts
- Future tools might have different patterns
- Security bypass attempts
- Performance impact from sanitization

## Mitigation
- Review all tool schemas thoroughly
- Test with malicious payloads
- Monitor logs for suspicious patterns
- Benchmark sanitization overhead