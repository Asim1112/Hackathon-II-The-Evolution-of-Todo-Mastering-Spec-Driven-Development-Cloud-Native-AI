"""
Diagnostic script to intercept and log actual LLM API requests.

This will show us exactly what parameters are being sent to Cerebras,
including whether tools are included or not.
"""

import asyncio
import logging
import sys
from pathlib import Path
from unittest.mock import patch
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_with_request_logging():
    """Test agent and log actual API requests."""

    from src.agents.chatkit_server import get_agent
    from agents import Runner

    # Get agent
    logger.info("Initializing agent...")
    agent = await get_agent()

    # Check MCP tools
    if agent.mcp_servers:
        mcp_server = agent.mcp_servers[0]
        tools = await mcp_server.list_tools()
        logger.info(f"MCP tools available: {[t.name for t in tools]}")

    # Monkey-patch the OpenAI client to log requests
    original_create = agent.model.openai_client.chat.completions.create

    async def logged_create(*args, **kwargs):
        logger.info("=" * 70)
        logger.info("LLM API REQUEST INTERCEPTED")
        logger.info("=" * 70)
        logger.info(f"Model: {kwargs.get('model', 'not specified')}")
        logger.info(f"Messages count: {len(kwargs.get('messages', []))}")

        # Check for tools parameter
        if 'tools' in kwargs:
            tools = kwargs['tools']
            logger.info(f"[SUCCESS] Tools parameter IS present: {len(tools)} tools")
            for i, tool in enumerate(tools):
                tool_name = tool.get('function', {}).get('name', 'unknown')
                logger.info(f"  Tool {i+1}: {tool_name}")
        else:
            logger.info("[FAIL] Tools parameter is MISSING")

        # Check for tool_choice
        if 'tool_choice' in kwargs:
            logger.info(f"Tool choice: {kwargs['tool_choice']}")
        else:
            logger.info("Tool choice: not specified")

        logger.info("=" * 70)

        # Call original
        return await original_create(*args, **kwargs)

    agent.model.openai_client.chat.completions.create = logged_create

    # Test with a simple request
    input_items = [
        {
            "role": "system",
            "content": "The current user's ID is: 'test-user-123'. You MUST use this exact user_id when calling tools."
        },
        {
            "role": "user",
            "content": "List all my tasks."
        }
    ]

    logger.info("\nSending request to agent...")
    result = Runner.run_streamed(agent, input_items)

    # Consume events
    event_count = 0
    async for event in result:
        event_count += 1
        event_type = type(event).__name__
        logger.info(f"Event {event_count}: {event_type}")

        if event_count > 10:  # Limit output
            logger.info("(stopping after 10 events)")
            break

    logger.info(f"\nTotal events: {event_count}")


if __name__ == "__main__":
    asyncio.run(test_with_request_logging())
