"""
Monkey-patch to intercept and log all LLM API requests.

This will show us exactly what parameters are being sent to Cerebras,
including whether tools are included or not.
"""

import logging
from functools import wraps

logger = logging.getLogger(__name__)


def patch_openai_client(client):
    """Patch AsyncOpenAI client to log all requests."""

    original_create = client.chat.completions.create

    async def logged_create(*args, **kwargs):
        """Wrapper that logs request parameters."""
        logger.info("=" * 70)
        logger.info("[LLM REQUEST INTERCEPTED]")
        logger.info("=" * 70)

        # Log model
        model = kwargs.get('model', 'not specified')
        logger.info(f"Model: {model}")

        # Log messages
        messages = kwargs.get('messages', [])
        logger.info(f"Messages count: {len(messages)}")
        for i, msg in enumerate(messages[:3]):  # First 3 messages
            role = msg.get('role', 'unknown')
            content = str(msg.get('content', ''))[:100]
            logger.info(f"  Message {i+1}: role={role}, content={content}...")

        # Check for tools parameter - THIS IS THE CRITICAL CHECK
        if 'tools' in kwargs:
            tools = kwargs['tools']
            logger.info(f"[SUCCESS] Tools parameter IS PRESENT: {len(tools)} tools")
            for i, tool in enumerate(tools[:5]):  # First 5 tools
                tool_name = tool.get('function', {}).get('name', 'unknown')
                logger.info(f"  Tool {i+1}: {tool_name}")
        else:
            logger.error("[FAIL] Tools parameter is MISSING - This is the bug!")

        # Check for tool_choice
        if 'tool_choice' in kwargs:
            logger.info(f"Tool choice: {kwargs['tool_choice']}")
        else:
            logger.info("Tool choice: not specified")

        # Log other relevant parameters
        if 'temperature' in kwargs:
            logger.info(f"Temperature: {kwargs['temperature']}")
        if 'max_tokens' in kwargs:
            logger.info(f"Max tokens: {kwargs['max_tokens']}")

        logger.info("=" * 70)

        # Call original
        return await original_create(*args, **kwargs)

    # Replace the method
    client.chat.completions.create = logged_create
    logger.info("[PATCH] OpenAI client patched for request logging")

    return client
