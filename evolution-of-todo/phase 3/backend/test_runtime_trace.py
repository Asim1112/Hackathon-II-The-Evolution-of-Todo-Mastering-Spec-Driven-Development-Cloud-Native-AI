#!/usr/bin/env python3
"""
Test script to trace the exact runtime behavior of the agent tool calling.
This will help identify where the loop breaks in the execution path.
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agents import Agent, Runner
from chatkit.agents import simple_to_agent_input
from chatkit.types import UserMessageItem
from src.agents.chatkit_server import get_agent
from src.agents.tracer import get_tracer

async def test_agent_execution():
    """Test the complete agent execution flow with tracing."""

    print("="*80)
    print("TESTING AGENT EXECUTION FLOW WITH TRACING")
    print("="*80)

    # Create tracer
    tracer = get_tracer()

    # Create sample input following the same approach as in chatkit_server.py
    user_message = UserMessageItem(
        id="test_msg_1",
        role="user",
        content=[{"type": "text", "text": "Add a task to buy milk"}]
    )

    # Create input items list similar to how it's done in the server
    input_items = await simple_to_agent_input([user_message])

    # Inject user context (same as in server)
    user_context_message = {
        "role": "system",
        "content": (
            "The current user's ID is: 'test_user_123'. "
            "You MUST use this exact user_id value when calling any tool "
            "(list_tasks, add_task, complete_task, update_task, delete_task)."
        ),
    }
    input_list = [user_context_message] + list(input_items)

    print(f"Input items for agent: {input_list}")

    # Start trace
    trace_id = tracer.start_trace()
    print(f"\nStarted trace: {trace_id}")

    try:
        # Load agent
        print("\n1. Loading agent...")
        agent = await get_agent()
        tracer.log_step("TEST_AGENT_LOADED", agent.name, "Agent loaded in test context")

        print(f"   Agent name: {agent.name}")
        print(f"   Agent instructions length: {len(agent.instructions) if agent.instructions else 0}")
        print(f"   MCP servers: {len(agent.mcp_servers) if agent.mcp_servers else 0}")

        # List tools from MCP server
        if agent.mcp_servers:
            for mcp_server in agent.mcp_servers:
                try:
                    tools = await mcp_server.list_tools()
                    tool_names = [t.name for t in tools] if tools else []
                    print(f"   MCP tools available: {tool_names}")
                    tracer.log_step("TEST_MCP_TOOLS", tool_names, "Found MCP tools in test")
                except Exception as e:
                    print(f"   Error listing MCP tools: {e}")
                    tracer.log_error("TEST_MCP_LIST_ERROR", e, "Error listing MCP tools in test")

        # Run agent with Runner.run (our fixed approach)
        print("\n2. Running agent with Runner.run...")
        result = await Runner.run(agent, input_list)

        tracer.log_step("TEST_RUNNER_RESULT", {
            "result_type": type(result),
            "final_output": str(result.final_output) if hasattr(result, 'final_output') else None,
            "new_items_count": len(result.new_items) if hasattr(result, 'new_items') else 0
        }, "Runner.run completed")

        print(f"   Result type: {type(result)}")
        print(f"   Final output: {result.final_output if hasattr(result, 'final_output') else 'None'}")
        print(f"   New items count: {len(result.new_items) if hasattr(result, 'new_items') else 0}")

        # Analyze new items for tool calls
        print("\n3. Analyzing result items...")
        for i, item in enumerate(result.new_items):
            item_type = getattr(item, 'type', 'unknown')
            item_content = getattr(item, 'content', 'No content')
            print(f"   Item {i}: Type={item_type}, Content={item_content}")

            if 'tool' in str(item_type).lower():
                print(f"     *** FOUND TOOL ITEM: {item_type} ***")
                tracer.log_step("TEST_TOOL_FOUND", {
                    "item_index": i,
                    "item_type": item_type,
                    "item_content": str(item_content)[:200]
                }, "Tool call detected in result")

        print(f"\n✓ Test completed successfully")

    except Exception as e:
        print(f"\n✗ Error during test: {e}")
        import traceback
        traceback.print_exc()
        tracer.log_error("TEST_EXECUTION_ERROR", e, "Error in test execution")

    finally:
        tracer.end_trace()
        print(f"\nTrace completed. Total steps: {len(tracer.steps)}")

        # Print summary
        print("\n" + "="*50)
        print("TRACE SUMMARY:")
        print("="*50)
        for step in tracer.steps:
            print(f"  {step['step']}: {step['data']} | {step['details']}")


if __name__ == "__main__":
    asyncio.run(test_agent_execution())