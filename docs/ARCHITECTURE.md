# AlphaOmega Architecture Documentation

## System Overview

AlphaOmega is a multi-GPU AI orchestration platform designed for local deployment with enterprise-grade capabilities.

### Core Principles

1. **Local-First**: All processing happens on-device
2. **Privacy-Preserving**: No data leaves your machine
3. **Intelligent Routing**: Automatic backend selection
4. **Safety-Focused**: Built-in validation and permissions
5. **High Performance**: Multi-GPU parallelization

---

## Component Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                   │
│                     USER INTERACTION LAYER                        │
│                                                                   │
│    ┌───────────────────────────────────────────────────────┐    │
│    │           OpenWebUI (Port 3000)                        │    │
│    │           - Web Interface                              │    │
│    │           - Chat History                               │    │
│    │           - User Management                            │    │
│    └────────────────────┬──────────────────────────────────┘    │
│                         │                                         │
└─────────────────────────┼─────────────────────────────────────────┘
                          │
┌─────────────────────────┼─────────────────────────────────────────┐
│                         │                                         │
│                  ROUTING LAYER                                    │
│                         │                                         │
│    ┌────────────────────▼───────────────────────────────┐        │
│    │        Pipeline Router (Python)                    │        │
│    │        - Intent Detection                          │        │
│    │        - Backend Selection                         │        │
│    │        - Request Transformation                    │        │
│    └─┬──────────┬──────────┬──────────┬─────────────┬──┘        │
│      │          │          │          │             │            │
└──────┼──────────┼──────────┼──────────┼─────────────┼────────────┘
       │          │          │          │             │
       │          │          │          │             │
┌──────▼───┐  ┌──▼───────┐  ┌▼─────────▼┐  ┌────────▼─┐  ┌───────▼──┐
│          │  │          │  │            │  │          │  │          │
│ COMPUTE  │  │  IMAGE   │  │    LLM     │  │ COMPUTER │  │  TOOLS   │
│  LAYER   │  │   GEN    │  │  INFERENCE │  │   USE    │  │          │
│          │  │          │  │            │  │          │  │          │
│┌────────┐│  │┌────────┐│  │┌──────────┐│  │┌────────┐│  │┌────────┐│
││ComfyUI ││  ││Ollama  ││  ││Ollama    ││  ││Agent-S ││  ││  MCP   ││
││        ││  ││Vision  ││  ││Reasoning ││  ││        ││  ││ Server ││
││GPU 2   ││  ││GPU 0   ││  ││GPU 1     ││  ││        ││  ││        ││
││        ││  ││        ││  ││          ││  ││Vision  ││  ││mcpart  ││
││SDXL    ││  ││llava   ││  ││mistral   ││  ││Actions ││  ││        ││
││Flux    ││  ││:34b    ││  ││codellama ││  ││Safety  ││  ││Artifact││
││        ││  ││        ││  ││          ││  ││        ││  ││Memory  ││
│└────────┘│  │└────────┘│  │└──────────┘│  │└────────┘│  │└────────┘│
│          │  │          │  │            │  │          │  │          │
│  Port    │  │  Port    │  │   Port     │  │  Port    │  │  Port    │
│  8188    │  │  11434   │  │   11435    │  │  8001    │  │  8002    │
└──────────┘  └──────────┘  └────────────┘  └──────────┘  └──────────┘
     │              │               │              │              │
     │              │               │              │              │
┌────▼──────────────▼───────────────▼──────────────▼──────────────▼────┐
│                                                                        │
│                        INFRASTRUCTURE LAYER                            │
│                                                                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │   Docker     │  │    ROCm      │  │  Networking  │               │
│  │   Compose    │  │   Runtime    │  │              │               │
│  └──────────────┘  └──────────────┘  └──────────────┘               │
│                                                                        │
│  ┌────────────────────────────────────────────────────────────┐      │
│  │              Hardware (AMD MI50 GPUs)                       │      │
│  │  GPU 0: 48GB HBM2  │  GPU 1: 48GB HBM2  │  GPU 2: 48GB HBM2│      │
│  └────────────────────────────────────────────────────────────┘      │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Request Flow Diagrams

### 1. Computer Use Flow

```
User: "What's on my screen?"
  │
  ├─> OpenWebUI receives request
  │
  ├─> Pipeline Router analyzes message
  │   ├─ Keyword: "screen"
  │   └─> Intent: computer_use
  │
  ├─> Routes to Agent-S (port 8001)
  │
  ├─> Agent-S Server receives request
  │   │
  │   ├─> Screen Action: Capture screenshot
  │   │   └─> Save to /tmp/screenshot_TIMESTAMP.png
  │   │
  │   ├─> Vision Analyzer
  │   │   ├─> Preprocess image (resize to 1280x720)
  │   │   ├─> Send to Ollama Vision (GPU 0)
  │   │   └─> LLaVA 34B analyzes image
  │   │
  │   ├─> Generate response with vision result
  │   │
  │   └─> Return to OpenWebUI
  │
  └─> User sees: Analysis + Screenshot thumbnail
```

### 2. Image Generation Flow

```
User: "Generate an image of a sunset"
  │
  ├─> OpenWebUI receives request
  │
  ├─> Pipeline Router analyzes message
  │   ├─ Keyword: "generate image"
  │   └─> Intent: image_generation
  │
  ├─> Routes to ComfyUI (port 8188)
  │
  ├─> ComfyUI receives prompt
  │   │
  │   ├─> Load SDXL model on GPU 2
  │   │   └─> ~12GB VRAM allocated
  │   │
  │   ├─> Execute workflow
  │   │   ├─ Text encoding
  │   │   ├─ Latent generation
  │   │   ├─ Denoising steps (20 iterations)
  │   │   └─ VAE decode
  │   │
  │   ├─> Save image to output/
  │   │
  │   └─> Return image URL
  │
  └─> User sees: Generated image displayed
```

### 3. Code Generation Flow

```
User: "Write a Python function to sort a list"
  │
  ├─> OpenWebUI receives request
  │
  ├─> Pipeline Router analyzes message
  │   ├─ Keywords: "write", "Python function"
  │   └─> Intent: code_generation
  │
  ├─> Routes to Ollama Reasoning (GPU 1)
  │
  ├─> CodeLlama processes request
  │   │
  │   ├─> Model: codellama:13b (~7GB VRAM)
  │   │
  │   ├─> Generate code with context
  │   │   ├─ Function definition
  │   │   ├─ Docstring
  │   │   ├─ Implementation
  │   │   └─ Usage example
  │   │
  │   └─> Stream response back
  │
  └─> User sees: Complete code with examples
```

### 4. Multi-Step Automation Flow

```
User: "Click the Submit button"
  │
  ├─> Routes to Agent-S
  │
  ├─> Agent-S orchestrates action
  │   │
  │   ├─> 1. Capture screen
  │   │
  │   ├─> 2. Vision analysis (GPU 0)
  │   │   └─> "Submit button located at (450, 320)"
  │   │
  │   ├─> 3. Plan actions
  │   │   └─> Action: mouse_click(450, 320)
  │   │
  │   ├─> 4. Safety validation
  │   │   ├─> Check: Mouse action allowed? ✓
  │   │   ├─> Check: Dangerous hotkey? ✗
  │   │   └─> Result: SAFE
  │   │
  │   ├─> 5. Execute action
  │   │   └─> pyautogui.click(450, 320)
  │   │
  │   └─> 6. Return confirmation
  │
  └─> User sees: "✓ Clicked Submit button at (450, 320)"
```

---

## Data Flow

### 1. Vision Pipeline Data Flow

```
Screenshot (PNG)
    │
    ├─> Preprocessing
    │   ├─ Resize: 2560x1440 → 1280x720
    │   ├─ Optimize: Quality 85%
    │   └─ Size: ~2MB → ~500KB
    │
    ├─> Base64 Encoding
    │   └─ Embedded in JSON request
    │
    ├─> Ollama Vision API
    │   ├─ Model: llava:34b
    │   ├─ GPU: MI50 #0 (48GB)
    │   └─ Inference: ~3-4 seconds
    │
    ├─> Vision Analysis (Text)
    │   └─ Structured description of screen
    │
    └─> Response to User
```

### 2. Model Loading Strategy

```
Cold Start (First Request):
  ├─> Ollama loads model from disk
  │   └─> Time: ~5-10 seconds
  │
  ├─> Model loaded into VRAM
  │   └─> Memory: Model-specific
  │
  └─> Ready for inference

Warm (OLLAMA_KEEP_ALIVE=-1):
  ├─> Model stays in VRAM
  │
  ├─> Immediate inference
  │   └─> Time: <1 second to start
  │
  └─> Optimal for interactive use
```

---

## GPU Memory Management

### Allocation Strategy

```yaml
GPU 0 (MI50 - 48GB):
  Allocated: 40GB
  Available: 8GB buffer
  Model: llava:34b (~14GB loaded)
  Workload: Vision analysis
  
GPU 1 (MI50 - 48GB):
  Allocated: 20GB
  Available: 28GB buffer
  Models: 
    - mistral (~4GB)
    - codellama:13b (~7GB)
  Workload: Reasoning, code generation
  Strategy: Hot-swap based on request type
  
GPU 2 (MI50 - 48GB):
  Allocated: Dynamic (12-40GB)
  Available: Variable
  Models: SDXL, Flux, ControlNet
  Workload: Image generation
  Strategy: Load on demand
```

### Memory Optimization

1. **Model Quantization**: 4-bit quantized models where possible
2. **Dynamic Loading**: ComfyUI models loaded per workflow
3. **Shared Memory**: Ollama shares base models when possible
4. **Garbage Collection**: PyTorch HIP automatic cleanup

---

## Scaling & Performance

### Parallel Processing

```
Scenario: 3 simultaneous requests

Request A: "What's on my screen?"
  └─> GPU 0 (Vision)

Request B: "Write Python code"
  └─> GPU 1 (CodeLlama)

Request C: "Generate sunset image"
  └─> GPU 2 (ComfyUI)

Result: All 3 process simultaneously!
```

### Throughput Metrics

| Component | Latency | Throughput | GPU |
|-----------|---------|------------|-----|
| LLaVA Vision | 3-4s | ~15-20 req/min | 0 |
| Mistral Reasoning | 1-2s | ~30-60 req/min | 1 |
| CodeLlama | 2-3s | ~20-30 req/min | 1 |
| SDXL Image | 15-20s | ~3-4 img/min | 2 |

### Bottleneck Analysis

1. **Vision (GPU 0)**: Usually most loaded
   - Solution: Optimize preprocessing, use region analysis
   
2. **Reasoning (GPU 1)**: Can handle burst loads
   - Solution: Model hot-swapping
   
3. **Image Gen (GPU 2)**: Longest per-request time
   - Solution: Async queue, batch processing

---

## Safety Architecture

### Multi-Layer Validation

```
User Request
  │
  ├─> Layer 1: Intent Classification
  │   └─> Is this a risky action type?
  │
  ├─> Layer 2: Parameter Validation
  │   └─> Are parameters within safe bounds?
  │
  ├─> Layer 3: Permission Check
  │   └─> Is user allowed to perform this?
  │
  ├─> Layer 4: Safety Validator
  │   ├─> Dangerous commands?
  │   ├─> File path restrictions?
  │   └─> Keyboard hotkey risks?
  │
  ├─> Layer 5: Execution
  │   └─> Action performed
  │
  └─> Layer 6: Audit Logging
      └─> All actions logged with timestamp
```

---

## Network Architecture

### Internal Service Communication

```
┌─────────────┐     Docker Bridge Network (alphaomega-network)
│  OpenWebUI  │─────┐
└─────────────┘     │
                    ├──> ComfyUI (comfyui:8188)
┌─────────────┐     │
│  Agent-S    │─────┤
└─────────────┘     ├──> MCP Server (mcp-server:8002)
                    │
┌─────────────┐     │
│  Pipeline   │─────┘
└─────────────┘

Ollama Services (Host Network):
  - Vision: localhost:11434
  - Reasoning: localhost:11435
```

### External Access

```
Host Machine
  │
  ├─> :3000 → OpenWebUI (User access)
  ├─> :8001 → Agent-S API (Optional direct access)
  ├─> :8188 → ComfyUI (Admin/monitoring)
  ├─> :11434 → Ollama Vision (Internal)
  ├─> :11435 → Ollama Reasoning (Internal)
  └─> :8002 → MCP Server (Internal)
```

---

## Monitoring & Observability

### Key Metrics

1. **GPU Utilization**: rocm-smi
2. **Model Loading**: ollama ps
3. **Service Health**: HTTP health endpoints
4. **Request Routing**: Pipeline logs
5. **Action Safety**: Validator logs

### Log Aggregation

```
logs/
  ├─ alphaomega.log       # Main application log
  ├─ pipeline.log         # Routing decisions
  ├─ agent_actions.log    # Computer use actions
  ├─ mcp.log              # Tool executions
  ├─ ollama-vision.log    # GPU 0 inference
  └─ ollama-reasoning.log # GPU 1 inference
```

---

## Failure Handling

### Service Failure Scenarios

```
ComfyUI Down:
  User request → Pipeline detects failure
  → Returns: "⚠️ Image generation unavailable"
  → Other services continue normally

Ollama Vision Down:
  User request → Agent-S detects failure
  → Fallback: Text-based response without vision
  → Alert logged

Safety Validator Blocks Action:
  User request → Action planned
  → Validator: UNSAFE
  → Returns: Error with reason
  → Action never executed
```

---

## Future Enhancements

1. **Load Balancing**: Distribute vision requests across multiple GPUs
2. **Model Caching**: Intelligent model preloading based on usage patterns
3. **WebSocket Streaming**: Real-time updates during long operations
4. **Multi-User Support**: Concurrent user sessions with queue management
5. **Cloud Backup**: Optional encrypted cloud sync for artifacts

---

**AlphaOmega** - Production-grade local AI orchestration 🔱
