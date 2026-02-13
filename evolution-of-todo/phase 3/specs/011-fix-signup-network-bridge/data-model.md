# Data Model: Better-Auth Network Connectivity

**Feature**: Fix Better-Auth Signup Network Connectivity
**Branch**: `011-fix-signup-network-bridge`
**Date**: 2026-02-05
**Modeler**: Claude Code
**Status**: Completed

## Overview

This data model defines the interface contracts and data flow for the authentication network bridge between the Next.js frontend and FastAPI backend. It covers the Better-Auth client configuration, authentication request/response patterns, and proxy configuration parameters.

## Entity Definitions

### AuthenticationRequest
Represents the data structure for authentication requests flowing from frontend to backend.

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| method | string | Yes | GET/POST/PUT/DELETE | HTTP method for the request |
| endpoint | string | Yes | Valid auth endpoint | Specific auth endpoint (e.g., /auth/sign-up, /auth/login) |
| payload | object | Conditional | Per endpoint schema | Request payload data for POST/PUT requests |
| headers | object | No | Valid HTTP headers | Additional headers for authentication |

### AuthenticationResponse
Represents the data structure for authentication responses flowing from backend to frontend.

| Field | Type | Required | Values | Description |
|-------|------|----------|--------|-------------|
| status | number | Yes | 2xx, 4xx, 5xx | HTTP status code |
| data | object | Conditional | Response payload | Success response data |
| error | object | Conditional | Error details | Error response if request failed |
| success | boolean | Yes | true/false | Whether the request was successful |

### BetterAuthClientConfig
Configuration structure for the Better-Auth client in the frontend.

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| baseURL | string | Yes | Valid URL format | Base URL for Better-Auth API calls |
| headers | object | No | Valid HTTP headers | Default headers for all requests |
| timeout | number | No | Positive integer | Request timeout in milliseconds |

### ProxyRoute
Configuration structure for Next.js proxy routes.

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| source | string | Yes | Valid route pattern | Route pattern to match on frontend |
| destination | string | Yes | Valid URL format | Backend URL to forward requests to |
| changeOrigin | boolean | No | true/false | Whether to change the origin header |

## Interface Contracts

### Auth API Interface
The following endpoints need to be accessible through the proxy:

#### Sign-Up Endpoint
```typescript
POST /api/auth/sign-up
Payload: { email: string, password: string }
Response: { user: object, session: object } | { error: string }
```

#### Login Endpoint
```typescript
POST /api/auth/login
Payload: { email: string, password: string }
Response: { user: object, session: object } | { error: string }
```

#### Session Verification Endpoint
```typescript
GET /api/auth/session
Headers: { Authorization: string }
Response: { user: object, session: object } | { error: string }
```

## Data Flow

### Authentication Request Flow
1. User submits authentication form (signup/login)
2. Better-Auth client creates request with proper configuration
3. Request goes through Next.js proxy configuration
4. Proxy forwards request to FastAPI backend at `http://127.0.0.1:8000`
5. Backend processes request and sends response
6. Response travels back through proxy to frontend
7. Better-Auth client processes response and updates UI

### Error Handling Flow
1. If network error occurs: Better-Auth client catches and reports `TypeError: Failed to fetch`
2. If backend returns error: Proper error response transmitted to frontend
3. Frontend displays appropriate error message to user

## Security Considerations

### JWT Token Handling
- Tokens must be securely stored (preferably in httpOnly cookies or secure localStorage)
- Token validation must happen on both client and server
- Tokens must have appropriate expiration times

### CORS Configuration
- Allow only trusted origins (`http://localhost:3000` in development)
- Proper credential handling for cross-origin requests
- Secure headers configuration

### Network Layer Security
- All auth communication should be encrypted
- Proper validation of incoming requests
- Rate limiting on authentication endpoints

## Configuration Requirements

### Frontend (Next.js)
- Proxy configuration to forward `/api/auth/*` to backend
- Better-Auth client configured with proxy endpoint (not direct backend)
- CORS headers set appropriately

### Backend (FastAPI)
- CORS middleware configured to allow frontend origin
- Authentication routes properly exposed
- Backend running on correct port (`http://127.0.0.1:8000`)

## Validation Rules

### Client Configuration Validation
- Base URL must be a valid endpoint
- Timeout values must be positive numbers
- Headers must be valid HTTP headers

### Request Validation
- Authentication payloads must be properly formatted
- Required fields must be present
- Email/password validation must occur before submission

## Integration Points

### Frontend Integration
- `frontend/lib/auth.ts`: Better-Auth client configuration
- `next.config.js`: Proxy route configuration
- `frontend/components/auth/SignUpForm.tsx`: Authentication form implementation

### Backend Integration
- FastAPI auth routes: Backend authentication endpoints
- CORS middleware: Cross-origin request handling
- Authentication service: User management and session handling