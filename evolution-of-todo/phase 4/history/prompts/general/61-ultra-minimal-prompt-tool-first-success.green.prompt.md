---
id: 61
title: Ultra-Minimal Prompt Achieves Tool-First Behavior
stage: green
date: 2026-02-13
surface: agent
model: claude-sonnet-4-5
feature: none
branch: unknown
user: unknown
command: /sp.phr
labels: ["prompt-engineering", "cerebras", "tool-calling", "behavioral-fix", "success"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/agents/prompts.py
tests:
  - backend/test_agent_direct.py
---

## Prompt

Continue with ultra-minimal prompt verification after rewriting system prompt to be strictly tool-first and action-oriented.

## Response snapshot

Successfully reduced system prompt from 29 lines to 3 lines. Verified with test_agent_direct.py that agent now operates in pure tool-execution mode: calls tools immediately, executes them, returns result. No explanation mode, no helpdesk behavior. Cerebras now prioritizes tool calling over text generation.

## Outcome

- ✅ Impact: Agent behavior FIXED - ultra-minimal prompt (3 lines) forces Cerebras into tool-execution mode
- 🧪 Tests: test_agent_direct.py confirms ToolCallItem and ToolCallOutputItem generated, agent responds concisely
- 📁 Files: backend/src/agents/prompts.py (reduced from 29 lines to 3 lines)
- 🔁 Next prompts: Test with actual backend + frontend + authenticated user to verify end-to-end flow
- 🧠 Reflection: Cerebras requires extremely terse prompts - any verbosity (descriptions, examples, guidance) triggers explanation mode instead of action mode

## Evaluation notes (flywheel)

- Failure modes observed: Previous attempts at "simplified" prompts (29 lines, 25 lines) were still too verbose with tool descriptions, examples, and procedural guidance. Cerebras is extremely sensitive to prompt length and instructional tone.
- Graders run and results (PASS/FAIL): PASS - Agent calls tools immediately (ToolCallItem detected), tools execute (ToolCallOutputItem detected), agent returns concise result. Database not updated in test due to auth bypass (expected).
- Prompt variant (if applicable): Ultra-minimal 3-line prompt: "Tools: [list]. Call tool for user request. Return result."
- Next experiment (smallest change to try): Test with real ChatKit UI and authenticated user to verify complete flow including database persistence.

## Final System Prompt (3 lines)

```
Tools: add_task, list_tasks, complete_task, update_task, delete_task

Call tool for user request. Return result.
```

This is the minimal prompt that achieves tool-first behavior with Cerebras.
