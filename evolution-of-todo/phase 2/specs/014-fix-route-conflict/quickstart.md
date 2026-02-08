# Quickstart Guide: Next.js Route Conflict Resolution

**Feature**: Fix Next.js API Route Conflict
**Date**: 2026-02-06

## Overview
This guide provides instructions for resolving the Next.js API route conflict between `/api/tasks/route.ts` and `/api/tasks/[[...path]]/route.ts`. The conflict occurs because both routes attempt to handle the same path pattern, which Next.js prohibits.

## Prerequisites
- Node.js (18.x or higher)
- Next.js 16+
- Access to frontend directory structure

## Setup Instructions

### 1. Identify Conflicting Routes
Check for the presence of both route files:
- `frontend/app/api/tasks/route.ts` - The direct implementation route (TO BE REMOVED)
- `frontend/app/api/tasks/[[...path]]/route.ts` - The proxy route (TO BE KEPT)

### 2. Backup Current Route Files (Optional)
Before making changes, you may want to backup the current files:
```bash
cd frontend/app/api/tasks/
cp route.ts route.ts.backup  # Backup the conflicting route
```

### 3. Remove Conflicting Route
Delete the direct implementation route that's causing the conflict:
```bash
rm frontend/app/api/tasks/route.ts
```

### 4. Verify Remaining Proxy Route
Ensure the proxy route exists and is properly configured:
- Path: `frontend/app/api/tasks/[[...path]]/route.ts`
- Purpose: Proxies all `/api/tasks/*` requests to FastAPI backend
- Configuration: Should point to `BACKEND_URL` environment variable

### 5. Environment Configuration
Verify that the proxy route has proper environment configuration:
```env
# In frontend/.env.local
BACKEND_URL=http://localhost:8000  # FastAPI backend URL
```

## Running the Application

### Start Next.js Development Server
```bash
cd frontend
npm run dev
```

The server should now start without the "route specificity" error.

## Testing the Fix

### 1. Verify Server Starts
- Run `npm run dev` in the frontend directory
- Server should start without routing conflict errors
- No "same specificity" error should appear

### 2. Test API Route Access
- Visit `http://localhost:3000/api/tasks` - should proxy to FastAPI
- Visit `http://localhost:3000/api/tasks/123` - should proxy to FastAPI
- All `/api/tasks/*` paths should route correctly

### 3. Test Authentication Continuity
- Verify that Better Auth endpoints continue to work
- Test signup and signin functionality
- Ensure no authentication functionality was affected by route removal

### 4. Test Task API Functionality
- Make requests to task endpoints through Next.js proxy
- Verify GET, POST, PUT, PATCH, DELETE operations work
- Ensure responses come back correctly from FastAPI backend

## Troubleshooting

### Common Issues

**Issue**: Next.js server still reports routing conflict after removing route.ts
**Solution**: Clear Next.js cache and restart
```bash
rm -rf .next
npm run dev
```

**Issue**: API requests return 404 after route removal
**Solution**: Verify the proxy route at `frontend/app/api/tasks/[[...path]]/route.ts` exists and is properly configured

**Issue**: Environment variables not working
**Solution**: Ensure BACKEND_URL is set in frontend/.env.local and points to correct FastAPI backend

**Issue**: Authentication endpoints broken
**Solution**: Verify Better Auth endpoints are at `frontend/app/api/auth/[[...auth]]/route.ts` and are unaffected by task route changes

### Verification Commands

```bash
# Check for remaining conflicting route
ls -la frontend/app/api/tasks/

# Verify proxy route exists
ls -la frontend/app/api/tasks/[[...path]]/

# Check if server starts without errors
cd frontend && npm run dev
```

## Expected Results

After applying the fix:
- ✅ Next.js development server starts without routing conflict errors
- ✅ `/api/tasks/*` requests are properly proxied to FastAPI backend
- ✅ Better Auth authentication functionality remains intact
- ✅ All task API operations work through the proxy
- ✅ No duplicate or overlapping routes exist

## Next Steps

1. Test the application thoroughly to ensure all functionality works
2. Verify that no other routes have similar conflicts
3. Ensure all environment variables are properly configured for proxying
4. Test the application in a production-like environment