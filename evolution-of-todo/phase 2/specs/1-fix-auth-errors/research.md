# Research: Frontend-Backend Authentication Connection

**Feature**: Fix "Failed to fetch" errors during signup and signin
**Date**: 2026-02-06

## Research Summary

### Issue Identified
The frontend was experiencing "Failed to fetch" errors during signup and signin operations. Investigation revealed that the frontend was configured to use Better Auth for authentication, while the backend has a custom JWT-based FastAPI authentication system. This mismatch caused the frontend to try to communicate with incompatible authentication endpoints.

### Root Cause Analysis
1. **Frontend Authentication Service**: Using Better Auth client that expects Better Auth API endpoints
2. **Backend Authentication API**: Custom JWT-based implementation at `/api/v1/auth/signup` and `/api/v1/auth/signin`
3. **Communication Mismatch**: Different API protocols and data structures between frontend and backend

### Solution Implemented
Replaced Better Auth implementation in `frontend/lib/auth.ts` with direct API calls to FastAPI backend endpoints:
- `POST /api/v1/auth/signup` for user registration
- `POST /api/v1/auth/signin` for user authentication
- Proper JWT token handling and storage

### Backend API Structure Confirmed
- Authentication endpoints: `/api/v1/auth/signup` and `/api/v1/auth/signin`
- Task endpoints: `/api/v1/tasks/*`
- All task endpoints require JWT authentication
- Backend configured with proper CORS settings for frontend integration

## Technical Decisions

### Decision: Remove Better Auth Dependency
**Rationale**: Better Auth is designed for Next.js full-stack applications, but this project uses a separate frontend/backend architecture with a custom FastAPI backend. The BETTER_AUTH_DECISION.md recommends keeping the custom auth system.

**Alternatives considered**:
- Keep Better Auth and modify backend to support it: Would require major backend refactoring
- Use a hybrid approach: Would add unnecessary complexity
- Remove Better Auth entirely: Cleanest solution matching project architecture

### Decision: Use Direct Fetch API Calls
**Rationale**: Direct API calls provide maximum control over request/response handling and align with the existing custom authentication system.

**Alternatives considered**:
- Axios library: Would add unnecessary dependency
- Custom API wrapper: Already exists in api-client.ts for other endpoints
- GraphQL: Overkill for simple auth operations

### Decision: Maintain JWT Token Storage
**Rationale**: JWT tokens fit well with the existing custom authentication system and can be stored securely in localStorage for browser-based access.

**Alternatives considered**:
- HttpOnly cookies: Would require backend changes to handle CSRF protection
- Session storage: Less persistent than localStorage
- Memory-only storage: Would lose authentication on page refresh

## Implementation Details

### Authentication Flow
1. Frontend makes POST request to `/api/v1/auth/signup` or `/api/v1/auth/signin`
2. Backend validates credentials and returns JWT token
3. Frontend stores JWT token in localStorage
4. Subsequent API requests include Authorization header with Bearer token
5. Backend validates JWT token for protected endpoints

### Error Handling
- Network errors are caught and converted to user-friendly messages
- HTTP error responses from backend are parsed and displayed appropriately
- Invalid credentials return proper error messages without revealing system details

## Security Considerations

- JWT tokens are stored in localStorage (suitable for this architecture)
- All backend endpoints properly validate JWT tokens
- Passwords are never exposed to frontend (hashed server-side)
- Proper CORS headers configured for secure cross-origin requests

## Dependencies Updated

- Updated `frontend/lib/auth.ts` to remove Better Auth and implement direct API calls
- Updated `frontend/middleware.ts` to work with custom JWT authentication
- Updated `frontend/lib/api-client.ts` to use correct API endpoint structure
- Added `frontend/.env.local` for proper backend URL configuration