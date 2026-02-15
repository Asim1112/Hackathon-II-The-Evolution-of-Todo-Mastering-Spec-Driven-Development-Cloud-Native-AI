# Tool Result Injection Fix Specification

## Problem Statement
Tool results from Cerebras are not being converted into ChatKit Responses API events. When users call tools like `list_tasks()`, the tool executes (evidenced by FN_CALL=True in logs), but the results are never displayed in the UI. The model never receives the tool output, causing hallucination and stopping the conversation.

## Requirements

### Functional Requirements
1. **Tool Result Display**: When a tool is called, its results must be displayed in the ChatKit UI
2. **Model Input**: Tool call results must be properly fed back to the model for continued conversation
3. **UI Consistency**: Tool call IDs must be consistently handled to prevent display issues
4. **Streaming Support**: Results must be properly handled in the streaming flow

### Non-Functional Requirements
1. **Performance**: No degradation in streaming performance
2. **Reliability**: Tool calls must complete successfully without errors
3. **Compatibility**: Existing functionality must remain intact

## Solution Approach

### Architecture
- Enhance the TodoChatKitServer.respond() method to track tool call results
- Implement proper ID remapping for tool call results
- Ensure tool call completion events include output information

### Components
- `backend/src/agents/chatkit_server.py`: Enhanced tool call result handling
- Streaming event processing: Proper handling of tool call lifecycle events

### Data Flow
1. Tool call initiated by model
2. Tool executes and returns results
3. Results are tracked and mapped to proper IDs
4. Results are displayed in UI and fed back to model
5. Conversation continues naturally

## Acceptance Criteria
- [ ] Tool call results are displayed in the ChatKit UI
- [ ] Model receives tool outputs and continues conversation without hallucination
- [ ] No regression in existing message ID handling
- [ ] All tool types work correctly (add_task, list_tasks, complete_task, update_task, delete_task)
- [ ] Streaming performance is maintained

## Constraints
- Must maintain backward compatibility
- Cannot modify core ChatKit or Agents SDK behavior
- Must work with Cerebras backend
- ID remapping must continue to work properly

## Risks
- Potential regression in message handling
- Tool results still not displaying properly
- Performance degradation in streaming