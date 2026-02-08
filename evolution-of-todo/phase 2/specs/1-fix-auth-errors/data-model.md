# Data Model: Authentication System

**Feature**: Frontend-Backend Authentication Connection
**Date**: 2026-02-06

## Overview
This data model describes the authentication-related data structures used in the frontend-backend authentication system. The system maintains compatibility with the existing backend's JWT-based authentication approach.

## Authentication Data Structures

### User Credentials
**Description**: Information required for user authentication operations

**Fields**:
- email (string): User's email address for identification
- password (string): User's password (sent securely to backend for verification)

**Validation**:
- Email: Must be a valid email format
- Password: Minimum length requirements (handled by backend)

### Authentication Response
**Description**: Structure of data returned by backend authentication endpoints

**Fields**:
- access_token (string): JWT token issued upon successful authentication
- token_type (string): Type of token (always "bearer")
- user (object): User information

**Backend Response Format**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "uuid-string",
    "email": "user@example.com"
  }
}
```

### Frontend User Object
**Description**: Simplified user representation used in frontend application

**Fields**:
- userId (string): Unique identifier for the user
- email (string): User's email address

**Format**:
```json
{
  "userId": "uuid-string",
  "email": "user@example.com"
}
```

## Token Storage Model

### JWT Token
**Description**: Authentication token stored in browser localStorage

**Location**: `localStorage.auth_token`

**Structure**: Standard JWT with claims:
- `sub`: Subject (user ID)
- `email`: User email
- `exp`: Expiration timestamp
- `iat`: Issued at timestamp

**Security Considerations**:
- Stored in localStorage (accessible by JavaScript)
- Has expiration time to limit exposure window
- Sent with Bearer scheme in Authorization header

## API Request/Response Patterns

### Signup Request
**Endpoint**: `POST /api/v1/auth/signup`
**Content-Type**: `application/json`

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "secure-password"
}
```

**Response (Success)**:
```json
{
  "access_token": "jwt-token-string",
  "token_type": "bearer",
  "user": {
    "id": "user-uuid",
    "email": "user@example.com"
  }
}
```

### Signin Request
**Endpoint**: `POST /api/v1/auth/signin`
**Content-Type**: `application/json`

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "secure-password"
}
```

**Response (Success)**:
```json
{
  "access_token": "jwt-token-string",
  "token_type": "bearer",
  "user": {
    "id": "user-uuid",
    "email": "user@example.com"
  }
}
```

### Task API Authentication
**All task endpoints** require JWT authentication:
- Header: `Authorization: Bearer {access_token}`
- Backend verifies token validity before processing request

## State Management

### Authentication State
**Location**: React context managed by AuthProvider

**Structure**:
```typescript
interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}
```

### Token Lifecycle
1. Upon successful authentication: JWT stored in localStorage
2. For protected API requests: JWT retrieved from localStorage and sent in Authorization header
3. On logout: JWT removed from localStorage
4. Token validation: Handled server-side on each protected request

## Error Handling Data

### Authentication Errors
**Format**: Standard error response from backend

```json
{
  "detail": "Error message for user",
  "error_code": "AUTH_001",
  "timestamp": "2026-02-06T10:30:00Z"
}
```

### Network Errors
**Handled in frontend**: Converted to user-friendly messages
- "Network error: Unable to connect to authentication server"
- Proper error state updates in authentication context