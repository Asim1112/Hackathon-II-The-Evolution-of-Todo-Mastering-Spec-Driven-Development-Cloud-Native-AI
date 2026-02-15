name: "conversation-state-manager"
  description: "Manage stateless conversation flow with database-persisted history. Use when building chat systems that require horizontal scalability and conversation continuity
  across requests."
  version: "1.0.0"

  When to Use This Skill

  - Building stateless chat APIs that scale horizontally
  - Need to persist and retrieve conversation history
  - Managing conversation lifecycle (create, fetch, update)
  - Implementing conversation context for AI agents

  How This Skill Works

  1. Fetch conversation: Retrieve existing conversation by ID or create new one
  2. Load message history: Query all messages for conversation in chronological order
  3. Build context array: Format history as message array for agent consumption
  4. Store new messages: Persist user and assistant messages to database
  5. Return conversation state: Provide conversation_id and formatted history

  Output Format

  Provide:
  - Conversation Object: {conversation_id, user_id, created_at, updated_at}
  - Message History: Array of {id, role, content, created_at} ordered chronologically
  - Context Array: Formatted message array ready for agent input
  - Storage Confirmation: Success/failure status for message persistence

  Quality Criteria

  State management is ready when:
  - Conversation creation is idempotent (safe to retry)
  - Message history loads efficiently (indexed queries)
  - Context array format matches agent requirements exactly
  - Storage operations are atomic (all-or-nothing)
  - No server-side session state required

  Example

  Input: "Fetch conversation 42 for user 'ziakhan' and prepare context for new message 'Show my tasks'"

  Output:
  - Conversation: {id: 42, user_id: "ziakhan", created_at: "2026-02-10T10:00:00Z"}
  - History: [{role: "user", content: "Add task to buy milk"}, {role: "assistant", content: "Task created: Buy milk"}]
  - Context: [{role: "user", content: "Add task to buy milk"}, {role: "assistant", content: "Task created"}, {role: "user", content: "Show my tasks"}]

  ---