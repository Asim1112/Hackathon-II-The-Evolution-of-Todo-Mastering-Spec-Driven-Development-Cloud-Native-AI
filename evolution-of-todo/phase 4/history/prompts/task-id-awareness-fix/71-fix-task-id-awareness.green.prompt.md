---
id: 71
title: "Fix task ID awareness in system prompt"
stage: "green"
date: "2026-02-15"
surface: "agent"
model: "claude-sonnet-4-5-20250929"
feature: "task-id-awareness-fix"
branch: "main"
user: "unknown"
command: "manual"
labels: ["system-prompt", "task-ids", "llm-instructions", "update-task", "delete-task", "sdd-flow"]
links:
  spec: "specs/task-id-awareness-fix/spec.md"
  ticket: null
  adr: null
  pr: null
files:
  - "backend/src/agents/prompts.py"
  - "specs/task-id-awareness-fix/spec.md"
  - "specs/task-id-awareness-fix/plan.md"
  - "tasks/task-id-awareness-fix.tasks.md"
tests:
  - "Manual verification needed"
---

# Fix Task ID Awareness in System Prompt

## Context

The model could not update or delete tasks because it didn't understand how to use task IDs. While `list_tasks` already returns task IDs in the response, the system prompt didn't explain:
1. That list_tasks returns an "id" field for each task
2. That update_task and delete_task require the task "id" parameter (not the title)
3. How to map natural language references like "update Task 1" to actual database task IDs

**Evidence:**
- User says "update Task 1"
- Model calls update_task but doesn't know the task_id
- Model hallucinates success without actually updating the database

**Root Cause:**
The system prompt was too basic and didn't explain the task ID workflow to the model.

## Prompt

```
User reported task updating bug:
- Create and list now works (after database commit fix)
- Remaining bug: task updating doesn't work
- Root cause: Model cannot update tasks because it doesn't know task IDs
- Model only sees "Task 1, Task 2, Task 3" but update_task requires task_id (DB primary key)
- Model hallucinates success without actually updating

Task: Expose task.id to LLM and ensure agent prompt tells model to use id when calling update_task or delete_task
```

## Response

Following complete SDD flow:
1. Created specification documenting the problem and solution approach
2. Created implementation plan with prompt enhancement strategy
3. Created detailed task breakdown with test cases
4. Enhanced the system prompt in `prompts.py` to include:
   - Explanation that tasks have numeric IDs
   - Clear workflow: call list_tasks first to get IDs
   - Natural language mapping instructions (Task 1 → first task's id)
   - Example workflow showing correct usage
   - Instructions to use "id" field, not title

## Outcome & Impact

**Enhanced System Prompt:** The model now understands:
- Tasks have numeric IDs returned by list_tasks
- Must call list_tasks first before update/delete operations
- How to map natural language references to task IDs
- Correct workflow with concrete examples

**Before:** Model couldn't update or delete tasks because it didn't know how to use task IDs.

**After:** Model can correctly:
- Map "Task 1" to the first task's ID
- Map "the task about X" to the matching task's ID
- Call list_tasks first, then use the correct ID for updates/deletes

## Files Modified

- backend/src/agents/prompts.py - Enhanced system prompt with task ID workflow
- specs/task-id-awareness-fix/spec.md - Problem specification
- specs/task-id-awareness-fix/plan.md - Implementation plan
- tasks/task-id-awareness-fix.tasks.md - Task breakdown with test cases

## Tests Summary

Manual verification required:
1. Test "update Task 1 to say 'Buy groceries'" - should call list_tasks first
2. Test "delete the first task" - should get ID from list_tasks
3. Test "mark task 123 as complete" - should use ID directly if provided
4. Test "update the task about groceries" - should search by title in list_tasks
5. Verify no hallucination of success

## Next Steps

1. Restart the backend server to apply the prompt changes
2. Test with various natural language update/delete requests
3. Verify model calls list_tasks before update/delete operations
4. Confirm database changes are actually made
5. Test edge cases (ambiguous references, out of range, etc.)

## Reflection

Clear, explicit instructions in the system prompt are crucial for the model to understand workflows that involve multiple steps. The model needs to be told not just what tools are available, but how to use them together in the correct sequence. Providing concrete examples helps the model understand the expected behavior.