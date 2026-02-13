<!--
Sync Impact Report:
- Version change: 1.1.0 → 1.2.0 (Phase 3 multi-agent and MCP architecture principles)
- Modified principles:
  - Technology Stack Requirements: Added OpenAI Agents SDK, MCP Server, ChatKit
  - Full-Stack Architecture Standards: Added stateless conversation management requirements
- Added sections:
  - Multi-Agent System Design (NEW) - Defines reusable intelligence through skills and sub-agents
  - MCP Architecture Standards (NEW) - Defines tool design, stateless operations, and protocol compliance
  - AI Agent Orchestration (NEW) - Defines agent execution, tool calling, and conversation management
  - Natural Language Interface (NEW) - Defines intent routing and conversational UX principles
- Removed sections: None
- Templates requiring updates:
  - ⚠️ spec-template.md: May need AI chatbot feature template
  - ⚠️ plan-template.md: May need multi-agent architecture planning guidance
  - ⚠️ tasks-template.md: May need MCP tool implementation task patterns
- Follow-up TODOs:
  - Document MCP tool testing patterns
  - Add examples of multi-agent coordination
  - Define conversation state migration strategies
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

### Core Stack (Phase 1-2)
- Backend: Python FastAPI with SQLModel ORM
- Database: Neon Serverless PostgreSQL
- Frontend: Next.js 16+ with App Router
- Authentication: Better Auth (JWT-based, stateless) - may be implemented in Next.js frontend (Node.js runtime) or FastAPI backend (Python runtime) based on library requirements
- Environment: All auth secrets must be shared via environment variables
- API Design: RESTful endpoints with consistent error handling and response formats

### AI & Agent Stack (Phase 3)
- AI Framework: OpenAI Agents SDK for agent orchestration and tool calling
- MCP Server: Official MCP SDK (Python) for exposing task operations as standardized tools
- Chat Interface: OpenAI ChatKit for conversational UI
- LLM Provider: OpenAI API (GPT-3.5-turbo for development, GPT-4 for production)
- Conversation Storage: Database-persisted chat history (Conversation and Message models)
- Architecture Pattern: Stateless request/response with no server-side session state

## Development Workflow

- All code must be generated through Claude Code commands (e.g., /sp.specify, /sp.plan, /sp.tasks, /sp.implement)
- Specifications must be reviewed and approved before planning
- Task breakdowns must include acceptance criteria and validation scenarios
- Multi-user task isolation must be validated during implementation
- Frontend-backend communication must be exclusively through authenticated API calls
- **Production code:** All changes must follow the red-green-refactor cycle with proper testing
- **Hackathon/MVP code:** Implementation-first approach acceptable with validation tasks and refactor phase documented as post-MVP enhancement

## Multi-Agent System Design (Phase 3)

### Reusable Intelligence Through Skills
All AI capabilities must be packaged as reusable skills following the Spec-Kit Plus skill pattern; Each skill must represent a meaningful capability (not trivial functions); Skills must be clearly scoped with defined inputs, outputs, and responsibilities; Skills must be composable and reusable across multiple sub-agents; Skill definitions must include: when to use, how it works, output format, quality criteria, and examples.

### Sub-Agent Specialization
Intelligence must be distributed across specialized sub-agents, each with narrow, well-defined responsibilities; Each sub-agent must have a clear persona defining how it thinks and behaves; Sub-agents must rely on assigned skills for their capabilities; Sub-agents must coordinate through well-defined interfaces (no direct coupling); The system must demonstrate true reusable intelligence where agents compose skills to solve problems.

### Required Sub-Agents for Phase 3
- **MCP Server Architect**: Design and implement MCP tools following Official MCP SDK patterns
- **Conversation Flow Manager**: Manage stateless conversation lifecycle with database-persisted history
- **Intent Analysis Specialist**: Analyze natural language and route to appropriate MCP tools
- **Agent Execution Coordinator**: Orchestrate OpenAI agent with tool calling and multi-turn coordination
- **Chat API Coordinator**: Orchestrate end-to-end stateless chat request cycle
- **Database Operations Manager**: Define and manage Conversation and Message models

### Sub-Agent Coordination Principles
Request flow must follow clear orchestration: Chat API Coordinator → Conversation Flow Manager → Intent Analysis Specialist → Agent Execution Coordinator → MCP Server Architect; Each sub-agent must handle its own errors and return structured error information; No sub-agent may maintain state across requests (enables horizontal scalability); All sub-agents must rely on Database Operations Manager for schema definitions.

## MCP Architecture Standards (Phase 3)

### Tool Design Principles
All task operations must be exposed as MCP tools following Official MCP SDK patterns; Each tool must have complete schema with name, description, typed parameters (required/optional), and return structure; Tool schemas must be validated before execution with type checking and constraint enforcement; Tools must be stateless and idempotent where appropriate; Tool implementations must include comprehensive error taxonomy with actionable error messages.

### Required MCP Tools
- **add_task**: Create new task (params: user_id, title, description; returns: task_id, status, title)
- **list_tasks**: Retrieve tasks (params: user_id, status filter; returns: array of task objects)
- **complete_task**: Mark task complete (params: user_id, task_id; returns: task_id, status, title)
- **delete_task**: Remove task (params: user_id, task_id; returns: task_id, status, title)
- **update_task**: Modify task (params: user_id, task_id, title, description; returns: task_id, status, title)

### Stateless Operations
All MCP tools must be stateless with no server-side session state; Tool execution must be safe to retry (idempotent operations preferred); All state must be persisted to database immediately; Tools must support horizontal scaling (any server instance can handle any request); Tool results must be self-contained with no reliance on previous invocations.

### Protocol Compliance
MCP server must follow Official MCP SDK patterns for capability negotiation; Tools must return standardized content arrays (text, images, resources); Error responses must include error type, message, and recovery guidance; Tool documentation must include input/output examples for all use cases.

## AI Safety Principles (Phase 3)

### State Verification Mandate (CRITICAL)
**The agent MUST verify all mutation operations by re-querying system state. Claiming success without verification is FORBIDDEN.**

After ANY mutation operation (add_task, delete_task, complete_task, update_task), the agent MUST:
1. **Capture before-state**: Query current state before mutation (e.g., list_tasks to get task count)
2. **Execute mutation**: Call the mutation tool (e.g., delete_task)
3. **Verify after-state**: Re-query system state after mutation (e.g., list_tasks again)
4. **Compare states**: Explicitly compare before/after to verify the change occurred
5. **Report truthfully**: Only claim success if verification confirms the state change

**Forbidden Behaviors:**
- ❌ Claiming success based solely on tool return value (e.g., {"status": "deleted"})
- ❌ Assuming mutation succeeded without re-querying state
- ❌ Reporting success when verification shows state unchanged
- ❌ Skipping verification to save tokens or reduce latency

**Required Behaviors:**
- ✅ Always re-query state after mutations
- ✅ Explicitly compare before/after state in reasoning
- ✅ Report verification results to user ("I deleted 6 tasks. Verified: task count reduced from 12 to 6.")
- ✅ Admit failure if verification shows state unchanged ("The deletion appeared to succeed, but when I checked, all 12 tasks are still present. There may be a system issue.")

**Example - Correct Verification Pattern:**
```
User: "Delete duplicate tasks"

Agent reasoning:
1. Query before-state: list_tasks → 12 tasks found
2. Identify duplicates: Tasks 7-12 are duplicates of 1-6
3. Execute deletions: delete_task(7), delete_task(8), ..., delete_task(12)
4. Verify after-state: list_tasks → 6 tasks found
5. Compare: 12 - 6 = 6 tasks deleted ✓
6. Report: "I've deleted 6 duplicate tasks. Verified: Your task list now has 6 tasks (previously 12)."
```

**Example - Incorrect Pattern (FORBIDDEN):**
```
User: "Delete duplicate tasks"

Agent reasoning:
1. Execute deletions: delete_task(7) → {"status": "deleted"}
2. Report: "I've deleted the duplicate tasks." ❌ NO VERIFICATION
```

### Hallucination Prevention
The agent must distinguish between tool return values and actual system state; Tool success responses (e.g., {"status": "deleted"}) indicate the operation was attempted, NOT that the state changed; Database transactions, network failures, or bugs may cause silent failures; The agent must treat all mutations as "claimed success, pending verification" until state is re-queried.

### Error Transparency
If verification reveals a discrepancy (tool claimed success but state unchanged), the agent MUST:
1. Immediately inform the user of the discrepancy
2. Provide exact details (e.g., "Tool returned success, but task count is still 12")
3. Suggest troubleshooting steps (e.g., "There may be a database transaction issue. Please check the backend logs.")
4. Never hide or minimize the failure

## AI Agent Orchestration (Phase 3)

### Agent Execution Pattern
Agents must be initialized with clear instructions and available MCP tools; Message arrays must include system prompt, conversation history, and current user message; Agent execution must follow the built-in agent loop: invoke tools → process results → continue until complete; Multi-turn coordination must prevent infinite loops with maximum iteration limits; Tool results must be fed back to agent correctly for continued reasoning.

### Conversation State Management
All conversation state must be persisted to database (no server-side sessions); Conversation creation must be idempotent (safe to retry); Message history must load efficiently with indexed queries on user_id and conversation_id; Context arrays must be formatted exactly as required by OpenAI Agents SDK; Message storage must be atomic (user message + assistant response together or neither).

### Stateless Request Cycle
Every chat request must follow: receive message → fetch history → build context → store user message → run agent → invoke tools → store assistant response → return response; Server must hold no state between requests (ready for next request immediately); Any server instance must be able to handle any request (horizontal scalability); Conversation continuity must rely solely on database-persisted history.

### Tool Calling Coordination
Agent must have access to all 5 MCP tools during execution; Tool invocations must include proper parameter validation before execution; Tool failures must be handled gracefully with error messages returned to agent; Agent must be able to chain multiple tools in single turn when needed; Execution trace must log all tool calls with parameters and results for debugging.

## Natural Language Interface (Phase 3)

### Intent Recognition
System must interpret natural language input and map to appropriate MCP tools; Intent classification must handle common phrasings with 95%+ accuracy on test set; Parameter extraction must handle variations (synonyms, different word orders, implicit references); Ambiguous inputs must trigger clarification questions (never guess); Multi-step intents must be decomposed correctly (e.g., "find and delete task X" → list_tasks then delete_task).

### Conversational UX Principles
Agent must always confirm actions with friendly, natural language responses; Responses must be concise and actionable (avoid verbose explanations); Error messages must be user-friendly and suggest recovery actions; Agent must handle out-of-scope requests gracefully with helpful guidance; Conversation flow must feel natural (not robotic command execution).

### Required Natural Language Patterns
System must understand and respond to:
- Task creation: "Add a task to...", "Remember to...", "I need to..."
- Task listing: "Show my tasks", "What's pending?", "What have I completed?"
- Task completion: "Mark task X as done", "I finished...", "Complete..."
- Task deletion: "Delete task X", "Remove...", "Cancel..."
- Task updates: "Change task X to...", "Update...", "Rename..."

### ChatKit Integration
Frontend must use OpenAI ChatKit for conversational UI; ChatKit must connect to stateless /api/{user_id}/chat endpoint; Domain allowlist must be configured in OpenAI dashboard for production deployment; Environment variables must include NEXT_PUBLIC_OPENAI_DOMAIN_KEY; Chat interface must display tool invocations and results transparently.

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

**Version**: 1.2.0 | **Ratified**: 2025-12-22 | **Last Amended**: 2026-02-10
