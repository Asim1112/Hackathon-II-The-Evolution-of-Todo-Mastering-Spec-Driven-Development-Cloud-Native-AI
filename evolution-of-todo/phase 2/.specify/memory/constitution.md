<!--
Sync Impact Report:
- Version change: 1.0.0 → 1.1.0 (context-specific implementation amendments)
- Modified principles:
  - Spec-Driven Development: Expanded to allow test timing flexibility (test-first vs implementation-first based on context)
  - Full-Stack Architecture Standards: Expanded to allow runtime-appropriate authentication placement (Next.js vs FastAPI)
  - End-to-End Agentic Workflow: Expanded to allow workflow flexibility (red-green-refactor vs validation-first based on context)
- Added sections:
  - Context-Specific Implementation (NEW) - Defines production vs hackathon/MVP vs proof-of-concept requirements
- Removed sections: None
- Templates requiring updates:
  - ✅ plan-template.md: Constitution Check section aligns with new context-aware principles
  - ✅ spec-template.md: User Stories section already supports flexible test strategies
  - ✅ tasks-template.md: Format already supports optional tests with explicit strategy documentation
  - ⚠️ commands/*.md: Review for outdated references to strict test-first requirements (manual follow-up recommended)
- Follow-up TODOs:
  - Consider documenting upgrade paths from hackathon/MVP to production (when to add tests, refactor, harden security)
  - Add examples to constitution showing compliant hackathon vs production implementations
-->
# Todo Full-Stack Web Application Constitution

## Core Principles

### Spec-Driven Development (NON-NEGOTIABLE)
All development follows the spec → plan → tasks → implementation workflow; Specifications must be complete and approved before any coding begins; Every feature must have test strategy defined:
- **Production features:** Test cases must be written and defined in tasks.md before implementation (test-first approach required)
- **Hackathon/MVP features:** Test cases may be documented as post-MVP enhancement with manual validation checklist in tasks.md (implementation-first acceptable)
- **Proof-of-concept features:** Manual testing acceptable with upgrade path to automated tests documented

In all cases, the chosen test strategy must be explicitly stated in tasks.md header.

### Zero Manual Coding
Implementation must be achieved exclusively through Claude Code and automated tools; No hand-written code modifications allowed during the development phase; All changes must be traceable through the agentic development workflow.

### Security-First Design
JWT authentication must be enforced on every API route; Multi-user task isolation is mandatory - users can only access their own data; All sensitive data must be properly validated and sanitized before persistence; Session security must use HTTP-only cookies to prevent XSS attacks.

### Deterministic and Reproducible Outputs
Every development step must produce consistent, repeatable results; All environment configurations must be version-controlled and reproducible; Build and deployment processes must be idempotent and deterministic.

### Full-Stack Architecture Standards
Backend must use FastAPI + SQLModel with Neon Serverless PostgreSQL; Frontend must use Next.js 16+ App Router with stateless authentication; Better Auth (JWT-based) must be implemented for user management in the appropriate runtime environment:
- If authentication library requires Node.js runtime: Implement in Next.js frontend with JWT validation in FastAPI backend
- If authentication library has Python support: Implement in FastAPI backend
- In both cases: JWT tokens must be validated, multi-user isolation must be enforced, session security must use HTTP-only cookies

### End-to-End Agentic Workflow
All development phases must follow the Agentic Dev Stack workflow from specification to deployment; Each phase must be validated before proceeding to the next; Testing approach must match feature scope:
- **Production features:** Red-green-refactor cycle with comprehensive automated testing
- **Hackathon/MVP features:** Implementation-with-validation approach (validation tasks in tasks.md, refactor in subsequent iteration)
- **Proof-of-concept features:** Validation tasks only, refactor when promoted to production

## Context-Specific Implementation

The principles above define WHAT outcomes are required (security, testability, quality, validation). This section clarifies HOW those outcomes may be achieved based on feature context.

### Production Features
Production features are user-facing releases requiring full rigor:
- **Test approach:** Test-first required (tests written before implementation)
- **Workflow:** Red-green-refactor cycle mandatory
- **Test coverage:** Automated test coverage ≥80% for critical paths
- **Authentication:** All security outcomes mandatory (JWT validation, multi-user isolation, HTTP-only cookies)
- **Documentation:** Complete API documentation, deployment guides, runbooks
- **Validation:** Comprehensive automated test suites, integration tests, contract tests

### Hackathon/MVP Features
Hackathon/MVP features are time-boxed deliveries (days/weeks) focused on rapid prototyping:
- **Test approach:** Test strategy documented (implementation-first acceptable)
- **Workflow:** Implementation-with-validation (validation tasks required in tasks.md)
- **Test coverage:** Manual validation checklist acceptable (120+ validation tasks minimum)
- **Authentication:** All security outcomes mandatory (methods flexible - trusted headers acceptable with JWT validation documented for post-MVP)
- **Documentation:** Setup instructions, troubleshooting guide, upgrade path to production
- **Validation:** Manual end-to-end testing with checkpoints after each user story
- **Refactor phase:** Explicitly documented as post-MVP enhancement with clear acceptance criteria

### Proof-of-Concept Features
Proof-of-concept features are experimental explorations with minimal testing:
- **Test approach:** Manual testing only
- **Workflow:** Validation tasks only (no refactor required)
- **Test coverage:** Smoke tests sufficient
- **Authentication:** Security outcomes required if handling sensitive data
- **Documentation:** Clear upgrade path if promoted to production
- **Validation:** Basic functionality verification only

### Transition Guidelines
When promoting features between contexts:
- **Hackathon → Production:** Add automated tests (target 80% coverage), implement full JWT validation, add refactor phase, complete documentation
- **POC → Production:** Add comprehensive test suite, implement all security outcomes, add CI/CD integration, complete architecture review
- **MVP → Enhanced:** Iteratively add tests per user story, refactor technical debt, harden security (move from trusted headers to JWT validation)

## Technology Stack Requirements

- Backend: Python FastAPI with SQLModel ORM
- Database: Neon Serverless PostgreSQL
- Frontend: Next.js 16+ with App Router
- Authentication: Better Auth (JWT-based, stateless) - may be implemented in Next.js frontend (Node.js runtime) or FastAPI backend (Python runtime) based on library requirements
- Environment: All auth secrets must be shared via environment variables
- API Design: RESTful endpoints with consistent error handling and response formats

## Development Workflow

- All code must be generated through Claude Code commands (e.g., /sp.specify, /sp.plan, /sp.tasks, /sp.implement)
- Specifications must be reviewed and approved before planning
- Task breakdowns must include acceptance criteria and validation scenarios
- Multi-user task isolation must be validated during implementation
- Frontend-backend communication must be exclusively through authenticated API calls
- **Production code:** All changes must follow the red-green-refactor cycle with proper testing
- **Hackathon/MVP code:** Implementation-first approach acceptable with validation tasks and refactor phase documented as post-MVP enhancement

## Governance

This constitution governs all development activities for the Todo Full-Stack Web Application; All team members must comply with these principles; Amendments require explicit documentation and approval through the /sp.constitution command; Version control and audit trails must be maintained for all changes.

**Amendment Process:**
- Amendments must provide clear rationale and impact analysis
- Version bumps follow semantic versioning: MAJOR (breaking changes to principles), MINOR (new guidance/context added), PATCH (clarifications only)
- All amendments must include Sync Impact Report documenting affected templates and artifacts
- Constitution changes must be validated against existing features for compliance

**Compliance Review:**
- All features must pass constitution check in plan.md before implementation
- /sp.analyze command validates cross-artifact alignment with constitutional principles
- Violations must be resolved before proceeding to implementation phase
- Context-specific implementation choices must be explicitly documented in feature artifacts

**Version**: 1.1.0 | **Ratified**: 2025-12-22 | **Last Amended**: 2026-02-07
