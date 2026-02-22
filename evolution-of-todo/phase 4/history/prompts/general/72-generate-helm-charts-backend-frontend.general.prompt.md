---
id: 72
title: Generate Helm Charts Backend and Frontend
stage: general
date: 2026-02-20
surface: agent
model: claude-sonnet-4-6
feature: none
branch: main
user: user
command: generate helm charts for backend and frontend
labels: ["helm", "kubernetes", "minikube", "devops", "infrastructure"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend-chart/Chart.yaml
  - backend-chart/values.yaml
  - backend-chart/templates/_helpers.tpl
  - backend-chart/templates/deployment.yaml
  - backend-chart/templates/service.yaml
  - backend-chart/templates/secret.yaml
  - backend-chart/templates/NOTES.txt
  - frontend-chart/Chart.yaml
  - frontend-chart/values.yaml
  - frontend-chart/templates/_helpers.tpl
  - frontend-chart/templates/deployment.yaml
  - frontend-chart/templates/service.yaml
  - frontend-chart/templates/secret.yaml
  - frontend-chart/templates/NOTES.txt
tests:
  - find command confirmed all 14 chart files present
---

## Prompt

I am in Phase 4 of my hackathon. My Minikube cluster is running. I have two local Docker images: todo-backend:latest and todo-frontend:latest.

Please generate two Helm Charts for me:
1. A backend-chart for my FastAPI app (Port 8000).
2. A frontend-chart for my Next.js app (Port 3000).

Important: Set the imagePullPolicy to IfNotPresent so Kubernetes uses my local images, and ensure the frontend knows how to communicate with the backend service. Save these in folders named 'backend-chart' and 'frontend-chart'.

## Response snapshot

Generated 14 files across two complete Helm charts:

**backend-chart** (ClusterIP, port 8000):
- fullnameOverride: "todo-backend" → predictable DNS name inside cluster
- imagePullPolicy: IfNotPresent → uses local Minikube image
- Health probes on /health endpoint
- Sensitive vars (DATABASE_URL, BETTER_AUTH_SECRET, JWT_SECRET, API keys) stored in Kubernetes Secret via stringData
- Non-sensitive vars (ENVIRONMENT, JWT_ALGORITHM, etc.) as plain env vars

**frontend-chart** (NodePort 30000, port 3000):
- fullnameOverride: "todo-frontend"
- imagePullPolicy: IfNotPresent → uses local Minikube image
- BACKEND_URL set to "http://todo-backend:8000" — matches backend service DNS name via fullnameOverride
- next.config.ts reads BACKEND_URL at runtime to route server-side API proxy rewrites
- BETTER_AUTH_BASE_URL configurable for the Minikube external URL
- NodePort 30000 for external browser access

## Outcome

- ✅ Impact: Full Kubernetes deployment configuration ready for helm install; frontend-to-backend communication wired via cluster DNS
- 🧪 Tests: find command confirmed all 14 files at expected paths
- 📁 Files: 14 new files in backend-chart/ and frontend-chart/
- 🔁 Next prompts: helm install backend ./backend-chart, helm install frontend ./frontend-chart, then minikube service todo-frontend --url
- 🧠 Reflection: Using fullnameOverride in both charts is critical for predictable DNS — without it the service name would vary by Helm release name and the frontend BACKEND_URL would need to be updated per deployment.

## Evaluation notes (flywheel)

- Failure modes observed: none — all files generated and validated structurally
- Graders run and results (PASS/FAIL): file structure check via find — PASS
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): helm install with real secrets via --set flags
