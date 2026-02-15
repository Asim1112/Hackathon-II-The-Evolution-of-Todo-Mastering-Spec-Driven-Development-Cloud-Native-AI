# Bug Report: ChatKit Component Not Loading

**Bug ID**: BUG-001
**Date**: 2026-02-11
**Severity**: Critical (P0)
**Status**: Investigation

## Observed Behavior

**User Action**: Clicked "Chat" button in navigation
**Expected Result**: ChatKit UI loads and `/chatkit` endpoint is called
**Actual Result**: Backend logs show `POST /api/v1/tasks` being called instead

**Backend Log Evidence**:
```
2026-02-11 21:00:45,908 INFO sqlalchemy.engine.Engine BEGIN (implicit)
2026-02-11 21:00:45,910 INFO sqlalchemy.engine.Engine SELECT task.title, task.description, task.is_completed, task.id, task.owner_id, task.created_at, task.updated_at
FROM task
WHERE task.id = %(pk_1)s
2026-02-11 21:00:45,910 INFO sqlalchemy.engine.Engine [generated in 0.00041s] {'pk_1': 27}
INFO: ::1:0 - "POST /api/v1/tasks HTTP/1.1" 201 Created
2026-02-11 21:00:46,329 INFO sqlalchemy.engine.Engine ROLLBACK
```

## Spec Violation Analysis

### Violated Requirements

**FR-014**: Frontend MUST use ChatKit React component with apiUrl pointing to /chatkit endpoint
- **Expected**: When user navigates to `/dashboard/chat`, ChatKitChat component renders and calls `/chatkit`
- **Actual**: Tasks API (`/api/v1/tasks`) is being called instead

**SC-009**: Frontend uses ChatKit React component with apiUrl="/chatkit" and renders streaming responses
- **Expected**: ChatKit component makes requests to `/chatkit` endpoint
- **Actual**: No `/chatkit` requests observed in backend logs

### Root Cause Hypotheses

**Hypothesis 1: User Navigation Issue**
- User may not be clicking the "Chat" navigation link in Header.tsx:48
- User may be clicking a different button (e.g., "Create Task" button on dashboard)
- **Evidence**: Backend log shows task creation (POST /api/v1/tasks), which is the normal CRUD flow
- **Verification Needed**: Confirm user is actually navigating to `/dashboard/chat` URL

**Hypothesis 2: ChatKit Component Not Rendering**
- ChatKitChat component may be failing to render due to missing dependencies
- Browser console may show errors preventing component mount
- **Evidence**: No `/chatkit` requests in backend logs suggests component never initialized
- **Verification Needed**: Check browser console for errors, verify @openai/chatkit-react is installed

**Hypothesis 3: Environment Variable Missing**
- `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` may not be set in frontend/.env
- ChatKit requires domainKey for API configuration
- **Evidence**: ChatKitChat.tsx:13 uses `process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY || ""`
- **Verification Needed**: Check if env var is set, verify ChatKit initialization

**Hypothesis 4: Route Not Accessible**
- `/dashboard/chat` route may not be properly registered
- AuthGuard may be blocking access
- **Evidence**: Route exists at frontend/app/dashboard/chat/page.tsx
- **Verification Needed**: Test direct navigation to http://localhost:3000/dashboard/chat

## Investigation Steps Required

1. **Verify User Navigation**
   - Ask user to confirm they are clicking "Chat" link in header (not "Create Task" button)
   - Ask user to confirm browser URL shows `/dashboard/chat` after clicking
   - Ask user to check browser network tab for actual requests being made

2. **Check Browser Console**
   - Ask user to open browser DevTools console
   - Look for JavaScript errors related to ChatKit or React
   - Look for module loading errors (@openai/chatkit-react)

3. **Verify Environment Variables**
   - Check if `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` is set in frontend/.env
   - Verify frontend server was restarted after adding env vars

4. **Test Direct Navigation**
   - Navigate directly to http://localhost:3000/dashboard/chat
   - Verify page loads and ChatKit component renders
   - Check network tab for `/chatkit` requests

5. **Verify Package Installation**
   - Run `npm list @openai/chatkit-react` in frontend directory
   - Confirm version matches package.json (@openai/chatkit-react@^1.4.3)

## Spec-Compliant Fix Strategy

Once root cause is identified, the fix must:

1. **Preserve Spec Requirements**
   - FR-014: ChatKit component with apiUrl="/chatkit"
   - SC-009: Streaming responses via ChatKit

2. **Minimal Changes**
   - Only modify what's necessary to fix the identified root cause
   - Do not add features or refactor unrelated code

3. **Verification**
   - After fix, verify `/chatkit` endpoint is called (not `/api/v1/tasks`)
   - Verify ChatKit UI renders correctly
   - Verify streaming responses work

## Confirmed Root Cause

**Diagnostic Results** (2026-02-11):
1. ✅ User clicked correct "Chat" link in header
2. ✅ Browser URL is correct: `http://localhost:3000/dashboard/chat`
3. ✅ Page structure renders: Header, "AI Chat Assistant" heading, subtext, and white box wrapper
4. ❌ **ChatKit component inside wrapper is not rendering** (white box is empty)
5. ❌ **No `/chatkit` requests in Network tab** (ChatKit never initialized)
6. ✅ No JavaScript errors in Console (clean except HMR message)
7. ✅ All resources loaded successfully (50-60 components with 200 status)

**Root Cause**: `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` is empty in `frontend/.env.local:16`

The `useChatKit()` hook receives an empty string for `domainKey`, which prevents ChatKit from initializing. The component wrapper renders (visible as white box), but the ChatKit component inside fails to initialize silently.

## Spec Violation Details

**FR-014**: Frontend MUST use ChatKit React component with apiUrl pointing to /chatkit endpoint
- **Expected**: ChatKit component initializes and makes requests to `/chatkit`
- **Actual**: ChatKit component fails to initialize due to empty `domainKey`, no `/chatkit` requests occur
- **Impact**: Chat functionality completely non-functional

**SC-009**: Frontend uses ChatKit React component with apiUrl="/chatkit" and renders streaming responses
- **Expected**: ChatKit renders UI and handles streaming
- **Actual**: ChatKit does not render at all

## Proposed Fix

**Option 1: Make domainKey optional** (Recommended)
- Remove `domainKey` from ChatKit config if it's not required for local development
- ChatKit SDK may not require domainKey for single-tenant scenarios

**Option 2: Use placeholder value**
- Set `domainKey: "local-dev"` or similar placeholder
- Only if ChatKit requires a non-empty value

**Option 3: Document requirement**
- If domainKey is truly required, add it to quickstart.md and .env.example
- User must obtain a valid domainKey from OpenAI

**Next Step**: Check ChatKit SDK documentation to determine if domainKey is required or optional, then implement minimal fix.
