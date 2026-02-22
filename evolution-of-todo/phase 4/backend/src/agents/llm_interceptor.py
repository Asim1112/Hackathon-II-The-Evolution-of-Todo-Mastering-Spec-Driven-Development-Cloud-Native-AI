"""
LLM request/response interceptor for debugging tool calling.

Patches the OpenAI client to capture both request parameters and
streaming response tool calls from Cerebras/OpenAI backends.
"""

import logging

logger = logging.getLogger(__name__)


class StreamingToolCallTracker:
    """Wraps an async stream to log tool calls as they arrive from Cerebras."""

    def __init__(self, stream):
        self._stream = stream
        self._tool_calls = {}  # index -> {name, arguments, id}
        self._has_content = False

    def __aiter__(self):
        return self

    async def __anext__(self):
        chunk = await self._stream.__anext__()

        # Track tool calls from streaming chunks
        if hasattr(chunk, 'choices') and chunk.choices:
            delta = chunk.choices[0].delta
            if delta:
                # Track text content
                if hasattr(delta, 'content') and delta.content:
                    if not self._has_content:
                        self._has_content = True
                        logger.info("[LLM STREAM] Text content started")

                # Track tool calls
                if hasattr(delta, 'tool_calls') and delta.tool_calls:
                    for tc in delta.tool_calls:
                        idx = tc.index
                        if idx not in self._tool_calls:
                            self._tool_calls[idx] = {"name": "", "arguments": "", "id": ""}
                            logger.info(f"[LLM STREAM] New tool call detected at index {idx}")

                        if tc.function:
                            if tc.function.name:
                                self._tool_calls[idx]["name"] = tc.function.name
                                logger.info(f"[LLM STREAM] Tool call [{idx}] name: {tc.function.name}")
                            if tc.function.arguments:
                                self._tool_calls[idx]["arguments"] += tc.function.arguments

                        if tc.id:
                            self._tool_calls[idx]["id"] = tc.id

            # Check for finish_reason
            if hasattr(chunk.choices[0], 'finish_reason') and chunk.choices[0].finish_reason:
                finish = chunk.choices[0].finish_reason
                logger.info(f"[LLM STREAM] Finish reason: {finish}")
                if self._tool_calls:
                    logger.info(f"[LLM STREAM] Tool calls completed: {len(self._tool_calls)}")
                    for idx, tc in self._tool_calls.items():
                        logger.info(f"  [{idx}] {tc['name']}(id={tc['id']}) args={tc['arguments'][:200]}")
                elif self._has_content:
                    logger.info("[LLM STREAM] Response was text-only (no tool calls)")

        return chunk

    # Forward all other async stream methods
    async def aclose(self):
        if hasattr(self._stream, 'aclose'):
            await self._stream.aclose()

    async def __aenter__(self):
        if hasattr(self._stream, '__aenter__'):
            await self._stream.__aenter__()
        return self

    async def __aexit__(self, *args):
        if hasattr(self._stream, '__aexit__'):
            await self._stream.__aexit__(*args)

    @property
    def response(self):
        """Forward the response property for OpenAI stream compatibility."""
        return self._stream.response if hasattr(self._stream, 'response') else None


def intercept_llm_requests(client):
    """
    Intercept OpenAI client requests to log parameters and streaming tool calls.

    Patches client.chat.completions.create to:
    1. Log outgoing request tools and messages
    2. For streaming: wrap the stream to track tool calls as they arrive
    3. For non-streaming: log the response tool calls directly
    """
    original_create = client.chat.completions.create

    async def logged_create(*args, **kwargs):
        """Log request parameters and wrap streaming responses."""
        is_streaming = kwargs.get('stream', False)

        logger.info("=" * 70)
        logger.info(f"[LLM REQUEST] stream={is_streaming}")
        logger.info("=" * 70)

        # Log tools
        if 'tools' in kwargs and kwargs['tools']:
            tool_names = [t.get('function', {}).get('name', '?') for t in kwargs['tools']]
            logger.info(f"[OK] Tools: {tool_names}")
        else:
            logger.warning("[WARN] NO TOOLS in request!")

        # Log message count and last message role
        if 'messages' in kwargs and kwargs['messages']:
            msgs = kwargs['messages']
            logger.info(f"Messages: {len(msgs)} total")
            if msgs:
                last = msgs[-1]
                role = last.get('role', '?')
                content = str(last.get('content', ''))[:100]
                logger.info(f"  Last msg: role={role}, content={content}...")

        # Log tool_choice
        if 'tool_choice' in kwargs:
            logger.info(f"Tool choice: {kwargs['tool_choice']}")

        logger.info("=" * 70)

        # Call original
        response = await original_create(*args, **kwargs)

        if not is_streaming:
            # Non-streaming: log response directly
            logger.info("=" * 70)
            logger.info("[LLM RESPONSE - non-streaming]")
            if hasattr(response, 'choices') and response.choices:
                message = response.choices[0].message
                if hasattr(message, 'tool_calls') and message.tool_calls:
                    logger.info(f"[OK] Tool calls: {len(message.tool_calls)}")
                    for tc in message.tool_calls:
                        logger.info(f"  - {tc.function.name}({tc.function.arguments[:100]})")
                else:
                    content = message.content[:100] if message.content else "(empty)"
                    logger.info(f"[INFO] Text response: {content}")
            logger.info("=" * 70)
        else:
            # Streaming: wrap to track tool calls
            logger.info("[LLM RESPONSE - streaming, tracking tool calls...]")
            response = StreamingToolCallTracker(response)

        return response

    client.chat.completions.create = logged_create
    return client
