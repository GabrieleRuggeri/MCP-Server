"""Tests covering the default language model agent."""

from __future__ import annotations

import asyncio
import sys
import types

import pytest

from fastmcp_template.llm import Agent


class FakePrompt:
    def __init__(self, template: str):
        self.template = template

    def __or__(self, other: "FakeModel") -> "FakeChain":
        return FakeChain(other)


class FakePromptTemplate:
    @staticmethod
    def from_template(template: str) -> FakePrompt:
        return FakePrompt(template)


class FakeModel:
    def __init__(self, *, model: str, temperature: float):
        self.model = model
        self.temperature = temperature

    async def ainvoke(self, payload: dict[str, str]) -> str:
        return f"{self.model}:{payload['question']}@{self.temperature}"


class FakeChain:
    def __init__(self, model: FakeModel):
        self.model = model

    async def ainvoke(self, payload: dict[str, str]) -> str:
        return await self.model.ainvoke(payload)


@pytest.fixture(autouse=True)
def patch_langchain(monkeypatch: pytest.MonkeyPatch) -> None:
    prompts_module = types.SimpleNamespace(ChatPromptTemplate=FakePromptTemplate)
    llms_module = types.SimpleNamespace(OllamaLLM=FakeModel)
    monkeypatch.setitem(sys.modules, "langchain_core.prompts", prompts_module)
    monkeypatch.setitem(sys.modules, "langchain_ollama.llms", llms_module)


def test_agent_chat_returns_result() -> None:
    agent = Agent(model_id="test-model", temperature=0.5)
    result = asyncio.run(agent.chat("hello"))
    assert result == {"result": "test-model:hello@0.5"}


def test_chat_sync_reuses_async() -> None:
    agent = Agent(model_id="another-model")
    result = agent.chat_sync("ping")
    assert result["result"].startswith("another-model:ping")
