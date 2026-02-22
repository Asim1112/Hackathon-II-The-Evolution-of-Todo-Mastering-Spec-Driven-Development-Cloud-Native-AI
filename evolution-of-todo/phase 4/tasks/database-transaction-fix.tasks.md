# Tasks for Database Transaction Commit Fix

## Overview
Fix the database transaction commit issue where INSERT operations are not visible to subsequent SELECT operations due to uncommitted transactions.

## Dependencies
- PostgreSQL database connection working
- MCP server running
- All 5 MCP tools registered

## Tasks

### 1. Fix _SessionContext to Explicitly Commit Transactions
**Description:** Modify the `_SessionContext.__exit__` method to explicitly call `session.commit()` when no exception occurs
**Acceptance Criteria:**
- session.commit() is called when exc_type is None
- session.rollback() is still called when exceptions occur
- Docstring updated to reflect correct behavior
- No misleading comments about auto-commit

**Implementation:**
- [ ] Modify `_SessionContext.__exit__` to add explicit commit
- [ ] Update docstring to remove auto-commit claim
- [ ] Keep rollback behavior on exceptions
- [ ] Test with add_task followed by list_tasks

**Test Cases:**
```python
# Test 1: Successful commit
add_task(user_id="test", title="Task 1")
tasks = list_tasks(user_id="test")
assert len(tasks) == 1  # Should see the inserted task

# Test 2: Rollback on exception
try:
    add_task(user_id="test", title="")  # Invalid - empty title
except ValueError:
    pass
tasks = list_tasks(user_id="test")
assert len(tasks) == 1  # Should still be 1, not 2

# Test 3: Multiple operations
add_task(user_id="test", title="Task 2")
add_task(user_id="test", title="Task 3")
tasks = list_tasks(user_id="test")
assert len(tasks) == 3  # Should see all 3 tasks
```

### 2. Verify All MCP Tools Work Correctly
**Description:** Test all 5 MCP tools to ensure they work with the fixed transaction handling
**Acceptance Criteria:**
- add_task creates tasks that are immediately visible
- list_tasks returns all tasks for the user
- complete_task marks tasks as completed
- update_task modifies task data
- delete_task removes tasks

**Implementation:**
- [ ] Test add_task with immediate list_tasks verification
- [ ] Test complete_task and verify status change
- [ ] Test update_task and verify changes
- [ ] Test delete_task and verify removal
- [ ] Test with the actual user_id from the evidence

**Test Cases:**
```python
user_id = "aj02MZpu47L1qwUfHFXc0Ch04Y8HfhzO"

# Add tasks
add_task(user_id=user_id, title="Task 1", description="Test 1")
add_task(user_id=user_id, title="Task 2", description="Test 2")

# List tasks
tasks = list_tasks(user_id=user_id, status="all")
assert len(tasks) >= 2

# Complete task
task_id = tasks[0]["id"]
complete_task(user_id=user_id, task_id=task_id)
tasks = list_tasks(user_id=user_id, status="completed")
assert len(tasks) >= 1

# Update task
update_task(user_id=user_id, task_id=task_id, title="Updated Title")
tasks = list_tasks(user_id=user_id, status="all")
assert any(t["title"] == "Updated Title" for t in tasks)

# Delete task
delete_task(user_id=user_id, task_id=task_id)
tasks = list_tasks(user_id=user_id, status="all")
assert not any(t["id"] == task_id for t in tasks)
```

### 3. Test Exception Handling and Rollback
**Description:** Verify that exceptions properly trigger rollback and don't leave partial data
**Acceptance Criteria:**
- Exceptions trigger rollback
- No partial data persists after exceptions
- Database remains consistent

**Implementation:**
- [ ] Test with invalid data that triggers exceptions
- [ ] Verify rollback occurs
- [ ] Confirm no data corruption

**Test Cases:**
```python
# Test invalid title (empty)
initial_count = len(list_tasks(user_id="test", status="all"))
try:
    add_task(user_id="test", title="")
except ValueError:
    pass
final_count = len(list_tasks(user_id="test", status="all"))
assert initial_count == final_count

# Test invalid task_id
try:
    complete_task(user_id="test", task_id=99999)
except PermissionError:
    pass
# Database should remain consistent
```

### 4. Verify Database Engine Consistency
**Description:** Ensure all operations use the same SQLAlchemy engine and database
**Acceptance Criteria:**
- Single engine instance used throughout
- No multiple database files created
- PostgreSQL connection working correctly

**Implementation:**
- [ ] Verify settings.database_url is correct
- [ ] Confirm single engine in session.py
- [ ] Check no other engine creations exist
- [ ] Verify PostgreSQL connection string

## Testing
- [ ] Manual testing with actual user_id from evidence
- [ ] Test all 5 MCP tools in sequence
- [ ] Test exception handling
- [ ] Verify no regression in existing functionality

## Risks
- Potential data corruption if commit logic is incorrect
- Rollback might not work properly
- Performance impact (unlikely but possible)

## Mitigation
- Thorough testing before deployment
- Rollback plan ready
- Monitor database logs for errors