# Root-Cause Analysis Spec: Agent Hallucination & State Corruption

**Date**: 2026-02-12
**Feature**: 017-migrate-official-sdks
**Document Type**: Root-Cause Analysis
**Status**: Critical Failure Analysis

## Observed Failures

### Failure 1: State Hallucination
**Input**: "hello, how are you?"
**Expected**: Greeting response, no task mention
**Actual**: "You have 7 tasks..." (wrong count, unsolicited)
**Database Reality**: 12 tasks exist

### Failure 2: False Execution Claims
**Input**: (Implied from context - user asked to delete tasks)
**Expected**: Tool calls to delete_task, database updated, verification
**Actual**: Agent claimed deletion occurred
**Database Reality**: No tasks were deleted

### Failure 3: Conversation Corruption
**Input**: "what is your name?"
**Expected**: New message appended with agent's name
**Actual**: Previous message was overwritten/mutated
**UI Reality**: Message history corrupted

## Root-Cause Analysis

### Failure 1 Analysis: State Hallucination

**Symptom**: Agent mentions tasks without being asked, with wrong count

**Hypothesis Chain**:

1. **Agent did NOT call list_tasks tool**
   - If it had called list_tasks, it would return 12 tasks, not 7
   - The number "7" is likely from training data or random generation
   - This proves the agent is in pure text-generation mode

2. **Why didn't the agent call tools?**
   - **Option A**: Tools not discovered by agent
   - **Option B**: Tools discovered but not passed to LLM
   - **Option C**: LLM doesn't support function calling
   - **Option D**: LLM supports tools but prompt doesn't trigger them

3. **Why did greeting trigger task output?**
   - Agent has conversation history loaded
   - History may contain previous task-related messages
   - Without tool access, agent "continues" the conversation pattern
   - LLM generates plausible-sounding task data from context

**Root Cause**: Agent is operating in **pure text-generation mode** without access to tools. The LLM is either:
- Not receiving tool schemas in the API request, OR
- Receiving them but the model doesn't support function calling

**Evidence Needed**:
- Backend logs: Does "MCP tools available to agent: [...]" appear?
- API request logs: Are tools in the Cerebras API request payload?
- Model documentation: Does llama-3.3-70b support function calling?

### Failure 2 Analysis: False Execution Claims

**Symptom**: Agent claims to have deleted tasks, but database unchanged

**Hypothesis Chain**:

1. **Agent did NOT call delete_task tool**
   - If it had, database would show 0 tasks
   - Agent generated text claiming deletion without executing it

2. **Why did agent claim success?**
   - User request: "delete all my tasks"
   - Agent understands the intent
   - Without tool access, agent generates plausible completion text
   - LLM training includes examples of successful task operations
   - Agent hallucinates the outcome

3. **Why wasn't verification performed?**
   - System prompt mandates verification (call list_tasks after mutations)
   - Agent ignored this instruction
   - This proves agent is not following system prompt for tool use

**Root Cause**: Same as Failure 1 - agent has no tool access. Additionally, the system prompt's verification mandate is ineffective because the agent can't call tools even if it wanted to.

**Critical Trust Violation**: This is the most dangerous failure mode. Users will believe tasks were deleted when they weren't, leading to data inconsistency and loss of trust.

### Failure 3 Analysis: Conversation Corruption

**Symptom**: New response overwrites previous message instead of appending

**Hypothesis Chain**:

1. **Message ID collision or reuse**
   - Frontend expects each message to have unique ID
   - If two messages share the same ID, UI overwrites instead of appending
   - This suggests message ID generation is broken

2. **Streaming state corruption**
   - ChatKit streaming sends events: message.created, message.delta, message.completed
   - If message.created uses same ID as previous message, UI updates existing message
   - This suggests the agent or streaming layer is reusing message IDs

3. **Thread/Conversation state confusion**
   - Store adapter maps thread IDs to conversation IDs
   - If mapping is wrong, messages might be saved to wrong conversation
   - Or message IDs might be generated incorrectly

4. **ChatKit event handling bug**
   - stream_agent_response() yields ThreadStreamEvent objects
   - If events have wrong message IDs, frontend will mishandle them
   - This could be in ChatKit SDK or our usage of it

**Root Cause Investigation Needed**:

**Check 1**: Message ID generation in store_adapter.py
```python
def generate_item_id(self, item_type, thread, context) -> str:
    return f"{item_type}_{uuid.uuid4().hex[:12]}"
```
- This generates unique IDs like "message_abc123"
- BUT: Are these IDs being used consistently?
- Are they being saved to database correctly?

**Check 2**: Message persistence in add_thread_item()
```python
async def add_thread_item(self, thread_id: str, item, context: RequestContext) -> None:
    message = Message(
        conversation_id=conversation_id,
        user_id=context.user_id,
        role=role,
        content=json.dumps(serialize_thread_item(item)),
        created_at=datetime.utcnow(),
    )
    session.add(message)
    session.commit()
```
- Message gets database-generated ID (auto-increment)
- But item.id (from ChatKit) might not match database ID
- This mismatch could cause confusion

**Check 3**: Message retrieval in load_thread_items()
```python
items = [deserialize_thread_item(msg) for msg in data]
```
- deserialize_thread_item() creates ThreadItem with id=str(message.id)
- This should be unique database ID
- But if deserialization is wrong, IDs could collide

**Check 4**: ChatKit streaming in stream_agent_response()
- This is a ChatKit SDK function
- We don't control its internals
- It might be generating message IDs incorrectly
- Or our AgentContext might be providing wrong thread/message info

**Most Likely Root Cause**: The issue is in how ChatKit's `stream_agent_response()` generates message IDs for streaming events. Possible scenarios:

1. **Scenario A**: stream_agent_response() reuses the same message ID for all responses in a session
2. **Scenario B**: AgentContext provides wrong thread metadata, causing ID collision
3. **Scenario C**: The agent's response doesn't include proper message boundaries, causing UI to update instead of append

**Evidence Needed**:
- Frontend console logs: What message IDs are in the SSE events?
- Backend logs: What IDs are generated by generate_item_id()?
- Database: Are messages being saved with unique IDs?
- ChatKit SDK source: How does stream_agent_response() generate message IDs?

## Unified Root-Cause Hypothesis

All three failures stem from **two fundamental issues**:

### Issue 1: Agent Has No Tool Access (Failures 1 & 2)

**Evidence**:
- Agent generates task data without calling list_tasks
- Agent claims actions without calling tools
- Task counts are wrong (hallucinated)
- No tool call logs in backend

**Possible Causes**:
1. **MCP tools not passed to LLM**: Agent SDK doesn't automatically include MCP tools in API request
2. **Model doesn't support function calling**: Cerebras llama-3.3-70b may not support OpenAI-style function calling
3. **Tool schema format mismatch**: Cerebras expects different format than OpenAI

**Critical Test**: Run diagnostic script (test_agent_tools.py) to verify tool discovery

### Issue 2: Message ID Management Broken (Failure 3)

**Evidence**:
- New messages overwrite previous ones
- UI shows mutation instead of append
- Conversation history corrupted

**Possible Causes**:
1. **ChatKit streaming generates non-unique IDs**: stream_agent_response() reuses IDs
2. **AgentContext provides wrong metadata**: Thread/message info is incorrect
3. **Store adapter ID mapping broken**: Mismatch between ChatKit IDs and database IDs
4. **Frontend state management bug**: UI incorrectly handles message IDs

**Critical Test**: Add logging to capture message IDs at each layer (generation, streaming, storage, retrieval)

## Verification Steps

### Step 1: Verify Tool Discovery
```bash
cd backend
python test_agent_tools.py
```
**Expected**: Test 1 should show tools discovered
**If FAIL**: MCP server connection or tool registration is broken

### Step 2: Verify Tool Calling
**Expected**: Test 2 should show agent calls list_tasks
**If FAIL**: Tools discovered but not used → model doesn't support function calling

### Step 3: Check Backend Logs
**Look for**:
- "MCP tools available to agent: [...]"
- "Processing chat request for user: ..."
- Any tool call events

**If missing**: Tools not being passed to agent or model

### Step 4: Check Message IDs
**Add logging** to store_adapter.py:
```python
async def add_thread_item(self, thread_id: str, item, context: RequestContext) -> None:
    logger.info(f"Saving item with ID: {item.id}, type: {item.type}")
    # ... rest of method
```

**Expected**: Each message should have unique ID
**If duplicates**: ID generation is broken

### Step 5: Check Cerebras API Request
**Add logging** to chatkit_server.py before Runner.run_streamed:
```python
# Log what's being sent to the model
logger.info(f"Agent instructions length: {len(agent.instructions)}")
logger.info(f"Agent has tools: {hasattr(agent, 'tools')}")
```

**Expected**: Agent should have tools attribute or MCP servers should provide tools
**If missing**: Tools not wired to model

## Priority Ranking

**P0 - Critical (Blocks all functionality)**:
1. Tool access broken → Agent can't perform any task operations
2. Message corruption → Conversation history unusable

**P1 - High (Causes data integrity issues)**:
1. False execution claims → Users believe actions happened when they didn't

**P2 - Medium (Causes confusion)**:
1. Hallucinated state → Wrong task counts, unsolicited information

## Next Steps

Based on diagnostic results:

**If tools NOT discovered**:
→ Fix MCP server connection or tool registration

**If tools discovered but NOT called**:
→ Model doesn't support function calling
→ Switch to OpenAI GPT-4 or fix tool schema format

**If message IDs duplicated**:
→ Fix ID generation in store_adapter or ChatKit integration

**If message IDs unique but UI still corrupts**:
→ Frontend bug or ChatKit SDK issue
