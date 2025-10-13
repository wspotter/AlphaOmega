# AlphaOmega 🚀

> **Unified Local AI Orchestration Platform**
> 
> A complete AI infrastructure running entirely on your hardware - no cloud dependencies, complete privacy.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![ROCm Compatible](https://img.shields.io/badge/ROCm-Compatible-orange.svg)](https://rocm.docs.amd.com/)

## 🌟 Features

### Core Services
- **🌐 OpenWebUI** - Unified web interface for all AI interactions
- **🤖 Ollama** - Local LLM inference with 25+ models (Mistral, LLaVA, CodeLlama, etc.)
- **🔧 MCP Server** - 76 unified business tools (inventory, sales, social media, tasks, files)
- **🗣️ Coqui TTS** - Professional text-to-speech with voice cloning

### In Development
- **🎨 ComfyUI** - Advanced image generation (SDXL, Flux workflows)
- **🖥️ Agent-S** - Computer use automation (screen analysis, mouse/keyboard control)

### Web Dashboard
- ✅ Real-time service monitoring (auto-refresh every 3 seconds)
- ✅ One-click start/stop controls for all services  
- ✅ System resource monitoring (CPU, RAM, Disk)
- ✅ Direct links to running services
- ✅ Process management and logging

## 🎯 Philosophy

- **Privacy-First**: Everything runs locally - no cloud APIs, no data leaving your machine
- **No Docker Dependencies**: Pure local execution for maximum control
- **AMD GPU Optimized**: Built for AMD MI50 GPUs with ROCm support
- **Production-Ready**: Complete with monitoring, logging, and safety validators

## 🚀 Quick Start

### Prerequisites

**Hardware:**
- AMD MI50 GPUs (or other ROCm-compatible GPUs) recommended
- 16GB+ RAM minimum
- 100GB+ free disk space

**Software:**
- Linux (Ubuntu 22.04+ recommended)
- Python 3.12+
- ROCm 6.0+ ([installation guide](https://rocm.docs.amd.com/))
- Node.js 18+ (for MCP server)

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

# Start the dashboard
./scripts/start-dashboard.sh
```

The dashboard will open automatically at **http://localhost:5000**

From there, you can start all services with one click! 🎉

## 📊 Service Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Dashboard (Port 5000)                  │
│              Web-based Service Management               │
└─────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┬─────────────┐
        │                 │                 │             │
   ┌────▼────┐      ┌─────▼─────┐    ┌─────▼─────┐ ┌────▼────┐
   │OpenWebUI│      │  Ollama   │    │    MCP    │ │Coqui TTS│
   │  :8080  │      │  :11434   │    │   :8002   │ │  :5002  │
   └─────────┘      └───────────┘    └───────────┘ └─────────┘
        │                 │                 │             │
        └─────────────────┴─────────────────┴─────────────┘
                    All Running Locally
```

## 📖 Usage

### Start Everything

```bash
# Option 1: Use the web dashboard (recommended)
./scripts/start-dashboard.sh
# Then click "Start All Services" at http://localhost:5000

# Option 2: Start services individually
./scripts/start-openwebui.sh      # OpenWebUI on port 8080
./scripts/start-mcp-unified.sh    # MCP Server on port 8002  
./tts/start_coqui_api.sh          # Coqui TTS on port 5002
```

### Access Services

- **Dashboard**: http://localhost:5000 (service management)
- **OpenWebUI**: http://localhost:8080 (main AI interface)
- **Ollama API**: http://localhost:11434 (LLM endpoint)
- **MCP Server**: http://localhost:8002 (business tools)
- **Coqui TTS**: http://localhost:5002 (text-to-speech)

### Check Status

```bash
# Quick status check
./scripts/check-services.sh

# View logs
tail -f logs/dashboard.log
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

Coqui TTS supports:
- 100+ pre-trained voices across 20+ languages
- Voice cloning from 5-10 second audio samples
- 3x real-time generation speed on AMD MI50

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
├── tts/                  # Coqui TTS setup
├── dashboard.py          # Main dashboard application
└── requirements.txt      # Python dependencies
```

## 🛠️ Development

### Adding a New Service

1. Add service definition to `dashboard.py`:
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

2. Create startup script in `scripts/start-myservice.sh`
3. Restart dashboard to see the new service

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
  curl http://localhost:5002/health        # TTS
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
- [Coqui TTS](https://github.com/coqui-ai/TTS) - High-quality open source TTS
- [AMD ROCm](https://rocm.docs.amd.com/) - GPU compute platform

## 📧 Contact

Project Link: [https://github.com/wspotter/AlphaOmega](https://github.com/wspotter/AlphaOmega)

---

**Made with ❤️ for the local AI community**
