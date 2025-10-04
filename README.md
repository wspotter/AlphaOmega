# AlphaOmega 🔱

> **The Ultimate Local AI Orchestration Platform**
> 
> Multi-GPU AI system combining vision, reasoning, image generation, and computer use automation - all running locally on AMD MI50 GPUs.

## Overview

AlphaOmega is a unified AI platform that brings together multiple cutting-edge capabilities:

- 🧠 **Multi-Model LLM Inference** - LLaVA 34B (vision), Mistral (reasoning), CodeLlama (code generation)
- 🎨 **Image Generation** - ComfyUI with SDXL/Flux workflows
- 🖥️ **Computer Use Automation** - AI-powered screen analysis and action execution
- 🔧 **Tool Integration** - MCP server for artifacts, memory, and file operations
- 🌐 **Unified Interface** - Single OpenWebUI portal for all interactions

### Why AlphaOmega?

- **Privacy-First**: Everything runs locally - no cloud APIs, no data leaving your machine
- **Powerful Hardware**: Leverages 3× AMD MI50 GPUs (144GB VRAM total) for enterprise-grade performance
- **Intelligent Routing**: Automatically routes requests to the appropriate backend
- **Safety Built-In**: Action validation and permissions system prevents dangerous operations
- **Production-Ready**: Docker orchestration, health checks, logging, and monitoring

## Quick Start

### Prerequisites

- **Hardware**: AMD MI50 GPUs (or other ROCm-compatible GPUs)
- **Software**: 
  - ROCm 6.0+ ([installation guide](https://rocm.docs.amd.com/))
  - Docker & Docker Compose
  - Git

### Installation

```bash
# Clone repository
git clone https://github.com/wspotter/AlphaOmega.git
cd AlphaOmega

# Run setup script (installs dependencies, pulls models, builds containers)
./scripts/setup.sh

# Configure your GPU assignments
nano .env  # Edit GPU IDs to match your system

# Start all services
./scripts/start.sh
```

### Access

- **OpenWebUI**: http://localhost:3000 - Main interface
- **Agent-S API**: http://localhost:8001 - Computer use automation
- **ComfyUI**: http://localhost:8188 - Image generation
- **Ollama Vision**: http://localhost:11434 - LLaVA inference
- **Ollama Reasoning**: http://localhost:11435 - Mistral/CodeLlama

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  OpenWebUI (Port 3000)                       │
│              [Unified User Interface]                        │
└────────────────────┬────────────────────────────────────────┘
                     │
          ┌──────────┴──────────┐
          │  Pipeline Router    │
          │  (Intent Detection) │
          └──────────┬──────────┘
                     │
     ┌───────────────┼───────────────┐
     │               │               │
┌────▼─────┐  ┌─────▼──────┐  ┌────▼─────┐  ┌──────────┐
│  Ollama  │  │  ComfyUI   │  │ Agent-S  │  │   MCP    │
│ MI50 0,1 │  │  MI50 #2   │  │ Computer │  │  Server  │
│          │  │            │  │   Use    │  │          │
│ LLaVA    │  │   SDXL     │  │  Vision  │  │Artifacts │
│ Mistral  │  │   Flux     │  │  Actions │  │ Memory   │
│CodeLlama │  │ControlNet  │  │  Safety  │  │  Files   │
└──────────┘  └────────────┘  └──────────┘  └──────────┘
```

### GPU Distribution

```yaml
MI50 GPU 0 (48GB): Ollama Vision - llava:34b
MI50 GPU 1 (48GB): Ollama Reasoning - mistral, codellama:13b
MI50 GPU 2 (48GB): ComfyUI - SDXL, Flux, ControlNet
RX 6600XT (8GB):   Display output only
```

## Features

### 1. Multi-Modal Conversation

Chat naturally and AlphaOmega automatically routes your request:

- **"What's on my screen?"** → Agent-S captures screenshot, LLaVA analyzes
- **"Generate an image of a futuristic city"** → ComfyUI with SDXL
- **"Write a Python function to parse JSON"** → CodeLlama on GPU 1
- **"Remember this for later"** → MCP server memory

### 2. Computer Use Automation

AI-powered control of your desktop:

```
User: "Take a screenshot and click on the Firefox icon"

AlphaOmega:
1. Captures screen
2. Analyzes with LLaVA 34B
3. Locates Firefox icon
4. Validates action safety
5. Executes mouse click
6. Returns confirmation
```

### 3. Image Generation

High-quality image generation with ComfyUI:

- SDXL workflows for photorealistic images
- Flux for artistic generation
- ControlNet for precise control
- Custom workflows support

### 4. Intelligent Code Generation

CodeLlama 13B optimized for programming:

- Multi-language support
- Context-aware completions
- Refactoring and optimization
- Bug detection and fixes

## Usage Examples

### Basic Chat

```
You: Explain quantum computing
AlphaOmega: [Routes to Mistral on GPU 1]
[Detailed explanation...]
```

### Computer Use

```
You: What applications are currently open?
AlphaOmega: [Routes to Agent-S]
[Captures screenshot, analyzes with LLaVA]

I can see the following applications:
- Firefox (top-left)
- VS Code (center)
- Terminal (bottom)
```

### Image Generation

```
You: Generate an image of a cyberpunk street at night
AlphaOmega: [Routes to ComfyUI on GPU 2]
[Generates image with SDXL]
✅ Image generated successfully!
[Displays image]
```

### Code Generation

```
You: Write a FastAPI endpoint to handle file uploads
AlphaOmega: [Routes to CodeLlama on GPU 1]
[Generates complete, production-ready code]
```

## Configuration

### Environment Variables

Key settings in `.env`:

```bash
# GPU Assignments
OLLAMA_GPU_0=0          # Vision model GPU
OLLAMA_GPU_1=1          # Reasoning/code GPU
COMFYUI_GPU=2           # Image generation GPU

# Models
VISION_MODEL=llava:34b
REASONING_MODEL=mistral
CODE_MODEL=codellama:13b

# Safety
AGENT_SAFE_MODE=true
AGENT_ALLOW_FILE_WRITE=false
AGENT_ALLOW_SYSTEM_COMMANDS=false
```

### Safety Configuration

Edit `config/permissions/agent_permissions.yaml`:

```yaml
mouse_actions:
  enabled: true
  
keyboard_actions:
  enabled: true
  dangerous_hotkeys:
    - "ctrl+alt+delete"
    - "alt+f4"
  
file_operations:
  enabled: false  # Disabled by default
  allowed_paths:
    - /tmp
    - /home/*/Downloads
  
system_commands:
  enabled: false  # Disabled by default
```

## Management

### Starting Services

```bash
./scripts/start.sh
```

### Stopping Services

```bash
./scripts/stop.sh
```

### Monitoring

```bash
./scripts/monitor.sh
```

Shows real-time:
- GPU utilization (rocm-smi)
- Loaded models
- Service health
- API availability

### Logs

```bash
# All logs
docker-compose logs -f

# Specific service
docker-compose logs -f agent-s
docker-compose logs -f openwebui

# Local logs
tail -f logs/agent_actions.log    # Agent-S actions
tail -f logs/pipeline.log          # Routing decisions
```

## Development

### Project Structure

```
AlphaOmega/
├── pipelines/                   # OpenWebUI pipelines
│   └── alphaomega_router.py     # Main routing logic
├── agent_s/                     # Computer use automation
│   ├── server.py                # FastAPI server
│   ├── vision/                  # LLaVA integration
│   ├── actions/                 # Mouse, keyboard, screen
│   ├── mcp/                     # MCP client
│   └── safety/                  # Action validation
├── comfyui_bridge/              # ComfyUI integration
│   ├── workflows/               # Workflow definitions
│   └── api.py                   # API wrapper
├── config/                      # Configuration files
├── scripts/                     # Management scripts
└── docker-compose.yml           # Service orchestration
```

### Adding New Capabilities

#### New Pipeline Route

Edit `pipelines/alphaomega_router.py`:

```python
def _detect_intent(self, message: str) -> str:
    if "your keyword" in message.lower():
        return "new_backend"
    # ... existing code
```

#### New Agent Action

Create `agent_s/actions/new_action.py`:

```python
class NewAction:
    def execute(self, params):
        # Implementation
        return {"success": True}
```

#### New ComfyUI Workflow

Add JSON workflow to `comfyui_bridge/workflows/`.

## Performance

### Benchmarks (MI50 Hardware)

| Task | Model | GPU | Latency | VRAM |
|------|-------|-----|---------|------|
| Screen Analysis | LLaVA 34B | 0 | ~3-4s | 14GB |
| Code Generation | CodeLlama 13B | 1 | ~2-3s | 7GB |
| Reasoning | Mistral | 1 | ~1-2s | 4GB |
| Image Gen (SDXL) | ComfyUI | 2 | ~15-20s | 12GB |

### Optimization Tips

1. **Keep models loaded**: `OLLAMA_KEEP_ALIVE=-1`
2. **Resize screenshots**: Scale to 1280x720 before vision analysis
3. **Use region analysis**: Crop to relevant areas for faster processing
4. **Parallel inference**: GPU 0 (vision) + GPU 1 (planning) can run simultaneously

## Troubleshooting

### Ollama Not Detecting GPUs

```bash
# Check ROCm
rocm-smi

# Set MI50 compatibility
export HSA_OVERRIDE_GFX_VERSION=9.0.0

# Restart Ollama
pkill ollama
ollama serve
```

### Agent-S Can't Capture Screen

```bash
# Check X11 permissions
xhost +local:docker

# Or for Wayland
# Ensure /run/user/1000 is mounted in container
```

### ComfyUI Out of Memory

```bash
# Reduce image resolution
# Or allocate more VRAM to GPU 2
export PYTORCH_HIP_ALLOC_CONF=garbage_collection_threshold:0.8
```

## Roadmap

- [ ] Advanced action planning with multi-step reasoning
- [ ] Voice input/output integration
- [ ] Web browsing automation
- [ ] Document analysis and processing
- [ ] Multi-monitor support
- [ ] Cloud sync for artifacts (optional)
- [ ] Mobile companion app

## Contributing

This is a private project, but suggestions and improvements are welcome!

## License

Private use only.

## Acknowledgments

Built on top of:
- [OpenWebUI](https://github.com/open-webui/open-webui)
- [Ollama](https://ollama.ai)
- [ComfyUI](https://github.com/comfyanonymous/ComfyUI)
- [LLaVA](https://llava-vl.github.io/)
- ROCm and AMD GPU ecosystem

---

**AlphaOmega** - Where local AI meets desktop automation. 🔱
