#!/usr/bin/env python3
"""
Direct test of Agent tool calling - bypasses ChatKit to isolate the issue.
Tests: Agent → MCP → Tools → Database
"""

import asyncio
import sys
import os

# Import agents SDK BEFORE adding src to path
from agents import Agent, Runner

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.agents.chatkit_server import get_agent
from src.database.session import Session, engine
from src.models.task import Task

async def main():
    print("="*80)
    print("DIRECT AGENT TOOL CALLING TEST")
    print("="*80)

    # Get agent
    print("\n1. Loading agent...")
    agent = await get_agent()
    print(f"   Agent: {agent.name}")

    # Create test messages
    messages = [
        {
            "role": "system",
            "content": "The current user's ID is: 'test_direct_user'. You MUST use this exact user_id value when calling any tool."
        },
        {
            "role": "user",
            "content": "Add a task to buy milk"
        }
    ]

    print(f"\n2. Running agent...")
    print(f"   User message: 'Add a task to buy milk'")

    # Run agent
    result = await Runner.run(agent, messages)

    print(f"\n3. Execution complete")
    print(f"   New items: {len(result.new_items)}")
    print(f"   Final output: {result.final_output}")

    # Check for tool calls
    print(f"\n4. Checking for tool calls...")
    tool_calls_found = False
    for i, item in enumerate(result.new_items):
        item_type = str(type(item).__name__)

        # Try to get tool name if it's a tool call
        tool_name = "unknown"
        if hasattr(item, 'tool_call') and hasattr(item.tool_call, 'name'):
            tool_name = item.tool_call.name
        elif hasattr(item, 'name'):
            tool_name = item.name

        if 'tool' in item_type.lower():
            print(f"   [OK] Item {i}: {item_type} - {tool_name} (TOOL DETECTED)")
            tool_calls_found = True
        else:
            print(f"   - Item {i}: {item_type}")

    # Check database
    print(f"\n5. Checking database...")
    with Session(engine) as db:
        tasks = db.query(Task).filter(Task.owner_id == 'test_direct_user').all()
        print(f"   Tasks found: {len(tasks)}")
        for task in tasks:
            print(f"      - {task.title}")

    # Final verdict
    print(f"\n" + "="*80)
    if tool_calls_found and len(tasks) > 0:
        print("[SUCCESS] Agent called tools AND database was updated!")
        print("="*80)
        return True
    elif tool_calls_found:
        print("[PARTIAL] Agent called tools but database not updated")
        print("="*80)
        return False
    else:
        print("[FAILURE] Agent did NOT call tools - still hallucinating")
        print("="*80)
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
