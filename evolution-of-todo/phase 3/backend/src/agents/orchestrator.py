"""
Agent orchestrator for coordinating OpenAI agent execution with MCP tools.

This module handles the core agent execution loop: running the OpenAI model,
processing tool calls, managing timeouts, and coordinating multi-turn interactions.
"""

from openai import OpenAI
from typing import Dict, Any, List
import asyncio
import json
import logging
from datetime import datetime
from src.agents.prompts import get_system_prompt
from src.config.settings import settings

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Orchestrates OpenAI agent execution with MCP tool integration.

    Responsibilities:
    - Initialize OpenAI client and agent configuration
    - Run agent with conversation messages and tools
    - Handle tool call execution and result formatting
    - Manage timeouts and error handling
    - Validate tool definitions
    """

    def __init__(self):
        """
        Initialize the agent orchestrator.

        Sets up:
        - Cerebras client (OpenAI-compatible) with API key from settings
        - Maximum timeout for agent execution (30 seconds)
        - Model selection (llama-3.3-70b via Cerebras)
        """
        self.client = OpenAI(
            api_key=settings.cerebras_api_key,
            base_url=settings.cerebras_base_url
        )
        self.max_timeout = 30  # seconds
        self.model = settings.cerebras_model

    def initialize_agent(self, tools: List[Dict]) -> Dict:
        """
        Initialize agent configuration for a new conversation turn.

        Args:
            tools: List of tool definitions in OpenAI format

        Returns:
            Dict containing:
                - model: Model identifier
                - messages: Empty list (to be populated by caller)
                - tools: Tool definitions
                - tool_choice: "auto" for automatic tool selection
                - temperature: 0.7 for balanced creativity
                - max_tokens: 1000 for response length limit
        """
        return {
            "model": self.model,
            "messages": [],
            "tools": tools,
            "tool_choice": "auto",
            "temperature": 0.7,
            "max_tokens": 1000
        }

    async def run_agent(self, messages: List[Dict], tools: List[Dict]) -> Dict:
        """
        Run the OpenAI agent with given messages and tools.

        This is the core execution method that:
        1. Prepends system prompt to messages
        2. Calls OpenAI Chat Completions API
        3. Wraps call in timeout for safety
        4. Extracts response content and tool calls
        5. Handles errors gracefully

        Args:
            messages: Conversation history (list of message dicts with role/content)
            tools: Available tool definitions

        Returns:
            Dict containing:
                - response: Text response from agent (str)
                - tool_calls: List of tool calls to execute (list of dicts)
                - finish_reason: Why the agent stopped (str)

        Raises:
            asyncio.TimeoutError: If execution exceeds max_timeout
            Exception: For other OpenAI API errors
        """
        try:
            # Prepend system prompt
            full_messages = [
                {"role": "system", "content": get_system_prompt()}
            ] + messages

            # Run agent with timeout
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self.client.chat.completions.create,
                    model=self.model,
                    messages=full_messages,
                    tools=tools if tools else None,
                    tool_choice="auto" if tools else None,
                    parallel_tool_calls=False,  # Reduce complexity for Cerebras/Llama
                    temperature=0.7,
                    max_tokens=1000
                ),
                timeout=self.max_timeout
            )

            # Extract response
            message = response.choices[0].message

            return {
                "response": message.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in (message.tool_calls or [])
                ],
                "finish_reason": response.choices[0].finish_reason
            }

        except asyncio.TimeoutError:
            return {
                "response": "I apologize, but the request took too long to process. Please try again.",
                "tool_calls": [],
                "finish_reason": "timeout"
            }
        except Exception as e:
            logger.error(f"Agent execution failed: {type(e).__name__}: {e}", exc_info=True)
            return {
                "response": f"I encountered an error while processing your request. Please try again later.",
                "tool_calls": [],
                "finish_reason": "error"
            }

    async def handle_tool_calls(
        self,
        tool_calls: List[Dict],
        tool_handlers: Dict[str, callable],
        inject_args: Dict[str, Any] = None
    ) -> List[Dict]:
        """
        Execute tool calls and format results for the agent.

        For each tool call:
        1. Look up handler function by tool name
        2. Parse arguments from JSON string
        3. Inject system-level arguments (e.g. user_id) not provided by model
        4. Execute handler (may be async or sync)
        5. Format result as tool message for OpenAI
        6. Handle errors gracefully

        Args:
            tool_calls: List of tool call dicts from agent response
            tool_handlers: Dict mapping tool names to handler functions
            inject_args: System-level arguments to inject into every tool call
                         (e.g. {"user_id": "..."} - stripped from model schemas)

        Returns:
            List of tool result messages in OpenAI format:
                - tool_call_id: ID linking result to original call
                - role: "tool"
                - name: Tool name
                - content: JSON-serialized result or error message
        """
        results = []

        for tool_call in tool_calls:
            tool_name = tool_call["function"]["name"]
            tool_call_id = tool_call["id"]

            try:
                # Get handler
                handler = tool_handlers.get(tool_name)
                if not handler:
                    results.append({
                        "tool_call_id": tool_call_id,
                        "role": "tool",
                        "name": tool_name,
                        "content": json.dumps({
                            "error": f"Tool '{tool_name}' not found"
                        })
                    })
                    continue

                # Parse arguments from model
                arguments = json.loads(tool_call["function"]["arguments"])

                # Inject system-level arguments (user_id etc.)
                if inject_args:
                    arguments.update(inject_args)

                # Execute handler (may be async or sync)
                if asyncio.iscoroutinefunction(handler):
                    result = await handler(**arguments)
                else:
                    result = handler(**arguments)

                # Format success result
                results.append({
                    "tool_call_id": tool_call_id,
                    "role": "tool",
                    "name": tool_name,
                    "content": json.dumps(result)
                })

            except json.JSONDecodeError as e:
                results.append({
                    "tool_call_id": tool_call_id,
                    "role": "tool",
                    "name": tool_name,
                    "content": json.dumps({
                        "error": "Invalid tool arguments format"
                    })
                })
            except Exception as e:
                results.append({
                    "tool_call_id": tool_call_id,
                    "role": "tool",
                    "name": tool_name,
                    "content": json.dumps({
                        "error": str(e)
                    })
                })

        return results

    def validate_tools(self, tools: List[Dict]) -> bool:
        """
        Validate that tool definitions match OpenAI's expected format.

        Each tool must have:
        - type: "function"
        - function: Dict with "name" and "description"

        Args:
            tools: List of tool definition dicts

        Returns:
            True if all tools are valid

        Raises:
            ValueError: If any tool is invalid
        """
        for tool in tools:
            if tool.get("type") != "function":
                raise ValueError(f"Tool must have type='function', got: {tool.get('type')}")

            function = tool.get("function")
            if not function:
                raise ValueError("Tool must have 'function' key")

            if not function.get("name"):
                raise ValueError("Tool function must have 'name'")

            if not function.get("description"):
                raise ValueError("Tool function must have 'description'")

        return True
