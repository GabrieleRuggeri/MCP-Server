"""CLI entry point demonstrating how to launch the template FastMCP server."""

from __future__ import annotations

from fastmcp_template import MCPServerBuilder, ServerSettings, create_agent


def main() -> None:
    """Create an MCP server instance and print startup instructions."""

    builder = MCPServerBuilder(create_agent, ServerSettings())
    server = builder.build()
    print(
        "Server initialised. Run `fastmcp serve main:main` or use the official CLI "
        "to host the server instance."
    )
    return server


if __name__ == "__main__":  # pragma: no cover - CLI guard
    main()
