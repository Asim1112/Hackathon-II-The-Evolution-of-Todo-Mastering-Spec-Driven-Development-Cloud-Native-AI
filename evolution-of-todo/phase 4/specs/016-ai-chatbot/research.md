# Research & Technology Validation

**Feature**: AI-Powered Todo Chatbot (016-ai-chatbot)
**Date**: 2026-02-10
**Purpose**: Resolve technical unknowns and validate technology choices before implementation

## R1: OpenAI Agents SDK Integration Patterns

### Decision
Use **per-request agent initialization** with OpenAI Agents SDK in FastAPI context.

### Rationale
- Stateless architecture requirement mandates no shared agent state
- Per-request initialization ensures clean state for each chat request
- Aligns with horizontal scalability goals (any server can handle any request)
- Simplifies error handling and recovery

### Implementation Pattern

```python
from openai_agents import Agent, Runner

# In chat endpoint handler
async def handle_chat(user_id: str, message: str, conversation_history: list):
    # Initialize agent per request
    agent = Agent(
        name="TodoAssistant",
        instructions="""You are a helpful todo list assistant.
        Help users manage their tasks through natural conversation.
        Use the provided tools to create, view, update, complete, and delete tasks.""",
        tools=[add_task_tool, list_tasks_tool, complete_task_tool,
               delete_task_tool, update_task_tool]
    )

    # Build message array: history + new message
    messages = conversation_history + [{"role": "user", "content": message}]

    # Run agent (synchronous for simplicity, async available)
    result = Runner.run_sync(agent, messages)

    return result.final_output, result.tool_calls
```

### Message Array Format
```python
messages = [
    {"role": "user", "content": "Add a task to buy groceries"},
    {"role": "assistant", "content": "I've created the task 'Buy groceries' for you."},
    {"role": "user", "content": "Show my tasks"}
]
```

### Error Handling
- Timeout: Set max execution time (30 seconds recommended)
- Tool failures: Agent receives error message, can retry or inform user
- API failures: Catch exceptions, return user-friendly error

### LLM Provider Changes

#### First Change: OpenAI → Groq (2026-02-11)

**Original decision**: Use OpenAI GPT-4o / GPT-3.5-turbo
**Updated decision**: Use **Groq API** with `llama-3.3-70b-versatile` model

**Reason for change**: OpenAI API quota exhausted (insufficient_quota error). Budget constraint - cannot purchase additional OpenAI credits.

**Why Groq**:
- Free tier (30 RPM, 14,400 requests/day) - sufficient for hackathon
- OpenAI-compatible API - uses same `from openai import OpenAI` SDK with custom `base_url`
- Full tool/function calling support - critical for MCP tool invocation
- Fast inference (LPU) - meets <3 second response time goal
- No credit card required

**Code impact**: 3-line change in orchestrator.py (base_url, api_key, model). Zero changes to MCP tools, schemas, chat endpoint, or frontend.

**Integration pattern**:
```python
from openai import OpenAI

client = OpenAI(
    api_key=settings.groq_api_key,
    base_url="https://api.groq.com/openai/v1"
)
# Tool calling format is identical to OpenAI
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=messages,
    tools=tools,
    tool_choice="auto"
)
```

#### Second Change: Groq → Cerebras (2026-02-11)

**Previous decision**: Use Groq API with `llama-3.3-70b-versatile` model
**Updated decision**: Use **Cerebras API** with `llama-3.3-70b` model

**Reason for change**: Groq daily token quota exhausted (100,000 tokens/day limit hit with 429 rate limit error). Need higher token allowance for continued development and testing.

**Why Cerebras**:
- **10x more tokens**: 1,000,000 tokens/day free tier (vs Groq's 100,000/day)
- **OpenAI-compatible API**: Uses same `from openai import OpenAI` SDK with custom `base_url`
- **Same model family**: `llama-3.3-70b` (equivalent to Groq's llama-3.3-70b-versatile)
- **Full tool calling support**: Structured function calling identical to OpenAI/Groq
- **Fast inference**: Optimized for low latency
- **No credit card required**: Free tier sufficient for hackathon scope

**Code impact**: 3-setting change in settings.py (cerebras_api_key, cerebras_base_url, cerebras_model). Zero changes to MCP tools, orchestrator logic, chat endpoint, or frontend. All tool calling patterns remain identical.

**Integration pattern**:
```python
from openai import OpenAI

client = OpenAI(
    api_key=settings.cerebras_api_key,
    base_url="https://api.cerebras.ai/v1"
)
# Tool calling format is identical to OpenAI/Groq
response = client.chat.completions.create(
    model="llama-3.3-70b",
    messages=messages,
    tools=tools,
    tool_choice="auto",
    parallel_tool_calls=False  # Keep for Llama model compatibility
)
```

**API Endpoint**: https://api.cerebras.ai/v1
**Model**: llama-3.3-70b
**Rate Limits**: 1M tokens/day, 30 requests/minute (free tier)
**Sign up**: https://cloud.cerebras.ai

### Alternatives Considered
- **Singleton agent**: Rejected due to state management complexity and scalability issues
- **Agent pooling**: Rejected as unnecessary complexity for MVP
- **OpenAI GPT-4o**: Rejected due to quota exhaustion and cost
- **Google Gemini**: Viable but Groq requires fewer code changes
- **OpenRouter**: Viable but tool calling support varies by model
- **Local Ollama**: Rejected - requires hardware, limited tool calling

---

## R2: Official MCP SDK Implementation

### Decision (CORRECTED)
Use **MCP-compatible tool patterns** WITHOUT running a full MCP server. Define tool schemas manually following MCP JSON Schema format, implement tool handlers as async functions, and invoke them directly from the agent orchestrator.

### Rationale
- Our architecture uses FastAPI REST endpoints, not MCP stdio/HTTP transport
- We only need MCP-compatible tool schemas and handlers, not a full MCP server
- Direct function invocation is simpler and more performant than MCP protocol overhead
- Tool schemas remain compatible with MCP spec for future interoperability
- Avoids dependency on MCP SDK server components we don't need

### Implementation Pattern

```python
# backend/src/mcp/schemas.py - Define MCP-compatible tool schemas
ADD_TASK_SCHEMA = {
    "name": "add_task",
    "description": "Create a new task",
    "input_schema": {
        "type": "object",
        "properties": {
            "user_id": {"type": "string", "description": "User ID"},
            "title": {"type": "string", "description": "Task title"},
            "description": {"type": "string", "description": "Task description"}
        },
        "required": ["user_id", "title"]
    }
}

ALL_SCHEMAS = [ADD_TASK_SCHEMA, LIST_TASKS_SCHEMA, ...]

# backend/src/mcp/tools/add_task.py - Implement tool handler
async def add_task_handler(user_id: str, title: str, description: str = "") -> dict:
    """Create a new task"""
    if not user_id or not title:
        raise ValueError("user_id and title are required")

    task = await task_service.create_task(user_id, title, description)

    return {
        "task_id": task.id,
        "status": "created",
        "title": task.title
    }

# backend/src/mcp/server.py - Tool registry (no MCP SDK server)
_tool_handlers = {}

def register_tool(name: str, handler):
    """Register a tool handler function"""
    _tool_handlers[name] = handler

def get_tool_handler(name: str):
    """Get a registered tool handler"""
    return _tool_handlers.get(name)

def initialize_tools():
    """Register all tool handlers at startup"""
    from src.mcp.tools import get_all_tool_handlers
    for name, handler in get_all_tool_handlers().items():
        register_tool(name, handler)
```

### Integration with OpenAI Agents SDK

```python
# Convert MCP schemas to OpenAI function calling format
def convert_mcp_schemas_to_agent_tools(schemas: list) -> list:
    return [
        {
            "type": "function",
            "function": {
                "name": schema["name"],
                "description": schema["description"],
                "parameters": schema["input_schema"]
            }
        }
        for schema in schemas
    ]

# In chat endpoint
agent_tools = convert_mcp_schemas_to_agent_tools(ALL_SCHEMAS)
# Agent calls tools, orchestrator invokes handlers directly
```

### Error Taxonomy
- `INVALID_PARAMETERS`: Missing or invalid tool parameters
- `UNAUTHORIZED`: User not authorized for operation
- `NOT_FOUND`: Task or conversation not found
- `DATABASE_ERROR`: Database operation failed
- `INTERNAL_ERROR`: Unexpected server error

### Alternatives Considered
- **Custom tool protocol**: Rejected in favor of MCP standard for interoperability
- **Direct function calls**: Rejected as MCP provides better structure and validation

---

## R3: OpenAI ChatKit Configuration

### Decision
Use **self-hosted backend** approach with custom fetch method for JWT authentication.

### Rationale
- Full control over authentication flow
- Integrates with existing Better Auth JWT system
- No dependency on OpenAI-hosted infrastructure
- Supports custom API endpoint structure

### Implementation Pattern

```typescript
// frontend/src/lib/chatkit.ts
import { useChatKit } from '@openai/chatkit-react';

export function useTodoChatKit(userId: string) {
  const { control } = useChatKit({
    api: {
      url: `/api/${userId}/chat`,
      // Custom fetch to inject JWT
      fetch: async (url, options) => {
        const token = localStorage.getItem('auth_token');
        return fetch(url, {
          ...options,
          headers: {
            ...options.headers,
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
      }
    }
  });

  return control;
}
```

### ChatKit Component

```tsx
// frontend/src/components/chat/ChatInterface.tsx
import { ChatKit } from '@openai/chatkit-react';
import { useTodoChatKit } from '@/lib/chatkit';

export function ChatInterface({ userId }: { userId: string }) {
  const control = useTodoChatKit(userId);

  return (
    <ChatKit
      control={control}
      className="h-[600px] w-full"
    />
  );
}
```

### Domain Allowlist Setup
1. Deploy frontend to production URL (e.g., Vercel)
2. Navigate to: https://platform.openai.com/settings/organization/security/domain-allowlist
3. Add production domain (e.g., `https://your-app.vercel.app`)
4. Obtain domain key
5. Add to environment: `NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-key`

### Alternatives Considered
- **OpenAI-hosted backend**: Rejected due to lack of control over authentication
- **Vanilla JS implementation**: Rejected in favor of React integration for better DX

---

## R4: Conversation State Management Patterns

### Decision
Use **database-first stateless pattern** with atomic message storage and indexed queries.

### Rationale
- Aligns with stateless architecture requirement
- Database as single source of truth
- Atomic storage prevents partial state
- Indexed queries ensure performance

### Service Layer Pattern

```python
# backend/src/services/conversation_service.py
from sqlmodel import Session, select
from models import Conversation, Message

class ConversationService:
    def __init__(self, db: Session):
        self.db = db

    def create_or_get_conversation(
        self,
        user_id: str,
        conversation_id: int = None
    ) -> Conversation:
        """Idempotent conversation creation"""
        if conversation_id:
            # Fetch existing
            conv = self.db.get(Conversation, conversation_id)
            if not conv or conv.user_id != user_id:
                raise ValueError("Conversation not found or unauthorized")
            return conv

        # Create new
        conv = Conversation(user_id=user_id)
        self.db.add(conv)
        self.db.commit()
        self.db.refresh(conv)
        return conv

    def get_conversation_history(
        self,
        conversation_id: int,
        user_id: str,
        limit: int = 100
    ) -> list[Message]:
        """Retrieve message history with pagination"""
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .where(Message.user_id == user_id)
            .order_by(Message.created_at.asc())
            .limit(limit)
        )
        return self.db.exec(statement).all()

    def store_messages(
        self,
        conversation_id: int,
        user_id: str,
        user_message: str,
        assistant_message: str
    ) -> tuple[Message, Message]:
        """Atomic storage of user + assistant messages"""
        try:
            # Create both messages
            user_msg = Message(
                conversation_id=conversation_id,
                user_id=user_id,
                role="user",
                content=user_message
            )
            assistant_msg = Message(
                conversation_id=conversation_id,
                user_id=user_id,
                role="assistant",
                content=assistant_message
            )

            # Add both
            self.db.add(user_msg)
            self.db.add(assistant_msg)

            # Commit atomically
            self.db.commit()

            # Refresh to get IDs
            self.db.refresh(user_msg)
            self.db.refresh(assistant_msg)

            return user_msg, assistant_msg
        except Exception as e:
            # Rollback on any error
            self.db.rollback()
            raise

    def build_context_array(
        self,
        conversation_id: int,
        user_id: str,
        new_message: str
    ) -> list[dict]:
        """Build message array for agent input"""
        history = self.get_conversation_history(conversation_id, user_id)

        # Convert to agent format
        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in history
        ]

        # Add new message
        messages.append({"role": "user", "content": new_message})

        return messages
```

### Query Optimization
- Index on `(user_id, created_at DESC)` for user's recent conversations
- Index on `(conversation_id, created_at ASC)` for message history
- Denormalized `user_id` in Message table for efficient filtering

### Alternatives Considered
- **Redis caching**: Deferred to post-MVP (adds complexity)
- **Separate user/assistant storage**: Rejected in favor of atomic storage

---

## R5: Intent Classification Approaches

### Decision
Use **agent-native intent recognition** (let OpenAI agent decide which tool to use).

### Rationale
- Simplifies architecture (one less component)
- OpenAI Agents SDK has built-in tool selection
- Reduces latency (no pre-processing step)
- Lower cost (single LLM call instead of two)
- Easier to maintain (no separate classifier to train/update)

### Implementation
```python
# System prompt guides agent to use appropriate tools
agent = Agent(
    name="TodoAssistant",
    instructions="""You are a helpful todo list assistant.

    When users want to:
    - Create tasks: Use add_task tool
    - View tasks: Use list_tasks tool (with appropriate status filter)
    - Complete tasks: Use complete_task tool
    - Update tasks: Use update_task tool
    - Delete tasks: Use delete_task tool

    Always confirm actions and provide friendly responses.""",
    tools=[...]  # MCP tools
)
```

### Trade-offs
- **Latency**: Slightly higher (agent must reason about tool selection)
- **Accuracy**: Depends on prompt quality and model capability
- **Cost**: Single LLM call per request
- **Maintainability**: Simpler architecture, easier to debug

### Fallback Strategy
If agent-native approach doesn't achieve 95% accuracy:
1. Improve system prompt with more examples
2. Use few-shot examples in prompt
3. Consider lightweight pre-classifier (future enhancement)

### Alternatives Considered
- **Pre-processing classifier**: Rejected for MVP (adds complexity, extra latency)
- **Hybrid approach**: Deferred to post-MVP if accuracy issues arise

---

## R6: Database Migration Strategy

### Decision
Use **Alembic migration** with additive-only changes to avoid disrupting Phase 2 functionality.

### Rationale
- Alembic is standard for SQLModel/SQLAlchemy
- Additive migrations are safe (no schema changes to existing tables)
- Rollback plan is straightforward (drop new tables)
- No impact on existing Task/User models

### Migration Script

```python
# backend/alembic/versions/xxx_add_conversation_models.py
"""Add Conversation and Message models for chat feature

Revision ID: xxx
Revises: yyy (previous migration)
Create Date: 2026-02-10
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # Create conversations table
    op.create_table(
        'conversation',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE')
    )

    # Create indexes for conversations
    op.create_index('ix_conversation_user_id', 'conversation', ['user_id'])
    op.create_index('ix_conversation_user_created', 'conversation', ['user_id', 'created_at'], postgresql_using='btree')

    # Create messages table
    op.create_table(
        'message',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversation.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.CheckConstraint("role IN ('user', 'assistant')", name='check_message_role')
    )

    # Create indexes for messages
    op.create_index('ix_message_conversation_id', 'message', ['conversation_id'])
    op.create_index('ix_message_conversation_created', 'message', ['conversation_id', 'created_at'], postgresql_using='btree')
    op.create_index('ix_message_user_created', 'message', ['user_id', 'created_at'], postgresql_using='btree')

def downgrade():
    # Drop in reverse order (messages first due to foreign key)
    op.drop_table('message')
    op.drop_table('conversation')
```

### Rollback Plan
```bash
# Rollback migration
alembic downgrade -1

# Verify existing functionality
pytest tests/test_tasks.py
```

### Testing Strategy
1. Run migration on development database
2. Verify existing Phase 2 functionality (task CRUD)
3. Test new conversation/message operations
4. Test rollback
5. Apply to production

### Alternatives Considered
- **Manual SQL scripts**: Rejected in favor of Alembic for version control
- **Schema changes to existing tables**: Rejected to avoid risk to Phase 2

---

## Integration Points with Phase 2

### Reused Components
- **Authentication**: Better Auth JWT validation (no changes)
- **Task Model**: Used by MCP tools (no changes)
- **Task Service**: Called by MCP tools (no changes)
- **Database Connection**: Shared connection pool (no changes)
- **API Middleware**: JWT middleware applied to chat endpoint (no changes)

### New Components (Additive Only)
- Conversation and Message models
- Conversation service
- MCP server and tools
- Agent orchestrator
- Chat API endpoint
- ChatKit frontend integration

### No Breaking Changes
All Phase 2 functionality remains intact. Phase 3 is purely additive.

---

## Risk Mitigation Strategies

### LLM API Rate Limits
- Using Groq free tier (30 RPM, 14,400 req/day) - sufficient for hackathon
- Model: llama-3.3-70b-versatile (free, full tool calling support)
- Monitor usage via Groq console
- Fallback: Can switch to Google Gemini free tier if Groq limits hit

### Intent Recognition Accuracy
- Start with comprehensive system prompt
- Iterate based on user testing
- Add few-shot examples if needed
- Fallback to clarification questions

### Conversation History Performance
- Implement pagination (limit 100 messages per query)
- Add database indexes (already in migration)
- Monitor query performance
- Consider caching for post-MVP

### MCP SDK Integration
- Follow official examples closely
- Test each tool independently
- Implement comprehensive error handling
- Log tool invocations for debugging

### Groq Tool Calling Compatibility (ISSUE RESOLVED 2026-02-11)

**Issue**: `tool_use_failed` error where Llama model generates XML-format function calls (`<function=list_tasks {"status": "all"} </function>`) instead of structured tool_calls API format.

**Root Cause**: Known Groq/Llama issue (confirmed via community forums) - intermittent failures where models revert to XML format instead of using OpenAI-compatible structured tool calling.

**Contributing Factors**:
1. Non-standard `"default": "all"` field in `list_tasks` schema (not part of OpenAI function calling spec)
2. Empty `required: []` array after `user_id` stripping (confuses model about parameter requirements)

**Fix Applied**:
1. Remove `"default"` field from all tool schemas (non-standard for OpenAI function calling)
2. Remove empty `required` arrays from converted schemas (if no required params, omit the key entirely)
3. Add `parallel_tool_calls=False` to orchestrator API call (reduces complexity for model)

**Verification**: Test `add_task` (works), `list_tasks` (was failing), `complete_task`, `update_task`, `delete_task` to ensure all tools work consistently.

---

### Agent Hallucination Bug - Delete Operations (CRITICAL ISSUE RESOLVED 2026-02-11)

**Issue**: Agent claimed successful task deletion but tasks remained in database. Agent reported "I've deleted 6 duplicate tasks" but re-querying showed all 12 tasks still present. This is a production-grade AI safety issue - the agent was hallucinating success without verifying actual system state changes.

**Root Cause**: Agent was trained to trust tool return values (e.g., `{"status": "deleted"}`) as proof of success, without re-querying system state to verify the change occurred. The agent lacked explicit instructions to perform state verification after mutations.

**Contributing Factors**:
1. **Transaction rollback bug**: Manual `session.commit()` calls in MCP tool handlers conflicted with SQLModel's Session context manager auto-commit, causing silent rollbacks (fixed separately)
2. **Missing verification mandate**: Agent prompt and constitution lacked explicit requirements to verify mutations by re-querying state
3. **Trust in tool responses**: Agent assumed tool success responses meant state changed, without understanding that database transactions, network failures, or bugs can cause silent failures

**Impact**:
- User trust erosion: Agent confidently claimed success when operations failed
- Data integrity risk: Users believe tasks are deleted when they're not
- Debugging difficulty: Silent failures with no error messages
- AI safety violation: Agent hallucinating reality instead of verifying truth

**Fix Applied (SDD Flow - Docs First, Then Code):**

1. **Constitution Update** (`.specify/memory/constitution.md`):
   - Added "AI Safety Principles" section with "State Verification Mandate"
   - Mandates: After ANY mutation (add/delete/complete/update), agent MUST re-query state and verify change
   - Forbids: Claiming success based solely on tool return values
   - Requires: Explicit before/after state comparison and truthful reporting
   - Includes: Correct and incorrect verification pattern examples

2. **Agent Prompt Update** (`backend/src/agents/prompts.py`):
   - Added "CRITICAL: State Verification Mandate" section at top of prompt
   - Provides step-by-step verification pattern (before-state → execute → after-state → compare → report)
   - Includes concrete examples of correct vs forbidden behavior
   - Explains why verification is required (tool responses indicate attempt, not success)
   - Mandates transparency if verification fails

3. **Transaction Bug Fix** (`backend/src/mcp/mcp_server.py`):
   - Removed manual `session.commit()` calls from all tool handlers
   - Changed to `session.flush()` to persist changes within transaction
   - Let SQLModel's Session context manager handle auto-commit on successful exit
   - Fixed `_SessionContext` to properly handle auto-commit behavior

**Verification Pattern (Now Enforced):**
```
User: "Delete duplicate tasks"

Agent MUST:
1. Call list_tasks → Count: 12 tasks
2. Identify duplicates (tasks 7-12)
3. Call delete_task(7), delete_task(8), ..., delete_task(12)
4. Call list_tasks again → Count: 6 tasks
5. Compare: 12 - 6 = 6 deleted ✓
6. Report: "I've deleted 6 duplicate tasks. Verified: Your task list now has 6 tasks (previously 12)."
```

**Testing Requirements:**
1. Ask agent to delete duplicate tasks
2. Verify agent calls list_tasks BEFORE deletion (captures before-state)
3. Verify agent calls delete_task for each duplicate
4. Verify agent calls list_tasks AFTER deletion (captures after-state)
5. Verify agent reports before/after comparison in response
6. Confirm tasks are actually deleted in database (no rollback)

**Status**: Fix applied, pending verification testing with real user interaction.

---

## Technology Stack Summary

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Backend Framework | FastAPI | Latest | API server |
| ORM | SQLModel | Latest | Database models |
| Database | Neon PostgreSQL | Latest | Data persistence |
| AI Framework | OpenAI Python SDK | Latest | Agent orchestration (OpenAI-compatible) |
| MCP | MCP-compatible patterns | N/A | Tool schemas and handlers (no SDK server) |
| LLM | Groq (llama-3.3-70b-versatile) | Latest | Natural language understanding |
| Frontend Framework | Next.js | 16+ | Web application |
| Chat UI | OpenAI ChatKit | Latest | Conversational interface |
| Authentication | Better Auth | Latest | JWT-based auth (existing) |

---

## Conclusion

All research tasks completed. Key decisions:
1. Per-request agent initialization (stateless)
2. Official MCP SDK with custom tool registration
3. Self-hosted ChatKit with JWT authentication
4. Database-first stateless conversation management
5. Agent-native intent recognition (no pre-processing)
6. Alembic migration with additive-only changes

**Status**: ✅ Research complete - Ready for Phase 1 design artifacts
