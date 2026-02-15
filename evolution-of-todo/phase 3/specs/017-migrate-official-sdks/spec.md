# Feature Specification: Migrate to Official OpenAI SDKs for Phase III Compliance

**Feature Branch**: `017-migrate-official-sdks`
**Created**: 2026-02-11
**Status**: Draft
**Input**: User description: "Migrate Todo AI Chatbot to Official OpenAI Agents SDK + OpenAI ChatKit for Full Phase-III Compliance"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Phase III Compliance Verification (Priority: P1)

As a **hackathon judge** evaluating Phase III submissions, I need to verify that the Todo AI Chatbot uses the official OpenAI Agents SDK and ChatKit SDK as required by the specification, so that I can confirm the project meets all mandatory technical requirements.

**Why this priority**: This is the core requirement for Phase III compliance. Without using the official SDKs, the project fails the hackathon evaluation criteria regardless of functionality.

**Independent Test**: Can be fully tested by inspecting the codebase for OpenAI Agents SDK usage (Agent, Runner classes) in backend and ChatKit React components in frontend, and verifying all 6 Phase III requirements pass.

**Acceptance Scenarios**:

1. **Given** the Phase III specification requirements, **When** auditing the backend code, **Then** the system uses OpenAI Agents SDK (Agent, Runner) for all AI orchestration instead of manual OpenAI client calls
2. **Given** the Phase III specification requirements, **When** auditing the frontend code, **Then** the system uses official ChatKit React components (@openai/chatkit-react) instead of custom chat UI components
3. **Given** the compliance checklist, **When** running the audit, **Then** all 6 Phase III requirements show PASS status
4. **Given** the existing MCP tools (add_task, list_tasks, etc.), **When** the agent processes user requests, **Then** all 5 MCP tools continue to work identically to the current implementation

---

### User Story 2 - Functional Parity Verification (Priority: P1)

As a **QA tester**, I need to verify that all existing chatbot functionality works identically after the SDK migration, so that users experience no disruption or regression in features.

**Why this priority**: Maintaining 100% functional parity is critical. The migration must be transparent to end users - they should not notice any difference in behavior.

**Independent Test**: Can be fully tested by executing the same test scenarios before and after migration and comparing results for identical behavior.

**Acceptance Scenarios**:

1. **Given** a user asks "show me my tasks", **When** the agent processes the request, **Then** the system calls list_tasks MCP tool and returns the task list in the same format as before migration
2. **Given** a user asks "add a task to buy milk", **When** the agent processes the request, **Then** the system calls add_task MCP tool and creates the task with identical behavior to pre-migration
3. **Given** a multi-turn conversation, **When** the user references previous context, **Then** the agent maintains conversation history and responds appropriately just as it did before migration
4. **Given** a user completes a task, **When** the agent processes the completion, **Then** the system calls complete_task and verifies the state change identically to the current implementation

---

### User Story 3 - Architecture Preservation Verification (Priority: P2)

As a **system architect**, I need to verify that the SDK migration preserves all existing architectural decisions (MCP Server, stateless API, database schema, authentication), so that the system maintains its design integrity and doesn't introduce technical debt.

**Why this priority**: The migration should only replace the AI orchestration and UI layers. All other architectural components must remain unchanged to avoid scope creep and maintain system stability.

**Independent Test**: Can be fully tested by verifying that MCP server definitions, database models, API contracts, and authentication logic remain byte-for-byte identical to pre-migration code.

**Acceptance Scenarios**:

1. **Given** the existing MCP server with FastMCP tools, **When** inspecting the MCP tool definitions, **Then** all tool schemas, function signatures, and implementations remain unchanged
2. **Given** the stateless /api/{user_id}/chat endpoint, **When** testing the API, **Then** the endpoint contract (request/response format) remains identical
3. **Given** the SQLModel database schema, **When** inspecting the models, **Then** Conversation and Message models remain unchanged
4. **Given** the Better Auth integration, **When** testing authentication, **Then** auth flows work identically to pre-migration

---

### User Story 4 - Developer Experience Verification (Priority: P3)

As a **developer** maintaining the codebase, I need the SDK migration to reduce code complexity and improve maintainability, so that future changes are easier to implement and the codebase is more aligned with industry standards.

**Why this priority**: While not critical for initial compliance, improved code quality and maintainability provide long-term value and demonstrate best practices to hackathon judges.

**Independent Test**: Can be fully tested by measuring code metrics (lines of code, cyclomatic complexity) and comparing pre/post migration, expecting significant reduction in orchestration code.

**Acceptance Scenarios**:

1. **Given** the current manual tool calling logic (50+ lines), **When** comparing to SDK implementation, **Then** the new code is significantly shorter (expected ~20 lines) and more maintainable
2. **Given** the SDK documentation, **When** a new developer reads the code, **Then** the implementation follows official SDK patterns and is easier to understand
3. **Given** future feature additions, **When** adding new MCP tools, **Then** the SDK integration makes tool registration simpler than manual implementation

---

### Edge Cases

- What happens when the OpenAI Agents SDK encounters an MCP tool error? (System must handle errors gracefully and maintain conversation state)
- How does the system handle ChatKit widget rendering failures? (System must fall back to text-only responses without crashing)
- What happens when conversation history exceeds context limits? (System must truncate history intelligently while preserving recent context)
- How does the system handle concurrent requests to the same conversation? (Stateless design must continue to work correctly)
- What happens when the MCP server is unavailable? (System must provide appropriate error messages to users)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Backend MUST replace manual OpenAI client usage (chat.completions.create) with OpenAI Agents SDK (Agent, Runner) for all AI orchestration
- **FR-002**: Frontend MUST replace custom ChatInterface component with official ChatKit React components (@openai/chatkit-react)
- **FR-003**: System MUST integrate all 5 existing MCP tools (add_task, list_tasks, complete_task, delete_task, update_task) with OpenAI Agents SDK using MCPServerStreamableHttp pattern
- **FR-004**: System MUST maintain identical natural language understanding and tool calling behavior as the current implementation
- **FR-005**: Backend MUST implement ChatKitServer with respond() method that integrates OpenAI Agents SDK (Agent, Runner, AgentContext) with ChatKit's streaming event system
- **FR-006**: System MUST implement ChatKit Store interface (load_thread, save_thread, load_thread_items, add_thread_item, etc.) that adapts existing Conversation and Message models without schema changes
- **FR-007**: System MUST use ChatKit's simple_to_agent_input() and stream_agent_response() helpers to bridge ChatKit thread items with OpenAI Agents SDK input/output
- **FR-008**: System MUST preserve user_id injection and isolation in all Store operations via context parameter
- **FR-009**: System MUST maintain the same error handling and user feedback patterns
- **FR-010**: System MUST pass all 6 Phase III specification requirements when audited
- **FR-011**: Backend MUST NOT modify MCP server tool definitions, schemas, or implementations (tools will be registered with Agent via tools parameter)
- **FR-012**: Backend MUST NOT change database models (Conversation, Message) or schema (Store interface adapts to existing schema)
- **FR-013**: Backend MUST NOT alter authentication logic or Better Auth integration
- **FR-014**: Frontend MUST use ChatKit React component with apiUrl pointing to /chatkit endpoint
- **FR-015**: System MUST support the same conversation flows and user interactions as before migration (ChatKit thread_id maps to existing conversation_id)

### Key Entities

- **Agent**: OpenAI Agents SDK agent instance (configured with name, instructions, model, mcp_servers list) that replaces manual orchestration
- **Runner**: OpenAI Agents SDK execution engine (Runner.run_streamed() for streaming responses)
- **MCPServerStreamableHttp**: MCP integration class that connects Agent to FastMCP server via HTTP (recommended pattern with cache_tools_list=True)
- **ChatKitServer**: Backend server base class with respond() method for generating responses and optional action() method for widget interactions
- **Store**: ChatKit persistence interface (13 methods: load_thread, save_thread, load_thread_items, add_thread_item, etc.) that adapts existing Conversation/Message models
- **AgentContext**: Bridge between ChatKit and Agents SDK (provides thread, store, request_context; used with simple_to_agent_input and stream_agent_response helpers)
- **ThreadMetadata**: ChatKit thread representation (maps to existing Conversation model via Store adapter)
- **ThreadItem**: ChatKit message types (UserMessageItem, AssistantMessageItem, ToolCallItem) that map to existing Message model
- **ChatKit React Component**: Frontend component from @openai/chatkit-react that replaces custom ChatInterface

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Phase III compliance audit shows PASS on all 6 requirements (currently shows FAIL on Requirement #2 and Frontend requirement)
- **SC-002**: All existing chatbot functionality works identically - 100% of current test scenarios pass after migration
- **SC-003**: Backend orchestration code is reduced by at least 80% (from ~100 lines manual orchestration to ~20 lines using Agent + Runner + ChatKitServer pattern)
- **SC-004**: ChatKit endpoint (/chatkit) handles all chat operations via single FastAPI route with server.process() method
- **SC-005**: Conversation history and multi-turn interactions work identically via ChatKit Store interface loading thread items with pagination (limit=20-50, order="asc")
- **SC-006**: All 5 MCP tools execute successfully through Agent's mcp_servers parameter using MCPServerStreamableHttp integration
- **SC-007**: System maintains the same response time performance (within 10% of current latency)
- **SC-008**: Zero modifications to MCP server code, database models, or authentication logic (Store adapter pattern preserves existing schema)
- **SC-009**: Frontend uses ChatKit React component with apiUrl="/chatkit" and renders streaming responses with automatic message handling
- **SC-010**: Implementation follows patterns from knowledge base files: Agent with mcp_servers, ChatKitServer.respond() with AgentContext, simple_to_agent_input/stream_agent_response helpers

## Scope & Boundaries *(mandatory)*

### In Scope

- Replacing backend orchestrator.py with OpenAI Agents SDK implementation (Agent, Runner, MCPServerStreamableHttp)
- Creating ChatKitServer subclass with respond() method that uses AgentContext, simple_to_agent_input(), and stream_agent_response()
- Implementing ChatKit Store interface (13 methods) as adapter layer over existing Conversation/Message models
- Adding /chatkit FastAPI endpoint that calls server.process() and returns StreamingResponse or JSON Response
- Replacing frontend ChatInterface component with ChatKit React component from @openai/chatkit-react
- Integrating existing FastMCP tools with Agent via mcp_servers parameter (MCPServerStreamableHttp with cache_tools_list=True)
- Maintaining 100% functional parity with current implementation
- Ensuring Phase III compliance audit passes all requirements

### Out of Scope

- Adding new features or capabilities beyond SDK replacement
- Modifying MCP server tool definitions or implementations (tools registered via Agent.mcp_servers, not Agent.tools)
- Changing database schema or models (Store adapter preserves existing schema)
- Altering authentication logic or Better Auth integration
- Redesigning UI/UX or adding new chat features
- Refactoring unrelated code or "improvements" outside SDK migration
- Implementing ChatKit widget system (Card, Button, Form, etc.) - available in SDK but deferred as future enhancement
- Implementing ChatKit action handlers for interactive widgets - deferred as future enhancement
- Adding client tools (browser callbacks) - deferred as future enhancement
- Performance optimizations beyond maintaining current performance
- Adding new MCP tools or changing existing tool behavior

## Assumptions *(mandatory)*

1. **SDK Compatibility**: OpenAI Agents SDK v0.7.0 and ChatKit SDK are compatible with the current Python/Node.js versions used in the project
2. **MCP Integration Pattern**: OpenAI Agents SDK's MCPServerStreamableHttp class can connect to existing FastMCP server via HTTP URL (http://localhost:8001/mcp) with cache_tools_list=True for tool caching
3. **Store Adapter Pattern**: ChatKit Store interface (13 async methods) can be implemented as adapter layer over existing Conversation/Message SQLModel models without schema changes
4. **Thread-to-Conversation Mapping**: ChatKit ThreadMetadata.id can map directly to existing Conversation.id, and ThreadItem types (UserMessageItem, AssistantMessageItem, ToolCallItem) can serialize to/from existing Message.content JSON field
5. **AgentContext Integration**: ChatKit's AgentContext (with simple_to_agent_input and stream_agent_response helpers) correctly bridges thread items to Agent input format and Agent streaming output to ChatKit events
6. **Stateless Endpoint Pattern**: ChatKit's server.process(request_body, context) method supports stateless operation where context parameter carries user_id for Store isolation
7. **Session Management**: OpenAI Agents SDK's session parameter (for conversation history) is NOT needed because ChatKit Store handles conversation persistence via load_thread_items() with pagination

## Dependencies *(mandatory)*

### Technical Dependencies

- OpenAI Agents SDK (openai-agents-python v0.7.0) - already installed
  - Core classes: Agent, Runner, MCPServerStreamableHttp
  - MCP integration: Agent.mcp_servers parameter for FastMCP server connection
  - Streaming: Runner.run_streamed() for streaming responses
- ChatKit Python SDK (openai-chatkit) - already installed
  - Core classes: ChatKitServer, Store, StreamingResult
  - Integration helpers: AgentContext, simple_to_agent_input(), stream_agent_response()
  - Types: ThreadMetadata, ThreadItem (UserMessageItem, AssistantMessageItem, ToolCallItem), Page
- ChatKit React SDK (@openai/chatkit-react) - already installed
  - Component: ChatKit with apiUrl, threadId, placeholder props
  - Automatic message rendering and streaming support
- Existing MCP Server with FastMCP tools - must remain functional (accessed via MCPServerStreamableHttp)
- Existing database schema and models - must remain unchanged (Store adapter preserves schema)
- Existing authentication system - must remain functional (context parameter in Store methods)

### Knowledge Dependencies

- OpenAI-Agents-SDK-Knowledge.md (1,788 lines) - Key patterns:
  - Agent with mcp_servers=[MCPServerStreamableHttp(...)] for MCP integration
  - Runner.run_streamed(agent, input, context=agent_context) for execution
  - MCPServerStreamableHttp with cache_tools_list=True recommended
  - Session management (SQLiteSession) - NOT needed for ChatKit integration
- Chatkit-SDK-Documentation.md (3,427 lines) - Key patterns:
  - ChatKitServer.respond() yields ThreadStreamEvent objects
  - Store interface: 13 async methods for thread/item persistence
  - AgentContext bridges ChatKit and Agents SDK
  - simple_to_agent_input() converts thread items to agent input
  - stream_agent_response() converts agent output to ChatKit events
  - FastAPI integration: server.process(body, context) returns StreamingResult or JSONResult
- Phase III specification document - defines compliance requirements
- Current codebase understanding - orchestrator.py, ChatInterface component, MCP tools

### Process Dependencies

- Spec-driven development workflow must be followed (/sp.specify → /sp.plan → /sp.tasks → /sp.implement)
- All changes must be testable and verifiable against acceptance criteria
- Compliance audit must be run after implementation to verify PASS status

## Constraints *(mandatory)*

### Technical Constraints

- **Preserve Architecture**: MCP Server, stateless API, ConversationService, SQLModel, Neon DB, Better Auth must remain unchanged
- **No Schema Changes**: Database models and schema must remain byte-for-byte identical (Store adapter pattern serializes ThreadItem to/from Message.content JSON)
- **API Contract**: New /chatkit endpoint replaces /api/{user_id}/chat but maintains same functional behavior (user_id passed via context parameter to Store methods)
- **Functional Parity**: All existing behavior must work identically - zero regressions allowed
- **Minimal Changes**: Only modify files directly related to AI orchestration (orchestrator.py → chatkit_server.py + store_adapter.py) and chat UI (ChatInterface → ChatKit component)
- **MCP Integration**: Must use MCPServerStreamableHttp with HTTP URL to existing FastMCP server (not direct tool registration via Agent.tools parameter)
- **Store Implementation**: Must implement all 13 Store methods (load_thread, save_thread, load_threads, load_thread_items, add_thread_item, save_item, load_item, delete_thread, delete_thread_item, save_attachment, load_attachment, delete_attachment, generate_item_id)
- **Pagination**: Store.load_thread_items() must use cursor-based pagination (after parameter) with reasonable limit (20-50 items) and ascending order for chronological context

### Process Constraints

- **SDD Workflow**: Must follow spec → plan → tasks → implement workflow strictly
- **SDK Patterns**: Must use official SDK patterns exactly as documented in knowledge base files:
  - Agent with mcp_servers=[MCPServerStreamableHttp(...)]
  - ChatKitServer.respond() with AgentContext
  - simple_to_agent_input() and stream_agent_response() helpers
  - Store adapter pattern over existing models
- **No Vibe Coding**: All implementation must reference official documentation, no improvisation
- **Backward Compatibility**: All changes must be backward-compatible with existing functionality (Store adapter ensures this)

### Business Constraints

- **Compliance Focus**: Primary goal is achieving Phase III compliance, not adding features
- **Audit Readiness**: Implementation must be audit-ready for hackathon judges
- **Documentation**: Code must be clear and follow SDK best practices for judge review
- **Widget System Deferred**: ChatKit widget system (Card, Button, Form, interactive UI) is available in SDK but deferred as future enhancement to minimize scope

## Non-Functional Requirements *(optional)*

### Performance

- Response latency must remain within 10% of current performance
- System must handle the same concurrent user load as current implementation
- Conversation history loading must not introduce noticeable delays

### Maintainability

- Code must follow official SDK patterns for easier future maintenance
- Implementation must be well-documented with references to SDK documentation
- Code complexity should be reduced compared to current manual implementation

### Reliability

- Error handling must be as robust as current implementation
- System must gracefully handle SDK-specific errors
- Conversation state must be preserved correctly across requests

## Risks & Mitigation *(optional)*

### Risk 1: MCPServerStreamableHttp Integration Complexity
**Impact**: High
**Probability**: Medium
**Mitigation**: Use MCPServerStreamableHttp pattern from knowledge base with cache_tools_list=True; connect to existing FastMCP server via HTTP URL (http://localhost:8001/mcp); verify tool discovery works before full integration

### Risk 2: Store Adapter Implementation Complexity
**Impact**: High
**Probability**: Medium
**Mitigation**: Implement all 13 Store methods as thin adapter layer over existing Conversation/Message models; serialize ThreadItem types to/from Message.content JSON field; use cursor-based pagination with after parameter; test each method independently

### Risk 3: ChatKit-to-Agents SDK Bridge
**Impact**: High
**Probability**: Low
**Mitigation**: Use official helpers (simple_to_agent_input, stream_agent_response) exactly as documented; AgentContext provides bridge between ChatKit Store and Agent execution; verify event streaming works correctly

### Risk 4: Functional Regression in Tool Calling
**Impact**: High
**Probability**: Medium
**Mitigation**: Verify all 5 MCP tools execute identically through Agent.mcp_servers integration; test multi-turn tool calling; ensure tool results feed back correctly to model; maintain comprehensive test scenarios

### Risk 5: Audit Failure
**Impact**: Critical
**Probability**: Low
**Mitigation**: Verify compliance requirements continuously during implementation; ensure Agent class used (not manual OpenAI client); ensure ChatKit React component used (not custom UI); run audit before declaring completion

## Open Questions *(optional)*

None - all requirements are clearly defined in the user input and Phase III specification.

## References *(optional)*

### OpenAI Agents SDK Patterns (OpenAI-Agents-SDK-Knowledge.md - 1,788 lines)

**Core Integration Pattern:**
```python
from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp

# MCP Integration (recommended pattern)
async with MCPServerStreamableHttp(
    name="TodoMCP",
    params={"url": "http://localhost:8001/mcp", "timeout": 10},
    cache_tools_list=True,  # Cache tool list for performance
    max_retry_attempts=3,
) as server:
    agent = Agent(
        name="TodoAssistant",
        instructions="Use MCP tools to manage tasks",
        model="llama-3.3-70b",
        mcp_servers=[server]  # Register MCP server
    )

    # Streaming execution
    result = Runner.run_streamed(agent, input_items, context=agent_context)
```

**Key Points:**
- Agent.mcp_servers parameter for MCP integration (NOT Agent.tools)
- MCPServerStreamableHttp with cache_tools_list=True recommended
- Runner.run_streamed() for streaming responses
- Session management (SQLiteSession) NOT needed for ChatKit integration

### ChatKit SDK Patterns (Chatkit-SDK-Documentation.md - 3,427 lines)

**ChatKitServer Implementation:**
```python
from chatkit.server import ChatKitServer
from chatkit.agents import AgentContext, simple_to_agent_input, stream_agent_response

class TodoChatKitServer(ChatKitServer[dict]):
    async def respond(self, thread, input_user_message, context):
        # Load history with pagination
        items_page = await self.store.load_thread_items(
            thread.id, after=None, limit=20, order="asc", context=context
        )

        # Convert to agent input
        input_items = await simple_to_agent_input(items_page.data)

        # Create agent context
        agent_context = AgentContext(
            thread=thread,
            store=self.store,
            request_context=context
        )

        # Run agent and stream events
        result = Runner.run_streamed(assistant, input_items, context=agent_context)
        async for event in stream_agent_response(agent_context, result):
            yield event
```

**Store Interface (13 methods):**
- load_thread, save_thread, load_threads
- load_thread_items (with pagination: after, limit, order)
- add_thread_item, save_item, load_item
- delete_thread, delete_thread_item
- save_attachment, load_attachment, delete_attachment
- generate_item_id

**FastAPI Integration:**
```python
@app.post("/chatkit")
async def chatkit_endpoint(request: Request):
    result = await server.process(await request.body(), context={})
    if isinstance(result, StreamingResult):
        return StreamingResponse(result, media_type="text/event-stream")
    return Response(content=result.json, media_type="application/json")
```

**Frontend Integration:**
```typescript
import { ChatKit } from '@openai/chatkit-react';

<ChatKit
  apiUrl="http://localhost:8000/chatkit"
  threadId="user_123"
  placeholder="Ask me about your tasks..."
/>
```

### Additional References

- Phase III Specification - Hackathon compliance requirements (6 requirements total)
- Current Implementation - backend/src/agents/orchestrator.py (manual OpenAI client usage)
- Current Frontend - frontend/src/components/ChatInterface (custom React component)
- MCP Server - backend/src/mcp/mcp_server.py (FastMCP tools: add_task, list_tasks, complete_task, delete_task, update_task)
