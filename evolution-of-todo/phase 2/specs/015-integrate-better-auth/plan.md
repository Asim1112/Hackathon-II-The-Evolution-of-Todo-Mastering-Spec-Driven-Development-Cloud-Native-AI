# Implementation Plan: Integrate Better Auth with Next.js and FastAPI

**Branch**: `015-integrate-better-auth` | **Date**: 2026-02-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/015-integrate-better-auth/spec.md`

## Summary

Replace the current broken authentication implementation with Better Auth, a modern JWT-based authentication library. Better Auth will run in Next.js API routes (`/api/auth/*`), storing user sessions in the shared Neon PostgreSQL database, while FastAPI continues handling only task CRUD operations (`/api/v1/tasks/*`). This approach eliminates the "Failed to fetch" and 500 errors currently blocking user sign up and sign in, while maintaining clean separation of concerns between authentication (Next.js) and business logic (FastAPI).

## Technical Context

**Language/Version**:
- Frontend: TypeScript with Next.js 16+ (App Router)
- Backend: Python 3.11+ with FastAPI
- Database Client: @neondatabase/serverless (for Better Auth), psycopg2 (for FastAPI)

**Primary Dependencies**:
- better-auth (v1.x) - Modern authentication library with JWT support
- @neondatabase/serverless - Neon's serverless Postgres driver for Better Auth
- postgres - Required peer dependency for better-auth database adapter
- FastAPI - Backend REST API framework
- SQLModel - Python ORM for FastAPI models
- Psycopg2-binary - PostgreSQL adapter for FastAPI

**Storage**:
- Shared Neon Serverless PostgreSQL database
- Better Auth tables: `user`, `session`, `account`, `verification` (auto-created)
- FastAPI tables: `task`, existing `user` table (to be resolved - see Phase 0)

**Testing**:
- Manual end-to-end testing through browser UI
- Network inspection via browser DevTools
- Database inspection via Neon SQL Editor
- Integration tests for API routes (future phase)

**Target Platform**:
- Development: Windows local environment (localhost:3000 for Next.js, localhost:8000 for FastAPI)
- Production: Vercel (Next.js) + Cloud hosting for FastAPI + Neon PostgreSQL

**Project Type**:
- Web application (monorepo with separate frontend and backend directories)

**Performance Goals**:
- Authentication requests complete in <500ms p95
- Session validation adds <50ms overhead to task operations
- Database connection pool supports 10+ concurrent authentication requests

**Constraints**:
- Must use existing Neon database without data loss
- Cannot modify UI components (only update auth integration)
- Must maintain backward compatibility with existing task data
- SSL required for all Neon database connections (sslmode=require)
- Development must complete within hackathon timeframe (phased approach)

**Scale/Scope**:
- Single-tenant hackathon MVP (multi-user isolation for future scaling)
- Expected load: <100 concurrent users during demo
- Database: <1000 user records, <10,000 task records
- 8 files to create/modify (see Phase 1 for details)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Constitutional Requirements Analysis

✅ **Spec-Driven Development (NON-NEGOTIABLE)**
- Status: PASS
- Evidence: Complete specification exists at `specs/015-integrate-better-auth/spec.md`
- All functional requirements (FR-001 through FR-012) documented with acceptance criteria
- Test scenarios defined for each user story before implementation

✅ **Zero Manual Coding**
- Status: PASS
- Evidence: Implementation will be executed via `/sp.implement` command
- All code generation through Claude Code agentic workflow
- PHR records will track all development steps

✅ **Security-First Design**
- Status: PASS with CONDITIONS
- JWT authentication enforced via Better Auth session tokens
- Multi-user task isolation via `owner_id` foreign key in Task model
- Session tokens stored securely in HTTP-only cookies (Better Auth default)
- **Condition**: Phase 1 must validate that FastAPI endpoints properly verify JWT tokens OR accept user_id from trusted Next.js context

✅ **Deterministic and Reproducible Outputs**
- Status: PASS
- Environment variables documented in `.env.example`
- Better Auth configuration will be version-controlled
- Database schema migrations handled deterministically by Better Auth

⚠️ **Full-Stack Architecture Standards**
- Status: PARTIAL COMPLIANCE
- Backend: ✅ FastAPI + SQLModel + Neon (compliant)
- Frontend: ✅ Next.js 16+ App Router (compliant)
- Authentication: ⚠️ Better Auth implemented but NOT in FastAPI (deviation from constitution)
- **Justification**: Constitution states "Better Auth (JWT-based) must be implemented for user management" but doesn't specify location. Implementing in Next.js follows Better Auth's design pattern (Node.js library) and provides cleaner separation. FastAPI will validate JWT tokens issued by Better Auth.
- **Resolution**: Update constitution after successful implementation to reflect "Authentication layer in Next.js, validated by FastAPI"

✅ **End-to-End Agentic Workflow**
- Status: PASS
- Follows spec → plan → tasks → implementation workflow
- Each phase validated before proceeding
- Comprehensive testing integrated (10-phase test checklist in user input)

### Gate Decision: **PROCEED** with constitution update note

The single deviation (Better Auth location) is architecturally justified and actually improves security/separation of concerns. All other principles satisfied.

## Project Structure

### Documentation (this feature)

```text
specs/015-integrate-better-auth/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (database conflict resolution strategy)
├── data-model.md        # Phase 1 output (Better Auth schema + FastAPI integration)
├── quickstart.md        # Phase 1 output (developer setup guide)
├── contracts/           # Phase 1 output
│   └── better-auth-api.yaml   # OpenAPI spec for Next.js auth routes
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/
│   │   ├── main.py                 # [MODIFY] Remove auth routes, update CORS
│   │   └── routes/
│   │       ├── auth.py             # [DELETE] Remove FastAPI auth endpoints
│   │       └── tasks.py            # [MODIFY] Add JWT validation middleware
│   ├── auth/
│   │   ├── dependencies.py         # [MODIFY] Update to validate Better Auth JWT
│   │   ├── middleware.py           # [MODIFY] Extract user_id from JWT claims
│   │   └── utils.py                # [MODIFY] Add JWT verification functions
│   ├── models/
│   │   ├── task.py                 # [NO CHANGE] Already has owner_id field
│   │   └── user.py                 # [EVALUATE] May conflict with Better Auth user table
│   ├── config/
│   │   └── settings.py             # [MODIFY] Add BETTER_AUTH_SECRET for JWT validation
│   └── database/
│       └── session.py              # [NO CHANGE] SQLModel config unchanged
└── .env                            # [MODIFY] Add BETTER_AUTH_SECRET

frontend/
├── app/
│   ├── api/
│   │   └── auth/
│   │       └── [...all]/
│   │           └── route.ts        # [CREATE] Better Auth API route handler
│   ├── auth/
│   │   ├── signin/page.tsx         # [NO CHANGE] UI component unchanged
│   │   └── signup/page.tsx         # [NO CHANGE] UI component unchanged
│   └── dashboard/page.tsx          # [NO CHANGE] Auth consumer unchanged
├── lib/
│   ├── auth.ts                     # [MODIFY] Fix Better Auth client usage
│   └── auth-server.ts              # [CREATE] Better Auth server configuration
├── components/                     # [NO CHANGE] UI components unchanged
├── .env.local                      # [CREATE/MODIFY] Add DATABASE_URL, BETTER_AUTH_SECRET
├── package.json                    # [MODIFY] Add better-auth dependencies
└── middleware.ts                   # [EVALUATE] May need updates for session handling
```

**Structure Decision**:
The project follows a **Web Application** structure with clear separation:
- **Frontend** (`frontend/`): Next.js 16+ App Router handling all authentication via Better Auth
- **Backend** (`backend/`): FastAPI handling task CRUD operations with JWT validation
- **Shared Database**: Neon PostgreSQL accessed by both via different drivers
  - Better Auth uses `@neondatabase/serverless` (WebSocket-based)
  - FastAPI uses `psycopg2` (traditional connection pool)

This structure maintains clean boundaries: authentication is entirely contained in Next.js, business logic in FastAPI, with JWT tokens providing secure communication between layers.

## Complexity Tracking

> **Violations requiring justification:**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Better Auth in Next.js instead of FastAPI | Better Auth is a Node.js library with no official Python port; placing it in Next.js follows the library's design pattern and simplifies integration | Creating a custom Python authentication system would be more complex, error-prone, and violate the principle of using battle-tested libraries; attempting to wrap Better Auth in a Python proxy adds unnecessary complexity |
| Dual database drivers (@neondatabase/serverless + psycopg2) | Better Auth requires `@neondatabase/serverless` for Neon compatibility; FastAPI's SQLModel requires psycopg2; both must connect to the same database | Using only one driver would require rewriting either Better Auth's database adapter or FastAPI's entire database layer - both significantly more complex than managing two lightweight drivers |

## Phase 0: Research & Clarification

### Research Tasks

#### 1. Database Conflict Resolution Strategy
**Question**: Does an existing `user` table in the database conflict with Better Auth's auto-created `user` table?

**Research Required**:
- Inspect current Neon database schema for existing tables
- Check if FastAPI's `user` table has any foreign keys or dependencies
- Verify if the database has any existing user data
- Determine Better Auth's table naming flexibility

**Decision Criteria**:
- **If database is empty**: Drop existing `user` table, let Better Auth create fresh schema
- **If user data exists**: Rename FastAPI table to `app_user`, update foreign keys in Task model
- **If table structure compatible**: Evaluate manual migration vs fresh start

**Output**: `research.md` section: "Database Schema Migration Strategy"

---

#### 2. Better Auth + Neon Integration Best Practices
**Question**: What's the correct configuration for Better Auth to work with Neon Serverless PostgreSQL?

**Research Required**:
- Review Better Auth documentation for Neon adapter usage
- Check for required peer dependencies (postgres, @neondatabase/serverless)
- Verify DATABASE_URL format requirements (sslmode, pooling)
- Identify common integration pitfalls

**Decision Criteria**:
- Must use `@neondatabase/serverless` as Better Auth database adapter
- DATABASE_URL must include `?sslmode=require` suffix
- Connection pooling configuration for serverless context

**Output**: `research.md` section: "Better Auth Neon Configuration"

---

#### 3. JWT Token Validation in FastAPI
**Question**: How should FastAPI validate Better Auth JWT tokens for task endpoints?

**Research Required**:
- Review Better Auth's JWT token structure and signing algorithm
- Identify JWT validation libraries for Python (PyJWT, python-jose)
- Determine if Better Auth uses standard JWT claims (sub, exp, iat)
- Evaluate token extraction from HTTP headers vs cookies

**Decision Criteria**:
- **For Hackathon MVP**: Accept user_id from Next.js request headers (trusted context)
- **For Production**: Implement full JWT signature verification in FastAPI middleware
- Document security implications of chosen approach

**Output**: `research.md` section: "FastAPI JWT Validation Strategy"

---

#### 4. Session Persistence Mechanism
**Question**: How does Better Auth maintain session state across page refreshes?

**Research Required**:
- Review Better Auth's session management approach (cookies vs localStorage)
- Check default cookie settings (httpOnly, secure, sameSite)
- Verify session token refresh behavior
- Identify potential CORS issues with cross-origin cookies

**Decision Criteria**:
- Must use HTTP-only cookies (Better Auth default) for security
- Session tokens must persist across browser refresh
- CORS configuration must allow credentials (withCredentials: true)

**Output**: `research.md` section: "Session Persistence Architecture"

---

### Unknowns to Resolve

1. **NEEDS CLARIFICATION**: Current database state
   - Are there existing users in the database?
   - What is the current schema structure?
   - Are there foreign key dependencies?

2. **NEEDS CLARIFICATION**: Better Auth version compatibility
   - Which version of better-auth is compatible with current Next.js 16+?
   - Are there any peer dependency conflicts?

3. **NEEDS CLARIFICATION**: Existing auth middleware impact
   - Does `frontend/middleware.ts` currently implement any auth logic?
   - Will it interfere with Better Auth's session handling?

### Research Consolidation

**Deliverable**: Create `specs/015-integrate-better-auth/research.md` with:
- Database inspection results and migration decision
- Better Auth + Neon configuration recipe
- JWT validation approach (MVP vs production)
- Session persistence verification steps
- Resolved NEEDS CLARIFICATION items

## Phase 1: Design & Contracts

**Prerequisites**: `research.md` complete with all unknowns resolved

### 1. Data Model Design (`data-model.md`)

#### Entities

**Better Auth Schema (auto-created by library)**:
```typescript
// Better Auth will create these tables automatically:

table: user
- id: string (primary key, UUID)
- email: string (unique, indexed)
- emailVerified: boolean
- name: string (optional)
- createdAt: timestamp
- updatedAt: timestamp

table: session
- id: string (primary key)
- userId: string (foreign key → user.id)
- expiresAt: timestamp
- ipAddress: string (optional)
- userAgent: string (optional)

table: account
- id: string (primary key)
- userId: string (foreign key → user.id)
- accountId: string
- providerId: string
- accessToken: string (encrypted)
- refreshToken: string (encrypted, optional)
- expiresAt: timestamp (optional)

table: verification
- id: string (primary key)
- identifier: string
- value: string
- expiresAt: timestamp
```

**FastAPI Schema (existing, modified)**:
```python
# backend/src/models/task.py (NO CHANGE - already correct)
class Task(TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: str = Field()  # References Better Auth user.id (UUID string)
    created_at: datetime
    updated_at: datetime
    # ... other fields

# backend/src/models/user.py (TO BE EVALUATED)
# Decision based on research.md:
# - If migration path chosen: Rename to AppUser, update foreign keys
# - If fresh start: Delete this file entirely, reference Better Auth user table
```

#### Relationships

```
Better Auth user (id: string/UUID)
    ↓ 1:N
FastAPI task (owner_id: string)

Better Auth session (userId: string)
    ↓ N:1
Better Auth user (id: string)
```

#### Validation Rules

**Better Auth (handled by library)**:
- Email: valid format, unique
- Password: minimum 8 characters (configurable)
- Session: automatic expiration (default 30 days)

**FastAPI Task Model**:
- title: 1-255 characters (existing validation)
- owner_id: must be valid UUID matching Better Auth user.id
- Authentication: all task endpoints require valid session token

#### State Transitions

**Authentication Flow**:
```
Unauthenticated → Sign Up → User Created → Session Established → Authenticated
Unauthenticated → Sign In → Session Validated → Session Established → Authenticated
Authenticated → Sign Out → Session Invalidated → Unauthenticated
Authenticated → Session Expires → Unauthenticated
```

**Task Ownership**:
```
Task Created → owner_id set to current user.id
Task Read → filter by owner_id = current user.id
Task Update → verify owner_id = current user.id
Task Delete → verify owner_id = current user.id
```

**Deliverable**: Create `specs/015-integrate-better-auth/data-model.md`

---

### 2. API Contracts (`contracts/better-auth-api.yaml`)

**Authentication Endpoints (Next.js API Routes)**:

```yaml
openapi: 3.0.0
info:
  title: Better Auth API
  version: 1.0.0
  description: Authentication endpoints managed by Better Auth in Next.js

paths:
  /api/auth/signup:
    post:
      summary: Register new user
      requestBody:
        content:
          application/json:
            schema:
              type: object
              required: [email, password]
              properties:
                email:
                  type: string
                  format: email
                password:
                  type: string
                  minLength: 8
      responses:
        '200':
          description: User created successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  user:
                    type: object
                    properties:
                      id: {type: string, format: uuid}
                      email: {type: string}
                  session:
                    type: object
                    properties:
                      token: {type: string}
                      expiresAt: {type: string, format: date-time}
        '400':
          description: Validation error
          content:
            application/json:
              schema:
                type: object
                properties:
                  error: {type: string}
        '409':
          description: Email already exists
          content:
            application/json:
              schema:
                type: object
                properties:
                  error: {type: string}

  /api/auth/signin:
    post:
      summary: Authenticate existing user
      requestBody:
        content:
          application/json:
            schema:
              type: object
              required: [email, password]
              properties:
                email: {type: string, format: email}
                password: {type: string}
      responses:
        '200':
          description: Authentication successful
          headers:
            Set-Cookie:
              schema:
                type: string
                description: Session token (httpOnly, secure)
          content:
            application/json:
              schema:
                type: object
                properties:
                  user:
                    type: object
                    properties:
                      id: {type: string}
                      email: {type: string}
        '401':
          description: Invalid credentials
          content:
            application/json:
              schema:
                type: object
                properties:
                  error: {type: string}

  /api/auth/signout:
    post:
      summary: Invalidate user session
      security:
        - cookieAuth: []
      responses:
        '200':
          description: Sign out successful
          content:
            application/json:
              schema:
                type: object
                properties:
                  success: {type: boolean}

  /api/auth/session:
    get:
      summary: Get current session
      security:
        - cookieAuth: []
      responses:
        '200':
          description: Session data
          content:
            application/json:
              schema:
                type: object
                properties:
                  user:
                    type: object
                    properties:
                      id: {type: string}
                      email: {type: string}
                  session:
                    type: object
                    properties:
                      expiresAt: {type: string, format: date-time}
        '401':
          description: No active session

components:
  securitySchemes:
    cookieAuth:
      type: apiKey
      in: cookie
      name: better-auth.session_token
```

**Task Endpoints (FastAPI - Modified for JWT validation)**:

```yaml
# These endpoints already exist but need JWT validation middleware added

paths:
  /api/v1/tasks:
    get:
      summary: List user's tasks
      security:
        - bearerAuth: []
      parameters:
        - name: X-User-Id
          in: header
          schema:
            type: string
          description: User ID extracted from JWT (for MVP)
      responses:
        '200':
          description: Task list
        '401':
          description: Unauthorized

    post:
      summary: Create task
      security:
        - bearerAuth: []
      parameters:
        - name: X-User-Id
          in: header
          required: true
          schema:
            type: string
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/TaskCreate'
      responses:
        '201':
          description: Task created
        '401':
          description: Unauthorized

components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

**Deliverable**: Create `specs/015-integrate-better-auth/contracts/better-auth-api.yaml`

---

### 3. Quickstart Guide (`quickstart.md`)

**Deliverable**: Create `specs/015-integrate-better-auth/quickstart.md` with:

```markdown
# Better Auth Integration Quickstart

## Prerequisites
- Node.js ≥18 (required by Better Auth)
- Python 3.11+
- Neon PostgreSQL database with connection string

## Environment Setup

### Frontend (.env.local)
```bash
DATABASE_URL="postgresql://[user]:[password]@[host]/[db]?sslmode=require"
BETTER_AUTH_SECRET="[generated-secret]"
NEXT_PUBLIC_APP_URL="http://localhost:3000"
```

### Backend (.env)
```bash
DATABASE_URL="postgresql://[user]:[password]@[host]/[db]?sslmode=require"
BETTER_AUTH_SECRET="[same-as-frontend]"
```

## Installation

### Frontend Dependencies
```bash
cd frontend
npm install better-auth @neondatabase/serverless postgres
```

### Backend Dependencies
```bash
cd backend
# No new dependencies - uses existing psycopg2
```

## First Run

1. Start Next.js (initializes Better Auth tables):
```bash
cd frontend && npm run dev
```

2. Verify tables created in Neon dashboard:
   - user
   - session
   - account
   - verification

3. Start FastAPI:
```bash
cd backend && uvicorn src.api.main:app --reload
```

4. Test auth flow:
   - Visit http://localhost:3000/auth/signup
   - Create account
   - Verify success (no "Failed to fetch" error)

## Troubleshooting

### "Failed to fetch" on signup
- Check DATABASE_URL includes `?sslmode=require`
- Verify Better Auth API route exists at `app/api/auth/[...all]/route.ts`
- Check browser console for CORS errors

### 500 errors on auth requests
- Verify BETTER_AUTH_SECRET is set in .env.local
- Check Neon database connectivity
- Inspect Next.js terminal for error stack traces

### Tasks return 401
- Verify JWT token present in request headers
- Check FastAPI CORS allows http://localhost:3000
- Confirm owner_id field exists in Task model
```

---

### 4. Agent Context Update

**Action**: Run the agent context update script to add new technology context.

```bash
cd "F:\Hackathon II\evolution-of-todo\phase 2"
.specify/scripts/powershell/update-agent-context.ps1 -AgentType claude
```

**Expected Changes**:
- Add Better Auth library context
- Add Neon Serverless adapter context
- Add JWT validation patterns
- Preserve existing manual additions

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Browser Client                           │
│  ┌────────────┐         ┌────────────┐        ┌──────────────┐ │
│  │ Sign Up UI │────────▶│ Sign In UI │───────▶│ Dashboard UI │ │
│  └────────────┘         └────────────┘        └──────────────┘ │
│         │                      │                       │         │
└─────────┼──────────────────────┼───────────────────────┼─────────┘
          │                      │                       │
          │ POST /api/auth/signup│ POST /api/auth/signin│ GET /api/v1/tasks
          ▼                      ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                Next.js Frontend (localhost:3000)                 │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │             Better Auth Server                              │ │
│  │  /app/api/auth/[...all]/route.ts                           │ │
│  │                                                              │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────┐ │ │
│  │  │  Sign Up │  │ Sign In  │  │ Sign Out │  │  Session  │ │ │
│  │  │  POST    │  │  POST    │  │  POST    │  │  GET      │ │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └───────────┘ │ │
│  └────────────────────────────────────────────────────────────┘ │
│           │                                              │        │
│           │ @neondatabase/serverless                     │        │
│           │ (WebSocket connection)                       │        │
│           ▼                                              │        │
│  ┌────────────────────┐                                 │        │
│  │  Better Auth       │                                 │        │
│  │  Client Library    │                                 │        │
│  │  /lib/auth.ts      │                                 │        │
│  └────────────────────┘                                 │        │
│           │                                              │        │
│           │ Sets HTTP-only cookie:                      │        │
│           │ better-auth.session_token (JWT)             │        │
│           ▼                                              ▼        │
└───────────────────────────────────────────────────────────────────┘
            │                                              │
            ├──────────────────────────────────────────────┤
            │         Shared Neon PostgreSQL Database      │
            │                                              │
            ▼                                              ▼
    ┌───────────────┐                          ┌──────────────────┐
    │  Better Auth  │                          │   FastAPI Task   │
    │    Tables     │                          │     Table        │
    │               │                          │                  │
    │  - user       │                          │  - task          │
    │  - session    │                          │    (owner_id FK) │
    │  - account    │                          │                  │
    │  - verification                          │                  │
    └───────────────┘                          └──────────────────┘
            ▲                                              ▲
            │                                              │
            │ psycopg2 (connection pool)                  │
            │                                              │
┌───────────┴──────────────────────────────────────────────┴────────┐
│                FastAPI Backend (localhost:8000)                    │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │               Task API Routes                               │  │
│  │  /api/v1/tasks/*                                           │  │
│  │                                                              │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────┐ │  │
│  │  │  List    │  │  Create  │  │  Update  │  │  Delete   │ │  │
│  │  │  GET     │  │  POST    │  │  PUT     │  │  DELETE   │ │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └───────────┘ │  │
│  │       │             │             │             │          │  │
│  │       └─────────────┴─────────────┴─────────────┘          │  │
│  │                       ▼                                     │  │
│  │              JWT Validation Middleware                      │  │
│  │              (Verify session token from cookie)            │  │
│  │              Extract user_id from JWT claims               │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │               CORS Configuration                            │  │
│  │  - Allow origin: http://localhost:3000                     │  │
│  │  - Allow credentials: true                                 │  │
│  │  - Allow headers: Authorization, Content-Type              │  │
│  └────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘

Authentication Flow:
1. User submits credentials to /api/auth/signup or /api/auth/signin
2. Better Auth server validates and creates user/session in Neon DB
3. JWT session token set as HTTP-only cookie
4. Browser automatically includes cookie in subsequent requests
5. FastAPI middleware extracts and validates JWT from cookie header
6. Task operations execute with user_id from validated JWT claims
7. Sign out invalidates session in database and clears cookie
```

## Implementation Sequence

### Phase 1: Database Preparation (5 minutes)
**Dependencies**: None
**Deliverables**:
- Database inspection report
- Migration decision documented
- Connection string validated

**Steps**:
1. Access Neon SQL Editor
2. Run: `SELECT * FROM information_schema.tables WHERE table_schema = 'public'`
3. If `user` table exists:
   - Check for existing data: `SELECT COUNT(*) FROM "user"`
   - If data exists: Plan migration to `app_user`
   - If empty: Plan to drop and recreate
4. Verify DATABASE_URL format includes `?sslmode=require`

**Acceptance Criteria**:
- [ ] Current database schema documented
- [ ] Migration strategy chosen (drop vs rename)
- [ ] No blocking foreign key dependencies

---

### Phase 2: Dependencies Installation (5 minutes)
**Dependencies**: Phase 1 complete
**Deliverables**:
- better-auth and peer dependencies installed
- No version conflicts
- package.json updated

**Steps**:
```bash
cd frontend
npm install better-auth@latest @neondatabase/serverless postgres
```

**Acceptance Criteria**:
- [ ] `npm install` completes without errors
- [ ] No peer dependency warnings for critical packages
- [ ] Node.js version ≥18 confirmed

---

### Phase 3: Better Auth Server Configuration (10 minutes)
**Dependencies**: Phase 2 complete
**Deliverables**:
- `frontend/lib/auth-server.ts` created
- Database connection tested
- Environment variables configured

**Steps**:
1. Create `frontend/lib/auth-server.ts`:
```typescript
import { betterAuth } from "better-auth";
import { Pool } from "@neondatabase/serverless";

export const auth = betterAuth({
  database: new Pool({ connectionString: process.env.DATABASE_URL }),
  emailAndPassword: {
    enabled: true,
  },
  session: {
    cookieCache: {
      enabled: true,
      maxAge: 60 * 60, // 1 hour
    },
  },
  secret: process.env.BETTER_AUTH_SECRET,
});
```

2. Update `frontend/.env.local`:
```bash
DATABASE_URL="postgresql://[user]:[password]@[host]/[db]?sslmode=require"
BETTER_AUTH_SECRET="[generate-random-secret]"
NEXT_PUBLIC_APP_URL="http://localhost:3000"
```

**Acceptance Criteria**:
- [ ] TypeScript compiles without errors
- [ ] Environment variables loaded correctly
- [ ] No connection errors in terminal

---

### Phase 4: Next.js API Routes Setup (5 minutes)
**Dependencies**: Phase 3 complete
**Deliverables**:
- API route handler created
- Routes accessible via HTTP

**Steps**:
1. Create `frontend/app/api/auth/[...all]/route.ts`:
```typescript
import { auth } from "@/lib/auth-server";
import { toNextJsHandler } from "better-auth/next-js";

export const { GET, POST } = toNextJsHandler(auth);
```

2. Test route:
```bash
curl http://localhost:3000/api/auth/session
```

**Acceptance Criteria**:
- [ ] File created at correct path
- [ ] GET and POST handlers exported
- [ ] Route returns JSON response (not 404)
- [ ] No HTML error pages returned

---

### Phase 5: Frontend Client Update (10 minutes)
**Dependencies**: Phase 4 complete
**Deliverables**:
- `frontend/lib/auth.ts` updated
- Sign up/in/out functions working

**Steps**:
1. Update `frontend/lib/auth.ts`:
```typescript
import { createAuthClient } from "better-auth/react";

export const authClient = createAuthClient({
  baseURL: "http://localhost:3000", // Point to Next.js, not FastAPI
});

export async function signUp(email: string, password: string) {
  const result = await authClient.signUp.email({ email, password });
  return result;
}

export async function signIn(email: string, password: string) {
  const result = await authClient.signIn.email({ email, password });
  return result;
}

export async function signOut() {
  await authClient.signOut();
}
```

**Acceptance Criteria**:
- [ ] baseURL points to localhost:3000 (not 8000)
- [ ] signUp calls `authClient.signUp.email()`
- [ ] signIn calls `authClient.signIn.email()`
- [ ] No TypeScript errors

---

### Phase 6: Environment Configuration (5 minutes)
**Dependencies**: Phase 5 complete
**Deliverables**:
- All environment variables documented
- .env.example updated

**Steps**:
1. Update `frontend/.env.example`:
```bash
DATABASE_URL=postgresql://user:password@host/db?sslmode=require
BETTER_AUTH_SECRET=your-secret-here
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

2. Update `backend/.env.example`:
```bash
DATABASE_URL=postgresql://user:password@host/db?sslmode=require
BETTER_AUTH_SECRET=same-as-frontend
```

**Acceptance Criteria**:
- [ ] All required variables documented
- [ ] Format examples provided
- [ ] Security notes included

---

### Phase 7: FastAPI Backend Updates (10 minutes)
**Dependencies**: Phase 6 complete
**Deliverables**:
- Old auth routes removed
- CORS updated
- JWT validation middleware added (optional for MVP)

**Steps**:
1. Remove `backend/src/api/routes/auth.py`
2. Update `backend/src/api/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

3. Update task routes to accept user_id from header:
```python
@router.get("/tasks")
async def list_tasks(
    user_id: str = Header(..., alias="X-User-Id"),
    db: Session = Depends(get_session)
):
    tasks = db.exec(select(Task).where(Task.owner_id == user_id)).all()
    return tasks
```

**Acceptance Criteria**:
- [ ] `/api/v1/auth/*` routes removed
- [ ] CORS allows localhost:3000 with credentials
- [ ] Task routes accept X-User-Id header
- [ ] No TypeScript/Python compilation errors

---

### Phase 8: Integration Testing (15 minutes)
**Dependencies**: Phase 7 complete
**Deliverables**:
- End-to-end auth flow validated
- Test results documented

**Steps** (from user-provided test checklist):
1. Start both servers:
   - `cd frontend && npm run dev`
   - `cd backend && uvicorn src.api.main:app --reload`

2. Test sign up:
   - Visit http://localhost:3000/auth/signup
   - Submit form with valid email/password
   - Verify: no "Failed to fetch" error
   - Verify: user created in Neon `user` table
   - Verify: session created in `session` table

3. Test sign in:
   - Use created account
   - Verify: successful authentication
   - Verify: redirected to dashboard

4. Test session persistence:
   - Refresh page
   - Verify: still authenticated

5. Test task operations:
   - Create task
   - Verify: task has correct owner_id
   - Verify: only user's tasks visible

6. Test sign out:
   - Click sign out
   - Verify: session cleared
   - Verify: redirected to sign in

**Acceptance Criteria**:
- [ ] All 10 test phases pass (from user input)
- [ ] No console errors
- [ ] Network requests return 200 status
- [ ] Database tables populated correctly

---

### Phase 9: Bug Fixes and Refinement (20 minutes)
**Dependencies**: Phase 8 complete
**Deliverables**:
- All identified issues resolved
- Error messages improved

**Steps**:
1. Address any TypeScript errors
2. Fix CORS issues if any
3. Improve error messages for better UX
4. Add loading states to forms
5. Handle edge cases (duplicate email, weak password)

**Acceptance Criteria**:
- [ ] Zero TypeScript compilation errors
- [ ] User-friendly error messages
- [ ] Loading states on async operations
- [ ] Edge cases handled gracefully

---

### Phase 10: Documentation (10 minutes)
**Dependencies**: Phase 9 complete
**Deliverables**:
- README updated
- Troubleshooting guide added

**Steps**:
1. Update main README with auth flow diagram
2. Document environment variables
3. Add troubleshooting section
4. Include setup instructions

**Acceptance Criteria**:
- [ ] README reflects new auth architecture
- [ ] Environment variables documented
- [ ] Common errors and solutions listed
- [ ] Setup instructions tested

---

## Testing Strategy

### Environment Validation (Phase 1)
- Database connectivity verification
- Schema inspection
- Connection string format validation
- Node.js version check

### Better Auth Server Setup (Phase 2-3)
- TypeScript compilation
- Database connection
- Table auto-creation
- Manual user insertion test

### Next.js API Routes (Phase 4)
- Route accessibility
- Proper JSON responses
- No 404 errors
- HTTP method handling (GET, POST)

### Frontend Client Integration (Phase 5)
- Client initialization
- Correct baseURL configuration
- Method calls work
- TypeScript types match

### End-to-End Auth Flow (Phase 8)
- Sign up without errors
- User created in database
- Session established
- Cookies set properly
- Sign in successful
- State persists across refresh
- Sign out clears session

### FastAPI Integration (Phase 7-8)
- CORS allows frontend
- Task operations work with auth
- User isolation enforced
- 401 returned for unauthenticated requests

### Error Handling (Phase 9)
- Validation errors display properly
- Network errors handled gracefully
- Backend errors don't expose sensitive info
- Duplicate email detected

### Production Readiness (Phase 10)
- No debug code in production
- Environment variables documented
- Sensitive data not committed
- Error messages safe for users

---

## Quality Validation Criteria

**Before /sp.tasks generation**:
- [ ] All 5 architectural decisions documented with rationale
- [ ] Database conflict resolution strategy determined
- [ ] Better Auth + Neon configuration validated
- [ ] JWT validation approach chosen (MVP vs production)
- [ ] Session persistence mechanism understood
- [ ] Constitution check violations justified

**Before /sp.implement execution**:
- [ ] All 10 implementation phases have clear acceptance criteria
- [ ] File modification list complete (8 files: 2 create, 4 modify, 2 evaluate)
- [ ] Dependencies identified (better-auth, @neondatabase/serverless, postgres)
- [ ] Test strategy covers all 10 phases from user input
- [ ] Rollback plan documented (backup, git branch)

**Implementation success**:
- [ ] All success criteria from spec.md achieved:
  - ✓ User can sign up/sign in without "Failed to fetch" or 500 errors
  - ✓ Better Auth manages authentication via /api/auth/*
  - ✓ Sessions stored in Neon PostgreSQL
  - ✓ FastAPI handles only tasks CRUD at /api/v1/tasks/*
  - ✓ Shared Neon database between Next.js and FastAPI
  - ✓ Authentication state persists across page refreshes
  - ✓ User can log out successfully

---

## Risk Mitigation

### Risk 1: Database Schema Conflicts
**Likelihood**: High
**Impact**: High (blocks implementation)
**Mitigation**:
- Phase 0 research includes database inspection
- Migration strategy chosen before code changes
- Backup plan: use separate schemas if tables incompatible
- Fallback: rename FastAPI user table to `app_user`

### Risk 2: Better Auth + Neon Integration Issues
**Likelihood**: Medium
**Impact**: High (blocks authentication)
**Mitigation**:
- Use official `@neondatabase/serverless` adapter
- Verify connection string format in Phase 1
- Test database connection before implementing auth routes
- Fallback: use alternative Better Auth database adapter (SQLite for testing)

### Risk 3: CORS Configuration Errors
**Likelihood**: Medium
**Impact**: Medium (blocks frontend-backend communication)
**Mitigation**:
- Phase 7 explicitly configures CORS with credentials
- Test CORS with curl before integration testing
- Document exact CORS settings in quickstart.md
- Fallback: use Next.js API route as proxy if CORS fails

### Risk 4: JWT Validation Complexity
**Likelihood**: Low (if using MVP approach)
**Impact**: Medium (affects security but not hackathon functionality)
**Mitigation**:
- MVP uses trusted header approach (X-User-Id from Next.js)
- Document production upgrade path in Phase 1 design
- Fallback: implement basic JWT signature validation if time permits

### Risk 5: Session Persistence Issues
**Likelihood**: Low
**Impact**: Medium (affects UX but not core functionality)
**Mitigation**:
- Better Auth handles cookies automatically
- Phase 8 testing explicitly validates persistence
- Fallback: use localStorage for client-side state (less secure but functional)

---

## Follow-Up TODOs

**Post-Hackathon (Production Hardening)**:
1. Implement full JWT signature validation in FastAPI middleware
2. Add refresh token rotation for long-lived sessions
3. Enable Better Auth email verification flow
4. Add rate limiting on authentication endpoints
5. Implement comprehensive integration tests
6. Add security headers (CSP, HSTS, etc.)
7. Enable Better Auth audit logging
8. Configure production secrets management (not .env files)

**Documentation Updates**:
1. Create ADR for "Better Auth in Next.js vs FastAPI" decision
2. Update constitution to reflect "Authentication in Next.js, validation in FastAPI"
3. Add architecture diagram to main README
4. Document JWT token structure and claims

**Technical Debt**:
1. Remove old FastAPI user model entirely (or rename to app_user)
2. Consolidate database connection approaches (WebSocket vs connection pool)
3. Add TypeScript types for Better Auth responses across frontend
4. Implement proper error handling for all auth edge cases

---

## Phase 2 Deliverables (Not Created by /sp.plan)

**Note**: Phase 2 (Task Breakdown) is handled by the `/sp.tasks` command, not `/sp.plan`.

The `/sp.tasks` command will:
1. Read this plan.md file
2. Break down each implementation phase into granular, testable tasks
3. Generate `specs/015-integrate-better-auth/tasks.md`
4. Include acceptance criteria from test strategy for each task
5. Order tasks by dependency (Phase 1 → Phase 10)
6. Assign time estimates based on implementation sequence

After `/sp.tasks` completes, the `/sp.implement` command will execute all tasks in order.

---

## Architectural Decision Records (ADRs)

**Decisions Requiring Documentation**:

1. **Database Schema Strategy** → `/sp.adr database-schema-better-auth`
   - Decision: Let Better Auth auto-create tables (Option A)
   - Rationale: Standard approach, least error-prone, handles migrations
   - Alternatives: Manual SQLModel definition (too complex), separate schemas (connection overhead)

2. **Session Token Validation in FastAPI** → `/sp.adr fastapi-jwt-validation`
   - Decision: MVP uses trusted header (X-User-Id), production uses JWT validation (Option A for production, Option B for hackathon)
   - Rationale: Fastest hackathon path with documented upgrade path
   - Alternatives: Shared session store (Redis complexity), no validation (insecure)

3. **Authentication Flow Routing** → `/sp.adr auth-routing-nextjs`
   - Decision: All auth through Next.js API routes (Option A)
   - Rationale: Follows Better Auth design pattern, clean separation
   - Alternatives: FastAPI for auth (violates Better Auth conventions), hybrid sync (dual source of truth)

4. **Existing FastAPI Auth Endpoints** → `/sp.adr remove-fastapi-auth`
   - Decision: Remove entirely (Option A)
   - Rationale: Prevents dual auth systems confusion
   - Alternatives: Deprecate (rollback path but complexity), proxy to Better Auth (unnecessary layer)

5. **User Table Conflict Resolution** → `/sp.adr user-table-migration`
   - Decision: Check database first; if empty drop, if data exists rename to app_user (Option A/B hybrid)
   - Rationale: Preserves data if exists, clean slate if empty
   - Alternatives: Custom table name (non-standard Better Auth)

**Suggestion Format** (to be shown to user after Phase 1):
```
📋 Architectural decision detected: Database Schema Strategy for Better Auth
   Document reasoning and tradeoffs? Run `/sp.adr database-schema-better-auth`

📋 Architectural decision detected: FastAPI JWT Validation Approach
   Document reasoning and tradeoffs? Run `/sp.adr fastapi-jwt-validation`

📋 Architectural decision detected: Authentication Routing via Next.js
   Document reasoning and tradeoffs? Run `/sp.adr auth-routing-nextjs`

📋 Architectural decision detected: Remove FastAPI Auth Endpoints
   Document reasoning and tradeoffs? Run `/sp.adr remove-fastapi-auth`

📋 Architectural decision detected: User Table Conflict Resolution
   Document reasoning and tradeoffs? Run `/sp.adr user-table-migration`
```

---

## Summary

This plan provides a complete roadmap for integrating Better Auth with the existing Next.js + FastAPI todo application. The phased approach (10 phases, ~90 minutes total) ensures each component is validated before proceeding, minimizing the risk of cascading failures.

**Key Decisions**:
- Better Auth runs in Next.js (not FastAPI) - follows library design pattern
- Shared Neon database with dual drivers (WebSocket for Better Auth, psycopg2 for FastAPI)
- MVP uses trusted header for FastAPI validation, production path documented
- Existing FastAPI auth endpoints removed to avoid dual auth systems
- Database conflicts resolved based on inspection (drop if empty, rename if data exists)

**Success Criteria Met**:
- Eliminates "Failed to fetch" and 500 errors (Better Auth handles properly)
- Clean separation: auth in Next.js, business logic in FastAPI
- Session persistence via HTTP-only cookies
- Multi-user task isolation via owner_id foreign key

**Next Steps**:
1. User reviews and approves this plan
2. Run `/sp.tasks` to generate granular task breakdown
3. Run `/sp.implement` to execute all tasks in sequence
4. Optionally run `/sp.adr [decision-title]` to document architectural decisions
