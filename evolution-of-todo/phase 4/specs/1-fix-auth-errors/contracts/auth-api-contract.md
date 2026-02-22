# API Contract: Authentication Endpoints

**Feature**: Frontend-Backend Authentication Connection
**Date**: 2026-02-06
**Version**: 1.0

## Overview
This document defines the API contracts for authentication endpoints that the frontend communicates with. These contracts ensure proper integration between the Next.js frontend and FastAPI backend authentication systems.

## Authentication Endpoints

### POST /api/v1/auth/signup
**Description**: Register a new user account

#### Request
**Method**: POST
**URL**: `/api/v1/auth/signup`
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
- `password`: String, minimum length requirements applied by backend

#### Responses

**Success Response (200 OK)**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com"
  }
}
```

**Error Response (400 Bad Request)**
```json
{
  "detail": "Email already registered",
  "error_code": "BAD_REQUEST",
  "timestamp": "2026-02-06T10:30:00Z"
}
```

**Error Response (422 Unprocessable Entity)**
```json
{
  "detail": "Validation error details",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2026-02-06T10:30:00Z"
}
```

**Error Response (500 Internal Server Error)**
```json
{
  "detail": "An error occurred during signup",
  "error_code": "SERVER_ERROR",
  "timestamp": "2026-02-06T10:30:00Z"
}
```

---

### POST /api/v1/auth/signin
**Description**: Authenticate an existing user

#### Request
**Method**: POST
**URL**: `/api/v1/auth/signin`
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
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com"
  }
}
```

**Error Response (401 Unauthorized)**
```json
{
  "detail": "Invalid email or password",
  "error_code": "AUTH_001",
  "timestamp": "2026-02-06T10:30:00Z"
}
```

**Error Response (422 Unprocessable Entity)**
```json
{
  "detail": "Validation error details",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2026-02-06T10:30:00Z"
}
```

**Error Response (500 Internal Server Error)**
```json
{
  "detail": "An error occurred during signin",
  "error_code": "SERVER_ERROR",
  "timestamp": "2026-02-06T10:30:00Z"
}
```

---

## Protected Task Endpoints

### Authentication for All Task Operations
**Requirement**: All task endpoints require JWT authentication

**Header**: `Authorization: Bearer {access_token}`

**Error Response (401 Unauthorized)**
```json
{
  "detail": "Not authenticated",
  "error_code": "AUTH_001",
  "timestamp": "2026-02-06T10:30:00Z"
}
```

**Error Response (403 Forbidden)**
```json
{
  "detail": "Access forbidden",
  "error_code": "AUTH_002",
  "timestamp": "2026-02-06T10:30:00Z"
}
```

## Frontend Implementation Contract

### Token Storage
- **Location**: `localStorage.auth_token`
- **Format**: JWT token string
- **Usage**: Include in Authorization header as `Bearer {token}` for protected requests

### Error Handling
- Network errors should display "Network error: Unable to connect to authentication server"
- Specific backend errors should display the `detail` field from the response
- Validation errors should display user-friendly messages

### Success Redirects
- After successful signup: redirect to `/dashboard`
- After successful signin: redirect to `/dashboard`

## Security Requirements

1. Passwords must never be stored or cached on the frontend
2. JWT tokens must be securely stored and cleared on logout
3. All communication must use HTTPS in production
4. Token expiration must be handled gracefully