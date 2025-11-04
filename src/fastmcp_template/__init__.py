"""FastMCP client and server template package.

This package provides ready-to-use utilities for building a Model Context Protocol
(MCP) server and client powered by the `fastmcp` library. The template focuses on
clarity and extensibility so that developers can adapt it to their own LLM tools.
"""

from .config import ClientSettings, ServerSettings
from .llm import Agent, create_agent
from .server import MCPServerBuilder
from .client import MCPClient

__all__ = [
    "Agent",
    "ClientSettings",
    "ServerSettings",
    "MCPServerBuilder",
    "MCPClient",
    "create_agent",
]
