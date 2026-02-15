"""
MCP (Model Context Protocol) Package

Built with the Official MCP Python SDK (FastMCP).
Provides an MCP server that exposes task operations as tools.
"""

from .mcp_server import (
    mcp,
    get_mcp_tool_handlers,
    get_mcp_tool_schemas
)


__all__ = [
    "mcp",
    "get_mcp_tool_handlers",
    "get_mcp_tool_schemas"
]
