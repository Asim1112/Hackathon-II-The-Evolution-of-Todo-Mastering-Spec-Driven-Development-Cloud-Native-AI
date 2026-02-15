# API Contract: Next.js Route Proxy for FastAPI Integration

**Feature**: Fix Next.js API Route Conflict
**Date**: 2026-02-06
**Version**: 1.0

## Overview
This document defines the API contract for the Next.js proxy that forwards `/api/tasks/*` requests to the FastAPI backend. This proxy resolves the route conflict by ensuring only one route handles the `/api/tasks` path pattern.

## Proxy Endpoints

### GET /api/tasks/[[...path]]
**Description**: Proxy endpoint that forwards GET requests from Next.js to FastAPI backend

#### Request
**Method**: GET
**URL**: `/api/tasks/[[...path]]` (where [[...path]] captures the remaining path)
**Headers**:
- Forwarded from original request
- Authorization header (if present)
- Content-Type (if applicable)

**Parameters**:
- **path**: Dynamic path parameter captured by Next.js route pattern
- Example: If user requests `/api/tasks/123`, path captures `["123"]`
- Example: If user requests `/api/tasks?limit=10`, path is empty but query parameters are preserved

#### Responses

**Success Response (200 OK)**
```
Status Code: 200
Content-Type: application/json
Body: Response from FastAPI backend
```

**Success Response (201 Created)**
```
Status Code: 201
Content-Type: application/json
Body: Response from FastAPI backend
```

**Error Response (400 Bad Request)**
```
Status Code: 400
Content-Type: application/json
Body: Error response from FastAPI backend
```

**Error Response (401 Unauthorized)**
```
Status Code: 401
Content-Type: application/json
Body: Error response from FastAPI backend
```

**Error Response (404 Not Found)**
```
Status Code: 404
Content-Type: application/json
Body: Error response from FastAPI backend
```

**Error Response (500 Internal Server Error)**
```
Status Code: 500
Content-Type: application/json
Body: Error response from FastAPI backend
```

---

### POST /api/tasks/[[...path]]
**Description**: Proxy endpoint that forwards POST requests from Next.js to FastAPI backend

#### Request
**Method**: POST
**URL**: `/api/tasks/[[...path]]` (where [[...path]] captures the remaining path)
**Headers**:
- Forwarded from original request
- Authorization header (if present)
- Content-Type: application/json
- All other headers preserved

**Body**:
- Raw request body forwarded to FastAPI backend
- JSON payload for creating new resources

#### Responses
Same as GET method but appropriate for POST-specific responses

---

### PUT /api/tasks/[[...path]]
**Description**: Proxy endpoint that forwards PUT requests from Next.js to FastAPI backend

#### Request
**Method**: PUT
**URL**: `/api/tasks/[[...path]]` (where [[...path]] captures the remaining path)
**Headers**:
- Forwarded from original request
- Authorization header (if present)
- Content-Type: application/json
- All other headers preserved

**Body**:
- Raw request body forwarded to FastAPI backend
- JSON payload for updating resources

#### Responses
Same as GET method but appropriate for PUT-specific responses

---

### PATCH /api/tasks/[[...path]]
**Description**: Proxy endpoint that forwards PATCH requests from Next.js to FastAPI backend

#### Request
**Method**: PATCH
**URL**: `/api/tasks/[[...path]]` (where [[...path]] captures the remaining path)
**Headers**:
- Forwarded from original request
- Authorization header (if present)
- Content-Type: application/json
- All other headers preserved

**Body**:
- Raw request body forwarded to FastAPI backend
- JSON payload for partial updates

#### Responses
Same as GET method but appropriate for PATCH-specific responses

---

### DELETE /api/tasks/[[...path]]
**Description**: Proxy endpoint that forwards DELETE requests from Next.js to FastAPI backend

#### Request
**Method**: DELETE
**URL**: `/api/tasks/[[...path]]` (where [[...path]] captures the remaining path)
**Headers**:
- Forwarded from original request
- Authorization header (if present)
- All other headers preserved

**Body**: N/A for DELETE requests

#### Responses
Same as GET method but appropriate for DELETE-specific responses

## Proxy Configuration Contract

### Environment Requirements
- **BACKEND_URL**: Environment variable specifying the FastAPI backend URL
  - Example: `http://localhost:8000` or `https://prod-api.example.com`
  - Required for proper request forwarding

### Request Forwarding Rules
1. **Headers**: All headers from original request are forwarded to backend
2. **Body**: Request body is passed through unchanged
3. **Method**: HTTP method is preserved in proxy request
4. **Query Parameters**: Query parameters are forwarded to backend
5. **Path**: Captured path segments are appended to backend endpoint

### Response Handling Rules
1. **Status Codes**: Backend status codes are returned as-is
2. **Headers**: Backend headers are returned as-is
3. **Body**: Backend response body is returned as-is
4. **Error Handling**: Backend error responses are propagated to client

## Integration Contract

### Next.js to FastAPI Integration
- Next.js acts as pure proxy layer with no business logic
- All request processing happens on FastAPI backend
- Authentication is handled by Better Auth in Next.js but validated by FastAPI
- No data transformation in proxy layer

### Error Propagation
- FastAPI errors (4xx, 5xx) are returned directly to client
- Proxy-level errors (network issues, etc.) are returned as 500
- No masking of backend error messages

## Authentication Integration

### Authorization Header Handling
- Authorization header with Bearer token is forwarded to FastAPI backend
- Better Auth validates session in Next.js before forwarding
- FastAPI validates JWT token from authorization header

### Session Management
- Next.js manages Better Auth sessions
- FastAPI validates tokens passed through authorization header
- No separate session management in FastAPI

## Performance Considerations

### Response Time
- Proxy overhead should be minimal (<50ms)
- Request forwarding should be efficient
- No unnecessary processing in proxy layer

### Connection Management
- Keep-alive connections should be used when possible
- Proxy should handle connection pooling appropriately
- Timeout handling should match backend expectations