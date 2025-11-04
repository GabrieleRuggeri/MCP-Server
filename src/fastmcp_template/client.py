"""Client utilities for interacting with FastMCP servers."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from importlib import import_module
from types import ModuleType
from typing import Any

from .config import ClientSettings


@dataclass(slots=True)
class MCPClient:
    """High-level async client for interacting with the template FastMCP server."""

    settings: ClientSettings = field(default_factory=ClientSettings)
    fastmcp_module: ModuleType | None = None
    tool_name: str = "prompt"

    async def invoke(self, prompt: str, **extra_payload: Any) -> str:
        """Send a prompt to the configured server tool and return the response text."""

        fastmcp = self.fastmcp_module or import_module("fastmcp")
        client_cls = getattr(fastmcp, "Client")
        async with client_cls(  # type: ignore[call-arg]
            server_url=self.settings.server_url,
            request_timeout=self.settings.request_timeout,
            extra_headers=dict(self.settings.extra_headers),
        ) as client:
            payload = {"question": prompt, **extra_payload}
            response = await client.invoke_tool(self.tool_name, **payload)
        return self._extract_response_text(response)

    def invoke_sync(self, prompt: str, **extra_payload: Any) -> str:
        """Synchronously invoke the client."""

        return asyncio.run(self.invoke(prompt, **extra_payload))

    @staticmethod
    def _extract_response_text(response: Any) -> str:
        """Normalise the server response into a string."""

        if isinstance(response, str):
            return response
        if isinstance(response, dict):
            if "result" in response:
                return str(response["result"])
            if "content" in response:
                return str(response["content"])
        if hasattr(response, "content"):
            return str(response.content)
        raise TypeError(
            "Unable to convert the FastMCP response into text. Ensure that the server "
            "tool returns either a string, a mapping containing 'result' or 'content', "
            "or an object exposing a 'content' attribute."
        )
