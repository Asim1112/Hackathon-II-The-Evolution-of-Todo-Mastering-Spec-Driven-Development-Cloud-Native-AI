 name: "intent-router"
  description: "Analyze natural language input and route to appropriate MCP tools or actions. Use when building conversational interfaces that map user utterances to structured
  tool invocations."
  version: "1.0.0"

  When to Use This Skill

  - Need to interpret user intent from natural language
  - Mapping conversational input to structured tool calls
  - Building routing logic for multi-tool agent systems
  - Implementing command disambiguation and clarification

  How This Skill Works

  1. Parse user input: Extract key entities (action verbs, task identifiers, status filters)
  2. Identify intent: Classify into intent categories (create, list, update, complete, delete)
  3. Extract parameters: Pull out tool parameters from natural language (task_id, title, status)
  4. Map to tool: Select appropriate MCP tool based on intent
  5. Handle ambiguity: Request clarification when intent is unclear or parameters missing

  Output Format

  Provide:
  - Intent Classification: Primary intent (add_task, list_tasks, etc.) with confidence score
  - Extracted Parameters: Key-value pairs for tool invocation
  - Tool Selection: Recommended MCP tool to invoke
  - Clarification Needed: List of missing or ambiguous parameters
  - Fallback Strategy: What to do if intent cannot be determined

  Quality Criteria

  Routing is ready when:
  - Common phrasings map correctly to intents (95%+ accuracy on test set)
  - Parameter extraction handles variations (synonyms, different word orders)
  - Ambiguous inputs trigger appropriate clarification questions
  - Multi-step intents are decomposed correctly (e.g., "find and delete task X")
  - Graceful fallback for out-of-scope requests

  Example

  Input: "Mark the grocery shopping task as done"

  Output:
  - Intent: complete_task (confidence: 0.95)
  - Parameters: {task_identifier: "grocery shopping", action: "mark_complete"}
  - Tool: complete_task
  - Clarification: "Multiple tasks match 'grocery shopping'. Did you mean task #3 or #7?"

  ---