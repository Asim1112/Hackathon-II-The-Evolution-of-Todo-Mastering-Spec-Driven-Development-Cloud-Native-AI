"""
Test script to verify if Cerebras llama-3.3-70b supports OpenAI-style function calling.

This will help determine if we need to:
1. Fix how tools are passed to the SDK, OR
2. Switch to OpenAI GPT-4 as a fallback
"""

import asyncio
import os
from pathlib import Path
from openai import AsyncOpenAI

# Load environment variables from .env file
from dotenv import load_dotenv
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

async def test_cerebras_function_calling():
    """Test if Cerebras supports function calling."""

    # Get API key from environment
    api_key = os.getenv("CEREBRAS_API_KEY")
    if not api_key:
        print("[FAIL] CEREBRAS_API_KEY not set")
        return False

    # Create client
    client = AsyncOpenAI(
        api_key=api_key,
        base_url="https://api.cerebras.ai/v1",
    )

    # Define a simple test tool
    test_tools = [{
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city name"
                    }
                },
                "required": ["location"]
            }
        }
    }]

    print("[TEST] Testing Cerebras llama-3.3-70b function calling support...")
    print(f"       API Key: {api_key[:10]}...")
    print(f"       Base URL: https://api.cerebras.ai/v1")
    print()

    try:
        # Test 1: Request with tools parameter
        print("Test 1: Sending request with tools parameter...")
        response = await client.chat.completions.create(
            model="llama-3.3-70b",
            messages=[
                {"role": "user", "content": "What's the weather in San Francisco?"}
            ],
            tools=test_tools,
            tool_choice="auto",
        )

        print(f"[OK] Request succeeded")
        print(f"     Response ID: {response.id}")
        print(f"     Model: {response.model}")

        # Check if response has tool_calls
        message = response.choices[0].message

        if hasattr(message, 'tool_calls') and message.tool_calls:
            print(f"[SUCCESS] Model returned tool_calls!")
            print(f"          Tool calls: {len(message.tool_calls)}")
            for tc in message.tool_calls:
                print(f"          - {tc.function.name}({tc.function.arguments})")
            return True
        else:
            print(f"[FAIL] Model did NOT return tool_calls")
            print(f"       Content: {message.content}")
            return False

    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        return False

async def test_openai_function_calling():
    """Test OpenAI GPT-4 as a comparison."""

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("[SKIP] OPENAI_API_KEY not set, skipping OpenAI test")
        return None

    client = AsyncOpenAI(api_key=api_key)

    test_tools = [{
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "The city name"}
                },
                "required": ["location"]
            }
        }
    }]

    print("\n[TEST] Testing OpenAI GPT-4 function calling (for comparison)...")

    try:
        response = await client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "user", "content": "What's the weather in San Francisco?"}
            ],
            tools=test_tools,
            tool_choice="auto",
        )

        message = response.choices[0].message

        if hasattr(message, 'tool_calls') and message.tool_calls:
            print(f"[SUCCESS] OpenAI returned tool_calls (as expected)")
            return True
        else:
            print(f"[WARN] OpenAI did NOT return tool_calls (unexpected)")
            return False

    except Exception as e:
        print(f"[ERROR] OpenAI test error: {e}")
        return None

async def main():
    print("=" * 70)
    print("CEREBRAS FUNCTION CALLING TEST")
    print("=" * 70)
    print()

    cerebras_works = await test_cerebras_function_calling()
    openai_works = await test_openai_function_calling()

    print()
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"Cerebras function calling: {'[WORKS]' if cerebras_works else '[DOES NOT WORK]'}")
    if openai_works is not None:
        print(f"OpenAI function calling:   {'[WORKS]' if openai_works else '[DOES NOT WORK]'}")
    print()

    if not cerebras_works:
        print("RECOMMENDATION:")
        print("Cerebras llama-3.3-70b does not support OpenAI-style function calling.")
        print("You must switch to OpenAI GPT-4 for tool-calling operations.")
        print()
        print("Add to .env:")
        print("  OPENAI_API_KEY=sk-...")
        print("  USE_OPENAI_FOR_TOOLS=true")
    else:
        print("RECOMMENDATION:")
        print("Cerebras supports function calling. The issue is likely in how")
        print("tools are being passed to the Agents SDK Runner.")

if __name__ == "__main__":
    asyncio.run(main())
