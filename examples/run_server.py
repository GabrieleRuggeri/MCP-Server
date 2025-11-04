"""Example script that starts the FastMCP server for local development.

Usage
-----
python examples/run_server.py

The script returns a configured FastMCP application. To host it using the official
FastMCP CLI run `fastmcp serve examples.run_server:build_server`.
"""

from __future__ import annotations

from fastmcp_template import MCPServerBuilder, ServerSettings, create_agent


def build_server():
    """Create the FastMCP server application."""

    builder = MCPServerBuilder(
        agent_factory=lambda: create_agent(model_id="qwen2.5:1.5b"),
        settings=ServerSettings(server_name="local-fastmcp"),
    )
    return builder.build()


if __name__ == "__main__":  # pragma: no cover - script entry point
    app = build_server()
    print("FastMCP application created:", app)
