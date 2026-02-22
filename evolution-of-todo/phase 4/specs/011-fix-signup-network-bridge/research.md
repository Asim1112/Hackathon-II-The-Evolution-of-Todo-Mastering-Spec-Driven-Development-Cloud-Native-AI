# Research: Better-Auth Signup Network Connectivity Issue

## Executive Summary

This research investigates the "TypeError: Failed to fetch" error occurring during signup in the Better-Auth integration. The issue stems from a broken network bridge between the frontend Next.js application and the backend FastAPI server, preventing authentication requests from reaching the backend service.

## Problem Analysis

### Symptom
- Error: `TypeError: Failed to fetch`
- Trigger: Clicking "Create Account" on signup form
- Location: `frontend/components/auth/SignUpForm.tsx`
- Call stack: `betterFetch → $fetch → signUp → AuthProvider → onSubmit`

### Root Cause Investigation
The network request fails at fetch-time, indicating that one or more of these components is misconfigured:
1. Better-Auth API base URL
2. Frontend-to-backend origin/port mapping
3. Backend auth route exposure
4. CORS/proxy configuration
5. Next.js proxy/middleware routing

## Technical Findings

### Backend Configuration
- Target backend: FastAPI server running on `http://127.0.0.1:8000`
- Expected auth endpoints: Likely `/auth/*` or `/api/auth/*` routes
- Need to verify actual exposed endpoints

### Frontend Configuration
- Current frontend: Next.js app running on `http://localhost:3000`
- Better-Auth client in `frontend/lib/auth.ts` needs proper base URL
- Proxy configuration required to forward requests

### Known Architecture Constraints
- From constitution: Full-Stack Architecture Standards require FastAPI + Next.js + Better Auth
- JWT-based, stateless authentication
- Frontend-backend communication exclusively through authenticated API calls

## Recommended Solution Approach

### Phase 1: Backend Endpoint Discovery
1. Identify actual auth endpoints exposed by FastAPI Better-Auth backend
2. Confirm backend server availability on `http://127.0.0.1:8000`

### Phase 2: Frontend Configuration
1. Configure Better-Auth client with correct base URL
2. Set up Next.js proxy to forward auth requests to backend

### Phase 3: CORS Configuration
1. Enable CORS on FastAPI to allow requests from `http://localhost:3000`
2. Verify credential handling if needed

## Decision: Backend Endpoint Strategy
**Rationale**: Using the standard FastAPI + Better-Auth integration pattern
**Decision**: The backend likely exposes auth routes at `/auth/*` pattern which needs to be proxied properly

## Decision: Proxy Configuration
**Rationale**: Next.js proxy is the standard way to handle CORS in development
**Decision**: Configure Next.js proxy to forward `/api/auth/*` requests to `http://127.0.0.1:8000/auth/*`

## Decision: Client Configuration
**Rationale**: Better-Auth client should connect to the same origin as served to avoid CORS
**Decision**: Configure Better-Auth client to use `/api/auth` base path for proxy

## Alternatives Considered

### Alternative 1: Direct Backend Calls
- **Approach**: Configure Better-Auth client to call `http://127.0.0.1:8000` directly
- **Issue**: Would require CORS configuration on backend and is not ideal for production
- **Rejection**: Proxy approach is more standard and secure

### Alternative 2: Custom API Routes
- **Approach**: Create Next.js API routes that act as proxy
- **Issue**: Additional complexity layer
- **Rejection**: Built-in Next.js proxy configuration is more straightforward

## Security Considerations
- Maintain stateless JWT authentication as required by constitution
- Ensure proper CORS configuration without exposing endpoints unnecessarily
- Secure credential handling during auth flow