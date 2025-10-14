# Research Notes: OpenWebUI and MCP Integration

## Key Findings

### OpenWebUI Tool Integration
- OpenWebUI natively supports function calling through OpenAPI-compatible tool servers
- Uses standard REST/HTTP endpoints with OpenAPI schema
- Flow: User Prompt → OpenWebUI → LLM (Ollama/etc) → LLM decides to call tool → OpenWebUI Backend makes API call
- Stateless, request-response interaction
- Two types of tool servers:
  - **User Tool Servers**: Client-side requests from browser, can use localhost
  - **Global Tool Servers**: Server-side requests from OpenWebUI backend, for shared tools

### Model Context Protocol (MCP)
- Stateful, context-preserving protocol for AI agent interactions
- Uses client-server architecture with long-lived connections
- Typically communicates via stdio (standard input/output)
- Designed for rich, ongoing communication with complex environments
- Supports notifications, state management, and multi-step interactions
- **Critical**: OpenWebUI and Ollama DO NOT natively speak MCP protocol

### MCP vs OpenAPI
- **OpenAPI**: Stateless, request-response, REST-based, widely adopted standard
- **MCP**: Stateful, session-based, stdio-based, designed for AI agents
- Analogy: OpenAPI is like a vending machine (one request, one response), MCP is like an ongoing conversation

### MCP-to-OpenAPI Bridge (mcpo)
- OpenWebUI provides mcpo (MCP-to-OpenAPI proxy) to bridge the gap
- Exposes MCP servers through standard OpenAPI endpoints
- Auto-generates OpenAPI documentation
- Allows cloud-deployed OpenWebUI to access local MCP servers
- Benefits: security, scalability, compatibility with existing tools

### Architecture Pattern
- Bridge server sits between OpenWebUI and MCP server
- Exposes simple OpenAPI endpoints to OpenWebUI
- Manages complex stateful MCP communication on backend
- Translates between stateless REST and stateful MCP protocols

