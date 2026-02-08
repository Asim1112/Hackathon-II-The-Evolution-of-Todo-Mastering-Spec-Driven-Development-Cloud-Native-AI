---
description: "Reconstructed task breakdown for Better Auth integration — reflects actual implementation"
---

# Tasks: Integrate Better Auth with Next.js and FastAPI

**Input**: Design documents from `/specs/015-integrate-better-auth/`
**Prerequisites**: plan.md (reconstructed), spec.md (reconstructed)
**Reconstructed**: 2026-02-08 (Post-implementation reconciliation — code is source of truth)
**Status**: MVP Implementation Complete (Phases 1-8), Polish Pending (Phase 9)

**Tests**: Tests are OPTIONAL per Hackathon/MVP context (constitution v1.1.0). Manual validation was performed during implementation. Automated tests documented as post-MVP upgrade path.

**Organization**: Tasks reflect what was ACTUALLY done, grouped by implementation phase. Status reflects reality: [x] = completed, [ ] = not done, [~] = partially done, [SKIP] = skipped intentionally.

## Format: `[ID] [Status] Description`

---

## Phase 1: Dependencies & Environment Setup

**Purpose**: Install required packages and configure environment variables
**Status**: COMPLETED

- [x] T001 Install `better-auth` package in frontend: `npm install better-auth`
- [x] T002 Install `@neondatabase/serverless` package: `npm install @neondatabase/serverless`
- [x] T003 Install `ws` package for WebSocket support: `npm install ws` *(discovered during debugging — not in original plan)*
- [x] T004 Configure `frontend/.env.local` with `DATABASE_URL` connection string
- [x] T005 Configure `frontend/.env.local` with `BETTER_AUTH_SECRET` (generated secret)
- [x] T006 Configure `frontend/.env.local` with `BETTER_AUTH_URL=http://localhost:3000`
- [x] T007 Configure `frontend/.env.local` with `NEXT_PUBLIC_APP_URL=http://localhost:3000`
- [SKIP] T008 Install `postgres` package — NOT NEEDED (Neon Pool used instead)
- [SKIP] T009 Update `backend/.env` with `BETTER_AUTH_SECRET` — NOT NEEDED (backend doesn't validate tokens)

**Checkpoint**: All dependencies installed, environment configured

---

## Phase 2: Better Auth Server Configuration

**Purpose**: Set up Better Auth server with Neon database and Next.js API route handler
**Status**: COMPLETED

- [x] T010 Create `frontend/lib/auth-server.ts` with `betterAuth()` configuration
- [x] T011 Configure Neon Pool database connection with `@neondatabase/serverless`
- [x] T012 Configure `neonConfig.webSocketConstructor = ws` for Node.js runtime *(discovered during debugging)*
- [x] T013 Enable `emailAndPassword: { enabled: true }` in Better Auth config
- [x] T014 Configure session cookie cache: `session.cookieCache.enabled = true, maxAge = 3600`
- [x] T015 Add `nextCookies()` plugin to Better Auth config: `plugins: [nextCookies()]` *(CRITICAL — discovered during debugging, root cause of "no session" bug)*
- [x] T016 Create directory `frontend/app/api/auth/[...all]/`
- [x] T017 Create `frontend/app/api/auth/[...all]/route.ts` with `toNextJsHandler(auth)`
- [x] T018 Export GET and POST handlers from route.ts
- [x] T019 Delete conflicting `frontend/app/api/auth/[[...auth]]/` directory *(route conflict caused build errors)*
- [x] T020 Verify Better Auth tables auto-created in Neon: `user`, `session`, `account`, `verification`

**Checkpoint**: Better Auth server operational, API routes accessible, database tables created

---

## Phase 3: Frontend Auth Client & Context

**Purpose**: Set up client-side authentication with reactive session state
**Status**: COMPLETED

- [x] T021 Create `frontend/lib/auth-client.ts` with `createAuthClient()`
- [x] T022 Export destructured `{ signIn, signUp, signOut, useSession }` from auth client
- [x] T023 Delete old `frontend/lib/auth.ts` (replaced by auth-client.ts + auth-server.ts)
- [x] T024 Rewrite `frontend/hooks/useAuth.tsx` to use `authClient.useSession()` for reactive session state
- [x] T025 Implement `signIn` callback using `authClient.signIn.email({ email, password, callbackURL: "/dashboard" })`
- [x] T026 Implement `signUp` callback using `authClient.signUp.email({ email, password, name, callbackURL: "/dashboard" })`
- [x] T027 Implement `signOut` callback using `authClient.signOut({ fetchOptions: { onSuccess: () => router.push("/") } })`
- [x] T028 Map `session.isPending` to `isLoading` for backward compatibility with consuming components
- [x] T029 Map `session.data.user` to `User` type `{ userId, email }` for backward compatibility
- [x] T030 Preserve `useRequireAuth()` and `useRedirectIfAuthenticated()` hooks
- [x] T031 Update `SignUpForm.tsx` to use `isSubmitting` from react-hook-form (not `isLoading` from useAuth)
- [x] T032 Update `SignInForm.tsx` to use `isSubmitting` from react-hook-form

**Checkpoint**: Auth client operational, reactive session state working, consuming components unchanged

---

## Phase 4: Middleware & Route Protection

**Purpose**: Protect routes using Better Auth session cookies
**Status**: COMPLETED

- [x] T033 Rewrite `frontend/middleware.ts` to use `getSessionCookie()` from `better-auth/cookies`
- [x] T034 Define protected paths: `["/dashboard"]`
- [x] T035 Define auth paths: `["/auth/signin", "/auth/signup"]`
- [x] T036 Redirect unauthenticated users from protected paths to `/auth/signin` with `?redirect=` param
- [x] T037 Redirect authenticated users from auth paths to `/dashboard`
- [x] T038 Configure middleware matcher to exclude `_next/static`, `_next/image`, `favicon.ico`, `api/auth`, static assets

**Checkpoint**: Route protection working — unauthenticated users redirected, authenticated users bypass auth pages

---

## Phase 5: Next.js Configuration

**Purpose**: Configure Next.js rewrites to proxy task API requests to FastAPI
**Status**: COMPLETED

- [x] T039 Update `next.config.ts` rewrites to ONLY proxy `/api/v1/:path*` to `http://127.0.0.1:8000/api/v1/:path*`
- [x] T040 Remove `/api/auth/:path*` rewrite that was proxying auth requests to FastAPI *(ROOT CAUSE of 500 errors on signup)*

**Checkpoint**: Auth requests handled locally by Next.js, task requests proxied to FastAPI

---

## Phase 6: FastAPI Backend Updates

**Purpose**: Remove old auth middleware, ensure task routes work with X-User-Id header
**Status**: COMPLETED

- [x] T041 Remove JWT middleware import from `backend/src/api/main.py`
- [x] T042 Remove `app.middleware("http")(jwt_middleware)` registration from main.py
- [x] T043 Verify CORS middleware allows `http://localhost:3000` and `http://127.0.0.1:3000` with credentials
- [x] T044 Verify `get_current_user_id` dependency reads `X-User-Id` header from requests
- [x] T045 Verify task routes (GET, POST, PUT, PATCH, DELETE) use `get_current_user_id` dependency
- [x] T046 Verify task routes filter by `owner_id == request_user_id` and return 403 on mismatch
- [SKIP] T047 Delete `backend/src/api/routes/auth.py` — already deleted in earlier feature (pre-015)

**Checkpoint**: FastAPI accepts X-User-Id header, no JWT middleware blocking requests, task isolation enforced

---

## Phase 7: API Client Integration

**Purpose**: Connect frontend task API client to Better Auth session for user identity
**Status**: COMPLETED

- [x] T048 Update `frontend/lib/api-client.ts` to import `authClient` from `./auth-client`
- [x] T049 Add `authClient.getSession()` call in request method to extract user ID
- [x] T050 Send `X-User-Id` header with value `session.data.user.id` on all task requests
- [x] T051 Use relative URLs (`/api/v1/tasks`) instead of absolute URLs (proxied through Next.js rewrites)
- [x] T052 Handle missing session gracefully (try/catch around getSession)

**Checkpoint**: Task API requests include user identity, all requests go through Next.js proxy

---

## Phase 8: Bug Fixes & Build Errors

**Purpose**: Resolve runtime errors discovered during integration testing
**Status**: COMPLETED

- [x] T053 Add `formatRelativeTime` function to `frontend/lib/utils.ts` (build error — referenced but missing)
- [x] T054 Fix database schema: add `emailVerified`, `name`, `image` columns to `user` table
- [x] T055 Fix database schema: rename `created_at` → `createdAt`, `updated_at` → `updatedAt` in `user` table
- [x] T056 Fix database schema: make `password` column nullable in `user` table (Better Auth stores password in `account` table)
- [x] T057 Delete diagnostic scripts: `scripts/diagnose-auth.mjs`, `scripts/fix-user-table.mjs`, `scripts/test-signup.mjs`

**Checkpoint**: Frontend builds and runs without errors, all auth flows operational

---

## Phase 9: Polish & Post-MVP (NOT STARTED)

**Purpose**: Documentation, error handling, security hardening, dead code cleanup
**Status**: PENDING

- [ ] T058 Remove dead code: `backend/src/auth/middleware.py` (102 lines, never imported)
- [ ] T059 Remove dead code: unused functions in `backend/src/auth/dependencies.py` (lines 12-42)
- [ ] T060 Update landing page: remove "JWT authentication" text (uses session cookies)
- [ ] T061 Update README with actual architecture diagram from plan.md
- [ ] T062 Document all environment variables in `.env.example` files
- [ ] T063 Add rate limiting on Better Auth authentication endpoints
- [ ] T064 Enable Better Auth email verification flow
- [ ] T065 Implement signed session token validation in FastAPI (replace trusted X-User-Id header)
- [ ] T066 Add automated tests per constitution production upgrade path
- [ ] T067 Run TypeScript compiler `npx tsc --noEmit` to verify zero type errors
- [ ] T068 Remove any `console.log` debug statements from production code
- [ ] T069 Amend constitution: replace "JWT authentication" with "session-based authentication with HTTP-only cookies"

**Checkpoint**: Production-ready implementation with documentation, security hardening, and clean codebase

---

## Task Summary

| Phase | Description | Tasks | Status |
|-------|-------------|-------|--------|
| 1 | Dependencies & Environment | T001-T009 | COMPLETED (7 done, 2 skipped) |
| 2 | Better Auth Server Config | T010-T020 | COMPLETED (11 done) |
| 3 | Frontend Auth Client & Context | T021-T032 | COMPLETED (12 done) |
| 4 | Middleware & Route Protection | T033-T038 | COMPLETED (6 done) |
| 5 | Next.js Configuration | T039-T040 | COMPLETED (2 done) |
| 6 | FastAPI Backend Updates | T041-T047 | COMPLETED (6 done, 1 skipped) |
| 7 | API Client Integration | T048-T052 | COMPLETED (5 done) |
| 8 | Bug Fixes & Build Errors | T053-T057 | COMPLETED (5 done) |
| 9 | Polish & Post-MVP | T058-T069 | PENDING (0 of 12 done) |

**Total**: 69 tasks (54 completed, 3 skipped, 12 pending)
**MVP Complete**: Phases 1-8 (57 tasks done)
**Remaining**: Phase 9 polish and post-MVP hardening (12 tasks)

---

## Comparison to Original Task List

The original tasks.md had 122 tasks across 8 phases organized by user story. The reconstructed version has 69 tasks across 9 phases organized by implementation sequence. Key differences:

1. **Reduced from 122 to 69 tasks**: Original had many validation/testing sub-tasks that were done informally during debugging, not as discrete tracked tasks
2. **Reorganized by phase, not user story**: Implementation followed a natural sequence (server → client → middleware → config → backend → integration) rather than user-story-first order
3. **Added 13 tasks not in original**: `nextCookies()`, `ws` package, auth-client.ts creation, middleware rewrite, route conflict resolution, etc.
4. **Removed 53 validation tasks**: Granular validation tasks (T032-T041, T046-T052, etc.) were performed as part of debugging, not as discrete tasks
5. **Honest status**: Each task is marked with actual completion status, not aspirational checkboxes

---

## Dependencies & Execution Order

### Actual Dependency Chain
```
Phase 1 (Deps) → Phase 2 (Server) → Phase 3 (Client) → Phase 4 (Middleware)
                                                            ↓
Phase 5 (Next.js Config) → Phase 6 (FastAPI) → Phase 7 (API Client) → Phase 8 (Bug Fixes)
                                                                           ↓
                                                                    Phase 9 (Polish)
```

### Critical Path Items
- T015 (`nextCookies()` plugin) — without this, all auth fails silently
- T040 (remove auth rewrite) — without this, all auth requests 500
- T019 (delete `[[...auth]]`) — without this, build fails
- T049 (`authClient.getSession()` in API client) — without this, tasks 401

---

## Notes

- All tasks were executed through Claude Code agentic workflow (Zero Manual Coding compliant)
- Hackathon/MVP context: manual validation acceptable per constitution v1.1.0
- Phase 9 tasks are documented for post-MVP iteration
- Dead code cleanup (T058-T059) is recommended before demo to avoid confusion
- Constitution amendment (T069) should be done to align "JWT" language with actual cookie-based sessions
