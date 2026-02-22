# Data Model: Next.js Route Conflict Resolution

**Feature**: Fix Next.js API Route Conflict
**Date**: 2026-02-06

## Overview
This data model describes the routing structure needed to resolve the conflict between duplicate Next.js API routes. The issue involves two routes with the same specificity: `/api/tasks` and `/api/tasks/[[...path]]`.

## Route Structure Before Fix

### Conflicting Routes
- **Route 1**: `frontend/app/api/tasks/route.ts` (direct route implementation)
- **Route 2**: `frontend/app/api/tasks/[[...path]]/route.ts` (optional catch-all route)
- **Conflict**: Next.js sees both routes as having same specificity and throws an error

### Route Behavior
- Route 1 was likely attempting to implement task functionality directly in Next.js
- Route 2 was attempting to proxy all `/api/tasks/*` requests to FastAPI backend
- Both routes tried to handle requests at `/api/tasks`, causing the conflict

## Route Structure After Fix

### Valid Route Only
- **Route**: `frontend/app/api/tasks/[[...path]]/route.ts` (optional catch-all route)
- **Function**: Proxy all `/api/tasks/*` requests to FastAPI backend
- **Pattern**: `[[...path]]` captures all paths under `/api/tasks`

### Removed Route
- **Route**: `frontend/app/api/tasks/route.ts` (removed completely)
- **Function**: No longer exists, eliminating the conflict

## API Request Flow

### Before Fix (Broken)
```
User request -> Next.js router -> CONFLICT (same specificity) -> ERROR
```

### After Fix (Working)
```
User request to /api/tasks/*
    ↓
Next.js router with [[...path]]
    ↓
Proxy handler in [[...path]]/route.ts
    ↓
Forwarded to BACKEND_URL (FastAPI)
    ↓
FastAPI processes request
    ↓
Response returned to user
```

## Proxy Data Structure

### Proxy Request
**Description**: Structure of requests forwarded from Next.js to FastAPI

**Components**:
- **basePath**: `/api/tasks`
- **pathParams**: Captured by `[[...path]]` pattern
- **headers**: Forwarded from original request with authorization if present
- **method**: HTTP method (GET, POST, PUT, PATCH, DELETE)
- **body**: Request body content if applicable

### Proxy Response
**Description**: Structure of responses returned from FastAPI via Next.js proxy

**Components**:
- **statusCode**: Status code from FastAPI backend
- **headers**: Headers from FastAPI backend
- **body**: Response content from FastAPI backend

## Configuration Data

### Environment Variables
- **BACKEND_URL**: Base URL for FastAPI backend (e.g., `http://localhost:8000`)
- **Required for**: Proxy functionality to forward requests to correct backend

### Route Configuration
- **Pattern**: `[[...path]]` - Next.js optional catch-all route parameter
- **Behavior**: Matches all paths under the parent route
- **Usage**: Captures all sub-paths under `/api/tasks`

## Security Data Considerations

### Authentication Preservation
- Better Auth tokens should be preserved and forwarded to FastAPI backend
- Authorization headers should be passed through the proxy
- Session information should remain intact during proxy operation

### Request Validation
- Input validation should be handled by FastAPI backend
- Next.js proxy should pass through requests without modification
- Security headers should be preserved during forwarding