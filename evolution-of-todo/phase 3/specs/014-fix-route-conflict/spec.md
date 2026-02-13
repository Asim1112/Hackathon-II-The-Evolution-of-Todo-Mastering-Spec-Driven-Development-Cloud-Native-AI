# Feature Specification: Fix Next.js API Route Conflict

**Feature Branch**: `014-fix-route-conflict`
**Created**: 2026-02-06
**Status**: Draft
**Input**: User description: "BUG SPECIFICATION: Next.js API Route Conflict Causing Dev Server Crash and Auth Failures

- Error:
Next.js fails to start with:
'You cannot define a route with the same specificity as a optional catch-all route ("/api/tasks" and "/api/tasks[[...path]]")'

- Symptoms:
1. Frontend crashes on startup
2. Signup API returns HTTP 500 (email → Failed to fetch)
3. Better Auth fails even though backend is running
4. Network tab shows auth.ts:54 → fetch → 500

- Location:
frontend/app/api/tasks/

- Root Cause:
The frontend defines two conflicting routes:

1. /api/tasks/route.ts
2. /api/tasks/[[...path]]/route.ts

The optional catch-all route ([[...path]]) already matches `/api/tasks`, so Next.js prohibits having both.

This happened because Claude previously added a FastAPI proxy layer while the original Next.js route still existed.

This is a routing-level crash that happens before Better Auth or any API call can run.

- Architectural Requirement (MANDATORY):
This project follows a strict split:

Frontend: Next.js (UI only)
Backend: FastAPI (ALL business logic & APIs)
Auth: Better Auth (frontend ↔ backend)

Therefore:
Next.js must NOT implement `/api/tasks` itself.
It must only PROXY `/api/tasks/*` to FastAPI.

The only valid Next.js route for tasks is:
frontend/app/api/tasks/[[...path]]/route.ts

The direct implementation must be removed:
frontend/app/api/tasks/route.ts

- What must NOT be done:
❌ Do NOT remove Better Auth
❌ Do NOT replace auth with JWT
❌ Do NOT move task logic into Next.js
❌ Do NOT bypass FastAPI
❌ Do NOT change tech stack

- Expected Outcome:
1. Next.js dev server starts without routing errors
2. /api/tasks/* correctly proxies to FastAPI
3. Better Auth endpoints remain intact and functional
4. Signup no longer returns 500
5. No duplicate or overlapping routes exist

Fix the routing layer only — do not touch authentication or backend logic."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Developer Can Start Frontend Server Successfully (Priority: P1)

A developer attempts to start the Next.js development server and expects it to start without routing conflicts. The server should boot up properly without the "cannot define a route with the same specificity" error.

**Why this priority**: Critical for development workflow - without a working frontend server, no development can proceed on the application.

**Independent Test**: The Next.js development server can be started with `npm run dev` without routing conflicts, proving the route resolution system works properly.

**Acceptance Scenarios**:

1. **Given** the frontend code with route conflicts has been resolved, **When** a developer runs `npm run dev`, **Then** the Next.js server starts successfully without routing errors
2. **Given** only the valid proxy route exists, **When** Next.js attempts to resolve routes, **Then** no conflicts occur and the server boots normally

---
### User Story 2 - Task API Requests Are Properly Proxied (Priority: P1)

A user performs task-related operations in the application, expecting the Next.js frontend to properly proxy these requests to the FastAPI backend instead of handling them locally.

**Why this priority**: Critical for functionality - task operations are core to the application and must work properly via the intended architecture.

**Independent Test**: API requests to `/api/tasks/*` are successfully proxied to the FastAPI backend and return appropriate responses.

**Acceptance Scenarios**:

1. **Given** a user makes a request to `/api/tasks/`, **When** the request goes through Next.js, **Then** it is properly forwarded to the FastAPI backend and returns the expected task data
2. **Given** a user makes requests to specific task endpoints like `/api/tasks/123`, **When** the request goes through Next.js, **Then** it is properly forwarded to the FastAPI backend with correct parameters

---
### User Story 3 - Authentication Continues to Function Properly (Priority: P2)

A user attempts to sign up or log in while the route conflict is being fixed, expecting Better Auth functionality to remain unaffected and operational.

**Why this priority**: Important for user experience - authentication should not be impacted by routing changes to the task API.

**Independent Test**: Better Auth endpoints continue to work normally without disruption during the route conflict fix.

**Acceptance Scenarios**:

1. **Given** the route conflict has been resolved, **When** a user attempts to sign up, **Then** the request is processed successfully without HTTP 500 errors
2. **Given** the route conflict has been resolved, **When** a user attempts to log in, **Then** the authentication process completes successfully

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST resolve the routing conflict between `/api/tasks/route.ts` and `/api/tasks/[[...path]]/route.ts`
- **FR-002**: System MUST remove the conflicting direct implementation at `frontend/app/api/tasks/route.ts`
- **FR-003**: System MUST maintain only the proxy route at `frontend/app/api/tasks/[[...path]]/route.ts`
- **FR-004**: System MUST correctly forward all `/api/tasks/*` requests to the FastAPI backend
- **FR-005**: System MUST NOT interfere with Better Auth endpoints and authentication functionality
- **FR-006**: System MUST allow Next.js development server to start without routing errors
- **FR-007**: System MUST preserve the architectural split where Next.js only acts as a proxy for FastAPI
- **FR-008**: System MUST continue to support all task-related API operations through the proxy

### Key Entities *(include if feature involves data)*

- **Route Conflict**: The dual route definition causing Next.js startup failure
- **Proxy Route**: The valid route `frontend/app/api/tasks/[[...path]]/route.ts` that forwards to FastAPI
- **Conflicting Route**: The invalid route `frontend/app/api/tasks/route.ts` that needs removal
- **Task API Requests**: API calls for task operations that need to be properly proxied to FastAPI

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Next.js development server starts successfully 100% of the time without routing conflict errors
- **SC-002**: All `/api/tasks/*` requests are successfully proxied to FastAPI backend with <2s response time
- **SC-003**: Better Auth functionality remains operational with 100% success rate for authentication operations
- **SC-004**: No duplicate or overlapping routes exist in the Next.js routing system
- **SC-005**: Task-related API operations continue to work normally through the proxy layer