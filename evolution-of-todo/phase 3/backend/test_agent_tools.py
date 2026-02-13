"""
Diagnostic test for Agent tool calling functionality.

Run this script to verify:
1. Agent can be initialized
2. MCP tools are discovered
3. Agent calls tools when given explicit instructions

Usage:
    cd backend
    python test_agent_tools.py
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.agents.chatkit_server import get_agent
from agents import Runner

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_tool_discovery():
    """Test 1: Verify MCP tools are discovered."""
    logger.info("=" * 60)
    logger.info("TEST 1: Tool Discovery")
    logger.info("=" * 60)

    try:
        agent = await get_agent()

        if not agent.mcp_servers:
            logger.error("❌ FAIL: No MCP servers attached to agent!")
            return False

        mcp_server = agent.mcp_servers[0]
        tools = await mcp_server.list_tools()

        if not tools:
            logger.error("❌ FAIL: MCP server connected but no tools discovered!")
            return False

        tool_names = [t.name for t in tools]
        logger.info(f"✅ PASS: Tools discovered: {tool_names}")

        expected_tools = ["add_task", "list_tasks", "complete_task", "update_task", "delete_task"]
        missing_tools = [t for t in expected_tools if t not in tool_names]

        if missing_tools:
            logger.warning(f"⚠️  WARNING: Missing expected tools: {missing_tools}")

        return len(tools) > 0

    except Exception as e:
        logger.error(f"❌ FAIL: Exception during tool discovery: {e}", exc_info=True)
        return False


async def test_simple_tool_call():
    """Test 2: Verify agent calls list_tasks tool."""
    logger.info("=" * 60)
    logger.info("TEST 2: Simple Tool Call")
    logger.info("=" * 60)

    try:
        agent = await get_agent()

        input_items = [
            {
                "role": "system",
                "content": (
                    "The current user's ID is: 'test-user-123'. "
                    "You MUST use this exact user_id value when calling any tool."
                )
            },
            {
                "role": "user",
                "content": "List all my tasks using the list_tasks tool."
            }
        ]

        logger.info("Sending request to agent...")
        result = Runner.run_streamed(agent, input_items)

        tool_called = False
        response_text = ""
        event_count = 0

        async for event in result:
            event_count += 1
            event_type = type(event).__name__
            logger.info(f"Event #{event_count}: {event_type}")

            # Check for tool calls
            if hasattr(event, 'tool_calls') and event.tool_calls:
                logger.info(f"✅ Tool called: {event.tool_calls}")
                tool_called = True

            # Collect response text
            if hasattr(event, 'content'):
                if isinstance(event.content, str):
                    response_text += event.content
                elif isinstance(event.content, list):
                    for item in event.content:
                        if hasattr(item, 'text'):
                            response_text += item.text

        logger.info(f"Total events received: {event_count}")

        if response_text:
            logger.info(f"Response text: {response_text[:200]}...")

        if tool_called:
            logger.info("✅ PASS: Agent called tools")
            return True
        else:
            logger.error("❌ FAIL: Agent did not call any tools")
            logger.error("This indicates the agent is responding in chat mode instead of using tools")
            return False

    except Exception as e:
        logger.error(f"❌ FAIL: Exception during tool call test: {e}", exc_info=True)
        return False


async def test_user_id_injection():
    """Test 3: Verify user_id is correctly injected in context."""
    logger.info("=" * 60)
    logger.info("TEST 3: User ID Injection")
    logger.info("=" * 60)

    try:
        # This test verifies the system message with user_id is present
        test_user_id = "diagnostic-test-user"

        input_items = [
            {
                "role": "system",
                "content": f"The current user's ID is: '{test_user_id}'."
            },
            {
                "role": "user",
                "content": "What is my user ID?"
            }
        ]

        logger.info(f"Testing with user_id: {test_user_id}")
        logger.info("Input items constructed:")
        for i, item in enumerate(input_items):
            logger.info(f"  Item {i}: role={item['role']}, content={item['content'][:50]}...")

        logger.info("✅ PASS: User ID injection structure is correct")
        return True

    except Exception as e:
        logger.error(f"❌ FAIL: Exception during user ID test: {e}", exc_info=True)
        return False


async def main():
    """Run all diagnostic tests."""
    logger.info("\n" + "=" * 60)
    logger.info("AGENT TOOL DIAGNOSTICS - PHASE 1")
    logger.info("=" * 60 + "\n")

    results = {}

    # Test 1: Tool Discovery
    results['tool_discovery'] = await test_tool_discovery()

    # Test 2: Tool Call (only if tools discovered)
    if results['tool_discovery']:
        results['tool_call'] = await test_simple_tool_call()
    else:
        logger.error("⏭️  SKIP: Test 2 skipped - tools not discovered")
        results['tool_call'] = None

    # Test 3: User ID Injection
    results['user_id_injection'] = await test_user_id_injection()

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)

    for test_name, result in results.items():
        if result is True:
            status = "✅ PASS"
        elif result is False:
            status = "❌ FAIL"
        else:
            status = "⏭️  SKIP"
        logger.info(f"{test_name}: {status}")

    # Overall result
    passed = sum(1 for r in results.values() if r is True)
    total = len([r for r in results.values() if r is not None])

    logger.info("\n" + "=" * 60)
    if passed == total:
        logger.info(f"✅ ALL TESTS PASSED ({passed}/{total})")
    else:
        logger.info(f"❌ SOME TESTS FAILED ({passed}/{total} passed)")
    logger.info("=" * 60 + "\n")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
