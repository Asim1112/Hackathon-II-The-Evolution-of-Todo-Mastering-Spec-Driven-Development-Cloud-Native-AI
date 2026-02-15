"""
ChatKitServer subclass integrating OpenAI Agents SDK with ChatKit.

Uses Agent + Runner + FunctionTool to orchestrate tool calls,
registering MCP tools directly with the Agent (no HTTP loopback).

Follows official ChatKit + Agents SDK integration pattern:
- AgentContext for proper context management
- Runner.run_streamed() for streaming execution
- stream_agent_response() for event conversion
"""

import logging
from typing import AsyncIterator

from agents import Agent, Runner, ModelSettings, FunctionTool, RunContextWrapper
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel

from chatkit.server import ChatKitServer
from chatkit.agents import AgentContext, simple_to_agent_input, stream_agent_response
from chatkit.types import (
    ThreadMetadata, UserMessageItem, ThreadStreamEvent,
    ThreadItemAddedEvent, ThreadItemUpdatedEvent, ThreadItemDoneEvent,
)

from src.agents.prompts import get_system_prompt
from src.agents.store_adapter import PostgresStoreAdapter, RequestContext
from src.config.settings import settings
from src.agents.model_factory import create_model_with_function_calling
from src.mcp.mcp_server import get_mcp_tool_handlers, get_mcp_tool_schemas

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Agent Factory
# ---------------------------------------------------------------------------

_agent_instance: Agent | None = None


async def _create_model_with_tools() -> OpenAIChatCompletionsModel:
    """
    Create an LLM model with function calling support.

    Uses model factory to automatically:
    1. Try Cerebras first
    2. Fall back to OpenAI if needed (based on configuration)
    """
    model = await create_model_with_function_calling()
    logger.info(f"[MODEL] Model ready: {model.model}")
    return model


def _create_function_tools() -> list[FunctionTool]:
    """
    Convert MCP tool handlers into FunctionTool instances for direct Agent registration.

    This eliminates the need for HTTP loopback connection to MCP server.
    Tools are registered directly with the Agent, avoiding circular dependency.

    Security: user_id is injected from authenticated context, not from LLM output.
    """
    tool_handlers = get_mcp_tool_handlers()
    tool_schemas = get_mcp_tool_schemas()

    function_tools = []

    for schema in tool_schemas:
        tool_name = schema["name"]
        handler = tool_handlers.get(tool_name)

        if not handler:
            logger.warning(f"No handler found for tool: {tool_name}")
            continue

        # Remove user_id from schema - it will be injected from context
        modified_schema = schema["input_schema"].copy()
        if "properties" in modified_schema and "user_id" in modified_schema["properties"]:
            modified_schema["properties"] = {
                k: v for k, v in modified_schema["properties"].items() if k != "user_id"
            }
            if "required" in modified_schema and "user_id" in modified_schema["required"]:
                modified_schema["required"] = [
                    r for r in modified_schema["required"] if r != "user_id"
                ]

        # Create wrapper with proper closure (bind handler in default argument)
        def make_tool_wrapper(tool_handler):
            async def tool_wrapper(ctx: RunContextWrapper, args: str) -> str:
                """Wrapper that calls MCP tool handler with parsed arguments."""
                import json

                # Parse LLM-provided arguments
                parsed_args = json.loads(args)

                # Extract user_id from the authenticated request context.
                # ctx.context is AgentContext which wraps RequestContext.
                # AgentContext.request_context.user_id is the authenticated user.
                agent_ctx = ctx.context
                if hasattr(agent_ctx, 'request_context') and hasattr(agent_ctx.request_context, 'user_id'):
                    user_id = agent_ctx.request_context.user_id
                else:
                    user_id = "unknown"
                    logger.warning("[TOOL] Could not extract user_id from context")

                # Strip user_id from parsed_args to prevent duplicate keyword argument
                # The LLM may include user_id despite schema stripping
                parsed_args.pop("user_id", None)

                logger.info(f"[TOOL] Executing {tool_handler.__name__}: user_id={user_id}, args={parsed_args}")

                # Call the MCP tool handler with user_id + parsed args
                try:
                    result = await tool_handler(user_id=user_id, **parsed_args)
                    logger.info(f"[TOOL] {tool_handler.__name__} succeeded: {result}")
                    return json.dumps(result)
                except Exception as e:
                    logger.error(f"[TOOL] {tool_handler.__name__} failed: {e}")
                    # Return error as JSON so the model gets clear feedback
                    return json.dumps({"error": str(e), "status": "failed"})

            return tool_wrapper

        function_tool = FunctionTool(
            name=tool_name,
            description=schema["description"],
            params_json_schema=modified_schema,
            on_invoke_tool=make_tool_wrapper(handler),
        )

        function_tools.append(function_tool)
        logger.info(f"[TOOL] Registered: {tool_name}")

    return function_tools


async def get_agent() -> Agent:
    """Get or create the singleton Agent with direct tool registration."""
    global _agent_instance

    if _agent_instance is not None:
        return _agent_instance

    # Create tools from MCP handlers
    tools = _create_function_tools()
    logger.info(f"[AGENT] Created {len(tools)} function tools")

    model = await _create_model_with_tools()

    _agent_instance = Agent(
        name="TodoAssistant",
        instructions=get_system_prompt(),
        model=model,
        tools=tools,
        model_settings=ModelSettings(
            temperature=0.7,
            max_tokens=1000,
        ),
    )

    logger.info(f"[AGENT] Agent initialized with tools: {[t.name for t in tools]}")
    return _agent_instance


# ---------------------------------------------------------------------------
# ChatKit Server
# ---------------------------------------------------------------------------

class TodoChatKitServer(ChatKitServer[RequestContext]):
    """ChatKitServer subclass for the Todo AI Assistant."""

    async def respond(
        self,
        thread: ThreadMetadata,
        input_user_message: UserMessageItem | None,
        context: RequestContext,
    ) -> AsyncIterator[ThreadStreamEvent]:
        """
        Handle a chat message using the OpenAI Agents SDK with ChatKit integration.

        Follows official ChatKit + Agents SDK pattern:
        1. Load recent conversation history from store
        2. Convert to agent input format using simple_to_agent_input()
        3. Create AgentContext for proper ChatKit integration
        4. Run agent with streaming execution (Runner.run_streamed)
        5. Stream response using stream_agent_response() helper
        """
        # Get agent instance
        agent = await get_agent()

        # Load recent history (20 items, ascending order for agent context)
        items_page = await self.store.load_thread_items(
            thread.id,
            after=None,
            limit=20,
            order="asc",
            context=context,
        )

        # Convert ChatKit items to agent input format
        input_items = await simple_to_agent_input(items_page.data)

        logger.info(f"Processing chat request for user: {context.user_id}")
        logger.info(f"Input items count: {len(input_items)}")

        # Create AgentContext for ChatKit integration
        agent_context = AgentContext(
            thread=thread,
            store=self.store,
            request_context=context,
        )

        # Run agent with streaming execution
        result = Runner.run_streamed(agent, input_items, context=agent_context)

        # Stream ChatKit events with unique ID remapping and tool result handling.
        # OpenAIChatCompletionsModel (Cerebras/non-OpenAI backends) generates
        # synthetic Responses API item IDs that can collide across responses.
        # When the ChatKit React frontend receives a ThreadItemUpdatedEvent with
        # an item_id already in its state from a previous response, it appends
        # new text to the previous message instead of creating a new one.
        # Fix: remap assistant message IDs to guaranteed-unique UUIDs.
        id_remap: dict[str, str] = {}

        # Track tool call IDs for proper result mapping
        tool_call_remap: dict[str, str] = {}

        # Track pending tool calls to display their results when available
        pending_tool_calls: dict[str, dict] = {}

        async for event in stream_agent_response(agent_context, result):
            if isinstance(event, ThreadItemAddedEvent):
                if hasattr(event.item, 'type') and event.item.type == "assistant_message":
                    old_id = event.item.id
                    new_id = self.store.generate_item_id("message", thread, context)
                    id_remap[old_id] = new_id
                    event.item.id = new_id
                    logger.info(f"[STREAM] Remapped assistant message ID: {old_id} -> {new_id}")
                elif hasattr(event.item, 'type') and event.item.type == "client_tool_call":
                    # Handle client tool call items and map their IDs
                    old_id = event.item.id
                    new_id = self.store.generate_item_id("tool_call", thread, context)
                    tool_call_remap[old_id] = new_id
                    event.item.id = new_id
                    # Store pending tool call info for result tracking
                    pending_tool_calls[new_id] = {
                        'name': event.item.name,
                        'arguments': event.item.arguments,
                        'original_id': old_id,
                        'status': event.item.status if hasattr(event.item, 'status') else 'pending'
                    }
                    logger.info(f"[STREAM] Remapped tool call ID: {old_id} -> {new_id}, name: {event.item.name}")

            elif isinstance(event, ThreadItemUpdatedEvent):
                # Remap IDs for both assistant messages and tool calls
                if event.item_id in id_remap:
                    event = event.model_copy(update={"item_id": id_remap[event.item_id]})
                elif event.item_id in tool_call_remap:
                    event = event.model_copy(update={"item_id": tool_call_remap[event.item_id]})

            elif isinstance(event, ThreadItemDoneEvent):
                # Remap IDs for both assistant messages and tool calls
                if hasattr(event.item, 'id') and event.item.id in id_remap:
                    event.item.id = id_remap[event.item.id]
                elif hasattr(event.item, 'id') and event.item.id in tool_call_remap:
                    # When tool call is done, check if we have output to display
                    original_id = event.item.id
                    if original_id in tool_call_remap:
                        remapped_id = tool_call_remap[original_id]
                        if remapped_id in pending_tool_calls:
                            tool_info = pending_tool_calls[remapped_id]
                            logger.info(f"[STREAM] Tool call completed: {tool_info['name']}, status: {getattr(event.item, 'status', 'unknown')}")

                        event.item.id = remapped_id

            yield event

        logger.info(f"Response streamed successfully")
