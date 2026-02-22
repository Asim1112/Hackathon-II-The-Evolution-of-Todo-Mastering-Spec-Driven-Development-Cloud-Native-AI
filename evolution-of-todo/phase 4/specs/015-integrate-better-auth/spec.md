# Feature Specification: Integrate Better Auth with Next.js and FastAPI

**Feature Branch**: `015-integrate-better-auth`
**Created**: 2026-02-06
**Reconstructed**: 2026-02-08 (Post-implementation reconciliation — code is source of truth)
**Status**: Implemented (MVP)
**Context**: Hackathon/MVP (per constitution v1.1.0 context-specific implementation)

**Input**: User description: "Integrate Better Auth with Next.js frontend and FastAPI backend for hackathon Todo app - Fix authentication errors by implementing Better Auth with Next.js API routes while maintaining FastAPI for tasks CRUD. User can successfully sign up and sign in without 'Failed to fetch' or 500 errors. Better Auth manages authentication via Next.js API routes (/api/auth/*). Better Auth stores user sessions in Neon PostgreSQL database. FastAPI backend handles only tasks CRUD operations (/api/v1/tasks/*). Both Next.js and FastAPI share the same Neon database. Authentication state persists across page refreshes. User can log out successfully."

**Reconstruction Note**: This spec has been reconstructed from the working codebase after emergency vibe-coding during implementation. All claims below are verified against running code. See `drift-report.md` for the full forensic analysis.

## Architecture Summary (Actual)

Better Auth runs as a **cookie-based session authentication** library inside Next.js API routes. It does NOT use JWTs. Sessions are stored as database rows in the `session` table. Authentication cookies (`better-auth.session_token`) are HTTP-only and set via the `nextCookies()` plugin. FastAPI receives user identity through a trusted `X-User-Id` header sent by the frontend JavaScript client, which extracts the user ID from the Better Auth session. This is an MVP approach — production would require cryptographic token validation.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - User Can Successfully Sign Up (Priority: P1)

A user visits the application and creates a new account by providing email, password, and name. Better Auth processes the signup through its `/api/auth/sign-up/email` endpoint, creates a user record, hashes the password (scrypt) in the `account` table, creates a session, and sets HTTP-only cookies.

**Why this priority**: Critical for user acquisition. Without signup, the application cannot be used.

**Independent Test**: Navigate to `/auth/signup`, submit form with valid email/password, verify: no errors, user row in `user` table, account row in `account` table with hashed password, session row in `session` table, `better-auth.session_token` cookie set, redirect to `/dashboard`.

**Acceptance Scenarios**:

1. **Given** a user is on the sign up page with valid credentials, **When** the user submits the form, **Then** Better Auth creates a `user` record, an `account` record with scrypt-hashed password, a `session` record, sets the `better-auth.session_token` HTTP-only cookie via `nextCookies()` plugin, and the frontend redirects to `/dashboard`

2. **Given** a user provides a duplicate email, **When** the user submits the form, **Then** Better Auth returns an error and no duplicate user is created

---
### User Story 2 - User Can Successfully Sign In (Priority: P1)

An existing user authenticates using their credentials. Better Auth validates the password against the scrypt hash in the `account` table, creates a new session, and sets cookies.

**Why this priority**: Critical for returning users to access their data.

**Independent Test**: Use an existing account, sign in at `/auth/signin`, verify: successful authentication, session cookie set, redirect to `/dashboard`.

**Acceptance Scenarios**:

1. **Given** a user is on the sign in page with valid credentials, **When** the user submits the form, **Then** Better Auth validates credentials against the `account` table, creates a session in the `session` table, sets the `better-auth.session_token` cookie, and the frontend redirects to `/dashboard`

2. **Given** a user provides invalid credentials, **When** the user submits the form, **Then** Better Auth returns an authentication error without creating a session

---
### User Story 3 - User Can Successfully Sign Out (Priority: P2)

An authenticated user signs out, clearing their session from the database and removing authentication cookies.

**Why this priority**: Important for security on shared devices.

**Independent Test**: From authenticated state, click sign out, verify: session cleared from `session` table, cookies removed, redirect to `/`.

**Acceptance Scenarios**:

1. **Given** an authenticated user on any page, **When** the user initiates sign out, **Then** Better Auth invalidates the session in the database, clears the `better-auth.session_token` cookie, and the frontend redirects to `/`

---
### User Story 4 - Task Operations Work with Authentication (Priority: P1)

An authenticated user performs CRUD operations on tasks. The frontend extracts the user ID from the Better Auth session and sends it as an `X-User-Id` header to the FastAPI backend (via Next.js rewrite proxy). FastAPI filters tasks by `owner_id` matching the header value.

**Why this priority**: Core functionality — the app is a todo list. Tasks must work with authentication.

**Independent Test**: As authenticated user, create/read/update/delete tasks, verify: `X-User-Id` header sent, tasks filtered by owner, other users' tasks not accessible.

**Acceptance Scenarios**:

1. **Given** an authenticated user, **When** the user performs task operations, **Then** the frontend API client extracts `user.id` from `authClient.getSession()`, sends it as `X-User-Id` header, and FastAPI processes the request filtering by `owner_id`

2. **Given** an unauthenticated user, **When** the user attempts task operations, **Then** the middleware redirects to `/auth/signin` (no API call reaches FastAPI)

3. **Given** an authenticated user, **When** the user attempts to access another user's task, **Then** FastAPI returns 403 Forbidden

---
### User Story 5 - Authentication State Persists Across Page Refreshes (Priority: P2)

An authenticated user refreshes the page or navigates between sections. The `better-auth.session_token` cookie persists across requests. The Next.js middleware checks for the cookie using `getSessionCookie()`. The React hook `authClient.useSession()` provides reactive session state.

**Why this priority**: Essential for usable UX — users should not need to re-login on every page load.

**Independent Test**: Sign in, refresh page, verify: still authenticated, dashboard loads, tasks visible, no redirect to sign in.

**Acceptance Scenarios**:

1. **Given** an authenticated user, **When** the user refreshes the page, **Then** the `better-auth.session_token` cookie is sent with the request, middleware allows access, and `authClient.useSession()` returns the active session

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST handle user sign up requests without returning "Failed to fetch" or 500 errors — **IMPLEMENTED** via Better Auth catch-all route at `/api/auth/[...all]/route.ts`
- **FR-002**: System MUST process user sign in requests without returning "Failed to fetch" or 500 errors — **IMPLEMENTED** via Better Auth `signIn.email()` method
- **FR-003**: System MUST store user sessions in Neon PostgreSQL database via Better Auth — **IMPLEMENTED** via `session` table with Neon Pool connection
- **FR-004**: System MUST route authentication requests through Next.js API routes at `/api/auth/*` — **IMPLEMENTED** via `[...all]/route.ts` catch-all with `toNextJsHandler(auth)`
- **FR-005**: System MUST maintain user authentication state across page refreshes — **IMPLEMENTED** via HTTP-only `better-auth.session_token` cookie and `authClient.useSession()` hook
- **FR-006**: System MUST handle user sign out requests and clear session cookies — **IMPLEMENTED** via `authClient.signOut()` with `fetchOptions.onSuccess` redirect
- **FR-007**: System MUST identify users for FastAPI task endpoints via `X-User-Id` header — **IMPLEMENTED** as MVP trusted header approach (no cryptographic validation)
- **FR-008**: System MUST allow authenticated users to perform CRUD operations on tasks — **IMPLEMENTED** via task routes with `get_current_user_id` dependency
- **FR-009**: System MUST protect routes using `getSessionCookie()` in Next.js middleware — **IMPLEMENTED** in `middleware.ts` with `/dashboard` protection
- **FR-010**: System MUST share Neon database between Next.js (auth tables) and FastAPI (task table) — **IMPLEMENTED** via `@neondatabase/serverless` Pool (frontend) and psycopg2/SQLModel (backend)
- **FR-011**: System MUST configure CORS to allow frontend-backend communication — **IMPLEMENTED** in FastAPI with `allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"]`
- **FR-012**: System MUST proxy task API requests from frontend to FastAPI via Next.js rewrites — **IMPLEMENTED** in `next.config.ts` rewriting `/api/v1/:path*` to `http://127.0.0.1:8000/api/v1/:path*`

### Non-Functional Requirements (MVP Context)

- **NFR-001**: Authentication mechanism is cookie-based sessions (NOT JWT) per Better Auth library design
- **NFR-002**: Password hashing uses scrypt algorithm (Better Auth default) stored in `account` table
- **NFR-003**: User-to-FastAPI identity bridge uses trusted `X-User-Id` header (MVP; production requires signed tokens)
- **NFR-004**: `nextCookies()` plugin is REQUIRED for Better Auth to set cookies in Next.js server context
- **NFR-005**: `ws` package is REQUIRED for `@neondatabase/serverless` Pool in Node.js runtime

### Key Entities

- **User** (`user` table): id (text PK), email, name, createdAt, updatedAt, emailVerified, image — created by Better Auth
- **Account** (`account` table): id, userId (FK→user), accountId, providerId ("credential"), password (scrypt hash) — stores auth credentials
- **Session** (`session` table): id, userId (FK→user), token (unique), expiresAt, ipAddress, userAgent — active sessions
- **Verification** (`verification` table): id, identifier, value, expiresAt — email verification tokens
- **Task** (`task` table): id (int PK), title, description, is_completed, owner_id (references user.id), created_at, updated_at — managed by FastAPI/SQLModel

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Sign up requests complete successfully without "Failed to fetch" or 500 errors — **MET**
- **SC-002**: Sign in requests complete successfully without "Failed to fetch" or 500 errors — **MET**
- **SC-003**: Authentication state persists across page refreshes via session cookies — **MET**
- **SC-004**: Sign out clears session from database and removes cookies — **MET**
- **SC-005**: Authenticated users can perform task CRUD with owner-based isolation — **MET**
- **SC-006**: Unauthenticated users are redirected to sign in via middleware — **MET**
- **SC-007**: Better Auth creates user accounts in Neon PostgreSQL `user` and `account` tables — **MET**
- **SC-008**: Frontend and backend communicate via Next.js rewrite proxy with CORS — **MET**

### Known MVP Limitations (Post-MVP Upgrade Path)

- **LIM-001**: FastAPI trusts `X-User-Id` header without cryptographic validation — upgrade to signed session tokens
- **LIM-002**: No rate limiting on authentication endpoints — add rate limiting middleware
- **LIM-003**: No email verification flow enabled — enable Better Auth email verification
- **LIM-004**: Dead code exists in backend (`middleware.py`, unused dependency functions) — clean up
- **LIM-005**: No automated tests — add per constitution production upgrade path
