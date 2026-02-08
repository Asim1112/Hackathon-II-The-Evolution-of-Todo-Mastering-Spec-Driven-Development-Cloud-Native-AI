# Quickstart Guide: Authentication System

**Feature**: Frontend-Backend Authentication Connection
**Date**: 2026-02-06

## Overview
This guide provides instructions for setting up and running the authentication system with proper frontend-backend communication.

## Prerequisites
- Node.js (18.x or higher)
- Python (3.8 or higher)
- uv package manager (or pip)
- Backend database (SQLite for development, PostgreSQL for production)

## Setup Instructions

### 1. Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   # Using uv (recommended)
   uv sync

   # Or using pip
   pip install -e .
   ```

3. Set up environment variables:
   Create a `.env` file in the backend directory:
   ```env
   DATABASE_URL=sqlite:///./todo_app.db
   SECRET_KEY=your-super-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

4. Start the backend server:
   ```bash
   uv run uvicorn src.api.main:app --reload
   ```

   The backend will be available at `http://localhost:8000`

### 2. Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Configure environment variables:
   Create a `.env.local` file in the frontend directory:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

4. Start the frontend server:
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:3000`

## Authentication Flow

### User Registration (Signup)
1. User visits `/auth/signup` page
2. User enters email and password
3. Frontend sends POST request to `/api/v1/auth/signup`
4. Backend validates credentials and creates user
5. Backend returns JWT token
6. Frontend stores token and redirects to `/dashboard`

### User Login (Signin)
1. User visits `/auth/signin` page
2. User enters email and password
3. Frontend sends POST request to `/api/v1/auth/signin`
4. Backend validates credentials
5. Backend returns JWT token
6. Frontend stores token and redirects to `/dashboard`

### Protected Routes
1. Pages requiring authentication (e.g., `/dashboard`) check for valid JWT
2. Middleware redirects unauthenticated users to `/auth/signin`
3. JWT token is included in headers for API requests to backend

## Troubleshooting

### Common Issues

**"Failed to fetch" errors:**
- Verify backend server is running at the configured URL
- Check that `NEXT_PUBLIC_API_URL` matches the backend server URL
- Ensure CORS settings allow frontend domain

**Authentication not persisting:**
- Verify JWT token is being stored in localStorage
- Check that Authorization header is being sent with API requests

**Token validation errors:**
- Ensure JWT secret key is consistent between frontend and backend
- Verify token hasn't expired

### API Endpoints
- **Signup**: `POST http://localhost:8000/api/v1/auth/signup`
- **Signin**: `POST http://localhost:8000/api/v1/auth/signin`
- **Tasks**: `GET/POST/PUT/PATCH/DELETE http://localhost:8000/api/v1/tasks/*`

## Testing Authentication

### Manual Testing
1. Start both backend and frontend servers
2. Navigate to `http://localhost:3000`
3. Go to `/auth/signup` and create a new account
4. Verify you can log out and log back in at `/auth/signin`
5. Access the `/dashboard` to confirm authentication is working

### Expected Behaviors
- Signup with valid credentials → Success and redirect to dashboard
- Signin with valid credentials → Success and redirect to dashboard
- Invalid credentials → Error message displayed
- Unauthenticated access to protected routes → Redirect to signin page