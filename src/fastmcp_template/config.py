"""Configuration models for the FastMCP template."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping


@dataclass(slots=True)
class ServerSettings:
    """Configuration required to bootstrap an MCP server.

    Args:
        server_name: Human readable name for the MCP server instance.
        instructions: High-level instructions describing the server's behaviour.
        tool_name: Identifier of the primary tool exposed by the MCP server.
        tool_description: Summary of what the tool does.
        metadata: Additional metadata attached to the server registration payload.
    """

    server_name: str = "fastmcp-template-server"
    instructions: str = "Respond to MCP invocations using the configured language model."
    tool_name: str = "prompt"
    tool_description: str = (
        "Send natural language prompts to the backing language model and receive a response."
    )
    metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class ClientSettings:
    """Configuration for building a FastMCP client instance.

    Args:
        server_url: Base URL for connecting to the MCP server.
        request_timeout: Timeout in seconds for client requests.
        extra_headers: Optional HTTP headers to send with each request.
    """

    server_url: str = "http://localhost:8000"
    request_timeout: float = 30.0
    extra_headers: Mapping[str, str] = field(default_factory=dict)
