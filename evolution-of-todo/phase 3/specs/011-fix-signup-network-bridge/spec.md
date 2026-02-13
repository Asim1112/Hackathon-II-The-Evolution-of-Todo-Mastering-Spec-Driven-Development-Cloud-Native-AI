# Feature Specification: Fix Better-Auth Signup Network Connectivity

**Feature Branch**: `011-fix-signup-network-bridge`
**Created**: 2026-02-05
**Status**: Draft
**Input**: User description: "BUG SPECIFICATION: Signup Request Fails — Better-Auth Client Cannot Reach Backend

- Error:
TypeError: Failed to fetch

Triggered when clicking **Create Account** on the signup form.

Call stack shows failure inside Better-Auth network layer:

   betterFetch → $fetch → signUp → AuthProvider → onSubmit

- Location:
Frontend runtime during:
frontend/components/auth/SignUpForm.tsx submission
(frontend/.next static chunks calling Better-Auth client)

- Root Cause:
The Better-Auth frontend client is attempting to call the authentication API (signUp) but the network request fails at fetch-time.

This indicates that one or more of the following is broken:

- The Better-Auth API base URL is incorrect or missing.
- The frontend is pointing to the wrong backend origin or port.
- The backend auth routes are not exposed where the client expects them.
- CORS or proxy configuration is blocking the request.
- The Next.js proxy/middleware is not forwarding `/api/auth/*` correctly to the FastAPI backend.

Because the request never reaches the server, the browser throws `TypeError: Failed to fetch` instead of receiving an HTTP response.

- Expected Behavior:
When clicking **Create Account**, the frontend should send a POST request to the backend Better-Auth signup endpoint.

The backend should respond with a success or validation error, and the UI should proceed to login or dashboard instead of crashing.

- Solution Approach:
Verify and fix the frontend → backend auth network bridge:

- Identify the actual auth endpoint exposed by the FastAPI Better-Auth backend (e.g. `/auth`, `/api/auth`, etc).
- Ensure the Better-Auth client in `frontend/lib/auth.ts` is configured with the correct base URL.
- Verify that Next.js proxy (or `proxy.ts`) forwards auth requests to `http://127.0.0.1:8000`.
- Ensure CORS on the FastAPI backend allows requests from `http://localhost:3000`.
- Confirm that a real HTTP request reaches the backend when SignUp is clicked."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - User Can Successfully Complete Signup (Priority: P1)

User clicks the "Create Account" button on the signup form and the request successfully reaches the backend authentication service, allowing the user to register for the application. The process completes without network errors, enabling user acquisition to proceed normally.

**Why this priority**: This is critical as the signup functionality is currently non-functional due to the network connectivity issue. Without fixing this, new users cannot register for the application, effectively blocking user acquisition and growth.

**Independent Test**: The signup form can successfully send registration requests to the backend service and receive appropriate responses, proving the authentication network bridge is operational.

**Acceptance Scenarios**:

1. **Given** a user filling out the signup form with valid credentials, **When** the user clicks "Create Account", **Then** the request successfully reaches the backend authentication service and the user receives confirmation of successful registration

2. **Given** the Better-Auth client properly configured with correct backend endpoint, **When** the SignUpForm component attempts to submit user data via the API, **Then** the network request completes successfully without "TypeError: Failed to fetch" errors

---

### User Story 2 - Network Connectivity is Reliable (Priority: P2)

The authentication system maintains stable connectivity between the frontend and backend services, ensuring consistent communication during user registration and subsequent authentication operations. The network bridge handles requests reliably without intermittent failures.

**Why this priority**: Essential for system reliability and user experience to ensure authentication operations work consistently across different network conditions and usage patterns.

**Independent Test**: Authentication requests consistently reach the backend service with minimal failure rates under normal operating conditions.

**Acceptance Scenarios**:

1. **Given** properly configured network bridge between frontend and backend, **When** multiple users attempt signup simultaneously, **Then** requests are processed successfully without connectivity errors

---

### User Story 3 - Error Handling Works Properly (Priority: P3)

When authentication requests fail for legitimate reasons (invalid credentials, server overload, etc.), users receive appropriate error messages rather than generic network errors. Proper error handling ensures users understand what went wrong and how to proceed.

**Why this priority**: Important for user experience to provide meaningful feedback when authentication operations fail for expected reasons.

**Independent Test**: When authentication requests fail for expected reasons, users receive appropriate error responses rather than network-level errors.

**Acceptance Scenarios**:

1. **Given** backend authentication service is reachable but rejects a request due to validation errors, **When** signup fails for valid reasons, **Then** users receive specific error messages about what needs correction

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST establish reliable network connectivity between Better-Auth frontend client and backend authentication service
- **FR-002**: System MUST configure the Better-Auth client with correct base URL and backend endpoint information
- **FR-003**: System MUST route authentication requests from frontend to the correct backend service endpoint
- **FR-004**: System MUST handle network errors appropriately and provide meaningful feedback to users
- **FR-005**: System MUST ensure CORS policies allow communication between frontend and backend services
- **FR-006**: System MUST establish proper proxy configuration to forward requests from frontend port to backend port
- **FR-007**: System MUST verify that authentication requests actually reach the backend service and receive responses

### Key Entities

- **Authentication Client**: The Better-Auth frontend client component that initiates authentication requests
- **Network Bridge**: The communication layer connecting frontend and backend services (proxy, routing, CORS)
- **Authentication Service**: The backend service that processes registration and authentication requests
- **User Registration Data**: The user information sent during the signup process (credentials, personal information)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Signup requests successfully reach the backend service 100% of the time without "TypeError: Failed to fetch" errors
- **SC-002**: Network connectivity between frontend and backend maintains >99% uptime during normal operation
- **SC-003**: Authentication requests complete within 5 seconds under normal network conditions
- **SC-004**: Error handling correctly distinguishes between network errors and validation errors with >95% accuracy
- **SC-005**: Development server starts within 30 seconds of running `npm run dev` with proper service connectivity
