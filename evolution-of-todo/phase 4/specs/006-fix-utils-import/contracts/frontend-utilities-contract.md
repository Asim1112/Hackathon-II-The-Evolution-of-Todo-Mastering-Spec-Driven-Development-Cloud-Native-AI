# Frontend Utilities Contract

## Purpose
Defines the shared utility functions that provide common functionality to frontend UI components.

## Utility Functions

### cn(...inputs: ClassValue[])
**Description**: Concatenates class names conditionally using clsx for conditional logic and tailwind-merge for conflict resolution
**Import Path**: `@/lib/utils`
**Parameters**:
- `...inputs`: Spread of ClassValue types (string, boolean, object, array)
**Return Type**: `string` - Space-separated string of active class names
**Usage**: Used by UI components to conditionally apply CSS classes

**Example Usage**:
```typescript
// In a component
<div className={cn("base-class", condition && "conditional-class", { "object-class": objCondition })}>
  Content
</div>
```

## Module Interface
- **Export Type**: Named export
- **Function Name**: `cn`
- **Dependencies**: `clsx`, `tailwind-merge`
- **Import Convention**: `import { cn } from "@/lib/utils"`

## Compatibility Requirements
- Must work with TypeScript 5.x
- Must be compatible with Next.js 16+
- Should handle various input types (string, boolean, object, array)
- Should properly merge Tailwind CSS classes to avoid conflicts