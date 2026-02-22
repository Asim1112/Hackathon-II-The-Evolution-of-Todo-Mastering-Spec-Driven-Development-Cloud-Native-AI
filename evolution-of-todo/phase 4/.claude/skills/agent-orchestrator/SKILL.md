name: "agent-orchestrator"
  description: "Coordinate AI agent execution with tool calling and response handling. Use when building agent-based systems that require tool invocation, response processing, and
  multi-turn coordination."
  version: "1.0.0"

  When to Use This Skill

  - Running AI agents with tool calling capabilities
  - Coordinating between agent reasoning and tool execution
  - Handling multi-turn agent interactions
  - Processing agent responses and tool results

  How This Skill Works

  1. Prepare agent input: Build message array with system prompt, history, and user message
  2. Invoke agent: Call OpenAI Agents SDK with available MCP tools
  3. Process tool calls: Execute requested tools and collect results
  4. Handle agent response: Extract assistant message and tool invocation details
  5. Coordinate multi-turn: If agent requests more tools, repeat cycle until completion

  Output Format

  Provide:
  - Agent Response: Assistant's natural language response to user
  - Tool Invocations: List of tools called with parameters and results
  - Execution Trace: Step-by-step log of agent reasoning and tool calls
  - Final State: Conversation state after agent execution completes
  - Error Recovery: Handling for tool failures or agent errors

  Quality Criteria

  Orchestration is ready when:
  - Agent receives properly formatted message array
  - Tool calls are executed in correct order with proper parameters
  - Tool results are fed back to agent correctly
  - Multi-turn coordination completes without infinite loops
  - Errors in tool execution are handled gracefully

  Example

  Input: "User says 'Show my pending tasks', conversation history loaded, MCP tools available"

  Output:
  - Agent Response: "You have 3 pending tasks: 1) Buy groceries, 2) Call mom, 3) Pay bills"
  - Tool Invocations: [{tool: "list_tasks", params: {user_id: "ziakhan", status: "pending"}, result: [{id: 1, title: "Buy groceries"}, ...]}]
  - Trace: "Agent identified list intent → Called list_tasks → Formatted results → Generated response"

  ---