---
id: 003
title: Create Implementation Plan for SDK Migration
stage: plan
date: 2026-02-11
surface: agent
model: claude-sonnet-4-5-20250929
feature: 017-migrate-official-sdks
branch: 017-migrate-official-sdks
user: asimh
command: /sp.plan
labels: ["implementation-plan", "phase-0-research", "phase-1-design", "sdk-migration", "architecture", "technical-decisions"]
links:
  spec: specs/017-migrate-official-sdks/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/017-migrate-official-sdks/plan.md
  - specs/017-migrate-official-sdks/research.md
  - specs/017-migrate-official-sdks/data-model.md
  - specs/017-migrate-official-sdks/contracts/chatkit-endpoint.yaml
  - specs/017-migrate-official-sdks/quickstart.md
tests:
  - Manual: Review plan completeness and technical accuracy
  - Manual: Verify all Phase 0 research patterns extracted from knowledge base
  - Manual: Verify Phase 1 design artifacts (data-model, contracts, quickstart)
  - Manual: Validate technical decisions against SDK documentation
---

## Prompt

User command: `/sp.plan Create: Detailed migration plan to achieve full Phase-III compliance by replacing the current AI orchestration and chat UI with the official required SDKs.`

**User Requirements:**
- Produce clear, executable plan for integrating OpenAI Agents SDK (backend) and ChatKit (frontend)
- Preserve 100% functionality, MCP architecture, stateless design, database flows, user experience
- Deliverables: Architecture sketch (before/after), file-by-file changes, step-by-step integration, detailed mappings, risk assessment
- Document all technical decisions with options/tradeoffs
- Reference patterns from knowledge files (OpenAI-Agents-SDK-Knowledge.md, Chatkit-SDK-Documentation.md)
- Define testing & validation strategy (Phase III compliance, regression testing, audit simulation)
- First step: Deeply re-analyze knowledge files (5,215 lines total)
- Minimize changes, maintain API contract, use official SDK patterns exactly
- Not planning: New features, changes outside AI/chat UI layers, large-scale refactoring

## Response snapshot

**Approach:**
Created comprehensive implementation plan following SDD-RI plan template structure with complete Phase 0 (Research) and Phase 1 (Design) artifacts.

**Plan Structure:**

1. **Summary**: Migration overview, primary goal (Phase III compliance), technical approach (5 key steps)

2. **Technical Context**: Language/version, dependencies, storage, testing, platform, constraints, scale

3. **Constitution Check**: Comprehensive compliance assessment against all constitutional requirements (✅ PASS on all gates)

4. **Project Structure**: Documentation tree and source code tree with [CREATE], [MODIFY], [REMOVE], [PRESERVE] annotations

5. **Architecture Overview**:
   - Current architecture diagram (manual orchestration, custom UI)
   - Target architecture diagram (Agent + Runner + ChatKitServer, ChatKit component)
   - Key architectural changes table (7 components)

6. **Phase 0: Research & Pattern Extraction**:
   - 4 research tasks (Agents SDK patterns, ChatKit patterns, Store adapter, Frontend integration)
   - Expected findings with code examples
   - Created research.md (comprehensive pattern extraction from 5,215 lines)

7. **Phase 1: Design & Contracts**:
   - Data model documentation (ThreadMetadata ↔ Conversation, ThreadItem ↔ Message)
   - Store adapter interface (13 methods)
   - API contracts (OpenAPI spec for /chatkit endpoint)
   - Quickstart guide (9-step setup instructions)
   - Created data-model.md, contracts/chatkit-endpoint.yaml, quickstart.md

8. **Implementation Strategy**:
   - 6-step migration plan (Store adapter → ChatKitServer → /chatkit endpoint → ChatKit component → page update → deprecate old)
   - Detailed implementation for each step with code examples
   - Key decisions and testing approach for each step

9. **Technical Decisions**:
   - 6 major decisions documented with options table, rationale, implementation
   - Decision 1: MCP Integration (MCPServerStreamableHttp)
   - Decision 2: Store Adapter Pattern
   - Decision 3: Agent Lifecycle (Singleton)
   - Decision 4: History Loading (Fixed limit 20 items)
   - Decision 5: Thread ID Strategy (user_id as thread_id)
   - Decision 6: Error Handling (Let ChatKit SDK handle)

10. **Risk Assessment & Mitigation**:
    - 5 major risks identified with impact/probability/mitigation
    - Risk 1: MCPServerStreamableHttp connection failure
    - Risk 2: Store adapter serialization bugs
    - Risk 3: Functional regression in tool calling
    - Risk 4: ChatKit frontend integration issues
    - Risk 5: Performance degradation

11. **Testing & Validation Strategy**:
    - Phase III compliance verification (6 requirements checklist)
    - Regression testing plan (4 test suites: NLU, multi-turn, verification, error handling)
    - 12 NLU test cases, 5 multi-turn test cases, 4 verification test cases, 4 error test cases
    - 4 manual test scenarios (new user, returning user, complex workflow, error recovery)
    - Post-migration audit simulation (code inspection, functional testing, architecture review)
    - 10 acceptance criteria

12. **File-by-File Change Summary**:
    - Backend: 3 files CREATE, 0 MODIFY, 1 REMOVE, 6+ PRESERVE
    - Frontend: 1 file CREATE, 1 MODIFY, 1 REMOVE, all others PRESERVE
    - Summary statistics: +630 lines, -476 lines, net +154 lines (80% orchestration reduction)

13. **Implementation Timeline**:
    - Phase 0: Research (1 day)
    - Phase 1: Design (1 day)
    - Phase 2: Implementation (3-5 days)
    - Phase 3: Testing & Validation (2-3 days)
    - Phase 4: Cleanup & Documentation (1 day)
    - Total: 8-10 days

14. **Next Steps**: Command sequence (/sp.tasks → /sp.implement), success criteria reminder

15. **Conclusion**: Summary of migration benefits and readiness for task generation

**Phase 0 Deliverable (research.md):**
- Extracted all patterns from 5,215 lines of knowledge base
- 7 major patterns documented with code examples and line references
- Pattern 1: Agent initialization with MCP integration
- Pattern 2: Runner execution with streaming
- Pattern 3: Session management (NOT NEEDED for ChatKit)
- Pattern 4: ChatKitServer implementation
- Pattern 5: Store interface implementation
- Pattern 6: FastAPI integration
- Pattern 7: Frontend ChatKit component
- Serialization strategy (ThreadItem ↔ Message.content JSON)
- Pagination strategy (cursor-based)
- Decision summary table (6 decisions)

**Phase 1 Deliverables:**

1. **data-model.md**: Entity mappings and serialization
   - ThreadMetadata ↔ Conversation mapping
   - ThreadItem ↔ Message mapping (JSON serialization)
   - RequestContext for user isolation
   - Store adapter interface (13 methods with implementations)
   - Pagination details (cursor-based)
   - Database schema (UNCHANGED)

2. **contracts/chatkit-endpoint.yaml**: OpenAPI 3.0 specification
   - /chatkit POST endpoint
   - 3 request types (SendMessage, LoadHistory, Action)
   - Response types (JSON, SSE)
   - Error responses (400, 401, 404, 500)
   - Security scheme (X-User-ID header)

3. **quickstart.md**: Developer setup guide
   - Prerequisites verification
   - Dependency installation (backend + frontend)
   - Environment configuration
   - Database setup
   - 9-step startup sequence
   - 3 endpoint tests (send message, load history, tool calling)
   - Frontend testing steps
   - Phase III compliance audit
   - Troubleshooting (5 common issues)
   - Performance tuning tips

**Key Technical Decisions:**
- MCPServerStreamableHttp for MCP integration (preserves existing server, cache_tools_list=True)
- Store adapter pattern (zero schema changes, JSON serialization)
- Singleton Agent (stateless, better performance)
- Fixed history limit 20 items (predictable tokens, fast queries)
- user_id as thread_id (matches current behavior, simple)
- Let ChatKit SDK handle errors (consistent format, less code)

**Architecture Highlights:**
- Before: ~100 lines manual orchestration, custom chat UI
- After: ~20 lines ChatKitServer.respond(), ChatKit React component
- 80% code reduction in orchestration layer
- Zero schema changes (Store adapter preserves existing models)
- Zero breaking changes (100% functional parity)

## Outcome

- ✅ Impact: Created comprehensive implementation plan (plan.md - 500+ lines) with complete Phase 0 research (research.md - 400+ lines) and Phase 1 design artifacts (data-model.md - 400+ lines, contracts/chatkit-endpoint.yaml - 200+ lines, quickstart.md - 400+ lines). Total: 1,900+ lines of planning documentation covering architecture, technical decisions, implementation strategy, testing, and developer setup. Plan provides step-by-step migration path with 6 major technical decisions documented, 5 risks assessed, 4 test suites defined (25 test cases total), and 10 acceptance criteria. Ready for /sp.tasks command.
- 🧪 Tests: Manual review required - verify plan completeness, technical accuracy, SDK pattern correctness
- 📁 Files: 5 files created (plan.md, research.md, data-model.md, contracts/chatkit-endpoint.yaml, quickstart.md)
- 🔁 Next prompts: User should proceed with `/sp.tasks` to generate actionable task breakdown, then `/sp.implement` to execute migration
- 🧠 Reflection: This planning phase required deep analysis of 5,215 lines of SDK documentation to extract accurate implementation patterns. The plan balances comprehensiveness (detailed architecture, decisions, risks, testing) with actionability (step-by-step implementation, code examples, file-by-file changes). Key insight: The migration is primarily a replacement task (not new feature development), so the plan emphasizes preservation (zero schema changes, 100% functional parity) while achieving compliance. The 6 technical decisions are well-documented with options/tradeoffs, making the plan audit-ready. The testing strategy is comprehensive (25 test cases across 4 suites) to ensure zero regressions. Phase 0 research and Phase 1 design artifacts provide complete context for implementation phase.

## Evaluation notes (flywheel)

- Failure modes observed: None - planning completed successfully with all required artifacts
- Graders run and results (PASS/FAIL): Constitution check - PASS (all gates met), Plan completeness - PASS (all sections complete)
- Prompt variant (if applicable): Standard /sp.plan workflow with comprehensive user requirements
- Next experiment (smallest change to try): Proceed with /sp.tasks to generate actionable task breakdown. Tasks should reference specific sections of plan.md and include acceptance criteria from testing strategy. Each task should be independently testable and map to one of the 6 implementation steps.
