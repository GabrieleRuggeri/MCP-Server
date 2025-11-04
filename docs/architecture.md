# Architecture Overview

The template is intentionally lightweight while providing a clear separation of
concerns between configuration, server orchestration, client utilities, and the
language model integration.

## Key components

- **`fastmcp_template.llm.Agent`** — encapsulates the prompt pipeline, providing a
  consistent `chat` coroutine that returns a mapping with a `result` key.
- **`fastmcp_template.server.MCPServerBuilder`** — constructs the FastMCP server by
  registering a single tool that proxies requests to the configured agent. The
  builder handles payload normalisation and response formatting.
- **`fastmcp_template.client.MCPClient`** — convenience wrapper around the
  FastMCP client. It exposes synchronous and asynchronous interfaces and offers a
  consistent string response regardless of the underlying server response format.
- **`fastmcp_template.config`** — provides dataclasses that hold default
  configuration values. Override them or use environment variables in your own
  project to tailor runtime behaviour.

## Control flow

1. A client issues a tool invocation (via `MCPClient.invoke`) that includes a
   `question` payload.
2. FastMCP forwards the invocation to the registered handler built by
   `MCPServerBuilder`.
3. The handler instantiates an agent using the supplied factory and calls
   `Agent.chat` with the extracted question.
4. The agent prompts the backing language model and returns the answer wrapped in
   a dictionary.
5. The handler converts the answer into the response structure expected by
   FastMCP and returns it to the client.

This control flow ensures that replacing the agent implementation has no impact
on the server/client plumbing as long as the `chat` contract remains stable.

## Extending the template

- **Multiple tools**: extend `MCPServerBuilder.build` to register additional tools
  with custom handlers. The configuration dataclass can be expanded to hold the
  metadata for each tool.
- **Stateful agents**: if your agent maintains state across invocations, update the
  `agent_factory` to return a pre-initialised instance and store it on the builder
  or handler closure.
- **Observability**: integrate the Python `logging` module inside the handler to
  trace requests, timings, or user identifiers.

## Deployment notes

The template intentionally avoids bundling deployment opinionated code. Use the
server instance returned by `MCPServerBuilder.build` with the official FastMCP
CLI or embed it in an ASGI/WSGI application depending on your production needs.
