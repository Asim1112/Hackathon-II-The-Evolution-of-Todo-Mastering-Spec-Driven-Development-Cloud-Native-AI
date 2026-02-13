"""
Test Cerebras function calling with SDK in NON-streaming mode.

This will help us determine if the issue is with streaming.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Import agents SDK BEFORE adding src to path
from agents import Runner

# Now add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_non_streaming():
    """Test with Runner.run() instead of Runner.run_streamed()."""

    from src.agents.chatkit_server import get_agent

    logger.info("=" * 70)
    logger.info("TEST: Non-Streaming Mode")
    logger.info("=" * 70)

    # Get agent
    agent = await get_agent()
    logger.info(f"Agent: {agent.name}")

    # Create input
    input_items = [
        {"role": "system", "content": "The current user's ID is: 'test-user'. You MUST use this exact user_id when calling tools."},
        {"role": "user", "content": "Add a task to buy milk. Use the add_task tool."}
    ]

    # Run WITHOUT streaming
    logger.info("\nCalling Runner.run() (non-streaming)...")
    result = await Runner.run(agent, input_items)

    # Check result
    logger.info(f"\nResult:")
    logger.info(f"  Final output: {result.final_output}")
    logger.info(f"  New items: {len(result.new_items)}")

    # Check for tool calls in new_items
    tool_calls = [item for item in result.new_items if hasattr(item, 'type') and 'tool' in str(item.type).lower()]
    logger.info(f"  Tool calls: {len(tool_calls)}")

    if tool_calls:
        logger.info("SUCCESS: Tool calls detected!")
        for tc in tool_calls:
            logger.info(f"  - {tc}")
        return True
    else:
        logger.error("FAILURE: No tool calls detected")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_non_streaming())
    sys.exit(0 if success else 1)
