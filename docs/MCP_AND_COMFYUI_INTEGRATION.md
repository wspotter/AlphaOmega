# MCP and ComfyUI Integration with OpenWebUI

**Date**: October 10, 2025  
**Research**: Complete integration documentation based on OpenWebUI source code

---

## Executive Summary

OpenWebUI has **native support** for both MCP (Model Context Protocol) servers and ComfyUI image generation. Both can be configured through the OpenWebUI Admin UI and work as independent services.

---

## MCP (Model Context Protocol) Integration

### What is MCP?

MCP is a protocol for connecting AI assistants to external tools and data sources. It allows:
- **Tools**: Function calling capabilities
- **Resources**: Access to files and data
- **Prompts**: Reusable prompt templates

### How OpenWebUI Connects to MCP Servers

OpenWebUI treats MCP servers as **Tool Servers** alongside OpenAPI servers.

#### Configuration Location
**Admin Settings → Tools → Tool Servers**

#### Connection Types
OpenWebUI supports MCP servers with multiple auth types:
- **None**: No authentication
- **Bearer**: Bearer token in header
- **Session**: Uses user's OpenWebUI session token
- **System OAuth**: OAuth token from external system
- **OAuth 2.1**: Full OAuth 2.1 flow (experimental)

#### How to Add MCP Server

1. **Via Admin UI**:
   - Navigate to Settings → Admin → Tools
   - Click "Add Connection"
   - Select Type: **MCP** (not OpenAPI)
   - Enter:
     - **URL**: `http://localhost:8002` (your MCP server)
     - **ID**: Required unique identifier (e.g., `filesystem`)
     - **Name**: Display name
     - **Description**: Optional
     - **Auth Type**: Select authentication method
     - **API Key**: If using bearer auth

2. **Via User Settings**:
   - Chat Settings → Tools → Manage Tool Servers
   - Same process as admin, but limited to user's own connections

#### MCP Server Implementation

OpenWebUI uses the official MCP Python SDK:
```python
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
```

**Connection Flow**:
1. OpenWebUI creates `MCPClient` instance
2. Connects via HTTP streaming transport
3. Calls `session.initialize()`
4. Discovers tools via `session.list_tools()`
5. Exposes tools in chat interface

**Tool Execution**:
- User selects MCP tools from Integrations menu
- OpenWebUI calls `session.call_tool(function_name, args)`
- Results returned to chat

#### Example: Running MCP Filesystem Server

```bash
# Install mcpo (MCP orchestrator)
pip install mcp

# Create artifacts directory
mkdir -p /home/stacy/AlphaOmega/artifacts

# Run MCP filesystem server via mcpo
uvx mcpo --port 8002 -- uvx mcp-server-filesystem /home/stacy/AlphaOmega/artifacts
```

**Then in OpenWebUI**:
- Admin → Tools → Add Connection
- Type: MCP
- URL: `http://localhost:8002`
- ID: `filesystem`
- Name: `File System Tools`
- Auth: None (for local dev)

#### Available MCP Servers

Popular MCP servers you can use:
- `mcp-server-filesystem` - File operations
- `mcp-server-memory` - Persistent key-value storage
- `mcp-server-git` - Git operations
- `mcp-server-postgres` - Database access
- Custom servers (build your own)

#### Code References

**Backend**: `backend/open_webui/utils/mcp/client.py`
```python
class MCPClient:
    async def connect(self, url: str, headers: Optional[dict] = None)
    async def list_tool_specs(self) -> Optional[dict]
    async def call_tool(self, function_name: str, function_args: dict)
    async def list_resources(self, cursor: Optional[str] = None)
    async def read_resource(self, uri: str)
```

**Configuration**: `backend/open_webui/routers/configs.py`
- `POST /configs/tool_servers` - Save MCP connections
- `POST /configs/tool_servers/verify` - Test connection

**Frontend**: `src/lib/components/AddToolServerModal.svelte`
- UI for adding/editing tool servers
- Supports both OpenAPI and MCP types

---

## ComfyUI Integration

### What is ComfyUI?

ComfyUI is a powerful node-based interface for Stable Diffusion that allows complex image generation workflows.

### How OpenWebUI Connects to ComfyUI

OpenWebUI has **built-in ComfyUI support** as one of its image generation engines (alongside DALL-E, Automatic1111, Gemini).

#### Configuration Location
**Admin Settings → Images**

#### Setup Steps

1. **Install ComfyUI Locally**:
```bash
# Clone ComfyUI
cd /opt  # or your preferred location
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install torch torchvision --index-url https://download.pytorch.org/whl/rocm6.2  # For AMD
pip install -r requirements.txt

# Download SDXL model
# Place checkpoint in: ComfyUI/models/checkpoints/

# Configure for AMD MI50 GPU2
export HSA_OVERRIDE_GFX_VERSION=9.0.0
export ROCR_VISIBLE_DEVICES=2

# Start ComfyUI server
python main.py --listen --port 8188
```

2. **Configure in OpenWebUI**:
   - Admin → Images → Image Settings
   - Enable: **Image Generation (Experimental)**
   - Engine: Select **ComfyUI**
   - ComfyUI Base URL: `http://localhost:8188`
   - ComfyUI API Key: (optional, leave empty for local)

3. **Export Workflow from ComfyUI**:
   - Design your workflow in ComfyUI web interface
   - Click **Save (API Format)** → `workflow.json`
   - Upload to OpenWebUI:
     - In Images settings, scroll to **ComfyUI Workflow**
     - Upload your `workflow.json` file
     - Configure workflow nodes (see below)

#### Workflow Node Configuration

OpenWebUI needs to know which nodes control what:

**Required Nodes**:
- **prompt***: Text prompt input (required)
- **negative_prompt**: Negative prompt (optional)
- **model**: Checkpoint selection
- **width**: Image width
- **height**: Image height
- **n**: Batch size (number of images)
- **steps**: Sampling steps
- **seed**: Random seed

**Configuration**:
For each node type, specify:
- **Node ID(s)**: Comma-separated ComfyUI node IDs (e.g., `6,7`)
- **Key**: Input parameter name (defaults: `text`, `width`, `height`, etc.)

**Example**:
```json
{
  "type": "prompt",
  "key": "text",
  "node_ids": ["6"]
}
```

#### Default Workflow

OpenWebUI includes a default SDXL workflow:
```json
{
  "3": {"class_type": "KSampler", ...},    // Sampler
  "4": {"class_type": "CheckpointLoaderSimple", ...},  // Model loader
  "6": {"class_type": "CLIPTextEncode", ...},  // Positive prompt
  "7": {"class_type": "CLIPTextEncode", ...},  // Negative prompt
  "8": {"class_type": "VAEDecode", ...},    // VAE decode
  "9": {"class_type": "SaveImage", ...}     // Save output
}
```

You can use this as a starting point and modify in ComfyUI.

#### Environment Variable (Alternative)

You can also set ComfyUI connection via environment variable:
```bash
export COMFYUI_BASE_URL=http://localhost:8188
```

OpenWebUI will automatically detect and use ComfyUI if this is set and engine is configured.

#### Usage in Chat

Once configured:
1. Type image generation prompt in chat
2. OpenWebUI detects image intent
3. Routes to ComfyUI automatically
4. Returns generated images

OR

Use explicit commands:
- "Generate an image of..."
- "Create a picture showing..."

#### Code References

**Backend**: `backend/open_webui/utils/images/comfyui.py`
```python
async def comfyui_generate_image(
    model: str, 
    payload: ComfyUIGenerateImageForm, 
    client_id, 
    base_url, 
    api_key
)
```

**Configuration**: `backend/open_webui/routers/images.py`
- `POST /images/config/update` - Save ComfyUI settings
- `GET /images/models` - List available models
- `POST /images/generations` - Generate images

**Environment Variables**:
- `COMFYUI_BASE_URL` - ComfyUI server URL
- `COMFYUI_API_KEY` - Optional API key
- `COMFYUI_WORKFLOW` - JSON workflow definition
- `IMAGE_GENERATION_ENGINE` - Set to `comfyui`

---

## Integration Strategy for AlphaOmega

### MCP Server Setup

**Goal**: Provide persistent artifacts and tool integration

**Recommended Approach**:
```bash
# 1. Install MCP tools
pip install mcp

# 2. Create directory structure
mkdir -p /home/stacy/AlphaOmega/artifacts
mkdir -p /home/stacy/AlphaOmega/mcp_memory

# 3. Create startup script
cat > /home/stacy/AlphaOmega/scripts/start-mcp.sh << 'EOF'
#!/bin/bash
cd /home/stacy/AlphaOmega
uvx mcpo --port 8002 -- \
    uvx mcp-server-filesystem /home/stacy/AlphaOmega/artifacts
EOF
chmod +x /home/stacy/AlphaOmega/scripts/start-mcp.sh

# 4. Start MCP server
./scripts/start-mcp.sh
```

**Then in OpenWebUI**:
- Admin → Tools → Add Connection
- Type: MCP
- URL: `http://localhost:8002`
- ID: `alphaomega-files`
- Name: `AlphaOmega File System`
- Auth: None

### ComfyUI Setup

**Goal**: Enable image generation on MI50 GPU2

**Installation**:
```bash
# 1. Install ComfyUI
cd /opt
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI

# 2. Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install torch torchvision --index-url https://download.pytorch.org/whl/rocm6.2
pip install -r requirements.txt

# 3. Download SDXL model
mkdir -p models/checkpoints
cd models/checkpoints
# Download from HuggingFace or Civitai
# Example: stabilityai/stable-diffusion-xl-base-1.0

# 4. Create startup script
cat > /home/stacy/AlphaOmega/scripts/start-comfyui.sh << 'EOF'
#!/bin/bash
export HSA_OVERRIDE_GFX_VERSION=9.0.0
export ROCR_VISIBLE_DEVICES=2  # MI50 GPU2
cd /opt/ComfyUI
source venv/bin/activate
python main.py --listen --port 8188
EOF
chmod +x /home/stacy/AlphaOmega/scripts/start-comfyui.sh

# 5. Start ComfyUI
./scripts/start-comfyui.sh
```

**OpenWebUI Configuration**:
- Admin → Images
- Enable Image Generation
- Engine: ComfyUI
- Base URL: `http://localhost:8188`
- Upload workflow.json (export from ComfyUI first)

### Agent-S Integration

**Current State**: 
Agent-S already has MCP client code in `agent_s/mcp/client.py`

**Integration Points**:
1. Agent-S can use MCP for artifact storage
2. Vision analysis results can be saved as artifacts
3. Action history can be persisted

**No changes needed** - Agent-S will work as optional module called by pipeline

### Pipeline Updates

**Goal**: Remove Docker networking, use localhost

**Changes Needed**:
```python
# In pipelines/alphaomega_router.py

class Valves(BaseModel):
    OLLAMA_HOST: str = Field(
        default="http://localhost:11434",  # Changed from host.docker.internal
        description="Ollama endpoint"
    )
    COMFYUI_HOST: str = Field(
        default="http://localhost:8188",   # Direct localhost
        description="ComfyUI endpoint"
    )
    AGENT_S_HOST: str = Field(
        default="http://localhost:8001",   # Direct localhost
        description="Agent-S endpoint"
    )
    # Remove MCP_HOST - OpenWebUI handles MCP tools directly
```

---

## Complete Local Architecture

```
┌─────────────────────────────────────────────────────┐
│      OpenWebUI (Port 8080)                          │
│      - Web interface                                │
│      - Built-in pipeline system                     │
│      - MCP tool integration (native)                │
│      - ComfyUI image generation (native)            │
└──────────────┬──────────────────────────────────────┘
               │
    ┌──────────┼──────────┬────────────┬──────────┐
    │          │          │            │          │
┌───▼──┐  ┌───▼────┐  ┌──▼─────┐  ┌─▼────┐  ┌──▼──────┐
│Ollama│  │ComfyUI │  │  MCP   │  │Agent-│  │Pipeline │
│GPU1  │  │ GPU2   │  │ Server │  │  S   │  │ Router  │
│:11434│  │ :8188  │  │ :8002  │  │:8001 │  │(Inside  │
│      │  │        │  │        │  │      │  │OpenWebUI│
│LLaVA │  │  SDXL  │  │mcpart  │  │Vision│  │         │
│      │  │  Flux  │  │  FS    │  │Mouse │  │         │
└──────┘  └────────┘  └────────┘  └──────┘  └─────────┘
```

### Service Startup Order

1. **Ollama** (Port 11434) - Start first
2. **ComfyUI** (Port 8188) - Start second  
3. **MCP Server** (Port 8002) - Start third
4. **OpenWebUI** (Port 8080) - Start after backends ready
5. **Agent-S** (Port 8001) - Optional, start when needed

### Configuration Files

**OpenWebUI Environment**:
```bash
# Add to your shell profile or .env
export OLLAMA_BASE_URL=http://localhost:11434
export COMFYUI_BASE_URL=http://localhost:8188
export ENABLE_IMAGE_GENERATION=true
export IMAGE_GENERATION_ENGINE=comfyui
```

**AlphaOmega .env**:
```bash
# Already updated in this repo
OLLAMA_HOST=http://localhost:11434
COMFYUI_HOST=http://localhost:8188
AGENT_S_HOST=http://localhost:8001
# MCP is configured in OpenWebUI UI, not here
```

---

## Testing Checklist

### MCP Integration Test
- [ ] MCP server running at localhost:8002
- [ ] Added in OpenWebUI Admin → Tools
- [ ] Tools appear in chat Integrations menu
- [ ] Can enable MCP tools for a chat
- [ ] Tool execution works (e.g., create file)
- [ ] Results appear in chat

### ComfyUI Integration Test
- [ ] ComfyUI running at localhost:8188
- [ ] Configured in OpenWebUI Admin → Images
- [ ] Engine set to ComfyUI
- [ ] Workflow uploaded and nodes configured
- [ ] Can generate image from chat
- [ ] Image appears in chat response
- [ ] Multiple images work (n > 1)

### Agent-S Test
- [ ] Agent-S server runs successfully
- [ ] Can capture screenshots
- [ ] Vision analysis works (LLaVA)
- [ ] Can be called from pipeline
- [ ] MCP client in Agent-S works (optional)

### Pipeline Test
- [ ] Pipeline loaded in OpenWebUI
- [ ] Intent detection works
- [ ] Routes to correct backend
- [ ] Localhost endpoints work (no Docker)
- [ ] Streaming responses work

---

## Key Insights

### What We Learned

1. **MCP is First-Class in OpenWebUI**
   - Native MCP support since recent versions
   - Treated same as OpenAPI tool servers
   - Full protocol implementation via official SDK
   - Supports multiple auth methods

2. **ComfyUI is Built-In**
   - One of 4 image generation engines
   - Workflow support with node mapping
   - WebSocket communication for streaming
   - Model selection from ComfyUI server

3. **No Custom Code Needed**
   - OpenWebUI handles all integration
   - Just configure endpoints and credentials
   - Pipeline can focus on intent detection
   - Agent-S is optional enhancement

4. **Local Deployment is Simple**
   - All services run independently
   - Connect via localhost URLs
   - No Docker networking complexity
   - Easy to debug and monitor

### Common Pitfalls to Avoid

1. **MCP Server Type**
   - Must select "MCP" not "OpenAPI" when adding
   - ID field is required for MCP
   - Auth type matters (use "None" for local dev)

2. **ComfyUI Workflow**
   - Must export as "API Format" not "Save"
   - Node IDs must match your workflow
   - Prompt node is required (marked with *)
   - Test workflow in ComfyUI first

3. **GPU Assignment**
   - Set `ROCR_VISIBLE_DEVICES` for each service
   - ComfyUI needs dedicated GPU
   - Ollama can share GPU but may need unload/load

4. **Port Conflicts**
   - Check all ports are available
   - Default ports: 8080 (OpenWebUI), 11434 (Ollama), 8188 (ComfyUI), 8002 (MCP)
   - Use `lsof -i :PORT` to check

---

## Next Steps

With this research complete, we can now:

1. **Create Installation Scripts**
   - `scripts/setup-local.sh` - Install all components
   - `scripts/start-local.sh` - Start all services
   - `scripts/stop-local.sh` - Stop all services

2. **Update Documentation**
   - Rewrite README.md for local setup
   - Update copilot-instructions.md
   - Add troubleshooting guide

3. **Simplify Pipeline**
   - Remove Docker networking
   - Use localhost endpoints
   - Remove MCP client code (OpenWebUI handles it)

4. **Test Full Stack**
   - Local installation
   - Service startup
   - Integration testing
   - Performance benchmarking

---

## Resources

### Official Documentation
- **MCP Protocol**: https://modelcontextprotocol.io/
- **MCP Python SDK**: https://github.com/modelcontextprotocol/python-sdk
- **ComfyUI**: https://github.com/comfyanonymous/ComfyUI
- **OpenWebUI**: https://github.com/open-webui/open-webui

### OpenWebUI Source References
- MCP Client: `backend/open_webui/utils/mcp/client.py`
- Tool Management: `backend/open_webui/routers/tools.py`
- Image Generation: `backend/open_webui/routers/images.py`
- ComfyUI Utils: `backend/open_webui/utils/images/comfyui.py`
- Config Management: `backend/open_webui/routers/configs.py`

### Community Resources
- OpenWebUI Discord: https://discord.gg/5rJgQTnV4s
- MCP Servers List: https://github.com/modelcontextprotocol/servers
- ComfyUI Workflows: https://comfyworkflows.com/

---

**End of Research Document**

*This document provides complete guidance for integrating MCP and ComfyUI with OpenWebUI in a local deployment.*
