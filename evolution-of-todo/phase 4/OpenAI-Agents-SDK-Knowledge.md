# OpenAI Agents SDK - Complete Implementation Guide

**Version**: Based on openai-agents-python v0.7.0
**Documentation Source**: https://openai.github.io/openai-agents-python
**Last Updated**: 2026-02-11
**Purpose**: Comprehensive reference for implementing OpenAI Agents SDK in Phase III Todo AI Chatbot

---

## Table of Contents

### 1. Overview & Core Concepts
- 1.1 What is OpenAI Agents SDK
- 1.2 Design Principles
- 1.3 Three Core Primitives
  - Agents
  - Handoffs
  - Guardrails
- 1.4 Key Features
- 1.5 Installation & Setup

### 2. Agent Architecture
- 2.1 Agent Class Definition
- 2.2 Agent Configuration Parameters
  - name, description, instructions
  - model, model_settings
  - tools, mcp_servers, mcp_config
  - handoffs
  - output_type
  - hooks
  - tool_use_behavior
  - reset_tool_choice
  - input_guardrails, output_guardrails
- 2.3 Agent Initialization & Validation
- 2.4 Context Typing with Generics
- 2.5 Dynamic Instructions

### 3. Runner - Agent Execution
- 3.1 Runner.run() - Async Execution
  - Parameters
  - Return Type (RunResult)
  - Execution Loop
  - Exception Handling
- 3.2 Runner.run_sync() - Synchronous Execution
- 3.3 Runner.run_streamed() - Streaming Execution
  - Stream Events
  - Event Types
- 3.4 Execution Parameters
  - starting_agent
  - input
  - context
  - max_turns
  - hooks
  - run_config
  - previous_response_id
  - conversation_id
  - session

### 4. Session Management
- 4.1 Session Architecture
- 4.2 SQLAlchemySession
  - from_url() Method
  - PostgreSQL Integration
  - create_tables
- 4.3 SQLiteSession
- 4.4 EncryptedSession
  - Encryption with Fernet
  - TTL-based Expiration
- 4.5 OpenAIConversationsSession
- 4.6 Session Methods
  - get_items()
  - add_items()
  - pop_item()
  - clear_session()
- 4.7 Automatic Conversation History

### 5. MCP Server Integration
- 5.1 MCP Integration Overview
- 5.2 MCPServerStreamableHttp
  - Configuration
  - Parameters
  - Headers & Authentication
- 5.3 MCPServerStdio
  - Subprocess-based Servers
  - Command & Args
- 5.4 MCPServerManager
  - Multi-server Management
  - Active Servers
- 5.5 HostedMCPTool
  - Remote MCP Servers
  - Tool Configuration
- 5.6 MCP Configuration Options
  - cache_tools_list
  - tool_filter
  - require_approval
  - tool_meta_resolver
  - convert_schemas_to_strict
  - failure_error_function
- 5.7 Tool Filtering
  - Static Filtering
  - Dynamic Filtering
- 5.8 Approval Policies

### 6. Function Tools
- 6.1 @function_tool Decorator
  - Automatic Schema Generation
  - Type Hints & Docstrings
- 6.2 Decorator Parameters
  - name_override
  - description_override
  - docstring_style
  - use_docstring_info
  - failure_error_function
  - strict_mode
  - is_enabled
  - tool_input_guardrails
  - tool_output_guardrails
- 6.3 Pydantic Field Constraints
- 6.4 RunContextWrapper Access
- 6.5 Return Types
  - Text
  - Images (ToolOutputImage)
  - Files (ToolOutputFileContent)
- 6.6 Manual FunctionTool Creation
- 6.7 Error Handling in Tools
- 6.8 Hosted Tools
  - WebSearchTool
  - FileSearchTool
  - CodeInterpreterTool
  - ImageGenerationTool

### 7. Handoffs & Multi-Agent Orchestration
- 7.1 Handoff Concept
- 7.2 Creating Handoffs
  - Direct Agent Passing
  - handoff() Function
- 7.3 Handoff Configuration
  - tool_name_override
  - tool_description_override
  - on_handoff Callback
  - input_type
  - input_filter
  - nest_handoff_history
  - is_enabled
- 7.4 Handoff Input Data
  - Structured Input with Pydantic
  - HandoffInputData
- 7.5 Input Filters
  - Conversation History Control
  - handoff_filters Module
- 7.6 Agents as Tools
  - as_tool() Method
  - parameters
  - include_input_schema
  - needs_approval
  - custom_output_extractor
  - on_stream
- 7.7 Recommended Prompt Patterns

### 8. Guardrails
- 8.1 Guardrail Architecture
- 8.2 InputGuardrail
  - Parallel Execution (run_in_parallel=True)
  - Blocking Execution (run_in_parallel=False)
  - @input_guardrail Decorator
- 8.3 OutputGuardrail
  - @output_guardrail Decorator
  - Final Output Validation
- 8.4 ToolInputGuardrail
- 8.5 ToolOutputGuardrail
- 8.6 GuardrailResult
  - tripwire_triggered
  - output_info
- 8.7 Tripwire Mechanism
  - GuardrailTripwireTriggered Exception
  - Execution Halting
- 8.8 Guardrail Implementation Patterns

### 9. Streaming
- 9.1 Streaming Architecture
- 9.2 Stream Event Types
  - RawResponsesStreamEvent
  - RunItemStreamEvent
  - AgentUpdatedStreamEvent
- 9.3 Token-by-Token Streaming
  - ResponseTextDeltaEvent
- 9.4 Higher-Level Event Streaming
  - message_output_created
  - tool_called
  - tool_output
  - handoff_requested
  - handoff_occured
- 9.5 Async Iteration Pattern
- 9.6 ItemHelpers Utilities

### 10. RunResult Structure
- 10.1 RunResult Attributes
  - input
  - new_items
  - raw_responses
  - final_output
  - input_guardrail_results
  - output_guardrail_results
  - tool_input_guardrail_results
  - tool_output_guardrail_results
  - context_wrapper
  - last_agent
  - last_response_id
- 10.2 RunResult Methods
  - final_output_as()
  - to_input_list()
  - release_agents()
- 10.3 RunErrorDetails
- 10.4 Error Handling

### 11. Hooks & Lifecycle Events
- 11.1 AgentHooks
- 11.2 RunHooks
- 11.3 Lifecycle Callbacks

### 12. Model Configuration
- 12.1 Model Selection
- 12.2 ModelSettings
  - temperature
  - top_p
  - max_tokens
- 12.3 Default Models
- 12.4 GPT-5 Reasoning Settings

### 13. Complete Implementation Examples
- 13.1 Basic Agent with MCP Server
- 13.2 Multi-Agent with Handoffs
- 13.3 Agent with Session Management
- 13.4 Streaming Implementation
- 13.5 Guardrails Implementation
- 13.6 Phase III Todo Chatbot Migration Pattern

### 14. Phase III Migration Guide
- 14.1 Current Architecture Analysis
- 14.2 Migration Strategy
- 14.3 Step-by-Step Migration
- 14.4 Code Comparison (Before/After)
- 14.5 Testing & Verification

### 15. Best Practices & Patterns
- 15.1 Session Management
- 15.2 Error Handling
- 15.3 Tool Design
- 15.4 Handoff Patterns
- 15.5 Performance Optimization
- 15.6 Production Considerations

### 16. API Reference Quick Lookup
- 16.1 Agent Class
- 16.2 Runner Methods
- 16.3 Session Classes
- 16.4 MCP Server Classes
- 16.5 Tool Decorators
- 16.6 Guardrail Decorators
- 16.7 Exception Types

---

## 1. Overview & Core Concepts

### 1.1 What is OpenAI Agents SDK

The OpenAI Agents SDK is a **production-ready framework** for building multi-agent workflows in Python. It is described as a "production-ready upgrade of Swarm" with enhanced features for enterprise use.

**Key Characteristics:**
- Python-first orchestration using native language features
- Built-in agent loop handling tool invocation and continuation
- Automatic schema generation from Python type hints
- Native MCP (Model Context Protocol) server integration
- Persistent memory through sessions
- Built-in tracing for visualization, debugging, and monitoring
- Support for realtime voice agents with interruption detection

### 1.2 Design Principles

1. **Few enough primitives for quick learning, enough features to be useful**
   - Minimal abstractions to reduce cognitive load
   - Powerful enough for production use cases

2. **Works great out-of-the-box with customization options**
   - Sensible defaults for immediate productivity
   - Extensive configuration for advanced scenarios

### 1.3 Three Core Primitives

**Agents:** LLMs configured with instructions, tools, and behavior settings.

**Handoffs:** Mechanism for agents to delegate work to other specialized agents.

**Guardrails:** Input/output validation and safety checks.

### 1.4 Key Features

- Built-in agent loop with automatic tool invocation
- Function tools with automatic schema generation
- MCP server integration (5 approaches)
- Session management (SQLAlchemy, SQLite, Encrypted)
- Built-in tracing and observability

### 1.5 Installation & Setup

```bash
pip install openai-agents
export OPENAI_API_KEY=sk-...
```

**Basic Usage:**
```python
from agents import Agent, Runner

agent = Agent(name="Assistant", instructions="You are helpful")
result = Runner.run_sync(agent, "Hello!")
print(result.final_output)
```

---

**Document Status**: Phase 1 content appended - Ready for Phase 2

---

## 5. MCP Server Integration - Complete Reference

### 5.1 MCPServerStreamableHttp - Production Pattern

**For Phase III Todo Chatbot - This is the recommended approach**

```python
from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp

async with MCPServerStreamableHttp(
    name="TodoMCP",
    params={
        "url": "http://localhost:8001/mcp",
        "headers": {"Authorization": f"Bearer {token}"},
        "timeout": 10
    },
    cache_tools_list=True,
    max_retry_attempts=3
) as server:
    agent = Agent(
        name="TodoAssistant",
        instructions="Use MCP tools to manage tasks",
        mcp_servers=[server]
    )

    result = await Runner.run(agent, "Add task to buy milk")
    print(result.final_output)
```

**Parameters:**
- `name`: Readable name for the server
- `params`: Dict with url, headers, timeout, terminate_on_close
- `cache_tools_list`: Cache tool list (True recommended for performance)
- `client_session_timeout_seconds`: Read timeout (default: 5)
- `tool_filter`: Filter tools (static or dynamic)
- `use_structured_content`: Use tool_result.structured_content (default: False)
- `max_retry_attempts`: Retry failed calls (default: 0)
- `retry_backoff_seconds_base`: Exponential backoff base (default: 1.0)

### 5.2 MCPServerStdio - Subprocess Pattern

```python
from agents.mcp import MCPServerStdio

async with MCPServerStdio(
    name="Filesystem Server",
    params={
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path"],
        "env": {"KEY": "value"},
        "cwd": "/working/dir"
    }
) as server:
    agent = Agent(mcp_servers=[server])
```

### 5.3 MCPServerManager - Multi-Server

```python
from agents.mcp import MCPServerManager, MCPServerStreamableHttp

servers = [
    MCPServerStreamableHttp(name="calendar", params={"url": "http://localhost:8000/mcp"}),
    MCPServerStreamableHttp(name="docs", params={"url": "http://localhost:8001/mcp"})
]

async with MCPServerManager(servers) as manager:
    agent = Agent(
        name="Assistant",
        mcp_servers=manager.active_servers
    )
```

### 5.4 Tool Filtering

**Static Filtering:**
```python
from agents.mcp import create_static_tool_filter

server = MCPServerStdio(
    params={...},
    tool_filter=create_static_tool_filter(
        allowed_tool_names=["read_file", "write_file"]
    )
)
```

**Dynamic Filtering:**
```python
async def context_aware_filter(context: ToolFilterContext, tool) -> bool:
    if context.agent.name == "ReadOnly" and tool.name.startswith("write_"):
        return False
    return True

server = MCPServerStdio(
    params={...},
    tool_filter=context_aware_filter
)
```

### 5.5 MCP Configuration in Agent

```python
agent = Agent(
    name="Assistant",
    mcp_servers=[server],
    mcp_config={
        "convert_schemas_to_strict": True,
        "failure_error_function": None  # Raise exceptions
    }
)
```

---

## 6. Function Tools - Complete Reference

### 6.1 @function_tool Decorator - Automatic Schema Generation

```python
from agents import function_tool

@function_tool
async def fetch_weather(location: str, units: str = "celsius") -> str:
    """Fetch the weather for a given location.

    Args:
        location: The location to fetch weather for
        units: Temperature units (celsius or fahrenheit)
    """
    return f"Weather in {location}: 22°{units[0].upper()}"
```

**Automatic Features:**
- Tool name from function name
- Description from docstring
- Schema from type hints
- Pydantic validation

### 6.2 Decorator Parameters

```python
@function_tool(
    name_override="custom_name",
    description_override="Custom description",
    docstring_style="google",  # or "sphinx", "numpy"
    use_docstring_info=True,
    failure_error_function=my_error_handler,
    strict_mode=True,
    is_enabled=True,  # or callable
    tool_input_guardrails=[...],
    tool_output_guardrails=[...]
)
def my_tool(param: str) -> str:
    return f"Result: {param}"
```

### 6.3 Pydantic Field Constraints

```python
from pydantic import Field
from typing import Annotated

@function_tool
def score(
    score: Annotated[int, Field(ge=0, le=100, description="Score 0-100")]
) -> str:
    return f"Score recorded: {score}"
```

### 6.4 RunContextWrapper Access

```python
from agents import function_tool, RunContextWrapper

@function_tool
def get_user_info(ctx: RunContextWrapper[MyContext]) -> str:
    user_id = ctx.context.user_id
    return f"User: {user_id}"
```

### 6.5 Custom Error Handling

```python
def my_error_handler(ctx: RunContextWrapper, error: Exception) -> str:
    print(f"Tool failed: {error}")
    return "An error occurred. Please try again."

@function_tool(failure_error_function=my_error_handler)
def risky_operation(data: str) -> str:
    if not data:
        raise ValueError("Data required")
    return process(data)
```

### 6.6 Manual FunctionTool Creation

```python
from pydantic import BaseModel
from agents import FunctionTool, RunContextWrapper

class FunctionArgs(BaseModel):
    username: str
    age: int

async def run_function(ctx: RunContextWrapper, args: str) -> str:
    parsed = FunctionArgs.model_validate_json(args)
    return f"{parsed.username} is {parsed.age} years old"

tool = FunctionTool(
    name="process_user",
    description="Processes user data",
    params_json_schema=FunctionArgs.model_json_schema(),
    on_invoke_tool=run_function
)
```

---

## 7. Handoffs - Complete Multi-Agent Reference

### 7.1 Basic Handoff Pattern

```python
from agents import Agent, handoff

billing_agent = Agent(name="Billing Agent")
refund_agent = Agent(name="Refund Agent")

triage_agent = Agent(
    name="Triage Agent",
    handoffs=[billing_agent, refund_agent]
)
```

**How it works:** Handoffs are represented as tools to the LLM. For "Refund Agent", the tool becomes `transfer_to_refund_agent`.

### 7.2 Customized Handoffs

```python
from agents import handoff
from pydantic import BaseModel

class EscalationData(BaseModel):
    reason: str

async def on_handoff(ctx: RunContextWrapper, input_data: EscalationData):
    print(f"Escalation reason: {input_data.reason}")

handoff_obj = handoff(
    agent=escalation_agent,
    on_handoff=on_handoff,
    input_type=EscalationData,
    tool_name_override="escalate_to_supervisor",
    tool_description_override="Escalate complex issues",
    is_enabled=True
)

triage_agent = Agent(
    name="Triage",
    handoffs=[handoff_obj]
)
```

### 7.3 Handoff Parameters

- `agent`: Target agent
- `tool_name_override`: Custom tool name (default: `transfer_to_<agent_name>`)
- `tool_description_override`: Custom description
- `on_handoff`: Callback when handoff is invoked
- `input_type`: Pydantic model for structured input
- `input_filter`: Filter conversation history for next agent
- `nest_handoff_history`: Control history nesting
- `is_enabled`: Boolean or callable to enable/disable

### 7.4 Input Filters

```python
from agents.extensions import handoff_filters

handoff_obj = handoff(
    agent=next_agent,
    input_filter=handoff_filters.remove_all_tools
)
```

**Purpose:** Control what conversation history the next agent sees.

### 7.5 Agents as Tools

```python
spanish_agent = Agent(name="Spanish Translator")

orchestrator = Agent(
    name="Orchestrator",
    tools=[
        spanish_agent.as_tool(
            tool_name="translate_to_spanish",
            tool_description="Translate to Spanish",
            parameters=TranslationInput,
            include_input_schema=True,
            needs_approval=False
        )
    ]
)
```

**Difference from Handoffs:** Agent runs as a tool without full handoff. Orchestrator remains in control.

---

## 8. Guardrails - Complete Safety Reference

### 8.1 InputGuardrail - Pre-Execution Checks

```python
from agents import input_guardrail, GuardrailFunctionOutput

@input_guardrail(run_in_parallel=False)  # Blocking execution
async def check_input(ctx: RunContextWrapper, agent: Agent, input: str) -> GuardrailFunctionOutput:
    if "forbidden" in input.lower():
        return GuardrailFunctionOutput(
            output_info="Forbidden content detected",
            tripwire_triggered=True
        )
    return GuardrailFunctionOutput(tripwire_triggered=False)

agent = Agent(
    name="SafeAgent",
    input_guardrails=[check_input]
)
```

**Execution Modes:**
- `run_in_parallel=True` (default): Runs concurrently with agent
- `run_in_parallel=False`: Runs before agent starts (blocks execution)

### 8.2 OutputGuardrail - Post-Execution Validation

```python
from agents import output_guardrail, GuardrailFunctionOutput
from pydantic import BaseModel

class MessageOutput(BaseModel):
    response: str

@output_guardrail
async def validate_output(
    ctx: RunContextWrapper,
    agent: Agent,
    output: MessageOutput
) -> GuardrailFunctionOutput:
    if len(output.response) > 1000:
        return GuardrailFunctionOutput(
            output_info="Response too long",
            tripwire_triggered=True
        )
    return GuardrailFunctionOutput(tripwire_triggered=False)

agent = Agent(
    name="Agent",
    output_type=MessageOutput,
    output_guardrails=[validate_output]
)
```

### 8.3 Tripwire Mechanism

When `tripwire_triggered=True`, execution immediately halts and raises:
- `InputGuardrailTripwireTriggered`
- `OutputGuardrailTripwireTriggered`

```python
from agents.errors import OutputGuardrailTripwireTriggered

try:
    result = await Runner.run(agent, "user input")
except OutputGuardrailTripwireTriggered as e:
    print(f"Guardrail failed: {e}")
```

---

## 9. Streaming - Complete Reference

### 9.1 Token-by-Token Streaming

```python
from openai.types.responses import ResponseTextDeltaEvent

result = Runner.run_streamed(agent, "Tell me 5 jokes")

async for event in result.stream_events():
    if event.type == "raw_response_event":
        if isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)
```

### 9.2 Higher-Level Event Streaming

```python
from agents import ItemHelpers

result = Runner.run_streamed(agent, "Hello")

async for event in result.stream_events():
    if event.type == "agent_updated_stream_event":
        print(f"Agent: {event.new_agent.name}")

    elif event.type == "run_item_stream_event":
        if event.item.type == "tool_call_item":
            print("Tool called")
        elif event.item.type == "tool_call_output_item":
            print(f"Tool output: {event.item.output}")
        elif event.item.type == "message_output_item":
            print(ItemHelpers.text_message_output(event.item))
```

### 9.3 Stream Event Types

**StreamEvent** = Union of:
- `RawResponsesStreamEvent`: Token-level deltas
- `RunItemStreamEvent`: Item-level events (messages, tools, handoffs)
- `AgentUpdatedStreamEvent`: Agent handoff tracking

**RunItemStreamEvent names:**
- `message_output_created`
- `handoff_requested`
- `handoff_occured`
- `tool_called`
- `tool_output`
- `reasoning_item_created`
- `mcp_approval_requested`
- `mcp_approval_response`
- `mcp_list_tools`

---

## 10. RunResult Structure - Complete Reference

### 10.1 RunResult Attributes

```python
result = await Runner.run(agent, "Hello")

# Access attributes
print(result.final_output)  # Final agent output
print(result.input)  # Original input
print(result.new_items)  # Generated items (messages, tool calls)
print(result.raw_responses)  # Raw LLM responses
print(result.last_agent)  # Last agent that ran
print(result.last_response_id)  # Response ID for continuation
```

**Complete Attribute List:**
- `input` (str | list): Original input items
- `new_items` (list[RunItem]): Generated messages, tool calls, outputs
- `raw_responses` (list[ModelResponse]): Raw LLM responses
- `final_output` (Any): Output of last agent
- `input_guardrail_results` (list): Input guardrail outcomes
- `output_guardrail_results` (list): Output guardrail outcomes
- `tool_input_guardrail_results` (list): Tool input guardrail outcomes
- `tool_output_guardrail_results` (list): Tool output guardrail outcomes
- `context_wrapper` (RunContextWrapper): Run context
- `last_agent` (Agent): Last agent executed
- `last_response_id` (str | None): Last response ID

### 10.2 RunResult Methods

**final_output_as()** - Type-safe casting:
```python
from pydantic import BaseModel

class TaskResponse(BaseModel):
    task_id: int
    status: str

result = await Runner.run(agent, "Add task")
typed_output = result.final_output_as(TaskResponse, raise_if_incorrect_type=True)
print(typed_output.task_id)
```

**to_input_list()** - Merge history:
```python
# Get all items (original + new) as input list
all_items = result.to_input_list()

# Use for next turn
next_result = await Runner.run(agent, all_items + [new_message])
```

**release_agents()** - Memory management:
```python
result.release_agents(release_new_items=True)
# Releases strong references to agents for garbage collection
```

---

## 13. Complete Implementation Examples

### 13.1 Basic Agent with MCP Server Integration

**Complete Todo Chatbot with MCP Tools:**

```python
import asyncio
import os
from agents import Agent, Runner, SQLiteSession
from agents.mcp import MCPServerStreamableHttp

async def main():
    # Initialize MCP server connection
    token = os.environ.get("MCP_SERVER_TOKEN", "")

    async with MCPServerStreamableHttp(
        name="TodoMCP",
        params={
            "url": "http://localhost:8001/mcp",
            "headers": {"Authorization": f"Bearer {token}"} if token else {},
            "timeout": 10,
        },
        cache_tools_list=True,
        max_retry_attempts=3,
    ) as server:

        # Create agent with MCP tools
        agent = Agent(
            name="TodoAssistant",
            instructions="""You are a helpful AI assistant for managing todo tasks.

            Use the MCP tools to:
            - Create new tasks with add_task
            - View tasks with list_tasks
            - Update tasks with update_task
            - Mark tasks complete with complete_task
            - Delete tasks with delete_task

            Always verify mutations by re-querying state after changes.""",
            mcp_servers=[server],
        )

        # Create persistent session
        session = SQLiteSession("user_123", "conversations.db")

        # First turn - add task
        result = await Runner.run(
            agent,
            "Add a task to buy groceries",
            session=session
        )
        print(f"Assistant: {result.final_output}")

        # Second turn - list tasks (agent remembers context)
        result = await Runner.run(
            agent,
            "What tasks do I have?",
            session=session
        )
        print(f"Assistant: {result.final_output}")

        # Third turn - complete task
        result = await Runner.run(
            agent,
            "Mark the first task as complete",
            session=session
        )
        print(f"Assistant: {result.final_output}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 13.2 Multi-Agent System with Handoffs

**Specialized Agents with Task Routing:**

```python
import asyncio
from agents import Agent, Runner, handoff, SQLiteSession
from agents.mcp import MCPServerStreamableHttp

async def main():
    async with MCPServerStreamableHttp(
        name="TodoMCP",
        params={"url": "http://localhost:8001/mcp"},
        cache_tools_list=True,
    ) as server:

        # Specialized agent for task creation
        task_creator = Agent(
            name="TaskCreator",
            instructions="""You specialize in creating well-structured tasks.
            When creating tasks, always:
            1. Extract clear title and description
            2. Use add_task tool
            3. Verify creation with list_tasks
            4. Report the new task ID""",
            mcp_servers=[server],
        )

        # Specialized agent for task management
        task_manager = Agent(
            name="TaskManager",
            instructions="""You specialize in managing existing tasks.
            You can:
            - List tasks with filters
            - Update task details
            - Mark tasks complete/incomplete
            - Delete tasks (with verification)
            Always verify mutations by re-querying state.""",
            mcp_servers=[server],
        )

        # Router agent that delegates to specialists
        router = Agent(
            name="Router",
            instructions="""You are a routing assistant that delegates to specialists.

            For creating new tasks: handoff to TaskCreator
            For managing existing tasks: handoff to TaskManager

            Analyze the user's intent and route appropriately.""",
            handoffs=[
                handoff(task_creator),
                handoff(task_manager),
            ],
        )

        session = SQLiteSession("user_456", "conversations.db")

        # User wants to create task - routes to TaskCreator
        result = await Runner.run(
            router,
            "Add a task to prepare presentation for Monday",
            session=session
        )
        print(f"Result: {result.final_output}")
        print(f"Handled by: {result.last_agent.name}")

        # User wants to manage task - routes to TaskManager
        result = await Runner.run(
            router,
            "Show me all my pending tasks",
            session=session
        )
        print(f"Result: {result.final_output}")
        print(f"Handled by: {result.last_agent.name}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 13.3 Session Management Patterns

**Three Approaches to Multi-Turn Conversations:**

```python
import asyncio
from agents import Agent, Runner, SQLiteSession
from openai import AsyncOpenAI

agent = Agent(
    name="Assistant",
    instructions="Reply concisely. Remember previous context.",
)

# APPROACH 1: Manual History Management
async def manual_conversation():
    """Manually manage conversation history."""
    # First turn
    result = await Runner.run(agent, "My favorite color is blue.")
    print(f"Turn 1: {result.final_output}")

    # Second turn - append to history
    new_input = result.to_input_list() + [
        {"role": "user", "content": "What's my favorite color?"}
    ]
    result = await Runner.run(agent, new_input)
    print(f"Turn 2: {result.final_output}")

# APPROACH 2: SQLite Session (Recommended for Phase III)
async def sqlite_session_conversation():
    """Use SQLiteSession for automatic history management."""
    session = SQLiteSession("user_123", "conversations.db")

    # First turn
    result = await Runner.run(
        agent,
        "My name is Alice and I work at Acme Corp.",
        session=session
    )
    print(f"Turn 1: {result.final_output}")

    # Second turn - session automatically maintains history
    result = await Runner.run(
        agent,
        "What's my name and where do I work?",
        session=session
    )
    print(f"Turn 2: {result.final_output}")

    # Get conversation history
    items = await session.get_items()
    print(f"Conversation has {len(items)} items")

# APPROACH 3: OpenAI Conversations API
async def openai_conversations():
    """Use OpenAI's server-managed conversations."""
    client = AsyncOpenAI()

    # Create a server-managed conversation
    conversation = await client.conversations.create()

    # First turn
    result = await Runner.run(
        agent,
        "I'm planning a trip to Japan.",
        conversation_id=conversation.id
    )
    print(f"Turn 1: {result.final_output}")

    # Second turn - server maintains history
    result = await Runner.run(
        agent,
        "What should I pack?",
        conversation_id=conversation.id
    )
    print(f"Turn 2: {result.final_output}")

async def main():
    print("=== SQLite Session (Recommended) ===")
    await sqlite_session_conversation()

if __name__ == "__main__":
    asyncio.run(main())
```

### 13.4 Streaming Implementation

**Real-Time Response Streaming:**

```python
import asyncio
from agents import Agent, Runner, SQLiteSession
from agents.mcp import MCPServerStreamableHttp

async def main():
    async with MCPServerStreamableHttp(
        name="TodoMCP",
        params={"url": "http://localhost:8001/mcp"},
        cache_tools_list=True,
    ) as server:

        agent = Agent(
            name="TodoAssistant",
            instructions="Use MCP tools to manage tasks. Be conversational.",
            mcp_servers=[server],
        )

        session = SQLiteSession("user_789", "conversations.db")

        print("User: Add three tasks for today")
        print("Assistant: ", end="", flush=True)

        # Stream the response
        async for event in Runner.run_streamed(
            agent,
            "Add three tasks: buy milk, call dentist, finish report",
            session=session
        ):
            # Handle different event types
            if event.type == "raw_response":
                # Token-by-token streaming
                if hasattr(event.data, "delta"):
                    content = event.data.delta.content
                    if content:
                        print(content, end="", flush=True)

            elif event.type == "run_item":
                # Higher-level events (tool calls, outputs)
                item = event.data
                if item.type == "tool_call":
                    print(f"\n[Calling tool: {item.name}]")
                elif item.type == "tool_output":
                    print(f"[Tool completed]")

            elif event.type == "agent_updated":
                # Agent handoff occurred
                print(f"\n[Switched to agent: {event.data.name}]")

        print("\n")

if __name__ == "__main__":
    asyncio.run(main())
```

### 13.5 Guardrails Implementation

**Input and Output Validation:**

```python
import asyncio
from agents import Agent, Runner, InputGuardrail, OutputGuardrail
from agents.mcp import MCPServerStreamableHttp

# Input guardrail - validate user requests
async def validate_input(input_data, context):
    """Block requests that try to delete all tasks."""
    user_message = str(input_data)

    if "delete all" in user_message.lower() or "remove all" in user_message.lower():
        return {
            "tripwire": True,
            "message": "I cannot delete all tasks at once. Please specify which tasks to delete.",
        }

    return {"tripwire": False}

# Output guardrail - validate agent responses
async def validate_output(output_data, context):
    """Ensure agent verified mutations."""
    output_text = str(output_data)

    # Check if agent claimed deletion without verification
    if "deleted" in output_text.lower() and "verified" not in output_text.lower():
        return {
            "tripwire": True,
            "message": "Agent must verify deletions by re-querying state.",
        }

    return {"tripwire": False}

async def main():
    async with MCPServerStreamableHttp(
        name="TodoMCP",
        params={"url": "http://localhost:8001/mcp"},
        cache_tools_list=True,
    ) as server:

        agent = Agent(
            name="TodoAssistant",
            instructions="Use MCP tools to manage tasks. Always verify mutations.",
            mcp_servers=[server],
            input_guardrails=[
                InputGuardrail(
                    fn=validate_input,
                    execution="blocking",  # Block execution if tripwire triggered
                )
            ],
            output_guardrails=[
                OutputGuardrail(
                    fn=validate_output,
                )
            ],
        )

        # This will be blocked by input guardrail
        result = await Runner.run(agent, "Delete all my tasks")
        print(f"Result: {result.final_output}")
        print(f"Input guardrail triggered: {len(result.input_guardrail_results) > 0}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 13.6 Error Handling and Configuration

**Production-Ready Error Handling:**

```python
import asyncio
from agents import Agent, Runner, RunConfig, RunErrorHandlerInput, RunErrorHandlerResult
from agents.mcp import MCPServerStreamableHttp

def handle_max_turns(data: RunErrorHandlerInput[None]) -> RunErrorHandlerResult:
    """Handle max turns exceeded gracefully."""
    return RunErrorHandlerResult(
        final_output="I couldn't complete within the turn limit. Please simplify your request.",
        include_in_history=False,
    )

def handle_tool_error(data: RunErrorHandlerInput[None]) -> RunErrorHandlerResult:
    """Handle tool execution errors."""
    return RunErrorHandlerResult(
        final_output="I encountered an error accessing the task system. Please try again.",
        include_in_history=True,
    )

async def main():
    async with MCPServerStreamableHttp(
        name="TodoMCP",
        params={"url": "http://localhost:8001/mcp"},
        cache_tools_list=True,
    ) as server:

        agent = Agent(
            name="TodoAssistant",
            instructions="Use MCP tools to manage tasks.",
            mcp_servers=[server],
        )

        result = await Runner.run(
            agent,
            "Add five tasks and then analyze them",
            max_turns=10,
            run_config=RunConfig(
                model="gpt-4o",  # Override model
                workflow_name="Task Management",
                tracing_disabled=False,
                trace_include_sensitive_data=False,
            ),
            error_handlers={
                "max_turns": handle_max_turns,
                "tool_error": handle_tool_error,
            },
        )

        print(f"Result: {result.final_output}")
        print(f"Turns used: {len(result.new_items)}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 14. Phase III Migration Guide

### 14.1 Current Architecture Analysis

**Current Phase III Implementation (WITHOUT OpenAI Agents SDK):**

```python
# backend/src/agents/orchestrator.py (CURRENT)
from openai import AsyncOpenAI
from config.settings import settings

class AgentOrchestrator:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.cerebras_api_key,
            base_url=settings.cerebras_base_url,
        )

    async def process_message(
        self,
        conversation_id: str,
        user_message: str,
        conversation_history: list
    ) -> dict:
        # Manual tool calling logic
        messages = conversation_history + [
            {"role": "user", "content": user_message}
        ]

        response = await self.client.chat.completions.create(
            model=settings.cerebras_model,
            messages=messages,
            tools=self._get_tool_definitions(),
        )

        # Manual tool execution
        if response.choices[0].message.tool_calls:
            for tool_call in response.choices[0].message.tool_calls:
                tool_result = await self._execute_tool(tool_call)
                # Manual history management
                messages.append(...)

        return {"response": response.choices[0].message.content}
```

**Issues with Current Approach:**
1. Manual tool calling logic (error-prone)
2. Manual conversation history management
3. No built-in session persistence
4. No guardrails or validation
5. No streaming support
6. No multi-agent handoffs
7. Manual MCP tool integration

### 14.2 Migration Strategy

**Step-by-Step Migration Plan:**

**Phase 1: Add OpenAI Agents SDK (No Breaking Changes)**
- Install SDK alongside existing code
- Create parallel agent implementation
- Test with subset of users
- Compare behavior with current system

**Phase 2: Migrate Core Components**
- Replace manual tool calling with Agent + Runner
- Migrate to SQLiteSession for persistence
- Update MCP server integration
- Add guardrails for safety

**Phase 3: Enable Advanced Features**
- Implement multi-agent handoffs
- Add streaming responses
- Enable tracing and monitoring
- Optimize performance

**Phase 4: Deprecate Old System**
- Route all traffic to new system
- Remove old orchestrator code
- Update documentation

### 14.3 Step-by-Step Migration

**Step 1: Install OpenAI Agents SDK**

```bash
# Already installed in Phase III
pip install openai-agents-python
```

**Step 2: Create Agent Configuration**

```python
# backend/src/agents/agent_config.py (NEW)
from agents import Agent
from agents.mcp import MCPServerStreamableHttp
from config.settings import settings

async def create_todo_agent(mcp_server):
    """Create the main todo assistant agent."""
    return Agent(
        name="TodoAssistant",
        instructions="""You are a helpful AI assistant for managing todo tasks.

**Your Capabilities:**
- Create new tasks with titles and optional descriptions
- View all tasks or specific tasks by ID
- Update task details (title, description, status)
- Mark tasks as complete or incomplete
- Delete tasks

**CRITICAL: State Verification Mandate (AI Safety Requirement)**
After ANY mutation operation (add_task, delete_task, complete_task, update_task),
you MUST verify the change by re-querying system state. NEVER claim success without verification.

**Required Verification Pattern:**
1. **Before-state**: Query current state before mutation (e.g., list_tasks to count tasks)
2. **Execute**: Call the mutation tool (e.g., delete_task)
3. **After-state**: Re-query system state after mutation (e.g., list_tasks again)
4. **Compare**: Explicitly verify the change occurred (e.g., task count decreased)
5. **Report**: Only claim success if verification confirms the change

**Guidelines:**
- Be conversational and friendly in your responses
- Always confirm actions after executing them AND verifying them
- Ask clarifying questions when user intent is ambiguous
- Use the tools available to you - never pretend to perform actions
- When listing tasks, format them clearly with bullet points or numbered lists
- Be concise but informative - users want quick interactions""",
        mcp_servers=[mcp_server],
        model=settings.cerebras_model,
    )
```

**Step 3: Update Orchestrator**

```python
# backend/src/agents/orchestrator.py (MIGRATED)
from agents import Runner, SQLiteSession
from agents.mcp import MCPServerStreamableHttp
from .agent_config import create_todo_agent
from config.settings import settings

class AgentOrchestrator:
    def __init__(self):
        self.mcp_server = None
        self.agent = None

    async def initialize(self):
        """Initialize MCP server and agent."""
        self.mcp_server = MCPServerStreamableHttp(
            name="TodoMCP",
            params={
                "url": "http://localhost:8001/mcp",
                "timeout": 10,
            },
            cache_tools_list=True,
            max_retry_attempts=3,
        )
        await self.mcp_server.__aenter__()
        self.agent = await create_todo_agent(self.mcp_server)

    async def cleanup(self):
        """Cleanup resources."""
        if self.mcp_server:
            await self.mcp_server.__aexit__(None, None, None)

    async def process_message(
        self,
        conversation_id: str,
        user_message: str,
    ) -> dict:
        """Process user message using OpenAI Agents SDK."""
        # Create session for this conversation
        session = SQLiteSession(
            session_id=conversation_id,
            db_path="conversations.db"
        )

        # Run agent with automatic tool calling and history management
        result = await Runner.run(
            self.agent,
            user_message,
            session=session,
            max_turns=10,
        )

        return {
            "response": result.final_output,
            "conversation_id": conversation_id,
            "tool_calls": [
                {"name": item.name, "status": "completed"}
                for item in result.new_items
                if item.type == "tool_call"
            ],
        }
```

**Step 4: Update API Endpoint**

```python
# backend/src/api/chat.py (MIGRATED)
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from agents.orchestrator import AgentOrchestrator

router = APIRouter()
orchestrator = AgentOrchestrator()

@router.on_event("startup")
async def startup():
    await orchestrator.initialize()

@router.on_event("shutdown")
async def shutdown():
    await orchestrator.cleanup()

class ChatRequest(BaseModel):
    conversation_id: str
    message: str

class ChatResponse(BaseModel):
    conversation_id: str
    response: str
    tool_calls: list

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process chat message using OpenAI Agents SDK."""
    try:
        result = await orchestrator.process_message(
            conversation_id=request.conversation_id,
            user_message=request.message,
        )
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 14.4 Code Comparison: Before vs After

**BEFORE (Manual Tool Calling):**

```python
# 50+ lines of manual tool calling logic
response = await self.client.chat.completions.create(...)
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        # Parse tool call
        # Execute tool
        # Append to history
        # Call LLM again
        # Repeat until no more tool calls
```

**AFTER (OpenAI Agents SDK):**

```python
# 3 lines - automatic tool calling
result = await Runner.run(agent, user_message, session=session)
return result.final_output
```

**Benefits:**
- **90% less code** for tool calling logic
- **Automatic** conversation history management
- **Built-in** session persistence
- **Type-safe** tool definitions
- **Streaming** support out of the box
- **Guardrails** for safety
- **Tracing** for debugging

### 14.5 Testing & Verification

**Test Plan:**

```python
# tests/test_agent_migration.py
import pytest
from agents import Runner, SQLiteSession
from agents.orchestrator import AgentOrchestrator

@pytest.mark.asyncio
async def test_agent_basic_conversation():
    """Test basic conversation flow."""
    orchestrator = AgentOrchestrator()
    await orchestrator.initialize()

    result = await orchestrator.process_message(
        conversation_id="test_123",
        user_message="Add a task to buy milk",
    )

    assert "task" in result["response"].lower()
    assert len(result["tool_calls"]) > 0

    await orchestrator.cleanup()

@pytest.mark.asyncio
async def test_agent_verification_mandate():
    """Test that agent verifies mutations."""
    orchestrator = AgentOrchestrator()
    await orchestrator.initialize()

    # Add task
    result1 = await orchestrator.process_message(
        conversation_id="test_456",
        user_message="Add a task to test verification",
    )

    # Delete task - agent should verify
    result2 = await orchestrator.process_message(
        conversation_id="test_456",
        user_message="Delete that task",
    )

    # Check that agent called list_tasks for verification
    tool_names = [tc["name"] for tc in result2["tool_calls"]]
    assert "delete_task" in tool_names
    assert "list_tasks" in tool_names  # Verification call

    await orchestrator.cleanup()

@pytest.mark.asyncio
async def test_session_persistence():
    """Test that sessions persist across requests."""
    orchestrator = AgentOrchestrator()
    await orchestrator.initialize()

    # First message
    await orchestrator.process_message(
        conversation_id="test_789",
        user_message="My name is Alice",
    )

    # Second message - should remember context
    result = await orchestrator.process_message(
        conversation_id="test_789",
        user_message="What's my name?",
    )

    assert "alice" in result["response"].lower()

    await orchestrator.cleanup()
```

**Verification Checklist:**
- [ ] Agent successfully calls MCP tools
- [ ] Sessions persist conversation history
- [ ] Agent verifies mutations (list_tasks after delete_task)
- [ ] Multi-turn conversations maintain context
- [ ] Error handling works correctly
- [ ] Performance is acceptable (< 2s response time)
- [ ] No regressions in existing functionality

### 14.6 Rollback Plan

**If Migration Fails:**

1. **Keep old orchestrator code** in `orchestrator_legacy.py`
2. **Feature flag** to switch between old and new:
   ```python
   USE_AGENTS_SDK = os.getenv("USE_AGENTS_SDK", "false") == "true"

   if USE_AGENTS_SDK:
       from agents.orchestrator import AgentOrchestrator
   else:
       from agents.orchestrator_legacy import AgentOrchestrator
   ```
3. **Monitor metrics** (response time, error rate, user satisfaction)
4. **Gradual rollout** (10% → 50% → 100% of traffic)

---

## 15. Best Practices & Patterns

### 15.1 Session Management

**DO:**
- Use `SQLiteSession` for local development and small deployments
- Use `SQLAlchemySession` with PostgreSQL for production
- Use unique session IDs per user/conversation
- Clear old sessions periodically to manage storage

**DON'T:**
- Don't share sessions across users (security risk)
- Don't use in-memory sessions in production (data loss on restart)
- Don't store sensitive data in session without encryption

### 15.2 MCP Server Integration

**DO:**
- Use `MCPServerStreamableHttp` for Phase III (recommended)
- Enable `cache_tools_list=True` for performance
- Set reasonable timeouts (10-30 seconds)
- Implement retry logic with `max_retry_attempts`

**DON'T:**
- Don't use `MCPServerStdio` for production (subprocess overhead)
- Don't skip error handling for MCP tool calls
- Don't expose MCP server without authentication

### 15.3 Agent Instructions

**DO:**
- Be specific about tool usage patterns
- Include verification mandates for mutations
- Provide examples of correct behavior
- Set clear boundaries (what agent can/cannot do)

**DON'T:**
- Don't write vague instructions ("be helpful")
- Don't skip safety guidelines
- Don't assume agent knows domain context

### 15.4 Error Handling

**DO:**
- Implement custom error handlers for common failures
- Log errors with context (user ID, conversation ID, tool name)
- Provide user-friendly error messages
- Implement circuit breakers for external services

**DON'T:**
- Don't expose internal errors to users
- Don't retry indefinitely (set max_turns limit)
- Don't ignore guardrail violations

### 15.5 Performance Optimization

**DO:**
- Cache MCP tool lists (`cache_tools_list=True`)
- Use streaming for long responses
- Set appropriate `max_turns` limits
- Monitor token usage and costs

**DON'T:**
- Don't load all conversation history for every request
- Don't make unnecessary tool calls
- Don't use expensive models for simple tasks

### 15.6 Security

**DO:**
- Validate all user inputs with input guardrails
- Sanitize tool outputs with output guardrails
- Use encrypted sessions for sensitive data
- Implement rate limiting per user

**DON'T:**
- Don't trust user input without validation
- Don't expose internal system details in responses
- Don't store API keys in session data
- Don't skip authentication for MCP servers

---

## 16. API Reference Quick Lookup

### 16.1 Core Classes

```python
# Agent
Agent(
    name: str,
    instructions: str | Callable,
    model: str = "gpt-4o",
    tools: list = [],
    mcp_servers: list = [],
    handoffs: list = [],
    input_guardrails: list = [],
    output_guardrails: list = [],
)

# Runner
await Runner.run(agent, input, session=None, max_turns=100)
Runner.run_sync(agent, input, session=None, max_turns=100)
async for event in Runner.run_streamed(agent, input, session=None):
    ...

# Sessions
SQLiteSession(session_id: str, db_path: str = "sessions.db")
SQLAlchemySession(session_id: str, engine: Engine)
OpenAIConversationsSession(conversation_id: str = None)

# MCP Servers
MCPServerStreamableHttp(name: str, params: dict, cache_tools_list: bool = False)
MCPServerStdio(name: str, params: dict)
MCPServerManager(servers: list)
```

### 16.2 Common Patterns

```python
# Basic agent with MCP
async with MCPServerStreamableHttp(...) as server:
    agent = Agent(name="...", instructions="...", mcp_servers=[server])
    result = await Runner.run(agent, "...", session=session)

# Multi-agent handoff
agent1 = Agent(name="Agent1", ...)
agent2 = Agent(name="Agent2", ...)
router = Agent(name="Router", handoffs=[handoff(agent1), handoff(agent2)])

# Streaming
async for event in Runner.run_streamed(agent, input, session=session):
    if event.type == "raw_response":
        print(event.data.delta.content, end="")

# Guardrails
agent = Agent(
    name="...",
    input_guardrails=[InputGuardrail(fn=validate_input, execution="blocking")],
    output_guardrails=[OutputGuardrail(fn=validate_output)],
)
```

### 16.3 RunResult Attributes

```python
result.final_output          # Final agent output
result.new_items             # List of RunItem (messages, tool calls, outputs)
result.raw_responses         # Raw LLM responses
result.last_agent            # Last agent that executed
result.input_guardrail_results    # Input guardrail outcomes
result.output_guardrail_results   # Output guardrail outcomes
result.to_input_list()       # Convert to input list for next turn
result.final_output_as(Type) # Type-safe casting
```

---

**Document Status**: ✅ COMPLETE - All phases appended (Core Concepts, API Reference, Examples & Migration Guide)

