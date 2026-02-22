"""
ChatKit unified endpoint for the Todo AI Assistant.

Handles all ChatKit operations (send message, load history, actions)
via a single POST endpoint processed by ChatKitServer.
"""

import logging

from fastapi import APIRouter, Request, Depends
from fastapi.responses import StreamingResponse, Response

from chatkit.server import StreamingResult

from src.agents.chatkit_server import TodoChatKitServer
from src.agents.store_adapter import PostgresStoreAdapter, RequestContext
from src.auth.dependencies import get_current_user_id

logger = logging.getLogger(__name__)

router = APIRouter()

# ---------------------------------------------------------------------------
# Singleton Server Instance
# ---------------------------------------------------------------------------

_store = PostgresStoreAdapter()
_chatkit_server = TodoChatKitServer(store=_store)


# ---------------------------------------------------------------------------
# ChatKit Endpoint
# ---------------------------------------------------------------------------

@router.post("/chatkit")
async def chatkit_endpoint(
    request: Request,
    user_id: str = Depends(get_current_user_id),
):
    """
    ChatKit unified endpoint.

    Accepts POST requests and responds with either:
    - StreamingResponse (SSE) for streaming operations
    - JSON response for non-streaming operations (e.g., load history)
    """
    context = RequestContext(user_id=user_id)

    result = await _chatkit_server.process(await request.body(), context=context)

    if isinstance(result, StreamingResult):
        return StreamingResponse(result, media_type="text/event-stream")
    return Response(content=result.json, media_type="application/json")
