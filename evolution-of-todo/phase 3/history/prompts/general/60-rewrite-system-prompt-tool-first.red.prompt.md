---
id: 60
title: Rewrite System Prompt for Tool-First Behavior
stage: red
date: 2026-02-13
surface: agent
model: claude-sonnet-4-5
feature: none
branch: unknown
user: unknown
command: manual
labels: ["prompt-engineering", "cerebras", "tool-calling", "behavioral-fix"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/agents/prompts.py
tests:
  - none
---

## Prompt

The agent is still responding in helpdesk mode instead of action mode. The system prompt must be rewritten to be strictly tool-first and action-oriented. No capability descriptions, no explanations, no guidance. Only: interpret → call tool → return result.

The MCP server, tools, and database are correct and working. The failure was NOT technical — it was behavioral.

Cerebras is extremely sensitive to verbose or instructional prompts and will enter "assistant/explanation mode" instead of "tool-execution mode" if the system prompt is too long or descriptive.

## Response snapshot

Analyzing current prompt (29 lines) - still contains:
- Identity statements ("You are a helpful AI assistant")
- Tool descriptions ("Create a new task", "View all tasks")
- Numbered procedural steps
- Verbose examples with arrows and explanations
- Behavioral guidance

Creating minimal, action-first prompt optimized for Cerebras:
- Remove all descriptions and explanations
- Remove identity/role statements
- Remove procedural guidance
- Direct intent-to-tool mapping only
- Single completion instruction

Target: <10 lines, pure action dispatch.

## Outcome

- ✅ Impact: Creating ultra-minimal prompt to force Cerebras into tool-execution mode
- 🧪 Tests: Will verify with test_agent_direct.py after change
- 📁 Files: backend/src/agents/prompts.py
- 🔁 Next prompts: Test with real user message, verify tool execution happens immediately
- 🧠 Reflection: Cerebras requires extremely terse prompts - any verbosity triggers explanation mode instead of action mode

## Evaluation notes (flywheel)

- Failure modes observed: Previous "simplified" prompt (29 lines) was still too verbose with examples, descriptions, and guidance causing Cerebras to explain rather than act
- Graders run and results (PASS/FAIL): Pending - will test after applying ultra-minimal prompt
- Prompt variant (if applicable): Ultra-minimal action-dispatch prompt (<10 lines)
- Next experiment (smallest change to try): If still fails, reduce to absolute minimum: just tool names and "call tool for user request"
