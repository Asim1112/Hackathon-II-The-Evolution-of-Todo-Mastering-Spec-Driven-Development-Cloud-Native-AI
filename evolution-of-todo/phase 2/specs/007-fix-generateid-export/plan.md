# Implementation Plan: Fix Missing generateId Export in Utils Module

**Branch**: `007-fix-generateid-export` | **Date**: 2026-02-05 | **Spec**: [link to spec.md]
**Input**: Feature specification from `/specs/007-fix-generateid-export/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implementation of missing `generateId` export in `frontend/lib/utils.ts` module to resolve Next.js build failure caused by "Export generateId doesn't exist in target module" error. The solution involves adding the `generateId` utility function to the existing utility module that already exports `cn`, ensuring the toast notification system can properly import and use the function for generating unique identifiers.

## Technical Context

**Language/Version**: TypeScript 5.x, Next.js 16.1.1, React 19.2.3
**Primary Dependencies**: Next.js with App Router, React, clsx for class name utilities, toast notifications
**Storage**: Client-side only (no storage required for this fix)
**Testing**: Next.js built-in testing for component rendering
**Target Platform**: Web browsers (Chrome, Firefox, Safari, Edge)
**Project Type**: Web application (frontend + backend)
**Performance Goals**: Fast toast generation, minimal performance impact from ID generation
**Constraints**: Must follow Next.js path alias conventions and TypeScript best practices
**Scale/Scope**: Single utility function serving the toast notification system

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Compliance with Project Constitution**:
- ✅ Spec-Driven Development: Following spec → plan → tasks → implementation workflow
- ✅ Zero Manual Coding: Using automated tools to add the missing utility function
- ✅ Deterministic and Reproducible Outputs: Adding the missing function to ensure consistent behavior
- ✅ Full-Stack Architecture Standards: Frontend uses Next.js 16+ with App Router as required
- ✅ End-to-End Agentic Workflow: Following the Agentic Dev Stack workflow from specification to deployment
- ✅ Technology Stack Compliance: Using TypeScript and Next.js as required per constitution
- ✅ Frontend Integrity: Ensuring UI components have access to required utility functions
- ✅ Build System Compliance: Resolving module resolution errors to enable proper builds

## Project Structure

### Documentation (this feature)

```text
specs/007-fix-generateid-export/
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
│   ├── useAuth.tsx
│   ├── useTasks.ts
│   └── useToast.tsx       # Imports generateId from @/lib/utils (line 5)
├── lib/
│   ├── api-client.ts
│   ├── auth.ts
│   └── utils.ts           # Currently missing generateId export - TO BE UPDATED
├── types/
└── tsconfig.json
```

**Structure Decision**: Web application with separate frontend (Next.js) and backend (FastAPI) directories as detected in the repository structure. This fix addresses a frontend issue in the Next.js application's utility module.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
|[N/A] | [No violations identified] | [All constitution principles followed] |
