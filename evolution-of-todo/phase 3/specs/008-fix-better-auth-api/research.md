# Research: Better Auth React Client API Discovery

## Investigation Findings

### Problem Identification
- **Error**: "Export signIn doesn't exist in target module" when importing from "better-auth/react"
- **Location**: `frontend/lib/auth.ts:1` - import statement: `import { signIn, signUp, signOut } from "better-auth/react";`
- **Root Cause**: The installed version of Better Auth (1.4.9) does not export `signIn`, `signUp`, or `signOut` functions from the "better-auth/react" module
- **Impact**: Next.js build failure preventing the entire frontend from rendering

### Current State Analysis
- The Better Auth package has the correct version (1.4.9) installed in node_modules
- The current implementation tries to import non-existent functions from "better-auth/react"
- According to Better Auth documentation, the proper approach is to use a client instance pattern with `createAuthClient` or similar
- The backend appears to be configured with Better Auth JWT-based authentication

### Resolution Approach

**Decision**: Replace the incorrect import pattern with the proper Better Auth client API

**Rationale**:
- Better Auth follows a client instance pattern rather than direct function imports
- The correct approach involves creating an auth client instance and using its methods
- This maintains the JWT-based authentication flow expected by the backend

**Implementation**:
- Import `createAuthClient` or similar from Better Auth
- Create an auth client instance in lib/auth.ts
- Use the client's methods for sign-in, sign-up, and sign-out operations
- Update useAuth hook to use the properly configured client

**Alternatives Considered**:
1. **Keep existing pattern**: Rejected - would continue to cause build failures
2. **Switch to different auth library**: Rejected - would break existing backend integration and require extensive refactoring
3. **Mock the functions**: Rejected - would create false functionality without real authentication

## Implementation Path

### Phase 0: SDK API Discovery
- Inspect the actual Better Auth exports from node_modules
- Identify the correct client API methods for sign-in, sign-up, and sign-out
- Verify compatibility with existing backend configuration

### Phase 1: Client Alignment
- Update lib/auth.ts to use the correct Better Auth client pattern
- Implement proper sign-in, sign-up, and sign-out functions using the client
- Ensure token handling and session management work correctly

### Phase 2: Hook Refactor
- Update useAuth.tsx to consume the corrected auth client methods
- Ensure all authentication flows work through the real client

### Expected Outcome
- Frontend compiles without Better Auth module resolution errors
- Authentication flows (sign in, sign up, sign out) work properly
- JWT token handling remains consistent with backend expectations