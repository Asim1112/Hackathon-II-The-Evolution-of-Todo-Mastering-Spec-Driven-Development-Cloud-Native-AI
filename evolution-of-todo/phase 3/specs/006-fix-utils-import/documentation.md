# Frontend Utility Module Documentation

## Issue
The Next.js frontend was failing to build due to a "Module not found: Can't resolve '@/lib/utils'" error.

## Solution
Created the missing `frontend/lib/utils.ts` file with the `cn` utility function.

## Implementation Details

### File Created
- **Location**: `frontend/lib/utils.ts`
- **Function**: `cn(...inputs: ClassValue[])`
- **Purpose**: Class name concatenation with conditional logic using `clsx` and Tailwind CSS class merging with `tailwind-merge`

### Dependencies Added
- `tailwind-merge`: Added to package.json to properly merge Tailwind CSS classes and prevent conflicts

### Function Implementation
```typescript
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

## Impact
- Resolves the "Module not found" error in UI components (Button.tsx, etc.)
- Enables proper conditional class name handling in UI components
- Prevents Tailwind CSS class conflicts through proper merging
- Allows the frontend to build and run successfully

## Components Affected
- Button component (components/ui/Button.tsx) - primary consumer
- Header component (components/Header.tsx) - indirectly uses Button which uses cn