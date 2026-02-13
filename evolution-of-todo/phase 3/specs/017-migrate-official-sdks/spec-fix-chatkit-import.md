# Spec Fix: Missing ChatKit Web Component Registration

**Date**: 2026-02-11
**Issue**: FR-014 incomplete - missing web component registration step
**Status**: Ready to implement
**Source**: Official ChatKit.js documentation (https://openai.github.io/chatkit-js/quickstart)

## Problem Statement

**Current Spec (FR-014)**: Frontend MUST use ChatKit React component with apiUrl pointing to /chatkit endpoint

**Implementation attempted**:
```typescript
import { useChatKit, ChatKit } from "@openai/chatkit-react";
```

**Result**: Component does not render because the `<openai-chatkit>` custom element is not registered.

## Root Cause

The `@openai/chatkit` package contains the web component implementation, but it must be **explicitly imported** to register the custom element in the browser.

**From official documentation** (https://openai.github.io/chatkit-js/quickstart):

### Vanilla JS Setup
```bash
npm install @openai/chatkit
```

```javascript
import '@openai/chatkit';  // Registers <openai-chatkit> custom element

const chatkit = document.createElement('openai-chatkit');
chatkit.setOptions({ /* ... */ });
```

### React Setup
```bash
npm install @openai/chatkit-react
```

```jsx
import { ChatKit, useChatKit } from '@openai/chatkit-react';

export function SupportChat() {
  const { control } = useChatKit({
    api: {
      url: 'http://localhost:8000/chatkit',
      domainKey: 'local-dev',  // ← Can use simple string for local dev
    },
  });

  return <ChatKit control={control} className="h-[600px] w-[360px]" />;
}
```

**Critical Note**: The React example doesn't show the `import '@openai/chatkit'` line, but it's required for the web component to be registered.

## Spec Violation

**FR-014 is incomplete**. It specifies:
- ✅ Install `@openai/chatkit-react`
- ✅ Use `useChatKit` hook and `<ChatKit>` component
- ❌ **Missing**: Import `@openai/chatkit` to register web component

## Proposed Fix

### 1. Update Spec (FR-014)

**Add requirement**:
- **FR-014a**: Frontend MUST import `@openai/chatkit` to register the `<openai-chatkit>` custom element before using React components

### 2. Implementation Change

**File**: `frontend/components/chat/ChatKitChat.tsx`

**Add import**:
```typescript
import "@openai/chatkit";  // Registers <openai-chatkit> web component
```

**Complete implementation**:
```typescript
"use client";

import "@openai/chatkit";  // ← ADD THIS LINE
import { useChatKit, ChatKit } from "@openai/chatkit-react";

interface ChatKitChatProps {
  userId: string;
}

export function ChatKitChat({ userId }: ChatKitChatProps) {
  const chatkit = useChatKit({
    api: {
      url: "/chatkit",
      domainKey: "local-dev",  // ← Use simple string for local dev
      fetch: async (url, init) => {
        const headers = new Headers(init?.headers);
        headers.set("X-User-Id", userId);
        return fetch(url, { ...init, headers, credentials: "include" });
      },
    },
    initialThread: userId,
    composer: { placeholder: "Ask me about your tasks..." },
    header: { title: { text: "AI Todo Assistant" } },
    theme: "light",
  });

  return (
    <div className="h-[calc(100vh-12rem)] w-full rounded-lg border border-zinc-200 dark:border-zinc-800 shadow-sm overflow-hidden">
      <ChatKit control={chatkit.control} style={{ height: "100%", width: "100%" }} />
    </div>
  );
}
```

### 3. domainKey Configuration

**From official docs**: `domainKey: 'local-dev'` is valid for local development.

**Options**:
- Use `"local-dev"` hardcoded (simplest for hackathon)
- Use env var with fallback: `process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY || "local-dev"`

## Verification Steps

After implementing the fix:

1. ✅ Refresh browser at `http://localhost:3000/dashboard/chat`
2. ✅ ChatKit UI should render (input box, message area)
3. ✅ Network tab should show `/chatkit` requests
4. ✅ Sending "Hello" should trigger agent response
5. ✅ MCP tools should work ("Add a task to buy milk")

## Compliance Impact

**Phase III Requirement**: Use official OpenAI SDKs

**After fix**:
- ✅ Backend uses OpenAI Agents SDK (already working)
- ✅ Frontend uses ChatKit React SDK (will work after fix)
- ✅ All 6 Phase III requirements met

## Next Steps (SDD Process)

1. ✅ Document spec gap (this file)
2. → Implement the fix (add import line)
3. → Test verification steps
4. → Update quickstart.md with complete setup
5. → Mark FR-014 as complete
