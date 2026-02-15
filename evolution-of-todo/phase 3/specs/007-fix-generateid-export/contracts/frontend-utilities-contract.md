# Frontend Utilities Contract

## Purpose
Defines the shared utility functions that provide common functionality to frontend components and hooks.

## Utility Functions

### generateId(): string
**Description**: Generates a unique string identifier for toast notifications and other components requiring unique IDs
**Import Path**: `@/lib/utils`
**Parameters**: None
**Return Type**: `string` - Unique identifier string
**Usage**: Used by useToast hook to generate unique IDs for each toast notification

**Example Usage**:
```typescript
// In useToast hook
const id = generateId(); // Returns a unique string like "xyz7abc12def"
```

## Module Interface
- **Export Type**: Named export
- **Function Name**: `generateId`
- **Return Value**: String identifier unique for each call
- **Import Convention**: `import { generateId } from "@/lib/utils"`

## Requirements
- Each call must return a unique identifier
- Function must not require any parameters
- Return value must be a string
- Should work in both client and server environments