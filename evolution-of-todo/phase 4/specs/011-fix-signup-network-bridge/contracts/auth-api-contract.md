# API Contract: Authentication Service Interface

**Feature**: Fix Better-Auth Signup Network Connectivity
**Contract Version**: 1.0
**Date**: 2026-02-05
**Status**: Active

## Contract Overview

This API contract defines the interface between the frontend Better-Auth client and the backend authentication service. It specifies the endpoints, request/response formats, and error handling patterns for authentication operations.

## API Endpoints

### Sign Up Endpoint
```
POST /api/auth/sign-up
```

#### Request
- **Headers**:
  - `Content-Type: application/json`
- **Body**:
  ```json
  {
    "email": "string (valid email format)",
    "password": "string (valid password format)"
  }
  ```

#### Success Response (200)
- **Headers**:
  - `Content-Type: application/json`
- **Body**:
  ```json
  {
    "user": {
      "id": "string",
      "email": "string",
      "createdAt": "ISO 8601 timestamp"
    },
    "session": {
      "token": "string (JWT token)",
      "expiresAt": "ISO 8601 timestamp"
    }
  }
  ```

#### Error Responses
- **400 Bad Request**: Invalid input data
  ```json
  {
    "error": "string (error message)",
    "details": "object (validation details)"
  }
  ```
- **409 Conflict**: User already exists
  ```json
  {
    "error": "User with this email already exists"
  }
  ```

### Login Endpoint
```
POST /api/auth/login
```

#### Request
- **Headers**:
  - `Content-Type: application/json`
- **Body**:
  ```json
  {
    "email": "string (valid email format)",
    "password": "string (valid password)"
  }
  ```

#### Success Response (200)
- **Headers**:
  - `Content-Type: application/json`
- **Body**:
  ```json
  {
    "user": {
      "id": "string",
      "email": "string",
      "createdAt": "ISO 8601 timestamp"
    },
    "session": {
      "token": "string (JWT token)",
      "expiresAt": "ISO 8601 timestamp"
    }
  }
  ```

#### Error Responses
- **400 Bad Request**: Invalid input data
  ```json
  {
    "error": "string (error message)",
    "details": "object (validation details)"
  }
  ```
- **401 Unauthorized**: Invalid credentials
  ```json
  {
    "error": "Invalid email or password"
  }
  ```

### Session Verification Endpoint
```
GET /api/auth/session
```

#### Request
- **Headers**:
  - `Authorization: Bearer {token}`
  - `Content-Type: application/json`

#### Success Response (200)
- **Headers**:
  - `Content-Type: application/json`
- **Body**:
  ```json
  {
    "user": {
      "id": "string",
      "email": "string",
      "createdAt": "ISO 8601 timestamp"
    },
    "session": {
      "token": "string (JWT token)",
      "expiresAt": "ISO 8601 timestamp"
    }
  }
  ```

#### Error Responses
- **401 Unauthorized**: Invalid or expired token
  ```json
  {
    "error": "Unauthorized"
  }
  ```

## Network Layer Contract

### Proxy Configuration
The frontend must configure Next.js rewrites to forward `/api/auth/*` requests to the backend:

```
Proxy Rule:
Source: /api/auth/:path*
Destination: http://127.0.0.1:8000/api/auth/:path*
Change Origin: true
```

### CORS Policy
The backend must allow requests from the frontend origin:
- **Allowed Origins**: `http://localhost:3000`
- **Allowed Methods**: `GET, POST, PUT, DELETE, OPTIONS`
- **Allowed Headers**: `Content-Type, Authorization, X-Requested-With`
- **Credentials**: `true`

## Error Handling Contract

### Network Errors
- When the proxy fails to forward a request: `502 Bad Gateway`
- When the backend is unreachable: `503 Service Unavailable`
- Frontend should display: "Unable to connect to authentication service"

### Timeout Policy
- Backend requests should timeout after 30 seconds
- Frontend should implement retry logic with exponential backoff

## Security Contract

### Authentication
- All authentication requests must use HTTPS in production
- Session tokens must be stored securely
- Passwords must not be logged or exposed in client-side code

### Rate Limiting
- Implement rate limiting for authentication endpoints
- Maximum 5 attempts per IP per minute for login/signup

## Version Compatibility

### Client-Server Compatibility
- API version: 1.0
- Client library: Better-Auth 1.4.9
- Protocol: REST over HTTP/HTTPS
- Data format: JSON

## Monitoring Points

### Key Metrics
- Authentication request success rate (>95%)
- Average response time (<1000ms)
- Failed authentication rate (<5%)
- Network error rate (<1%)

### Error Tracking
- Log all 4xx and 5xx responses
- Track user flow through authentication process
- Monitor for security-related anomalies