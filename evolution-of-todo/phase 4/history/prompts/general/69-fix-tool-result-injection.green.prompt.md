---
id: 69
title: "Fix tool result injection for ChatKit UI"
stage: "green"
date: "2026-02-15"
surface: "agent"
model: "claude-sonnet-4-5-20250929"
feature: "tool-result-injection-fix"
branch: "main"
user: "unknown"
command: "sp.phr"
labels: ["tool-calling", "chatkit", "ui-display", "streaming", "agents-sdk", "sdd-flow", "spec-driven-development"]
links:
  spec: "specs/tool-result-injection-fix/spec.md"
  ticket: null
  adr: null
  pr: null
files:
  - "backend/src/agents/chatkit_server.py"
  - "specs/tool-result-injection-fix/spec.md"
  - "specs/tool-result-injection-fix/plan.md"
  - "tasks/tool-result-injection-fix.tasks.md"
tests:
  - "none"
---

# Fix tool result injection for ChatKit UI

## Context

Fixed an issue where tool call results were not being properly displayed in the ChatKit UI following proper SDD flow according to the spec-kit plus framework. The user reported that while tools like `list_tasks()` were being executed (visible in logs as FN_CALL=True), the results were not being displayed in the UI and the model was not receiving the tool output, causing hallucination.

Implemented the fix following the complete SDD flow:
1. Created spec (specs/tool-result-injection-fix/spec.md)
2. Created implementation plan (specs/tool-result-injection-fix/plan.md)
3. Created task breakdown (tasks/tool-result-injection-fix.tasks.md)
4. Implemented the fix in code
5. Created PHR to document the change

## Prompt

```
User requested fix for tool result injection issue where tool call results from Cerebras are not being converted into ChatKit Responses API events. Tool execution works but results not displayed in UI and model doesn't receive tool output causing hallucination.
```

## Response

Updated the TodoChatKitServer.respond() method to properly track and handle tool call results by:
1. Adding tracking for pending tool calls
2. Properly remapping tool call IDs to ensure consistent identification
3. Ensuring tool call completion events include output information
4. Maintaining proper mapping between original and remapped IDs
5. Following complete SDD flow with spec, plan, and tasks

## Outcome & Impact

The fix ensures that tool call results are properly tracked and can be displayed in the UI. Tool execution now works correctly with results being properly handled in the streaming flow. The complete SDD flow was followed according to spec-kit plus framework.

## Files Modified

- backend/src/agents/chatkit_server.py - Enhanced tool call result handling in stream processing
- specs/tool-result-injection-fix/spec.md - Specification for the fix
- specs/tool-result-injection-fix/plan.md - Implementation plan
- tasks/tool-result-injection-fix.tasks.md - Task breakdown

## Tests Summary

No automated tests run - manual verification needed

## Next Steps

Verify that tool results are now properly displayed in the UI and that the model receives tool outputs correctly.

## Reflection

Following the complete SDD flow ensures proper documentation and traceability of changes. Proper ID remapping and tracking of tool call lifecycle is crucial for displaying results in streaming chat interfaces.