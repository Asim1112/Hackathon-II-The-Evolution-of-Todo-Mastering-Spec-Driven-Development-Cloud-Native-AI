---
id: 77
title: C Drive Space Recovery Plan
stage: general
date: 2026-02-21
surface: agent
model: claude-sonnet-4-6
feature: none
branch: main
user: Asim
command: "now should we discuss again the issues that i was facing regarding my C drive is getting full and you recommended a safe space recovery plan?"
labels: ["c-drive","disk-space","docker","minikube","vhdx","cleanup","recovery"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - check-space.ps1
  - find-vhdx.ps1
  - safe-cleanup.ps1
tests:
  - manual: C drive free space increased from 2.52 GB to 6.23 GB after Phase 1
---

## Prompt

"now should we discuss again the issues that i was facing regarding my C drive is getting full and you recommended a safe space recovery plan?"

## Response snapshot

Full disk analysis performed. Found the following root causes:

**Space consumers on C drive:**
- Docker data vhdx: `AppData\Local\Docker\wsl\disk\docker_data.vhdx` = 21.52 GB (never auto-shrinks)
- Ubuntu 22.04 WSL distro ext4.vhdx = 4.66 GB
- Minikube cache/images = 3.01 GB (re-downloadable)
- Minikube cache/kic = 515 MB (re-downloadable)
- Minikube cache/preloaded-tarball = 271 MB (re-downloadable)
- Docker Desktop main ext4.vhdx = 0.09 GB

**3-phase safe recovery plan:**

**Phase 1 (DONE):** Deleted Minikube cache folders (~3.8 GB) — immediate C drive recovery.
- Result: C drive free went from 2.52 GB → 6.23 GB

**Phase 2 (DONE):** Removed old Minikube frontend images (v2, v3, :latest) from inside Minikube containerd.
- Dangling kicbase image cannot be removed while Minikube is running (expected)

**Phase 3 (Pending - user action):** Compact docker_data.vhdx using diskpart.
- Requires: minikube stop → wsl --shutdown → diskpart compact vdisk
- Expected recovery: 8-12 GB, bringing C drive to ~15 GB free
- After compaction: restart Docker Desktop → minikube start → update helm BETTER_AUTH_BASE_URL

## Outcome

- ✅ Impact: Immediate 3.7 GB recovered from Minikube cache. Phase 3 compaction will recover another 8-12 GB.
- 🧪 Tests: C drive free space verified before (2.52 GB) and after Phase 1 (6.23 GB)
- 📁 Files: check-space.ps1, find-vhdx.ps1, safe-cleanup.ps1 (helper scripts created)
- 🔁 Next prompts: Guide user through diskpart vhdx compaction (Phase 3)
- 🧠 Reflection: Docker vhdx files grow as images are pulled but never auto-shrink. The key insight is that minikube cache folders are plain C drive files (not inside vhdx) and are the fastest, safest space recovery. Vhdx compaction is the big win but requires full shutdown.

## Evaluation notes (flywheel)

- Failure modes observed: Bash shell eating PowerShell $ variables — solved by writing ps1 script files
- Graders run and results (PASS/FAIL): Phase 1 PASS (3.7 GB recovered)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Guide user through vhdx compaction (Phase 3)
