"""
Test script to send a chat request and trigger diagnostic logging.

This will help us see if tools are being included in LLM requests.
"""

import asyncio
import httpx
import json

async def test_chat_request():
    """Send a test chat request to the backend."""

    # Backend URL
    base_url = "https://asim1112-todo-ai-chatbot.hf.space"

    # Test user and conversation
    user_id = "test-user-diagnostic"
    conversation_id = "test-conv-diagnostic"

    print("=" * 70)
    print("DIAGNOSTIC TEST: Sending chat request to backend")
    print("=" * 70)
    print(f"User ID: {user_id}")
    print(f"Conversation ID: {conversation_id}")
    print(f"Message: 'Add a task to buy milk'")
    print()

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Send chat request
            response = await client.post(
                f"{base_url}/chatkit",
                json={
                    "user_id": user_id,
                    "conversation_id": conversation_id,
                    "message": "Add a task to buy milk"
                }
            )

            print(f"Response status: {response.status_code}")
            print()

            if response.status_code == 200:
                print("Response received:")
                print(response.text[:500])
                print()
                print("SUCCESS: Request completed")
                print()
                print("Now check the backend logs for:")
                print("  [LLM REQUEST INTERCEPTED]")
                print("  [SUCCESS] Tools parameter IS PRESENT")
                print("  OR")
                print("  [FAIL] Tools parameter is MISSING")
            else:
                print(f"ERROR: Request failed with status {response.status_code}")
                print(response.text)

        except Exception as e:
            print(f"ERROR: {type(e).__name__}: {e}")
            print()
            print("Make sure:")
            print("  1. Backend server is running (port 8000)")
            print("  2. MCP server is running (port 8001)")
            print("  3. Database is accessible")

    print()
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_chat_request())
