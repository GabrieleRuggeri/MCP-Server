"""Example script showcasing the MCP client wrapper.

Run after the development server is started via `examples/run_server.py`.
"""

from __future__ import annotations

from fastmcp_template import MCPClient


def main() -> None:
    """Send a sample prompt to the MCP server and display the response."""

    client = MCPClient()
    response = client.invoke_sync("List three benefits of FastMCP.")
    print("Server response:")
    print(response)


if __name__ == "__main__":  # pragma: no cover - script entry point
    main()
