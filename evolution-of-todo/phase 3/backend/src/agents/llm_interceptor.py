"""
Minimal LLM request interceptor to see if tools are being sent.

This patches the OpenAI client at a lower level to capture requests.
"""

import logging
from functools import wraps

logger = logging.getLogger(__name__)


def intercept_llm_requests(client):
    """
    Intercept OpenAI client requests to log parameters.

    This is a minimal version that just logs whether tools are present.
    """
    original_create = client.chat.completions.create

    async def logged_create(*args, **kwargs):
        """Log request parameters."""
        logger.info("=" * 70)
        logger.info("[LLM REQUEST]")
        logger.info("=" * 70)

        # Check for tools
        if 'tools' in kwargs and kwargs['tools']:
            logger.info(f"[OK] Tools present: {len(kwargs['tools'])} tools")
            for i, tool in enumerate(kwargs['tools'][:3]):
                name = tool.get('function', {}).get('name', 'unknown')
                logger.info(f"  Tool {i+1}: {name}")
        else:
            logger.error("[FAIL] NO TOOLS in request!")

        # Log tool_choice
        if 'tool_choice' in kwargs:
            logger.info(f"Tool choice: {kwargs['tool_choice']}")

        logger.info("=" * 70)

        # Call original
        response = await original_create(*args, **kwargs)

        # Log response
        logger.info("=" * 70)
        logger.info("[LLM RESPONSE]")
        logger.info("=" * 70)
        if response.choices:
            message = response.choices[0].message
            if hasattr(message, 'tool_calls') and message.tool_calls:
                logger.info(f"[OK] Tool calls returned: {len(message.tool_calls)}")
                for tc in message.tool_calls:
                    logger.info(f"  - {tc.function.name}")
            else:
                logger.error("[FAIL] NO TOOL CALLS in response!")
                if hasattr(message, 'content') and message.content:
                    logger.info(f"Text response: {message.content[:200]}")
        logger.info("=" * 70)

        return response

    client.chat.completions.create = logged_create
    return client
