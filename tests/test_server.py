"""Tests for the FastMCP server builder."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any

import pytest

from fastmcp_template import MCPServerBuilder, ServerSettings


@dataclass
class DummyAgent:
    """Simple agent used to simulate language model interactions."""

    responses: dict[str, str]

    async def chat(self, query: str) -> dict[str, str]:
        return {"result": self.responses[query]}


class FakeTool:
    def __init__(self, name: str, description: str, handler):
        self.name = name
        self.description = description
        self.handler = handler


class FakeApp:
    def __init__(self, *, name: str, instructions: str, metadata: dict[str, str]):
        self.name = name
        self.instructions = instructions
        self.metadata = metadata
        self.tools: list[FakeTool] = []

    def register_tool(self, tool: FakeTool) -> None:
        self.tools.append(tool)


class FakeResponseMessage:
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content


@pytest.fixture()
def fastmcp_module() -> SimpleNamespace:
    """Return a fake FastMCP module used to isolate tests from the real library."""

    return SimpleNamespace(FastMCP=FakeApp, Tool=FakeTool, ResponseMessage=FakeResponseMessage)


def test_build_server_registers_tool(fastmcp_module: SimpleNamespace) -> None:
    agent = DummyAgent({"hello": "world"})
    builder = MCPServerBuilder(lambda: agent, ServerSettings(), fastmcp_module)

    app = builder.build()

    assert isinstance(app, FakeApp)
    assert len(app.tools) == 1
    handler = app.tools[0].handler
    response = asyncio.run(handler(question="hello"))
    assert isinstance(response, FakeResponseMessage)
    assert response.content == "world"


def test_handler_accepts_multiple_aliases(fastmcp_module: SimpleNamespace) -> None:
    agent = DummyAgent({"question": "value", "prompt": "value", "query": "value"})
    builder = MCPServerBuilder(lambda: agent, ServerSettings(), fastmcp_module)
    app = builder.build()
    handler = app.tools[0].handler

    for key in ("question", "prompt", "query"):
        response = asyncio.run(handler(**{key: key}))
        assert response.content == "value"


def test_handler_without_response_message_returns_mapping() -> None:
    agent = DummyAgent({"ping": "pong"})
    fastmcp = SimpleNamespace(FastMCP=FakeApp, Tool=FakeTool)
    builder = MCPServerBuilder(lambda: agent, ServerSettings(), fastmcp)
    app = builder.build()
    handler = app.tools[0].handler

    response = asyncio.run(handler(prompt="ping"))
    assert response == {"role": "assistant", "content": "pong"}


def test_extract_query_missing_value_raises_value_error() -> None:
    payload = {}
    with pytest.raises(ValueError):
        MCPServerBuilder._extract_query(payload)
