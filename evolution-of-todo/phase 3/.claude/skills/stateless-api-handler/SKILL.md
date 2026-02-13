 name: "stateless-api-handler"
  description: "Implement stateless request/response patterns for horizontally scalable APIs. Use when building REST endpoints that require no server-side session state."
  version: "1.0.0"

  When to Use This Skill

  - Building stateless REST APIs for chat or task management
  - Implementing request validation and authentication
  - Formatting responses with consistent structure
  - Handling errors with proper HTTP status codes

  How This Skill Works

  1. Validate request: Check authentication, parse body, validate parameters
  2. Extract context: Pull user_id from JWT, conversation_id from request
  3. Execute business logic: Call appropriate services/managers
  4. Format response: Structure response with consistent schema
  5. Handle errors: Map exceptions to HTTP status codes with error details

  Output Format

  Provide:
  - Request Validation: Schema validation rules and error messages
  - Authentication Logic: JWT verification and user_id extraction
  - Response Schema: Consistent JSON structure for success and errors
  - Error Mapping: Exception types mapped to HTTP status codes
  - API Documentation: OpenAPI/Swagger spec for endpoint

  Quality Criteria

  API handler is ready when:
  - All requests are validated before processing
  - Authentication is enforced consistently
  - Responses follow consistent schema
  - Errors include actionable messages
  - No server-side session state required

  Example

  Input: "Handle POST /api/{user_id}/chat with message and optional conversation_id"

  Output:
  - Validation: Check JWT matches user_id, message is non-empty string, conversation_id is valid integer
  - Response: {conversation_id: 42, response: "Task created", tool_calls: [{tool: "add_task", ...}]}
  - Errors: 401 Unauthorized, 400 Bad Request (invalid message), 404 Conversation Not Found

  ---