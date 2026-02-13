# Quickstart Guide: OpenAI SDKs Migration

**Feature**: Migrate to Official OpenAI SDKs for Phase III Compliance
**Date**: 2026-02-11
**Purpose**: Step-by-step setup instructions for developers

## Overview

This guide provides complete setup instructions for the OpenAI Agents SDK and ChatKit SDK migration. Follow these steps to set up your development environment and verify the migration works correctly.

## Prerequisites

### Required Software

- **Python 3.11+**: Backend runtime
- **Node.js 18+**: Frontend runtime
- **PostgreSQL 14+**: Database (Neon Serverless PostgreSQL in production)
- **Git**: Version control

### Verify Prerequisites

```bash
# Check Python version
python --version  # Should be 3.11 or higher

# Check Node.js version
node --version  # Should be 18 or higher

# Check PostgreSQL
psql --version  # Should be 14 or higher
```

## Step 1: Install Dependencies

### Backend Dependencies

```bash
cd backend

# Install OpenAI Agents SDK
pip install openai-agents-python==0.7.0

# Install ChatKit Python SDK
pip install openai-chatkit

# Install existing dependencies (if not already installed)
pip install fastapi uvicorn sqlmodel psycopg2-binary python-dotenv
```

**Verify Installation**:
```bash
python -c "from agents import Agent, Runner; print('Agents SDK installed')"
python -c "from chatkit.server import ChatKitServer; print('ChatKit SDK installed')"
```

### Frontend Dependencies

```bash
cd frontend

# Install ChatKit React SDK
npm install @openai/chatkit-react

# Install existing dependencies (if not already installed)
npm install next react react-dom
```

**Verify Installation**:
```bash
npm list @openai/chatkit-react
# Should show @openai/chatkit-react@<version>
```

## Step 2: Environment Configuration

### Backend Environment Variables

Create or update `backend/.env`:

```bash
# Existing variables (PRESERVE)
CEREBRAS_API_KEY=your_cerebras_api_key_here
CEREBRAS_BASE_URL=https://api.cerebras.ai/v1
CEREBRAS_MODEL=llama-3.3-70b

DATABASE_URL=postgresql://user:password@localhost:5432/todo_db

# Better Auth (if applicable)
AUTH_SECRET=your_auth_secret_here

# MCP Server Configuration (NEW - if not already present)
MCP_SERVER_URL=http://localhost:8001/mcp
MCP_SERVER_TIMEOUT=10
```

### Frontend Environment Variables

Create or update `frontend/.env.local`:

```bash
# Existing variables (PRESERVE)
NEXT_PUBLIC_API_URL=http://localhost:8000

# ChatKit Configuration (NEW - if not already present)
NEXT_PUBLIC_CHATKIT_API_URL=http://localhost:8000/chatkit
```

## Step 3: Database Setup

### Verify Existing Schema

The migration requires NO schema changes. Verify your existing schema:

```sql
-- Connect to database
psql $DATABASE_URL

-- Verify conversation table
\d conversation
-- Expected columns: id, user_id, created_at

-- Verify message table
\d message
-- Expected columns: id, conversation_id, role, content, created_at

-- Verify indexes
\di
-- Expected: idx_user_id on conversation, idx_conversation_created on message
```

**If tables don't exist**, run migrations:
```bash
cd backend
python -m alembic upgrade head
```

## Step 4: Start MCP Server

The MCP server must be running for the Agent to access tools.

```bash
cd backend

# Start MCP server on port 8001
python -m src.mcp.mcp_server

# Expected output:
# MCP Server running on http://localhost:8001
# Available tools: add_task, list_tasks, complete_task, delete_task, update_task
```

**Verify MCP Server**:
```bash
# In another terminal
curl http://localhost:8001/mcp/tools

# Expected: JSON list of 5 tools
```

## Step 5: Start Backend Server

```bash
cd backend

# Start FastAPI server
uvicorn src.main:app --reload --port 8000

# Expected output:
# INFO:     Uvicorn running on http://127.0.0.1:8000
# INFO:     Application startup complete
```

**Verify Backend**:
```bash
# Health check
curl http://localhost:8000/health

# Expected: {"status": "ok"}
```

## Step 6: Start Frontend Server

```bash
cd frontend

# Start Next.js development server
npm run dev

# Expected output:
# ▲ Next.js 16.x.x
# - Local:        http://localhost:3000
# - Ready in X.Xs
```

**Verify Frontend**:
Open browser to http://localhost:3000

## Step 7: Test ChatKit Endpoint

### Test 1: Send Message

```bash
curl -X POST http://localhost:8000/chatkit \
  -H "Content-Type: application/json" \
  -H "X-User-ID: test_user_123" \
  -d '{
    "thread_id": "test_user_123",
    "message": "Hello"
  }'

# Expected: Streaming response (SSE events)
# event: text_delta
# data: {"delta": "Hi"}
# ...
# event: done
```

### Test 2: Load History

```bash
curl -X POST http://localhost:8000/chatkit \
  -H "Content-Type: application/json" \
  -H "X-User-ID: test_user_123" \
  -d '{
    "thread_id": "test_user_123",
    "after": null,
    "limit": 20
  }'

# Expected: JSON response with items array
# {"items": [...], "has_more": false}
```

### Test 3: Tool Calling

```bash
curl -X POST http://localhost:8000/chatkit \
  -H "Content-Type: application/json" \
  -H "X-User-ID: test_user_123" \
  -d '{
    "thread_id": "test_user_123",
    "message": "Add a task to buy milk"
  }'

# Expected: Agent calls add_task tool and responds
# "I've added the task 'buy milk'"
```

## Step 8: Test Frontend Integration

### Manual Testing

1. Navigate to http://localhost:3000/chat
2. Log in (if authentication required)
3. Verify ChatKit component renders
4. Send message: "Hello"
5. Verify agent responds
6. Send message: "Add a task to buy milk"
7. Verify task created
8. Send message: "Show my tasks"
9. Verify task list displays

### Expected Behavior

- ✅ ChatKit component renders with input field
- ✅ Messages appear in real-time (streaming)
- ✅ Agent responds to natural language
- ✅ Tool calls execute successfully
- ✅ Conversation history persists across page reloads

## Step 9: Run Phase III Compliance Audit

### Automated Audit

```bash
cd backend

# Run compliance audit script
python scripts/audit_phase3_compliance.py

# Expected output:
# ✅ Requirement #1: MCP Server - PASS
# ✅ Requirement #2: OpenAI Agents SDK - PASS
# ✅ Requirement #3: Tool Integration - PASS
# ✅ Requirement #4: Conversation Persistence - PASS
# ✅ Requirement #5: Stateless Architecture - PASS
# ✅ Requirement #6: Frontend ChatKit - PASS
#
# OVERALL: PASS (6/6 requirements met)
```

### Manual Verification

**Backend Verification**:
```bash
# Verify Agent usage (not manual OpenAI client)
grep -r "from agents import Agent, Runner" backend/src/agents/

# Expected: Found in chatkit_server.py

# Verify no manual OpenAI client
grep -r "OpenAI()" backend/src/agents/

# Expected: Not found (removed from orchestrator.py)
```

**Frontend Verification**:
```bash
# Verify ChatKit usage
grep -r "from '@openai/chatkit-react'" frontend/src/

# Expected: Found in ChatKitChat.tsx

# Verify no custom ChatInterface
ls frontend/src/components/ChatInterface.tsx

# Expected: File not found (removed)
```

## Troubleshooting

### Issue 1: MCP Server Connection Failed

**Symptom**: Agent cannot call tools, error "MCP server unavailable"

**Solution**:
```bash
# Verify MCP server is running
curl http://localhost:8001/mcp/tools

# If not running, start it:
python -m src.mcp.mcp_server

# Verify MCP_SERVER_URL in .env
echo $MCP_SERVER_URL  # Should be http://localhost:8001/mcp
```

### Issue 2: Database Connection Failed

**Symptom**: Error "could not connect to database"

**Solution**:
```bash
# Verify DATABASE_URL
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1"

# If connection fails, check PostgreSQL is running:
pg_isready
```

### Issue 3: ChatKit Component Not Rendering

**Symptom**: Blank page or error in browser console

**Solution**:
```bash
# Check browser console for errors
# Common issues:
# - Missing @openai/chatkit-react dependency
# - Incorrect apiUrl prop
# - CORS issues

# Verify ChatKit installed
npm list @openai/chatkit-react

# Verify apiUrl in component
grep "apiUrl" frontend/src/components/ChatKitChat.tsx
```

### Issue 4: Agent Not Calling Tools

**Symptom**: Agent responds but doesn't call MCP tools

**Solution**:
```bash
# Verify Agent has mcp_servers configured
grep "mcp_servers" backend/src/agents/chatkit_server.py

# Verify MCPServerStreamableHttp configuration
grep "MCPServerStreamableHttp" backend/src/agents/chatkit_server.py

# Check agent logs for tool discovery
# Should see: "Discovered 5 tools from MCP server"
```

### Issue 5: Streaming Not Working

**Symptom**: Messages appear all at once, not streaming

**Solution**:
```bash
# Verify StreamingResponse used
grep "StreamingResponse" backend/src/api/routes/chatkit.py

# Verify Runner.run_streamed() used (not Runner.run())
grep "run_streamed" backend/src/agents/chatkit_server.py

# Check browser network tab:
# - Content-Type should be "text/event-stream"
# - Transfer-Encoding should be "chunked"
```

## Performance Tuning

### Optimize History Loading

Tune the history limit based on your use case:

```python
# In chatkit_server.py
items_page = await self.store.load_thread_items(
    thread.id,
    after=None,
    limit=20,  # Adjust: 10-50 items
    order="asc",
    context=context
)
```

**Guidelines**:
- 10 items: Fast queries, minimal context
- 20 items: Balanced (recommended default)
- 50 items: Maximum context, slower queries

### Enable MCP Tool Caching

Ensure `cache_tools_list=True` in MCPServerStreamableHttp:

```python
async with MCPServerStreamableHttp(
    name="TodoMCP",
    params={"url": "http://localhost:8001/mcp", "timeout": 10},
    cache_tools_list=True,  # IMPORTANT: Cache tool definitions
    max_retry_attempts=3,
) as server:
    # ...
```

## Next Steps

After completing this quickstart:

1. **Run Regression Tests**: Execute all test suites (NLU, multi-turn, verification, error handling)
2. **Manual Testing**: Complete all 4 manual test scenarios
3. **Performance Benchmarking**: Measure response latency and compare with baseline
4. **Production Deployment**: Deploy to staging environment for final validation

## Additional Resources

- **OpenAI Agents SDK Documentation**: OpenAI-Agents-SDK-Knowledge.md (1,788 lines)
- **ChatKit SDK Documentation**: Chatkit-SDK-Documentation.md (3,427 lines)
- **Implementation Plan**: specs/017-migrate-official-sdks/plan.md
- **Data Model**: specs/017-migrate-official-sdks/data-model.md
- **API Contract**: specs/017-migrate-official-sdks/contracts/chatkit-endpoint.yaml

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review implementation plan for detailed architecture
3. Consult knowledge base files for SDK patterns
4. Check Phase III compliance audit results

---

**Migration Status**: Ready for implementation (/sp.tasks → /sp.implement)
