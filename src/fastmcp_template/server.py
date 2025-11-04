"""Utilities to build a FastMCP server backed by an :class:`Agent`."""

from __future__ import annotations

from dataclasses import dataclass, field
from importlib import import_module
from types import ModuleType
from typing import Any, Callable, Protocol

from .config import ServerSettings
from .llm import Agent


class _AsyncToolHandler(Protocol):
    async def __call__(self, **data: Any) -> Any:  # pragma: no cover - protocol definition
        """Signature expected by the FastMCP tool registration API."""


@dataclass(slots=True)
class MCPServerBuilder:
    """Factory helper that wires an :class:`Agent` to a FastMCP server instance.

    The builder keeps the coupling between the language model agent and the
    underlying FastMCP application explicit, offering a clear starting point for
    projects that require more complex orchestration.

    Args:
        agent_factory: Callable that returns a fully configured :class:`Agent`.
        settings: Optional :class:`ServerSettings` object. Defaults to
            :class:`ServerSettings`.
        fastmcp_module: Optional FastMCP module. Primarily useful during testing
            where the real library may not be installed yet.
    """

    agent_factory: Callable[[], Agent]
    settings: ServerSettings = field(default_factory=ServerSettings)
    fastmcp_module: ModuleType | None = None

    def build(self) -> Any:
        """Instantiate a FastMCP server configured with the provided agent."""

        fastmcp = self.fastmcp_module or import_module("fastmcp")
        fastmcp_app = fastmcp.FastMCP(  # type: ignore[attr-defined]
            name=self.settings.server_name,
            instructions=self.settings.instructions,
            metadata=dict(self.settings.metadata),
        )
        tool = fastmcp.Tool(  # type: ignore[attr-defined]
            name=self.settings.tool_name,
            description=self.settings.tool_description,
            handler=self._build_handler(fastmcp),
        )
        fastmcp_app.register_tool(tool)  # type: ignore[attr-defined]
        return fastmcp_app

    def _build_handler(self, fastmcp: ModuleType) -> _AsyncToolHandler:
        """Create the coroutine used by FastMCP to process tool invocations."""

        async def _handler(**payload: Any) -> Any:
            query = self._extract_query(payload)
            agent = self.agent_factory()
            response = await agent.chat(query)
            result_text = response["result"]
            response_message = getattr(fastmcp, "ResponseMessage", None)
            if response_message is None:
                return {"role": "assistant", "content": result_text}
            return response_message(role="assistant", content=result_text)

        return _handler

    @staticmethod
    def _extract_query(payload: dict[str, Any]) -> str:
        """Extract a usable prompt from the incoming tool payload."""

        for key in ("question", "prompt", "query"):
            value = payload.get(key)
            if value:
                return str(value)
        raise ValueError(
            "Unable to extract a prompt from the incoming FastMCP payload. Provide "
            "a 'question', 'prompt', or 'query' argument when invoking the tool."
        )
