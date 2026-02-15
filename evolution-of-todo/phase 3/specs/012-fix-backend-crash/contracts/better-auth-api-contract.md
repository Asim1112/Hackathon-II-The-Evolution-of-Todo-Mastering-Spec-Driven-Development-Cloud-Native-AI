# API Contract: Better Auth Authentication Endpoints

**Feature**: Fix Better-Auth Signup HTTP 500 Error
**Date**: 2026-02-06
**Version**: 1.0

## Overview
This document defines the API contracts for Better Auth authentication endpoints that the frontend communicates with. These contracts ensure proper integration between the Next.js frontend and the Better Auth authentication system.

## Authentication Endpoints

### POST /api/auth/signup
**Description**: Register a new user account through Better Auth

#### Request
**Method**: POST
**URL**: `/api/auth/signup`
**Headers**:
- `Content-Type: application/json`

**Body**:
```json
{
  "email": "user@example.com",
  "password": "secure-password",
  "name": "User Name"
}
```

**Field Requirements**:
- `email`: String, valid email format
- `password`: String, minimum length and complexity requirements enforced by Better Auth
- `name`: String (optional), user's display name

#### Responses

**Success Response (200 OK)**
```json
{
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "emailVerified": false,
    "createdAt": "2026-02-06T10:30:00Z",
    "updatedAt": "2026-02-06T10:30:00Z"
  },
  "session": {
    "id": "sess_1234567890abcdef",
    "expiresAt": "2026-02-07T10:30:00Z",
    "createdAt": "2026-02-06T10:30:00Z"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Error Response (400 Bad Request)**
```json
{
  "error": {
    "message": "Invalid email format",
    "code": "INVALID_EMAIL"
  }
}
```

**Error Response (409 Conflict)**
```json
{
  "error": {
    "message": "User with this email already exists",
    "code": "USER_EXISTS"
  }
}
```

**Error Response (422 Unprocessable Entity)**
```json
{
  "error": {
    "message": "Password does not meet requirements",
    "code": "PASSWORD_WEAK"
  }
}
```

**Error Response (500 Internal Server Error)**
```json
{
  "error": {
    "message": "Internal server error occurred during signup",
    "code": "INTERNAL_ERROR",
    "timestamp": "2026-02-06T10:30:00Z"
  }
}
```

---

### POST /api/auth/signin
**Description**: Authenticate an existing user through Better Auth

#### Request
**Method**: POST
**URL**: `/api/auth/signin`
**Headers**:
- `Content-Type: application/json`

**Body**:
```json
{
  "email": "user@example.com",
  "password": "secure-password"
}
```

**Field Requirements**:
- `email`: String, valid email format
- `password`: String, user's password

#### Responses

**Success Response (200 OK)**
```json
{
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com"
  },
  "session": {
    "id": "sess_1234567890abcdef",
    "expiresAt": "2026-02-07T10:30:00Z"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Error Response (400 Bad Request)**
```json
{
  "error": {
    "message": "Invalid email or password",
    "code": "INVALID_CREDENTIALS"
  }
}
```

**Error Response (429 Too Many Requests)**
```json
{
  "error": {
    "message": "Too many failed attempts, please try again later",
    "code": "RATE_LIMITED"
  }
}
```

---

### GET /api/auth/session
**Description**: Retrieve current user session information

#### Request
**Method**: GET
**URL**: `/api/auth/session`
**Headers**:
- `Authorization: Bearer {jwt_token}` (optional, for authenticated users)

#### Responses

**Success Response (200 OK) - Authenticated User**
```json
{
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com"
  },
  "session": {
    "id": "sess_1234567890abcdef",
    "expiresAt": "2026-02-07T10:30:00Z"
  }
}
```

**Success Response (200 OK) - No Active Session**
```json
{
  "user": null,
  "session": null
}
```

---

### POST /api/auth/signout
**Description**: Terminate current user session

#### Request
**Method**: POST
**URL**: `/api/auth/signout`
**Headers**:
- `Authorization: Bearer {jwt_token}`

#### Responses

**Success Response (200 OK)**
```json
{
  "success": true
}
```

**Error Response (401 Unauthorized)**
```json
{
  "error": {
    "message": "Not authenticated",
    "code": "NOT_AUTHENTICATED"
  }
}
```

---

## User Profile Endpoints

### GET /api/auth/user
**Description**: Retrieve current user profile information

#### Request
**Method**: GET
**URL**: `/api/auth/user`
**Headers**:
- `Authorization: Bearer {jwt_token}`

#### Responses

**Success Response (200 OK)**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "emailVerified": false,
  "createdAt": "2026-02-06T10:30:00Z",
  "updatedAt": "2026-02-06T10:30:00Z",
  "profile": {
    "name": "User Name"
  }
}
```

### PUT /api/auth/user
**Description**: Update current user profile information

#### Request
**Method**: PUT
**URL**: `/api/auth/user`
**Headers**:
- `Content-Type: application/json`
- `Authorization: Bearer {jwt_token}`

**Body**:
```json
{
  "name": "Updated Name",
  "email": "newemail@example.com"
}
```

#### Responses

**Success Response (200 OK)**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "newemail@example.com",
  "emailVerified": false,
  "createdAt": "2026-02-06T10:30:00Z",
  "updatedAt": "2026-02-06T11:45:00Z"
}
```

## Error Handling Requirements

### Standard Error Response Format
All error responses from Better Auth endpoints should follow this format:

```json
{
  "error": {
    "message": "Human-readable error message",
    "code": "STANDARDIZED_ERROR_CODE",
    "timestamp": "2026-02-06T10:30:00Z"
  }
}
```

### Error Codes
- `INVALID_EMAIL`: Email format is invalid
- `USER_EXISTS`: Attempt to create duplicate account
- `INVALID_CREDENTIALS`: Signin credentials are incorrect
- `PASSWORD_WEAK`: Password does not meet complexity requirements
- `RATE_LIMITED`: Too many requests from same IP/device
- `NOT_AUTHENTICATED`: Action requires authentication
- `FORBIDDEN`: User lacks permission for requested action
- `INTERNAL_ERROR`: Unexpected server error occurred
- `VALIDATION_ERROR`: Request validation failed
- `DATABASE_ERROR`: Database operation failed

## Security Requirements

1. Passwords must never be returned in any API response
2. JWT tokens must be securely signed and properly validated
3. Session information must include appropriate expiration data
4. Rate limiting must be enforced on authentication endpoints
5. Input validation must be performed on all user-provided data
6. Error messages should not expose sensitive system information
7. All communications must use HTTPS in production

## Performance Requirements

- Authentication operations should complete within 2 seconds
- Error responses should be returned within 1 second
- Session validation should be efficient and scalable