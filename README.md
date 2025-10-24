# AlphaOmega 🚀

> **Unified Local AI Orchestration Platform**
> 
> A complete AI infrastructure running entirely on your hardware - no cloud dependencies, complete privacy.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![NVIDIA CUDA Compatible](https://img.shields.io/badge/NVIDIA-CUDA-green.svg)](https://developer.nvidia.com/cuda-toolkit)

## 🌟 Features

### Core Services
- **🌐 OpenWebUI** - Unified web interface for all AI interactions
- **🤖 Ollama** - Local LLM inference with 25+ models (Mistral, LLaVA, CodeLlama, etc.)
- **🔧 MCP Server** - 76 unified business tools (inventory, sales, social media, tasks, files)
- **🗣️ Chatterbox TTS** - Expressive neural text-to-speech backend

### In Development
- **🎨 ComfyUI** - Advanced image generation (SDXL, Flux workflows)
- **🖥️ Agent-S** - Computer use automation (screen analysis, mouse/keyboard control)

### Optional Dashboard
- Real-time service monitoring (auto-refresh every 3 seconds)
- One-click start/stop controls for host-managed services  
- System resource monitoring (CPU, RAM, disk)
- Direct links to running services
- Process management and logging

## 🎯 Philosophy

- **Privacy-First**: Everything runs locally - no cloud APIs, no data leaving your machine
- **Local-First**: Most services run directly on the host (no Docker overhead)
- **NVIDIA GPU Optimized**: Built for NVIDIA GPUs with CUDA support
- **Production-Ready**: Complete with monitoring, logging, and safety validators

## 🏗️ Architecture

**Most services run directly on the host:**
- OpenWebUI (port 8080) - Web interface
- Ollama (port 11434) - LLM inference
- Agent-S (port 8001) - Computer use automation
- ComfyUI (port 8188) - Image generation (local install)
- MCP OpenAPI Proxy (port 8002) - Tools server

**Docker is only used for:**
- **Chatterbox TTS** (port 5003) - Isolated Python 3.11+ environment

## 🚀 Quick Start

### Prerequisites

**Hardware:**
- AMD MI50 GPUs (or other ROCm-compatible GPUs) recommended
- 16GB+ RAM minimum
- 100GB+ free disk space

**Software:**
- Linux (Ubuntu 22.04+ recommended)
- Python 3.10+
- ROCm 6.0+ ([installation guide](https://rocm.docs.amd.com/))
- Node.js 18+ (for MCP server)
- Docker (ONLY for ComfyUI and Chatterbox TTS)
```

### Installation

```bash
# Clone repository
git clone https://github.com/wspotter/AlphaOmega.git
cd AlphaOmega

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start the full stack
./scripts/start-all.sh
```

Once the script finishes, visit **http://localhost:8080** to use OpenWebUI. 

Need a web control panel? Launch the optional dashboard anytime with `./scripts/start-dashboard.sh` (served at **http://localhost:5000**).

## 📊 Service Architecture

```
┌─────────────────────────────────────────────────────────┐
│                Core Host Services (Local)               │
└─────────────────────────────────────────────────────────┘
     │                 │                 │             │
   ┌────▼────┐      ┌─────▼─────┐    ┌─────▼─────┐ ┌────▼────┐
  │OpenWebUI│      │  Ollama   │    │ MCP Tools │ │Chatterbox│
  │  :8080  │      │  :11434   │    │   :8002   │ │  :5003   │
   └─────────┘      └───────────┘    └───────────┘ └─────────┘
     │                 │                 │             │
     └─────────────────┴─────────────────┴─────────────┘
      (Optional dashboard available on :5000)
```

## 📖 Usage

### Start Everything

```bash
# Option 1: Start core services with one command
./scripts/start-all.sh

# Option 2: Start services individually
./scripts/start-openwebui.sh      # OpenWebUI on port 8080
./scripts/start-mcp-unified.sh    # MCP Server on port 8002  
./scripts/start-tts.sh            # Chatterbox TTS on port 5003 (optional)
```

### Access Services

- **OpenWebUI**: http://localhost:8080 (main AI interface)
- **Ollama API**: http://localhost:11434 (LLM endpoint)
- **MCP Tool Server**: http://localhost:8002/openapi.json (business tools)
- **Chatterbox TTS**: http://localhost:5003 (text-to-speech)
- **Dashboard (optional)**: http://localhost:5000 (service management)

### Check Status

```bash
# Quick status check
./scripts/check-services.sh

# View logs
tail -f logs/openwebui.log
tail -f logs/mcp-unified.log
```

### Stop Everything

```bash
# Via dashboard: click "Stop All Services"
# Or use the stop script:
./scripts/stop-all.sh
```

## 🔧 Configuration

### MCP Server Tools (76 Total)

The MCP server provides 8 categories of business tools:

- **Inventory Management** (12 tools) - Product tracking, stock levels
- **Sales & Analytics** (8 tools) - Revenue tracking, reports
- **Social Media** (12 tools) - Facebook, Instagram integration
- **Tasks & Calendar** (10 tools) - Task management, scheduling
- **File System** (13 tools) - File operations with safety validation
- **Business Operations** (11 tools) - Invoices, expenses, payroll
- **VIP Clients** (6 tools) - Client relationship management
- **Universal Tools** (4 tools) - General utilities

### Ollama Models

AlphaOmega includes 25+ models for different tasks:

- **Vision**: llama3.2-vision, llava:34b
- **Reasoning**: mistral, qwen2.5:14b
- **Coding**: codellama:13b, deepseek-coder-v2:16b
- **And many more...**

List available models: `ollama list`

### Text-to-Speech Voices

Chatterbox TTS provides expressive, OpenAI-compatible speech synthesis with GPU acceleration via Docker. The default configuration exposes `/v1/audio/speech` and `/health` endpoints on port 5003. For alternate voices or legacy backends (Coqui, Piper), see the additional scripts in `tts/`.

## 📁 Project Structure

```
AlphaOmega/
├── agent_s/              # Computer use automation (in development)
├── comfyui_bridge/       # Image generation interface (in development)
├── config/               # Configuration files
├── docs/                 # Documentation
│   ├── ARCHITECTURE.md   # System design
│   ├── DASHBOARD_GUIDE.md # Dashboard usage
│   └── MCP_INTEGRATION.md # MCP setup guide
├── logs/                 # Service logs
├── models/               # AI model storage
├── pipelines/            # OpenWebUI pipeline integrations
├── scripts/              # Startup/utility scripts
├── templates/            # Dashboard HTML templates
├── tests/                # Test suites
├── tts/                  # Chatterbox + legacy TTS backends
├── dashboard.py          # Main dashboard application
└── requirements.txt      # Python dependencies
```

## 🛠️ Development

### Optional Dashboard Extensions

If you rely on the optional dashboard UI, you can register additional services by updating `dashboard.py`:
```python
"myservice": {
  "name": "My Service",
  "port": 9000,
  "check_url": "http://localhost:9000/health",
  "start_cmd": f"{PROJECT_DIR}/scripts/start-myservice.sh",
  "stop_cmd": "pkill -f myservice",
  "process_name": "myservice",
  "description": "What my service does",
  "status": "ready"
}
```
Then create the matching script under `scripts/` and restart the dashboard. The core stack does not depend on these entries.

### Running Tests

```bash
# Unit tests
pytest tests/unit/

# Integration tests (requires services running)
pytest tests/integration/
```

## 🔐 Security & Safety

- **Action Validation**: MCP server validates all file operations
- **Safe Mode**: Agent-S requires confirmation for risky actions
- **Process Isolation**: Each service runs in its own process
- **Local Only**: No external API calls or data transmission
- **Configurable Permissions**: Fine-grained control over service capabilities

## 🐛 Troubleshooting

### Service Won't Start

```bash
# Check if port is in use
lsof -i :8080  # Replace with your service port

# View service logs
tail -50 logs/[service-name].log

# Verify process is running
pgrep -f "service-name"
```

### Dashboard Not Showing Service Status

- Refresh browser (Ctrl+R)
- Check service health endpoints manually:
  ```bash
  curl http://localhost:11434/api/tags     # Ollama
  curl http://localhost:8002/openapi.json  # MCP
  curl http://localhost:5003/health        # TTS
  ```

### GPU Not Detected

```bash
# Verify ROCm installation
rocm-smi --showid

# Set GPU override for MI50
export HSA_OVERRIDE_GFX_VERSION=9.0.0
```

## 📚 Documentation

- **[Dashboard Guide](docs/DASHBOARD_GUIDE.md)** - Complete dashboard usage
- **[MCP Integration](docs/MCP_INTEGRATION.md)** - MCP server setup
- **[Architecture](docs/ARCHITECTURE.md)** - System design details
- **[Services Running](SERVICES_RUNNING.md)** - Current service status

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [OpenWebUI](https://github.com/open-webui/open-webui) - Excellent web interface
- [Ollama](https://ollama.ai/) - Amazing local LLM platform
- [Chatterbox TTS](https://github.com/resemble-ai/chatterbox) - Expressive neural TTS
- [AMD ROCm](https://rocm.docs.amd.com/) - GPU compute platform

## 📧 Contact

Project Link: [https://github.com/wspotter/AlphaOmega](https://github.com/wspotter/AlphaOmega)

---

**Made with ❤️ for the local AI community**
