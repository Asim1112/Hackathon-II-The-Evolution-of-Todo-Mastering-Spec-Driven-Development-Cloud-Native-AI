# Todo Full-Stack Web Application

This is a todo application built with FastAPI, SQLModel, and Neon PostgreSQL as part of the Spec-Driven Development Hackathon Phase II.

## Backend Foundation & Persistence

This feature implements the backend foundation for the Todo application with CRUD operations for tasks.

### Features

- Create, read, update, and delete todo tasks
- Data persistence using SQLModel and PostgreSQL
- RESTful API endpoints
- Proper error handling and validation

### Tech Stack

- Python 3.11
- FastAPI
- SQLModel
- Pydantic
- Neon PostgreSQL (with SQLite for development)

### API Endpoints

- `POST /api/v1/tasks` - Create a new task
- `GET /api/v1/tasks` - Get all tasks
- `GET /api/v1/tasks/{id}` - Get a specific task
- `PUT /api/v1/tasks/{id}` - Update a specific task
- `DELETE /api/v1/tasks/{id}` - Delete a specific task
- `GET /` - Root endpoint
- `GET /health` - Health check

### Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables (optional, defaults to SQLite):
   ```
   DATABASE_URL=postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/dbname?sslmode=require
   ```
4. Run the application: `uvicorn backend.src.api.main:app --reload`

### Running Tests

```bash
pytest
```

### Environment Variables

- `DATABASE_URL`: Database connection string (defaults to SQLite)
- `NEON_DATABASE_URL`: Neon PostgreSQL connection string (optional)

## Authentication & API Security

This feature implements authentication and API security using JWT tokens for user identification and access control.

### Features

- JWT-based authentication for all API endpoints
- User-specific data access (users can only access their own tasks)
- Cross-user access prevention
- Token validation and expiration checking
- Proper error handling for authentication failures

### JWT Configuration

- Algorithm: HS256 (configurable)
- Default expiration: 7 days (configurable)
- Secret key stored in environment variables

### API Security

- All task endpoints require valid JWT authentication
- Users can only access, modify, or delete their own tasks
- Invalid/expired tokens return 401 Unauthorized
- Cross-user access attempts return 403 Forbidden

### Environment Variables

- `JWT_SECRET`: Secret key for signing JWT tokens (defaults to development key)
- `JWT_ALGORITHM`: Algorithm for JWT signing (defaults to HS256)
- `JWT_EXPIRATION_DELTA`: Token expiration time in seconds (defaults to 604800 = 7 days)

### API Endpoints (Authentication Required)

All existing task endpoints now require authentication:

- `POST /api/v1/tasks` - Create a new task (requires valid JWT)
- `GET /api/v1/tasks` - Get all tasks for authenticated user
- `GET /api/v1/tasks/{id}` - Get a specific task (must belong to authenticated user)
- `PUT /api/v1/tasks/{id}` - Update a specific task (must belong to authenticated user)
- `DELETE /api/v1/tasks/{id}` - Delete a specific task (must belong to authenticated user)

### Authentication Setup

1. The application automatically validates JWT tokens on all protected endpoints
2. Include the JWT token in the Authorization header as: `Authorization: Bearer <token>`
3. The application will extract the user ID from the token's `sub` claim
4. Requests are validated against the user ID to ensure data access is limited to the authenticated user's own data

### Testing Authentication

Authentication can be tested using the comprehensive test suite:

```bash
cd backend
python -m pytest tests/test_auth_utils.py  # Test JWT utilities
```

## AI-Powered Todo Chatbot (Phase 3)

This feature implements a conversational AI interface for task management using natural language. Users can create, view, update, complete, and delete tasks through a chat interface powered by OpenAI's GPT-4.

### Features

- **Natural Language Task Management**: Create tasks by saying "Add a task to buy groceries"
- **Conversational Task Viewing**: Ask "Show my tasks" or "What's pending?"
- **Task Completion**: Mark tasks done with "Mark task 3 as complete"
- **Task Updates**: Modify tasks with "Change task 1 to 'Buy groceries and fruits'"
- **Task Deletion**: Remove tasks with "Delete task 2"
- **Conversation History**: Full context maintained across chat sessions
- **Multi-Agent Architecture**: Specialized sub-agents for different operations
- **Stateless Design**: Horizontally scalable with database-persisted conversations

### Tech Stack Additions

- **OpenAI Agents SDK** (v0.6.4): Agent orchestration and tool calling
- **MCP SDK** (v1.25.0): Model Context Protocol for tool definitions
- **OpenAI ChatKit** (React): Conversational UI component
- **GPT-4 Optimized**: AI model for natural language understanding

### Architecture Overview

The chatbot uses a multi-agent architecture with 6 specialized sub-agents:

1. **Database Operations Manager**: Conversation and message persistence
2. **MCP Server Architect**: Tool registration and schema management
3. **Conversation Flow Manager**: History retrieval and context building
4. **Intent Analysis Specialist**: Natural language understanding (built into agent)
5. **Agent Execution Coordinator**: OpenAI agent orchestration with tool calling
6. **Chat API Coordinator**: End-to-end request lifecycle management

### Setup Instructions

#### Backend Setup

1. **Install Dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables**:
   Add to `backend/.env`:
   ```bash
   OPENAI_API_KEY=sk-your-openai-api-key-here
   DATABASE_URL=postgresql://username:password@host/dbname?sslmode=require
   ```

3. **Initialize Database**:
   The application automatically creates conversation and message tables on startup.

4. **Start Backend Server**:
   ```bash
   uvicorn src.api.main:app --reload
   ```

#### Frontend Setup

1. **Install Dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Configure Environment Variables**:
   Add to `frontend/.env.local`:
   ```bash
   NEXT_PUBLIC_OPENAI_DOMAIN_KEY=
   # Leave empty for localhost development
   # For production, add your domain to OpenAI's allowlist
   ```

3. **Start Frontend Server**:
   ```bash
   npm run dev
   ```

4. **Access Chat Interface**:
   Navigate to `http://localhost:3000/dashboard/chat` after signing in.

### OpenAI API Key Setup (T104)

1. **Create OpenAI Account**:
   - Visit https://platform.openai.com/signup
   - Complete account registration

2. **Generate API Key**:
   - Navigate to https://platform.openai.com/api-keys
   - Click "Create new secret key"
   - Copy the key (starts with `sk-`)
   - Store securely - it won't be shown again

3. **Add to Environment**:
   ```bash
   # backend/.env
   OPENAI_API_KEY=sk-your-actual-key-here
   ```

4. **Verify Setup**:
   - Start the backend server
   - Check logs for "MCP tools initialized" message
   - No errors should appear related to OpenAI authentication

### ChatKit Domain Allowlist (Production) (T105)

For **localhost development**, no domain configuration is needed.

For **production deployment**:

1. **Deploy Frontend**:
   - Deploy to Vercel, Netlify, or your hosting provider
   - Note your production domain (e.g., `https://your-app.vercel.app`)

2. **Configure OpenAI Domain Allowlist**:
   - Navigate to https://platform.openai.com/settings/organization/security/domain-allowlist
   - Click "Add domain"
   - Enter your production domain: `https://your-app.vercel.app`
   - Save changes

3. **Update Frontend Environment**:
   ```bash
   # frontend/.env.production
   NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-domain-key-from-openai
   ```

4. **Redeploy Frontend**:
   - Redeploy with updated environment variables
   - ChatKit will now work in production

### API Endpoints (Chat)

- `POST /api/{user_id}/chat` - Send chat message and receive AI response
  - Requires JWT authentication
  - Request body: `{ "message": "Add a task to buy groceries", "conversation_id": 42 }`
  - Response: `{ "conversation_id": 42, "response": "I've created...", "tool_calls": [...] }`

### MCP Tools Available

The chatbot has access to 5 MCP tools for task management:

1. **add_task**: Create new tasks
   - Parameters: `user_id`, `title`, `description` (optional)

2. **list_tasks**: Retrieve tasks with filtering
   - Parameters: `user_id`, `status` (all/pending/completed)

3. **complete_task**: Mark tasks as done
   - Parameters: `user_id`, `task_id`

4. **update_task**: Modify task details
   - Parameters: `user_id`, `task_id`, `title` (optional), `description` (optional)

5. **delete_task**: Remove tasks
   - Parameters: `user_id`, `task_id`

### Usage Examples

**Create a task**:
```
User: "Add a task to buy groceries"
Assistant: "I've created the task 'Buy groceries' for you. Your task ID is 5."
```

**View tasks**:
```
User: "Show my tasks"
Assistant: "You have 3 pending tasks: 1) Buy groceries, 2) Call mom, 3) Pay bills"
```

**Complete a task**:
```
User: "Mark task 5 as complete"
Assistant: "Great! I've marked 'Buy groceries' as completed."
```

**Update a task**:
```
User: "Change task 1 to 'Buy groceries and fruits'"
Assistant: "I've updated task 1 to 'Buy groceries and fruits'."
```

**Delete a task**:
```
User: "Delete task 2"
Assistant: "I've removed 'Call mom' from your task list."
```

### Database Schema (Phase 3)

**Conversation Table**:
- `id`: Primary key
- `user_id`: Foreign key to user table (indexed)
- `created_at`: Timestamp
- `updated_at`: Timestamp

**Message Table**:
- `id`: Primary key
- `conversation_id`: Foreign key to conversation table (indexed)
- `user_id`: User identifier (indexed for filtering)
- `role`: Enum (USER, ASSISTANT)
- `content`: Text content
- `created_at`: Timestamp

### Troubleshooting

**"OpenAI API key not configured"**:
- Verify `OPENAI_API_KEY` is set in `backend/.env`
- Restart the backend server
- Check for typos in the key

**"ChatKit not loading"**:
- For localhost: Ensure `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` is empty or not set
- For production: Verify domain is added to OpenAI allowlist
- Check browser console for errors

**"Tool execution failed"**:
- Verify database connection is working
- Check backend logs for detailed error messages
- Ensure user is authenticated (valid JWT token)

**"Conversation not persisting"**:
- Verify database tables were created (conversation, message)
- Check database connection string
- Review backend logs for database errors