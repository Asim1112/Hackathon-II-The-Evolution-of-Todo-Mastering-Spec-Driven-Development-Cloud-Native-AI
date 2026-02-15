---
id: 004
title: Fix Groq Tool Calling Errors
stage: misc
date: 2026-02-11
surface: agent
model: claude-sonnet-4-5
feature: 016-ai-chatbot
branch: main
user: asimh
command: debugging-session
labels: ["groq", "tool-calling", "bug-fix", "validation", "prompt-engineering"]
links:
  spec: specs/016-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/016-ai-chatbot/research.md
  - frontend/next.config.ts
  - backend/src/api/routes/chat.py
  - backend/src/agents/orchestrator.py
  - backend/src/agents/prompts.py
tests:
  - Manual testing of all 4 chatbot prompts
  - Verified create, list, complete, update, delete operations
---

## Prompt

User reported AI chatbot errors after switching from OpenAI to Groq API. Initial symptoms:
- "Show me all my tasks" - ERROR
- "Mark my first task as complete" - ERROR
- "What tasks do I have for today?" - ERROR
- "Create a task to buy groceries" - WORKS

User emphasized: "avoid vibe coding, follow SDD to maintain the flow"

Debugging process involved multiple error iterations:
1. Frontend "Error loading tasks - Not Found" on dashboard
2. Backend validation error: `parameters` field expecting dict, receiving None
3. Backend validation error: `result` field expecting dict, receiving list
4. Groq API error: `tool_use_failed` with XML-format tool calls

## Response snapshot

Following strict SDD methodology, resolved all errors through systematic root cause analysis:

**Error 1: Port Mismatch (404 Not Found)**
- Root cause: Backend on port 8001, frontend config hardcoded to 8000
- Fix: Updated next.config.ts rewrites to use port 8001
- Evidence: Backend terminal showed no request logs, confirming routing failure

**Error 2: Validation Error (parameters=None)**
- Root cause: Groq tool calls can have None/empty arguments field
- Fix: Updated _format_tool_calls() to handle None parameters with fallback to {}
- File: backend/src/api/routes/chat.py

**Error 3: Validation Error (result as list)**
- Root cause: ToolCall model expected result: Dict, but list_tasks returns array
- Fix: Changed ToolCall.result type from Dict[str, Any] to Any
- File: backend/src/api/routes/chat.py

**Error 4: Groq XML-Format Tool Calling**
- Root cause: Known Groq/Llama issue - model generates `<function=name>` XML format instead of structured tool_calls when uncertain
- Contributing factors: Non-standard "default" field in schemas, empty required arrays, complex date-based queries
- Fixes applied:
  1. Removed "default" fields from all tool schemas (non-standard for OpenAI function calling)
  2. Removed empty required arrays after user_id stripping
  3. Added parallel_tool_calls=False to reduce model complexity
  4. Updated system prompt with explicit tool calling instructions
  5. Added date query handling guidance (list_tasks has no date filter)
- Files: backend/src/api/routes/chat.py, backend/src/agents/orchestrator.py, backend/src/agents/prompts.py

**Research Documentation:**
- Updated specs/016-ai-chatbot/research.md with "Groq Tool Calling Compatibility" section
- Documented root cause, contributing factors, fixes applied, and verification steps

## Outcome

- ✅ Impact: All 4 chatbot operations now working (create, list, complete, update, delete). Groq API integration stable.
- 🧪 Tests: Manual testing confirmed all prompts work without errors
- 📁 Files: 5 files modified (1 spec, 1 frontend config, 3 backend files)
- 🔁 Next prompts: Create ADR for LLM provider switch (OpenAI → Groq), initialize git repository, update tasks.md
- 🧠 Reflection: Strict SDD adherence prevented vibe coding. Every fix was evidence-based with root cause analysis. Groq's intermittent XML-format tool calling required prompt engineering solution.

## Evaluation notes (flywheel)

- Failure modes observed: Groq/Llama models intermittently revert to XML-format tool calls when uncertain (known community issue). Non-standard schema fields (default, empty required) exacerbate the problem.
- Graders run and results (PASS/FAIL): Manual testing - PASS (all 4 prompts working)
- Prompt variant (if applicable): Enhanced system prompt with explicit tool calling instructions and date query guidance
- Next experiment (smallest change to try): If XML-format errors recur, consider switching to different Groq model (qwen-qwq-32b) or adding retry logic with prompt adjustment
