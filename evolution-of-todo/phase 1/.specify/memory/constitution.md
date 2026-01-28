<!-- Sync Impact Report:
Version change: N/A → 1.0.0
Added sections: All core principles and governance
Removed sections: None
Templates requiring updates: ✅ updated
Follow-up TODOs: None
-->
# Phase I - In-Memory Python Console Todo Application Constitution

## Core Principles

### I. Strict Spec-Driven Development
All code must be generated and refined solely via Claude Code from precise Markdown specifications. No manual code writing or editing allowed — refine specs iteratively until output is correct, functional, and passes tests. This ensures traceability and reproducibility of all implementation decisions.

### II. Clean Code & Pythonic Excellence
Follow PEP 8, use descriptive names, modular structure, type hints (Python 3.13+), docstrings, and exception handling. Prioritize readability, maintainability, and minimalism. Code should be self-documenting and easy to understand for future developers.

### III. In-Memory Only Storage
Use simple Python data structures (e.g., list of dicts or dataclass objects) for task storage — no files, databases, or external persistence in this phase. This maintains simplicity for Phase I while allowing for future persistence layers in subsequent phases.

### IV. User-Centric CLI Interface
Provide intuitive command-line interface (text menu or command parser) for all operations. Clear output formatting (e.g., numbered lists, status indicators like [x] for complete). The interface should be discoverable and user-friendly for basic task management operations.

### V. Core CRUD + Complete Operations
Implement exactly the 5 Basic Level features: Add Task (with title + description), View Task List (display all with status), Update Task (modify details), Delete Task (by ID), Mark as Complete (toggle completion). These form the essential foundation of the todo application.

### VI. Quality & Safety Standards
Include basic input validation, unique auto-incrementing task IDs, graceful error handling (e.g., invalid ID), and a help/usage command. The application must be robust against invalid user inputs and provide clear error messages.

## Additional Constraints

### Technology Stack
- Python version: 3.13+
- Dependency management: Use UV for fast, reproducible environments (uv init, uv add if needed — but minimize external deps; prefer stdlib)
- Project structure: src/ for code, specs/ for specifications, CLAUDE.md for agent instructions, README.md with setup/run/demo

### Output Style Requirements
Console output should be clean, tabular (use tabulate if added via UV, else simple formatting), with success/error messages. Visual clarity is important for user experience in the console interface.

### Scope Limitations
Console-only, single-user, in-memory (tasks lost on exit — expected for Phase I). No web, no auth, no persistence, no advanced features (priorities, due dates, search, recurring — save for later phases).

## Development Workflow

### Code Generation Process
Code generation must be complete, runnable out-of-the-box after uv sync or python -m src.todo. All generated code must reference the spec it came from (comments). Track spec iterations in /specs/history/.

### Testing Mindset
Generate unit tests or manual verification steps in specs where possible. Each feature should have clear acceptance criteria and verification steps.

### Deliverables
Must produce: Constitution.md, specs/feature files (e.g., task-crud.md), src/main.py or app.py, README.md with instructions, CLAUDE.md. All deliverables must work together as a cohesive system.

## Governance

This constitution supersedes all other practices and guides all implementation decisions for the Phase I Todo application. Amendments require documentation of the change, approval from project stakeholders, and a migration plan for existing code. All PRs/reviews must verify compliance with these principles. The constitution serves as the ultimate authority for resolving implementation disputes and ensuring consistent architectural decisions.

**Version**: 1.0.0 | **Ratified**: 2026-01-28 | **Last Amended**: 2026-01-28