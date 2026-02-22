# Phase IV — Summary Report
## Evolution of Todo: Cloud-Native AI Chatbot Deployment on Local Kubernetes

---

| Field | Details |
|---|---|
| **Developer** | Asim |
| **Phase** | Phase 4 — Cloud-Native Deployment |
| **Project Path** | `F:\Hackathon II\evolution-of-todo\phase 4` |
| **Date** | February 21, 2026 |
| **Status** | ✅ Successfully Completed |

---

## 1. Phase 4 Objective

The goal of Phase 4 was to transform the Phase 3 AI-powered Todo Chatbot into a **Cloud-Native Application** by deploying it on a local Kubernetes cluster using modern DevOps and AI-assisted tools.

**This phase focused on:**
- Containerization using Docker and Docker AI Agent (Gordon)
- Kubernetes orchestration using Minikube
- Helm Charts for spec-driven deployment
- AI-assisted DevOps using kubectl-ai, Kagent, and Claude CLI
- Secure cloud database integration (Neon PostgreSQL)

This phase simulates a real **production-grade deployment environment** locally.

---

## 2. Technology Stack

### Containerization Layer

| Component | Technology |
|---|---|
| Container Engine | Docker Desktop |
| Docker AI | Gordon (Ask Gordon) |
| Image Registry | Local Docker Images |
| Generated Images | `todo-frontend:v4`, `todo-backend:latest` |

### Orchestration Layer

| Component | Technology |
|---|---|
| Container Orchestration | Kubernetes |
| Local Cluster | Minikube |
| Driver | Docker Driver |
| Cluster Management | kubectl |

### Deployment Layer

| Component | Technology |
|---|---|
| Package Manager | Helm |
| Deployment Method | Helm Charts |
| Charts Created | `backend-chart`, `frontend-chart` |

### AI-Assisted DevOps Layer

| Component | Technology |
|---|---|
| Docker AI | Gordon |
| Kubernetes AI | kubectl-ai |
| Advanced AI Ops | Kagent |
| Spec-Driven Infrastructure | Claude CLI |

### Application Layer

| Component | Technology |
|---|---|
| Frontend | Next.js 16 (React) |
| Backend | FastAPI (Python) |
| Authentication | Better Auth v1.4.18 |
| Database | Neon PostgreSQL (Cloud) |
| AI Chatbot | Cerebras API |
| Task Proxy | Next.js API Routes |

---

## 3. Architecture

```
Browser (http://127.0.0.1:PORT)
         │
         ▼
┌─────────────────────────────┐
│   Minikube Kubernetes       │
│   Cluster (Docker Driver)   │
│                             │
│  ┌──────────────────────┐   │
│  │  Frontend Pod        │   │
│  │  (Next.js : 3000)    │   │
│  │  NodePort: 30000     │   │
│  └──────────┬───────────┘   │
│             │               │
│             ▼               │
│  ┌──────────────────────┐   │
│  │  Backend Pod         │   │
│  │  (FastAPI : 8000)    │   │
│  │  ClusterIP Service   │   │
│  └──────────┬───────────┘   │
│             │               │
└─────────────┼───────────────┘
              │
              ▼
   Neon PostgreSQL (Cloud)
   ep-fragrant-cake-*.neon.tech
```

**Request Flow:**
- Browser → Minikube Tunnel → Frontend Pod (Next.js)
- Frontend → Next.js Rewrites → Backend Pod (FastAPI) via `todo-backend:8000`
- Backend → Neon PostgreSQL (cloud) for data persistence
- Auth requests → Better Auth (server-side in Next.js) → Neon PostgreSQL

---

## 4. Kubernetes Resources Deployed

### Pods
```
todo-backend-...    1/1   Running
todo-frontend-...   1/1   Running
```

### Services
```
todo-backend    ClusterIP   port 8000   (internal only)
todo-frontend   NodePort    port 3000   (exposed on 30000)
```

### Deployments
```
todo-backend    1/1 ready
todo-frontend   1/1 ready
```

### Helm Releases
```
todo-backend    DEPLOYED   backend-chart
todo-frontend   DEPLOYED   frontend-chart (Revision 6)
```

---

## 5. Implementation Steps

### Step 1 — Phase 3 to Phase 4 Transition
Phase 3 project was duplicated into the Phase 4 directory to preserve the original working system and implement cloud-native deployment independently.

### Step 2 — Containerization via Docker AI (Gordon)
Docker AI Agent (Gordon) analyzed the project structure and generated optimized Dockerfiles:
- `frontend/Dockerfile` — Multi-stage Node.js build
- `backend/Dockerfile` — Python FastAPI container

Docker images built:
```
todo-frontend:v4
todo-backend:latest
```

### Step 3 — Kubernetes Cluster Setup (Minikube)
```powershell
minikube start
kubectl get nodes
```
Cluster started using Docker driver. Verified operational.

### Step 4 — Loading Images into Minikube
```powershell
minikube image load todo-backend
minikube image load todo-frontend:v4
```
Local Docker images loaded into Minikube's internal container registry.

> **Key Learning:** Always use versioned tags (`:v2`, `:v3`, `:v4`) when loading images into Minikube. The `:latest` tag is cached and does not reliably update — leading to stale images running in pods.

### Step 5 — Helm Chart Generation (Claude CLI)
Claude CLI was used to generate Helm Charts implementing Spec-Driven Deployment:

**`backend-chart/` contains:**
- Deployment specification
- ClusterIP Service definition
- Kubernetes Secret for DATABASE_URL, JWT_SECRET, CEREBRAS_API_KEY
- ConfigMap for non-sensitive env vars
- Liveness and Readiness probes on `/health`

**`frontend-chart/` contains:**
- Deployment specification
- NodePort Service definition (port 30000)
- Kubernetes Secret for DATABASE_URL, BETTER_AUTH_SECRET
- ConfigMap for BETTER_AUTH_BASE_URL, BETTER_AUTH_TRUSTED_ORIGINS
- Liveness and Readiness probes on `/`

### Step 6 — Deployment via Helm
```powershell
helm install todo-backend ./backend-chart
helm install todo-frontend ./frontend-chart
```

### Step 7 — Application Exposure
```powershell
minikube service todo-frontend
```
App accessible via tunnel at `http://127.0.0.1:PORT`

---

## 6. Issues Encountered and Resolutions

### Issue 1 — Backend CrashLoopBackOff (Original)
**Error:** `psycopg2.OperationalError: could not translate host name "postgres"`

**Cause:** Backend Helm chart had a placeholder DATABASE_URL pointing to a nonexistent local postgres service.

**Fix:** Updated `backend-chart/values.yaml` with real Neon PostgreSQL URL:
```yaml
DATABASE_URL: "postgresql://neondb_owner:...@ep-fragrant-cake-*.neon.tech/neondb?sslmode=require"
```
```powershell
helm upgrade todo-backend ./backend-chart
kubectl delete pod <backend-pod>
```

---

### Issue 2 — Signup "Failed to Fetch"
**Error:** Browser showed "Failed to fetch" when attempting signup.

**Root Cause:** `auth-client.ts` had `http://localhost:3000` baked into the Next.js production bundle as the Better Auth base URL. Since `NEXT_PUBLIC_APP_URL` was never set as a Docker build arg, the fallback was compiled in permanently.

**Fix:** Changed `frontend/lib/auth-client.ts`:
```ts
// Before
baseURL: process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000"

// After
baseURL: process.env.NEXT_PUBLIC_APP_URL ||
  (typeof window !== "undefined" ? window.location.origin : "")
```
Auth client now uses `window.location.origin` dynamically — works regardless of tunnel port.

---

### Issue 3 — Frontend DATABASE_URL Placeholder
**Error:** Better Auth could not initialize database connection on the frontend pod.

**Cause:** `frontend-chart/values.yaml` had a placeholder DATABASE_URL (`postgresql://user:password@postgres:5432/todoapp`) which was never updated after fixing the backend.

**Fix:** Updated `frontend-chart/values.yaml` secrets with the real Neon URL (same as backend).

---

### Issue 4 — "Invalid Origin" from Better Auth
**Error:** `ERROR [Better Auth]: Invalid origin: http://127.0.0.1:PORT`

**Root Cause:** Better Auth v1.4.18 silently ignores the `BETTER_AUTH_BASE_URL` environment variable. Without an explicit `baseURL` passed in code, Better Auth has no trusted origins and rejects all requests.

**Fix:** Explicitly passed `baseURL` and `trustedOrigins` inside `frontend/lib/auth-server.ts`:
```ts
const baseURL = process.env.BETTER_AUTH_BASE_URL || "http://localhost:3000";
const trustedOrigins = process.env.BETTER_AUTH_TRUSTED_ORIGINS
  ? process.env.BETTER_AUTH_TRUSTED_ORIGINS.split(",").map(o => o.trim())
  : [baseURL];

export const auth = betterAuth({
  database: new Pool({ connectionString: databaseUrl }),
  baseURL,
  trustedOrigins,
  ...
});
```

---

### Issue 5 — Minikube Stale Image Cache
**Problem:** After rebuilding the Docker image, the running pod continued using the old image. `kubectl rollout restart` had no effect.

**Root Cause:** `minikube image load todo-frontend:latest` does not reliably replace an existing image with the same tag in Minikube's containerd registry. The pod with `pullPolicy: IfNotPresent` found the old `latest` image and used it.

**Fix:** Switched to versioned image tags for every rebuild:
```powershell
docker build -t todo-frontend:v2 ./frontend   # fix 1
docker build -t todo-frontend:v3 ./frontend   # fix 2
docker build -t todo-frontend:v4 ./frontend   # fix 3
```
Updated `frontend-chart/values.yaml` tag field accordingly for each version.

---

### Issue 6 — Tasks Returning HTTP 500
**Error:** Dashboard showed "Error loading tasks — HTTP error! status: 500"

**Root Cause:** Next.js bakes the `rewrites()` configuration from `next.config.ts` into `.next/routes-manifest.json` at **build time**. Since `BACKEND_URL` was not set during `docker build`, the default `http://localhost:8000` was compiled into the routes manifest. At runtime in Kubernetes, the environment variable `BACKEND_URL=http://todo-backend:8000` was correctly injected by Kubernetes — but the routes manifest already had `localhost:8000`, causing `ECONNREFUSED` on every API request.

**Fix:** Changed the default in `frontend/next.config.ts`:
```ts
// Before
const backendUrl = process.env.BACKEND_URL || "http://localhost:8000";

// After
const backendUrl = process.env.BACKEND_URL || "http://todo-backend:8000";
```
Rebuilt as `todo-frontend:v4`. Kubernetes service name is now baked as the default.

---

## 7. Final Deployment Status

| Feature | Status |
|---|---|
| App accessible in browser | ✅ Working |
| User Signup | ✅ Working |
| User Login | ✅ Working |
| Users saved in Neon DB | ✅ Confirmed |
| Task creation | ✅ Working |
| Task listing | ✅ Working |
| Task completion toggle | ✅ Working |
| Task deletion | ✅ Working |
| AI Chatbot (Cerebras) | ✅ Working (API key injected via helm) |
| Backend health endpoint | ✅ `/health` returning 200 |
| Both pods 1/1 Running | ✅ Confirmed |

---

## 8. Key Learnings from Phase 4

| Learning | Detail |
|---|---|
| `NEXT_PUBLIC_*` vars are build-time | Must be set as Docker build args — runtime k8s env vars have no effect |
| Next.js rewrites are build-time | `routes-manifest.json` is generated at build — use correct defaults in `next.config.ts` |
| Better Auth v1.4.18 ignores env vars | Must pass `baseURL` and `trustedOrigins` explicitly in `betterAuth()` config |
| Minikube `:latest` tag caching | Always use versioned tags (`:v2`, `:v3`) — `:latest` does not reliably update |
| Minikube tunnel port changes | `BETTER_AUTH_BASE_URL` must be updated each session via `helm upgrade --set` |
| Kubernetes secrets for runtime config | Sensitive values (API keys, DB URLs) injected via `helm upgrade --set` — never committed to git |

---

## 9. Session Startup Guide (Every Time)

```powershell
# 1. Ensure Docker Desktop is running

# 2. Navigate to project
cd "F:\Hackathon II\evolution-of-todo\phase 4"

# 3. Start cluster
minikube start

# 4. Verify pods
kubectl get pods
# Both should show 1/1 Running

# 5. Open tunnel (Terminal 1 — keep open)
minikube service todo-frontend
# Note the tunnel port: http://127.0.0.1:XXXXX

# 6. Update auth URL with new port (Terminal 2)
helm upgrade todo-frontend ./frontend-chart `
  --set "env.BETTER_AUTH_BASE_URL=http://127.0.0.1:XXXXX" `
  --set "env.BETTER_AUTH_TRUSTED_ORIGINS=http://127.0.0.1:XXXXX"

kubectl rollout restart deployment/todo-frontend
kubectl get pods -w   # wait for 1/1 Running

# 7. Access app
# Open http://127.0.0.1:XXXXX in browser

# Shutdown
minikube stop
```

---

## 10. AI-Assisted DevOps Tools Used

| Tool | Usage |
|---|---|
| **Docker AI (Gordon)** | Generated optimized Dockerfiles for frontend and backend |
| **Claude CLI** | Generated Helm Charts implementing Spec-Driven Deployment |
| **Claude Code (AI Agent)** | Diagnosed and fixed all runtime deployment bugs |
| **kubectl-ai / Kagent** | Cluster monitoring and AI-assisted operations |

---

## 11. Skills Demonstrated

- Docker Containerization and multi-stage builds
- Kubernetes Orchestration (Pods, Services, Deployments)
- Helm Chart creation and lifecycle management (`install`, `upgrade`)
- AI-assisted DevOps toolchain
- Cloud-Native Architecture patterns
- Spec-Driven Infrastructure with Claude CLI
- Neon PostgreSQL cloud database integration
- Next.js production deployment (build-time vs runtime env vars)
- Better Auth server-side configuration
- Kubernetes secret management
- Production-style debugging (logs, exec, rollout strategies)

---

## 12. Conclusion

Phase 4 has been **successfully completed**. The AI Todo Chatbot was transformed from a locally running Phase 3 application into a fully containerized, Kubernetes-orchestrated cloud-native system:

- **Docker** containers package both the Next.js frontend and FastAPI backend
- **Minikube** runs a local Kubernetes cluster simulating a production environment
- **Helm Charts** provide spec-driven, repeatable deployment
- **Neon PostgreSQL** provides persistent cloud database storage
- **Better Auth** handles secure user authentication
- **Cerebras AI** powers the intelligent todo chatbot

All deployment objectives specified in the Phase 4 Hackathon documentation have been fulfilled. The system runs end-to-end with users able to sign up, log in, manage tasks, and interact with the AI chatbot — all within a cloud-native Kubernetes environment.

---

*Report generated: February 21, 2026*
*Claude Code — Spec-Driven Development Agent*
