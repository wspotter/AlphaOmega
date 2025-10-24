# AlphaOmega Dashboard - Quick Reference

## Starting the Dashboard

### Method 1: Command Line (Recommended)
```bash
cd /home/stacy/AlphaOmega
./scripts/start-dashboard.sh
```

**What it does:**
- ✅ Automatically activates virtual environment
- ✅ Installs missing dependencies if needed
- ✅ Starts dashboard on http://localhost:5000
- ✅ Opens dashboard in browser automatically
- ✅ Logs output to `logs/dashboard.log`

### Method 2: Desktop Launcher
- Search for "AlphaOmega Dashboard" in your application menu
- Click to launch

## Stopping the Dashboard

```bash
cd /home/stacy/AlphaOmega
./scripts/stop-dashboard.sh
```

**What it does:**
- ✅ Gracefully stops the dashboard process
- ✅ Automatically deactivates virtual environment
- ✅ Cleans up PID files

## Dashboard Features

### Web Interface
Access at: **http://localhost:5000**

- 📊 Real-time service status monitoring
- 🚀 Start/Stop individual services
- 💻 System resource monitoring (CPU, RAM, Disk)
- 📝 Service logs viewer

### API Endpoints

**Get Status:**
```bash
curl http://localhost:5000/api/status
```

**Start All Services:**
```bash
curl http://localhost:5000/api/start_all
```

**Start Individual Service:**
```bash
curl http://localhost:5000/api/start/ollama
curl http://localhost:5000/api/start/tts
curl http://localhost:5000/api/start/comfyui
```

**Stop All Services:**
```bash
curl http://localhost:5000/api/stop_all
```

**Stop Individual Service:**
```bash
curl http://localhost:5000/api/stop/ollama
```

## Managed Services

The dashboard controls these AlphaOmega services:

| Service | Port | Description |
|---------|------|-------------|
| OpenWebUI | 8080 | Unified web interface |
| Ollama | 11434 | LLM inference engine |
| MCP | 8002 | Tool server (76 tools) |
| TTS | 5002 | Text-to-speech |
| SearxNG | 8181 | Search engine |
| ComfyUI | 8188 | Image generation |
| Agent-S | 8001 | Computer automation |

## Troubleshooting

### Dashboard won't start
```bash
# Check if port 5000 is in use
lsof -i :5000

# Kill conflicting process
lsof -ti:5000 | xargs kill

# Try starting again
./scripts/start-dashboard.sh
```

### Service won't start via dashboard
```bash
# Check service logs
tail -f logs/dashboard.log
tail -f logs/<service>.log

# Check if service is already running
ps aux | grep <service>
```

### View Dashboard Logs
```bash
# Real-time logs
tail -f /home/stacy/AlphaOmega/logs/dashboard.log

# Last 50 lines
tail -50 /home/stacy/AlphaOmega/logs/dashboard.log
```

## Virtual Environment

The dashboard scripts **automatically handle** the virtual environment:

- **Start script**: Activates venv, installs dependencies if needed
- **Stop script**: Deactivates venv after stopping dashboard

**Manual venv activation (if needed):**
```bash
source /home/stacy/AlphaOmega/venv/bin/activate
```

**Manual venv deactivation:**
```bash
deactivate
```

## Files & Locations

```
AlphaOmega/
├── dashboard.py                    # Main dashboard app
├── scripts/
│   ├── start-dashboard.sh         # Start script (with venv)
│   └── stop-dashboard.sh          # Stop script (with venv)
├── logs/
│   └── dashboard.log              # Dashboard logs
├── venv/                          # Virtual environment
└── templates/
    └── dashboard.html             # Web interface
```

## Quick Commands Summary

```bash
# Start dashboard
./scripts/start-dashboard.sh

# Stop dashboard
./scripts/stop-dashboard.sh

# Check if running
ps aux | grep "python dashboard.py"

# View logs
tail -f logs/dashboard.log

# Access dashboard
xdg-open http://localhost:5000
```

---

**Last Updated:** October 23, 2025
