---
id: 005
title: Switch LLM Provider from Groq to Cerebras
stage: misc
date: 2026-02-11
surface: agent
model: claude-sonnet-4-5-20250929
feature: 016-ai-chatbot
branch: main
user: asimh
command: continuation
labels: ["llm-provider", "cerebras", "groq", "migration", "rate-limits"]
links:
  spec: specs/016-ai-chatbot/spec.md
  ticket: null
  adr: history/adr/001-llm-provider-for-ai-chatbot.md
  pr: null
files:
  - specs/016-ai-chatbot/research.md
  - backend/src/config/settings.py
  - backend/src/agents/orchestrator.py
  - backend/.env
  - backend/src/api/routes/chat.py
  - history/adr/001-llm-provider-for-ai-chatbot.md
tests:
  - Pending: User must obtain Cerebras API key from https://cloud.cerebras.ai
  - Pending: Test all 5 chatbot operations (add_task, list_tasks, complete_task, update_task, delete_task)
  - Pending: Verify tool calling works correctly with Cerebras
  - Pending: Verify no rate limit errors with 1M tokens/day limit
---

## Prompt

User request: "Switch the LLM provider from Groq to Cerebras. MCP SDK is already implemented — do not modify it. This is a provider swap only, not a refactor. Keep: Spec-Kit Plus architecture, Tool/function calling, Agent orchestration and memory. After the switch, verify that: Tool calling still works, Agents can run multi-step workflows, Token limits are no longer constrained by Groq. Proceed. YOU MUST FOLLOW SPEC DRIVEN DEVELOPMENT TO IMPLEMENT THIS, STRICTLY AVOID VIBE CODING. DO YOUR BEST TO MAINTAIN SDD FLOW"

Context: Groq daily token quota (100,000 tokens/day) was exhausted during testing with 429 rate limit error. Cerebras offers 1,000,000 tokens/day (10x more) with same OpenAI-compatible API and llama-3.3-70b model.

## Response snapshot

Followed strict SDD flow:

**1. Update Documentation FIRST (SDD requirement)**
- Updated research.md with "Second Change: Groq → Cerebras" section
- Documented reason (Groq 100K token/day limit exhausted)
- Documented why Cerebras (1M tokens/day, 10x capacity, OpenAI-compatible)
- Documented code impact (3-setting change)

**2. Code Changes (Targeted, Minimal)**
- settings.py: Changed groq_api_key → cerebras_api_key, groq_base_url → cerebras_base_url (https://api.cerebras.ai/v1), groq_model → cerebras_model (llama-3.3-70b)
- orchestrator.py: Updated client initialization to use settings.cerebras_* instead of settings.groq_*, updated docstring comments
- .env: Changed GROQ_API_KEY → CEREBRAS_API_KEY (value cleared, user must obtain from https://cloud.cerebras.ai)
- chat.py: Updated comments referencing Groq/Llama to Cerebras/Llama (lines 61, 80)

**3. Update ADR (SDD requirement)**
- Updated ADR-001 with "Evolution History" section documenting both provider changes
- Updated Decision section to reflect current Cerebras provider
- Updated Consequences section with 10x token benefit
- Updated Alternatives section to include Groq as replaced alternative

**4. Create PHR (SDD requirement)**
- Created this PHR (005-switch-groq-to-cerebras.misc.prompt.md)

**Files Changed:**
- specs/016-ai-chatbot/research.md (added Cerebras documentation)
- backend/src/config/settings.py (3 settings changed)
- backend/src/agents/orchestrator.py (client init + comments)
- backend/.env (API key variable renamed)
- backend/src/api/routes/chat.py (2 comments updated)
- history/adr/001-llm-provider-for-ai-chatbot.md (evolution history added)

**Zero Changes To:**
- MCP server (mcp_server.py) - unchanged
- MCP tools - unchanged
- Chat endpoint logic - unchanged
- Frontend - unchanged
- Tool calling patterns - unchanged

## Outcome

- ✅ Impact: Successfully migrated from Groq to Cerebras following strict SDD (docs first, then code, then ADR, then PHR). Provider swap complete with 10x more daily tokens (1M vs 100K).
- 🧪 Tests: Pending user action - user must obtain Cerebras API key from https://cloud.cerebras.ai and update .env file, then test all 5 chatbot operations
- 📁 Files: 6 files modified (research.md, settings.py, orchestrator.py, .env, chat.py, ADR-001)
- 🔁 Next prompts: User must obtain Cerebras API key, update .env, restart backend, test chatbot operations
- 🧠 Reflection: SDD flow strictly followed - documentation updated BEFORE code changes, ADR updated to reflect evolution history, PHR created for traceability. Migration is minimal (3-setting change) due to OpenAI-compatible API.

## Evaluation notes (flywheel)

- Failure modes observed: None - migration not yet tested (pending user API key)
- Graders run and results (PASS/FAIL): Pending - awaiting user API key setup and testing
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): After user obtains API key, test single operation (add_task) first to verify tool calling works, then test remaining 4 operations
