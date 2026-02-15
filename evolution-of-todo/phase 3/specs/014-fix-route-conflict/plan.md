# Implementation Plan: Fix Next.js API Route Conflict

**Branch**: `014-fix-route-conflict` | **Date**: 2026-02-06 | **Spec**: [link to spec.md]

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This plan addresses the Next.js routing conflict that occurs when two routes have the same specificity: `/api/tasks` and `/api/tasks/[[...path]]`. The issue stems from having both a direct route implementation and an optional catch-all route, which Next.js prohibits. The solution involves removing the conflicting direct route while preserving the proxy functionality to FastAPI.

## Technical Context

**Language/Version**: TypeScript/JavaScript (frontend), Python 3.8+ (backend)
**Primary Dependencies**: Next.js 16+ (frontend), FastAPI (backend), Better Auth (authentication)
**Storage**: Browser localStorage for tokens, Neon PostgreSQL for data
**Testing**: Manual testing of routing functionality, API endpoint validation
**Target Platform**: Web application (Next.js + FastAPI)
**Project Type**: web (full-stack with separate frontend and backend)
**Performance Goals**: <2s response time for API operations, instant route resolution
**Constraints**: Must maintain architectural split (Next.js as proxy only), preserve Better Auth functionality
**Scale/Scope**: Individual user routing, single tenant architecture

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- ✅ Security-First Design: Better Auth JWT authentication maintained as required
- ✅ Full-Stack Architecture Standards: Next.js 16+ + FastAPI + Neon PostgreSQL as required
- ✅ Better Auth (JWT-based) remains implemented for user management as required
- ✅ Frontend acts as proxy for backend APIs, not direct implementation as required
- ✅ Deterministic outputs: Route resolution is predictable and consistent

## Project Structure

### Documentation (this feature)

```text
specs/014-fix-route-conflict/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
frontend/
├── app/
│   ├── api/
│   │   └── tasks/           # Route conflict location
│   │       ├── [[...path]]/   # Valid proxy route: [[...path]]/route.ts
│   │       └── route.ts       # Conflicting route to be removed
│   └── ...
└── .env.local               # BACKEND_URL configuration for proxy

backend/
└── src/
    └── api/
        └── routes/
            └── tasks.py     # Actual task API endpoints
```

**Structure Decision**: Maintain frontend/backend separation with Next.js acting as proxy to FastAPI, resolving route conflict by removing direct implementation.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [None] | [No violations found] | [N/A] |