# Tasks for Task ID Awareness Fix

## Overview
Fix the model's inability to update or delete tasks by enhancing the system prompt to explain task ID workflow and usage.

## Dependencies
- System prompt in prompts.py
- MCP tools working correctly
- list_tasks returning task IDs (already working)

## Tasks

### 1. Enhance System Prompt with Task ID Workflow
**Description:** Update the TODO_ASSISTANT_PROMPT to include clear instructions about task IDs and how to use them
**Acceptance Criteria:**
- Prompt explains that tasks have numeric IDs
- Prompt instructs to use list_tasks first to get IDs
- Prompt shows how to map natural language to task IDs
- Prompt remains concise and clear
- Examples are provided for clarity

**Implementation:**
- [ ] Add section explaining task ID concept
- [ ] Add workflow instructions (list first, then update/delete)
- [ ] Add examples of natural language mapping
- [ ] Keep prompt under 500 words
- [ ] Test with various user requests

**Test Cases:**
```
User: "update Task 1 to say 'Buy groceries'"
Expected: Model calls list_tasks first, gets ID, then calls update_task with correct ID

User: "delete the first task"
Expected: Model calls list_tasks, identifies first task by position, uses its ID

User: "mark task 123 as complete"
Expected: Model uses ID 123 directly (if user provides it)

User: "update the task about groceries"
Expected: Model calls list_tasks, searches for task with "groceries" in title, uses its ID
```

### 2. Test Natural Language to Task ID Mapping
**Description:** Verify that the model correctly maps various natural language references to task IDs
**Acceptance Criteria:**
- "Task 1" / "first task" maps to first task in list
- "Task 2" / "second task" maps to second task in list
- "the task about X" searches by title/description
- Direct ID references work (e.g., "task 123")

**Implementation:**
- [ ] Test positional references (first, second, last)
- [ ] Test ordinal references (Task 1, Task 2)
- [ ] Test content-based references (task about X)
- [ ] Test direct ID references
- [ ] Verify model calls list_tasks when needed

**Test Cases:**
```
# Positional
"update the first task" -> list_tasks, use tasks[0].id
"delete the last task" -> list_tasks, use tasks[-1].id

# Ordinal
"update Task 1" -> list_tasks, use tasks[0].id
"complete Task 3" -> list_tasks, use tasks[2].id

# Content-based
"update the task about groceries" -> list_tasks, find by title match
"delete the shopping task" -> list_tasks, find by title/description match

# Direct ID
"update task 123" -> use ID 123 directly
"complete task id 456" -> use ID 456 directly
```

### 3. Verify Update and Delete Operations Work
**Description:** Test that update_task and delete_task work correctly with the enhanced prompt
**Acceptance Criteria:**
- Model successfully updates tasks using correct IDs
- Model successfully deletes tasks using correct IDs
- No hallucination of success
- Database changes are verified

**Implementation:**
- [ ] Test update_task with various natural language inputs
- [ ] Test delete_task with various natural language inputs
- [ ] Verify database changes after each operation
- [ ] Confirm no false success messages

**Test Cases:**
```
# Setup
add_task(title="Buy milk", description="From store")
add_task(title="Call mom", description="Birthday")
add_task(title="Fix bug", description="In production")

# Test updates
User: "update Task 1 to say 'Buy organic milk'"
Verify: First task title changed to "Buy organic milk"

User: "change the description of the task about mom to 'Birthday on Friday'"
Verify: Second task description changed

# Test deletes
User: "delete the last task"
Verify: Third task removed from database

User: "remove the task about milk"
Verify: First task removed from database
```

### 4. Handle Ambiguous References
**Description:** Ensure the model asks for clarification when references are ambiguous
**Acceptance Criteria:**
- Model asks for clarification when multiple tasks match
- Model asks for clarification when reference is unclear
- Model provides helpful context in clarification requests

**Implementation:**
- [ ] Test with ambiguous references
- [ ] Verify model asks for clarification
- [ ] Verify clarification requests are helpful
- [ ] Test resolution after clarification

**Test Cases:**
```
# Multiple matches
add_task(title="Buy groceries", description="Milk and bread")
add_task(title="Buy supplies", description="Office supplies")
User: "update the task about buying"
Expected: Model asks which task (both have "buy")

# Unclear reference
User: "update that task"
Expected: Model asks which task

# Out of range
User: "update Task 10" (only 3 tasks exist)
Expected: Model calls list_tasks, sees only 3 tasks, asks for clarification
```

## Testing
- [ ] Test with actual user scenarios
- [ ] Verify all natural language patterns work
- [ ] Confirm no regression in existing functionality
- [ ] Test with multiple users and task sets

## Risks
- Prompt might be too verbose and confuse the model
- Natural language mapping might still be ambiguous
- Model might not consistently follow workflow

## Mitigation
- Keep prompt concise and clear
- Provide explicit examples
- Test thoroughly with various inputs
- Iterate on prompt if needed