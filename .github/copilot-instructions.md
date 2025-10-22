# AlphaOmega - AI Coding Assistant Instructions

## Project Overview

AlphaOmega is a unified local AI orchestration platform that combines:
- **OpenWebUI** - Single web interface for all AI interactions
- **Ollama + LLaVA** - Multi-model LLM inference (vision, reasoning, code) on AMD MI50 GPUs
- **ComfyUI** - Advanced image generation (SDXL, Flux workflows)
- **Agent-S** - Computer use automation (screen analysis, mouse/keyboard control)
- **MCP Server (mcpart)** - Persistent artifacts, memory, and file operations

**Hardware**: 3× AMD MI50 (48GB each) + AMD RX 6600XT (display)
**Philosophy**: Everything runs locally, no cloud dependencies, privacy-first design

## Architecture

### System Flow
```
User → OpenWebUI (Port 8080) → Pipeline Router (Intent Detection)
  ↓
  ├─> Ollama GPU 0 (llava:34b) - Vision analysis
  ├─> Ollama GPU 1 (mistral/codellama) - Reasoning/code
  ├─> ComfyUI GPU 2 (SDXL/Flux) - Image generation [LOCAL]
  ├─> Agent-S (Computer use) - Screen/mouse/keyboard [LOCAL]
  ├─> Chatterbox TTS (port 5003) - Text-to-speech [LOCAL]
  └─> MCP Server (mcpart) - Artifacts/memory/files [LOCAL]
```

### GPU Distribution
```yaml
MI50_0 (48GB): Ollama Vision - llava:34b (port 11434)
MI50_1 (48GB): Ollama Reasoning - mistral, codellama:13b (port 11435)
MI50_2 (48GB): ComfyUI - SDXL, Flux image generation (port 8188)
RX6600XT (8GB): Display output only (not used for AI)
```

### Key Design Decisions

**Why OpenWebUI as orchestrator?**
- Single unified interface (no context switching)
- Built-in pipeline system for intelligent routing
- Active development, ComfyUI integration support
- Streaming responses and great UX
- **Runs locally** - No Docker, direct Python execution

**Why separate Agent-S service (LOCAL)?**
- Needs host network access for X11/Wayland
- Requires privileged mode for input control
- Isolates potentially risky computer use actions
- Independent FastAPI server for direct API access
- **Must run locally** - Needs direct display/input access

**Why integrate mcpart MCP server (LOCAL)?**
- Persistent memory across sessions
- Artifact creation/management (code, documents)
- File operations with safety validation
- Extensible tool system
- **Must run locally** - Needs direct filesystem access

## Development Setup

### Prerequisites
```bash
# ROCm for AMD GPUs (MI50 requires gfx906 support)
sudo apt install rocm-dkms rocm-libs
export HSA_OVERRIDE_GFX_VERSION=9.0.0

# Verify GPU access
rocm-smi --showid
```

### Initial Setup
```bash
git clone https://github.com/wspotter/AlphaOmega.git
cd AlphaOmega

# Run automated setup (installs deps, pulls models)
./scripts/setup.sh

# Configure GPU assignments
cp .env.example .env
nano .env  # Edit GPU IDs to match your system

# Start all services (all local)
./scripts/start.sh

# Monitor status
./scripts/monitor.sh
```

### Verify Installation
```bash
# Check local services
curl http://localhost:8080                  # OpenWebUI
curl http://localhost:8001/health           # Agent-S
curl http://localhost:11434/api/tags        # Ollama Vision
curl http://localhost:11435/api/tags        # Ollama Reasoning
curl http://localhost:8002/openapi.json     # MCP Tool Server (mcpart via mcpo)
curl http://localhost:8188/system_stats     # ComfyUI
curl http://localhost:5003/health           # Chatterbox TTS

# Check GPU usage
rocm-smi --showuse --showmeminfo vram
```

## Development Workflow

### Running in Development Mode
```bash
# Run Ollama locally
ROCR_VISIBLE_DEVICES=0 OLLAMA_HOST=127.0.0.1:11434 ollama serve &
ROCR_VISIBLE_DEVICES=1 OLLAMA_HOST=127.0.0.1:11435 ollama serve &

# Run OpenWebUI locally
cd /home/stacy/AlphaOmega
source venv/bin/activate
open-webui serve --port 8080 &

# Run Agent-S locally
cd agent_s
python server.py &

# Run unified MCP tool server locally
cd /home/stacy/AlphaOmega/mcpart
npm run build
$HOME/.local/bin/uvx mcpo --port 8002 -- node build/index.js &

# Run ComfyUI locally
cd comfyui_bridge
python main.py &

# Run Chatterbox TTS locally
cd tts
python chatterbox_server.py &
```

### Testing Components

**Test Vision Analysis:**
```bash
# Capture test screenshot
scrot /tmp/test.png

# Test with LLaVA directly
curl -X POST http://localhost:11434/api/generate \
  -d '{"model":"llava:34b","prompt":"Describe this image","images":["'$(base64 -w0 /tmp/test.png)'"]}'

# Test through Agent-S API
curl -X POST http://localhost:8001/action \
  -H "Content-Type: application/json" \
  -d '{"prompt":"What applications are open?","safe_mode":true}'
```

**Test Pipeline Routing:**
```bash
# Check routing logs
tail -f logs/pipeline.log

# Test different intents
echo "Test vision: What's on my screen?"
echo "Test image gen: Generate a sunset image"
echo "Test code: Write a Python sorting function"
```

## Code Conventions

### Pipeline Development Pattern
All OpenWebUI pipelines in `pipelines/` follow this structure:

```python
class Pipeline:
    class Valves(BaseModel):
        # Configuration - editable from OpenWebUI UI
        SETTING: str = Field(default="value", description="Help text")
    
    def __init__(self):
        self.name = "Pipeline Name"
        self.valves = self.Valves()
    
    async def pipe(self, body: Dict, __user__: Optional[Dict] = None, 
                   __event_emitter__: Any = None) -> AsyncGenerator[str, None]:
        # Main routing logic with streaming
        intent = self._detect_intent(body["messages"][-1]["content"])
        async for chunk in self._route_to_backend(intent):
            yield chunk
```

### Agent-S Action Pattern
All actions in `agent_s/actions/` follow this interface:

```python
class ActionHandler:
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute action and return result"""
        # Implementation
        return {"success": True, "result": "..."}
```

### Vision Analysis Pattern
```python
from agent_s.vision.analyzer import VisionAnalyzer

vision = VisionAnalyzer(model="llava:34b")

# Full screen analysis
result = await vision.analyze(
    image_path="/tmp/screenshot.png",
    prompt="List all visible applications"
)

# Region analysis (faster, more accurate)
result = vision.analyze_region(
    image_path="/tmp/screenshot.png",
    x=100, y=100, w=400, h=300,
    prompt="What button is at this location?"
)
```

### MCP Integration Pattern
```python
from agent_s.mcp.client import MCPClient

mcp = MCPClient()

# Create artifact
await mcp.create_artifact(
    content="Generated code",
    artifact_type="code",
    title="Script",
    language="python"
)

# Save to memory
await mcp.save_to_memory("last_action", {"timestamp": "...", "result": "..."})

# Read from memory
data = await mcp.read_from_memory("last_action")
```

## Testing Strategy

### Unit Tests
```bash
pytest tests/unit/test_vision.py
pytest tests/unit/test_actions.py
pytest tests/unit/test_safety.py
```

### Integration Tests (requires services running)
```bash
./scripts/start.sh
pytest tests/integration/
```

### Performance Benchmarks
```bash
python tests/benchmarks/benchmark_vision.py --model llava:34b
python tests/benchmarks/benchmark_pipeline.py --scenario computer_use
```

## Key Files & Directories

```
```
AlphaOmega/
├── .env                         # Configuration (GPU IDs, ports, safety settings)
│
├── pipelines/
│   └── alphaomega_router.py     # Main router: intent detection + backend routing
│
├── agent_s/
│   ├── server.py                # FastAPI server (computer use coordination)
│   ├── vision/
│   │   └── analyzer.py          # LLaVA integration for screen analysis
│   ├── actions/
│   │   ├── screen.py            # Screenshot capture (mss/pyautogui/scrot)
│   │   ├── mouse.py             # Mouse control (pyautogui)
│   │   └── keyboard.py          # Keyboard input (pyautogui)
│   ├── mcp/
│   │   └── client.py            # MCP server client (artifacts, memory, files)
│   └── safety/
│       └── validator.py         # Action safety validation (prevent dangerous ops)
│
├── comfyui_bridge/
│   ├── main.py                  # Local ComfyUI server
│   └── workflows/               # ComfyUI workflow JSON definitions
│
├── tts/
│   └── chatterbox_server.py     # Local Chatterbox TTS server
│
```
├── config/
│   ├── models/                  # Model configs per GPU
│   └── permissions/             # Agent action permissions
│
├── scripts/
│   ├── setup.sh                 # Automated setup (deps, models, build)
│   ├── start.sh                 # Start all services
│   ├── stop.sh                  # Stop all services
│   └── monitor.sh               # Real-time status monitoring
│
└── logs/
    ├── pipeline.log             # Routing decisions
    ├── agent_actions.log        # Computer use actions
    └── *.log                    # Service logs
```

## External Dependencies

### Running Services
- **OpenWebUI** (8080): Web interface [LOCAL]
- **Ollama Vision** (11434): LLaVA 34B on MI50 GPU 0 [LOCAL]
- **Ollama Reasoning** (11435): Mistral/CodeLlama on MI50 GPU 1 [LOCAL]
- **ComfyUI** (8188): SDXL/Flux on MI50 GPU 2 [LOCAL]
- **Agent-S** (8001): Computer use automation [LOCAL]
- **MCP Tool Server (mcpart via mcpo)** (8002): Filesystem + business tools [LOCAL]
- **Chatterbox TTS** (5003): Text-to-speech [LOCAL]

### Python Packages (requirements.txt)
```
fastapi, uvicorn        # Agent-S server
ollama                  # Ollama API client
pyautogui, python-mss   # Screen capture, mouse/keyboard
pillow, opencv-python   # Image processing
httpx, aiohttp          # HTTP clients
pydantic                # Data validation
```

### Git Submodules
```bash
# Add mcpart as submodule (if using)
git submodule add https://github.com/wspotter/mcpart mcpart
```

## Common Tasks

### Add New Pipeline Route
Edit `pipelines/alphaomega_router.py`:

```python
def _detect_intent(self, message: str) -> str:
    if "new keyword" in message.lower():
        return "new_backend"
    # ... existing code

async def _route_to_new_backend(self, message, messages, event_emitter):
    # Implementation
    yield "Response..."
```

### Add New Agent Action
Create `agent_s/actions/new_action.py`:

```python
class NewAction:
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Implementation
        return {"success": True}
```

Register in `agent_s/server.py`:
```python
new_action = NewAction()
# Use in action execution loop
```

### Debug Vision Analysis
```bash
export VISION_DEBUG=true
export SAVE_DEBUG_IMAGES=true

# Restart Agent-S locally
pkill -f "python.*agent_s/server.py"
cd agent_s && python server.py &

# Check debug output
tail -f logs/agent_actions.log
ls /tmp/agent_screenshots/
```

### Monitor Pipeline Routing
```bash
export PIPELINE_LOG_LEVEL=DEBUG

# Restart OpenWebUI locally
pkill -f "open-webui serve"
cd /home/stacy/AlphaOmega
source venv/bin/activate
open-webui serve --port 8080 &

tail -f logs/pipeline.log | grep "intent:"
```

### Optimize Model Performance
```bash
# Keep models loaded in memory (no reload delays)
export OLLAMA_KEEP_ALIVE=-1

# Adjust per-GPU memory allocation in .env
LLAVA_MEMORY_LIMIT=40     # Leave 8GB free on MI50
MISTRAL_MEMORY_LIMIT=8
CODELLAMA_MEMORY_LIMIT=8
```

## ROCm Specific Notes

### MI50 Compatibility
```bash
# MI50 reports as gfx906, needs architecture override
export HSA_OVERRIDE_GFX_VERSION=9.0.0

# Add to .bashrc for persistence
echo 'export HSA_OVERRIDE_GFX_VERSION=9.0.0' >> ~/.bashrc
```

### GPU Device Assignment
```bash
# List GPUs with IDs
rocm-smi --showid

# Assign specific GPU to process
ROCR_VISIBLE_DEVICES=0 ollama serve      # Use GPU 0
ROCR_VISIBLE_DEVICES=1 ollama serve      # Use GPU 1
ROCR_VISIBLE_DEVICES=0,1 python app.py   # Use GPU 0 and 1
```

### Troubleshooting ROCm
```bash
# Check GPU detection
rocm-smi

# Verify GPU access for all services
ROCR_VISIBLE_DEVICES=0 ollama ps
ROCR_VISIBLE_DEVICES=1 ollama ps
ROCR_VISIBLE_DEVICES=2 python -c "import torch; print('GPU available:', torch.cuda.is_available())"
```

## Safety Considerations

### Agent-S Safe Mode
```bash
# Enable safe mode (requires confirmation for risky actions)
AGENT_SAFE_MODE=true

# Actions that trigger validation:
# - File system writes outside /tmp
# - System command execution
# - Application launches
# - Dangerous hotkeys (Ctrl+Alt+Del, Alt+F4, etc.)
```

### Action Logging
All Agent-S actions are logged:
```bash
tail -f logs/agent_actions.log
# Format: timestamp | action_type | params | result | safety_check
```

### Configurable Permissions
Edit `.env`:
```bash
AGENT_ALLOW_FILE_WRITE=false        # Disable file operations
AGENT_ALLOW_SYSTEM_COMMANDS=false   # Disable system commands
AGENT_ALLOW_APP_LAUNCH=true         # Allow app launching
AGENT_ALLOWED_PATHS=/tmp,~/Downloads  # Restrict file access
```

## Performance Tips

1. **Keep Models Loaded**: `OLLAMA_KEEP_ALIVE=-1` prevents reload delays (~5-10s)
2. **Resize Screenshots**: Scale to 1280x720 before vision analysis (2-3x faster, similar accuracy)
3. **Region Analysis**: Use `analyze_region()` for UI elements instead of full screen
4. **Parallel Inference**: GPU 0 (vision) and GPU 1 (reasoning) can run simultaneously
5. **ComfyUI Cache**: Enable model caching to speed up repeated generations

## Integration Points

### OpenWebUI ↔ Agent-S
- OpenWebUI pipeline detects computer use intent
- Routes to Agent-S API at http://localhost:8001/action
- Agent-S streams back results with screenshots

### Agent-S ↔ Ollama
- Agent-S captures screenshot
- Sends to Ollama Vision endpoint (GPU 0) via ollama.Client
- Receives vision analysis for action planning

### Agent-S ↔ MCP Server
- Agent-S uses MCPClient for artifacts and memory
- Stores action history, creates code artifacts
- Persistent memory across sessions

---

*This is a living document. Update as new patterns emerge, especially around vision optimization and multi-GPU workload distribution.*
