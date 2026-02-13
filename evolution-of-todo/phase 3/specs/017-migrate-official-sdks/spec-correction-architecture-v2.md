# Correction Architecture Spec: Restore Agent Tool Execution

**Date**: 2026-02-12
**Feature**: 017-migrate-official-sdks
**Document Type**: Correction Architecture
**Status**: Awaiting Approval

## Problem Statement

The agent is operating in pure text-generation mode instead of agent mode:
- **Issue 1**: Agent does not call MCP tools, hallucinates task data
- **Issue 2**: Agent claims to perform actions without executing them
- **Issue 3**: Messages overwrite previous messages instead of appending

## What Is Broken

### Component 1: Tool Wiring (Critical)

**Current State**:
```python
_agent_instance = Agent(
    name="TodoAssistant",
    instructions=get_system_prompt(),
    model=_create_cerebras_model(),
    mcp_servers=[_mcp_server],  # ← MCP server attached here
    model_settings=ModelSettings(
        temperature=0.7,
        max_tokens=1000,
    ),
)
```

**Problem**: The `mcp_servers` parameter attaches the MCP server to the Agent, but this does NOT automatically make tools available to the LLM. The Agents SDK may require explicit tool extraction and passing.

**Evidence Needed**: Check if `Runner.run_streamed()` automatically includes MCP tools in the LLM API request, or if we need to explicitly pass them.

### Component 2: Model Function Calling Support (Critical)

**Current State**:
```python
def _create_cerebras_model() -> OpenAIChatCompletionsModel:
    client = AsyncOpenAI(
        api_key=settings.cerebras_api_key,
        base_url=settings.cerebras_base_url,
    )
    return OpenAIChatCompletionsModel(
        model=settings.cerebras_model,  # llama-3.3-70b
        openai_client=client,
    )
```

**Problem**: Cerebras llama-3.3-70b may not support OpenAI-style function calling. The model might:
- Not support `tools` parameter in API requests
- Not generate function call responses
- Only support text generation

**Evidence Needed**: Check Cerebras API documentation for function calling support.

### Component 3: System Prompt (Medium Priority)

**Current State**: System prompt mentions tools but doesn't strongly mandate their use at the beginning.

**Problem**: Even if tools are available, the LLM might prefer text generation over tool calling if the prompt doesn't emphasize tool use strongly enough.

### Component 4: Message ID Generation (Critical)

**Current State**:
```python
def generate_item_id(self, item_type, thread, context) -> str:
    return f"{item_type}_{uuid.uuid4().hex[:12]}"
```

**Problem**: This generates unique IDs, but:
- ChatKit's `stream_agent_response()` might not use these IDs
- The streaming layer might generate its own IDs
- ID mismatch between generation, streaming, and storage

**Evidence Needed**: Log message IDs at each layer to find where duplication occurs.

### Component 5: ChatKit Streaming Integration (High Priority)

**Current State**:
```python
async for event in stream_agent_response(agent_context, result):
    yield event
```

**Problem**: `stream_agent_response()` is a ChatKit SDK function. We don't control:
- How it generates message IDs
- How it creates ThreadStreamEvent objects
- Whether it reuses IDs across responses

**Evidence Needed**: Check ChatKit SDK source code or documentation for message ID behavior.

## Correction Architecture

### Fix 1: Explicit Tool Extraction and Passing

**Hypothesis**: The Agents SDK doesn't automatically pass MCP tools to the LLM. We need to explicitly extract and pass them.

**Architecture Change**:

```python
async def respond(self, thread, input_user_message, context):
    agent = await get_agent()

    # Load history
    items_page = await self.store.load_thread_items(...)
    input_items = await simple_to_agent_input(items_page.data)

    # Inject user context
    user_context_message = {...}
    input_items = [user_context_message] + list(input_items)

    # CRITICAL FIX: Explicitly extract tools from MCP server
    tools = None
    if agent.mcp_servers:
        mcp_server = agent.mcp_servers[0]
        mcp_tools = await mcp_server.list_tools()

        # Convert MCP tools to OpenAI function format
        tools = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema,
                }
            }
            for tool in mcp_tools
        ]
        logger.info(f"Passing {len(tools)} tools to Runner")

    # Create agent context
    agent_context = AgentContext(...)

    # Run agent with explicit tools
    result = Runner.run_streamed(
        agent,
        input_items,
        context=agent_context,
        tools=tools,  # ← Explicitly pass tools
    )

    async for event in stream_agent_response(agent_context, result):
        yield event
```

**Rationale**: If the Agents SDK doesn't automatically include MCP tools in the LLM request, we need to extract them and pass them explicitly.

**Verification**: Check `Runner.run_streamed()` signature to see if it accepts a `tools` parameter.

### Fix 2: Switch to OpenAI Model (If Cerebras Doesn't Support Tools)

**Hypothesis**: Cerebras llama-3.3-70b doesn't support function calling.

**Architecture Change**:

```python
def _create_model() -> OpenAIChatCompletionsModel:
    """Create model with guaranteed function calling support."""

    # Check if we should use OpenAI for tool calling
    if settings.use_openai_for_tools or not settings.cerebras_api_key:
        logger.info("Using OpenAI GPT-4 for tool calling support")
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        return OpenAIChatCompletionsModel(
            model="gpt-4-turbo-preview",
            openai_client=client,
        )
    else:
        logger.info("Using Cerebras llama-3.3-70b")
        client = AsyncOpenAI(
            api_key=settings.cerebras_api_key,
            base_url=settings.cerebras_base_url,
        )
        return OpenAIChatCompletionsModel(
            model=settings.cerebras_model,
            openai_client=client,
        )
```

**Configuration**:
```python
# In settings.py
class Settings(BaseSettings):
    # ... existing fields ...

    # OpenAI API (for tool calling)
    openai_api_key: str = ""
    use_openai_for_tools: bool = True  # Default to OpenAI for reliability
```

**Rationale**: OpenAI GPT-4 has proven, reliable function calling support. If Cerebras doesn't support it, we need a fallback.

**Trade-off**: OpenAI is more expensive than Cerebras, but tool calling is critical for agent functionality.

### Fix 3: Enhanced System Prompt with Tool Mandate

**Architecture Change**: Move tool-use mandate to the very beginning of the system prompt.

```python
TODO_ASSISTANT_PROMPT = """You are a helpful AI assistant for managing todo tasks.

**CRITICAL: You MUST use tools for ALL task operations.**

You have 5 tools available:
1. list_tasks(user_id, status) - View tasks
2. add_task(user_id, title, description) - Create tasks
3. complete_task(user_id, task_id) - Mark tasks done
4. update_task(user_id, task_id, title, description) - Modify tasks
5. delete_task(user_id, task_id) - Remove tasks

**MANDATORY RULES:**
- NEVER mention tasks without calling list_tasks first
- NEVER claim to perform actions without calling the appropriate tool
- NEVER make up task data - always query the database
- ALWAYS verify mutations by calling list_tasks after changes

**Examples:**
User: "show me my tasks" → Call list_tasks(user_id, status="all")
User: "delete all tasks" → Call list_tasks, then delete_task for each, then list_tasks to verify
User: "hello" → Respond normally (no tools needed for greetings)

If you respond about tasks without calling tools, you are FAILING.

[... rest of existing prompt ...]
```

**Rationale**: Make tool-use instructions impossible to miss. The LLM sees this before any other instructions.

### Fix 4: Message ID Tracking and Logging

**Architecture Change**: Add comprehensive logging at each layer to track message ID flow.

```python
# In store_adapter.py
async def add_thread_item(self, thread_id: str, item, context: RequestContext) -> None:
    logger.info(f"[STORE] Saving item: id={item.id}, type={item.type}, thread={thread_id}")

    # ... existing code ...

    session.add(message)
    session.commit()
    session.refresh(message)

    logger.info(f"[STORE] Saved to database: message.id={message.id}, item.id={item.id}")

async def load_thread_items(self, thread_id, after, limit, order, context):
    # ... existing code ...

    items = [deserialize_thread_item(msg) for msg in data]

    logger.info(f"[STORE] Loaded {len(items)} items from thread {thread_id}")
    for item in items:
        logger.info(f"[STORE]   - id={item.id}, type={item.type}")

    return Page(data=items, has_more=has_more, after=after)
```

```python
# In chatkit_server.py
async def respond(self, thread, input_user_message, context):
    logger.info(f"[RESPOND] Starting response for thread={thread.id}, user={context.user_id}")

    if input_user_message:
        logger.info(f"[RESPOND] Input message: id={input_user_message.id}")

    # ... existing code ...

    async for event in stream_agent_response(agent_context, result):
        if hasattr(event, 'id'):
            logger.info(f"[STREAM] Event: type={type(event).__name__}, id={event.id}")
        yield event
```

**Rationale**: Comprehensive logging will reveal where message IDs are duplicated or corrupted.

### Fix 5: Investigate ChatKit Streaming Behavior

**Architecture Change**: Add wrapper around `stream_agent_response()` to control message ID generation.

```python
async def respond(self, thread, input_user_message, context):
    # ... existing code ...

    # Wrap streaming to track and potentially fix message IDs
    seen_message_ids = set()

    async for event in stream_agent_response(agent_context, result):
        # Log event details
        event_type = type(event).__name__
        event_id = getattr(event, 'id', None)

        logger.info(f"[STREAM] Event: {event_type}, id={event_id}")

        # Check for ID collision
        if event_id and event_id in seen_message_ids:
            logger.error(f"[STREAM] DUPLICATE MESSAGE ID DETECTED: {event_id}")
            # Potentially generate new ID here

        if event_id:
            seen_message_ids.add(event_id)

        yield event
```

**Rationale**: If ChatKit is generating duplicate IDs, we can detect and potentially fix them before yielding to the frontend.

## Implementation Strategy

### Phase 1: Diagnostic Verification (Already Done)
- ✅ CR-001: Tool discovery logging
- ✅ CR-002: Request context logging
- ✅ CR-004: Diagnostic test script

### Phase 2: Tool Access Fix (Critical Path)

**Step 1**: Run diagnostic test script
```bash
cd backend
python test_agent_tools.py
```

**Step 2**: Based on results:
- **If tools NOT discovered**: Fix MCP connection (unlikely, we fixed this)
- **If tools discovered but NOT called**: Proceed to Step 3

**Step 3**: Check if Runner.run_streamed accepts tools parameter
- Read Agents SDK source code
- Check Runner.run_streamed signature
- Verify if tools need to be passed explicitly

**Step 4**: Implement Fix 1 or Fix 2
- **If Runner needs explicit tools**: Implement Fix 1 (extract and pass tools)
- **If Cerebras doesn't support tools**: Implement Fix 2 (switch to OpenAI)

**Step 5**: Implement Fix 3 (enhanced prompt)
- Always do this regardless of other fixes
- Makes tool-use mandate more prominent

### Phase 3: Message ID Fix (Parallel Track)

**Step 1**: Implement Fix 4 (message ID logging)
- Add logging at all layers
- Run chat session
- Analyze logs for ID duplication

**Step 2**: Based on logs:
- **If IDs unique in backend but duplicated in frontend**: Frontend bug
- **If IDs duplicated in streaming**: Implement Fix 5 (wrapper)
- **If IDs duplicated in storage**: Fix store_adapter

### Phase 4: Validation

**Test 1**: Greeting test
```
User: "hello, how are you?"
Expected: Friendly greeting, NO task mention, NO tool calls
```

**Test 2**: Task query test
```
User: "show me my tasks"
Expected: Calls list_tasks, returns accurate count (12), lists actual tasks
```

**Test 3**: Task deletion test
```
User: "delete all my tasks"
Expected: Calls list_tasks, calls delete_task for each, calls list_tasks to verify, database shows 0 tasks
```

**Test 4**: Follow-up test
```
User: "what is your name?"
Expected: New message appended, previous message unchanged
```

## Success Criteria

After implementing corrections:
1. ✅ Agent calls list_tasks when asked about tasks
2. ✅ Agent never mentions tasks without calling list_tasks
3. ✅ Task counts match database exactly
4. ✅ Agent calls tools for all task operations
5. ✅ Database changes match agent claims
6. ✅ Each message has unique ID
7. ✅ New messages append, never overwrite
8. ✅ Greetings don't trigger tool calls
9. ✅ No hallucinated state or false execution claims

## Rollback Plan

If fixes cause regressions:
1. Keep diagnostic logging (Fix 4) - useful for debugging
2. Revert model changes (Fix 2) if OpenAI causes issues
3. Revert prompt changes (Fix 3) if they cause confusion
4. Revert tool extraction (Fix 1) if it breaks existing functionality
5. Document findings for alternative approach
