# AlphaOmega Services - All Running! ✅

**Date**: October 11, 2025  
**Status**: ALL SYSTEMS OPERATIONAL

## Running Services

### ✅ 1. Dashboard (Port 5000) - NEW! 🎉
- **Status**: Running - Web-based service management
- **Features**:
  - Real-time status monitoring (auto-refresh every 3 seconds)
  - One-click service start/stop controls
  - System resource monitoring (CPU, RAM, disk)
  - Direct links to all services
  - Service logs viewer
- **URL**: http://localhost:5000
- **Access**: Opens automatically in browser when started
- **Scripts**:
  - Start: `./scripts/start-dashboard.sh`
  - Stop: `./scripts/stop-dashboard.sh`

### ✅ 2. Ollama (Port 11434)
- **Status**: Running with 25 models
- **Models**: llama3.2-vision, codellama:13b, mistral, llava:34b, and 21 more
- **GPU**: Uses available AMD GPUs (RX 6600 XT + MI50s)
- **API**: http://localhost:11434

### ✅ 3. MCP Server (Port 8002) - UNIFIED
- **Status**: Running with 76 tools
- **Important**: This is ONE unified server, not split!
- **Tools by Category**:
  - Inventory Management (12 tools)
  - Sales & Analytics (8 tools)
  - Social Media (12 tools)
  - Task & Calendar (10 tools)
  - File System (13 tools)
  - Business Operations (11 tools)
  - VIP Clients (6 tools)
  - Universal Tools (4 tools)
- **API**: http://localhost:8002
- **Docs**: http://localhost:8002/docs

### ✅ 4. Coqui TTS (Port 5002)
- **Status**: Running with professional voice quality
- **Features**:
  - 100+ pre-trained models
  - Voice cloning (5-10 sec audio sample)
  - Multi-language support (20+ languages)
  - 3x real-time speed on AMD MI50
- **API**: http://localhost:5002
- **Health**: http://localhost:5002/health

## Quick Start Commands

### Start All Services (Easy Way - Use Dashboard!)
```bash
# Start the web dashboard (recommended)
./scripts/start-dashboard.sh
# Opens in browser at http://localhost:5000
# Click "▶️ Start All Services" button
```

### Start All Services (Command Line)
```bash
# Start MCP Server (76 tools, port 8002)
./scripts/start-mcp-unified.sh

# Start Coqui TTS (already running)
./tts/start_coqui_api.sh

# Start Dashboard
./scripts/start-dashboard.sh

# Ollama starts automatically
```

### Check Status
```bash
# Via web dashboard (recommended)
# Open http://localhost:5000 in your browser

# Or via command line
./scripts/check-services.sh
```

### Stop Services
```bash
# Via web dashboard (recommended)
# Open http://localhost:5000 and click "⏹️ Stop All Services"

# Or via command line:
# Stop Dashboard
./scripts/stop-dashboard.sh

# Stop MCP
pkill -f 'mcpo.*8002'

# Stop TTS
./tts/stop_coqui_api.sh

# Stop Ollama
pkill ollama
```

## Important Notes

### ⚠️ MCP Server Configuration
**DO NOT use `start-mcp-servers.sh` - it's been renamed to `.WRONG_DONT_USE`**

The MCP server is UNIFIED on port 8002 with all 76 tools. 
Do not split it into multiple servers!

See: `MCP_SERVER_WARNING.md` for details.

### File Locations
```
/home/stacy/AlphaOmega/
├── scripts/
│   ├── start-mcp-unified.sh       ✅ Use this for MCP
│   ├── check-services.sh          ✅ Check all services
│   └── start-mcp-servers.sh.WRONG_DONT_USE  ❌ Don't use
├── tts/
│   ├── start_coqui_api.sh         ✅ Start TTS
│   ├── stop_coqui_api.sh          ✅ Stop TTS
│   └── coqui_api.py               Server code
├── logs/
│   ├── mcp-unified.log            MCP server logs
│   └── coqui_tts.log              TTS logs
└── docs/
    ├── MCP_VERIFICATION_GUIDE.md  MCP tools reference
    ├── COQUI_TTS_SETUP.md         TTS setup guide
    └── VOICE_CLONING_GUIDE.md     Voice cloning tutorial
```

## Integration with OpenWebUI

### MCP Server
1. Open OpenWebUI Admin Panel
2. Settings → External Tools
3. Click [+] under 'Manage Tool Servers'
4. Add:
   - **Name**: AlphaOmega MCP (76 Tools)
   - **URL**: http://localhost:8002

### TTS Configuration
1. OpenWebUI Settings → Audio → Text-to-Speech
2. **TTS API Base URL**: http://localhost:5002/v1
3. **Model**: 
   - `tts-1` (fast, good quality)
   - `tts-1-hd` (XTTS-v2 with voice cloning)

## Testing

### Test MCP Server
```bash
# List all tools
curl http://localhost:8002/openapi.json | jq '.paths | keys | length'
# Should return: 76

# Test a tool
curl http://localhost:8002/get_low_stock_items

# View documentation
curl http://localhost:8002/docs
# Or open in browser
```

### Test TTS
```bash
# Generate speech
curl -X POST http://localhost:8002/v1/audio/speech \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "tts-1",
    "input": "Hello from Coqui TTS!",
    "voice": "alloy"
  }' \
  --output test.wav

# Check health
curl http://localhost:5002/health
```

### Test Ollama
```bash
# List models
curl http://localhost:11434/api/tags

# Test generation
curl http://localhost:11434/api/generate -d '{
  "model": "mistral",
  "prompt": "Hello!"
}'
```

## What Changed Today

1. **✅ Installed Coqui TTS** - Professional voice quality, voice cloning
2. **✅ Fixed MCP Server** - Corrected unified configuration (76 tools on port 8002)
3. **✅ Created Warning Documentation** - Prevent accidental server split
4. **🎉 NEW: Web Dashboard** - Graphical service management interface
   - Auto-refreshing status display
   - One-click service control
   - System resource monitoring
   - Direct links to all services
   - Port 5000: http://localhost:5000
4. **✅ Created Service Check Script** - Easy status verification
5. **✅ Removed Piper TTS** - Replaced with Coqui (better quality)

## Documentation

- **MCP Tools**: `docs/MCP_VERIFICATION_GUIDE.md`
- **MCP Warning**: `MCP_SERVER_WARNING.md`
- **TTS Setup**: `docs/COQUI_TTS_SETUP.md`
- **Voice Cloning**: `docs/VOICE_CLONING_GUIDE.md`
- **TTS Complete**: `COQUI_TTS_COMPLETE.md`

## Support

### If Services Stop
```bash
# Check what's running
./scripts/check-services.sh

# Restart MCP
pkill -f 'mcpo.*8002'
./scripts/start-mcp-unified.sh

# Restart TTS
./tts/stop_coqui_api.sh
./tts/start_coqui_api.sh
```

### Check Logs
```bash
# MCP logs
tail -f logs/mcp-unified.log

# TTS logs
tail -f logs/coqui_tts.log

# Ollama logs (if started manually)
tail -f logs/ollama-*.log
```

---

**All systems operational and ready for use!** 🚀
