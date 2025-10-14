# OpenWebUI Integration Guide - Code Examples

This directory contains all the code examples and resources from the comprehensive guide "Integrating External Tools with OpenWebUI: A Deep Dive into OpenAPI and the MCP Bridge Pattern".

## Files Included

### Documentation
- **openwebui_integration_guide.md** - The complete developer's guide
- **README.md** - This file with setup instructions

### Code Examples
- **weather_tool_server.py** - Simple OpenAPI tool server example
- **mock_mcp_client.py** - Mock MCP client for demonstration
- **mcp_bridge_server.py** - Complete MCP-to-OpenAPI bridge server

### Diagrams
- **mcp_bridge_diagram.mmd** - Mermaid source for the architecture diagram
- **mcp_bridge_diagram.png** - Rendered architecture diagram

### Generated Files
- **weather_openapi.json** - OpenAPI schema from the weather server
- **bridge_openapi.json** - OpenAPI schema from the bridge server

## Quick Start

### Prerequisites

```bash
pip install fastapi uvicorn pydantic
```

### Running the Weather Tool Server

```bash
python weather_tool_server.py
```

The server will start on `http://localhost:8000`

**Test it:**
```bash
curl -X POST http://localhost:8000/get_weather \
  -H "Content-Type: application/json" \
  -d '{"city": "Tokyo"}'
```

**View OpenAPI docs:** http://localhost:8000/docs

### Running the MCP Bridge Server

```bash
python mcp_bridge_server.py
```

The server will start on `http://localhost:8001`

**Test it:**
```bash
curl -X POST http://localhost:8001/execute_cua_command \
  -H "Content-Type: application/json" \
  -d '{"command": "list files"}'
```

**View OpenAPI docs:** http://localhost:8001/docs

## Connecting to OpenWebUI

### For User Tool Servers (Client-side)

1. Open OpenWebUI in your browser
2. Go to **⚙️ Settings**
3. Click **➕ Tools**
4. Enter the tool server URL (e.g., `http://localhost:8000`)
5. Click **Save**

### For Global Tool Servers (Server-side)

1. Open OpenWebUI as an admin
2. Go to **Admin Settings > Tools**
3. Add the tool server URL
4. Configure user permissions as needed

## Architecture Overview

The bridge pattern allows OpenWebUI (which speaks OpenAPI) to communicate with MCP servers (which use a different protocol):

```
OpenWebUI → HTTP/REST → Bridge Server → stdio → MCP Server
                         ↑
                    Maintains state
                    Translates protocols
```

See `mcp_bridge_diagram.png` for a detailed visual representation.

## Key Concepts

### OpenAPI Integration (Native)
- Stateless request-response
- Standard HTTP/REST endpoints
- Automatic schema discovery
- Works out of the box with OpenWebUI

### MCP Integration (via Bridge)
- Stateful session management
- stdio-based communication
- Requires bridge server
- Enables complex, multi-step workflows

## Testing the Examples

### Weather Server Tests

```bash
# Get weather for Tokyo
curl -X POST http://localhost:8000/get_weather \
  -H "Content-Type: application/json" \
  -d '{"city": "Tokyo"}'

# Get weather for London
curl -X POST http://localhost:8000/get_weather \
  -H "Content-Type: application/json" \
  -d '{"city": "London"}'

# Retrieve OpenAPI schema
curl http://localhost:8000/openapi.json
```

### Bridge Server Tests

```bash
# List files
curl -X POST http://localhost:8001/execute_cua_command \
  -H "Content-Type: application/json" \
  -d '{"command": "list files"}'

# Read a file
curl -X POST http://localhost:8001/execute_cua_command \
  -H "Content-Type: application/json" \
  -d '{"command": "read file notes.md"}'

# Get MCP state
curl http://localhost:8001/mcp_state

# Retrieve OpenAPI schema
curl http://localhost:8001/openapi.json
```

## Troubleshooting

### Tool Not Being Called
- Ensure you're using a model that supports function calling (e.g., GPT-4)
- Set Function Calling to "Native" in Chat Controls > Advanced Params
- Make your prompts clear and specific

### Connection Errors
- Check that the server is running: `curl http://localhost:8000/`
- Verify no port conflicts: `netstat -tuln | grep 8000`
- For Global tools, ensure the backend can reach the URL

### CORS Issues (for User Tool Servers)
Add CORS middleware to your FastAPI app:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Next Steps

1. Read the complete guide in `openwebui_integration_guide.md`
2. Modify the examples to suit your needs
3. Build your own tool servers
4. Explore the OpenWebUI community for more examples

## Resources

- [OpenWebUI Documentation](https://docs.openwebui.com/)
- [OpenAPI Specification](https://swagger.io/specification/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## License

These examples are provided for educational purposes. Feel free to use and modify them for your projects.

