---
id: 68
title: Fix tool calling via user_id extraction and streaming interceptor
stage: green
date: 2026-02-15
surface: agent
model: claude-opus-4-6
feature: chatbot
branch: main
user: developer
command: direct-prompt
labels: ["bugfix", "tool-calling", "user-id", "streaming", "cerebras"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/agents/chatkit_server.py
  - backend/src/agents/llm_interceptor.py
tests:
  - manual: verify list_tasks returns real user tasks (not empty)
  - manual: verify add_task creates task for authenticated user
  - manual: verify delete_task works after previous user_id duplicate fix
  - manual: check backend logs for [TOOL] and [LLM STREAM] entries
---

## Prompt

Tool calling is broken. list_tasks() is called repeatedly returning "You have no tasks" but add_task() is never called. User hypothesizes protocol adapter bug where Cerebras Chat Completions tool calls are not translated into ChatKit Responses API tool events. Requests tool-call extraction + mapping layer.

## Response snapshot

Root cause analysis revealed a cascading failure:

**Primary Bug (chatkit_server.py:98):** `user_id` extraction was completely broken. The code accessed `ctx.context.user_id` but `ctx.context` is `AgentContext` (not `RequestContext`). `AgentContext` has no `user_id` attribute, so ALL tool calls used `user_id="unknown"`. This meant `list_tasks("unknown")` always returned empty, confusing the model into never calling other tools.

**Fix:** Changed to `ctx.context.request_context.user_id` which correctly traverses `AgentContext.request_context: RequestContext` to get the authenticated user.

**Additional improvements:**
1. Added try/except with JSON error return in tool wrapper so tool failures are reported to the model (not swallowed)
2. Added comprehensive tool execution logging (`[TOOL] Executing/succeeded/failed`)
3. Rewrote LLM interceptor with `StreamingToolCallTracker` that wraps Cerebras streaming responses to log tool calls as they arrive, providing visibility into what tools the model generates

**Verified:** Unit test confirms `AgentContext.request_context.user_id` returns correct value while old `AgentContext.user_id` path returns nothing.

## Outcome

- Impact: All 5 MCP tools (add_task, list_tasks, complete_task, update_task, delete_task) should now work with correct user isolation
- Tests: Import verification PASS, user_id extraction path PASS
- Files: 2 files modified (chatkit_server.py, llm_interceptor.py)
- Next prompts: Restart backend, test full conversation flow with task CRUD, verify streaming logs show tool calls
- Reflection: AgentContext wraps RequestContext - always verify the full context chain when accessing attributes through SDK wrappers

## Evaluation notes (flywheel)

- Failure modes observed: Wrong context attribute path causing all tools to operate on wrong user; silent failures due to no error handling in tool wrapper
- Graders run and results (PASS/FAIL): Import PASS, user_id extraction PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): If tools still not called after user_id fix, add tool_choice="auto" to ModelSettings
