# QuickStart Guide: Better-Auth Network Connectivity Fix

**Feature**: Fix Better-Auth Signup Network Connectivity
**Branch**: `011-fix-signup-network-bridge`
**Date**: 2026-02-05
**Guide Version**: 1.0

## Overview

This quickstart guide provides immediate implementation steps to fix the "TypeError: Failed to fetch" error during signup by establishing proper network connectivity between the Better-Auth frontend client and backend service.

## Immediate Action Steps

### Step 1: Configure Next.js Proxy (5 minutes)
Update `next.config.js` to add proxy configuration:

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/auth/:path*",
        destination: "http://127.0.0.1:8000/api/auth/:path*",
      },
    ];
  },
};

module.exports = nextConfig;
```

### Step 2: Update Better-Auth Client (3 minutes)
Modify `frontend/lib/auth.ts` to use the proxy endpoint:

```typescript
import { createAuthClient } from "@better-auth/client";

export const authClient = createAuthClient({
  baseURL: "/api/auth",  // Using proxy route instead of direct backend
  // Other client options...
});
```

### Step 3: Verify Backend Server (2 minutes)
Ensure the FastAPI backend is running on `http://127.0.0.1:8000` and authentication endpoints are accessible.

### Step 4: Configure Backend CORS (3 minutes)
In your FastAPI backend, ensure CORS middleware allows requests from `http://localhost:3000`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Implementation Details

### Proxy Configuration Purpose
The Next.js proxy configuration forwards requests from the frontend to the backend, avoiding CORS issues and enabling proper authentication flow. The `/api/auth/*` routes are redirected to the FastAPI backend.

### Client Configuration
The Better-Auth client should use the proxy route (`/api/auth`) as its base URL instead of the direct backend URL. This ensures all authentication requests go through the Next.js proxy layer.

### Error Prevention
- Verify the backend is running on the expected port (127.0.0.1:8000)
- Ensure proxy configuration matches backend endpoint structure
- Test network connectivity before attempting signup

## Verification Checklist

### Pre-Implementation
- [ ] FastAPI backend running on http://127.0.0.1:8000
- [ ] Next.js frontend running on http://localhost:3000
- [ ] Authentication endpoints accessible on backend

### Post-Implementation
- [ ] Proxy configuration added to next.config.js
- [ ] Better-Auth client uses proxy URL
- [ ] CORS configured to allow localhost:3000
- [ ] Signup form no longer throws "TypeError: Failed to fetch"

## Common Issues & Solutions

### Issue: Proxy not working
**Solution**: Check that your Next.js app is restarted after changing next.config.js

### Issue: Backend endpoints not accessible
**Solution**: Verify backend server is running and authentication routes are properly defined

### Issue: Still getting CORS errors
**Solution**: Double-check that CORS configuration in backend allows localhost:3000

## Testing Commands

### Start Frontend
```bash
cd frontend
npm run dev
```

### Start Backend
```bash
cd backend
uvicorn main:app --host 127.0.0.1 --port 8000
```

### Test Authentication Request
Try signing up with a test account to verify the network connection is working.

## Success Indicators

### Immediate Success
- [ ] Next.js proxy configuration added
- [ ] Better-Auth client configured with proxy URL
- [ ] Backend CORS properly configured

### Verification Success
- [ ] No "TypeError: Failed to fetch" during signup
- [ ] Network requests reach the backend successfully
- [ ] Authentication flow completes properly

## Rollback Plan

If implementation causes issues:

1. Remove proxy configuration from next.config.js
2. Restore original Better-Auth client configuration
3. Temporarily disable CORS restrictions on backend
4. Restart both frontend and backend servers