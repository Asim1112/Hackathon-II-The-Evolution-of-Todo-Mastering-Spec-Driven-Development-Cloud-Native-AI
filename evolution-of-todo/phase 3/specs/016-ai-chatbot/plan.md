# Implementation Plan: AI-Powered Todo Chatbot

**Branch**: `016-ai-chatbot` | **Date**: 2026-02-10 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/016-ai-chatbot/spec.md`

## Summary

Build a conversational AI interface for task management using natural language. Users interact with their todo list through chat, using phrases like "Add a task to buy groceries" or "Show my pending tasks". The system uses OpenAI Agents SDK for natural language understanding, MCP (Model Context Protocol) for standardized tool interfaces, and a stateless architecture for horizontal scalability. The implementation follows a multi-agent design pattern where specialized sub-agents handle distinct responsibilities: database operations, MCP tool implementation, conversation management, intent analysis, agent orchestration, and API coordination.

**Core Technical Approach**: Stateless request/response architecture with database-persisted conversation history. Each chat request follows: receive message → fetch history → analyze intent → run agent with MCP tools → store response → return to user. No server-side session state enables horizontal scaling.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript/JavaScript (frontend)
**Primary Dependencies**:
- Backend: FastAPI, SQLModel, OpenAI Agents SDK (Python), Official MCP SDK (Python), python-jose (JWT)
- Frontend: Next.js 16+, OpenAI ChatKit, TanStack Query, Shadcn UI
**Storage**: Neon Serverless PostgreSQL (existing + new Conversation/Message tables)
**Testing**: pytest (backend), manual validation checklist (hackathon/MVP approach)
**Target Platform**: Web application (Linux server backend, browser frontend)
**Project Type**: Web (existing monorepo with backend/ and frontend/ directories)
**Performance Goals**:
- Chat response time <3 seconds under normal load
- Conversation history retrieval <2 seconds for 100 messages
- Support 100 concurrent chat users
- 95% intent recognition accuracy
**Constraints**:
- Stateless architecture (no server-side sessions)
- Horizontal scalability required
- User isolation enforced at database level
- OpenAI API rate limits (mitigated with GPT-3.5-turbo for development)
**Scale/Scope**:
- 6 user stories (P1-P5 prioritized)
- 5 MCP tools (add, list, complete, delete, update tasks)
- 6 specialized sub-agents
- 2 new database models (Conversation, Message)
- 1 new API endpoint (/api/{user_id}/chat)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Spec-Driven Development
- **Status**: PASS
- **Evidence**: Complete specification with 6 prioritized user stories, 32 functional requirements, 10 measurable success criteria
- **Test Strategy**: Hackathon/MVP approach - implementation-first with manual validation checklist (120+ validation tasks in tasks.md)

### ✅ Zero Manual Coding
- **Status**: PASS
- **Evidence**: All implementation will be through Claude Code commands (/sp.implement)
- **Traceability**: Changes tracked through SDD workflow (spec → plan → tasks → implementation)

### ✅ Security-First Design
- **Status**: PASS
- **Evidence**:
  - FR-020: JWT authentication enforced on chat endpoint
  - FR-021, FR-022, FR-023: User isolation for tasks and conversations
  - All MCP tools require user_id parameter
  - Database queries filtered by user_id
- **Implementation**: Reuse existing Phase 2 Better Auth JWT validation

### ✅ Deterministic and Reproducible Outputs
- **Status**: PASS
- **Evidence**:
  - Stateless architecture ensures consistent behavior
  - Database-persisted state (no in-memory sessions)
  - Environment variables for configuration
  - Idempotent conversation creation

### ✅ Full-Stack Architecture Standards
- **Status**: PASS
- **Evidence**:
  - Backend: FastAPI + SQLModel + Neon PostgreSQL (existing)
  - Frontend: Next.js 16+ App Router (existing)
  - Authentication: Better Auth JWT (existing, reused)
  - New: OpenAI Agents SDK, MCP Server, ChatKit
- **Compliance**: Extends existing Phase 2 architecture without breaking changes

### ✅ End-to-End Agentic Workflow
- **Status**: PASS
- **Evidence**: Following spec → plan → tasks → implementation workflow
- **Test Approach**: Hackathon/MVP - implementation-with-validation, refactor phase documented as post-MVP

### ✅ Multi-Agent System Design (Phase 3)
- **Status**: PASS
- **Evidence**:
  - 6 specialized sub-agents defined with clear responsibilities
  - 6 reusable skills created (MCP Tool Builder, Conversation State Manager, Intent Router, Agent Orchestrator, Database Schema Manager, Stateless API Handler)
  - Sub-agents coordinate through well-defined interfaces
  - No direct coupling between sub-agents

### ✅ MCP Architecture Standards (Phase 3)
- **Status**: PASS
- **Evidence**:
  - 5 MCP tools defined with complete schemas
  - Tools are stateless and idempotent
  - Parameter validation and error taxonomy included
  - Follows Official MCP SDK patterns

### ✅ AI Agent Orchestration (Phase 3)
- **Status**: PASS
- **Evidence**:
  - Stateless request cycle defined
  - Conversation state persisted to database
  - Agent execution pattern follows OpenAI Agents SDK
  - Multi-turn coordination with loop prevention

### ✅ Natural Language Interface (Phase 3)
- **Status**: PASS
- **Evidence**:
  - Intent recognition patterns defined for all CRUD operations
  - Conversational UX principles documented
  - ChatKit integration specified
  - 95% accuracy target for intent classification

**Overall Constitution Compliance**: ✅ PASS - All gates satisfied, ready for Phase 0 research

## Project Structure

### Documentation (this feature)

```text
specs/016-ai-chatbot/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (in progress)
├── research.md          # Phase 0 output (to be created)
├── data-model.md        # Phase 1 output (to be created)
├── quickstart.md        # Phase 1 output (to be created)
├── contracts/           # Phase 1 output (to be created)
│   ├── chat-api.yaml    # OpenAPI spec for chat endpoint
│   └── mcp-tools.json   # MCP tool schemas
├── checklists/          # Quality validation
│   └── requirements.md  # Spec quality checklist (completed)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── task.py              # Existing Phase 2 model
│   │   ├── conversation.py      # NEW: Conversation model
│   │   └── message.py           # NEW: Message model
│   ├── services/
│   │   ├── task_service.py      # Existing Phase 2 service
│   │   ├── conversation_service.py  # NEW: Conversation management
│   │   └── intent_service.py    # NEW: Intent analysis
│   ├── mcp/
│   │   ├── __init__.py
│   │   ├── server.py            # NEW: MCP server setup
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   ├── add_task.py      # NEW: add_task MCP tool
│   │   │   ├── list_tasks.py    # NEW: list_tasks MCP tool
│   │   │   ├── complete_task.py # NEW: complete_task MCP tool
│   │   │   ├── delete_task.py   # NEW: delete_task MCP tool
│   │   │   └── update_task.py   # NEW: update_task MCP tool
│   │   └── schemas.py           # NEW: MCP tool schemas
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── orchestrator.py      # NEW: Agent execution coordinator
│   │   └── prompts.py           # NEW: System prompts for agent
│   └── api/
│       ├── routes/
│       │   ├── tasks.py         # Existing Phase 2 routes
│       │   └── chat.py          # NEW: Chat endpoint
│       └── middleware/
│           └── auth.py          # Existing Phase 2 JWT validation
└── tests/
    ├── test_models.py           # Existing + new model tests
    ├── test_mcp_tools.py        # NEW: MCP tool tests
    ├── test_conversation.py     # NEW: Conversation service tests
    └── test_chat_api.py         # NEW: Chat endpoint tests

frontend/
├── src/
│   ├── components/
│   │   ├── tasks/               # Existing Phase 2 components
│   │   └── chat/
│   │       ├── ChatInterface.tsx    # NEW: Main chat component
│   │       ├── ChatMessage.tsx      # NEW: Message display
│   │       └── ChatInput.tsx        # NEW: Input component
│   ├── app/
│   │   ├── (authenticated)/
│   │   │   ├── tasks/           # Existing Phase 2 pages
│   │   │   └── chat/
│   │   │       └── page.tsx     # NEW: Chat page
│   │   └── api/
│   │       └── auth/            # Existing Phase 2 auth routes
│   └── lib/
│       ├── api.ts               # Existing Phase 2 API client
│       └── chatkit.ts           # NEW: ChatKit configuration
└── tests/
    └── chat.test.tsx            # NEW: Chat component tests

.env.example                     # Update with OPENAI_API_KEY, OPENAI_DOMAIN_KEY
```

**Structure Decision**: Web application (Option 2) - Extends existing Phase 2 monorepo structure. Backend adds MCP server, agent orchestration, and chat API. Frontend adds ChatKit integration and chat UI. No changes to existing Phase 2 code required (additive only).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. All constitution gates passed.

## Phase 0: Research & Technology Validation

### Research Tasks

#### R1: OpenAI Agents SDK Integration Patterns

**Question**: How to integrate OpenAI Agents SDK with FastAPI for stateless request handling?

**Research Focus**:
- Agent initialization patterns (per-request vs singleton)
- Message array formatting for conversation history
- Tool registration with MCP tools
- Error handling and timeout management
- Streaming vs non-streaming responses

**Expected Output**: Code patterns for agent setup, tool registration, and request handling

---

#### R2: Official MCP SDK Implementation

**Question**: How to implement MCP server with Official MCP SDK in Python FastAPI context?

**Research Focus**:
- MCP server initialization and lifecycle
- Tool schema definition and validation
- Integration with FastAPI endpoints
- Error taxonomy and response formatting
- Capability negotiation patterns

**Expected Output**: MCP server setup pattern, tool implementation template

---

#### R3: OpenAI ChatKit Configuration

**Question**: How to configure ChatKit to connect to custom backend API with JWT authentication?

**Research Focus**:
- ChatKit initialization options
- Custom fetch method for JWT injection
- Domain allowlist setup process
- Message formatting and display
- Tool invocation visualization

**Expected Output**: ChatKit configuration code, authentication integration pattern

---

#### R4: Conversation State Management Patterns

**Question**: What are best practices for stateless conversation management with database persistence?

**Research Focus**:
- Conversation creation idempotency
- Message history pagination strategies
- Atomic message storage (user + assistant together)
- Query optimization for conversation retrieval
- Context array building for agent input

**Expected Output**: Database schema design, service layer patterns

---

#### R5: Intent Classification Approaches

**Question**: Should intent classification be handled by the agent or pre-processed before agent invocation?

**Research Focus**:
- Agent-native intent recognition (let OpenAI agent decide)
- Pre-processing with lightweight classifier
- Hybrid approach (pre-filter + agent refinement)
- Trade-offs: latency, accuracy, cost

**Expected Output**: Decision on intent handling approach with rationale

---

#### R6: Database Migration Strategy

**Question**: How to add Conversation and Message models without disrupting existing Phase 2 functionality?

**Research Focus**:
- Alembic migration for new tables
- Foreign key relationships to existing User model
- Index strategy for conversation queries
- Cascade delete behavior

**Expected Output**: Migration script, rollback plan

---

### Research Consolidation

**Output File**: `research.md` will contain:
- Decision for each research task
- Rationale and alternatives considered
- Code examples and patterns
- Integration points with existing Phase 2 code
- Risk mitigation strategies

## Phase 1: Design & Contracts

### Sub-Agent Architecture Design

The implementation is organized around 6 specialized sub-agents, each with distinct responsibilities:

#### 1. Database Operations Manager
**Responsibility**: Define and manage Conversation and Message models

**Deliverables**:
- Conversation model (SQLModel)
- Message model (SQLModel)
- Database migration script
- Index definitions for query optimization

**Skills Used**: Database Schema Manager

**Interfaces**:
- Provides: Schema definitions to all other sub-agents
- Consumes: Existing User and Task models from Phase 2

---

#### 2. MCP Server Architect
**Responsibility**: Implement 5 MCP tools following Official MCP SDK patterns

**Deliverables**:
- MCP server setup (`backend/src/mcp/server.py`)
- 5 MCP tool implementations:
  - `add_task`: Create new task
  - `list_tasks`: Retrieve tasks with status filter
  - `complete_task`: Mark task complete
  - `delete_task`: Remove task
  - `update_task`: Modify task title/description
- Tool schema definitions
- Parameter validation logic
- Error taxonomy

**Skills Used**: MCP Tool Builder

**Interfaces**:
- Provides: MCP tools to Agent Execution Coordinator
- Consumes: Task model from Database Operations Manager
- Consumes: Task service from Phase 2

---

#### 3. Conversation Flow Manager
**Responsibility**: Manage stateless conversation lifecycle

**Deliverables**:
- Conversation service (`backend/src/services/conversation_service.py`)
- Functions:
  - `create_or_get_conversation(user_id, conversation_id=None)`
  - `get_conversation_history(conversation_id, user_id)`
  - `store_messages(conversation_id, user_id, user_message, assistant_message)`
  - `build_context_array(conversation_id, user_id, new_message)`

**Skills Used**: Conversation State Manager

**Interfaces**:
- Provides: Conversation history to Agent Execution Coordinator
- Consumes: Conversation and Message models from Database Operations Manager
- Provides: Message storage to Chat API Coordinator

---

#### 4. Intent Analysis Specialist
**Responsibility**: Analyze natural language and route to appropriate MCP tools

**Deliverables**:
- Intent service (`backend/src/services/intent_service.py`)
- Functions:
  - `classify_intent(message: str) -> IntentType`
  - `extract_parameters(message: str, intent: IntentType) -> dict`
  - `generate_clarification(ambiguous_input: str) -> str`

**Skills Used**: Intent Router

**Interfaces**:
- Provides: Intent classification to Agent Execution Coordinator
- Consumes: Natural language patterns from constitution

**Note**: Based on R5 research, may be simplified if agent-native intent recognition is chosen

---

#### 5. Agent Execution Coordinator
**Responsibility**: Orchestrate OpenAI agent with tool calling

**Deliverables**:
- Agent orchestrator (`backend/src/agents/orchestrator.py`)
- Functions:
  - `initialize_agent(mcp_tools: list) -> Agent`
  - `run_agent(agent: Agent, context: list, user_message: str) -> AgentResponse`
  - `handle_tool_calls(agent: Agent, tool_results: list) -> AgentResponse`
- System prompts (`backend/src/agents/prompts.py`)

**Skills Used**: Agent Orchestrator

**Interfaces**:
- Provides: Agent responses to Chat API Coordinator
- Consumes: MCP tools from MCP Server Architect
- Consumes: Conversation context from Conversation Flow Manager
- Consumes: Intent hints from Intent Analysis Specialist (optional)

---

#### 6. Chat API Coordinator
**Responsibility**: Orchestrate end-to-end stateless chat request cycle

**Deliverables**:
- Chat endpoint (`backend/src/api/routes/chat.py`)
- POST `/api/{user_id}/chat`
- Request validation
- Sub-agent coordination
- Response formatting

**Skills Used**: Stateless API Handler

**Interfaces**:
- Entry point for all chat requests
- Coordinates: Conversation Flow Manager → Agent Execution Coordinator → Conversation Flow Manager
- Provides: Final response to frontend

---

### Data Model Design

**Output File**: `data-model.md`

#### Conversation Model

```python
class Conversation(SQLModel, table=True):
    id: int (primary key, auto-increment)
    user_id: str (foreign key to User, indexed)
    created_at: datetime (auto-generated)
    updated_at: datetime (auto-updated)

    # Relationships
    messages: list[Message] (cascade delete)

    # Constraints
    - user_id must reference existing User
    - Indexes: (user_id), (user_id, created_at DESC)
```

#### Message Model

```python
class Message(SQLModel, table=True):
    id: int (primary key, auto-increment)
    conversation_id: int (foreign key to Conversation, indexed)
    user_id: str (foreign key to User, indexed, denormalized for query optimization)
    role: str (enum: "user" | "assistant")
    content: str (text, not null)
    created_at: datetime (auto-generated)

    # Relationships
    conversation: Conversation

    # Constraints
    - conversation_id must reference existing Conversation
    - user_id must match conversation.user_id (enforced in service layer)
    - role must be "user" or "assistant"
    - Indexes: (conversation_id, created_at ASC), (user_id, created_at DESC)
```

#### Validation Rules

- Conversation creation is idempotent (if conversation_id provided, fetch existing)
- Messages must be stored atomically (user + assistant together or neither)
- User isolation enforced: all queries filtered by user_id
- Cascade delete: deleting conversation deletes all messages

#### State Transitions

- Conversation: created → active (has messages) → archived (future enhancement)
- Message: created (immutable, no state transitions)

---

### API Contracts

**Output Directory**: `contracts/`

#### Chat API Contract

**File**: `contracts/chat-api.yaml` (OpenAPI 3.0)

```yaml
POST /api/{user_id}/chat:
  summary: Send chat message and receive AI response
  parameters:
    - name: user_id
      in: path
      required: true
      schema:
        type: string
  requestBody:
    required: true
    content:
      application/json:
        schema:
          type: object
          properties:
            conversation_id:
              type: integer
              description: Existing conversation ID (optional, creates new if not provided)
            message:
              type: string
              description: User's natural language message
          required:
            - message
  responses:
    200:
      description: Successful response
      content:
        application/json:
          schema:
            type: object
            properties:
              conversation_id:
                type: integer
              response:
                type: string
                description: AI assistant's response
              tool_calls:
                type: array
                items:
                  type: object
                  properties:
                    tool:
                      type: string
                    parameters:
                      type: object
                    result:
                      type: object
    400:
      description: Bad request (invalid message)
    401:
      description: Unauthorized (invalid JWT)
    404:
      description: Conversation not found
    500:
      description: Internal server error
```

#### MCP Tools Contract

**File**: `contracts/mcp-tools.json`

```json
{
  "tools": [
    {
      "name": "add_task",
      "description": "Create a new task",
      "parameters": {
        "type": "object",
        "properties": {
          "user_id": {"type": "string", "description": "User identifier"},
          "title": {"type": "string", "description": "Task title"},
          "description": {"type": "string", "description": "Optional task description"}
        },
        "required": ["user_id", "title"]
      },
      "returns": {
        "type": "object",
        "properties": {
          "task_id": {"type": "integer"},
          "status": {"type": "string", "enum": ["created"]},
          "title": {"type": "string"}
        }
      }
    },
    {
      "name": "list_tasks",
      "description": "Retrieve tasks from the list",
      "parameters": {
        "type": "object",
        "properties": {
          "user_id": {"type": "string", "description": "User identifier"},
          "status": {"type": "string", "enum": ["all", "pending", "completed"], "default": "all"}
        },
        "required": ["user_id"]
      },
      "returns": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "id": {"type": "integer"},
            "title": {"type": "string"},
            "description": {"type": "string"},
            "completed": {"type": "boolean"},
            "created_at": {"type": "string", "format": "date-time"}
          }
        }
      }
    },
    {
      "name": "complete_task",
      "description": "Mark a task as complete",
      "parameters": {
        "type": "object",
        "properties": {
          "user_id": {"type": "string", "description": "User identifier"},
          "task_id": {"type": "integer", "description": "Task identifier"}
        },
        "required": ["user_id", "task_id"]
      },
      "returns": {
        "type": "object",
        "properties": {
          "task_id": {"type": "integer"},
          "status": {"type": "string", "enum": ["completed"]},
          "title": {"type": "string"}
        }
      }
    },
    {
      "name": "delete_task",
      "description": "Remove a task from the list",
      "parameters": {
        "type": "object",
        "properties": {
          "user_id": {"type": "string", "description": "User identifier"},
          "task_id": {"type": "integer", "description": "Task identifier"}
        },
        "required": ["user_id", "task_id"]
      },
      "returns": {
        "type": "object",
        "properties": {
          "task_id": {"type": "integer"},
          "status": {"type": "string", "enum": ["deleted"]},
          "title": {"type": "string"}
        }
      }
    },
    {
      "name": "update_task",
      "description": "Modify task title or description",
      "parameters": {
        "type": "object",
        "properties": {
          "user_id": {"type": "string", "description": "User identifier"},
          "task_id": {"type": "integer", "description": "Task identifier"},
          "title": {"type": "string", "description": "New task title (optional)"},
          "description": {"type": "string", "description": "New task description (optional)"}
        },
        "required": ["user_id", "task_id"]
      },
      "returns": {
        "type": "object",
        "properties": {
          "task_id": {"type": "integer"},
          "status": {"type": "string", "enum": ["updated"]},
          "title": {"type": "string"}
        }
      }
    }
  ]
}
```

---

### Quickstart Guide

**Output File**: `quickstart.md`

Will contain:
- Environment setup (OpenAI API key, domain key)
- Database migration steps
- Backend server startup
- Frontend development server
- Testing the chat interface
- Troubleshooting common issues

---

### Agent Context Update

After Phase 1 design completion, run:

```bash
powershell.exe -ExecutionPolicy Bypass -File .specify/scripts/powershell/update-agent-context.ps1 -AgentType claude
```

This will update `.claude/context.md` (or equivalent) with:
- New technologies: OpenAI Agents SDK, MCP SDK, ChatKit
- New models: Conversation, Message
- New endpoints: /api/{user_id}/chat
- Sub-agent architecture overview

---

## Constitution Check (Post-Design)

*Re-evaluate after Phase 1 design completion*

### ✅ Design Alignment with Constitution

- **Multi-Agent System Design**: Architecture organized around 6 specialized sub-agents with clear responsibilities ✅
- **MCP Architecture Standards**: 5 MCP tools defined with complete schemas and validation ✅
- **AI Agent Orchestration**: Stateless request cycle with database-persisted conversation state ✅
- **Natural Language Interface**: Intent patterns and conversational UX principles integrated ✅
- **Security-First Design**: User isolation enforced at database and service layers ✅
- **Stateless Architecture**: No server-side sessions, horizontal scalability enabled ✅

**Post-Design Status**: ✅ PASS - Design maintains full constitution compliance

---

## Implementation Order (for /sp.tasks)

When generating tasks.md, follow this dependency order:

1. **Database Operations Manager** (no dependencies)
   - Create Conversation and Message models
   - Generate database migration
   - Add indexes

2. **MCP Server Architect** (depends on: Database Operations Manager, Phase 2 Task model)
   - Implement MCP server setup
   - Implement 5 MCP tools
   - Add tool validation and error handling

3. **Conversation Flow Manager** (depends on: Database Operations Manager)
   - Implement conversation service
   - Add conversation creation and retrieval
   - Add message storage (atomic)

4. **Intent Analysis Specialist** (optional, depends on R5 research decision)
   - Implement intent classification (if pre-processing approach chosen)
   - Add parameter extraction
   - Add clarification generation

5. **Agent Execution Coordinator** (depends on: MCP Server Architect, Conversation Flow Manager)
   - Implement agent orchestrator
   - Add OpenAI Agents SDK integration
   - Add tool calling coordination
   - Add system prompts

6. **Chat API Coordinator** (depends on: all above)
   - Implement chat endpoint
   - Add request validation
   - Add sub-agent coordination
   - Add response formatting

7. **Frontend Integration** (depends on: Chat API Coordinator)
   - Implement ChatKit configuration
   - Add chat UI components
   - Add chat page
   - Integrate with existing authentication

---

## Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| OpenAI API rate limits | High | Medium | Use GPT-3.5-turbo for development, implement retry logic, monitor usage |
| Intent recognition accuracy <95% | Medium | Medium | Iterative prompt engineering, fallback to clarification questions |
| Conversation history query performance | Medium | Low | Proper indexing, pagination, query optimization |
| MCP SDK integration complexity | High | Medium | Thorough Phase 0 research, reference examples, incremental testing |
| ChatKit domain allowlist setup | Low | Low | Document setup process in quickstart.md, test early |
| Stateless architecture complexity | Medium | Low | Clear service layer boundaries, comprehensive testing |

---

## Success Metrics (from Spec)

- SC-001: Task creation <10 seconds ✅
- SC-002: 95% intent accuracy ✅
- SC-004: History load <2 seconds ✅
- SC-005: 100 concurrent users ✅
- SC-009: Response time <3 seconds ✅
- SC-010: 100% user isolation ✅

All metrics will be validated during implementation phase through manual testing (hackathon/MVP approach).

---

## Next Steps

1. **Complete Phase 0**: Generate `research.md` by researching all 6 research tasks (R1-R6)
2. **Complete Phase 1**: Generate `data-model.md`, `contracts/`, and `quickstart.md`
3. **Run agent context update**: Update Claude context with new technologies
4. **Proceed to /sp.tasks**: Generate task breakdown organized by sub-agent implementation order
5. **Begin implementation**: Execute /sp.implement following task order

---

**Plan Status**: ✅ Complete - Ready for Phase 0 research
**Next Command**: Begin Phase 0 research or proceed directly to /sp.tasks if research is deferred
