# Tasks for User ID Extraction Fix

## Overview
Fix broken user_id extraction in tool wrapper that was causing all tools to use "unknown" user_id, preventing proper tool execution and user isolation.

## Dependencies
- AgentContext and RequestContext structure
- Authentication flow working
- Tool wrapper in chatkit_server.py
- All 5 MCP tools

## Tasks

### 1. Fix Context Navigation Path
**Description:** Correct the object hierarchy traversal from RunContextWrapper to user_id
**Acceptance Criteria:**
- Context path changed from ctx.context.user_id to ctx.context.request_context.user_id
- hasattr checks at each level
- Fallback to "unknown" with warning if extraction fails
- Logging shows successful extraction

**Implementation:**
- [ ] Change: agent_ctx = ctx.context
- [ ] Add: if hasattr(agent_ctx, 'request_context')
- [ ] Add: if hasattr(agent_ctx.request_context, 'user_id')
- [ ] Extract: user_id = agent_ctx.request_context.user_id
- [ ] Add fallback: else: user_id = "unknown"
- [ ] Add warning log when fallback occurs
- [ ] Test with authenticated requests

**Test Cases:**
```python
# Test 1: Correct extraction with full context
ctx = create_authenticated_context(user_id="test_user_123")
agent_ctx = ctx.context
assert hasattr(agent_ctx, 'request_context')
assert hasattr(agent_ctx.request_context, 'user_id')
user_id = agent_ctx.request_context.user_id
assert user_id == "test_user_123"
assert user_id != "unknown"

# Test 2: Missing request_context
ctx = create_mock_context_without_request_context()
agent_ctx = ctx.context
user_id = extract_user_id(ctx)
assert user_id == "unknown"
# Verify warning logged

# Test 3: Missing user_id in request_context
ctx = create_mock_context_without_user_id()
user_id = extract_user_id(ctx)
assert user_id == "unknown"
# Verify warning logged
```

### 2. Verify add_task Creates Tasks with Correct owner_id
**Description:** Test that add_task now creates tasks with the authenticated user's ID
**Acceptance Criteria:**
- Tasks created with correct owner_id
- No "unknown" owner_id in database
- User can see their own tasks
- User cannot see other users' tasks

**Implementation:**
- [ ] Authenticate as user A
- [ ] Call add_task with title and description
- [ ] Query database for created task
- [ ] Verify task.owner_id == user A's ID
- [ ] Verify task.owner_id != "unknown"
- [ ] Test with multiple users
- [ ] Verify user isolation

**Test Cases:**
```python
# Test 1: Single user task creation
user_id = "user_abc_123"
result = add_task(user_id=user_id, title="My Task", description="Test")
assert result["status"] == "created"

# Query database directly
task = db.query(Task).filter(Task.id == result["task_id"]).first()
assert task.owner_id == user_id
assert task.owner_id != "unknown"

# Test 2: Multiple users
user_a_task = add_task(user_id="user_a", title="A's Task")
user_b_task = add_task(user_id="user_b", title="B's Task")

task_a = db.query(Task).filter(Task.id == user_a_task["task_id"]).first()
task_b = db.query(Task).filter(Task.id == user_b_task["task_id"]).first()

assert task_a.owner_id == "user_a"
assert task_b.owner_id == "user_b"
assert task_a.owner_id != task_b.owner_id

# Test 3: No "unknown" in database
all_tasks = db.query(Task).all()
unknown_tasks = [t for t in all_tasks if t.owner_id == "unknown"]
assert len(unknown_tasks) == 0
```

### 3. Verify list_tasks Returns Correct User's Tasks
**Description:** Test that list_tasks now returns only the authenticated user's tasks
**Acceptance Criteria:**
- list_tasks returns user's own tasks
- list_tasks does not return other users' tasks
- Empty list for users with no tasks (not error)
- Correct filtering by status

**Implementation:**
- [ ] Create tasks for user A
- [ ] Create tasks for user B
- [ ] Call list_tasks as user A
- [ ] Verify only user A's tasks returned
- [ ] Call list_tasks as user B
- [ ] Verify only user B's tasks returned
- [ ] Test with no tasks (new user)
- [ ] Test status filtering

**Test Cases:**
```python
# Test 1: User isolation
add_task(user_id="user_a", title="A's Task 1")
add_task(user_id="user_a", title="A's Task 2")
add_task(user_id="user_b", title="B's Task 1")

tasks_a = list_tasks(user_id="user_a", status="all")
tasks_b = list_tasks(user_id="user_b", status="all")

assert len(tasks_a) == 2
assert len(tasks_b) == 1
assert all(t["title"].startswith("A's") for t in tasks_a)
assert all(t["title"].startswith("B's") for t in tasks_b)

# Test 2: New user with no tasks
tasks_new = list_tasks(user_id="new_user", status="all")
assert tasks_new == []
assert isinstance(tasks_new, list)

# Test 3: Status filtering
add_task(user_id="user_c", title="Task 1")
task2 = add_task(user_id="user_c", title="Task 2")
complete_task(user_id="user_c", task_id=task2["task_id"])

pending = list_tasks(user_id="user_c", status="pending")
completed = list_tasks(user_id="user_c", status="completed")
all_tasks = list_tasks(user_id="user_c", status="all")

assert len(pending) == 1
assert len(completed) == 1
assert len(all_tasks) == 2
```

### 4. Test Model Can Now Create and List Tasks
**Description:** Verify the LLM can successfully create tasks and see them in list
**Acceptance Criteria:**
- Model can call add_task successfully
- Model can call list_tasks and see created tasks
- No "You have no tasks" when tasks exist
- Model workflow works end-to-end

**Implementation:**
- [ ] Send message: "create a task with title 'playing cricket'"
- [ ] Verify add_task is called
- [ ] Verify task is created in database
- [ ] Send message: "show me my tasks"
- [ ] Verify list_tasks is called
- [ ] Verify model sees the created task
- [ ] Verify model responds with task information

**Test Cases:**
```python
# Test 1: Create and list workflow
user_id = "test_user_456"
chat_session = create_chat_session(user_id=user_id)

# Create task via chat
response1 = chat_session.send("create a task with title 'playing cricket'")
assert "created" in response1.lower() or "added" in response1.lower()

# List tasks via chat
response2 = chat_session.send("show me my tasks")
assert "playing cricket" in response2.lower()
assert "you have no tasks" not in response2.lower()

# Test 2: Multiple tasks
chat_session.send("create task: buy groceries")
chat_session.send("create task: call mom")
chat_session.send("create task: fix bug")

response = chat_session.send("list all my tasks")
assert "buy groceries" in response.lower()
assert "call mom" in response.lower()
assert "fix bug" in response.lower()

# Test 3: Model doesn't see other users' tasks
user_a_session = create_chat_session(user_id="user_a")
user_b_session = create_chat_session(user_id="user_b")

user_a_session.send("create task: A's private task")
response = user_b_session.send("show my tasks")
assert "A's private task" not in response.lower()
```

### 5. Verify No "unknown" user_id in Logs
**Description:** Monitor logs to ensure user_id extraction is working correctly
**Acceptance Criteria:**
- No "unknown" user_id in normal operation
- Warning logged only for actual failures
- Successful extractions logged at info level
- Clear audit trail of user_id usage

**Implementation:**
- [ ] Enable logging for tool execution
- [ ] Make authenticated requests
- [ ] Check logs for user_id values
- [ ] Verify no "unknown" appears
- [ ] Test edge case: missing context
- [ ] Verify warning appears for edge case
- [ ] Review log format and clarity

**Test Cases:**
```python
# Test 1: Normal operation - no "unknown"
with capture_logs() as logs:
    add_task(user_id="user_123", title="Test")
    list_tasks(user_id="user_123", status="all")

log_text = "\n".join(logs)
assert "user_id=user_123" in log_text
assert "user_id=unknown" not in log_text

# Test 2: Edge case - missing context
with capture_logs() as logs:
    ctx_broken = create_context_without_request_context()
    try:
        await tool_wrapper(ctx_broken, '{"title": "Test"}')
    except:
        pass

log_text = "\n".join(logs)
assert "Could not extract user_id from context" in log_text
assert "user_id=unknown" in log_text

# Test 3: Audit trail
with capture_logs() as logs:
    add_task(user_id="user_abc", title="Task 1")
    complete_task(user_id="user_abc", task_id=1)
    delete_task(user_id="user_abc", task_id=1)

log_text = "\n".join(logs)
# Verify each operation logged with user_id
assert log_text.count("user_id=user_abc") >= 3
```

### 6. Test All 5 MCP Tools with Correct user_id
**Description:** Comprehensive test of all tools with proper user_id extraction
**Acceptance Criteria:**
- add_task works with correct user_id
- list_tasks works with correct user_id
- complete_task works with correct user_id
- update_task works with correct user_id
- delete_task works with correct user_id
- User isolation maintained for all tools

**Implementation:**
- [ ] Test add_task with authenticated user
- [ ] Test list_tasks with authenticated user
- [ ] Test complete_task with authenticated user
- [ ] Test update_task with authenticated user
- [ ] Test delete_task with authenticated user
- [ ] Verify user isolation for each tool
- [ ] Test permission errors for cross-user access

**Test Cases:**
```python
# Test 1: Full workflow with user A
user_a = "user_a_123"

# Add
task1 = add_task(user_id=user_a, title="Task 1", description="Desc 1")
assert task1["status"] == "created"

# List
tasks = list_tasks(user_id=user_a, status="all")
assert len(tasks) == 1
assert tasks[0]["title"] == "Task 1"

# Complete
result = complete_task(user_id=user_a, task_id=task1["task_id"])
assert result["status"] == "completed"

# Update
result = update_task(user_id=user_a, task_id=task1["task_id"], title="Updated")
assert result["status"] == "updated"

# Delete
result = delete_task(user_id=user_a, task_id=task1["task_id"])
assert result["status"] == "deleted"

# Test 2: User isolation for all tools
user_a_task = add_task(user_id="user_a", title="A's Task")
task_id = user_a_task["task_id"]

# User B cannot complete A's task
try:
    complete_task(user_id="user_b", task_id=task_id)
    assert False, "Should raise PermissionError"
except PermissionError:
    pass

# User B cannot update A's task
try:
    update_task(user_id="user_b", task_id=task_id, title="Hacked")
    assert False, "Should raise PermissionError"
except PermissionError:
    pass

# User B cannot delete A's task
try:
    delete_task(user_id="user_b", task_id=task_id)
    assert False, "Should raise PermissionError"
except PermissionError:
    pass

# User B cannot see A's task in list
user_b_tasks = list_tasks(user_id="user_b", status="all")
assert not any(t["id"] == task_id for t in user_b_tasks)
```

## Testing
- [ ] Unit tests for context navigation
- [ ] Integration tests with all 5 MCP tools
- [ ] User isolation tests
- [ ] Model workflow tests
- [ ] Logging verification tests
- [ ] Edge case tests (missing context)

## Risks
- Context structure might change in future SDK versions
- Authentication flow might break
- User isolation might be violated
- Performance impact from hasattr checks

## Mitigation
- Pin SDK versions
- Test authentication thoroughly
- Comprehensive user isolation tests
- Benchmark context navigation overhead
- Monitor "unknown" user_id in production