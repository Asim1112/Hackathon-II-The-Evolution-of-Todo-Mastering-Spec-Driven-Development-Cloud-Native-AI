# Task ID Awareness Fix Specification

## Problem Statement
The model cannot update or delete tasks because it doesn't understand how to use task IDs. While `list_tasks` already returns task IDs in the response, the system prompt doesn't explain:
1. That list_tasks returns an "id" field for each task
2. That update_task and delete_task require the task "id" parameter (not the title)
3. How to map natural language references like "update Task 1" to the actual database task ID

**Evidence:**
- User says "update Task 1"
- Model calls update_task but doesn't know the task_id
- Model hallucinates success without actually updating the database

**Root Cause:**
The system prompt in `prompts.py` is too basic and doesn't explain the task ID workflow to the model.

## Requirements

### Functional Requirements
1. **ID Awareness**: Model must understand that tasks have numeric IDs
2. **Workflow Clarity**: Model must know to call list_tasks first to get IDs
3. **Natural Language Mapping**: Model must map user references like "Task 1" or "the first task" to actual task IDs
4. **Correct Tool Usage**: Model must use the correct task ID when calling update_task or delete_task

### Non-Functional Requirements
1. **Clarity**: Prompt must be clear and unambiguous
2. **Conciseness**: Prompt should be concise but complete
3. **Reliability**: Model should consistently use correct IDs

## Solution Approach

### Fix
Update the system prompt in `prompts.py` to:
1. Explain that list_tasks returns tasks with an "id" field
2. Instruct the model to use the "id" field (not title) for update_task and delete_task
3. Provide clear workflow: list_tasks first, then use IDs for updates/deletes
4. Explain how to handle natural language references

### Components
- `backend/src/agents/prompts.py`: Enhanced system prompt with task ID instructions

## Acceptance Criteria
- [ ] System prompt explains task ID workflow clearly
- [ ] Model calls list_tasks before attempting updates/deletes
- [ ] Model uses correct task IDs from list_tasks response
- [ ] Model successfully updates and deletes tasks
- [ ] Natural language references like "update Task 1" work correctly

## Constraints
- Must maintain existing tool signatures
- Cannot change tool behavior
- Must work with current ChatKit integration

## Risks
- Prompt might be too verbose
- Model might still misunderstand the workflow
- Natural language mapping might be ambiguous