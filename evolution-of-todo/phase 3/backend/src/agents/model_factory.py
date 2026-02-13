"""
Model factory for creating LLM models with function calling support.

Simplified version - uses Cerebras by default, OpenAI if explicitly configured.
"""

import logging
from openai import AsyncOpenAI
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel
from src.config.settings import settings
from src.agents.llm_interceptor import intercept_llm_requests

logger = logging.getLogger(__name__)


async def create_model_with_function_calling() -> OpenAIChatCompletionsModel:
    """
    Create an LLM model with function calling support.

    Strategy:
    1. If use_openai_for_tools is True, use OpenAI directly
    2. Otherwise, use Cerebras (we confirmed it supports function calling)

    Returns:
        OpenAIChatCompletionsModel configured for function calling
    """

    # Option 1: Force OpenAI (user explicitly set use_openai_for_tools=True)
    if settings.use_openai_for_tools:
        if not settings.openai_api_key:
            raise RuntimeError(
                "use_openai_for_tools is True but OPENAI_API_KEY is not set. "
                "Please set OPENAI_API_KEY in .env file."
            )

        logger.info("[MODEL] Using OpenAI")
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        client = intercept_llm_requests(client)
        return OpenAIChatCompletionsModel(
            model=settings.openai_model,
            openai_client=client,
        )

    # Option 2: Use Cerebras (confirmed to support function calling)
    logger.info("[MODEL] Using Cerebras")
    cerebras_client = AsyncOpenAI(
        api_key=settings.cerebras_api_key,
        base_url=settings.cerebras_base_url,
    )
    cerebras_client = intercept_llm_requests(cerebras_client)
    return OpenAIChatCompletionsModel(
        model=settings.cerebras_model,
        openai_client=cerebras_client,
    )
