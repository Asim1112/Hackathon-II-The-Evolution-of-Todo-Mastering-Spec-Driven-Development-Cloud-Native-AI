---
id: 001
title: "Create Signup Network Fix Specification"
stage: spec
date_iso: "2026-02-05"
surface: "agent"
model: "Claude Sonnet 4.5"
feature: "fix-signup-network-bridge"
branch: "011-fix-signup-network-bridge"
user: "user"
command: "sp.specify"
labels:
  - "bug-fix"
  - "network"
  - "auth"
  - "frontend"
  - "backend"
links:
  spec: "F:\\Hackathon II\\evolution-of-todo\\phase 2\\specs\\011-fix-signup-network-bridge\\spec.md"
  ticket: null
  adr: null
  pr: null
files_yaml:
  - "F:\\Hackathon II\\evolution-of-todo\\phase 2\\specs\\011-fix-signup-network-bridge\\spec.md"
  - "F:\\Hackathon II\\evolution-of-todo\\phase 2\\specs\\011-fix-signup-network-bridge\\checklists\\requirements.md"
tests_yaml:
  - "User story validation"
  - "Requirements completeness check"
  - "Success criteria measurability"
outcome: "Created comprehensive specification for fixing Better-Auth signup network connectivity"
evaluation: "Specification addresses all aspects of the network connectivity issue with clear user stories and requirements"
---

# Prompt History Record

## Input
```
BUG SPECIFICATION: Signup Request Fails — Better-Auth Client Cannot Reach Backend

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
- Confirm that a real HTTP request reaches the backend when SignUp is clicked.
```

## Response Summary
Created comprehensive feature specification to address the Better-Auth signup network connectivity issue. The spec includes three prioritized user stories focusing on successful signup completion, reliable network connectivity, and proper error handling. Seven functional requirements define the necessary capabilities to establish proper communication between frontend and backend services. Success criteria include measurable outcomes for network reliability and performance.

## Outcome
Specification provides clear roadmap for fixing the "TypeError: Failed to fetch" error during signup by addressing the network bridge between Better-Auth client and backend authentication service.