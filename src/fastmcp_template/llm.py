"""Language model interface compatible with the template server."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from importlib import import_module
from typing import Any


@dataclass(slots=True)
class Agent:
    """Thin wrapper around an Ollama language model."""

    model_id: str = "qwen2.5:1.5b"
    temperature: float = 0.1
    system_prompt: str = (
        "You are an AI assistant. Answer the user question precisely and politely.\n"
        "USER QUESTION: {question}"
    )
    _model: Any = field(init=False, repr=False)
    _prompt: Any = field(init=False, repr=False)
    _chain: Any = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Initialise the LangChain prompt pipeline."""
        prompts_module = import_module("langchain_core.prompts")
        ollama_module = import_module("langchain_ollama.llms")
        chat_prompt_template = getattr(prompts_module, "ChatPromptTemplate")
        ollama_llm = getattr(ollama_module, "OllamaLLM")
        self._model = ollama_llm(model=self.model_id, temperature=self.temperature)
        self._prompt = chat_prompt_template.from_template(self.system_prompt)
        self._chain = self._prompt | self._model

    async def chat(self, query: str) -> dict[str, str]:
        """Send a prompt to the configured language model."""
        result: str = await self._chain.ainvoke({"question": query})
        return {"result": result}

    def chat_sync(self, query: str) -> dict[str, str]:
        """Synchronously evaluate a prompt."""  # noqa: D401
        return asyncio.run(self.chat(query))

    def test(self) -> None:
        """Print the result of a simple sanity-check query."""
        response = self.chat_sync("What is the capital of France?")
        print(f"Response: {response['result']}")


def create_agent(**overrides: Any) -> Agent:
    """Factory helper that builds an :class:`Agent` instance."""  # noqa: D401
    return Agent(**overrides)
