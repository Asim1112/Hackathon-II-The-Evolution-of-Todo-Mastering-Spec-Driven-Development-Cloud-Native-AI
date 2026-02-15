# Tasks: Fix Better Auth React Client API Mismatch

**Feature**: Fix Better Auth React Client API Mismatch
**Branch**: `008-fix-better-auth-api`
**Created**: 2026-02-05
**Input**: Feature specification from `/specs/008-fix-better-auth-api/spec.md`

## Implementation Strategy

The implementation will address the Better Auth React API mismatch by discovering the correct API exports and updating the frontend authentication integration. We'll follow an incremental approach, starting with SDK API discovery, then updating the auth module, followed by updating the auth hook, and finally validating the complete integration.

**MVP Goal**: User Story 1 - Frontend runs successfully without Better Auth module resolution errors

## Dependencies Between User Stories

- US1 (P1) → US2 (P2): Successful frontend startup enables proper authentication functionality
- US1 (P1) → US3 (P3): Working development server enables build system validation

## Parallel Execution Examples

- SDK API discovery can run in parallel with checking current auth.ts implementation
- Updating lib/auth.ts can run in parallel with planning useAuth.tsx updates

## Phase 1: Setup

**Goal**: Prepare environment and verify Better Auth SDK installation

- [x] T001 Verify Better Auth SDK installation in node_modules with version 1.4.9
- [x] T002 Check current auth.ts implementation and identify incorrect import statements

## Phase 2: Foundational Tasks

**Goal**: Discover correct Better Auth API exports and prepare integration

- [x] T003 Identify the actual Better Auth React exports provided by the installed SDK (createAuthClient, useStore, or equivalent)
- [x] T004 Research Better Auth client instance pattern for authentication methods
- [x] T005 Document the correct API integration approach for signIn, signUp, and signOut functionality

## Phase 3: [US1] Developer Runs Frontend Successfully

**Goal**: Ensure frontend compiles and runs without Better Auth module resolution errors

**Independent Test Criteria**: The frontend server can be started successfully and the UI renders without Better Auth module resolution errors, proving the correct API is being used.

- [x] T006 [US1] Update lib/auth.ts to replace invalid imports with correct Better Auth API
- [x] T007 [US1] Initialize proper Better Auth client instance in lib/auth.ts
- [x] T008 [US1] Implement signIn, signUp, and signOut functions using correct client methods
- [x] T009 [US1] Verify frontend compiles without "Export signIn doesn't exist in target module" errors

## Phase 4: [US2] Authentication Functions Work Properly

**Goal**: Verify authentication system properly uses the correct Better Auth client API

**Independent Test Criteria**: Individual authentication functions (sign in, sign up, sign out) can be triggered and complete without API-related errors.

- [x] T010 [US2] Update hooks/useAuth.tsx to call the correct Better Auth client methods
- [x] T011 [US2] Ensure login, signup, and logout flows are wired through the real client
- [x] T012 [US2] Test that authentication flows work properly using the corrected API
- [x] T013 [US2] Confirm JWT token handling remains consistent with backend expectations

## Phase 5: [US3] Module Integrity Maintained

**Goal**: Ensure build system compiles application successfully

**Independent Test Criteria**: The application can be built successfully using `npm run build` without Better Auth module resolution errors.

- [x] T014 [US3] Run production build to verify Better Auth module resolution works in build process
- [x] T015 [US3] Test that all Better Auth import statements resolve correctly during build
- [x] T016 [US3] Verify built application functions properly with authentication
- [x] T017 [US3] Confirm build completes without Better Auth module resolution failures

## Final Phase: Polish & Cross-Cutting Concerns

**Goal**: Final verification and cleanup

- [x] T018 Perform full application test to confirm all authentication functionality works
- [x] T019 Verify development server starts within 30 seconds as specified
- [x] T020 Clean up any temporary files or test installations
- [x] T021 Update documentation with the corrected Better Auth integration details