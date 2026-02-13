# Feature Specification: Fix Better Auth Backend Failure

**Feature Branch**: `13-fix-better-auth-backend`
**Created**: 2026-02-06
**Status**: Draft
**Input**: User description: "BUG SPECIFICATION: Better-Auth Backend Failure + Architectural Violation by Automated Fixes

- Error:
User signup fails at runtime with:

  TypeError: Failed to fetch

Browser Network tab shows:
HTTP 500 returned from the backend during the Better-Auth signup request.

The frontend renders correctly, but submitting the SignUp form causes the request to reach FastAPI and crash.

- Location:
FastAPI backend during Better-Auth signup request
(triggered by Next.js SignUpForm → Better-Auth React client → FastAPI)

- Root Cause:
The signup request successfully reaches the backend, but the FastAPI Better-Auth handler throws an unhandled exception and returns HTTP 500.

The true failure exists inside:
- Better-Auth backend integration
- SQLModel user creation
- Or Neon PostgreSQL interaction

The frontend, proxy, and network routing are NOT the cause.

However, automated fixes incorrectly removed Better-Auth and replaced it with a custom JWT-based authentication system, which violates the project's architecture.

- Architectural Violation:
Claude replaced the required authentication system:

  Better Auth  →  Custom JWT + Direct API calls

This is not allowed.

The project specification explicitly defines:

Technology Stack:
Frontend: Next.js 16+ (App Router)
Backend: FastAPI
ORM: SQLModel
Database: Neon PostgreSQL
Authentication: Better Auth
Spec-Driven: Claude Code + Spec-Kit Plus

Better Auth is a **core architectural requirement** and must NOT be removed, replaced, bypassed, or wrapped with custom auth logic.

All fixes must preserve Better Auth.

- Expected Behavior:
Submitting the SignUp form should:

- Use the Better-Auth frontend client
- Call the Better-Auth FastAPI backend
- Create a user in Neon PostgreSQL
- Return a valid JSON response
- Establish a session or token
- Allow login and navigation

Without returning HTTP 500.

- Solution Approach:
Fix the real backend failure instead of bypassing it:

- Capture the FastAPI traceback produced when the signup request fails.
- Identify the exact line of code inside the Better-Auth backend or database layer that throws.
- Repair the broken database, model, or auth logic.
- Keep Better Auth fully intact.

Do NOT replace Better-Auth with custom JWT logic.
Do NOT change the authentication architecture.
Do NOT bypass the auth system."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Successful User Registration with Better Auth (Priority: P1)

A new user visits the application and wants to create an account by providing their email and password using the Better Auth system. The user fills out the signup form and expects to be successfully registered and logged in through the Better Auth integration.

**Why this priority**: Critical for user acquisition and core functionality of the application as required by architectural specification

**Independent Test**: Can be fully tested by filling out the signup form and verifying the user can register through Better Auth and access protected areas, delivering the ability for new users to join the system using the specified authentication system

**Acceptance Scenarios**:

1. **Given** a visitor is on the signup page, **When** they enter valid email and password and submit the form using Better Auth client, **Then** they are successfully registered through Better Auth and redirected to the dashboard
2. **Given** a visitor enters invalid credentials on the signup page, **When** they submit the form using Better Auth client, **Then** they see an appropriate error message without being redirected

---
### User Story 2 - Successful User Login with Better Auth (Priority: P1)

An existing user wants to access their account by logging in with their credentials using the Better Auth system. The user fills out the signin form and expects to be authenticated and gain access to their protected resources through Better Auth.

**Why this priority**: Critical for user retention and core functionality of the application as required by architectural specification

**Independent Test**: Can be fully tested by entering valid login credentials through Better Auth and accessing protected areas, delivering the ability for returning users to access their data

**Acceptance Scenarios**:

1. **Given** a visitor is on the signin page, **When** they enter valid email and password and submit the form using Better Auth client, **Then** they are successfully authenticated through Better Auth and redirected to the dashboard
2. **Given** a visitor enters incorrect credentials on the signin page, **When** they submit the form using Better Auth client, **Then** they see an appropriate error message without being granted access

---
### User Story 3 - Better Auth Backend Stability (Priority: P2)

When Better Auth requests reach the backend, they should be processed successfully without throwing HTTP 500 errors, maintaining system stability and preventing authentication failures.

**Why this priority**: Critical for system reliability and meeting architectural requirements

**Independent Test**: Can be tested by monitoring backend logs during Better Auth requests and verifying no 500 errors occur

**Acceptance Scenarios**:

1. **Given** a Better Auth request reaches the backend, **When** the request is processed, **Then** it returns an appropriate response without HTTP 500 error

---
## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST integrate with Better Auth as the required authentication system according to architectural specifications
- **FR-002**: System MUST process Better Auth signup requests without throwing HTTP 500 errors
- **FR-003**: Users MUST be able to submit email and password credentials through Better Auth frontend client for signup operations
- **FR-004**: System MUST handle Better Auth requests properly and interact correctly with SQLModel and Neon PostgreSQL
- **FR-005**: System MUST return valid JSON responses for all Better Auth requests
- **FR-006**: System MUST create users in Neon PostgreSQL through Better Auth integration without errors
- **FR-007**: System MUST NOT use custom JWT authentication as a replacement for Better Auth
- **FR-008**: System MUST maintain Better Auth as the sole authentication provider as specified in project architecture

### Key Entities *(include if feature involves data)*

- **Better Auth Request**: Authentication request coming from Better Auth frontend client to backend
- **Better Auth Response**: Valid JSON response returned from backend to Better Auth client
- **User Registration Data**: Email and password information submitted through Better Auth system

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Better Auth signup requests successfully process without HTTP 500 errors at 100% success rate
- **SC-002**: Users can successfully register new accounts via Better Auth signup form with 100% success rate when providing valid credentials
- **SC-003**: Users can successfully log into existing accounts via Better Auth signin form with 100% success rate when providing valid credentials
- **SC-004**: Better Auth authentication network requests properly connect to the backend API without "Failed to fetch" errors