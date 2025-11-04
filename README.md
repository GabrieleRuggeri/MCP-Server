# FastMCP Client/Server Template

A batteries-included template for building Model Context Protocol (MCP) clients and
servers with the [`fastmcp`](https://github.com/latent-space-inc/fastmcp) library.
The repository emphasises documentation and practical examples so that teams can
quickly customise the provided building blocks to suit their own language models
and deployment workflows.

---

## Features

- **LangChain-compatible agent** – ships with a reference implementation that uses
  `langchain-ollama` and mirrors the contract defined in `llm.py`.
- **Configurable FastMCP server builder** – focus on productivity by injecting your
  own agent implementation without changing the server scaffolding.
- **High-level client wrapper** – issue MCP tool invocations without memorising the
  low-level FastMCP client APIs.
- **Extensive documentation and examples** – step-by-step guides, configuration
  tables, and runnable scripts that shorten the onboarding time for new users.
- **Fully tested and typed** – includes unit tests, type hints, and linting
  configurations to ensure code quality.

## Repository layout

```
.
├── docs/                  # Additional documentation and design notes
├── examples/              # Runnable client/server examples
├── src/fastmcp_template/  # Template package source code
├── tests/                 # Pytest-based test-suite
├── main.py                # Minimal CLI entry point for the FastMCP server
└── README.md              # You're reading it!
```

## Getting started

### 1. Install dependencies

The project uses Python 3.12 or newer. Install dependencies with `uv`, `pip`, or
any modern package manager:

```bash
pip install -e .[dev]
```

The default extras include:

- `fastmcp`
- `langchain-core`
- `langchain-ollama`
- Tooling dependencies (`pytest`, `mypy`, `ruff`, etc.)

### 2. Configure your language model agent

The default agent lives in [`src/fastmcp_template/llm.py`](src/fastmcp_template/llm.py)
and exposes the contract expected by the MCP server – an asynchronous `chat`
method returning a `{"result": <str>}` dictionary. Replace the implementation or
parameterise the factory to target your own model.

Example customisation:

```python
from fastmcp_template import create_agent

ollama_agent = create_agent(model_id="qwen2.5:7b", temperature=0.3)
```

If you need a completely different backend, implement a class with the same
interface (`chat` coroutine) and update the factory you pass to the server
builder.

### 3. Launch the FastMCP server

Create a module (or reuse `main.py`) that builds an instance of the server and
exposes a `main()` function returning the FastMCP app:

```python
from fastmcp_template import MCPServerBuilder, ServerSettings, create_agent

builder = MCPServerBuilder(create_agent, ServerSettings(server_name="custom"))
server = builder.build()
```

Run the server using the FastMCP CLI:

```bash
fastmcp serve main:main
```

### 4. Interact with the server via the client wrapper

The template provides [`fastmcp_template.client.MCPClient`](src/fastmcp_template/client.py)
which hides the boilerplate required to invoke MCP tools.

```python
from fastmcp_template import MCPClient

client = MCPClient()
response = client.invoke_sync("Explain MCP in one sentence.")
print(response)
```

For asynchronous workflows you can await `client.invoke` directly.

## Examples

The [`examples/`](examples/) directory contains two scripts:

- [`run_server.py`](examples/run_server.py): boots a development FastMCP server.
- [`run_client.py`](examples/run_client.py): sends prompts to the server and prints
  the responses.

Follow the instructions in each file's docstring to tailor them to your needs.

## Documentation

Additional guides live in the [`docs/`](docs/) directory:

- [`architecture.md`](docs/architecture.md) explains the overall design.
- [`customisation.md`](docs/customisation.md) provides recipes for extending the
  template with new tools, authentication, and deployment tips.

## Development workflow

The repository ships with formatter, linter, type-checker, and test commands.
Run the helpers before submitting changes:

```bash
ruff check src tests
mypy src
pytest
```

These commands are wired into the `pyproject.toml` configuration and compatible
with most continuous integration providers.

## Testing

The unit tests rely on lightweight fakes instead of the real FastMCP library, so
they run quickly even on systems without the dependency installed. To run the
suite:

```bash
pytest
```

## License

This template is released under the MIT license. Adapt it freely for your own MCP
projects.
