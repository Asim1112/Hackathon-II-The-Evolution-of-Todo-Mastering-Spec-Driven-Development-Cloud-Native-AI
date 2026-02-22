# Quickstart: Frontend Utility Module Setup

## Prerequisites
- Node.js 18+ installed
- npm or yarn package manager
- Existing frontend project with Next.js 16+
- clsx dependency (should already be installed per package.json)

## Setup Steps

### 1. Verify Dependencies
```bash
cd frontend/
npm list clsx
```
If clsx is not installed:
```bash
npm install clsx
```

### 2. Create Utility Module
Create the missing utility file with the `cn` function:

**File**: `frontend/lib/utils.ts`
```typescript
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

### 3. Verify Path Alias Configuration
Confirm that tsconfig.json contains the path alias:
```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./*"]
    }
  }
}
```

### 4. Test Component Import
After creating the utility file, UI components should be able to import the cn function:
```typescript
import { cn } from "@/lib/utils";
```

### 5. Run Development Server
```bash
npm run dev
```

The server should start without module resolution errors.

## Verification

After setup:
1. The import `import { cn } from "@/lib/utils"` should resolve without errors
2. UI components like Button.tsx should render properly
3. The development server should start successfully
4. Class name concatenation should work in components