---
id: 59
title: Agent Tool Calling Bug Fix Complete
stage: green
date: 2026-02-13
surface: agent
model: claude-sonnet-4-5
feature: none
branch: unknown
user: unknown
command: /sp.phr
labels: ["agent", "tool-calling", "bug-fix", "prompt-engineering", "mcp"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/agents/prompts.py
  - backend/test_agent_direct.py
tests:
  - backend/test_agent_direct.py
---

## Prompt

--title "Agent Tool Calling Bug Fix Complete" --stage green

## Response snapshot

Successfully fixed the agent tool calling bug. The agent was hallucinating text responses instead of calling tools. Applied a surgical fix by simplifying the system prompt from 84 lines to 25 lines with explicit completion instructions. Verified the fix works: agent now successfully calls tools (ToolCallItem and ToolCallOutputItem detected), executes them, and responds to the user without infinite loops.

## Outcome

- ✅ Impact: Agent tool calling bug RESOLVED - agent now calls tools instead of hallucinating text responses
- 🧪 Tests: Created and ran test_agent_direct.py - confirmed ToolCallItem and ToolCallOutputItem are generated, execution completes successfully
- 📁 Files: Modified prompts.py (simplified TODO_ASSISTANT_PROMPT from 84 to 25 lines), created test_agent_direct.py for verification
- 🔁 Next prompts: Investigate why MCP add_task tool executes but doesn't create database records (secondary issue discovered during testing)
- 🧠 Reflection: Overly verbose system prompts with extensive instructions cause LLMs to respond instructionally rather than taking action. Concise, action-oriented prompts with explicit completion signals work better.

## Evaluation notes (flywheel)

- Failure modes observed: Initial prompt was too verbose (84 lines) with extensive verification patterns and examples, causing the LLM to generate instructional text instead of calling tools. Second iteration lacked completion instructions, causing MaxTurnsExceeded error. Third iteration with explicit "respond and stop" instructions resolved both issues.
- Graders run and results (PASS/FAIL): PASS - Agent successfully calls tools (ToolCallItem detected), tool executes (ToolCallOutputItem detected), agent responds to user (MessageOutputItem), no MaxTurnsExceeded error. PARTIAL - Database not updated (secondary issue, not part of original bug).
- Prompt variant (if applicable): Final working prompt is 25 lines with explicit tool list, usage examples, and completion instructions ("respond to user and stop")
- Next experiment (smallest change to try): Investigate MCP tool implementation to understand why add_task executes successfully but doesn't create database records. Check if it's a user_id vs owner_id mismatch or transaction commit issue.
