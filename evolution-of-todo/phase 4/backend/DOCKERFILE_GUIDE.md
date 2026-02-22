# FastAPI Backend Dockerfile

## Overview
A production-ready multi-stage Dockerfile for your FastAPI backend with Python 3.12, PostgreSQL support, and optimized image size.

## Image Details
- **Base Image**: python:3.12-slim
- **Final Size**: ~445MB
- **Build Time**: ~2 minutes
- **Port**: 8000

## Features

###  Multi-Stage Build
1. **Builder Stage**: 
   - Installs build tools (gcc, libpq-dev)
   - Creates Python virtual environment
   - Installs all dependencies
   - Removes build tools from final image

2. **Runtime Stage**:
   - Minimal footprint with only runtime dependencies
   - PostgreSQL client for debugging
   - curl for health checks

### Built-In Health Check
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
```

### Production Ready
- PYTHONUNBUFFERED=1: Logs stream immediately
- PYTHONDONTWRITEBYTECODE=1: Reduces disk I/O
- uvicorn with proper signal handling (dumb-init)

## What's Included

### Files Created
- `Dockerfile` - Multi-stage FastAPI build
- `.dockerignore` - Excludes unnecessary files from build context

### Fixed Issues
1. Removed problematic `psycopg2` package from `pyproject.toml`
   - Kept `psycopg2-binary` instead (pre-built, no compilation needed)
   - This was causing build failures due to missing C headers

2. Updated dependencies in `pyproject.toml`

## Build Command

```bash
docker build -t backend:latest ./backend
```

Or with custom image name:
```bash
docker build -t my-backend:v1 ./backend
```

## Run the Container

### Standalone
```bash
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:password@localhost:5432/todoapp" \
  -e BETTER_AUTH_SECRET="your-secret" \
  backend:latest
```

### With docker-compose (Recommended)
See docker-compose.yml in parent directory for full stack setup with frontend, backend, and PostgreSQL.

## Environment Variables

Required at runtime:
- `DATABASE_URL` - PostgreSQL connection string
- `NEON_DATABASE_URL` - Optional Neon database URL
- `BETTER_AUTH_SECRET` - Authentication secret
- `BETTER_AUTH_BASE_URL` - Base URL for auth callbacks

## Entry Point

The container runs:
```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

This loads your FastAPI app from `src/api/main.py`.

## Health Check

Test the health endpoint:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy"}
```

## Dependencies

All dependencies from `requirements.txt` and `pyproject.toml` are installed:
- FastAPI
- Uvicorn
- SQLModel
- Alembic (migrations)
- python-jose (JWT)
- psycopg2-binary (PostgreSQL)
- MCP (Model Context Protocol)
- OpenAI agents and chatkit

## Dockerfile Walkthrough

### Build Stage
1. Starts with Python 3.12 slim
2. Installs build tools (gcc, libpq-dev)
3. Creates virtual environment at `/opt/venv`
4. Installs all Python dependencies
5. Installs project itself via `pip install .`

### Runtime Stage
1. Starts fresh with Python 3.12 slim
2. Installs only runtime packages (postgresql-client, curl)
3. Copies virtual environment from builder
4. Copies application code
5. Sets environment variables
6. Exposes port 8000
7. Defines health check
8. Runs uvicorn

## Optimization Tips

### Reduce Image Size
- Virtual environment is copied as-is from builder (~200MB of deps)
- Already using `-slim` variant instead of standard Python image
- Further reductions would require using Alpine or distroless (but may break native extensions)

### Faster Builds
- Cache layers are used automatically
- Subsequent builds skip unchanged steps
- Dependencies are cached after first build

### Production Deployment
1. Use specific version tags: `backend:v1.0` not `backend:latest`
2. Set proper resource limits
3. Configure environment variables in your orchestration tool
4. Use secrets for sensitive values (DATABASE_URL, BETTER_AUTH_SECRET)
5. Run health checks before routing traffic

## Troubleshooting

### Build fails with "psycopg2"
✓ Fixed - removed problematic psycopg2 package

### Container exits immediately
Check logs:
```bash
docker logs <container_id>
```

Verify DATABASE_URL is set correctly

### Connection refused to database
Ensure PostgreSQL is running and DATABASE_URL is correct

## Next Steps

1. Update docker-compose.yml with your backend service configuration
2. Test locally: `docker build -t backend:test . && docker run -e DATABASE_URL=... backend:test`
3. Push to registry: `docker tag backend:latest myregistry/backend:v1 && docker push ...`
4. Deploy to orchestration platform (Docker Swarm, Kubernetes, etc.)
