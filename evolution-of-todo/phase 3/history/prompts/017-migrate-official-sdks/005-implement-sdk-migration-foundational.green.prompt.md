---
id: 005
title: Implement SDK Migration Foundational
stage: green
date: 2026-02-11
surface: agent
model: claude-opus-4-6
feature: 017-migrate-official-sdks
branch: none
user: asimh
command: /sp.implement
labels: ["openai-agents-sdk", "chatkit", "migration", "implementation", "phase-iii"]
links:
  spec: specs/017-migrate-official-sdks/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/requirements.txt
  - backend/src/agents/store_adapter.py
  - backend/src/agents/chatkit_server.py
  - backend/src/api/routes/chatkit.py
  - backend/src/api/main.py
  - frontend/components/chat/ChatKitChat.tsx
  - frontend/app/dashboard/chat/page.tsx
  - frontend/next.config.ts
  - specs/017-migrate-official-sdks/tasks.md
tests:
  - Manual verification: backend imports resolve correctly
  - Manual verification: /chatkit route registered in FastAPI app
  - Manual verification: frontend TypeScript compiles without errors
---

## Prompt

/sp.implement

## Response snapshot

Executed Phase 1 (Setup) and Phase 2 (Foundational) of the SDK migration — tasks T001 through T028 (28 tasks total).

**Phase 1 - Setup (T001-T006):**
- Verified Python 3.11+ and Node.js 18+ installed
- Upgraded openai-agents from 0.6.4 to 0.7.0 in backend/requirements.txt
- Installed openai-chatkit==1.6.0 in backend/requirements.txt
- Verified @openai/chatkit-react@^1.4.3 already in frontend package.json
- Verified MCP server running on /mcp endpoint
- Configured MCP_SERVER_URL environment variable

**Phase 2 - Foundational (T007-T028):**
- Created `backend/src/agents/store_adapter.py` — Full ChatKit Store interface implementation (13 methods) adapting existing Conversation/Message SQLModel models. Handles int-to-str ID conversion, JSON serialization of ThreadItems, cursor-based pagination, and legacy plain-text message wrapping.
- Created `backend/src/agents/chatkit_server.py` — TodoChatKitServer with Agent + Runner + MCPServerStreamableHttp integration. Uses OpenAIChatCompletionsModel for Cerebras compatibility. Singleton Agent pattern with lazy initialization. respond() method is ~20 lines replacing ~276 lines in old orchestrator.
- Created `backend/src/api/routes/chatkit.py` — Single POST /chatkit endpoint with X-User-Id auth, StreamingResponse for SSE events.
- Modified `backend/src/api/main.py` — Changed MCP from sse_app() to streamable_http_app(), added chatkit router.
- Created `frontend/components/chat/ChatKitChat.tsx` — ChatKit React component with useChatKit hook, custom fetch for X-User-Id injection, domainKey from env var.
- Modified `frontend/app/dashboard/chat/page.tsx` — Switched from ChatInterface to ChatKitChat component.
- Modified `frontend/next.config.ts` — Added /chatkit rewrite rule to proxy to backend.

**Key technical decisions:**
- MCP transport changed from SSE to Streamable HTTP (required by Agents SDK)
- Cerebras model via OpenAIChatCompletionsModel + AsyncOpenAI client
- Store adapter converts int PKs to str IDs for ChatKit compatibility
- Legacy messages wrapped into ChatKit types during deserialization

**Errors fixed during implementation:**
- ChatKit React: domainKey is required (not optional) in CustomApiConfig
- ChatKit React: header.title must be { text?: string } object, not plain string
- ChatKit React: theme must be "light" | "dark", not "auto"

## Outcome

- ✅ Impact: Phase 1 + Phase 2 complete (28/82 tasks). All foundational infrastructure for SDK migration is in place. User stories (Phase 3-6) can now proceed.
- 🧪 Tests: Manual verification only (hackathon/MVP context). Backend imports resolve, /chatkit route registered, frontend TypeScript compiles.
- 📁 Files: 9 files created/modified (3 new backend files, 1 new frontend component, 5 modified files)
- 🔁 Next prompts: Run Phase 3-7 validation tasks (T029-T082), remove deprecated orchestrator.py and ChatInterface.tsx, end-to-end runtime testing
- 🧠 Reflection: The Store adapter was the most complex piece — bridging int-based SQLModel PKs with str-based ChatKit IDs, plus handling legacy plain-text messages. The ChatKit React SDK had stricter TypeScript types than documented, requiring 3 fixes. The actual Agent+Runner code is remarkably concise (~20 lines of respond() logic).

## Evaluation notes (flywheel)

- Failure modes observed: API overload (529) on first Explore agent; ChatKit React TypeScript strictness not fully documented in SDK knowledge base
- Graders run and results (PASS/FAIL): Manual import verification PASS, route registration PASS, TypeScript compilation PASS
- Prompt variant (if applicable): /sp.implement standard execution
- Next experiment (smallest change to try): Runtime end-to-end test with actual MCP server and Cerebras API to validate full request flow
