# Quickstart: Better Auth Client Integration

## Prerequisites
- Node.js 18+ installed
- npm or yarn package manager
- Existing frontend project with Next.js 16+
- Better Auth 1.4.9 already installed (should be in package.json)

## Setup Steps

### 1. Verify Dependencies
```bash
cd frontend/
npm list better-auth
```
Should show better-auth@1.4.9 or similar version

### 2. Identify Correct Better Auth API
Better Auth 1.4.9 provides the following pattern for React integration:

**Option 1: Using createAuthClient**
```typescript
import { createAuthClient } from "better-auth/react";

const authClient = createAuthClient({
  // Configuration options
});
```

### 3. Update Auth Module
Replace the incorrect import in lib/auth.ts with proper Better Auth client initialization:

**File**: `frontend/lib/auth.ts`
```typescript
// Old (incorrect):
// import { signIn, signUp, signOut } from "better-auth/react";

// New (correct):
import { createAuthClient } from "better-auth/react";

const authClient = createAuthClient({
  // Configuration to match backend
});

// Implement signIn, signUp, signOut functions using the client
export async function signIn(email: string, password: string) {
  // Use authClient.signIn method
}

export async function signUp(email: string, password: string) {
  // Use authClient.signUp method
}

export async function signOut() {
  // Use authClient.signOut method
}
```

### 4. Update Hook Integration
Modify useAuth.tsx to use the corrected auth client methods

### 5. Test Authentication Flow
Verify that sign in, sign up, and sign out functionality works properly

## Verification

After setup:
1. The import statements should resolve without "Export signIn doesn't exist" errors
2. Authentication functions (sign in, sign up, sign out) should work properly
3. The development server should start successfully with `npm run dev`
4. Authentication flows should maintain JWT token handling consistent with backend