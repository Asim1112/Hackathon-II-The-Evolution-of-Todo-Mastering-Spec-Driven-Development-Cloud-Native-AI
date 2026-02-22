# Task ID Awareness Fix Implementation Plan

## Scope and Dependencies

### In Scope
- Update system prompt to explain task ID workflow
- Add clear instructions for using task IDs with update_task and delete_task
- Explain natural language to task ID mapping
- Maintain concise and clear prompt structure

### Out of Scope
- Changing tool signatures or behavior
- Modifying list_tasks output format (already returns IDs)
- Changing ChatKit integration
- Adding new tools

### External Dependencies
- OpenAI Agents SDK
- Cerebras LLM (llama-3.3-70b)
- Existing MCP tools

## Key Decisions and Rationale

### Decision 1: Prompt Enhancement Strategy
**Option 1**: Add brief ID usage note to existing prompt
**Option 2**: Comprehensive workflow explanation with examples
**Option 3**: Separate section for ID management
**Chosen**: Option 2 - Comprehensive workflow explanation
**Rationale**: The model needs clear, explicit instructions to understand the workflow. Brief notes might be missed or misunderstood.

### Decision 2: Workflow Instruction Placement
**Option 1**: Add to tool descriptions
**Option 2**: Add as separate workflow section
**Option 3**: Add inline with each tool mention
**Chosen**: Option 2 - Separate workflow section
**Rationale**: Keeps tool list clean while providing clear workflow guidance in a dedicated section.

### Decision 3: Natural Language Mapping Guidance
**Option 1**: Provide explicit examples
**Option 2**: General guidance only
**Chosen**: Option 1 - Explicit examples
**Rationale**: Examples help the model understand how to map user references to task IDs.

## Implementation Details

### Enhanced System Prompt Structure
```
1. Introduction (who you are)
2. Available Tools (list with brief descriptions)
3. Task ID Workflow (NEW - critical section)
   - Explain that tasks have numeric IDs
   - Workflow: list_tasks first, then use IDs
   - Examples of natural language mapping
4. General Guidelines (concise, helpful)
```

### Key Instructions to Add
1. "Tasks have numeric IDs (e.g., id: 123). Always use the 'id' field, not the title."
2. "To update or delete a task: First call list_tasks to get task IDs, then use the id parameter."
3. "When user says 'update Task 1' or 'the first task', call list_tasks first to find which task they mean."
4. Examples of correct workflow

## Non-Functional Requirements

### Clarity
- Instructions must be unambiguous
- Workflow must be explicit
- Examples must be clear

### Conciseness
- Keep prompt under 500 words
- Avoid redundancy
- Focus on essential information

### Reliability
- Model should consistently follow workflow
- ID usage should be correct 100% of time

## Testing Strategy
1. Test "update Task 1" - should call list_tasks first
2. Test "delete the first task" - should get ID from list_tasks
3. Test "mark task 123 as complete" - should use ID directly if provided
4. Test "update the task about groceries" - should search by title in list_tasks

## Risk Analysis

### Top Risks
1. **Prompt too verbose** - Impact: Medium, Mitigation: Keep concise
2. **Model still confused** - Impact: High, Mitigation: Clear examples
3. **Natural language ambiguity** - Impact: Medium, Mitigation: Instruct to ask for clarification

## Rollback Plan
If the enhanced prompt causes issues, revert to the original and iterate on a simpler version.