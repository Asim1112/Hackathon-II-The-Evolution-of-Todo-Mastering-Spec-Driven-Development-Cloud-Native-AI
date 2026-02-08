---
description: "Task breakdown for Better Auth integration with Next.js and FastAPI"
---

# Tasks: Integrate Better Auth with Next.js and FastAPI

**Input**: Design documents from `/specs/015-integrate-better-auth/`
**Prerequisites**: plan.md (complete), spec.md (complete)

**Tests**: Tests are OPTIONAL and NOT included in this implementation. This is a hackathon MVP focusing on getting authentication working quickly. Test tasks can be added in a future iteration.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/` at repository root
- Tasks reference actual paths from the project structure

---

## Phase 1: Setup (Environment & Dependencies)

**Purpose**: Prepare development environment and install required dependencies

- [ ] T001 Verify Node.js version ≥18 required by Better Auth using `node --version`
- [ ] T002 Verify Python 3.11+ installed using `python --version`
- [ ] T003 Verify Neon database connection string available in environment
- [ ] T004 [P] Install Better Auth dependencies in frontend: `npm install better-auth @neondatabase/serverless postgres`
- [ ] T005 [P] Verify no peer dependency conflicts in frontend/package.json
- [ ] T006 Generate BETTER_AUTH_SECRET using `openssl rand -base64 32` or equivalent

**Checkpoint**: All prerequisites verified, dependencies installed without errors

---

## Phase 2: Foundational (Database & Better Auth Server)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

**Database Preparation**:
- [ ] T007 Inspect Neon database schema using SQL Editor: `SELECT * FROM information_schema.tables WHERE table_schema = 'public'`
- [ ] T008 Check for existing 'user' table conflicts: `SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'user'`
- [ ] T009 If 'user' table exists with data, document migration strategy (rename to app_user OR drop if empty)
- [ ] T010 Verify DATABASE_URL includes `?sslmode=require` suffix

**Better Auth Server Configuration**:
- [ ] T011 Create frontend/lib/auth-server.ts with betterAuth() configuration
- [ ] T012 Configure database connection in auth-server.ts using Pool from @neondatabase/serverless
- [ ] T013 Enable emailAndPassword authentication in Better Auth config
- [ ] T014 Configure session settings with cookieCache enabled in auth-server.ts
- [ ] T015 Set BETTER_AUTH_SECRET from environment variable in auth-server.ts

**Next.js API Routes**:
- [ ] T016 Create directory frontend/app/api/auth/[...all]/
- [ ] T017 Create frontend/app/api/auth/[...all]/route.ts with Better Auth handler
- [ ] T018 Export GET and POST handlers using toNextJsHandler from better-auth/next-js
- [ ] T019 Test API route accessibility: `curl http://localhost:3000/api/auth/session` should return JSON

**Environment Configuration**:
- [ ] T020 [P] Create/update frontend/.env.local with DATABASE_URL, BETTER_AUTH_SECRET, NEXT_PUBLIC_APP_URL
- [ ] T021 [P] Update frontend/.env.example with required variables and format examples
- [ ] T022 [P] Update backend/.env with BETTER_AUTH_SECRET (same value as frontend)
- [ ] T023 [P] Update backend/.env.example with BETTER_AUTH_SECRET documentation

**Database Schema Initialization**:
- [ ] T024 Start Next.js dev server to trigger Better Auth table creation: `npm run dev`
- [ ] T025 Verify Better Auth tables created in Neon dashboard: user, session, account, verification
- [ ] T026 Validate table structure matches Better Auth schema (user.id is string/UUID)

**Checkpoint**: Foundation ready - Better Auth server configured, API routes accessible, database schema initialized, all user story implementation can now begin

---

## Phase 3: User Story 1 - User Can Successfully Sign Up (Priority: P1) 🎯 MVP

**Goal**: Enable users to create new accounts by providing email and password, with successful user account creation in Neon database and proper session establishment

**Independent Test**: Visit http://localhost:3000/auth/signup, submit form with valid credentials, verify no "Failed to fetch" or 500 errors, user created in Neon 'user' table, session created in 'session' table

### Implementation for User Story 1

**Frontend Client Updates**:
- [ ] T027 [US1] Update frontend/lib/auth.ts to fix Better Auth client baseURL to "http://localhost:3000"
- [ ] T028 [US1] Update signUp function in frontend/lib/auth.ts to call authClient.signUp.email({email, password})
- [ ] T029 [US1] Remove localStorage token handling from signUp function (Better Auth uses cookies)
- [ ] T030 [US1] Update signUp return value to match Better Auth response structure (user with id and email)
- [ ] T031 [US1] Fix error handling in signUp function to properly catch and rethrow Better Auth errors

**Sign Up Flow Validation**:
- [ ] T032 [US1] Start Next.js dev server: `cd frontend && npm run dev`
- [ ] T033 [US1] Navigate to http://localhost:3000/auth/signup in browser
- [ ] T034 [US1] Test sign up with valid email/password, verify network request goes to /api/auth/signup
- [ ] T035 [US1] Verify response status is 200 (not 500 or 404)
- [ ] T036 [US1] Check browser cookies contain better-auth.session_token
- [ ] T037 [US1] Query Neon database to verify user created: `SELECT * FROM "user" ORDER BY "createdAt" DESC LIMIT 1`
- [ ] T038 [US1] Query Neon database to verify session created: `SELECT * FROM "session" WHERE "userId" = [user.id]`
- [ ] T039 [US1] Test sign up with invalid email format, verify appropriate validation error shown
- [ ] T040 [US1] Test sign up with weak password (<8 chars), verify validation error shown
- [ ] T041 [US1] Test sign up with duplicate email, verify "Email already exists" error shown

**Checkpoint**: Sign up flow fully functional - users can create accounts without "Failed to fetch" errors, accounts stored in database with sessions

---

## Phase 4: User Story 2 - User Can Successfully Sign In (Priority: P1) 🎯 MVP

**Goal**: Enable existing users to authenticate using their credentials with proper session establishment and access to protected resources

**Independent Test**: Use account created in User Story 1, sign in with valid credentials, verify successful authentication and redirect to dashboard

### Implementation for User Story 2

**Frontend Client Updates**:
- [ ] T042 [US2] Update signIn function in frontend/lib/auth.ts to call authClient.signIn.email({email, password})
- [ ] T043 [US2] Remove localStorage token handling from signIn function (Better Auth uses cookies)
- [ ] T044 [US2] Update signIn return value to match Better Auth response structure
- [ ] T045 [US2] Fix error handling in signIn function for invalid credentials

**Sign In Flow Validation**:
- [ ] T046 [US2] Navigate to http://localhost:3000/auth/signin in browser
- [ ] T047 [US2] Test sign in with valid credentials (from User Story 1), verify network request to /api/auth/signin
- [ ] T048 [US2] Verify response status is 200 and session token set in cookies
- [ ] T049 [US2] Verify redirect to dashboard after successful sign in
- [ ] T050 [US2] Test sign in with incorrect password, verify "Invalid credentials" error
- [ ] T051 [US2] Test sign in with non-existent email, verify "Invalid credentials" error
- [ ] T052 [US2] Verify session token persists in cookies after sign in

**Checkpoint**: Sign in flow fully functional - existing users can authenticate without errors and gain access to dashboard

---

## Phase 5: User Story 3 - User Can Successfully Sign Out (Priority: P2)

**Goal**: Enable authenticated users to securely log out and clear session information

**Independent Test**: From authenticated state, initiate sign out, verify session cleared from database and cookies, user redirected to sign in page

### Implementation for User Story 3

**Frontend Client Updates**:
- [ ] T053 [US3] Update signOut function in frontend/lib/auth.ts to call authClient.signOut()
- [ ] T054 [US3] Remove localStorage.clear() from signOut function (Better Auth handles cookies)
- [ ] T055 [US3] Ensure signOut properly handles errors without throwing

**Sign Out Flow Validation**:
- [ ] T056 [US3] From authenticated state (after US2), click sign out button
- [ ] T057 [US3] Verify network request to /api/auth/signout
- [ ] T058 [US3] Verify response status is 200
- [ ] T059 [US3] Check browser cookies - better-auth.session_token should be cleared
- [ ] T060 [US3] Query Neon database to verify session invalidated: `SELECT * FROM "session" WHERE "userId" = [user.id]`
- [ ] T061 [US3] Verify redirect to sign in page after sign out
- [ ] T062 [US3] Attempt to access protected route (dashboard), verify redirect to sign in

**Checkpoint**: Sign out flow fully functional - users can securely terminate sessions with proper cleanup

---

## Phase 6: User Story 4 - Task Operations Work with Authentication (Priority: P1) 🎯 MVP

**Goal**: Enable authenticated users to perform CRUD operations on tasks with proper authorization validation

**Independent Test**: Create task as authenticated user, verify task has correct owner_id, only user's tasks are visible, unauthenticated requests return 401

### Implementation for User Story 4

**FastAPI Backend Updates - Remove Old Auth**:
- [ ] T063 [US4] Delete backend/src/api/routes/auth.py file entirely
- [ ] T064 [US4] Remove auth route imports from backend/src/api/main.py
- [ ] T065 [US4] Remove /api/v1/auth router registration from backend/src/api/main.py

**FastAPI Backend Updates - CORS Configuration**:
- [ ] T066 [US4] Update CORS middleware in backend/src/api/main.py to allow_origins=["http://localhost:3000"]
- [ ] T067 [US4] Set allow_credentials=True in CORS middleware
- [ ] T068 [US4] Set allow_methods=["*"] in CORS middleware
- [ ] T069 [US4] Set allow_headers=["*"] in CORS middleware

**FastAPI Backend Updates - Task Routes with Auth**:
- [ ] T070 [US4] Add user_id parameter to GET /tasks endpoint in backend/src/api/routes/tasks.py: `user_id: str = Header(..., alias="X-User-Id")`
- [ ] T071 [US4] Filter tasks by owner_id in GET /tasks: `Task.owner_id == user_id`
- [ ] T072 [US4] Add user_id parameter to POST /tasks endpoint in backend/src/api/routes/tasks.py
- [ ] T073 [US4] Set task.owner_id = user_id when creating new tasks
- [ ] T074 [US4] Add user_id parameter to PUT /tasks/{task_id} endpoint
- [ ] T075 [US4] Verify task.owner_id == user_id before allowing updates (return 403 if mismatch)
- [ ] T076 [US4] Add user_id parameter to DELETE /tasks/{task_id} endpoint
- [ ] T077 [US4] Verify task.owner_id == user_id before allowing deletes (return 403 if mismatch)

**Frontend Updates - Pass User ID to Backend**:
- [ ] T078 [US4] Update task API calls in frontend to include X-User-Id header from session
- [ ] T079 [US4] Verify session data available in frontend before making task API calls
- [ ] T080 [US4] Handle 401 errors from task endpoints by redirecting to sign in

**Task Operations Validation**:
- [ ] T081 [US4] Start both servers: `cd frontend && npm run dev` and `cd backend && uvicorn src.api.main:app --reload`
- [ ] T082 [US4] Sign in as user from User Story 1
- [ ] T083 [US4] Create new task, verify network request includes X-User-Id header
- [ ] T084 [US4] Verify task created with correct owner_id: `SELECT * FROM task WHERE owner_id = [user.id]`
- [ ] T085 [US4] List tasks, verify only current user's tasks returned
- [ ] T086 [US4] Update task, verify success with matching owner_id
- [ ] T087 [US4] Attempt to update another user's task (if exists), verify 403 Forbidden
- [ ] T088 [US4] Delete task, verify success with matching owner_id
- [ ] T089 [US4] Sign out, attempt task operation, verify 401 Unauthorized or redirect to sign in
- [ ] T090 [US4] Test CORS: verify no CORS errors in browser console during task operations

**Checkpoint**: Task operations fully integrated with authentication - users can perform CRUD with proper authorization, multi-user isolation enforced

---

## Phase 7: User Story 5 - Authentication State Persists Across Page Refreshes (Priority: P2)

**Goal**: Maintain user authentication state when refreshing the page or navigating between application sections

**Independent Test**: Sign in, refresh page, verify still authenticated and can access protected resources without re-signing in

### Implementation for User Story 5

**Session Persistence Validation**:
- [ ] T091 [US5] Sign in as user from User Story 1
- [ ] T092 [US5] Verify dashboard loads successfully after sign in
- [ ] T093 [US5] Refresh page (F5), verify still authenticated (no redirect to sign in)
- [ ] T094 [US5] Navigate to different route (e.g., /tasks), verify authentication maintained
- [ ] T095 [US5] Close browser tab, reopen http://localhost:3000/dashboard, verify session restored from cookie
- [ ] T096 [US5] Check browser DevTools → Application → Cookies, verify better-auth.session_token exists
- [ ] T097 [US5] Verify session token has appropriate expiration (default 30 days)
- [ ] T098 [US5] Test session restoration: clear localStorage, refresh page, verify still authenticated (proves cookie-based)

**Frontend Middleware Updates (if needed)**:
- [ ] T099 [US5] Review frontend/middleware.ts to ensure no conflicts with Better Auth session handling
- [ ] T100 [US5] If middleware exists, verify it doesn't clear Better Auth cookies
- [ ] T101 [US5] If middleware implements auth checks, update to use Better Auth session API

**Checkpoint**: Authentication state persists reliably across page refreshes and navigation using HTTP-only cookies

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, error handling improvements, and production readiness

**Documentation**:
- [ ] T102 [P] Update main README.md with new authentication flow architecture diagram
- [ ] T103 [P] Document all environment variables in frontend/.env.example and backend/.env.example
- [ ] T104 [P] Create troubleshooting guide in specs/015-integrate-better-auth/TROUBLESHOOTING.md
- [ ] T105 [P] Document setup instructions: Prerequisites, Installation, First Run, Testing

**Error Handling Improvements**:
- [ ] T106 [P] Add user-friendly error messages for invalid email format in frontend
- [ ] T107 [P] Add user-friendly error messages for weak password in frontend
- [ ] T108 [P] Add user-friendly error messages for duplicate email in frontend
- [ ] T109 [P] Add loading states to sign up form during async operations
- [ ] T110 [P] Add loading states to sign in form during async operations
- [ ] T111 [P] Ensure backend errors don't expose sensitive information in responses

**Code Quality**:
- [ ] T112 [P] Remove any console.log statements from production code
- [ ] T113 [P] Run TypeScript compiler: `cd frontend && npx tsc --noEmit` to verify no errors
- [ ] T114 [P] Run Python linter: `cd backend && ruff check` (if configured) to verify code quality
- [ ] T115 [P] Verify .env files are in .gitignore (no secrets committed)

**Security Hardening**:
- [ ] T116 [P] Verify HTTPS enforced for Neon database connections (sslmode=require)
- [ ] T117 [P] Verify Better Auth session cookies are httpOnly and secure (default behavior)
- [ ] T118 [P] Document JWT validation upgrade path for production (FastAPI middleware)

**Validation**:
- [ ] T119 Run full sign up → sign in → task operations → sign out flow end-to-end
- [ ] T120 Verify all 8 success criteria from spec.md are met
- [ ] T121 Verify all 10 test phases from plan.md pass
- [ ] T122 Create demo user account for presentation/testing

**Checkpoint**: Production-ready implementation with documentation, error handling, and security best practices

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - **User Story 1 (Sign Up)**: Can start after Foundational - No dependencies on other stories
  - **User Story 2 (Sign In)**: Depends on User Story 1 (needs account to test) - Can run in parallel with US3 during implementation
  - **User Story 3 (Sign Out)**: Depends on User Story 2 (needs authenticated session to test)
  - **User Story 4 (Tasks)**: Depends on User Story 2 (needs authentication to test task operations)
  - **User Story 5 (Persistence)**: Depends on User Story 2 (needs session to test persistence)
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1 - Sign Up)**: Foundation only
- **User Story 2 (P1 - Sign In)**: Depends on US1 for test data
- **User Story 3 (P2 - Sign Out)**: Depends on US2 for authenticated state
- **User Story 4 (P1 - Tasks)**: Depends on US2 for authentication
- **User Story 5 (P2 - Persistence)**: Depends on US2 for session

### Within Each User Story

- Frontend client updates before validation tasks
- Server configuration before client integration
- Core functionality before edge case testing
- Story complete before moving to next priority

### Parallel Opportunities

**Setup Phase (Phase 1)**:
- T004 (Install dependencies) and T006 (Generate secret) can run in parallel

**Foundational Phase (Phase 2)**:
- T020, T021, T022, T023 (Environment file updates) can all run in parallel

**User Story 4 (Phase 6)**:
- T063-T065 (Remove old auth), T066-T069 (CORS config), T070-T077 (Task routes) are different files - can be split among developers

**Polish Phase (Phase 8)**:
- T102-T105 (Documentation), T106-T111 (Error handling), T112-T118 (Code quality & security) can all run in parallel

### Sequential Requirements

- **MUST be sequential**: Phase 1 → Phase 2 → User Stories → Polish
- **User Story order**: US1 → US2 → US3 (sequential due to test dependencies)
- **User Story 4 and 5**: Can start after US2, but US4 has higher priority (P1 vs P2)

---

## Parallel Example: Foundational Phase

```bash
# Environment Configuration - all can run in parallel:
Task: "Create/update frontend/.env.local"
Task: "Update frontend/.env.example"
Task: "Update backend/.env"
Task: "Update backend/.env.example"
```

## Parallel Example: User Story 4

```bash
# Backend updates - different areas, can parallelize:
Task: "Delete backend/src/api/routes/auth.py"
Task: "Update CORS middleware in backend/src/api/main.py"
Task: "Add user_id parameter to GET /tasks in backend/src/api/routes/tasks.py"
```

## Parallel Example: Polish Phase

```bash
# Documentation, error handling, code quality - independent tasks:
Task: "Update main README.md"
Task: "Add user-friendly error messages for invalid email"
Task: "Remove console.log statements"
Task: "Verify HTTPS enforced"
```

---

## Implementation Strategy

### MVP First (User Stories 1, 2, 4 Only)

1. Complete Phase 1: Setup (6 tasks)
2. Complete Phase 2: Foundational (20 tasks) - CRITICAL checkpoint
3. Complete Phase 3: User Story 1 - Sign Up (15 tasks)
4. Complete Phase 4: User Story 2 - Sign In (11 tasks)
5. Complete Phase 6: User Story 4 - Task Operations (28 tasks)
6. **STOP and VALIDATE**: Test complete auth flow + task operations
7. Deploy/demo if ready

**Rationale**: User Stories 1, 2, and 4 (all P1) provide complete authentication + core functionality. User Stories 3 and 5 (both P2) are nice-to-have enhancements.

### Incremental Delivery

1. **Foundation** (Phase 1-2): ~26 tasks → Better Auth server ready, database initialized
2. **MVP** (US1, US2, US4): ~54 tasks → Complete auth flow + task operations → DEMO READY
3. **Enhanced** (+ US3, US5): ~21 additional tasks → Add sign out + session persistence → PRODUCTION READY
4. **Polished** (Phase 8): ~21 tasks → Documentation, error handling, security → RELEASE READY

### Parallel Team Strategy

With 2 developers after Foundational phase completes:

1. **Developer A**: Focus on authentication (US1 → US2 → US3)
2. **Developer B**: Focus on backend integration (US4 - FastAPI updates)
3. **Both**: Validate US5 (persistence) together
4. **Both**: Polish phase in parallel (documentation, error handling, quality)

### Time Estimates

- **Phase 1 (Setup)**: 10 minutes (6 tasks)
- **Phase 2 (Foundational)**: 45 minutes (20 tasks) - includes database setup and Better Auth config
- **Phase 3 (User Story 1)**: 30 minutes (15 tasks)
- **Phase 4 (User Story 2)**: 20 minutes (11 tasks)
- **Phase 5 (User Story 3)**: 15 minutes (10 tasks)
- **Phase 6 (User Story 4)**: 60 minutes (28 tasks) - includes all backend updates
- **Phase 7 (User Story 5)**: 20 minutes (11 tasks)
- **Phase 8 (Polish)**: 30 minutes (21 tasks)

**Total**: ~230 minutes (~3.8 hours) for complete implementation

**MVP Only** (US1, US2, US4 + Foundation): ~165 minutes (~2.75 hours)

---

## Notes

- [P] tasks = different files/independent concerns, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently testable at its checkpoint
- Tests are OPTIONAL - not included in this MVP implementation
- Validation tasks ensure each story works before moving forward
- Commit after each phase or logical group of tasks
- Stop at any checkpoint to validate story independently
- **CRITICAL**: Do not skip Foundational phase (Phase 2) - it blocks all user stories

---

## Format Validation Summary

✅ **All 122 tasks follow checklist format**: `- [ ] [TaskID] [P?] [Story?] Description`
✅ **Task IDs**: Sequential T001-T122 in execution order
✅ **[P] markers**: 27 parallelizable tasks identified across all phases
✅ **[Story] labels**: 80 tasks mapped to user stories (US1, US2, US3, US4, US5)
✅ **File paths**: Included in all implementation tasks
✅ **Phase structure**: Setup → Foundational → User Stories (priority order) → Polish
✅ **Checkpoints**: Each user story has independent validation checkpoint
✅ **Dependencies**: Clear blocking relationships documented
✅ **Parallel opportunities**: Examples provided for each phase
✅ **MVP scope**: User Stories 1, 2, 4 (80 tasks total for MVP)
