---
id: 002
title: Context-Specific Implementation Amendments
stage: constitution
date: 2026-02-07
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: 015-integrate-better-auth
user: asimh
command: /sp.constitution
labels: ["constitution", "amendments", "hackathon-mvp", "context-aware", "flexibility"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - Constitution validation (no unresolved placeholders)
  - Version bump validation (1.0.0 → 1.1.0 MINOR)
  - Sync impact report completeness
---

## Prompt

Amend constitution to resolve 3 CRITICAL violations blocking implementation of feature 015-integrate-better-auth while maintaining constitutional rigor for production releases.

**Context:**
Current constitution contains NON-NEGOTIABLE principles written for ideal production conditions. Feature 015 (Better Auth integration) is a hackathon MVP that encounters 3 architectural conflicts:
1. Better Auth library is Node.js-only (no Python port), requiring Next.js implementation instead of FastAPI
2. Hackathon timeline constraints make test-first approach impractical for MVP delivery
3. Red-green-refactor cycle adds overhead incompatible with rapid prototyping needs

**Analysis shows:** These conflicts stem from constitution being too prescriptive about HOW to achieve principles rather than WHAT outcomes are required. The principles themselves (security, testability, quality) remain valid, but implementation flexibility is needed.

---

## Proposed Amendments:

### Amendment 1: Full-Stack Architecture Standards

**Current Principle:**
"Backend must use FastAPI + SQLModel with Neon Serverless PostgreSQL; Frontend must use Next.js 16+ App Router with stateless authentication; Better Auth (JWT-based) must be implemented for user management."

**Proposed Amendment:**
"Backend must use FastAPI + SQLModel with Neon Serverless PostgreSQL; Frontend must use Next.js 16+ App Router with stateless authentication; Better Auth (JWT-based) must be implemented for user management in the appropriate runtime environment:
- If authentication library requires Node.js runtime: Implement in Next.js frontend with JWT validation in FastAPI backend
- If authentication library has Python support: Implement in FastAPI backend
- In both cases: JWT tokens must be validated, multi-user isolation must be enforced, session security must use HTTP-only cookies"

**Rationale:**
- Better Auth is a Node.js library with no official Python port (verified via documentation review)
- Forcing FastAPI implementation would require custom Python authentication system (violates "use battle-tested libraries" principle)
- Amendment maintains security outcomes (JWT validation, session security) while allowing runtime-appropriate placement
- Architecture decision properly documented in plan.md with tradeoffs analysis

**Impact:**
- Feature 015: UNBLOCKS implementation (Better Auth can be placed in Next.js as planned)
- Future features: No impact (Python-native auth libraries can still use FastAPI)
- Constitution scope: NARROWS from "must implement in FastAPI" to "must implement in appropriate runtime"

**Options Considered:**
- Option A: Amend constitution to allow runtime-appropriate placement (CHOSEN)
- Option B: Force FastAPI implementation with custom auth system (rejected - increases complexity, reduces security via untested code)
- Option C: Switch to Python-native auth library (rejected - Better Auth chosen for superior DX and Neon integration)

---

### Amendment 2: Spec-Driven Development (Test Requirements)

**Current Principle:**
"All development follows the spec → plan → tasks → implementation workflow; Specifications must be complete and approved before any coding begins; Every feature must have corresponding test cases defined in the tasks document before implementation."

**Proposed Amendment:**
"All development follows the spec → plan → tasks → implementation workflow; Specifications must be complete and approved before any coding begins; Every feature must have test strategy defined:
- **Production features:** Test cases must be written and defined in tasks.md before implementation (test-first approach required)
- **Hackathon/MVP features:** Test cases may be documented as post-MVP enhancement with manual validation checklist in tasks.md (implementation-first acceptable)
- **Proof-of-concept features:** Manual testing acceptable with upgrade path to automated tests documented

In all cases, the chosen test strategy must be explicitly stated in tasks.md header."

**Rationale:**
- Current principle is binary (test-first REQUIRED) which blocks rapid prototyping
- Hackathon context requires speed-to-demo over test coverage
- Amendment maintains test PLANNING (strategy must be documented) while allowing test TIMING flexibility
- Manual validation checklists still provide quality gates (120+ validation tasks in feature 015)
- Post-MVP test addition is explicitly planned, not forgotten

**Impact:**
- Feature 015: UNBLOCKS implementation (tasks.md explicitly documents "tests optional for MVP, manual validation used")
- Future features: Flexibility to choose test-first (production) vs implementation-first (MVP) based on context
- Constitution scope: EXPANDS from "test-first always" to "test strategy always, timing flexible"

**Options Considered:**
- Option A: Allow test timing flexibility with mandatory strategy documentation (CHOSEN)
- Option B: Remove test requirement entirely (rejected - loses quality rigor)
- Option C: Maintain test-first requirement (rejected - blocks hackathon delivery)

---

### Amendment 3: End-to-End Agentic Workflow (Red-Green-Refactor)

**Current Principle:**
"All development phases must follow the Agentic Dev Stack workflow from specification to deployment; Each phase must be validated before proceeding to the next; Comprehensive testing must be integrated throughout the workflow."

**AND in Development Workflow section:**
"All changes must follow the red-green-refactor cycle with proper testing."

**Proposed Amendment:**
"All development phases must follow the Agentic Dev Stack workflow from specification to deployment; Each phase must be validated before proceeding to the next; Testing approach must match feature scope:
- **Production features:** Red-green-refactor cycle with comprehensive automated testing
- **Hackathon/MVP features:** Implementation-with-validation approach (validation tasks in tasks.md, refactor in subsequent iteration)
- **Proof-of-concept features:** Validation tasks only, refactor when promoted to production

Development Workflow updated to:
'All production code must follow the red-green-refactor cycle with proper testing. Hackathon/MVP scope may use implementation-first approach with validation tasks and refactor phase documented as post-MVP enhancement.'"

**Rationale:**
- Red-green-refactor is ideal for production but adds iteration overhead incompatible with hackathon timelines
- Amendment maintains VALIDATION requirement (120+ validation tasks in feature 015) while removing REFACTOR timing constraint
- Refactor phase explicitly documented as Phase 9 "Post-MVP Hardening" in feature plan
- Quality gates preserved via validation checkpoints after each user story

**Impact:**
- Feature 015: UNBLOCKS implementation (validation tasks present, refactor documented for later)
- Future features: Flexibility to choose TDD (production) vs validation-first (MVP)
- Constitution scope: MAINTAINS workflow rigor, REMOVES timing prescription

**Options Considered:**
- Option A: Allow workflow flexibility with mandatory validation (CHOSEN)
- Option B: Remove red-green-refactor requirement entirely (rejected - loses quality discipline)
- Option C: Maintain strict red-green-refactor (rejected - incompatible with hackathon pace)

---

## Cross-Amendment Consistency:

All three amendments follow consistent pattern:
1. **Preserve WHAT** (outcomes): Security, testability, quality, validation
2. **Relax HOW** (methods): Allow implementation flexibility based on context
3. **Require DOCUMENTATION**: Chosen approach must be explicit in artifacts
4. **Maintain PRODUCTION RIGOR**: Full requirements apply to production releases

**Scope Definitions:**
- **Hackathon/MVP:** Time-boxed delivery (days/weeks), demo-focused, manual validation acceptable, refactor documented for later
- **Production:** User-facing release, automated tests required, TDD workflow, comprehensive coverage
- **Proof-of-concept:** Experimental, disposable, minimal testing, clear upgrade path if promoted

## Response snapshot

Successfully amended constitution from version 1.0.0 → 1.1.0 with 3 context-specific implementation amendments:

**Amendment 1: Full-Stack Architecture Standards**
- Added runtime-appropriate authentication placement guidance
- Allows Better Auth in Next.js frontend (Node.js runtime) with JWT validation in FastAPI backend
- Maintains security outcomes (JWT validation, multi-user isolation, HTTP-only cookies) as mandatory

**Amendment 2: Spec-Driven Development (Test Requirements)**
- Expanded test requirements to support context-specific approaches
- Production features: Test-first required
- Hackathon/MVP features: Implementation-first acceptable with validation tasks
- Proof-of-concept features: Manual testing with upgrade path
- All contexts require explicit test strategy documentation in tasks.md header

**Amendment 3: End-to-End Agentic Workflow (Red-Green-Refactor)**
- Expanded workflow requirements to support context-specific approaches
- Production features: Red-green-refactor cycle mandatory
- Hackathon/MVP features: Implementation-with-validation acceptable, refactor documented for post-MVP
- Proof-of-concept features: Validation only, refactor when promoted

**New Section Added: Context-Specific Implementation**
- Defines production vs hackathon/MVP vs proof-of-concept requirements
- Production: Full rigor (test-first, red-green-refactor, 80% coverage, complete docs)
- Hackathon/MVP: Flexibility (implementation-first ok, 120+ validation tasks, upgrade path documented)
- Proof-of-concept: Minimal (manual testing, basic validation, promotion path required)
- Transition guidelines for promoting features between contexts

**Sync Impact Report Generated:**
- Version change: 1.0.0 → 1.1.0 (MINOR bump - new guidance added, no breaking changes)
- Modified principles: 3 (Spec-Driven Development, Full-Stack Architecture Standards, End-to-End Agentic Workflow)
- Added sections: 1 (Context-Specific Implementation)
- Removed sections: 0
- Templates status:
  - ✅ plan-template.md: Already aligns with context-aware principles
  - ✅ spec-template.md: Already supports flexible test strategies
  - ✅ tasks-template.md: Already supports optional tests with strategy documentation
  - ⚠️ commands/*.md: Manual review recommended for outdated strict test-first references
- Follow-up TODOs: Document upgrade paths, add compliance examples

**Governance Updates:**
- Added Amendment Process section (rationale, versioning, sync reports)
- Added Compliance Review section (constitution check, /sp.analyze validation)
- Updated version metadata: 1.1.0 | Ratified: 2025-12-22 | Last Amended: 2026-02-07

**Validation Results:**
✅ No unresolved placeholder tokens
✅ Version bump justified (MINOR - new guidance without breaking changes)
✅ Dates in ISO format (YYYY-MM-DD)
✅ Principles declarative and testable
✅ Sync impact report complete

**Feature 015 Impact:**
✅ CRITICAL violation C1 (Better Auth location): RESOLVED - Constitution now explicitly allows Next.js placement
✅ CRITICAL violation C2 (Test requirements): RESOLVED - Constitution now allows implementation-first for MVP
✅ CRITICAL violation C3 (Red-green-refactor): RESOLVED - Constitution now allows validation-first for MVP
✅ Implementation UNBLOCKED - All 3 violations cleared

## Outcome

- ✅ Impact: Constitution updated to version 1.1.0, unblocking feature 015 implementation while maintaining production rigor for future releases
- 🧪 Tests: Validation passed (no placeholders, version correct, dates formatted, sync report complete)
- 📁 Files: Updated .specify/memory/constitution.md with 3 amendments + new Context-Specific Implementation section
- 🔁 Next prompts: Re-run /sp.analyze to verify CRITICAL violations cleared → Proceed with /sp.implement for feature 015
- 🧠 Reflection: Amendments successfully balance hackathon MVP pragmatism with production quality standards by focusing on WHAT outcomes are required (security, validation, testability) while relaxing HOW those outcomes are achieved (test timing, workflow order, auth placement)

## Evaluation notes (flywheel)

- Failure modes observed: None - amendments applied cleanly, sync report generated, version bumped correctly
- Graders run and results (PASS/FAIL): Constitution Validation: PASS (no placeholders), Version Bump: PASS (1.0.0 → 1.1.0 MINOR justified), Sync Impact Report: PASS (complete), Governance Compliance: PASS (amendment process followed)
- Prompt variant (if applicable): comprehensive-amendment-with-rationale
- Next experiment (smallest change to try): Re-run /sp.analyze on feature 015 to confirm all 3 CRITICAL violations are now resolved and implementation is unblocked
