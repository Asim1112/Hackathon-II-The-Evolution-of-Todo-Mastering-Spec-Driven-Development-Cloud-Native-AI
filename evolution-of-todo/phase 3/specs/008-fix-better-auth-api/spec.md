# Feature Specification: Fix Better Auth React Client API Mismatch

**Feature Branch**: `008-fix-better-auth-api`
**Created**: 2026-02-05
**Status**: Draft
**Input**: User description: "BUG SPECIFICATION: Better Auth React Client API Mismatch — signIn / signUp / signOut Not Exported

- Error:
Export signIn doesn't exist in target module

The following import fails:

  import { signIn, signUp, signOut } from "better-auth/react"

Next.js error:
The export signIn was not found in module:
node_modules/better-auth/dist/client/react/index.mjs

- Location:
frontend/lib/auth.ts:1

(imported via hooks/useAuth.tsx → components/Header.tsx → app/layout.tsx)

- Root Cause:
The installed version of `better-auth` does NOT export `signIn`, `signUp`, or `signOut` from `better-auth/react`.

Claude CLI generated frontend authentication code that assumes a React API that does not exist in the currently installed Better-Auth SDK.

Instead, the SDK exposes a store-based or client-instance API (e.g. `useStore`, `createAuthClient`, or similar), not direct auth functions.

This creates a **hard API mismatch** between:
- The generated frontend auth integration
- The actual Better-Auth package version in node_modules

Because the named exports do not exist, Next.js fails during static module resolution and the entire frontend crashes.

- Expected Behavior:
The frontend should be able to import valid Better-Auth APIs, initialize the auth client, and allow login, signup, and logout without build-time errors.

The application should render successfully on:
http://localhost:3000

- Solution Approach:
Align the frontend auth integration with the real Better-Auth React API:

- Identify the correct Better-Auth React exports provided by the installed SDK (e.g. `createAuthClient`, `useStore`, or equivalent).
- Replace `signIn`, `signUp`, and `signOut` imports with the correct API.
- Update `lib/auth.ts` and `useAuth.tsx` to call the proper Better-Auth client methods instead of non-existent functions.
- Ensure the frontend uses the same auth flow expected by the Better-Auth backend integration."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Developer Runs Frontend Successfully (Priority: P1)

Developer runs `npm run dev` in the frontend directory and the Next.js development server starts without build errors, becoming available at http://localhost:3000. The application renders properly without showing module resolution errors related to Better Auth API mismatches.

**Why this priority**: This is critical as the entire frontend is currently non-functional due to the Better Auth API mismatch. Without fixing this, developers cannot work on the application and users cannot access the UI.

**Independent Test**: The frontend server can be started successfully and the UI renders without Better Auth module resolution errors, proving the correct API is being used.

**Acceptance Scenarios**:

1. **Given** a fresh development environment with all other dependencies installed, **When** the developer runs `npm run dev`, **Then** the server starts without "Export signIn doesn't exist in target module" errors and becomes available at http://localhost:3000

2. **Given** the mismatched Better Auth React API, **When** the frontend tries to import auth functions from "better-auth/react", **Then** the imports succeed without errors

---

### User Story 2 - Authentication Functions Work Properly (Priority: P2)

The authentication system in the application works correctly, with login, signup, and logout functionality working properly using the correct Better Auth client API that matches the installed SDK version.

**Why this priority**: Essential for user authentication functionality to work properly. Without proper authentication, users cannot access protected features.

**Independent Test**: Individual authentication functions (sign in, sign up, sign out) can be triggered and complete without API-related errors.

**Acceptance Scenarios**:

1. **Given** the frontend with properly configured Better Auth API, **When** users trigger authentication flows, **Then** login, signup, and logout work correctly using the real Better Auth SDK

---

### User Story 3 - Module Integrity Maintained (Priority: P3)

The Next.js build system can compile the application successfully, with all Better Auth utility functions properly imported from the correct API endpoints, ensuring consistent behavior between development and production environments.

**Why this priority**: Important for deployment and ensuring no other components face similar import issues.

**Independent Test**: The application can be built successfully using `npm run build` without Better Auth module resolution errors.

**Acceptance Scenarios**:

1. **Given** a configured Better Auth module with all necessary exports, **When** the build process runs, **Then** all modules resolve correctly and the build completes successfully

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST identify the correct Better Auth React exports provided by the installed SDK (e.g., `createAuthClient`, `useStore`, or equivalent)
- **FR-002**: System MUST replace `signIn`, `signUp`, and `signOut` imports with the correct Better Auth API
- **FR-003**: lib/auth.ts MUST use proper Better Auth client methods instead of non-existent functions
- **FR-004**: useAuth.tsx MUST call the correct Better Auth client methods
- **FR-005**: Frontend application MUST compile and run without Better Auth module resolution errors
- **FR-006**: Build system MUST resolve Better Auth imports during compilation without errors
- **FR-007**: Authentication flows MUST work properly with the corrected API integration

### Key Entities

- **Better Auth Client**: The properly configured Better Auth client that matches the installed SDK version
- **Authentication System**: The authentication flows (login, signup, logout) that consume the Better Auth client
- **Frontend Integration**: The React components and hooks that interface with the Better Auth client

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Frontend application compiles successfully 100% of the time without "Export signIn doesn't exist in target module" errors
- **SC-002**: Authentication functions work without import-related errors during development
- **SC-003**: Build process completes successfully with no Better Auth module resolution failures
- **SC-004**: Development server starts within 30 seconds of running `npm run dev`
- **SC-005**: Users can successfully sign in, sign up, and sign out using the corrected Better Auth integration