---
id: 002
title: Update SDK Migration Spec with Real SDK Behavior
stage: spec
date: 2026-02-11
surface: agent
model: claude-sonnet-4-5-20250929
feature: 017-migrate-official-sdks
branch: 017-migrate-official-sdks
user: asimh
command: continuation
labels: ["specification", "knowledge-analysis", "sdk-patterns", "correction", "openai-agents-sdk", "chatkit-sdk"]
links:
  spec: specs/017-migrate-official-sdks/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/017-migrate-official-sdks/spec.md
  - specs/017-migrate-official-sdks/checklists/requirements.md
tests:
  - Manual: Verify all SDK patterns match knowledge base documentation
  - Manual: Confirm MCPServerStreamableHttp pattern is correct
  - Manual: Validate Store interface details (13 methods)
  - Manual: Check AgentContext integration pattern
---

## Prompt

User asked: "have you deeply explored and go through those two files from where you will get material/content and knowledge to implement OpenAI agents sdk and chatkit sdk? if not yet, then when you will explore?"

I admitted: "No, I have NOT deeply explored those two files yet. What I did: I read only the first ~100 lines of each file (table of contents)"

User instructed: "Yes. First deeply read and internalize both knowledge files. After that, update or amend the existing specification to reflect the real OpenAI Agents SDK and ChatKit SDK behavior. Do not create plans, tasks, or code yet. After the spec is corrected, I will run /sp.plan."

User then said: "Continue" to proceed with the knowledge file analysis and specification update.

## Response snapshot

**Approach:**
1. Read OpenAI-Agents-SDK-Knowledge.md completely (1,788 lines) - COMPLETED
2. Read Chatkit-SDK-Documentation.md completely (3,427 lines) - COMPLETED (read in chunks due to file size)
3. Analyzed both knowledge files for accurate SDK patterns and behavior
4. Updated specification to reflect REAL SDK behavior (not assumptions)

**Key SDK Patterns Discovered:**

**OpenAI Agents SDK:**
- Agent with mcp_servers=[MCPServerStreamableHttp(...)] for MCP integration (NOT Agent.tools)
- MCPServerStreamableHttp with cache_tools_list=True recommended for performance
- Runner.run_streamed(agent, input, context=agent_context) for streaming execution
- Session management (SQLiteSession) is NOT needed for ChatKit integration (ChatKit Store handles persistence)

**ChatKit SDK:**
- ChatKitServer base class with respond() method that yields ThreadStreamEvent objects
- Store interface: 13 async methods (load_thread, save_thread, load_threads, load_thread_items, add_thread_item, save_item, load_item, delete_thread, delete_thread_item, save_attachment, load_attachment, delete_attachment, generate_item_id)
- AgentContext bridges ChatKit and Agents SDK (provides thread, store, request_context)
- simple_to_agent_input() converts ChatKit thread items to agent input format
- stream_agent_response() converts agent streaming output to ChatKit events
- FastAPI integration: server.process(body, context) returns StreamingResult or JSONResult
- Store.load_thread_items() uses cursor-based pagination (after parameter, limit 20-50, order="asc")

**Specification Updates Made:**

1. **Functional Requirements (FR-003, FR-005, FR-006, FR-007, FR-014, FR-015):**
   - Added MCPServerStreamableHttp pattern for MCP integration
   - Added ChatKitServer.respond() with AgentContext integration
   - Added Store interface details (13 methods) as adapter over existing models
   - Added simple_to_agent_input() and stream_agent_response() helpers
   - Clarified frontend uses ChatKit React component with apiUrl="/chatkit"
   - Clarified thread_id maps to conversation_id

2. **Key Entities:**
   - Added Runner, MCPServerStreamableHttp, AgentContext, ThreadMetadata, ThreadItem
   - Detailed Store interface (13 methods)
   - Clarified Agent configuration (name, instructions, model, mcp_servers)

3. **Success Criteria:**
   - Updated SC-003: 80% code reduction (not 60%) based on knowledge base examples
   - Updated SC-004: ChatKit endpoint pattern with server.process()
   - Updated SC-005: Store.load_thread_items() with pagination details
   - Updated SC-006: Agent.mcp_servers parameter (not Agent.tools)
   - Updated SC-009: ChatKit React component with apiUrl
   - Updated SC-010: Specific helper functions (simple_to_agent_input, stream_agent_response)

4. **Scope & Boundaries:**
   - Added specific implementation details: ChatKitServer subclass, Store adapter (13 methods), /chatkit endpoint
   - Clarified widget system deferred (Card, Button, Form available but out of scope)
   - Clarified action handlers deferred (interactive widgets out of scope)
   - Clarified client tools deferred (browser callbacks out of scope)

5. **Assumptions:**
   - Replaced generic assumptions with specific SDK patterns
   - Added MCPServerStreamableHttp HTTP URL pattern
   - Added Store adapter pattern details
   - Added ThreadMetadata/ThreadItem serialization details
   - Clarified Session management NOT needed

6. **Dependencies:**
   - Added specific SDK classes and methods
   - Added key patterns from knowledge base with code examples
   - Clarified MCPServerStreamableHttp with cache_tools_list=True
   - Clarified simple_to_agent_input() and stream_agent_response() helpers

7. **Constraints:**
   - Added Store implementation requirement (all 13 methods)
   - Added pagination requirement (cursor-based with after parameter)
   - Added MCP integration constraint (MCPServerStreamableHttp, not direct tools)
   - Added widget system deferred constraint

8. **Risks:**
   - Updated risks to reflect real integration challenges
   - Added MCPServerStreamableHttp integration risk
   - Added Store adapter implementation risk
   - Added ChatKit-to-Agents SDK bridge risk

9. **References:**
   - Added complete code examples from knowledge base
   - Added MCPServerStreamableHttp pattern with cache_tools_list=True
   - Added ChatKitServer.respond() implementation pattern
   - Added Store interface method list
   - Added FastAPI integration pattern
   - Added frontend ChatKit component usage

10. **Checklist Update:**
    - Documented all corrections made
    - Listed key patterns discovered
    - Confirmed specification ready for /sp.plan phase

## Outcome

- ✅ Impact: Updated specification to reflect REAL SDK behavior after deeply analyzing 5,215 lines of knowledge base documentation (OpenAI Agents SDK: 1,788 lines, ChatKit SDK: 3,427 lines). Corrected 10 major sections with accurate SDK patterns, code examples, and integration details. Specification now provides precise implementation guidance based on official SDK documentation.
- 🧪 Tests: Manual verification required - compare updated spec against knowledge base files to confirm all patterns are accurate
- 📁 Files: 2 files updated (spec.md - corrected 10 sections, checklists/requirements.md - documented corrections)
- 🔁 Next prompts: User should proceed with `/sp.plan` to design implementation approach using the corrected SDK patterns
- 🧠 Reflection: This was a critical correction phase. The initial specification was based on assumptions without reading the full knowledge base files (only read first ~100 lines). After deeply reading all 5,215 lines, I discovered significant differences: (1) MCP integration uses Agent.mcp_servers with MCPServerStreamableHttp, NOT Agent.tools; (2) ChatKit requires implementing 13 Store methods as adapter layer; (3) AgentContext with simple_to_agent_input/stream_agent_response helpers bridge the two SDKs; (4) Session management (SQLiteSession) is NOT needed because ChatKit Store handles persistence; (5) Widget system is available but should be deferred to minimize scope. The specification now accurately reflects real SDK behavior and provides concrete code examples from the knowledge base. This correction prevents implementation failures that would have occurred from following incorrect patterns.

## Evaluation notes (flywheel)

- Failure modes observed: Initial specification created without deeply reading knowledge base files (only read table of contents). This would have led to incorrect implementation patterns and wasted effort.
- Graders run and results (PASS/FAIL): Specification quality checklist - PASS after corrections (all criteria met with accurate SDK patterns)
- Prompt variant (if applicable): User caught the issue by asking if I had deeply explored the knowledge files, then instructed me to read them completely before updating the spec
- Next experiment (smallest change to try): Proceed with /sp.plan using the corrected specification. The plan should reference specific code examples from the References section and follow the exact patterns documented (MCPServerStreamableHttp, ChatKitServer.respond(), Store adapter, AgentContext helpers).
