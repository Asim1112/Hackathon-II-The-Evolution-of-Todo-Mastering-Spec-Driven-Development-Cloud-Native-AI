# Quickstart: Email Validation Utility Implementation

## Prerequisites
- Node.js 18+ installed
- npm or yarn package manager
- TypeScript development environment
- Existing frontend project with Next.js 16+

## Setup Steps

### 1. Verify Current State
```bash
cd frontend/
ls -la lib/utils.ts
```

### 2. Add Email Validation Function
**File**: `frontend/lib/utils.ts`
```typescript
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

// Existing utilities
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function generateId(): string {
  return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
}

// New email validation utility
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/;
  return emailRegex.test(email);
}
```

### 3. Verify Import in Auth Forms
**Files**: `components/auth/SignInForm.tsx`, `components/auth/SignUpForm.tsx`
```typescript
import { isValidEmail } from "@/lib/utils";
```

### 4. Test Email Validation
Verify that the auth forms can now import and use the validation function:
```typescript
const isEmailValid = isValidEmail("user@example.com"); // Should return true
const isInvalid = isValidEmail("invalid-email");       // Should return false
```

### 5. Run Development Server
```bash
npm run dev
```

The authentication pages should now load successfully without module resolution errors.

## Verification

After implementation:
1. The import `import { isValidEmail } from "@/lib/utils"` should resolve without errors
2. Authentication forms should be able to call `isValidEmail()` function
3. Email validation should work correctly with proper validation logic
4. Development server should start without "Export isValidEmail doesn't exist" errors