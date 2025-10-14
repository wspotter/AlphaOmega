# AlphaOmega Quick Start Guide

## First Time Setup (10 minutes)

### 1. System Prerequisites

Make sure you have:
- AMD MI50 GPUs with ROCm installed
- Docker (ONLY for ComfyUI and Chatterbox TTS)
- Python 3.10+ and Node.js 18+ (for local services)
- At least 50GB free disk space (for models)

**Important**: See `DOCKER_POLICY.md` - only ComfyUI and Chatterbox TTS use Docker. All other services run locally.

### 2. Clone and Setup

```bash
# Clone repository
git clone https://github.com/wspotter/AlphaOmega.git
cd AlphaOmega

# Run automated setup (installs deps, pulls models, builds Docker images)
./scripts/setup.sh
```

The setup script will:
- ✅ Check system requirements (ROCm, Python, Node.js)
- ✅ Create directory structure
- ✅ Install local Python dependencies (OpenWebUI, Agent-S)
- ✅ Install Node.js dependencies (mcpart)
- ✅ Pull AI models (llava:34b, mistral, codellama)
- ✅ Build Docker containers (ComfyUI, Chatterbox only)

**Note**: Model downloads are large (~30GB total) and may take 15-30 minutes depending on your internet connection.

### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

**Key settings to verify:**

```bash
# GPU assignments (check with: rocm-smi --showid)
OLLAMA_GPU_VISION=1     # Vision/reasoning model (MI50 #1)
COMFYUI_GPU=2           # Image generation (MI50 #2) - DOCKER

# Safety settings
AGENT_SAFE_MODE=true    # Recommended for first use
```

### 4. Start Services

```bash
# Start all services
./scripts/start.sh

# Monitor startup (Ctrl+C to exit, services keep running)
./scripts/monitor.sh
```

Wait ~30 seconds for all services to initialize.

### 5. Access OpenWebUI

Open your browser to: **http://localhost:3000**

You should see the OpenWebUI interface!

## Your First Interactions

### Example 1: Test Vision (Computer Use)

In OpenWebUI, try:

```
What applications are currently open on my screen?
```

AlphaOmega will:
1. Detect this is a computer use request
2. Route to Agent-S
3. Capture your screen
4. Analyze with LLaVA 34B
5. Return description of visible applications

### Example 2: Generate an Image

```
Generate an image of a futuristic AI command center
```

AlphaOmega will:
1. Detect image generation intent
2. Route to ComfyUI on GPU 2
3. Generate image with SDXL
4. Display the result

### Example 3: Write Code

```
Write a Python function to validate email addresses with regex
```

AlphaOmega will:
1. Detect code generation intent
2. Route to CodeLlama on GPU 1
3. Generate working code with examples
4. Return formatted response

### Example 4: General Question

```
Explain how neural networks learn from data
```

AlphaOmega will:
1. Detect reasoning/explanation intent
2. Route to Mistral on GPU 1
3. Provide detailed explanation
4. Stream response in real-time

## Monitoring Your System

### Check GPU Usage

```bash
# Real-time GPU monitoring
watch -n 1 rocm-smi
```

You should see:
- GPU 0: ~14GB VRAM (LLaVA 34B)
- GPU 1: ~8GB VRAM (Mistral/CodeLlama)
- GPU 2: Variable (ComfyUI models loaded on demand)

### Check Service Health

```bash
# Check local services
curl http://localhost:8080                  # OpenWebUI
curl http://localhost:8001/health           # Agent-S
curl http://localhost:11434/api/tags        # Ollama
curl http://localhost:3000/health           # mcpart
curl http://localhost:8002/health           # mcpo

# Check Docker services (ComfyUI and Chatterbox only)
docker ps
curl http://localhost:8188/system_stats     # ComfyUI
curl http://localhost:5003/health           # Chatterbox TTS

# Check logs
tail -f logs/openwebui.log
tail -f logs/agent_actions.log
docker logs alphaomega-comfyui
docker logs alphaomega-chatterbox
```

### View Action Logs

```bash
# Computer use actions
tail -f logs/agent_actions.log

# Pipeline routing decisions
tail -f logs/pipeline.log
```

## Troubleshooting

### Services won't start

```bash
# Check ROCm
rocm-smi

# Check Docker (for ComfyUI/Chatterbox only)
docker --version
docker ps

# Check local services
ps aux | grep ollama
ps aux | grep open-webui
ps aux | grep "python.*agent_s"

# Check if ports are in use
sudo netstat -tulpn | grep -E '(8080|11434|11435|8188|8001|3000|8002|5003)'

# Restart everything
./scripts/stop.sh
./scripts/start.sh
```

### GPU not detected

```bash
# Check ROCm
rocm-smi

# Set MI50 compatibility
export HSA_OVERRIDE_GFX_VERSION=9.0.0

# Add to shell profile
echo 'export HSA_OVERRIDE_GFX_VERSION=9.0.0' >> ~/.bashrc
source ~/.bashrc
```

### Ollama models not loading

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags
curl http://localhost:11435/api/tags

# Manually pull models
ollama pull llava:34b
ollama pull mistral
ollama pull codellama:13b
```

### Agent-S can't capture screen

```bash
# Give Docker X11 access
xhost +local:docker

# Check display variable
echo $DISPLAY

# Test screenshot manually
scrot /tmp/test.png
```

## Next Steps

### 1. Explore Different Capabilities

Try these prompts in OpenWebUI:

**Vision & Computer Use:**
- "Take a screenshot and describe what you see"
- "What's the title of the active window?"
- "List all open applications"

**Image Generation:**
- "Generate a cyberpunk street scene"
- "Create an image of a sunset over mountains"
- "Draw a cat wearing sunglasses"

**Code Generation:**
- "Write a REST API endpoint in FastAPI"
- "Create a binary search algorithm in Python"
- "Write a React component for a login form"

**Analysis & Reasoning:**
- "Explain the difference between Docker and virtual machines"
- "What are the pros and cons of different database types?"
- "How does async/await work in Python?"

### 2. Customize Safety Settings

Edit `.env` to adjust permissions:

```bash
# Allow file operations (be careful!)
AGENT_ALLOW_FILE_WRITE=true
AGENT_ALLOWED_PATHS=/tmp,/home/stacy/Documents

# Allow application launching
AGENT_ALLOW_APP_LAUNCH=true
```

### 3. Monitor Performance

```bash
# Run monitoring dashboard
./scripts/monitor.sh
```

Watch how requests are distributed across GPUs.

### 4. Add Custom Workflows

Create custom ComfyUI workflows in:
```
comfyui_bridge/workflows/
```

### 5. Integrate MCP Server

Add mcpart submodule for advanced features:

```bash
git submodule add https://github.com/wspotter/mcpart agent_s/mcp/mcpart
```

## Stopping AlphaOmega

```bash
# Stop all services
./scripts/stop.sh
```

This stops:
- Docker containers (OpenWebUI, ComfyUI, Agent-S, MCP)
- Ollama services on GPUs

## Getting Help

### Check Logs

```bash
# Service logs
docker-compose logs -f [service-name]

# Application logs
tail -f logs/*.log
```

### Common Issues

1. **Out of VRAM**: Reduce model sizes or adjust GPU assignments
2. **Slow responses**: Check if models are kept loaded (OLLAMA_KEEP_ALIVE=-1)
3. **Connection refused**: Ensure all services are running (docker-compose ps)

### Resources

- OpenWebUI Docs: https://docs.openwebui.com
- Ollama Models: https://ollama.ai/library
- ComfyUI: https://github.com/comfyanonymous/ComfyUI
- ROCm: https://rocm.docs.amd.com

---

**You're ready to explore AlphaOmega!** 🔱

This is a powerful system running entirely on your hardware. Experiment, customize, and enjoy having enterprise-grade AI capabilities locally.
