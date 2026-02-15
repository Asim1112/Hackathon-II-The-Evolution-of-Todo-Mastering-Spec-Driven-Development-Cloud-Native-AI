"""
Minimal diagnostic test to trace tool calling flow.

This will show us exactly where the flow breaks:
1. Agent initialization
2. MCP tool discovery
3. Runner execution
4. LLM request (with or without tools)
5. Tool execution (if any)
"""

import asyncio
import logging
import sys
from pathlib import Path

# IMPORTANT: Import agents SDK BEFORE adding src to path
# to avoid shadowing the agents package with src/agents/
from agents import Runner

# Now add src to path for local imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Setup logging to see everything
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


async def test_tool_calling_flow():
    """Test the complete tool calling flow."""

    logger.info("=" * 70)
    logger.info("DIAGNOSTIC TEST: Tool Calling Flow")
    logger.info("=" * 70)

    try:
        # Import after path setup
        from src.agents.chatkit_server import get_agent
        from agents import Runner

        # Step 1: Get agent
        logger.info("\n[STEP 1] Getting agent...")
        agent = await get_agent()
        logger.info(f"[STEP 1] ✓ Agent created: {agent.name}")

        # Step 2: Verify MCP servers
        logger.info(f"\n[STEP 2] Checking MCP servers...")
        if not agent.mcp_servers:
            logger.error("[STEP 2] ✗ NO MCP SERVERS REGISTERED!")
            return False

        logger.info(f"[STEP 2] ✓ MCP servers: {len(agent.mcp_servers)}")

        # Step 3: List tools
        logger.info(f"\n[STEP 3] Listing MCP tools...")
        for mcp_server in agent.mcp_servers:
            tools = await mcp_server.list_tools()
            logger.info(f"[STEP 3] MCP server '{mcp_server.name}': {len(tools)} tools")
            for tool in tools:
                logger.info(f"[STEP 3]   - {tool.name}")

        # Step 4: Create test input
        logger.info(f"\n[STEP 4] Creating test input...")
        input_items = [
            {
                "role": "system",
                "content": "The current user's ID is: 'test-user-diagnostic'. You MUST use this exact user_id when calling tools."
            },
            {
                "role": "user",
                "content": "Add a task to buy milk. Use the add_task tool."
            }
        ]
        logger.info(f"[STEP 4] ✓ Input created with {len(input_items)} messages")

        # Step 5: Run agent
        logger.info(f"\n[STEP 5] Running agent with Runner.run_streamed()...")
        logger.info("[STEP 5] Watch for [LLM REQUEST INTERCEPTED] logs...")

        result = Runner.run_streamed(agent, input_items)

        # Step 6: Process events
        logger.info(f"\n[STEP 6] Processing stream events...")
        event_count = 0
        tool_call_count = 0
        tool_result_count = 0
        text_content = ""

        async for event in result.stream_events():
            event_count += 1
            event_type = type(event).__name__

            # Log every event
            logger.info(f"[STEP 6] Event #{event_count}: {event_type}")

            # Check for tool calls
            if hasattr(event, 'type'):
                event_type_str = str(event.type) if hasattr(event.type, '__str__') else str(event.type)
                logger.info(f"[STEP 6]   Event.type: {event_type_str}")

                if 'tool' in event_type_str.lower():
                    if 'call' in event_type_str.lower():
                        tool_call_count += 1
                        logger.info(f"[STEP 6]   *** TOOL CALL DETECTED #{tool_call_count} ***")
                        if hasattr(event, 'name'):
                            logger.info(f"[STEP 6]   Tool name: {event.name}")
                    elif 'output' in event_type_str.lower() or 'result' in event_type_str.lower():
                        tool_result_count += 1
                        logger.info(f"[STEP 6]   *** TOOL RESULT DETECTED #{tool_result_count} ***")

            # Collect text content
            if hasattr(event, 'content'):
                if isinstance(event.content, str):
                    text_content += event.content
                elif isinstance(event.content, list):
                    for item in event.content:
                        if hasattr(item, 'text'):
                            text_content += item.text

        # Step 7: Summary
        logger.info(f"\n[STEP 7] Summary:")
        logger.info(f"[STEP 7] Total events: {event_count}")
        logger.info(f"[STEP 7] Tool calls: {tool_call_count}")
        logger.info(f"[STEP 7] Tool results: {tool_result_count}")
        logger.info(f"[STEP 7] Text response: {text_content[:200] if text_content else '(none)'}")

        # Step 8: Verdict
        logger.info(f"\n[STEP 8] Verdict:")
        if tool_call_count > 0:
            logger.info("[STEP 8] ✓ SUCCESS: Agent called tools!")
            return True
        else:
            logger.error("[STEP 8] ✗ FAILURE: Agent did NOT call tools!")
            logger.error("[STEP 8] Agent is operating in text-only mode.")
            logger.error("[STEP 8] Check [LLM REQUEST INTERCEPTED] logs above.")
            logger.error("[STEP 8] Look for: [SUCCESS] Tools parameter IS PRESENT")
            logger.error("[STEP 8] Or: [FAIL] Tools parameter is MISSING")
            return False

    except Exception as e:
        logger.error(f"\n[ERROR] Test failed with exception: {e}", exc_info=True)
        return False


async def main():
    """Run the diagnostic test."""
    success = await test_tool_calling_flow()

    logger.info("\n" + "=" * 70)
    if success:
        logger.info("TEST RESULT: PASS - Tool calling is working")
    else:
        logger.info("TEST RESULT: FAIL - Tool calling is broken")
    logger.info("=" * 70)

    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
