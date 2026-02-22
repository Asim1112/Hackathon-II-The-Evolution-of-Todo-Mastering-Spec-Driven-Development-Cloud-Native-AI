---
id: 74
title: Fix Signup Failed to Fetch in Kubernetes
stage: general
date: 2026-02-21
surface: agent
model: claude-sonnet-4-6
feature: none
branch: main
user: Asim
command: "Diagnose and fix signup Failed to fetch error in Minikube deployment"
labels: ["kubernetes","minikube","better-auth","auth-client","docker","helm","signup","failed-to-fetch","NEXT_PUBLIC"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - frontend/lib/auth-client.ts
  - frontend-chart/values.yaml
tests:
  - manual: signup flow on http://127.0.0.1:63805/
---

## Prompt

User described current situation:
- minikube start → kubectl is configured to use minikube cluster
- kubectl get pods shows: todo-backend 0/1 Running (3 restarts, 21h old), todo-frontend 1/1 Running (1 restart, 24h old)
- minikube service todo-frontend → app accessible at http://127.0.0.1:63805/
- Attempting Signup (filling email/password) → error: "Failed to fetch"

## Response snapshot

Diagnosed three root causes via file inspection of:
- frontend/lib/auth-client.ts
- frontend/Dockerfile
- frontend-chart/values.yaml
- frontend/lib/auth-server.ts

**Root Cause 1 (direct cause of "Failed to fetch"):**
`auth-client.ts:4` uses `process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000"`.
Since `NEXT_PUBLIC_APP_URL` was never set as a Docker build ARG, the fallback `"http://localhost:3000"` is baked into the Next.js production bundle. Browser sends auth requests to `http://localhost:3000/api/auth/...` → nothing there → "Failed to fetch".

**Root Cause 2 (secondary — auth DB failure):**
`frontend-chart/values.yaml` secrets.DATABASE_URL was set to placeholder `postgresql://user:password@postgres:5432/todoapp`. Better Auth server uses this to connect to Neon — would fail on any actual auth query.

**Root Cause 3 (tertiary — BETTER_AUTH_BASE_URL wrong):**
`frontend-chart/values.yaml` env.BETTER_AUTH_BASE_URL was `http://localhost:30000` — wrong port, should match the minikube tunnel URL.

**Fixes applied:**

1. `frontend/lib/auth-client.ts` — Changed baseURL to use `window.location.origin` at runtime (no more hardcoded localhost:3000):
   ```ts
   baseURL: process.env.NEXT_PUBLIC_APP_URL || (typeof window !== "undefined" ? window.location.origin : ""),
   ```

2. `frontend-chart/values.yaml` — Updated DATABASE_URL and NEON_DATABASE_URL to real Neon PostgreSQL URL (same as backend-chart).

3. `frontend-chart/values.yaml` — Updated BETTER_AUTH_BASE_URL to `http://127.0.0.1:63805`.

**Rebuild required** because NEXT_PUBLIC_ vars are baked at build time. Commands provided:
```
docker build -t todo-frontend ./frontend
minikube image load todo-frontend
helm upgrade todo-frontend ./frontend-chart
kubectl rollout restart deployment/todo-frontend
minikube service todo-frontend
```

## Outcome

- ✅ Impact: Fixes "Failed to fetch" on signup. Auth client now uses dynamic window.location.origin so it works regardless of which tunnel port minikube assigns.
- 🧪 Tests: Manual - attempt signup at the new tunnel URL after rebuild and deployment restart.
- 📁 Files: frontend/lib/auth-client.ts (1 line changed), frontend-chart/values.yaml (DATABASE_URL + BETTER_AUTH_BASE_URL updated)
- 🔁 Next prompts: After successful signup, test login flow and todo CRUD. If BETTER_AUTH_BASE_URL needs updating next session, use: helm upgrade todo-frontend ./frontend-chart --set env.BETTER_AUTH_BASE_URL=http://127.0.0.1:<new-port>
- 🧠 Reflection: NEXT_PUBLIC_ variables in Next.js are a common pitfall in containerized deployments — they must be set at Docker build time, not injected at runtime via k8s secrets. The fix using window.location.origin avoids this class of issue entirely by making auth self-discovering.

## Evaluation notes (flywheel)

- Failure modes observed: NEXT_PUBLIC_ baked-in URL mismatch; placeholder DATABASE_URL in frontend Helm chart not updated when backend was fixed.
- Graders run and results (PASS/FAIL): N/A (pending user rebuild and test)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): If signup still fails after rebuild, check frontend pod logs: kubectl logs <todo-frontend-pod> for auth errors.
