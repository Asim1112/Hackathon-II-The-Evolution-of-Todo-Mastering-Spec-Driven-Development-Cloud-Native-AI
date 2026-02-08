# Implementation Plan: Integrate Better Auth with Next.js and FastAPI

**Branch**: `015-integrate-better-auth` | **Date**: 2026-02-07 | **Spec**: [spec.md](./spec.md)
**Reconstructed**: 2026-02-08 (Post-implementation reconciliation — code is source of truth)
**Status**: Implemented (MVP)

## Summary

Better Auth is integrated as a **cookie-based session authentication** library running in Next.js API routes (`/api/auth/*`). It stores user accounts, credentials (scrypt-hashed passwords), and sessions in the shared Neon PostgreSQL database. FastAPI handles task CRUD operations (`/api/v1/tasks/*`), receiving user identity through a trusted `X-User-Id` header extracted client-side from the Better Auth session. This approach eliminates the "Failed to fetch" and 500 errors that blocked authentication, while maintaining separation of concerns.

**Critical Correction**: The original plan described JWT-based authentication. Better Auth uses **cookie-based sessions**, not JWTs. Session tokens are opaque identifiers referencing database rows, not self-contained JSON Web Tokens.

## Technical Context

**Language/Version**:
- Frontend: TypeScript with Next.js 16+ (App Router)
- Backend: Python 3.11+ with FastAPI
- Database Client: `@neondatabase/serverless` Pool + `ws` (for Better Auth), psycopg2/SQLModel (for FastAPI)

**Primary Dependencies (Actual)**:
- `better-auth` (v1.x) — Cookie-based session authentication library
- `better-auth/next-js` — Provides `toNextJsHandler()` and `nextCookies()` plugin
- `better-auth/react` — Provides `createAuthClient()` with `useSession()` hook
- `better-auth/cookies` — Provides `getSessionCookie()` for middleware
- `@neondatabase/serverless` — Neon's serverless Postgres driver (Pool)
- `ws` — WebSocket implementation required by `@neondatabase/serverless` in Node.js
- FastAPI + SQLModel + psycopg2-binary — Backend framework and ORM

**Storage**:
- Shared Neon Serverless PostgreSQL database
- Better Auth tables (auto-created): `user`, `session`, `account`, `verification`
- FastAPI tables: `task` (with `owner_id` referencing `user.id`)

**Testing**:
- Manual end-to-end testing through browser UI (Hackathon/MVP context)
- Network inspection via browser DevTools
- Database inspection via Neon SQL Editor

**Target Platform**:
- Development: Windows (localhost:3000 for Next.js, localhost:8000 for FastAPI)
- Production: Vercel (Next.js) + Cloud hosting for FastAPI + Neon PostgreSQL

**Performance Goals**:
- Authentication requests complete in <500ms p95
- Session cookie validation adds <10ms overhead (cookie presence check, no crypto)
- Database connection pool via Neon Pool handles concurrent requests

**Constraints**:
- Must use existing Neon database
- SSL required for Neon connections (sslmode=require)
- `nextCookies()` plugin is mandatory — without it, cookies are not set in Next.js server context
- `ws` package required for `@neondatabase/serverless` in Node.js runtime
- Development must complete within hackathon timeframe

## Constitution Check

### Constitutional Requirements Analysis

✅ **Spec-Driven Development (NON-NEGOTIABLE)**
- Status: PASS (recovered after drift)
- Evidence: Spec reconstructed from working code. Drift report documents all deviations
- Test strategy: Manual validation (Hackathon/MVP context per constitution v1.1.0)

✅ **Zero Manual Coding**
- Status: PASS
- Evidence: All code generated through Claude Code agentic workflow

⚠️ **Security-First Design**
- Status: PARTIAL COMPLIANCE (MVP context)
- Cookie-based session authentication (not JWT as constitution states)
- HTTP-only cookies prevent XSS (constitutional requirement met)
- Multi-user task isolation via `owner_id` filtering (met)
- `X-User-Id` header trusted without cryptographic validation (MVP trade-off)
- **Constitution v1.1.0 Hackathon context**: "trusted headers acceptable with JWT validation documented for post-MVP" — COMPLIANT

✅ **Deterministic and Reproducible Outputs**
- Status: PASS
- Environment variables documented, Better Auth config version-controlled

⚠️ **Full-Stack Architecture Standards**
- Status: PARTIAL COMPLIANCE
- Better Auth in Next.js (not FastAPI) — justified: Node.js library, no Python port
- Constitution v1.1.0: "If authentication library requires Node.js runtime: Implement in Next.js frontend" — COMPLIANT

✅ **End-to-End Agentic Workflow**
- Status: PASS (recovered)
- Implementation-with-validation approach (Hackathon/MVP context)

### Gate Decision: **COMPLIANT** under Hackathon/MVP context

---

## Project Structure (Actual)

### Documentation

```text
specs/015-integrate-better-auth/
├── spec.md              # Feature specification (RECONSTRUCTED 2026-02-08)
├── plan.md              # This file (RECONSTRUCTED 2026-02-08)
├── tasks.md             # Task breakdown (RECONSTRUCTED 2026-02-08)
├── drift-report.md      # Forensic drift analysis (CREATED 2026-02-08)
└── compliance-audit.md  # Constitutional compliance audit (CREATED 2026-02-08)
```

### Source Code (Actual File Map)

```text
frontend/
├── app/
│   ├── api/
│   │   └── auth/
│   │       └── [...all]/
│   │           └── route.ts        # Better Auth catch-all handler
│   ├── auth/
│   │   ├── signin/page.tsx         # Sign in page (UI unchanged)
│   │   └── signup/page.tsx         # Sign up page (UI unchanged)
│   └── dashboard/page.tsx          # Protected dashboard
├── lib/
│   ├── auth-server.ts              # Better Auth server config + nextCookies() + Neon Pool + ws
│   ├── auth-client.ts              # createAuthClient() with destructured exports
│   ├── api-client.ts               # Task API client with X-User-Id header from session
│   └── utils.ts                    # Utility functions (includes formatRelativeTime)
├── hooks/
│   └── useAuth.tsx                 # Auth context using authClient.useSession()
├── components/
│   └── auth/
│       ├── SignInForm.tsx           # Uses react-hook-form isSubmitting
│       └── SignUpForm.tsx           # Uses react-hook-form isSubmitting
├── middleware.ts                   # Route protection via getSessionCookie()
├── next.config.ts                  # Rewrites /api/v1/* to FastAPI (auth handled locally)
├── .env.local                      # BETTER_AUTH_SECRET, BETTER_AUTH_URL, DATABASE_URL
└── package.json                    # better-auth, @neondatabase/serverless, ws

backend/
├── src/
│   ├── api/
│   │   ├── main.py                 # FastAPI app, CORS, task router (NO auth middleware)
│   │   └── routes/
│   │       └── tasks.py            # Task CRUD with get_current_user_id dependency
│   ├── auth/
│   │   ├── dependencies.py         # get_current_user_id reads X-User-Id header (ACTIVE)
│   │   └── middleware.py           # JWT middleware (DEAD CODE — never imported)
│   ├── models/
│   │   └── task.py                 # Task model with owner_id field
│   ├── config/
│   │   └── settings.py             # App settings
│   └── database/
│       └── session.py              # SQLModel database session
└── .env                            # DATABASE_URL
```

**Deleted Files** (during implementation):
- `frontend/lib/auth.ts` — old client with wrapper functions (replaced by `auth-client.ts`)
- `frontend/app/api/auth/[[...auth]]/route.ts` — conflicting optional catch-all route
- `backend/src/api/routes/auth.py` — old FastAPI auth endpoints (deleted in earlier feature)
- `frontend/scripts/diagnose-auth.mjs` — diagnostic script (cleanup)
- `frontend/scripts/fix-user-table.mjs` — migration script (cleanup)
- `frontend/scripts/test-signup.mjs` — test script (cleanup)

---

## Architecture Diagram (Actual)

```
┌─────────────────────────────────────────────────────────────────┐
│                         Browser Client                          │
│  ┌────────────┐         ┌────────────┐        ┌──────────────┐ │
│  │ Sign Up UI │────────▶│ Sign In UI │───────▶│ Dashboard UI │ │
│  └────────────┘         └────────────┘        └──────────────┘ │
│         │                      │                       │        │
└─────────┼──────────────────────┼───────────────────────┼────────┘
          │                      │                       │
          │ POST /api/auth/      │ POST /api/auth/       │ GET /api/v1/tasks
          │ sign-up/email        │ sign-in/email         │ (relative URL)
          ▼                      ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                Next.js Frontend (localhost:3000)                 │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  middleware.ts                                            │   │
│  │  getSessionCookie(request) → allow/redirect              │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  /app/api/auth/[...all]/route.ts                         │   │
│  │  toNextJsHandler(auth) → Better Auth handles all auth    │   │
│  │                                                           │   │
│  │  Endpoints (managed by Better Auth):                      │   │
│  │  POST /api/auth/sign-up/email  → Create user + session   │   │
│  │  POST /api/auth/sign-in/email  → Validate + session      │   │
│  │  POST /api/auth/sign-out       → Invalidate session      │   │
│  │  GET  /api/auth/get-session    → Return session data     │   │
│  └──────────────────────────────────────────────────────────┘   │
│           │                                                      │
│           │ Sets HTTP-only cookie:                               │
│           │ better-auth.session_token (opaque session ID)        │
│           │ via nextCookies() plugin                             │
│           │                                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  lib/auth-server.ts (Server-side)                         │   │
│  │  betterAuth({                                             │   │
│  │    database: new Pool({ connectionString }),               │   │
│  │    emailAndPassword: { enabled: true },                   │   │
│  │    session: { cookieCache: { enabled: true } },           │   │
│  │    plugins: [nextCookies()]  ← CRITICAL                   │   │
│  │  })                                                       │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  lib/auth-client.ts (Client-side)                         │   │
│  │  createAuthClient() → { signIn, signUp, signOut,         │   │
│  │                          useSession }                     │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  lib/api-client.ts (Task API Client)                      │   │
│  │  authClient.getSession() → extract user.id               │   │
│  │  → sends X-User-Id header with task requests             │   │
│  │  → uses relative URLs (/api/v1/tasks)                    │   │
│  └──────────────────────────────────────────────────────────┘   │
│           │                                                      │
│           │ next.config.ts rewrites:                             │
│           │ /api/v1/* → http://127.0.0.1:8000/api/v1/*          │
│           ▼                                                      │
└─────────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────┐
│                FastAPI Backend (localhost:8000)                   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  CORS Middleware                                          │   │
│  │  allow_origins: ["http://localhost:3000",                 │   │
│  │                   "http://127.0.0.1:3000"]               │   │
│  │  allow_credentials: true                                  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Task Routes (/api/v1/tasks/*)                            │   │
│  │  Dependency: get_current_user_id()                        │   │
│  │  → reads X-User-Id header (Header(..., alias="X-User-Id"))│  │
│  │  → filters tasks by owner_id = user_id                    │   │
│  │  → returns 403 if task.owner_id != user_id                │   │
│  │                                                           │   │
│  │  NO JWT validation middleware (MVP approach)              │   │
│  │  NO auth middleware registered in app                     │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
            │                              │
            ▼                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Shared Neon PostgreSQL Database                   │
│                                                                  │
│  ┌─── Better Auth Tables ───┐    ┌─── FastAPI Tables ─────┐    │
│  │                           │    │                         │    │
│  │  user                     │    │  task                   │    │
│  │  ├─ id (text PK)         │    │  ├─ id (int PK)        │    │
│  │  ├─ email                │    │  ├─ title              │    │
│  │  ├─ name                 │    │  ├─ description        │    │
│  │  ├─ emailVerified        │    │  ├─ is_completed       │    │
│  │  ├─ image                │    │  ├─ owner_id ──────────┼──┐ │
│  │  ├─ createdAt            │    │  ├─ created_at         │  │ │
│  │  └─ updatedAt            │    │  └─ updated_at         │  │ │
│  │                           │    └─────────────────────────┘  │ │
│  │  account                  │                                 │ │
│  │  ├─ id                   │    owner_id references ──────────┘ │
│  │  ├─ userId (FK→user.id)  │    user.id (text, UUID format)    │
│  │  ├─ accountId            │                                    │
│  │  ├─ providerId           │                                    │
│  │  ├─ password (scrypt)    │                                    │
│  │  └─ timestamps           │                                    │
│  │                           │                                    │
│  │  session                  │                                    │
│  │  ├─ id                   │                                    │
│  │  ├─ userId (FK→user.id)  │                                    │
│  │  ├─ token (unique)       │                                    │
│  │  ├─ expiresAt            │                                    │
│  │  ├─ ipAddress            │                                    │
│  │  └─ userAgent            │                                    │
│  │                           │                                    │
│  │  verification             │                                    │
│  │  ├─ id                   │                                    │
│  │  ├─ identifier           │                                    │
│  │  ├─ value                │                                    │
│  │  └─ expiresAt            │                                    │
│  └───────────────────────────┘                                    │
│                                                                    │
│  Connections:                                                      │
│  ├─ Better Auth: @neondatabase/serverless Pool (WebSocket via ws) │
│  └─ FastAPI: psycopg2 via SQLModel (traditional TCP)              │
└────────────────────────────────────────────────────────────────────┘
```

### Authentication Flow (Actual)

```
1. User submits credentials (email/password) on sign up or sign in form
2. hooks/useAuth.tsx calls authClient.signIn.email() or authClient.signUp.email()
3. Better Auth client sends POST to /api/auth/sign-in/email (or sign-up/email)
4. [..all]/route.ts delegates to Better Auth server via toNextJsHandler(auth)
5. Better Auth validates credentials against `account` table (scrypt hash comparison)
6. Better Auth creates session row in `session` table
7. nextCookies() plugin sets `better-auth.session_token` as HTTP-only cookie
8. Frontend receives success → router.push("/dashboard")
9. On subsequent requests, cookie is sent automatically by browser
10. middleware.ts checks cookie via getSessionCookie() → allow or redirect
11. For task operations: api-client.ts calls authClient.getSession()
12. Extracts user.id → sends as X-User-Id header
13. next.config.ts rewrites /api/v1/* → FastAPI backend
14. FastAPI get_current_user_id() reads X-User-Id header (trusted, no validation)
15. Task routes filter by owner_id = user_id
```

---

## Implementation Sequence (What Actually Happened)

### Phase 1: Dependencies & Environment (Completed)
- Installed `better-auth`, `@neondatabase/serverless`, `ws`
- Configured `.env.local` with `DATABASE_URL`, `BETTER_AUTH_SECRET`, `BETTER_AUTH_URL`
- Note: `postgres` package was NOT needed (originally listed in plan)

### Phase 2: Better Auth Server Configuration (Completed)
- Created `frontend/lib/auth-server.ts` with `betterAuth()` config
- Added `nextCookies()` plugin (discovered during debugging — not in original plan)
- Added `ws` + `neonConfig.webSocketConstructor = ws` (discovered during debugging)
- Created `frontend/app/api/auth/[...all]/route.ts` with `toNextJsHandler(auth)`
- Removed conflicting `[[...auth]]` optional catch-all route

### Phase 3: Frontend Client & Auth Context (Completed)
- Created `frontend/lib/auth-client.ts` with `createAuthClient()`
- Rewrote `frontend/hooks/useAuth.tsx` to use `authClient.useSession()` internally
- Maintained same `AuthProvider`/`useAuth` interface for consuming components
- Updated `SignUpForm.tsx` and `SignInForm.tsx` to use `isSubmitting` from react-hook-form

### Phase 4: Middleware & Route Protection (Completed)
- Rewrote `frontend/middleware.ts` to use `getSessionCookie()` from `better-auth/cookies`
- Protected `/dashboard` path, redirects auth pages if already authenticated
- Excluded `/api/auth` from middleware matcher to avoid blocking Better Auth routes

### Phase 5: Next.js Configuration (Completed)
- Updated `next.config.ts` to ONLY rewrite `/api/v1/*` to FastAPI
- Removed `/api/auth/*` rewrite that was proxying auth requests to FastAPI (root cause of 500 errors)

### Phase 6: FastAPI Backend Updates (Completed)
- Removed JWT middleware import and registration from `main.py`
- CORS already configured for `localhost:3000`
- Task routes already use `get_current_user_id` dependency (X-User-Id header)
- Deleted old `backend/src/api/routes/auth.py` (in earlier feature)

### Phase 7: API Client Integration (Completed)
- Updated `frontend/lib/api-client.ts` to extract user ID from Better Auth session
- Sends `X-User-Id` header with all task API requests
- Uses relative URLs through Next.js rewrite proxy

### Phase 8: Bug Fixes (Completed)
- Added `formatRelativeTime` to `lib/utils.ts` (build error fix)
- Multiple database schema fixes during debugging phase

### Phase 9-10: Polish & Documentation (NOT STARTED)
- Documentation not updated
- Error handling improvements not done
- Security hardening not done
- Dead code not cleaned up

---

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Better Auth in Next.js instead of FastAPI | Better Auth is a Node.js library with no Python port | Creating custom Python auth would be more complex and error-prone |
| Dual database drivers (Pool + psycopg2) | Better Auth requires `@neondatabase/serverless`; FastAPI uses SQLModel/psycopg2 | Using one driver would require rewriting either system |
| `ws` package for WebSocket | `@neondatabase/serverless` Pool needs WebSocket in Node.js | No simpler alternative — this is a runtime requirement |
| `nextCookies()` plugin | Better Auth cannot set cookies in Next.js without it | No alternative — this is how Better Auth works with Next.js |
| Trusted X-User-Id header (no JWT) | MVP time constraint; JWT validation requires additional research | Documented upgrade path to production JWT validation |

---

## Risk Mitigation (Actual Outcomes)

### Risk 1: Database Schema Conflicts — OCCURRED, RESOLVED
- Better Auth auto-created tables but column names conflicted with existing schema
- Resolution: Manual migration scripts fixed column names (createdAt, emailVerified, etc.)

### Risk 2: Better Auth + Neon Integration — OCCURRED, RESOLVED
- `@neondatabase/serverless` Pool requires `ws` package in Node.js
- Resolution: Installed `ws`, configured `neonConfig.webSocketConstructor = ws`

### Risk 3: Cookie Setting in Next.js — OCCURRED, RESOLVED
- Better Auth could NOT set cookies without `nextCookies()` plugin
- This was the root cause of "signup works but no session" bug
- Resolution: Added `plugins: [nextCookies()]` to auth-server.ts config

### Risk 4: Auth Request Routing — OCCURRED, RESOLVED
- `next.config.ts` was proxying `/api/auth/*` to FastAPI, causing 500 errors
- Resolution: Removed auth rewrite, only proxy `/api/v1/*`

### Risk 5: Route Conflicts — OCCURRED, RESOLVED
- `[[...auth]]` optional catch-all conflicted with `[...all]` catch-all
- Resolution: Deleted `[[...auth]]` directory

---

## Architectural Decisions (Actual)

### ADR-1: Cookie-Based Sessions Instead of JWT
- **Decision**: Use Better Auth's cookie-based sessions, not JWTs
- **Rationale**: Better Auth does not generate JWTs for email/password auth. It uses opaque session tokens stored in the database, referenced by HTTP-only cookies
- **Impact**: Constitution references "JWT authentication" but the security outcomes (session management, HTTP-only cookies, XSS prevention) are equivalent
- **Constitution**: Compliant under Hackathon/MVP context — "methods flexible"

### ADR-2: Trusted X-User-Id Header for FastAPI
- **Decision**: Frontend sends user ID as plain X-User-Id header to FastAPI
- **Rationale**: Fastest MVP path. No JWT validation library needed in Python. Constitutional Hackathon context explicitly allows "trusted headers acceptable"
- **Risk**: Header can be spoofed by any HTTP client
- **Upgrade Path**: Implement signed session token validation in FastAPI middleware

### ADR-3: nextCookies() Plugin Required
- **Decision**: Use `nextCookies()` plugin in Better Auth server config
- **Rationale**: Without it, Better Auth cannot set cookies in Next.js server context. This is a framework-specific requirement, not optional
- **Impact**: Hard dependency on `better-auth/next-js`

### ADR-4: Next.js Rewrite Proxy for FastAPI
- **Decision**: Frontend uses relative URLs; Next.js rewrites proxy to FastAPI
- **Rationale**: Avoids CORS issues between browser and FastAPI. All requests go through localhost:3000
- **Impact**: FastAPI is not directly accessible from browser JavaScript

### ADR-5: Auth Client in Separate File
- **Decision**: `lib/auth-client.ts` (client) separate from `lib/auth-server.ts` (server)
- **Rationale**: Better Auth requires server-only imports (Pool, ws) that crash in browser. Separation prevents "server-only module in client" errors

---

## Follow-Up TODOs (Post-MVP)

1. **Security**: Implement signed session token validation in FastAPI (replace X-User-Id trust)
2. **Dead Code**: Remove `backend/src/auth/middleware.py` (102 lines, never used)
3. **Dead Code**: Remove unused functions in `backend/src/auth/dependencies.py` (lines 12-42)
4. **Testing**: Add automated tests per constitution production upgrade path
5. **Rate Limiting**: Add rate limiting on Better Auth endpoints
6. **Email Verification**: Enable Better Auth email verification flow
7. **Constitution**: Amend "JWT authentication" to "session-based authentication with HTTP-only cookies"
8. **Documentation**: Update README with actual architecture diagram
