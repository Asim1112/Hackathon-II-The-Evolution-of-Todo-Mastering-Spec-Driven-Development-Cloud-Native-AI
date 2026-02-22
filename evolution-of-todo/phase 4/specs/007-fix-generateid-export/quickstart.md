# Quickstart: Toast ID Generation Setup

## Prerequisites
- Node.js 18+ installed
- npm or yarn package manager
- Existing frontend project with Next.js 16+
- Already installed dependencies (clsx, etc.)

## Setup Steps

### 1. Verify Dependencies
```bash
cd frontend/
npm list clsx
```

### 2. Enhance Utility Module
Update the existing utility file to add the missing `generateId` function:

**File**: `frontend/lib/utils.ts`
```typescript
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function generateId(): string {
  return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
}
```

### 3. Verify Import Statement
Confirm that useToast.tsx imports the function:
```typescript
import { generateId } from "@/lib/utils";
```

### 4. Test Function Usage
The useToast hook should use the function to create unique IDs:
```typescript
const id = generateId();
```

### 5. Run Development Server
```bash
npm run dev
```

The server should start without "Export generateId doesn't exist" errors.

## Verification

After setup:
1. The import `import { generateId } from "@/lib/utils"` should resolve without errors
2. useToast hook should be able to call `generateId()` without errors
3. Toast notifications should receive unique IDs and display properly
4. The development server should start successfully