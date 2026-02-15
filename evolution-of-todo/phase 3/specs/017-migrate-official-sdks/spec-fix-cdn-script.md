# Spec Fix: ChatKit CDN Script Required

**Date**: 2026-02-11
**Issue**: FR-014 incomplete - missing CDN script to load web component
**Status**: Ready to implement
**Source**: Official ChatKit.js documentation (https://openai.github.io/chatkit-js/quickstart)

## Root Cause

**From official documentation** (https://openai.github.io/chatkit-js/quickstart):

The ChatKit web component is loaded via CDN, not npm import:

```html
<script
  src="https://cdn.platform.openai.com/deployments/chatkit/chatkit.js"
  async
></script>
```

**Package architecture**:
- `@openai/chatkit` npm package - TypeScript types ONLY (no JavaScript implementation)
- `@openai/chatkit-react` npm package - React wrappers (no web component)
- **CDN script** - Actual `<openai-chatkit>` web component implementation

**Current state**:
- ✅ `@openai/chatkit@1.5.0` installed (types only)
- ✅ `@openai/chatkit-react@1.4.3` installed (React wrappers)
- ❌ **CDN script never loaded** → web component not registered

## Spec Violation

**FR-014 is incomplete**. It specifies:
- ✅ Install `@openai/chatkit-react`
- ✅ Use `useChatKit` hook and `<ChatKit>` component
- ❌ **Missing**: Load ChatKit CDN script to register web component

## Proposed Fix

### 1. Update Spec (FR-014)

**Add requirement**:
- **FR-014a**: Frontend MUST load ChatKit web component from CDN: `https://cdn.platform.openai.com/deployments/chatkit/chatkit.js`

### 2. Implementation Change

**File**: `frontend/app/layout.tsx`

**Add Script component**:
```typescript
import Script from "next/script";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Script
          src="https://cdn.platform.openai.com/deployments/chatkit/chatkit.js"
          strategy="afterInteractive"
        />
        <Providers>
          <Header />
          <main>{children}</main>
        </Providers>
      </body>
    </html>
  );
}
```

**Script loading strategy**:
- `strategy="afterInteractive"` - Loads after page is interactive (recommended for third-party scripts)
- Alternative: `strategy="lazyOnload"` - Loads during idle time (if not critical)

### 3. Component Configuration

**File**: `frontend/components/chat/ChatKitChat.tsx`

**Current implementation** (already correct):
```typescript
"use client";

import { useChatKit, ChatKit } from "@openai/chatkit-react";

export function ChatKitChat({ userId }: ChatKitChatProps) {
  const chatkit = useChatKit({
    api: {
      url: "/chatkit",
      domainKey: "local-dev",  // Valid for local development
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

## Verification Steps

After implementing the fix:

1. ✅ Refresh browser at `http://localhost:3000/dashboard/chat`
2. ✅ Check browser DevTools → Network tab → Filter "chatkit.js" → Should see 200 status
3. ✅ ChatKit UI should render (input box, message area, header)
4. ✅ Network tab should show `/chatkit` API requests
5. ✅ Sending "Hello" should trigger agent response with streaming
6. ✅ MCP tools should work: "Add a task to buy milk"

## Compliance Impact

**Phase III Requirement**: Use official OpenAI SDKs

**After fix**:
- ✅ Backend uses OpenAI Agents SDK (already working)
- ✅ Frontend uses ChatKit React SDK (will work after CDN script loads)
- ✅ All 6 Phase III requirements met

## Next Steps (SDD Process)

1. ✅ Document spec gap (this file)
2. → Implement the fix (add CDN script to layout.tsx)
3. → Test verification steps
4. → Update quickstart.md with CDN script requirement
5. → Mark FR-014 as complete
