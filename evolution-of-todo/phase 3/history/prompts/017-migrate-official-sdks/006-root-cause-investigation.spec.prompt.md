---
id: 006
title: Root-Cause Investigation for Agent Tool Calling Failure
stage: spec
date: 2026-02-12
surface: agent
model: claude-sonnet-4-5-20250929
feature: 017-migrate-official-sdks
branch: not-in-git
user: user
command: none
labels: ["root-cause", "debugging", "spec-driven-development", "agent-tools", "mcp", "function-calling"]
links:
  spec: specs/agent-tool-calling-fix/
  ticket: null
  adr: null
  pr: null
files:
  - specs/agent-tool-calling-fix/01-ground-truth-architecture.md
  - specs/agent-tool-calling-fix/02-runtime-reality.md
  - specs/agent-tool-calling-fix/03-root-cause-analysis.md
  - specs/agent-tool-calling-fix/04-correctness-restoration.md
  - specs/agent-tool-calling-fix/05-change-record.md
tests:
  - None (investigation and specification work)
---

## Prompt

This issue has NOT been resolved after multiple attempts.

Therefore, incremental fixes are not acceptable.

The system is showing these critical failures:

• FN_CALL=False is printed at runtime

• Tool calls never execute

• The LLM hallucinates task lists

• The assistant claims actions that never happened

• Previous messages get overwritten or mutated

These symptoms prove that the Agent → Tool → State → Chat loop is broken.

Your job is to perform a ROOT-CAUSE investigation, not a surface fix.

You must follow Spec-Driven Development.

Produce the following in strict order:

STEP 1 — **Ground-Truth Architecture Spec**
Describe how this system is supposed to work:
• ChatKit
• Agent
• MCP
• LLM
• Tool registry
• Database
• Conversation memory

STEP 2 — **Runtime Reality Spec**
Describe what is ACTUALLY happening at runtime based on:
• FN_CALL=False
• No tool execution
• Hallucinated state
• Message rewriting

STEP 3 — **Root-Cause Analysis Spec**
Identify exactly:
• Which layer is breaking the agent loop
• Whether FN_CALL=False is a cause or a symptom
• Why the system is falling back into text-only LLM mode

STEP 4 — **Correctness Restoration Spec**
Define precisely:
• What must be true for the system to be correct
• What flags, configs, or wiring must exist
• What invariants must be enforced so this can never happen again

STEP 5 — **Change Record**
List every required change.
NO code yet.

Wait for my approval before implementing anything.

## Response snapshot

Performed comprehensive root-cause investigation following Spec-Driven Development methodology:

**Investigation Phase:**
- Used Explore agent to map Phase 3 architecture comprehensively
- Analyzed 7+ critical files including chatkit_server.py, mcp_server.py, store_adapter.py
- Searched entire codebase for FN_CALL variable (not found - confirmed as SDK internal)
- Identified exact failure point: Line 166 of chatkit_server.py

**Specification Documents Created:**

1. **Ground-Truth Architecture Spec** (01-ground-truth-architecture.md)
   - Documented how ChatKit, Agent, MCP, LLM, Tool Registry, Database, and Conversation Memory should work
   - Defined expected end-to-end flow with 14 detailed steps
   - Created architecture diagram showing component interactions
   - Established critical success criteria (7 requirements)

2. **Runtime Reality Spec** (02-runtime-reality.md)
   - Documented actual broken behavior with evidence
   - Analyzed 5 critical symptoms with database verification
   - Identified missing components (tools in LLM request, tool execution loop, validation)
   - Proved system is in "text-only mode" instead of "tool-calling mode"

3. **Root-Cause Analysis Spec** (03-root-cause-analysis.md)
   - Analyzed 8-link agent-tool-calling chain
   - Identified PRIMARY failure point: Link [6] - LLM Request Formation
   - Determined FN_CALL=False is a SYMPTOM, not a cause
   - Explained why system falls back to text-only mode (graceful degradation)
   - Provided 4 verification tests to confirm diagnosis

4. **Correctness Restoration Spec** (04-correctness-restoration.md)
   - Defined 6 required system properties with enforcement mechanisms
   - Specified 3 configuration categories (model selection, tool calling, logging)
   - Detailed 3 critical wiring requirements (tool extraction, passing, model factory)
   - Established 5 invariants that must be enforced
   - Provided 3 testing requirements

5. **Change Record** (05-change-record.md)
   - Listed 26 changes across 4 priority levels (P0-P3)
   - Defined 3 investigation tasks
   - Provided 5-phase implementation plan (4-5 days estimated)
   - Included rollback plan and risk assessment
   - Established clear success criteria

**Key Findings:**

- **Root Cause**: Tools are not being passed to `Runner.run_streamed()` at line 166 of chatkit_server.py
- **Failure Point**: LLM Request Formation - tools parameter missing from API request
- **FN_CALL Status**: Symptom of missing tools, not the cause
- **Secondary Issue**: Cerebras llama-3.3-70b may not support OpenAI function calling
- **Message Corruption**: Separate issue from non-unique ID generation

**Critical Path to Fix:**
1. Implement tool extraction utility (P0-1)
2. Pass tools to Runner.run_streamed() (P0-2)
3. Add OpenAI fallback if Cerebras doesn't support function calling (P1-1 through P1-4)
4. Verify and test

**Confidence Level**: 90% - All evidence points to this root cause. Remaining uncertainty is whether Cerebras supports function calling.

## Outcome

- ✅ Impact: Complete root-cause diagnosis with 5 comprehensive specification documents following SDD methodology
- 🧪 Tests: No tests run (investigation phase only)
- 📁 Files: Created 5 specification documents in specs/agent-tool-calling-fix/
- 🔁 Next prompts: "Approve and implement P0 changes" or "Run investigations INV-1 and INV-2 first"
- 🧠 Reflection: This investigation revealed that the system was silently failing by falling back to text-only mode. The root cause is clear (tools not passed to LLM), but implementation requires verifying SDK API and Cerebras capabilities first.

## Evaluation notes (flywheel)

- Failure modes observed: Silent degradation to text-only mode, SDK graceful fallback masking critical failure, lack of logging preventing earlier diagnosis
- Graders run and results (PASS/FAIL): N/A (investigation work)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): INV-1 (verify Runner.run_streamed() accepts tools parameter) and INV-2 (test Cerebras function calling support) before implementing P0-2
