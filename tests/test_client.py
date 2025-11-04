"""Tests for the MCP client wrapper."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any

import pytest

from fastmcp_template import ClientSettings
from fastmcp_template.client import MCPClient


class FakeClient:
    """Asynchronous context manager that records invocations."""

    calls: list[tuple[str, dict[str, Any]]] = []

    def __init__(self, *, server_url: str, request_timeout: float, extra_headers: dict[str, str]):
        self.server_url = server_url
        self.request_timeout = request_timeout
        self.extra_headers = extra_headers

    async def __aenter__(self) -> "FakeClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
        return None

    async def invoke_tool(self, tool_name: str, **payload: Any) -> Any:
        self.__class__.calls.append((tool_name, payload))
        return {"result": payload["question"].upper()}


@pytest.fixture()
def fastmcp_module() -> SimpleNamespace:
    FakeClient.calls.clear()
    return SimpleNamespace(Client=FakeClient)


def test_invoke_returns_normalised_string(fastmcp_module: SimpleNamespace) -> None:
    settings = ClientSettings(server_url="http://test", request_timeout=10)
    client = MCPClient(settings=settings, fastmcp_module=fastmcp_module)

    result = asyncio.run(client.invoke("hello world"))
    assert result == "HELLO WORLD"


def test_invoke_sync_wraps_async_call(fastmcp_module: SimpleNamespace) -> None:
    client = MCPClient(fastmcp_module=fastmcp_module)
    result = client.invoke_sync("sync call")
    assert result == "SYNC CALL"


def test_extra_payload_is_forwarded(fastmcp_module: SimpleNamespace) -> None:
    client = MCPClient(fastmcp_module=fastmcp_module)
    asyncio.run(client.invoke("payload", tone="friendly"))
    _, payload = FakeClient.calls[-1]
    assert payload["tone"] == "friendly"


def test_extract_response_text_handles_variations() -> None:
    assert MCPClient._extract_response_text("value") == "value"
    assert MCPClient._extract_response_text({"result": 1}) == "1"
    assert MCPClient._extract_response_text({"content": 2}) == "2"

    @dataclass
    class Response:
        content: str

    assert MCPClient._extract_response_text(Response("data")) == "data"

    with pytest.raises(TypeError):
        MCPClient._extract_response_text(123)
