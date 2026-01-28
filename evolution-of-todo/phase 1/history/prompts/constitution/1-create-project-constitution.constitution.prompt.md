---
id: 1
title: Create Project Constitution
stage: constitution
date: 2026-01-28
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: user
command: /sp.constitution
labels: [constitution, setup, todo-app]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - none
---

## Prompt

Project: Phase I - In-Memory Python Console Todo Application (Hackathon II: Evolution of Todo)

Core principles:

- Strict Spec-Driven Development: All code must be generated and refined solely via Claude Code from precise Markdown specifications. No manual code writing or editing allowed — refine specs iteratively until output is correct, functional, and passes tests.

- Clean Code & Pythonic Excellence: Follow PEP 8, use descriptive names, modular structure, type hints (Python 3.13+), docstrings, and exception handling. Prioritize readability, maintainability, and minimalism.

- In-Memory Only: Use simple Python data structures (e.g., list of dicts or dataclass objects) for task storage — no files, databases, or external persistence in this phase.

- User-Centric CLI: Intuitive command-line interface (text menu or command parser) for all operations. Clear output formatting (e.g., numbered lists, status indicators like [x] for complete).

- Hackathon Compliance: Implement exactly the 5 Basic Level features: Add Task (with title + description), View Task List (display all with status), Update Task (modify details), Delete Task (by ID), Mark as Complete (toggle completion).

- Quality & Safety: Include basic input validation, unique auto-incrementing task IDs, graceful error handling (e.g., invalid ID), and a help/usage command.

- Reproducibility & Traceability: All generated code must reference the spec it came from (comments). Track spec iterations in /specs/history/.

Key standards:

- Python version: 3.13+
- Dependency management: Use UV for fast, reproducible environments (uv init, uv add if needed — but minimize external deps; prefer stdlib).
- Project structure: src/ for code, specs/ for specifications, CLAUDE.md for agent instructions, README.md with setup/run/demo.
- Testing mindset: Generate unit tests or manual verification steps in specs where possible.
- Output style: Console output should be clean, tabular (use tabulate if added via UV, else simple formatting), with success/error messages.

Constraints:

- Scope: Console-only, single-user, in-memory (tasks lost on exit — expected for Phase I).
- No web, no auth, no persistence, no advanced features (priorities, due dates, search, recurring — save for later phases).
- Code generation: Must be complete, runnable out-of-the-box after uv sync or python -m src.todo.
- Deliverables: Constitution.md, specs/feature files (e.g., task-crud.md), src/main.py or app.py, README.md with instructions, CLAUDE.md.

Success criteria:

- All 5 basic CRUD + complete operations work correctly via CLI.
- Code passes manual verification against spec (no syntax errors, handles edge cases like empty list, invalid input).
- Zero manual code changes — all via /sp.implement or equivalent after refining spec.
- Application runs with: uv run python src/main.py (or similar).
- Clear, user-friendly interface that demonstrates adding, viewing, updating, deleting, and toggling tasks.

## Response snapshot

Created a comprehensive constitution file at .specify/memory/constitution.md for the Phase I Todo application project. The constitution includes six core principles covering spec-driven development, clean code practices, in-memory storage, user-centric CLI, core CRUD operations, and quality standards. It also includes sections on technology stack, output style requirements, scope limitations, development workflow, and governance.

## Outcome

- ✅ Impact: Created foundational constitution document that will guide all future development decisions for the Phase I Todo application
- 🧪 Tests: none
- 📁 Files: Updated .specify/memory/constitution.md with complete project constitution
- 🔁 Next prompts: Continue with spec creation using /sp.specify to define the detailed feature requirements
- 🧠 Reflection: The constitution captures all the key principles from the user's requirements and establishes a solid foundation for the project

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Begin spec creation to define the detailed requirements for the todo application