---
id: 006
title: Fix Agent Hallucination Bug - Delete Operations
stage: misc
date: 2026-02-11
surface: agent
model: claude-sonnet-4-5-20250929
feature: 016-ai-chatbot
branch: main
user: asimh
command: continuation
labels: ["ai-safety", "hallucination", "state-verification", "delete-task", "critical-bug"]
links:
  spec: specs/016-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
  - backend/src/agents/prompts.py
  - backend/src/mcp/mcp_server.py
  - specs/016-ai-chatbot/research.md
tests:
  - Pending: Ask agent to delete duplicate tasks
  - Pending: Verify agent calls list_tasks BEFORE deletion (before-state)
  - Pending: Verify agent calls delete_task for each duplicate
  - Pending: Verify agent calls list_tasks AFTER deletion (after-state)
  - Pending: Verify agent reports before/after comparison
  - Pending: Confirm tasks actually deleted in database
---

## Prompt

User report: "There is a critical tool–agent reliability bug in my Phase-3 AI Todo system. The AI claimed it deleted duplicate tasks, but after re-querying with list_tasks, all duplicates were still present. This proves the agent is hallucinating success instead of verifying real system state."

**User's interaction showing the bug:**
```
User: "can you delete duplicate tasks safely? if yes then go on"

AI: "I've deleted the duplicate tasks. There are now 6 tasks remaining: [lists 6 tasks]"
Actions taken: list_tasks, list_tasks, delete_task (x6)

User: "again confirm me with perfection that you really deleted the duplicate task?"

AI: "I apologize for any confusion earlier. To confirm with perfection, I would like to retrieve the list of tasks again..."

User: "ok, confirm me how many tasks are there?"

AI: "There are 12 tasks in total." [lists all 12 tasks including the "deleted" ones]
Actions taken: list_tasks
```

**User's requirements:**
1. Inspect how delete_task is implemented in the backend
2. Verify whether it is actually committing deletions to the database
3. Check whether incorrect IDs, transactions, or async handling could cause silent failure
4. Add mandatory post-action state verification:
   - After any delete_task calls, the agent must re-call list_tasks
   - The agent must compare before/after state
   - The agent must only report success if the state has truly changed
5. Update the agent prompt and/or constitution file so the assistant is forbidden from claiming success without verification

**User emphasized:** "This is a production-grade AI safety issue, not just a UI bug. Fix it as a real AI engineer would. Follow spec driven development to resolve this, avoid vibe coding."

## Response snapshot

**Root Cause Analysis:**

1. **Transaction Rollback Bug** (discovered during investigation):
   - Manual `session.commit()` calls in MCP tool handlers conflicted with SQLModel's Session context manager
   - `_SessionContext.__exit__` called `next(self._gen)` which exited the Session context, triggering rollback
   - This undid the manual commit, causing silent failures
   - Backend logs showed `ROLLBACK` instead of `COMMIT`

2. **Agent Hallucination Bug** (primary issue):
   - Agent trusted tool return values (e.g., `{"status": "deleted"}`) as proof of success
   - Agent lacked explicit instructions to verify mutations by re-querying state
   - Agent assumed tool success responses meant state changed
   - No understanding that database transactions, network failures, or bugs can cause silent failures

**SDD Flow Applied (Docs First, Then Code):**

**Step 1: Update Constitution** (`.specify/memory/constitution.md`)
- Added new section: "AI Safety Principles (Phase 3)"
- Added "State Verification Mandate (CRITICAL)" subsection
- Mandates: After ANY mutation (add/delete/complete/update), agent MUST re-query state and verify change
- Forbids: Claiming success based solely on tool return values
- Requires: Explicit before/after state comparison and truthful reporting
- Includes: Correct and incorrect verification pattern examples
- Added "Hallucination Prevention" and "Error Transparency" subsections

**Step 2: Update Agent Prompt** (`backend/src/agents/prompts.py`)
- Added "CRITICAL: State Verification Mandate" section at top of TODO_ASSISTANT_PROMPT
- Provides step-by-step verification pattern:
  1. Before-state: Query current state before mutation
  2. Execute: Call the mutation tool
  3. After-state: Re-query system state after mutation
  4. Compare: Explicitly verify the change occurred
  5. Report: Only claim success if verification confirms the change
- Includes concrete examples:
  - Correct pattern: list_tasks → delete_task → list_tasks → compare → report
  - Forbidden pattern: delete_task → report (no verification)
- Explains why verification is required
- Mandates transparency if verification fails

**Step 3: Fix Transaction Bug** (`backend/src/mcp/mcp_server.py`)
- Removed manual `session.commit()` calls from all 4 tool handlers (add_task, complete_task, update_task, delete_task)
- Changed to `session.flush()` to persist changes within transaction
- Let SQLModel's Session context manager handle auto-commit on successful exit
- Updated `_SessionContext` docstring to explain auto-commit behavior

**Step 4: Document in Research** (`specs/016-ai-chatbot/research.md`)
- Added "Agent Hallucination Bug - Delete Operations" section
- Documented root cause, contributing factors, impact, fix applied
- Included verification pattern example
- Listed testing requirements

**Files Changed:**
- `.specify/memory/constitution.md` (added AI Safety Principles section - 60+ lines)
- `backend/src/agents/prompts.py` (added State Verification Mandate to prompt - 40+ lines)
- `backend/src/mcp/mcp_server.py` (removed manual commits, added flush - 4 functions modified)
- `specs/016-ai-chatbot/research.md` (documented hallucination bug - 80+ lines)

**Verification Pattern (Now Enforced):**
```
User: "Delete duplicate tasks"

Agent MUST:
1. Call list_tasks → Count: 12 tasks (before-state)
2. Identify duplicates (tasks 7-12)
3. Call delete_task(7), delete_task(8), ..., delete_task(12)
4. Call list_tasks again → Count: 6 tasks (after-state)
5. Compare: 12 - 6 = 6 deleted ✓
6. Report: "I've deleted 6 duplicate tasks. Verified: Your task list now has 6 tasks (previously 12)."
```

**Forbidden Pattern (Now Explicitly Banned):**
```
User: "Delete duplicate tasks"

Agent:
1. Call delete_task(7) → {"status": "deleted"}
2. Report: "I've deleted the duplicate tasks." ❌ NO VERIFICATION
```

## Outcome

- ✅ Impact: Fixed critical AI safety issue - agent now MUST verify all mutations by re-querying state. Constitution and prompt updated with explicit verification mandate. Transaction rollback bug fixed.
- 🧪 Tests: Pending user testing - agent must demonstrate verification behavior (list_tasks before/after deletion with explicit comparison)
- 📁 Files: 4 files modified (constitution.md, prompts.py, mcp_server.py, research.md)
- 🔁 Next prompts: User must test agent with "delete duplicate tasks" command and verify: 1) Agent calls list_tasks before deletion, 2) Agent calls delete_task for each duplicate, 3) Agent calls list_tasks after deletion, 4) Agent reports before/after comparison, 5) Tasks actually deleted in database
- 🧠 Reflection: This was a production-grade AI safety issue requiring systematic fix. SDD flow strictly followed: constitution first (defines principles), then prompt (enforces behavior), then code (fixes transaction bug), then docs (records issue). The agent was hallucinating success without verifying reality - a critical failure mode for AI systems. Fix addresses both the technical bug (transaction rollback) and the AI behavior bug (lack of verification mandate).

## Evaluation notes (flywheel)

- Failure modes observed:
  1. Agent hallucination - claiming success without verification
  2. Transaction rollback - manual commits conflicting with context manager
  3. Silent failures - no error messages when operations fail
- Graders run and results (PASS/FAIL): Pending - awaiting user testing of verification behavior
- Prompt variant (if applicable): Added "State Verification Mandate" section to agent prompt (60+ lines of explicit verification instructions)
- Next experiment (smallest change to try): Test with single delete operation first to verify agent calls list_tasks before/after, then test with multiple deletions to verify batch verification behavior
