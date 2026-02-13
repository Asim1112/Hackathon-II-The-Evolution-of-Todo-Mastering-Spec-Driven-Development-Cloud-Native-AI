"""
Chat API Route - Handles stateless chat interactions with AI assistant.

This module provides the main chat endpoint that:
- Validates user authorization
- Manages conversation lifecycle
- Orchestrates agent execution with MCP tools
- Handles multi-turn tool calling
- Stores conversation history
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import json
import logging

from src.database.session import get_session
from src.auth.dependencies import get_current_user_id
from src.services.conversation_service import ConversationService
from src.agents.orchestrator import AgentOrchestrator
from src.mcp.mcp_server import get_mcp_tool_schemas, get_mcp_tool_handlers

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response Models
class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[int] = Field(None)


class ToolCall(BaseModel):
    """Tool call information in response."""
    tool: str
    parameters: Dict[str, Any]
    result: Any  # Tool results can be dict, list, string, or any JSON type


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    conversation_id: int
    response: str
    tool_calls: List[ToolCall] = Field(default_factory=list)


# Helper Functions
def _convert_mcp_schemas_to_agent_tools(schemas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convert MCP tool schemas to OpenAI function calling format.

    Strips 'user_id' from tool parameters before sending to model.
    user_id is a system-level parameter injected by the chat endpoint
    when executing tool calls - the model should never provide it.

    Also removes non-standard fields like "default" that can confuse Cerebras/Llama models.

    Args:
        schemas: List of MCP tool schemas with name, description, input_schema

    Returns:
        List of tool definitions in OpenAI format (without user_id parameter)
    """
    agent_tools = []

    for schema in schemas:
        # Deep copy input_schema to avoid mutating original
        input_schema = json.loads(json.dumps(schema["input_schema"]))

        # Strip user_id from properties and required list
        if "properties" in input_schema:
            input_schema["properties"].pop("user_id", None)

            # Remove non-standard "default" fields from all properties
            # (Cerebras/Llama models can be confused by these)
            for prop_name, prop_schema in input_schema["properties"].items():
                if "default" in prop_schema:
                    del prop_schema["default"]

        if "required" in input_schema:
            input_schema["required"] = [
                r for r in input_schema["required"] if r != "user_id"
            ]
            # Remove empty required arrays (confuses models about parameter requirements)
            if not input_schema["required"]:
                del input_schema["required"]

        agent_tools.append({
            "type": "function",
            "function": {
                "name": schema["name"],
                "description": schema["description"],
                "parameters": input_schema
            }
        })

    return agent_tools


def _format_tool_calls(tool_calls: List[Dict[str, Any]]) -> List[ToolCall]:
    """
    Format raw tool calls into ToolCall response objects.

    Args:
        tool_calls: List of raw tool call dicts from orchestrator

    Returns:
        List of ToolCall objects for API response
    """
    formatted_calls = []

    for tc in tool_calls:
        try:
            # Parse arguments, handle None/empty cases
            arguments_str = tc["function"]["arguments"]
            if arguments_str is None or arguments_str == "":
                parameters = {}
            else:
                parameters = json.loads(arguments_str)

            # Ensure parameters is a dict (not None)
            if parameters is None:
                parameters = {}

            formatted_calls.append(ToolCall(
                tool=tc["function"]["name"],
                parameters=parameters,
                result=tc.get("result", {})
            ))
        except (KeyError, json.JSONDecodeError) as e:
            logger.error(f"Failed to format tool call: {e}")
            # Include partial data if formatting fails
            formatted_calls.append(ToolCall(
                tool=tc.get("function", {}).get("name", "unknown"),
                parameters={},
                result={"error": "Failed to format tool call"}
            ))

    return formatted_calls


# Chat Endpoint
@router.post("/{user_id}/chat", response_model=ChatResponse)
async def chat(
    user_id: str,
    request: ChatRequest,
    request_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> ChatResponse:
    """
    Handle chat message and return AI response with optional tool calls.

    Flow:
    1. Validate user_id matches JWT
    2. Validate message is non-empty
    3. Create/get conversation
    4. Build context from history
    5. Prepare MCP tools for agent
    6. Run agent (may involve multiple turns for tool calls)
    7. Store messages in database
    8. Return response with conversation_id and tool_calls

    Args:
        user_id: User ID from path parameter
        request: ChatRequest with message and optional conversation_id
        request_user_id: Authenticated user ID from JWT
        session: Database session

    Returns:
        ChatResponse with conversation_id, response text, and tool_calls

    Raises:
        HTTPException 401: User ID mismatch
        HTTPException 400: Empty message
        HTTPException 404: Conversation not found
        HTTPException 500: Agent timeout, agent errors, database errors
    """
    # 1. Validate user_id matches JWT
    if user_id != request_user_id:
        logger.warning(
            f"Security: User {request_user_id} attempted to chat as {user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID mismatch"
        )

    # 2. Validate message is non-empty
    if not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty"
        )

    try:
        # 3. Create/Get conversation
        conversation_service = ConversationService(session)

        try:
            conversation = conversation_service.create_or_get_conversation(
                user_id=user_id,
                conversation_id=request.conversation_id
            )
        except ValueError as e:
            # Conversation not found or unauthorized
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )

        # 4. Build context from history
        # For new conversations, this returns just the new message
        # For existing conversations, this includes full history + new message
        if request.conversation_id is None:
            # New conversation - just the new message
            context_array = [
                {"role": "user", "content": request.message}
            ]
        else:
            # Existing conversation - build from history
            context_array = conversation_service.build_context_array(
                conversation_id=conversation.id,
                user_id=user_id,
                new_message=request.message
            )

        # 5. Prepare MCP tools (schemas auto-generated by Official MCP SDK)
        agent_tools = _convert_mcp_schemas_to_agent_tools(get_mcp_tool_schemas())
        tool_handlers = get_mcp_tool_handlers()

        # 6. Run agent
        orchestrator = AgentOrchestrator()

        # Initial agent run
        agent_result = await orchestrator.run_agent(
            messages=context_array,
            tools=agent_tools
        )

        # Track all tool calls for response
        all_tool_calls = []

        # Handle multi-turn tool calling
        current_messages = context_array.copy()

        while agent_result.get("tool_calls"):
            tool_calls = agent_result["tool_calls"]

            # Execute tools (inject user_id - stripped from model schemas)
            tool_results = await orchestrator.handle_tool_calls(
                tool_calls=tool_calls,
                tool_handlers=tool_handlers,
                inject_args={"user_id": user_id}
            )

            # Store tool calls with results for response
            for i, tc in enumerate(tool_calls):
                tool_call_with_result = tc.copy()
                # Add the result from tool_results
                if i < len(tool_results):
                    tool_call_with_result["result"] = json.loads(
                        tool_results[i]["content"]
                    )
                all_tool_calls.append(tool_call_with_result)

            # Build next message list:
            # current_messages + assistant message (with tool_calls) + tool results
            assistant_message = {
                "role": "assistant",
                "content": agent_result.get("response") or "",
                "tool_calls": tool_calls
            }

            current_messages.append(assistant_message)
            current_messages.extend(tool_results)

            # Run agent again with tool results
            agent_result = await orchestrator.run_agent(
                messages=current_messages,
                tools=agent_tools
            )

        # Final response from agent
        final_response = agent_result.get("response", "")

        # Check for error conditions
        if agent_result.get("finish_reason") == "timeout":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Agent execution timed out"
            )

        if agent_result.get("finish_reason") == "error":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Agent encountered an error"
            )

        # 7. Store messages
        try:
            conversation_service.store_messages(
                conversation_id=conversation.id,
                user_id=user_id,
                user_message=request.message,
                assistant_message=final_response
            )
        except Exception as e:
            logger.error(f"Failed to store messages: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to store conversation messages"
            )

        # 8. Return response
        return ChatResponse(
            conversation_id=conversation.id,
            response=final_response,
            tool_calls=_format_tool_calls(all_tool_calls)
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Catch-all for unexpected errors
        logger.error(f"Unexpected error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )
