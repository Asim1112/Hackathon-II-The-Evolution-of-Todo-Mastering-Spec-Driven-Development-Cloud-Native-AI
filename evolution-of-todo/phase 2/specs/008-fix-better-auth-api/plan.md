# Implementation Plan: Fix Better Auth React Client API Mismatch

**Branch**: `008-fix-better-auth-api` | **Date**: 2026-02-05 | **Spec**: [link to spec.md]
**Input**: Feature specification from `/specs/008-fix-better-auth-api/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implementation to fix Better Auth React Client API mismatch by replacing non-existent exports (signIn, signUp, signOut) with the correct Better Auth React API provided by the installed SDK. The solution involves discovering the actual API exports, updating the frontend authentication integration in lib/auth.ts and hooks/useAuth.tsx, and ensuring compatibility with the backend Better Auth configuration.

## Technical Context

**Language/Version**: TypeScript 5.x, Next.js 16.1.1, React 19.2.3, Better Auth 1.4.9
**Primary Dependencies**: Next.js with App Router, React, Better Auth (JWT-based, stateless), clsx for class name utilities
**Storage**: Client-side only (localStorage for token storage)
**Testing**: Next.js built-in testing for component rendering and authentication flows
**Target Platform**: Web browsers (Chrome, Firefox, Safari, Edge) with JWT-based authentication
**Project Type**: Web application (frontend + backend)
**Performance Goals**: Fast authentication flows, minimal performance impact from auth operations
**Constraints**: Must follow Better Auth SDK patterns and JWT-based stateless authentication as required by constitution
**Scale/Scope**: Authentication system serving all frontend users with secure token handling

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Compliance with Project Constitution**:
- ✅ Spec-Driven Development: Following spec → plan → tasks → implementation workflow
- ✅ Zero Manual Coding: Using automated tools to align auth integration with real API
- ✅ Security-First Design: Ensuring JWT authentication remains secure with proper client integration
- ✅ Deterministic and Reproducible Outputs: Creating consistent auth integration that works reliably
- ✅ Full-Stack Architecture Standards: Frontend uses Better Auth (JWT-based, stateless) as required by constitution
- ✅ End-to-End Agentic Workflow: Following the Agentic Dev Stack workflow from specification to deployment
- ✅ Technology Stack Compliance: Using Better Auth 1.4.9 as required per constitution
- ✅ Frontend Integrity: Ensuring authentication system has access to required utility functions
- ✅ JWT Authentication Standard: Maintaining enforcement of JWT authentication on API routes

## Project Structure

### Documentation (this feature)

```text
specs/008-fix-better-auth-api/
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
│   ├── error.tsx
│   ├── layout.tsx
│   └── page.tsx
├── components/
│   ├── Header.tsx
│   ├── Providers.tsx
│   ├── auth/
│   ├── tasks/
│   └── ui/
│       ├── Button.tsx
│       └── Spinner.tsx
├── hooks/
│   ├── useAuth.tsx      # Imports from lib/auth.ts (to be updated)
│   ├── useTasks.ts
│   └── useToast.tsx
├── lib/
│   ├── api-client.ts
│   ├── auth.ts          # Current import: signIn, signUp, signOut from "better-auth/react" (TO BE FIXED)
│   └── utils.ts
├── types/
└── tsconfig.json
```

**Structure Decision**: Web application with separate frontend (Next.js) and backend (FastAPI) directories as detected in the repository structure. This fix addresses a frontend authentication integration issue that uses Better Auth client SDK incorrectly.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
|[N/A] | [No violations identified] | [All constitution principles followed] |
