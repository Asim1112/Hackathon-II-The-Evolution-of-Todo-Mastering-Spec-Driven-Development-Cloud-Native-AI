# Quickstart Guide: AI-Powered Todo Chatbot

**Feature**: 016-ai-chatbot
**Date**: 2026-02-10
**Purpose**: Get the AI chatbot feature up and running quickly

## Prerequisites

Before starting, ensure you have:
- ✅ Phase 2 Todo app fully functional (backend + frontend + auth)
- ✅ Python 3.11+ installed
- ✅ Node.js 18+ installed
- ✅ Neon PostgreSQL database accessible
- ✅ OpenAI API account with API key

## Step 1: Environment Setup

### 1.1 Obtain OpenAI API Key

1. Sign up at https://platform.openai.com/signup
2. Navigate to API Keys section
3. Create new API key
4. Copy the key (starts with `sk-`)

**Free Credits**: New accounts get $5 free credits (sufficient for development)

### 1.2 Configure Environment Variables

Add to your `.env` file (backend):

```bash
# Existing Phase 2 variables
DATABASE_URL=postgresql://...
JWT_SECRET=...

# NEW: Phase 3 AI variables
OPENAI_API_KEY=sk-your-api-key-here
```

Add to your `.env.local` file (frontend):

```bash
# Existing Phase 2 variables
NEXT_PUBLIC_API_URL=http://localhost:8000

# NEW: Phase 3 ChatKit variables
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=  # Leave empty for localhost development
```

**Note**: Domain key is only required for production deployment (see Step 6).

---

## Step 2: Install Dependencies

### 2.1 Backend Dependencies

```bash
cd backend

# Install OpenAI Agents SDK
pip install openai-agents

# Install Official MCP SDK
pip install mcp

# Update requirements.txt
pip freeze > requirements.txt
```

### 2.2 Frontend Dependencies

```bash
cd frontend

# Install OpenAI ChatKit
npm install @openai/chatkit-react

# Install if not already present
npm install @tanstack/react-query
```

---

## Step 3: Database Tables

### 3.1 Automatic Table Creation

The application automatically creates the required tables on startup using SQLModel's `create_all()` method. No manual migration is needed.

**Tables Created**:
- ✅ `conversation` table with indexes on user_id
- ✅ `message` table with indexes on conversation_id and user_id
- ✅ Foreign key constraints automatically applied

### 3.2 Verify Tables

```bash
# Connect to your database and verify tables
psql $DATABASE_URL -c "\dt"
# Should show: conversation, message (plus existing tables)

# Check conversation table structure
psql $DATABASE_URL -c "\d conversation"

# Check message table structure
psql $DATABASE_URL -c "\d message"
```

**Note**: Tables are created automatically when you start the backend server for the first time. No manual migration commands are needed.

---

## Step 4: Start Backend Server

### 4.1 Run Development Server

```bash
cd backend

# Start FastAPI server
uvicorn src.main:app --reload --port 8000
```

### 4.2 Verify Backend

Open http://localhost:8000/docs

You should see:
- ✅ Existing Phase 2 endpoints (`/api/{user_id}/tasks`)
- ✅ NEW: `/api/{user_id}/chat` endpoint

---

## Step 5: Start Frontend Server

### 5.1 Run Development Server

```bash
cd frontend

# Start Next.js dev server
npm run dev
```

### 5.2 Verify Frontend

Open http://localhost:3000

You should see:
- ✅ Existing Phase 2 pages (login, tasks)
- ✅ NEW: Chat page (navigate to `/chat` after login)

---

## Step 6: Test the Chat Interface

### 6.1 Login

1. Navigate to http://localhost:3000
2. Login with existing Phase 2 credentials
3. Navigate to `/chat` page

### 6.2 Test Basic Commands

Try these natural language commands:

**Create Task**:
```
User: Add a task to buy groceries
Expected: "I've created the task 'Buy groceries' for you."
```

**List Tasks**:
```
User: Show my tasks
Expected: List of all tasks with status
```

**Complete Task**:
```
User: Mark task 1 as complete
Expected: "Task 'Buy groceries' has been marked as complete."
```

**Update Task**:
```
User: Change task 1 to 'Buy groceries and fruits'
Expected: "I've updated the task title."
```

**Delete Task**:
```
User: Delete task 2
Expected: "Task has been deleted."
```

### 6.3 Test Conversation Context

```
User: Show my tasks
Assistant: You have 3 tasks: 1) Buy groceries, 2) Call mom, 3) Pay bills

User: Mark the first one as done
Expected: Assistant understands "first one" refers to task 1
```

---

## Step 7: Production Deployment (Optional)

### 7.1 Deploy Frontend

Deploy to Vercel (or your preferred platform):

```bash
cd frontend

# Deploy to Vercel
vercel deploy --prod
```

Note your production URL (e.g., `https://your-app.vercel.app`)

### 7.2 Configure OpenAI Domain Allowlist

1. Navigate to: https://platform.openai.com/settings/organization/security/domain-allowlist
2. Click "Add domain"
3. Enter your production URL: `https://your-app.vercel.app`
4. Save changes
5. Copy the domain key provided

### 7.3 Update Production Environment

Add domain key to your production environment:

```bash
# Vercel
vercel env add NEXT_PUBLIC_OPENAI_DOMAIN_KEY

# Or update .env.production
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-domain-key-here
```

### 7.4 Deploy Backend

Deploy backend to your hosting platform and update:
- `DATABASE_URL` (production database)
- `OPENAI_API_KEY` (production key)
- `JWT_SECRET` (production secret)

---

## Troubleshooting

### Issue: "OpenAI API key not found"

**Solution**:
```bash
# Verify environment variable is set
echo $OPENAI_API_KEY

# Restart backend server after adding key
```

### Issue: "Conversation not found"

**Solution**:
- Check database migration was applied: `alembic current`
- Verify tables exist: `psql $DATABASE_URL -c "\dt"`
- Check user_id matches JWT token

### Issue: "ChatKit not loading"

**Solution**:
```bash
# Verify ChatKit installed
npm list @openai/chatkit-react

# Clear Next.js cache
rm -rf .next
npm run dev
```

### Issue: "Tool calls not working"

**Solution**:
- Check MCP tools are registered in agent initialization
- Verify tool schemas match expected format
- Check backend logs for tool execution errors

### Issue: "Rate limit exceeded"

**Solution**:
- Switch to GPT-3.5-turbo for development (cheaper)
- Implement exponential backoff retry logic
- Monitor usage at https://platform.openai.com/usage

### Issue: "Conversation history not loading"

**Solution**:
- Check database indexes were created
- Verify user_id filtering in queries
- Check for database connection issues

---

## Development Tips

### Tip 1: Monitor OpenAI Usage

```bash
# Check API usage
curl https://api.openai.com/v1/usage \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Tip 2: Test MCP Tools Independently

```python
# Test add_task tool directly
from src.mcp.tools.add_task import add_task

result = await add_task(
    user_id="test_user",
    title="Test task"
)
print(result)  # Should return task_id, status, title
```

### Tip 3: Debug Agent Execution

```python
# Enable verbose logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Agent execution will log tool calls and responses
```

### Tip 4: Test Conversation State

```python
# Verify conversation persistence
from src.services.conversation_service import ConversationService

service = ConversationService(db)
conv = service.create_or_get_conversation(user_id="test_user")
print(f"Conversation ID: {conv.id}")

# Add messages
service.store_messages(
    conversation_id=conv.id,
    user_id="test_user",
    user_message="Hello",
    assistant_message="Hi!"
)

# Retrieve history
history = service.get_conversation_history(conv.id, "test_user")
print(f"Message count: {len(history)}")
```

### Tip 5: Performance Testing

```bash
# Test concurrent requests
ab -n 100 -c 10 -H "Authorization: Bearer $JWT_TOKEN" \
  -p chat_request.json \
  http://localhost:8000/api/user_123/chat
```

---

## Next Steps

After completing this quickstart:

1. ✅ **Verify all user stories work** (P1-P5 from spec.md)
2. ✅ **Test edge cases** (empty task list, invalid task IDs, etc.)
3. ✅ **Monitor performance** (response times, database queries)
4. ✅ **Review logs** (check for errors or warnings)
5. ✅ **Proceed to /sp.tasks** to generate detailed task breakdown

---

## Useful Commands Reference

```bash
# Backend
cd backend
uvicorn src.main:app --reload --port 8000  # Start server
alembic upgrade head                        # Apply migrations
alembic downgrade -1                        # Rollback migration
pytest tests/                               # Run tests
python -m src.main                          # Alternative start

# Frontend
cd frontend
npm run dev                                 # Start dev server
npm run build                               # Production build
npm run start                               # Start production server
npm run lint                                # Lint code

# Database
psql $DATABASE_URL -c "\dt"                 # List tables
psql $DATABASE_URL -c "\d conversation"     # Describe table
psql $DATABASE_URL -c "SELECT COUNT(*) FROM message"  # Query

# OpenAI
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"  # List models
```

---

## Support

If you encounter issues not covered in this guide:

1. Check backend logs: `tail -f backend/logs/app.log`
2. Check frontend console: Browser DevTools → Console
3. Review Phase 3 documentation: `specs/016-ai-chatbot/`
4. Consult research decisions: `specs/016-ai-chatbot/research.md`

---

**Status**: ✅ Quickstart guide complete - Ready for implementation
