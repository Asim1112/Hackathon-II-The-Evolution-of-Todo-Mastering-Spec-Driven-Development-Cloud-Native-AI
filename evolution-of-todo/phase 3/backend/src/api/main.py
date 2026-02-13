from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from src.api.routes import tasks, chat, chatkit
from src.database.session import create_db_and_tables
from src.mcp.mcp_server import mcp


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and MCP session manager on startup."""
    create_db_and_tables()
    async with mcp.session_manager.run():
        yield


app = FastAPI(title="Todo API", version="1.0.0", lifespan=lifespan)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(tasks.router, prefix="/api/v1", tags=["tasks"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(chatkit.router, tags=["chatkit"])


def create_error_response(detail: str, error_code: str = None, status_code: int = 500):
    """Create a standardized error response with timestamp."""
    return JSONResponse(
        status_code=status_code,
        content={
            "detail": detail,
            "error_code": error_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# Custom exception handlers for authentication errors
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    error_codes = {
        400: "BAD_REQUEST",
        401: "AUTH_001",
        403: "AUTH_002",
        404: "NOT_FOUND",
        422: "VALIDATION_ERROR",
        500: "SERVER_ERROR"
    }
    error_code = error_codes.get(exc.status_code)
    return create_error_response(
        detail=exc.detail or "An error occurred",
        error_code=error_code,
        status_code=exc.status_code
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors."""
    errors = exc.errors()
    detail = "; ".join([f"{err['loc'][-1]}: {err['msg']}" for err in errors])
    return create_error_response(
        detail=detail,
        error_code="VALIDATION_ERROR",
        status_code=422
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    return create_error_response(
        detail="Internal server error",
        error_code="SERVER_ERROR",
        status_code=500
    )


@app.get("/")
def read_root():
    return {"message": "Welcome to the Todo API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


# Mount Official MCP Server LAST - after all route definitions
# streamable_http_app() creates a Starlette app with internal route at "/mcp"
# Mounting at "" means /mcp is accessible directly at http://localhost:8001/mcp
# MUST be last so Mount("") doesn't catch requests meant for other routes
app.mount("", mcp.streamable_http_app())