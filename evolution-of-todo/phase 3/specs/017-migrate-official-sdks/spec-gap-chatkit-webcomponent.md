# Spec Gap Analysis: ChatKit Web Component Missing

**Date**: 2026-02-11
**Issue**: Critical implementation gap in FR-014
**Status**: Blocking

## Problem Statement

The current spec (FR-014) states:
> "Frontend MUST use ChatKit React component with apiUrl pointing to /chatkit endpoint"

**Implementation attempted**:
```typescript
import { useChatKit, ChatKit } from "@openai/chatkit-react";
```

**Result**: Component does not render, no API calls made.

## Root Cause

**Three-tier architecture discovered**:

1. **@openai/chatkit** (installed ✅)
   - TypeScript type definitions only
   - No implementation code
   - Purpose: Type safety for the web component

2. **@openai/chatkit-react** (installed ✅)
   - React hooks and JSX wrappers
   - Wraps the `<openai-chatkit />` custom element
   - Purpose: React-friendly API

3. **ChatKit Web Component** (NOT installed ❌)
   - The actual `<openai-chatkit />` custom element implementation
   - Handles rendering, API communication, streaming
   - **MISSING FROM OUR INSTALLATION**

## Spec Violation

**FR-014 is incomplete**. It specifies using the React component but does not specify:
- How to load the underlying web component
- What package contains the web component
- Whether it's loaded via CDN, npm, or other method

**Current spec says**:
```bash
npm install @openai/chatkit-react
```

**Missing requirement**:
```bash
# Unknown - need to determine correct method
npm install <chatkit-webcomponent-package>
# OR
<script src="https://cdn.../chatkit.js"></script>
```

## Investigation Needed

**Questions to answer**:
1. What is the package name for the ChatKit web component?
2. Is it distributed via npm or CDN?
3. How should it be loaded in a Next.js application?
4. Why doesn't the ChatKit SDK documentation specify this?

**Possible scenarios**:
- **Scenario A**: Web component is in a separate npm package we haven't found
- **Scenario B**: Web component is loaded via CDN script tag
- **Scenario C**: Web component is bundled with @openai/chatkit-react but requires explicit registration
- **Scenario D**: ChatKit is not meant for production use (beta/internal only)

## Impact on Compliance

**Phase III Requirement**: Use official OpenAI SDKs

**Current status**:
- ✅ Backend uses OpenAI Agents SDK (compliant)
- ❌ Frontend cannot use ChatKit React (missing web component)

**Risk**: If ChatKit web component is not publicly available, we cannot meet FR-014 and may need to revise the spec.

## Next Steps (SDD Process)

1. **Research**: Determine how ChatKit web component should be loaded
2. **Spec Update**: Add missing installation/setup requirements to spec.md
3. **Implementation**: Install/load the web component correctly
4. **Verification**: Confirm ChatKit renders and makes /chatkit requests
5. **Documentation**: Update quickstart.md with complete setup instructions

**Blocking**: Cannot proceed with implementation until we determine the correct method to load the ChatKit web component.
