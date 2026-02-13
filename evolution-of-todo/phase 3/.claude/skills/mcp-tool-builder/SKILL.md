 name: "mcp-tool-builder"
  description: "Define, validate, and implement MCP tools following Official MCP SDK patterns. Use when creating standardized tool interfaces for AI agents to
  interact with application logic."
  version: "1.0.0"

  When to Use This Skill

  - Need to expose application functionality as MCP tools
  - Building standardized interfaces for AI agent interactions
  - Implementing tool schema validation and execution logic
  - Creating reusable tool definitions across multiple agents

  How This Skill Works

  1. Define tool schema: Specify tool name, purpose, parameters (types, required/optional), and return structure
  2. Implement validation: Create parameter validation logic with type checking and constraint enforcement
  3. Build execution handler: Implement the core tool logic that performs the actual operation
  4. Add error handling: Define error taxonomy and graceful failure modes
  5. Document examples: Provide input/output examples for each tool

  Output Format

  Provide:
  - Tool Schema: JSON schema with name, description, parameters, and return types
  - Validation Logic: Parameter validation rules and error messages
  - Execution Handler: Core implementation that performs the tool operation
  - Error Taxonomy: Categorized error types with status codes
  - Usage Examples: Sample inputs and expected outputs

  Quality Criteria

  A tool is ready when:
  - Schema is complete with all parameters typed and documented
  - Validation catches all invalid inputs before execution
  - Execution handler is stateless and idempotent where appropriate
  - Error messages are actionable and user-friendly
  - Examples cover common use cases and edge cases

  Example

  Input: "Create MCP tool for adding tasks with user_id, title, and optional description"

  Output:
  - Schema: {"name": "add_task", "parameters": {"user_id": "string (required)", "title": "string (required)", "description": "string (optional)"}, "returns":
  {"task_id": "integer", "status": "string", "title": "string"}}
  - Validation: Check user_id format, title length (1-200 chars), description length (max 1000 chars)
  - Handler: Create Task record in database, return task_id and confirmation
  - Errors: USER_NOT_FOUND, INVALID_TITLE, DATABASE_ERROR

  ---