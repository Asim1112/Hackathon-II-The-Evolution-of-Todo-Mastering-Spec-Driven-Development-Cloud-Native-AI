---
id: 001
title: Better Auth Integration Plan
stage: plan
date: 2026-02-07
surface: agent
model: claude-sonnet-4-5-20250929
feature: 015-integrate-better-auth
branch: 015-integrate-better-auth
user: asimh
command: /sp.plan
labels: ["better-auth", "authentication", "next.js", "fastapi", "neon", "architecture", "planning"]
links:
  spec: specs/015-integrate-better-auth/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/015-integrate-better-auth/plan.md
tests:
  - Constitution check validation
  - Technical context completeness
  - Phase dependency validation
---

## Prompt

Create:

- Architecture diagram showing Better Auth + Next.js + FastAPI + Neon integration flow
- File structure for new auth implementation (what files to create/modify)
- Implementation sequence with dependencies (what must be done first)
- Testing checklist based on success criteria from specification

Decisions needing documentation:

1. Database Schema Strategy
   Options:
   a) Let Better Auth auto-create all tables (recommended)
   b) Manually define Better Auth tables in SQLModel
   c) Use separate schemas for Better Auth vs FastAPI
   Tradeoffs:
   - Option A: Fastest, least error-prone, Better Auth handles migrations
   - Option B: More control, but complex and maintenance-heavy
   - Option C: Clean separation, but adds connection complexity
   Recommendation: Option A - standard Better Auth approach

2. Session Token Validation in FastAPI
   Options:
   a) FastAPI validates Better Auth JWT tokens for task endpoints
   b) FastAPI trusts user_id from frontend without validation
   c) Use shared session store between Next.js and FastAPI
   Tradeoffs:
   - Option A: Most secure, requires JWT verification library
   - Option B: Simplest but insecure for production
   - Option C: Complex, requires Redis or shared database queries
   Recommendation: Option A for production, Option B acceptable for hackathon MVP

3. Authentication Flow Routing
   Options:
   a) All auth through Next.js API routes → Neon (chosen in spec)
   b) Frontend calls FastAPI for auth → FastAPI uses Better Auth
   c) Hybrid: Better Auth in Next.js, but sync users to FastAPI
   Tradeoffs:
   - Option A: Clean separation, follows Better Auth design pattern
   - Option B: More integrated but violates Better Auth conventions
   - Option C: Dual source of truth, complex sync logic
   Recommendation: Option A (already chosen in spec)

4. Existing FastAPI Auth Endpoints
   Options:
   a) Remove /api/v1/auth/signup and /signin entirely
   b) Keep them but mark as deprecated
   c) Proxy them to Better Auth
   Tradeoffs:
   - Option A: Cleanest, prevents confusion
   - Option B: Safer rollback path during transition
   - Option C: Maintains backward compatibility but adds complexity
   Recommendation: Option A - remove to avoid dual auth systems

5. User Table Conflict Resolution
   Options:
   a) Drop existing FastAPI user table if present
   b) Rename FastAPI user table to app_user
   c) Better Auth uses custom table name (user_account)
   Tradeoffs:
   - Option A: Clean slate, but loses existing data
   - Option B: Preserves data, but requires code updates
   - Option C: Avoids conflict, but non-standard Better Auth setup
   Recommendation: Check database first; if empty use Option A, if data exists use Option B

## Response snapshot

Created comprehensive implementation plan covering:

**Summary**: Replace broken auth with Better Auth in Next.js API routes, maintaining FastAPI for tasks CRUD only.

**Technical Context**:
- Languages: TypeScript (Next.js 16+), Python 3.11+ (FastAPI)
- Dependencies: better-auth, @neondatabase/serverless, postgres, FastAPI, SQLModel
- Storage: Shared Neon PostgreSQL (Better Auth auto-creates 4 tables, FastAPI uses existing task table)
- Testing: Manual end-to-end + browser DevTools + database inspection
- Constraints: No data loss, no UI changes, SSL required, hackathon timeframe

**Constitution Check**: ✅ PASS with one justified deviation
- Better Auth in Next.js (not FastAPI) justified because it's a Node.js library following design patterns
- All other principles satisfied: spec-driven, zero manual coding, security-first, deterministic, agentic workflow

**Project Structure**:
- Frontend: auth-server.ts (NEW), route.ts (NEW), auth.ts (MODIFY), .env.local (MODIFY)
- Backend: main.py (MODIFY - CORS), auth.py (DELETE), tasks.py (MODIFY - JWT)
- 8 files total: 2 create, 4 modify, 2 evaluate

**Phase 0 - Research (NEEDS CLARIFICATION)**:
1. Database conflict resolution (inspect existing schema)
2. Better Auth + Neon integration best practices
3. JWT validation approach (MVP vs production)
4. Session persistence mechanism (cookies vs localStorage)

**Phase 1 - Design & Contracts**:
- Data model: Better Auth tables (user, session, account, verification) + FastAPI task (owner_id FK)
- API contracts: OpenAPI spec for /api/auth/* and modified /api/v1/tasks/* with JWT
- Quickstart guide: Environment setup, installation steps, troubleshooting
- Agent context update: Add Better Auth + Neon Serverless to context

**Architecture Diagram**: Created ASCII diagram showing:
- Browser → Next.js Better Auth → Neon DB
- Browser → Next.js → FastAPI Tasks → Neon DB
- Shared database with dual drivers (@neondatabase/serverless + psycopg2)
- HTTP-only cookies for session tokens
- JWT validation middleware in FastAPI

**Implementation Sequence (10 phases, 90 minutes)**:
1. Database Preparation (5 min) - inspect schema, resolve conflicts
2. Dependencies Installation (5 min) - npm install better-auth
3. Better Auth Server Config (10 min) - auth-server.ts + .env.local
4. Next.js API Routes (5 min) - [...all]/route.ts
5. Frontend Client Update (10 min) - fix auth.ts baseURL
6. Environment Configuration (5 min) - document .env variables
7. FastAPI Backend Updates (10 min) - remove auth routes, update CORS
8. Integration Testing (15 min) - E2E auth flow validation
9. Bug Fixes (20 min) - TypeScript errors, CORS, error handling
10. Documentation (10 min) - README, troubleshooting guide

**Testing Strategy**: 10 phases covering environment validation, Better Auth setup, API routes, frontend integration, E2E flow, FastAPI integration, error handling, production readiness

**Quality Validation**: Checkboxes for before /sp.tasks, before /sp.implement, and implementation success

**Risk Mitigation**: 5 identified risks with likelihood, impact, and mitigation strategies

**5 ADR Suggestions** (to be created after user approval):
1. Database Schema Strategy for Better Auth
2. FastAPI JWT Validation Approach
3. Authentication Routing via Next.js
4. Remove FastAPI Auth Endpoints
5. User Table Conflict Resolution

## Outcome

- ✅ Impact: Complete architectural plan created for Better Auth integration with 10-phase implementation sequence, addressing all 5 architectural decisions and constitutional requirements
- 🧪 Tests: Constitution check validation passed (1 justified deviation), 10-phase test strategy defined covering all acceptance criteria from spec
- 📁 Files: Created plan.md (1,338 lines), defined structure for research.md, data-model.md, quickstart.md, contracts/better-auth-api.yaml
- 🔁 Next prompts: Phase 0 research to resolve NEEDS CLARIFICATION items → Phase 1 design artifacts → /sp.tasks for task breakdown → /sp.adr for architectural decisions
- 🧠 Reflection: Plan successfully balances hackathon MVP approach (trusted header validation) with production upgrade path (full JWT verification), maintains clean separation between auth (Next.js) and business logic (FastAPI)

## Evaluation notes (flywheel)

- Failure modes observed: None - plan creation followed template structure, addressed all constitutional requirements, justified architectural deviation
- Graders run and results (PASS/FAIL): Constitution Check: PASS (1 justified deviation), Technical Context: PASS (all fields filled, no NEEDS CLARIFICATION at root level), Phase Dependencies: PASS (clear prerequisite chains)
- Prompt variant (if applicable): standard-planning-workflow
- Next experiment (smallest change to try): Execute Phase 0 research to resolve database conflicts and validate Better Auth + Neon configuration before proceeding to /sp.tasks
