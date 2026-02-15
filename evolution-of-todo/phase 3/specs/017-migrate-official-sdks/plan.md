# Implementation Plan: Migrate to Official OpenAI SDKs for Phase III Compliance

**Branch**: `017-migrate-official-sdks` | **Date**: 2026-02-11 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/017-migrate-official-sdks/spec.md`

## Summary

Replace current manual OpenAI client orchestration with **OpenAI Agents SDK** (backend) and custom ChatInterface with **OpenAI ChatKit** (frontend) to achieve full Phase III compliance. The migration preserves 100% of existing functionality while reducing backend orchestration code by ~80% (from ~100 lines to ~20 lines) through official SDK patterns. All 5 MCP tools (add_task, list_tasks, complete_task, delete_task, update_task) will integrate via `MCPServerStreamableHttp` pattern. Frontend will use ChatKit React component with automatic message handling and streaming support.

**Primary Goal**: Pass Phase III compliance audit (PASS on all 6 requirements, currently FAIL on Requirement #2 and Frontend requirement).

**Technical Approach**:
1. Backend: Create `ChatKitServer` subclass with `respond()` method that uses `Agent` + `Runner` + `AgentContext` + helper functions (`simple_to_agent_input`, `stream_agent_response`)
2. Backend: Implement `Store` interface (13 methods) as adapter over existing `Conversation`/`Message` models
3. Backend: Add `/chatkit` FastAPI endpoint that calls `server.process()` and returns `StreamingResponse` or JSON
4. Frontend: Replace `ChatInterface` component with `<ChatKit>` from `@openai/chatkit-react`
5. Integration: Connect Agent to MCP server via `MCPServerStreamableHttp` with `cache_tools_list=True`

## Technical Context

**Language/Version**: Python 3.11 (backend), TypeScript/Next.js 16+ (frontend)
**Primary Dependencies**:
- Backend: OpenAI Agents SDK v0.7.0 (Agent, Runner, MCPServerStreamableHttp), ChatKit Python SDK (ChatKitServer, Store, AgentContext), FastAPI, SQLModel
- Frontend: ChatKit React SDK (@openai/chatkit-react), Next.js 16+ App Router
**Storage**: Neon Serverless PostgreSQL (existing Conversation and Message models - NO schema changes)
**Testing**: Manual validation checklist (120+ validation tasks), regression testing for all 5 MCP tools, Phase III compliance audit simulation
**Target Platform**: Linux server (backend), Web browser (frontend)
**Project Type**: Web application (backend + frontend)
**Performance Goals**: Maintain current response time (within 10% latency), support same concurrent user load
**Constraints**:
- Zero schema changes (Store adapter pattern preserves existing database structure)
- Zero breaking changes to functionality (100% functional parity required)
- Minimal file changes (only AI orchestration and chat UI layers)
- Must use official SDK patterns exactly as documented in knowledge base files
**Scale/Scope**: 5 MCP tools, 2 database models (Conversation, Message), 1 chat endpoint, 1 frontend component replacement

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Compliance Assessment

✅ **Spec-Driven Development**: Following spec → plan → tasks → implement workflow. Specification complete and approved.

✅ **Zero Manual Coding**: All implementation will be through Claude Code commands (/sp.implement).

✅ **Security-First Design**: Preserving existing JWT authentication, multi-user isolation via user_id in Store context parameter, HTTP-only cookies.

✅ **Full-Stack Architecture Standards**:
- Backend: FastAPI + SQLModel + Neon PostgreSQL (preserved)
- Frontend: Next.js 16+ App Router (preserved)
- Authentication: Better Auth JWT-based (preserved)
- AI Stack: Migrating to OpenAI Agents SDK + ChatKit (Phase III requirement)

✅ **AI & Agent Stack (Phase III)**:
- ✅ AI Framework: OpenAI Agents SDK for agent orchestration (replacing manual client)
- ✅ MCP Server: Official MCP SDK (preserved, accessed via MCPServerStreamableHttp)
- ✅ Chat Interface: OpenAI ChatKit (replacing custom ChatInterface)
- ✅ Conversation Storage: Database-persisted (preserved via Store adapter)
- ✅ Architecture Pattern: Stateless request/response (preserved via ChatKit Store)

✅ **Multi-Agent System Design**: Not applicable (single agent migration, not multi-agent coordination)

✅ **MCP Architecture Standards**:
- ✅ Tool Design: All 5 MCP tools preserved unchanged
- ✅ Stateless Operations: Preserved (Agent.mcp_servers integration maintains stateless pattern)
- ✅ Protocol Compliance: Preserved (MCPServerStreamableHttp handles protocol)

✅ **AI Safety Principles**:
- ✅ State Verification Mandate: Preserved (agent instructions include verification requirements)
- ✅ Hallucination Prevention: Preserved (verification pattern maintained)
- ✅ Error Transparency: Preserved (error handling maintained)

✅ **AI Agent Orchestration**:
- ✅ Agent Execution Pattern: Migrating to Runner.run_streamed() (official SDK pattern)
- ✅ Conversation State Management: Preserved via Store adapter over existing models
- ✅ Stateless Request Cycle: Preserved (ChatKit Store loads history, no server-side sessions)
- ✅ Tool Calling Coordination: Migrating to Agent.mcp_servers (official SDK pattern)

✅ **Natural Language Interface**:
- ✅ Intent Recognition: Preserved (agent instructions maintain NLU patterns)
- ✅ Conversational UX: Preserved (agent personality maintained)
- ✅ Required Patterns: Preserved (all natural language patterns work identically)
- ✅ ChatKit Integration: Implementing (Phase III requirement)

### Gate Status: ✅ PASS

All constitutional requirements are met. This is a compliant migration that replaces non-compliant implementations with official SDKs while preserving all architectural decisions, security patterns, and functional behavior.

## Project Structure

### Documentation (this feature)

```text
specs/017-migrate-official-sdks/
├── spec.md              # Feature specification (COMPLETE)
├── plan.md              # This file (IN PROGRESS)
├── research.md          # Phase 0 output (TO BE CREATED)
├── data-model.md        # Phase 1 output (TO BE CREATED)
├── quickstart.md        # Phase 1 output (TO BE CREATED)
├── contracts/           # Phase 1 output (TO BE CREATED)
│   └── chatkit-endpoint.yaml
├── checklists/
│   └── requirements.md  # Specification quality checklist (COMPLETE)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── agents/
│   │   ├── orchestrator.py          # [REMOVE] Current manual orchestration
│   │   ├── chatkit_server.py        # [CREATE] ChatKitServer subclass
│   │   ├── store_adapter.py         # [CREATE] Store interface adapter
│   │   └── prompts.py               # [PRESERVE] System prompt (unchanged)
│   ├── api/
│   │   └── routes/
│   │       ├── chat.py              # [PRESERVE] Existing endpoint (may deprecate later)
│   │       └── chatkit.py           # [CREATE] New /chatkit endpoint
│   ├── mcp/
│   │   ├── mcp_server.py            # [PRESERVE] FastMCP tools (unchanged)
│   │   └── __init__.py              # [PRESERVE] (unchanged)
│   ├── models/
│   │   ├── conversation.py          # [PRESERVE] Conversation model (unchanged)
│   │   └── message.py               # [PRESERVE] Message model (unchanged)
│   ├── services/
│   │   └── conversation_service.py  # [PRESERVE] (unchanged, may be used by Store)
│   └── config/
│       └── settings.py              # [PRESERVE] (unchanged)
└── tests/
    └── [TO BE DETERMINED]           # Manual validation checklist

frontend/
├── src/
│   ├── components/
│   │   ├── ChatInterface.tsx        # [REMOVE] Custom chat component
│   │   └── ChatKitChat.tsx          # [CREATE] ChatKit wrapper component
│   ├── app/
│   │   └── chat/
│   │       └── page.tsx             # [MODIFY] Use ChatKitChat instead of ChatInterface
│   └── lib/
│       └── [PRESERVE]               # All other code unchanged
└── tests/
    └── [TO BE DETERMINED]           # Manual validation checklist
```

**Structure Decision**: Web application structure (backend + frontend). Backend changes isolated to `agents/` directory (new chatkit_server.py, store_adapter.py; remove orchestrator.py) and `api/routes/` (new chatkit.py endpoint). Frontend changes isolated to `components/` (new ChatKitChat.tsx; remove ChatInterface.tsx) and one page update. All other directories preserved unchanged.

## Complexity Tracking

> **No violations requiring justification**

This migration simplifies the codebase by replacing manual orchestration with official SDK patterns. No new complexity introduced.

## Architecture Overview

### Current Architecture (Before Migration)

```text
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                 │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  ChatInterface.tsx (Custom React Component)                │ │
│  │  - Manual message rendering                                │ │
│  │  - Custom state management                                 │ │
│  │  - Manual API calls to /api/{user_id}/chat                │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │ HTTP POST
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         BACKEND                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  /api/{user_id}/chat (FastAPI Route)                      │ │
│  │  - Extract user_id from path                              │ │
│  │  - Load conversation history                              │ │
│  │  - Call AgentOrchestrator                                 │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  AgentOrchestrator (Manual Implementation)                │ │
│  │  - Initialize OpenAI client (Cerebras)                    │ │
│  │  - Build messages array manually                          │ │
│  │  - Call chat.completions.create()                         │ │
│  │  - Parse tool_calls manually                              │ │
│  │  - Execute tools via handle_tool_calls()                  │ │
│  │  - Loop until finish_reason != "tool_calls"               │ │
│  │  - ~100 lines of orchestration logic                      │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  MCP Server (FastMCP)                                      │ │
│  │  - 5 tools: add_task, list_tasks, complete_task,          │ │
│  │    delete_task, update_task                                │ │
│  │  - Direct function calls from orchestrator                │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Database (Neon PostgreSQL)                                │ │
│  │  - Conversation model (id, user_id, created_at)           │ │
│  │  - Message model (id, conversation_id, role, content)     │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘

ISSUES:
❌ Manual OpenAI client usage (not OpenAI Agents SDK)
❌ Custom chat UI (not OpenAI ChatKit)
❌ Manual tool calling loop (error-prone)
❌ ~100 lines of orchestration boilerplate
```

### Target Architecture (After Migration)

```text
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                 │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  <ChatKit> Component (@openai/chatkit-react)              │ │
│  │  - Automatic message rendering                            │ │
│  │  - Built-in state management                              │ │
│  │  - Streaming support                                       │ │
│  │  - apiUrl="/chatkit"                                       │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │ HTTP POST
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         BACKEND                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  /chatkit (FastAPI Route)                                  │ │
│  │  - Call server.process(request.body(), context={})        │ │
│  │  - Return StreamingResponse or JSONResponse               │ │
│  │  - ~5 lines of code                                       │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  TodoChatKitServer (ChatKitServer subclass)               │ │
│  │  - respond() method (~20 lines)                           │ │
│  │  - Load history: store.load_thread_items()                │ │
│  │  - Convert: simple_to_agent_input()                       │ │
│  │  - Create: AgentContext(thread, store, context)           │ │
│  │  - Run: Runner.run_streamed(agent, input, context)        │ │
│  │  - Stream: stream_agent_response(agent_context, result)   │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Agent (OpenAI Agents SDK)                                 │ │
│  │  - name="TodoAssistant"                                    │ │
│  │  - instructions="Use MCP tools..."                         │ │
│  │  - model="llama-3.3-70b"                                   │ │
│  │  - mcp_servers=[MCPServerStreamableHttp(...)]             │ │
│  │  - Automatic tool calling loop                            │ │
│  │  - Built-in error handling                                │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  MCPServerStreamableHttp                                   │ │
│  │  - url="http://localhost:8001/mcp"                         │ │
│  │  - cache_tools_list=True                                   │ │
│  │  - Connects to existing FastMCP server                    │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  MCP Server (FastMCP) - UNCHANGED                          │ │
│  │  - 5 tools: add_task, list_tasks, complete_task,          │ │
│  │    delete_task, update_task                                │ │
│  │  - Accessed via HTTP by MCPServerStreamableHttp           │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Store Adapter (ChatKit Store Interface)                  │ │
│  │  - 13 methods: load_thread, save_thread, etc.             │ │
│  │  - Adapts ThreadMetadata ↔ Conversation                   │ │
│  │  - Adapts ThreadItem ↔ Message                            │ │
│  │  - Preserves existing database schema                     │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Database (Neon PostgreSQL) - UNCHANGED                    │ │
│  │  - Conversation model (id, user_id, created_at)           │ │
│  │  - Message model (id, conversation_id, role, content)     │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘

BENEFITS:
✅ OpenAI Agents SDK (Phase III compliant)
✅ OpenAI ChatKit (Phase III compliant)
✅ Automatic tool calling (no manual loop)
✅ ~20 lines of orchestration (80% reduction)
✅ Official SDK patterns (maintainable)
✅ 100% functional parity (zero regressions)
```

### Key Architectural Changes

| Component | Before | After | Change Type |
|-----------|--------|-------|-------------|
| Frontend Chat UI | Custom ChatInterface | ChatKit React Component | **REPLACE** |
| Backend Orchestration | Manual OpenAI client | Agent + Runner + ChatKitServer | **REPLACE** |
| Tool Integration | Direct function calls | MCPServerStreamableHttp | **WRAP** |
| Conversation Storage | Direct DB access | Store adapter interface | **WRAP** |
| MCP Server | FastMCP tools | FastMCP tools (unchanged) | **PRESERVE** |
| Database Models | Conversation + Message | Conversation + Message (unchanged) | **PRESERVE** |
| Authentication | Better Auth JWT | Better Auth JWT (unchanged) | **PRESERVE** |

## Phase 0: Research & Pattern Extraction

### Objective

Extract all relevant implementation patterns, code examples, and best practices from the two knowledge base files to ensure the migration follows official SDK patterns exactly.

### Research Tasks

#### Task 1: OpenAI Agents SDK Patterns (OpenAI-Agents-SDK-Knowledge.md)

**Focus Areas:**
1. **Agent Initialization Pattern**
   - How to create Agent with name, instructions, model, mcp_servers
   - MCPServerStreamableHttp configuration (url, timeout, cache_tools_list, max_retry_attempts)
   - Async context manager pattern for MCP server lifecycle

2. **Runner Execution Pattern**
   - Runner.run_streamed() signature and usage
   - How to pass input items and context
   - Streaming response handling

3. **MCP Integration Pattern**
   - MCPServerStreamableHttp vs direct tool registration
   - Why cache_tools_list=True is recommended
   - HTTP URL format for FastMCP server connection

4. **Session Management**
   - SQLiteSession pattern (NOT needed for ChatKit integration)
   - Why ChatKit Store replaces session management

**Expected Findings:**
```python
# Pattern from knowledge base (lines 450-470)
async with MCPServerStreamableHttp(
    name="TodoMCP",
    params={"url": "http://localhost:8001/mcp", "timeout": 10},
    cache_tools_list=True,
    max_retry_attempts=3,
) as server:
    agent = Agent(
        name="TodoAssistant",
        instructions="Use MCP tools to manage tasks",
        model="llama-3.3-70b",
        mcp_servers=[server]
    )
    result = Runner.run_streamed(agent, input_items, context=agent_context)
```

#### Task 2: ChatKit SDK Patterns (Chatkit-SDK-Documentation.md)

**Focus Areas:**
1. **ChatKitServer Implementation**
   - respond() method signature and implementation
   - How to yield ThreadStreamEvent objects
   - AgentContext creation and usage

2. **Store Interface**
   - All 13 method signatures
   - Pagination pattern (after, limit, order parameters)
   - ThreadMetadata and ThreadItem serialization

3. **Integration Helpers**
   - simple_to_agent_input() usage and behavior
   - stream_agent_response() usage and behavior
   - How these bridge ChatKit and Agents SDK

4. **FastAPI Integration**
   - server.process() method
   - StreamingResult vs JSONResult handling
   - Endpoint implementation pattern

**Expected Findings:**
```python
# Pattern from knowledge base (lines 2850-2900)
class TodoChatKitServer(ChatKitServer[dict]):
    async def respond(self, thread, input_user_message, context):
        items_page = await self.store.load_thread_items(
            thread.id, after=None, limit=20, order="asc", context=context
        )
        input_items = await simple_to_agent_input(items_page.data)
        agent_context = AgentContext(
            thread=thread, store=self.store, request_context=context
        )
        result = Runner.run_streamed(assistant, input_items, context=agent_context)
        async for event in stream_agent_response(agent_context, result):
            yield event
```

#### Task 3: Store Adapter Pattern

**Focus Areas:**
1. **Method Signatures**
   - load_thread(thread_id, context) -> ThreadMetadata
   - save_thread(thread, context) -> None
   - load_thread_items(thread_id, after, limit, order, context) -> Page[ThreadItem]
   - add_thread_item(thread_id, item, context) -> None
   - (9 more methods)

2. **Serialization Strategy**
   - ThreadMetadata.id ↔ Conversation.id
   - ThreadItem types ↔ Message.content JSON
   - Pagination cursor handling

3. **User Isolation**
   - How context parameter carries user_id
   - WHERE clauses for multi-tenancy

**Expected Findings:**
```python
# Pattern from knowledge base (lines 2680-2750)
class PostgresStore(Store[RequestContext]):
    async def load_thread(self, thread_id: str, context: RequestContext):
        with psycopg.connect(self._conninfo) as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT data FROM threads WHERE id = %s AND user_id = %s",
                (thread_id, context.user_id)
            )
            row = cur.fetchone()
            if not row:
                raise NotFoundError(f"Thread {thread_id} not found")
            return ThreadMetadata.model_validate(row[0])
```

#### Task 4: Frontend ChatKit Integration

**Focus Areas:**
1. **ChatKit Component Usage**
   - Import statement
   - Props: apiUrl, threadId, placeholder
   - Styling and customization

2. **API Connection**
   - How ChatKit calls /chatkit endpoint
   - Request/response format
   - Streaming event handling

**Expected Findings:**
```typescript
// Pattern from knowledge base (lines 2940-2950)
import { ChatKit } from '@openai/chatkit-react';
import '@openai/chatkit-react/styles.css';

<ChatKit
  apiUrl="http://localhost:8000/chatkit"
  threadId="user_123"
  placeholder="Ask me about your tasks..."
/>
```

### Research Deliverable

Create `research.md` with:
- All extracted patterns organized by component
- Code examples with line references to knowledge base
- Decision rationale for each pattern choice
- Alternatives considered and why rejected

## Phase 1: Design & Contracts

### Data Model (data-model.md)

**Objective**: Document how ChatKit types map to existing database models.

#### Entity Mapping

**ThreadMetadata ↔ Conversation**
```python
# ChatKit Type
ThreadMetadata(
    id: str,              # Maps to Conversation.id
    created_at: datetime  # Maps to Conversation.created_at
)

# Existing Model (UNCHANGED)
class Conversation(SQLModel, table=True):
    id: str = Field(primary_key=True)
    user_id: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**ThreadItem ↔ Message**
```python
# ChatKit Types (Union)
UserMessageItem(id, thread_id, created_at, content, attachments, quoted_text)
AssistantMessageItem(id, thread_id, created_at, content)
ToolCallItem(id, thread_id, created_at, name, arguments, output)

# Existing Model (UNCHANGED)
class Message(SQLModel, table=True):
    id: str = Field(primary_key=True)
    conversation_id: str = Field(foreign_key="conversation.id", index=True)
    role: str  # "user", "assistant", "tool"
    content: str  # JSON-serialized ThreadItem
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**Serialization Strategy**:
- Store entire ThreadItem as JSON in Message.content
- Use ThreadItem.model_dump(mode="json") for serialization
- Use ThreadItem.model_validate(json_data) for deserialization
- Preserve all ThreadItem fields (attachments, quoted_text, tool arguments, etc.)

#### Store Adapter Interface

**Context Type**:
```python
@dataclass
class RequestContext:
    user_id: str  # For multi-tenancy isolation
```

**Store Methods** (13 total):
1. `load_thread(thread_id, context) -> ThreadMetadata`
2. `save_thread(thread, context) -> None`
3. `load_threads(limit, after, order, context) -> Page[ThreadMetadata]`
4. `load_thread_items(thread_id, after, limit, order, context) -> Page[ThreadItem]`
5. `add_thread_item(thread_id, item, context) -> None`
6. `save_item(thread_id, item, context) -> None`
7. `load_item(thread_id, item_id, context) -> ThreadItem`
8. `delete_thread(thread_id, context) -> None`
9. `delete_thread_item(thread_id, item_id, context) -> None`
10. `save_attachment(attachment, context) -> None`
11. `load_attachment(attachment_id, context) -> Attachment`
12. `delete_attachment(attachment_id, context) -> None`
13. `generate_item_id(item_type, thread, context) -> str`

**Pagination Pattern**:
- Cursor-based (not offset-based)
- `after` parameter: last item ID from previous page
- `limit` parameter: 20-50 items (tune for model context budget)
- `order` parameter: "asc" for chronological (required for agent input)

### API Contracts (contracts/chatkit-endpoint.yaml)

**Objective**: Define the /chatkit endpoint contract.

```yaml
openapi: 3.0.0
info:
  title: ChatKit Endpoint
  version: 1.0.0
paths:
  /chatkit:
    post:
      summary: ChatKit unified endpoint
      description: Handles all ChatKit operations (send message, load history, actions)
      requestBody:
        required: true
        content:
          application/json:
            schema:
              oneOf:
                - $ref: '#/components/schemas/SendMessageRequest'
                - $ref: '#/components/schemas/LoadHistoryRequest'
                - $ref: '#/components/schemas/ActionRequest'
      responses:
        '200':
          description: Success (JSON or SSE stream)
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/JSONResponse'
            text/event-stream:
              schema:
                type: string
                description: Server-Sent Events stream

components:
  schemas:
    SendMessageRequest:
      type: object
      properties:
        thread_id:
          type: string
        message:
          type: string

    LoadHistoryRequest:
      type: object
      properties:
        thread_id:
          type: string
        after:
          type: string
          nullable: true
        limit:
          type: integer
          default: 20

    ActionRequest:
      type: object
      properties:
        thread_id:
          type: string
        action:
          type: object
          properties:
            type:
              type: string
            data:
              type: object
```

### Quickstart Guide (quickstart.md)

**Objective**: Provide step-by-step setup instructions for developers.

**Contents**:
1. Prerequisites (Python 3.11, Node.js 18+, PostgreSQL)
2. Install dependencies (pip install openai-agents-python openai-chatkit, npm install @openai/chatkit-react)
3. Environment variables (CEREBRAS_API_KEY, DATABASE_URL, MCP_SERVER_URL)
4. Start MCP server (python -m src.mcp.mcp_server)
5. Start backend (uvicorn src.main:app --reload)
6. Start frontend (npm run dev)
7. Test /chatkit endpoint (curl examples)
8. Verify Phase III compliance (run audit script)

## Implementation Strategy

### Step-by-Step Migration Plan

#### Step 1: Backend - Create Store Adapter (store_adapter.py)

**Objective**: Implement ChatKit Store interface as adapter over existing Conversation/Message models.

**Implementation**:
```python
from chatkit.store import Store, NotFoundError
from chatkit.types import ThreadMetadata, ThreadItem, Page
from src.models.conversation import Conversation
from src.models.message import Message
from dataclasses import dataclass

@dataclass
class RequestContext:
    user_id: str

class PostgresStoreAdapter(Store[RequestContext]):
    def __init__(self, db_session):
        self.db = db_session

    async def load_thread(self, thread_id: str, context: RequestContext) -> ThreadMetadata:
        # Query: SELECT * FROM conversation WHERE id = ? AND user_id = ?
        # Convert Conversation → ThreadMetadata
        pass

    async def load_thread_items(
        self, thread_id: str, after: str | None, limit: int, order: str, context: RequestContext
    ) -> Page[ThreadItem]:
        # Query: SELECT * FROM message WHERE conversation_id = ?
        #        AND created_at > (SELECT created_at FROM message WHERE id = ?)
        #        ORDER BY created_at ASC LIMIT ?
        # Deserialize Message.content → ThreadItem
        # Return Page with pagination cursor
        pass

    # ... implement remaining 11 methods
```

**Key Decisions**:
- Use existing database session (no new connection pool)
- Serialize ThreadItem to Message.content as JSON
- Implement cursor-based pagination with created_at + id
- Filter all queries by context.user_id for multi-tenancy

**Testing**:
- Unit tests for each Store method
- Verify ThreadItem serialization/deserialization
- Verify pagination cursor logic
- Verify user_id isolation

#### Step 2: Backend - Create ChatKitServer (chatkit_server.py)

**Objective**: Implement ChatKitServer subclass with Agent + Runner integration.

**Implementation**:
```python
from chatkit.server import ChatKitServer
from chatkit.agents import AgentContext, simple_to_agent_input, stream_agent_response
from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp
from src.agents.prompts import get_system_prompt

# Initialize Agent with MCP integration
async def create_agent():
    async with MCPServerStreamableHttp(
        name="TodoMCP",
        params={"url": "http://localhost:8001/mcp", "timeout": 10},
        cache_tools_list=True,
        max_retry_attempts=3,
    ) as server:
        return Agent(
            name="TodoAssistant",
            instructions=get_system_prompt(),
            model="llama-3.3-70b",
            mcp_servers=[server]
        )

class TodoChatKitServer(ChatKitServer[RequestContext]):
    def __init__(self, store: PostgresStoreAdapter):
        super().__init__(store=store)
        self.agent = None  # Initialize in async context

    async def respond(self, thread, input_user_message, context):
        # Ensure agent is initialized
        if not self.agent:
            self.agent = await create_agent()

        # Load recent history (20 items, ascending order)
        items_page = await self.store.load_thread_items(
            thread.id, after=None, limit=20, order="asc", context=context
        )

        # Convert ChatKit items to agent input
        input_items = await simple_to_agent_input(items_page.data)

        # Create agent context
        agent_context = AgentContext(
            thread=thread,
            store=self.store,
            request_context=context
        )

        # Run agent with streaming
        result = Runner.run_streamed(self.agent, input_items, context=agent_context)

        # Stream ChatKit events
        async for event in stream_agent_response(agent_context, result):
            yield event
```

**Key Decisions**:
- Agent lifecycle: Create once, reuse across requests (stateless agent)
- MCP server: Use async context manager for proper cleanup
- History limit: 20 items (tune based on model context budget)
- System prompt: Reuse existing get_system_prompt() function

**Testing**:
- Integration test: Send message → verify agent response
- Integration test: Multi-turn conversation → verify history loading
- Integration test: Tool calling → verify MCP tools execute
- Integration test: Error handling → verify graceful degradation

#### Step 3: Backend - Create /chatkit Endpoint (api/routes/chatkit.py)

**Objective**: Add FastAPI endpoint that calls server.process().

**Implementation**:
```python
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse, Response
from chatkit.server import StreamingResult
from src.agents.chatkit_server import TodoChatKitServer
from src.agents.store_adapter import PostgresStoreAdapter, RequestContext
from src.database import get_db_session

router = APIRouter()

# Initialize server (singleton)
store = PostgresStoreAdapter(get_db_session())
chatkit_server = TodoChatKitServer(store=store)

@router.post("/chatkit")
async def chatkit_endpoint(request: Request):
    """
    ChatKit unified endpoint.

    Handles all ChatKit operations:
    - Send message
    - Load history
    - Execute actions

    Returns:
    - StreamingResponse (SSE) for streaming operations
    - JSONResponse for non-streaming operations
    """
    # Extract user_id from request (JWT token, header, etc.)
    user_id = request.headers.get("X-User-ID")  # TODO: Extract from JWT

    # Create context
    context = RequestContext(user_id=user_id)

    # Process request
    result = await chatkit_server.process(await request.body(), context=context)

    # Return appropriate response type
    if isinstance(result, StreamingResult):
        return StreamingResponse(result, media_type="text/event-stream")
    return Response(content=result.json, media_type="application/json")
```

**Key Decisions**:
- User ID extraction: From JWT token (Better Auth integration)
- Server lifecycle: Singleton instance (stateless, reusable)
- Error handling: Let ChatKit SDK handle errors (returns error events)

**Testing**:
- Integration test: POST /chatkit → verify response
- Integration test: Streaming → verify SSE events
- Integration test: User isolation → verify user_id filtering

#### Step 4: Frontend - Create ChatKit Component (components/ChatKitChat.tsx)

**Objective**: Replace custom ChatInterface with ChatKit React component.

**Implementation**:
```typescript
'use client';

import { ChatKit } from '@openai/chatkit-react';
import '@openai/chatkit-react/styles.css';

interface ChatKitChatProps {
  userId: string;
}

export function ChatKitChat({ userId }: ChatKitChatProps) {
  return (
    <div className="h-full w-full">
      <ChatKit
        apiUrl={`${process.env.NEXT_PUBLIC_API_URL}/chatkit`}
        threadId={userId}  // Use user_id as thread_id
        placeholder="Ask me about your tasks..."
        headers={{
          'X-User-ID': userId  // Pass user_id for backend isolation
        }}
      />
    </div>
  );
}
```

**Key Decisions**:
- Thread ID: Use user_id (one conversation per user for MVP)
- API URL: From environment variable
- Headers: Pass user_id for backend authentication
- Styling: Use default ChatKit styles (customize later if needed)

**Testing**:
- Manual test: Render component → verify UI displays
- Manual test: Send message → verify backend receives request
- Manual test: Streaming → verify messages appear in real-time

#### Step 5: Frontend - Update Chat Page (app/chat/page.tsx)

**Objective**: Replace ChatInterface with ChatKitChat.

**Implementation**:
```typescript
import { ChatKitChat } from '@/components/ChatKitChat';
import { getCurrentUser } from '@/lib/auth';  // Better Auth helper

export default async function ChatPage() {
  const user = await getCurrentUser();

  if (!user) {
    redirect('/login');
  }

  return (
    <main className="h-screen">
      <ChatKitChat userId={user.id} />
    </main>
  );
}
```

**Key Decisions**:
- Authentication: Use existing Better Auth helpers
- Layout: Full-screen chat interface
- User ID: Pass from authenticated session

**Testing**:
- Manual test: Navigate to /chat → verify ChatKit renders
- Manual test: Unauthenticated → verify redirect to login

#### Step 6: Deprecate Old Implementation

**Objective**: Remove orchestrator.py and ChatInterface.tsx after migration is verified.

**Actions**:
1. Run full regression test suite
2. Verify Phase III compliance audit passes
3. Remove backend/src/agents/orchestrator.py
4. Remove frontend/src/components/ChatInterface.tsx
5. Update imports and references
6. Commit changes with clear migration message

**Testing**:
- Verify no broken imports
- Verify all tests still pass
- Verify application runs without errors

## Technical Decisions

### Decision 1: MCP Integration Pattern

**Context**: Need to connect OpenAI Agents SDK to existing FastMCP server.

**Options Considered**:

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| **A. MCPServerStreamableHttp** (CHOSEN) | Connect via HTTP URL | ✅ Preserves existing MCP server<br>✅ Official SDK pattern<br>✅ cache_tools_list=True for performance<br>✅ No tool definition changes | ⚠️ Requires MCP server running on HTTP |
| B. Direct tool registration (Agent.tools) | Register tools directly with Agent | ✅ No HTTP dependency | ❌ Requires rewriting tool definitions<br>❌ Not MCP-compliant<br>❌ Violates "preserve MCP server" constraint |
| C. Custom MCP client | Build custom integration | ✅ Full control | ❌ Reinventing the wheel<br>❌ Not official SDK pattern<br>❌ High maintenance burden |

**Decision**: Option A (MCPServerStreamableHttp)

**Rationale**:
- Official SDK pattern from knowledge base (lines 450-470)
- Preserves existing FastMCP server unchanged
- cache_tools_list=True caches tool definitions for performance
- Async context manager handles lifecycle correctly
- Recommended pattern in OpenAI Agents SDK documentation

**Implementation**:
```python
async with MCPServerStreamableHttp(
    name="TodoMCP",
    params={"url": "http://localhost:8001/mcp", "timeout": 10},
    cache_tools_list=True,
    max_retry_attempts=3,
) as server:
    agent = Agent(
        name="TodoAssistant",
        instructions=get_system_prompt(),
        model="llama-3.3-70b",
        mcp_servers=[server]  # NOT Agent.tools
    )
```

### Decision 2: Store Adapter Pattern

**Context**: Need to implement ChatKit Store interface over existing Conversation/Message models without schema changes.

**Options Considered**:

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| **A. Adapter Pattern** (CHOSEN) | Implement Store interface as adapter | ✅ Zero schema changes<br>✅ Preserves existing models<br>✅ Clean separation of concerns | ⚠️ Requires serialization logic |
| B. Modify existing models | Add ChatKit fields to models | ✅ Direct mapping | ❌ Schema changes required<br>❌ Breaks existing code<br>❌ Violates constraints |
| C. Dual storage | Separate tables for ChatKit | ✅ Clean separation | ❌ Data duplication<br>❌ Sync complexity<br>❌ Schema changes |

**Decision**: Option A (Adapter Pattern)

**Rationale**:
- Zero schema changes (constitutional requirement)
- ThreadItem serializes cleanly to JSON (Message.content field)
- Store interface provides clean abstraction
- Existing ConversationService can be reused internally

**Serialization Strategy**:
```python
# ThreadItem → Message.content (JSON)
message = Message(
    id=generate_id(),
    conversation_id=thread_id,
    role="user",  # or "assistant", "tool"
    content=thread_item.model_dump_json(),  # Serialize to JSON
    created_at=datetime.utcnow()
)

# Message.content → ThreadItem
thread_item = ThreadItem.model_validate_json(message.content)
```

### Decision 3: Agent Lifecycle Management

**Context**: Need to decide when to create Agent instance (per-request vs singleton).

**Options Considered**:

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| **A. Singleton Agent** (CHOSEN) | Create once, reuse across requests | ✅ Better performance<br>✅ Stateless agent (no session state)<br>✅ MCP connection pooling | ⚠️ Must ensure thread-safety |
| B. Per-request Agent | Create new Agent for each request | ✅ Complete isolation | ❌ Performance overhead<br>❌ MCP reconnection cost<br>❌ Unnecessary for stateless agent |
| C. Agent pool | Pool of Agent instances | ✅ Balance performance/isolation | ❌ Over-engineering<br>❌ Stateless agent doesn't need pooling |

**Decision**: Option A (Singleton Agent)

**Rationale**:
- Agent is stateless (no session state stored in Agent instance)
- Conversation state managed by ChatKit Store (database-persisted)
- MCPServerStreamableHttp can be reused across requests
- Runner.run_streamed() is thread-safe
- Significant performance improvement (no reconnection overhead)

**Implementation**:
```python
class TodoChatKitServer(ChatKitServer[RequestContext]):
    def __init__(self, store):
        super().__init__(store=store)
        self.agent = None  # Lazy initialization

    async def respond(self, thread, input_user_message, context):
        if not self.agent:
            self.agent = await create_agent()  # Create once
        # Use self.agent for all requests
```

### Decision 4: Conversation History Loading

**Context**: Need to decide how many messages to load for agent context.

**Options Considered**:

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| **A. Fixed limit (20-50 items)** (CHOSEN) | Load recent N items | ✅ Predictable token usage<br>✅ Fast queries<br>✅ Recommended by ChatKit docs | ⚠️ May truncate long conversations |
| B. Load all history | Load entire conversation | ✅ Complete context | ❌ Token limit exceeded<br>❌ Slow queries<br>❌ Memory issues |
| C. Smart truncation | Truncate based on token count | ✅ Optimal context usage | ❌ Complex implementation<br>❌ Token counting overhead |

**Decision**: Option A (Fixed limit: 20 items)

**Rationale**:
- ChatKit documentation recommends 20-50 items (line 3210)
- Llama 3.3 70B context window: 128k tokens (~100k usable)
- 20 messages ≈ 5k-10k tokens (safe margin)
- Cursor-based pagination allows loading more if needed
- Can tune limit based on observed usage patterns

**Implementation**:
```python
items_page = await self.store.load_thread_items(
    thread.id,
    after=None,  # Start from beginning
    limit=20,    # Load 20 most recent items
    order="asc", # Chronological order (required for agent)
    context=context
)
```

### Decision 5: Frontend Thread ID Strategy

**Context**: Need to decide how to map users to ChatKit threads.

**Options Considered**:

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| **A. user_id as thread_id** (CHOSEN) | One conversation per user | ✅ Simple mapping<br>✅ Matches current behavior<br>✅ Easy user isolation | ⚠️ Single conversation per user |
| B. Generate thread IDs | Multiple conversations per user | ✅ Multiple conversations | ❌ Requires conversation management UI<br>❌ Out of scope for Phase III |
| C. Session-based threads | Thread per session | ✅ Automatic cleanup | ❌ Loses conversation history<br>❌ Poor UX |

**Decision**: Option A (user_id as thread_id)

**Rationale**:
- Current implementation: One conversation per user
- Maintains functional parity (zero breaking changes)
- Simplifies user isolation (thread_id = user_id)
- Multiple conversations can be added later (future enhancement)

**Implementation**:
```typescript
<ChatKit
  apiUrl="/chatkit"
  threadId={userId}  // Use user_id directly
  headers={{ 'X-User-ID': userId }}
/>
```

### Decision 6: Error Handling Strategy

**Context**: Need to decide how to handle errors in ChatKit integration.

**Options Considered**:

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| **A. Let ChatKit SDK handle** (CHOSEN) | Rely on built-in error handling | ✅ Consistent error format<br>✅ Automatic error events<br>✅ Less code | ⚠️ Less control over error messages |
| B. Custom error handling | Wrap all operations in try/catch | ✅ Full control | ❌ Duplicates SDK error handling<br>❌ More code<br>❌ Inconsistent with SDK patterns |
| C. Hybrid approach | Custom handling for critical errors | ✅ Balance control/simplicity | ❌ Complexity<br>❌ Unclear boundaries |

**Decision**: Option A (Let ChatKit SDK handle)

**Rationale**:
- ChatKit SDK has built-in error handling (returns error events)
- Consistent error format across all operations
- Reduces custom error handling code
- Follows official SDK patterns
- Can add custom handling later if needed

**Implementation**:
```python
# No try/catch needed - ChatKit handles errors
async def respond(self, thread, input_user_message, context):
    # If error occurs, ChatKit SDK yields error event automatically
    result = Runner.run_streamed(self.agent, input_items, context=agent_context)
    async for event in stream_agent_response(agent_context, result):
        yield event  # Includes error events
```

## Risk Assessment & Mitigation

### Risk 1: MCPServerStreamableHttp Connection Failure

**Impact**: High (agent cannot call tools)
**Probability**: Medium (network issues, MCP server down)

**Mitigation**:
1. **Retry logic**: Use max_retry_attempts=3 in MCPServerStreamableHttp
2. **Health check**: Add /health endpoint to MCP server
3. **Graceful degradation**: Agent can still respond without tools (text-only mode)
4. **Monitoring**: Log all MCP connection failures
5. **Fallback**: Keep old /api/{user_id}/chat endpoint temporarily

**Testing**:
- Simulate MCP server down → verify error handling
- Simulate network timeout → verify retry logic
- Verify agent responds gracefully without tools

### Risk 2: Store Adapter Serialization Bugs

**Impact**: High (data corruption, lost messages)
**Probability**: Medium (complex serialization logic)

**Mitigation**:
1. **Comprehensive tests**: Unit test every Store method
2. **Schema validation**: Use Pydantic models for type safety
3. **Rollback plan**: Keep existing ConversationService as backup
4. **Data validation**: Validate ThreadItem before serialization
5. **Logging**: Log all serialization errors with full context

**Testing**:
- Test all ThreadItem types (UserMessageItem, AssistantMessageItem, ToolCallItem)
- Test edge cases (empty content, special characters, large messages)
- Test pagination cursor logic
- Verify user_id isolation

### Risk 3: Functional Regression in Tool Calling

**Impact**: Critical (breaks core functionality)
**Probability**: Medium (different tool calling mechanism)

**Mitigation**:
1. **Regression tests**: Test all 5 MCP tools with natural language examples
2. **Side-by-side testing**: Run old and new implementations in parallel
3. **Verification**: Agent must verify mutations (constitutional requirement)
4. **Rollback**: Keep orchestrator.py until migration verified
5. **Monitoring**: Log all tool calls with parameters and results

**Testing**:
- Test: "Add task to buy milk" → verify add_task called
- Test: "Show my tasks" → verify list_tasks called
- Test: "Complete task 123" → verify complete_task called
- Test: "Delete task 456" → verify delete_task called
- Test: "Update task 789 to 'Buy groceries'" → verify update_task called
- Test multi-turn: "Add 3 tasks, then show them, then delete one"

### Risk 4: ChatKit Frontend Integration Issues

**Impact**: High (users cannot access chat)
**Probability**: Low (simple component replacement)

**Mitigation**:
1. **Incremental rollout**: Test with single user first
2. **Feature flag**: Add toggle to switch between old/new UI
3. **Fallback**: Keep ChatInterface.tsx until verified
4. **Browser testing**: Test on Chrome, Firefox, Safari, Edge
5. **Mobile testing**: Test on iOS and Android browsers

**Testing**:
- Test message sending → verify backend receives request
- Test streaming → verify messages appear in real-time
- Test authentication → verify user_id passed correctly
- Test error states → verify error messages display

### Risk 5: Performance Degradation

**Impact**: Medium (slower responses)
**Probability**: Low (SDK should be faster)

**Mitigation**:
1. **Benchmarking**: Measure response times before/after
2. **Profiling**: Profile Store adapter and ChatKitServer
3. **Optimization**: Tune history limit (20 items default)
4. **Caching**: Use cache_tools_list=True for MCP tools
5. **Monitoring**: Track p50, p95, p99 latencies

**Testing**:
- Benchmark: 100 requests → measure average latency
- Load test: 10 concurrent users → verify no degradation
- Compare: Old vs new implementation latency

## Testing & Validation Strategy

### Phase III Compliance Verification

**Objective**: Verify the migration passes all 6 Phase III requirements.

**Compliance Checklist**:

| Requirement | Verification Method | Expected Result |
|-------------|---------------------|-----------------|
| **#1: MCP Server** | Inspect backend/src/mcp/mcp_server.py | ✅ FastMCP tools unchanged |
| **#2: OpenAI Agents SDK** | Inspect backend/src/agents/chatkit_server.py | ✅ Agent + Runner used (not manual client) |
| **#3: Tool Integration** | Test all 5 MCP tools via agent | ✅ All tools execute successfully |
| **#4: Conversation Persistence** | Inspect Store adapter + database | ✅ Conversation/Message models unchanged |
| **#5: Stateless Architecture** | Inspect ChatKitServer.respond() | ✅ No server-side session state |
| **#6: Frontend ChatKit** | Inspect frontend/src/components/ChatKitChat.tsx | ✅ ChatKit React component used |

**Audit Simulation**:
```bash
# Run Phase III compliance audit script
python scripts/audit_phase3_compliance.py

# Expected output:
# ✅ Requirement #1: MCP Server - PASS
# ✅ Requirement #2: OpenAI Agents SDK - PASS (Agent class found)
# ✅ Requirement #3: Tool Integration - PASS (5 tools verified)
# ✅ Requirement #4: Conversation Persistence - PASS
# ✅ Requirement #5: Stateless Architecture - PASS
# ✅ Requirement #6: Frontend ChatKit - PASS (ChatKit component found)
#
# OVERALL: PASS (6/6 requirements met)
```

### Regression Testing Plan

**Objective**: Verify 100% functional parity with current implementation.

#### Test Suite 1: Natural Language Understanding

**Test all required natural language patterns from constitution:**

| Test Case | Input | Expected Tool Call | Expected Response |
|-----------|-------|-------------------|-------------------|
| TC-NLU-001 | "Add a task to buy milk" | add_task(title="buy milk") | "I've added the task 'buy milk'" |
| TC-NLU-002 | "Remember to call dentist" | add_task(title="call dentist") | "I've added the task 'call dentist'" |
| TC-NLU-003 | "I need to finish the report" | add_task(title="finish the report") | "I've added the task 'finish the report'" |
| TC-NLU-004 | "Show my tasks" | list_tasks() | List of all tasks |
| TC-NLU-005 | "What's pending?" | list_tasks(status="pending") | List of pending tasks |
| TC-NLU-006 | "What have I completed?" | list_tasks(status="completed") | List of completed tasks |
| TC-NLU-007 | "Mark task 123 as done" | complete_task(task_id=123) | "Task 123 marked as complete" |
| TC-NLU-008 | "I finished buying milk" | complete_task(task_id=...) | "Task marked as complete" |
| TC-NLU-009 | "Delete task 456" | delete_task(task_id=456) | "Task 456 deleted" |
| TC-NLU-010 | "Remove the dentist task" | delete_task(task_id=...) | "Task deleted" |
| TC-NLU-011 | "Update task 789 to 'Buy groceries'" | update_task(task_id=789, title="Buy groceries") | "Task 789 updated" |
| TC-NLU-012 | "Change the report task to 'Finish Q4 report'" | update_task(task_id=..., title="Finish Q4 report") | "Task updated" |

**Verification Method**:
- Run each test case through new ChatKit implementation
- Compare tool calls and responses with current implementation
- All 12 test cases must pass identically

#### Test Suite 2: Multi-Turn Conversations

**Test conversation history and context management:**

| Test Case | Conversation Flow | Expected Behavior |
|-----------|-------------------|-------------------|
| TC-CONV-001 | User: "Add task to buy milk"<br>Agent: "Added"<br>User: "Show my tasks" | Agent lists tasks including "buy milk" |
| TC-CONV-002 | User: "Add 3 tasks: milk, bread, eggs"<br>Agent: "Added 3 tasks"<br>User: "Delete the milk task" | Agent deletes correct task by referencing context |
| TC-CONV-003 | User: "What's my first task?"<br>Agent: "Task 1: buy milk"<br>User: "Mark it as done" | Agent completes task 1 using context |
| TC-CONV-004 | User: "Add task A"<br>User: "Add task B"<br>User: "Show all tasks" | Agent lists both tasks A and B |
| TC-CONV-005 | User: "Complete all pending tasks"<br>Agent: "Completed 5 tasks"<br>User: "Show completed" | Agent shows 5 completed tasks |

**Verification Method**:
- Execute multi-turn conversations
- Verify agent maintains context across turns
- Verify conversation history loads correctly

#### Test Suite 3: State Verification (Constitutional Requirement)

**Test agent verification mandate:**

| Test Case | Scenario | Expected Verification |
|-----------|----------|----------------------|
| TC-VERIFY-001 | Delete 3 tasks | Agent queries before (12 tasks) → deletes → queries after (9 tasks) → reports "Deleted 3 tasks, verified count reduced from 12 to 9" |
| TC-VERIFY-002 | Complete 5 tasks | Agent queries before → completes → queries after → reports verified count |
| TC-VERIFY-003 | Add 2 tasks | Agent adds → queries after → reports verified 2 new tasks |
| TC-VERIFY-004 | Update task title | Agent updates → queries after → reports verified title changed |

**Verification Method**:
- Inspect agent reasoning logs
- Verify agent calls list_tasks before and after mutations
- Verify agent reports verification results to user

#### Test Suite 4: Error Handling

**Test graceful error handling:**

| Test Case | Error Scenario | Expected Behavior |
|-----------|----------------|-------------------|
| TC-ERROR-001 | MCP server down | Agent responds: "I'm unable to access task tools right now. Please try again later." |
| TC-ERROR-002 | Invalid task ID | Agent responds: "Task not found. Please check the task ID." |
| TC-ERROR-003 | Database connection lost | Agent responds: "I'm experiencing technical difficulties. Please try again." |
| TC-ERROR-004 | Timeout (>30s) | Agent responds: "Request took too long. Please try again." |

**Verification Method**:
- Simulate error conditions
- Verify agent handles errors gracefully
- Verify no crashes or data corruption

### Manual Test Scenarios

**Objective**: End-to-end validation from user perspective.

#### Scenario 1: New User First Conversation

**Steps**:
1. Navigate to /chat (unauthenticated)
2. Verify redirect to /login
3. Log in with test credentials
4. Verify ChatKit component renders
5. Send message: "Hello"
6. Verify agent responds
7. Send message: "Add a task to buy milk"
8. Verify task created
9. Send message: "Show my tasks"
10. Verify task list displays

**Expected Result**: Complete flow works identically to current implementation.

#### Scenario 2: Existing User Returning

**Steps**:
1. Log in as user with existing conversation history
2. Verify ChatKit loads previous messages
3. Send new message referencing previous context
4. Verify agent understands context
5. Execute tool call (e.g., complete task)
6. Verify tool executes successfully

**Expected Result**: Conversation history preserved, context maintained.

#### Scenario 3: Complex Multi-Tool Workflow

**Steps**:
1. User: "Add 5 tasks: milk, bread, eggs, butter, cheese"
2. Verify agent adds all 5 tasks
3. User: "Show my pending tasks"
4. Verify agent lists 5 tasks
5. User: "Complete the milk and bread tasks"
6. Verify agent completes 2 tasks
7. User: "Delete the eggs task"
8. Verify agent deletes 1 task
9. User: "Show all tasks"
10. Verify agent shows 2 pending + 2 completed = 4 total

**Expected Result**: All tool calls execute correctly, state verified.

#### Scenario 4: Error Recovery

**Steps**:
1. Stop MCP server
2. User: "Add a task"
3. Verify agent shows error message
4. Restart MCP server
5. User: "Add a task"
6. Verify agent successfully adds task

**Expected Result**: Graceful error handling, automatic recovery.

### Post-Migration Audit Simulation

**Objective**: Simulate Phase III Auditor review process.

**Audit Steps**:

1. **Code Inspection**:
   ```bash
   # Verify OpenAI Agents SDK usage
   grep -r "from agents import Agent, Runner" backend/src/
   # Expected: Found in chatkit_server.py

   # Verify ChatKit usage
   grep -r "from '@openai/chatkit-react'" frontend/src/
   # Expected: Found in ChatKitChat.tsx

   # Verify no manual OpenAI client
   grep -r "OpenAI()" backend/src/agents/
   # Expected: Not found (removed from orchestrator.py)
   ```

2. **Functional Testing**:
   - Execute all 12 NLU test cases → 100% pass rate
   - Execute all 5 multi-turn test cases → 100% pass rate
   - Execute all 4 verification test cases → 100% pass rate
   - Execute all 4 error handling test cases → 100% pass rate

3. **Architecture Review**:
   - Verify MCP server unchanged
   - Verify database schema unchanged
   - Verify stateless architecture preserved
   - Verify authentication unchanged

4. **Compliance Report**:
   ```
   Phase III Compliance Audit Report
   ==================================

   Requirement #1: MCP Server
   Status: ✅ PASS
   Evidence: FastMCP tools in backend/src/mcp/mcp_server.py unchanged

   Requirement #2: OpenAI Agents SDK
   Status: ✅ PASS
   Evidence: Agent + Runner in backend/src/agents/chatkit_server.py

   Requirement #3: Tool Integration
   Status: ✅ PASS
   Evidence: All 5 MCP tools execute via MCPServerStreamableHttp

   Requirement #4: Conversation Persistence
   Status: ✅ PASS
   Evidence: Store adapter over Conversation/Message models

   Requirement #5: Stateless Architecture
   Status: ✅ PASS
   Evidence: ChatKitServer.respond() loads history from database

   Requirement #6: Frontend ChatKit
   Status: ✅ PASS
   Evidence: ChatKit React component in frontend/src/components/ChatKitChat.tsx

   OVERALL: ✅ PASS (6/6 requirements met)
   ```

### Acceptance Criteria

**Migration is considered successful when:**

1. ✅ Phase III compliance audit shows PASS on all 6 requirements
2. ✅ All 12 NLU test cases pass (100% functional parity)
3. ✅ All 5 multi-turn conversation test cases pass
4. ✅ All 4 state verification test cases pass
5. ✅ All 4 error handling test cases pass
6. ✅ All 4 manual test scenarios complete successfully
7. ✅ Response latency within 10% of current implementation
8. ✅ Zero schema changes to database
9. ✅ Zero breaking changes to API contracts
10. ✅ Code reduction: Backend orchestration reduced by 80%

## File-by-File Change Summary

### Backend Files

#### 🆕 CREATE: backend/src/agents/chatkit_server.py (~150 lines)

**Purpose**: ChatKitServer subclass with Agent + Runner integration

**Key Components**:
- `create_agent()`: Initialize Agent with MCPServerStreamableHttp
- `TodoChatKitServer`: ChatKitServer subclass
- `respond()`: Load history, run agent, stream events (~20 lines)

**Dependencies**:
- chatkit.server (ChatKitServer)
- chatkit.agents (AgentContext, simple_to_agent_input, stream_agent_response)
- agents (Agent, Runner)
- agents.mcp (MCPServerStreamableHttp)
- src.agents.prompts (get_system_prompt)

**Testing**: Integration tests for agent execution, tool calling, streaming

#### 🆕 CREATE: backend/src/agents/store_adapter.py (~400 lines)

**Purpose**: ChatKit Store interface adapter over Conversation/Message models

**Key Components**:
- `RequestContext`: Dataclass with user_id
- `PostgresStoreAdapter`: Store[RequestContext] implementation
- 13 methods: load_thread, save_thread, load_thread_items, etc.
- Serialization helpers: ThreadItem ↔ Message.content JSON

**Dependencies**:
- chatkit.store (Store, NotFoundError)
- chatkit.types (ThreadMetadata, ThreadItem, Page)
- src.models.conversation (Conversation)
- src.models.message (Message)

**Testing**: Unit tests for each Store method, serialization tests, pagination tests

#### 🆕 CREATE: backend/src/api/routes/chatkit.py (~50 lines)

**Purpose**: FastAPI endpoint for ChatKit

**Key Components**:
- `/chatkit` POST endpoint
- Extract user_id from JWT token
- Call server.process()
- Return StreamingResponse or JSONResponse

**Dependencies**:
- fastapi (APIRouter, Request)
- fastapi.responses (StreamingResponse, Response)
- chatkit.server (StreamingResult)
- src.agents.chatkit_server (TodoChatKitServer)
- src.agents.store_adapter (PostgresStoreAdapter, RequestContext)

**Testing**: Integration tests for endpoint, streaming, user isolation

#### ❌ REMOVE: backend/src/agents/orchestrator.py (~276 lines)

**Reason**: Replaced by chatkit_server.py (Agent + Runner pattern)

**Migration Path**:
1. Verify all functionality works with new implementation
2. Run full regression test suite
3. Remove file after successful migration
4. Update imports in any dependent files

#### ✅ PRESERVE: backend/src/agents/prompts.py (unchanged)

**Reason**: System prompt reused by Agent.instructions

**Usage**: `Agent(instructions=get_system_prompt())`

#### ✅ PRESERVE: backend/src/mcp/mcp_server.py (unchanged)

**Reason**: FastMCP tools accessed via MCPServerStreamableHttp

**Integration**: `MCPServerStreamableHttp(params={"url": "http://localhost:8001/mcp"})`

#### ✅ PRESERVE: backend/src/models/conversation.py (unchanged)

**Reason**: Store adapter preserves existing schema

**Usage**: Store.load_thread() queries Conversation table

#### ✅ PRESERVE: backend/src/models/message.py (unchanged)

**Reason**: Store adapter serializes ThreadItem to Message.content JSON

**Usage**: Store.load_thread_items() queries Message table

#### ⚠️ OPTIONAL: backend/src/api/routes/chat.py (may deprecate)

**Current Status**: Existing /api/{user_id}/chat endpoint

**Migration Strategy**:
- Keep temporarily for rollback safety
- Deprecate after /chatkit verified
- Remove in future cleanup phase

### Frontend Files

#### 🆕 CREATE: frontend/src/components/ChatKitChat.tsx (~30 lines)

**Purpose**: ChatKit React component wrapper

**Key Components**:
- `ChatKitChat` component with userId prop
- ChatKit component with apiUrl, threadId, headers
- Default styling from @openai/chatkit-react/styles.css

**Dependencies**:
- @openai/chatkit-react (ChatKit)
- @openai/chatkit-react/styles.css

**Testing**: Manual tests for rendering, message sending, streaming

#### ❌ REMOVE: frontend/src/components/ChatInterface.tsx (~200 lines)

**Reason**: Replaced by ChatKitChat.tsx (official ChatKit component)

**Migration Path**:
1. Update app/chat/page.tsx to use ChatKitChat
2. Verify UI works identically
3. Remove file after successful migration
4. Update imports in any dependent files

#### 🔧 MODIFY: frontend/src/app/chat/page.tsx (~10 lines changed)

**Changes**:
- Import ChatKitChat instead of ChatInterface
- Pass userId prop to ChatKitChat
- Remove custom state management (handled by ChatKit)

**Before**:
```typescript
import { ChatInterface } from '@/components/ChatInterface';
<ChatInterface userId={user.id} />
```

**After**:
```typescript
import { ChatKitChat } from '@/components/ChatKitChat';
<ChatKitChat userId={user.id} />
```

#### ✅ PRESERVE: All other frontend files (unchanged)

**Reason**: Changes isolated to chat UI component only

### Configuration Files

#### ✅ PRESERVE: backend/src/config/settings.py (unchanged)

**Reason**: Existing settings reused (CEREBRAS_API_KEY, DATABASE_URL, etc.)

**Usage**: Agent uses settings.cerebras_api_key, settings.cerebras_model

#### ✅ PRESERVE: .env (unchanged)

**Reason**: No new environment variables required

**Existing Variables**:
- CEREBRAS_API_KEY (used by Agent)
- DATABASE_URL (used by Store adapter)
- MCP_SERVER_URL (used by MCPServerStreamableHttp)

### Summary Statistics

| Metric | Count |
|--------|-------|
| Files Created | 3 (chatkit_server.py, store_adapter.py, chatkit.py, ChatKitChat.tsx) |
| Files Modified | 1 (app/chat/page.tsx) |
| Files Removed | 2 (orchestrator.py, ChatInterface.tsx) |
| Files Preserved | 10+ (all MCP, models, services, config, etc.) |
| Total Lines Added | ~630 lines |
| Total Lines Removed | ~476 lines |
| Net Change | +154 lines (but 80% reduction in orchestration complexity) |

## Implementation Timeline

### Phase 0: Research (1 day)

**Deliverables**:
- research.md with extracted SDK patterns
- Code examples with knowledge base references
- Decision rationale documentation

**Activities**:
- Deep read OpenAI-Agents-SDK-Knowledge.md (1,788 lines)
- Deep read Chatkit-SDK-Documentation.md (3,427 lines)
- Extract all relevant patterns and examples
- Document alternatives considered

### Phase 1: Design (1 day)

**Deliverables**:
- data-model.md with entity mappings
- contracts/chatkit-endpoint.yaml
- quickstart.md with setup instructions

**Activities**:
- Document ThreadMetadata ↔ Conversation mapping
- Document ThreadItem ↔ Message serialization
- Define Store adapter interface
- Create API contract specification
- Write developer setup guide

### Phase 2: Implementation (3-5 days)

**Deliverables**:
- All backend files (chatkit_server.py, store_adapter.py, chatkit.py)
- All frontend files (ChatKitChat.tsx, updated page.tsx)
- Unit tests for Store adapter
- Integration tests for ChatKitServer

**Activities**:
- Day 1: Implement Store adapter + tests
- Day 2: Implement ChatKitServer + tests
- Day 3: Implement /chatkit endpoint + tests
- Day 4: Implement ChatKitChat component
- Day 5: Integration testing and bug fixes

### Phase 3: Testing & Validation (2-3 days)

**Deliverables**:
- All test suites passing (NLU, multi-turn, verification, error handling)
- Manual test scenarios completed
- Phase III compliance audit report (PASS)

**Activities**:
- Day 1: Run regression test suite (12 NLU + 5 multi-turn + 4 verification + 4 error)
- Day 2: Execute manual test scenarios (4 scenarios)
- Day 3: Run Phase III compliance audit, fix any issues

### Phase 4: Cleanup & Documentation (1 day)

**Deliverables**:
- orchestrator.py removed
- ChatInterface.tsx removed
- Updated documentation
- Migration complete

**Activities**:
- Remove deprecated files
- Update imports and references
- Document migration in CHANGELOG
- Create migration guide for future reference

**Total Estimated Time**: 8-10 days

## Next Steps

### After This Plan

1. **User Review**: User reviews this plan and provides feedback
2. **Run /sp.tasks**: Generate actionable task breakdown from this plan
3. **Run /sp.implement**: Execute tasks to implement the migration
4. **Validation**: Run all test suites and compliance audit
5. **Deployment**: Deploy to production after successful validation

### Command Sequence

```bash
# Current: Plan complete
/sp.plan ✅ COMPLETE

# Next: Generate tasks
/sp.tasks

# Then: Implement migration
/sp.implement

# Finally: Validate and deploy
# (manual validation + deployment)
```

### Success Criteria Reminder

Migration is complete when:
- ✅ Phase III compliance audit: PASS (6/6 requirements)
- ✅ Functional parity: 100% (all test cases pass)
- ✅ Performance: Within 10% of current latency
- ✅ Architecture: Zero schema changes, zero breaking changes
- ✅ Code quality: 80% reduction in orchestration complexity

## Conclusion

This implementation plan provides a comprehensive, step-by-step approach to migrating the Todo AI Chatbot to official OpenAI Agents SDK and ChatKit SDK for full Phase III compliance. The migration:

1. **Preserves 100% functionality**: All existing features work identically
2. **Maintains architecture**: Zero schema changes, zero breaking changes
3. **Reduces complexity**: 80% reduction in orchestration code (100 lines → 20 lines)
4. **Follows official patterns**: Uses SDK patterns exactly as documented
5. **Ensures compliance**: Passes all 6 Phase III requirements

The plan is ready for task generation (/sp.tasks) and implementation (/sp.implement).

