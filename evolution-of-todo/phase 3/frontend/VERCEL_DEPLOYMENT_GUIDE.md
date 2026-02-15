# Vercel Deployment Guide - Next.js Frontend

## ✅ Pre-Deployment Fixes Completed

All critical issues have been resolved:

1. **Fixed Import Error** - `app/api/tasks/[[...path]]/route.ts:2`
   - Changed from: `import { auth } from "../../auth/[...all]/route"`
   - Changed to: `import { auth } from "@/lib/auth-server"`

2. **Fixed Hardcoded Localhost URLs** - `next.config.ts`
   - Replaced all `http://127.0.0.1:8000` with environment variable
   - Now uses: `process.env.BACKEND_API_URL || 'https://asim1112-todo-ai-chatbot.hf.space'`

3. **Fixed TypeScript Errors** - `lib/chat-api.ts` and `lib/api-client.ts`
   - Replaced `any` types with `unknown` and proper type assertions
   - Fixed null vs undefined type issues

4. **Installed Missing Types** - Added `@types/ws` for WebSocket support

5. **Build Verification** - ✅ Production build successful

---

## 🔐 Required Environment Variables for Vercel

### Step 1: Generate a New Production Secret

Before deployment, generate a new `BETTER_AUTH_SECRET`:

```bash
openssl rand -base64 32
```

Copy the output - you'll need it for Vercel.

### Step 2: Environment Variables to Add in Vercel Dashboard

Navigate to: **Project Settings → Environment Variables**

Add these variables for **Production**, **Preview**, and **Development** environments:

| Variable Name | Value | Notes |
|--------------|-------|-------|
| `BETTER_AUTH_SECRET` | `<output-from-openssl>` | ⚠️ CRITICAL - Generate new, don't reuse local |
| `DATABASE_URL` | `postgresql://neondb_owner:npg_a2dw3hMcYBiW@ep-fragrant-cake-ah0vrbvz-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require` | Your Neon PostgreSQL connection |
| `NEON_DATABASE_URL` | `<same as DATABASE_URL>` | Backup reference |
| `BACKEND_API_URL` | `https://asim1112-todo-ai-chatbot.hf.space` | FastAPI backend URL |
| `NEXT_PUBLIC_API_URL` | `https://asim1112-todo-ai-chatbot.hf.space` | Client-side API URL |
| `NEXT_PUBLIC_APP_URL` | `https://your-app.vercel.app` | ⚠️ Update after first deployment |

**Important Notes:**
- `NEXT_PUBLIC_*` variables are exposed to the browser
- After first deployment, update `NEXT_PUBLIC_APP_URL` with your actual Vercel URL
- Keep `DATABASE_URL` and `BETTER_AUTH_SECRET` secret

---

## 🚀 Vercel Deployment Steps (Manual UI)

### Step 1: Initial Setup

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click **"Add New..."** → **"Project"**
3. Import your Git repository:
   - If using GitHub: Click **"Import Git Repository"**
   - Select your repository: `evolution-of-todo`
   - Click **"Import"**

### Step 2: Configure Project Settings

1. **Framework Preset**: Next.js (should auto-detect)
2. **Root Directory**: Click **"Edit"** and set to: `phase 3/frontend`
3. **Build Command**: `npm run build` (default)
4. **Output Directory**: `.next` (default)
5. **Install Command**: `npm install` (default)

### Step 3: Add Environment Variables

1. Expand **"Environment Variables"** section
2. Add each variable from the table above:
   - Click **"Add"** for each variable
   - Enter **Name** and **Value**
   - Select environments: **Production**, **Preview**, **Development**
   - Click **"Add"** to confirm

**⚠️ CRITICAL**: For `NEXT_PUBLIC_APP_URL`, initially use a placeholder like `https://placeholder.vercel.app`. You'll update this after deployment.

### Step 4: Deploy

1. Click **"Deploy"** button
2. Wait for build to complete (2-5 minutes)
3. Once deployed, you'll see: **"Congratulations! Your project has been deployed."**
4. Copy your deployment URL (e.g., `https://your-app-abc123.vercel.app`)

### Step 5: Update Environment Variables

1. Go to **Project Settings** → **Environment Variables**
2. Find `NEXT_PUBLIC_APP_URL`
3. Click **"Edit"** and update with your actual Vercel URL
4. Click **"Save"**
5. Go to **Deployments** tab
6. Click **"..."** on the latest deployment → **"Redeploy"**
7. Check **"Use existing Build Cache"** → Click **"Redeploy"**

---

## 🔧 Backend CORS Configuration (CRITICAL)

Your FastAPI backend at `https://asim1112-todo-ai-chatbot.hf.space` **MUST** allow requests from your Vercel domain.

### Required FastAPI Configuration

Add this to your FastAPI backend (usually in `main.py` or `app.py`):

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-app.vercel.app",  # Replace with your actual Vercel URL
        "https://your-app-*.vercel.app",  # Allow preview deployments
        "http://localhost:3000",  # Keep for local development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
```

**⚠️ IMPORTANT**:
- Replace `your-app` with your actual Vercel project name
- The wildcard `your-app-*.vercel.app` allows preview deployments to work
- Redeploy your FastAPI backend after making this change

### How to Update Backend on Hugging Face Spaces

1. Go to your Hugging Face Space: `https://huggingface.co/spaces/asim1112/todo-ai-chatbot`
2. Edit your `app.py` or `main.py` file
3. Add the CORS configuration above
4. Commit changes - Space will automatically rebuild

---

## ✅ Post-Deployment Verification Checklist

### 1. Test Homepage
- [ ] Visit your Vercel URL
- [ ] Homepage loads without errors
- [ ] No console errors in browser DevTools (F12)

### 2. Test Authentication
- [ ] Click "Sign Up" or "Sign In"
- [ ] Create a new account or sign in
- [ ] Verify you're redirected to dashboard after login
- [ ] Check browser cookies - should see `better-auth.session_token`

### 3. Test Database Connection
- [ ] After signing in, check Vercel logs for: `[AUTH] Initializing Better Auth with database connection`
- [ ] No database connection errors
- [ ] User should be saved in Neon database

### 4. Test Backend API Connection
- [ ] Go to `/dashboard` page
- [ ] Open browser DevTools → Network tab
- [ ] Try creating a task or using chat
- [ ] Verify API calls to `/api/v1/*` or `/api/:userId/chat` succeed
- [ ] Check response status codes (should be 200, not 403/404/500)

### 5. Test CORS
- [ ] In Network tab, check for CORS errors
- [ ] Look for: `Access-Control-Allow-Origin` header in responses
- [ ] If you see CORS errors, update backend configuration (see above)

### 6. Check Vercel Logs
- [ ] Go to Vercel Dashboard → Your Project → **Logs** tab
- [ ] Filter by **Errors** to see any runtime issues
- [ ] Common issues:
  - Missing environment variables
  - Database connection failures
  - Backend API timeouts

---

## 🐛 Common Issues & Solutions

### Issue 1: "Unauthorized" or 401 Errors
**Cause**: Better Auth not configured properly
**Solution**:
- Verify `BETTER_AUTH_SECRET` is set in Vercel
- Check `DATABASE_URL` is correct
- Redeploy after adding variables

### Issue 2: CORS Errors in Browser Console
**Cause**: Backend doesn't allow requests from Vercel domain
**Solution**:
- Update FastAPI CORS configuration (see above)
- Redeploy backend on Hugging Face Spaces

### Issue 3: "Failed to fetch" or Network Errors
**Cause**: Backend URL incorrect or backend is down
**Solution**:
- Verify `BACKEND_API_URL` is set correctly
- Test backend directly: `curl https://asim1112-todo-ai-chatbot.hf.space/health`
- Check Hugging Face Spaces status

### Issue 4: Database Connection Errors
**Cause**: Neon database credentials incorrect or IP not allowed
**Solution**:
- Verify `DATABASE_URL` includes `?sslmode=require&channel_binding=require`
- Check Neon dashboard for connection issues
- Ensure Neon database is not paused

### Issue 5: Environment Variables Not Working
**Cause**: Variables not applied to deployment
**Solution**:
- After adding/changing variables, always **redeploy**
- Check variable names match exactly (case-sensitive)
- `NEXT_PUBLIC_*` variables require rebuild to take effect

---

## 📊 Monitoring & Maintenance

### Vercel Dashboard Tabs to Monitor

1. **Deployments**: See all deployments and their status
2. **Logs**: Real-time logs for debugging
3. **Analytics**: Traffic and performance metrics (if enabled)
4. **Settings → Environment Variables**: Manage secrets

### Recommended Next Steps

1. **Set up Custom Domain** (optional):
   - Go to **Settings** → **Domains**
   - Add your custom domain
   - Update `NEXT_PUBLIC_APP_URL` to your custom domain
   - Redeploy

2. **Enable Preview Deployments**:
   - Already enabled by default
   - Every Git branch gets a preview URL
   - Test changes before merging to main

3. **Set up Monitoring**:
   - Consider adding Sentry for error tracking
   - Use Vercel Analytics for performance monitoring

---

## 🎯 Quick Reference: URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend (Vercel) | `https://your-app.vercel.app` | Your deployed Next.js app |
| Backend (HF Spaces) | `https://asim1112-todo-ai-chatbot.hf.space` | FastAPI backend |
| Database (Neon) | `ep-fragrant-cake-ah0vrbvz-pooler.c-3.us-east-1.aws.neon.tech` | PostgreSQL database |
| Vercel Dashboard | `https://vercel.com/dashboard` | Manage deployments |

---

## 📝 Summary

**What Was Fixed:**
- ✅ Import errors in route handlers
- ✅ Hardcoded localhost URLs replaced with environment variables
- ✅ TypeScript type errors resolved
- ✅ Missing type definitions installed
- ✅ Production build verified successful

**What You Need to Do:**
1. Generate new `BETTER_AUTH_SECRET` with OpenSSL
2. Add all environment variables in Vercel dashboard
3. Deploy project from Vercel UI
4. Update `NEXT_PUBLIC_APP_URL` with actual Vercel URL
5. Update CORS configuration in FastAPI backend
6. Test all functionality using the verification checklist

**Estimated Time:** 15-20 minutes for initial deployment + backend CORS update

---

Good luck with your deployment! 🚀
