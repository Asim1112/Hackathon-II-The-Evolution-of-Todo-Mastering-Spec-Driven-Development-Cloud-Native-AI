---
id: 62
title: Tools Not Passed in ChatKit Flow
stage: red
date: 2026-02-13
surface: agent
model: claude-sonnet-4-5
feature: none
branch: unknown
user: unknown
command: manual
labels: ["debugging", "chatkit", "tools", "mcp", "integration"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - none
tests:
  - none
---

## Prompt

User reports: After fixing the prompt, chatbot still shows helpdesk text ("I can help you create new tasks...") instead of calling list_tasks tool. Second message shows "FN_CALL=False" replacing previous response, breaking chat flow.

## Response snapshot

Critical finding: Ultra-minimal prompt works in direct test (test_agent_direct.py) but fails in ChatKit UI. The "FN_CALL=False" message indicates diagnostic code from llm_interceptor.py showing tools are NOT being passed to the LLM in the ChatKit request flow.

Issue is NOT the prompt - issue is tools aren't being attached to requests when going through ChatKit integration.

Need to investigate:
1. Why tools work in Runner.run() directly but not through ChatKit
2. Check chatkit_server.py respond() method
3. Verify MCP servers are attached to agent in ChatKit flow
4. Check if there's a code path difference

## Outcome

- ✅ Impact: Identified root cause - tools not passed in ChatKit flow (different from direct test)
- 🧪 Tests: Direct test works, ChatKit UI fails
- 📁 Files: Need to investigate chatkit_server.py
- 🔁 Next prompts: Check why MCP tools aren't being passed in ChatKit integration
- 🧠 Reflection: Test in isolation can pass while production flow fails - need to test actual integration path

## Evaluation notes (flywheel)

- Failure modes observed: Direct test (test_agent_direct.py) passes but ChatKit UI fails. Tools are attached in direct Runner.run() but not in ChatKit flow. "FN_CALL=False" diagnostic message appearing in UI.
- Graders run and results (PASS/FAIL): FAIL - ChatKit integration broken, tools not passed to LLM
- Prompt variant (if applicable): Ultra-minimal prompt is correct, issue is in integration layer
- Next experiment (smallest change to try): Check if agent instance in ChatKit has MCP servers attached, verify Runner.run() is being called correctly in chatkit_server.py respond() method
