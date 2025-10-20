# AlphaOmega Dashboard Guide

## Overview

The AlphaOmega Dashboard provides a web-based graphical interface for managing all AlphaOmega services. It offers real-time status monitoring, one-click service control, and system resource tracking.

## Quick Start

### Starting the Dashboard
```bash
./scripts/start-dashboard.sh
```

The dashboard will:
- Start on port 5000
- Auto-open in your browser at http://localhost:5000
- Create logs at `/home/stacy/AlphaOmega/logs/dashboard.log`

### Stopping the Dashboard
```bash
./scripts/stop-dashboard.sh
```

## Features

### 1. Real-Time Status Monitoring
- **Auto-refresh**: Updates every 3 seconds
- **Service Status**: Shows running/stopped/starting state for each service
- **Responsiveness Check**: Verifies HTTP endpoints are accessible
- **Process Monitoring**: Displays PID for each running service

### 2. System Resource Monitoring
The dashboard displays real-time system statistics:
- **CPU Usage**: Percentage and core count
- **Memory Usage**: Used/total RAM in GB and percentage
- **Disk Usage**: Used/total disk space in GB and percentage

### 3. Service Management
Each service card provides:
- **Service Name**: Ollama, MCP Server, or Chatterbox TTS
- **Description**: What the service does
- **Port Number**: Which port the service runs on
- **Status Badge**: Color-coded visual indicator
  - 🟢 Green: Running and responsive
  - 🟠 Orange: Starting
  - 🔴 Red: Stopped
- **Service Details**:
  - Ollama: Number of models loaded
  - MCP: Number of tools available
  - TTS: Health status
- **Action Buttons**:
  - ▶️ Start: Launch the service
  - ⏹️ Stop: Shut down the service
  - 🔗 Open Service: Direct link to service UI (when running)

### 4. Bulk Operations
- **▶️ Start All Services**: Launch all services in sequence
- **⏹️ Stop All Services**: Shut down all services (requires confirmation)
- **🔄 Refresh Now**: Manually trigger status update

## Accessing the Dashboard

### Local Access
- **URL**: http://localhost:5000
- **Browser**: Any modern browser (Chrome, Firefox, Safari, Edge)

### Network Access
If you want to access the dashboard from another device on your network:
- **URL**: http://192.168.3.69:5000 (use your machine's IP)
- Note: Dashboard runs on all interfaces (0.0.0.0)

## Service Links

When services are running, you can click "🔗 Open Service" to access:

### Ollama
- **URL**: http://localhost:11434
- **Purpose**: LLM API endpoint
- **Test**: `curl http://localhost:11434/api/tags` to see loaded models

### MCP Server
- **URL**: http://localhost:8002
- **Purpose**: Model Context Protocol unified server with 76 tools
- **Documentation**: http://localhost:8002/openapi.json
- **Tool Count**: `curl http://localhost:8002/openapi.json | jq '.paths | keys | length'`

### Chatterbox TTS
- **URL**: http://localhost:5003/health
- **Purpose**: High-quality text-to-speech with voice cloning
- **Test**: `curl http://localhost:5003/health`

## Dashboard API Endpoints

The dashboard exposes a REST API that can be used programmatically:

### GET /api/status
Returns complete system status
```bash
curl http://localhost:5000/api/status | jq '.'
```

Response includes:
- System stats (CPU, memory, disk)
- Service status for each service
- Timestamp

### POST /api/start/<service>
Start a specific service
```bash
curl -X POST http://localhost:5000/api/start/ollama
curl -X POST http://localhost:5000/api/start/mcp
curl -X POST http://localhost:5000/api/start/tts
```

### POST /api/stop/<service>
Stop a specific service
```bash
curl -X POST http://localhost:5000/api/stop/ollama
curl -X POST http://localhost:5000/api/stop/mcp
curl -X POST http://localhost:5000/api/stop/tts
```

### POST /api/start_all
Start all services
```bash
curl -X POST http://localhost:5000/api/start_all
```

### POST /api/stop_all
Stop all services
```bash
curl -X POST http://localhost:5000/api/stop_all
```

### GET /api/logs/<service>
View recent logs for a service
```bash
curl http://localhost:5000/api/logs/mcp
curl http://localhost:5000/api/logs/dashboard
```

## File Locations

### Dashboard Files
- **Main App**: `/home/stacy/AlphaOmega/dashboard.py`
- **HTML Template**: `/home/stacy/AlphaOmega/templates/dashboard.html`
- **Startup Script**: `/home/stacy/AlphaOmega/scripts/start-dashboard.sh`
- **Stop Script**: `/home/stacy/AlphaOmega/scripts/stop-dashboard.sh`

### Runtime Files
- **Log File**: `/home/stacy/AlphaOmega/logs/dashboard.log`
- **PID File**: `/tmp/alphaomega-dashboard.pid`

### Service Logs
Each service has its own log file:
- **Ollama**: `/home/stacy/AlphaOmega/logs/ollama-local.log`
- **MCP**: `/home/stacy/AlphaOmega/logs/mcp-unified.log`
- **TTS**: `/home/stacy/AlphaOmega/logs/tts.log`

## Troubleshooting

### Dashboard Won't Start

**Port 5000 already in use:**
```bash
# Find and kill process using port 5000
lsof -ti:5000 | xargs kill
```

**Missing dependencies:**
```bash
source venv/bin/activate
pip install flask requests psutil
```

**Permission issues:**
```bash
chmod +x scripts/start-dashboard.sh scripts/stop-dashboard.sh
```

### Services Not Starting

**Check service logs:**
```bash
# Via dashboard
curl http://localhost:5000/api/logs/mcp | jq '.'

# Or directly
tail -50 logs/mcp-unified.log
tail -50 logs/ollama-local.log
tail -50 logs/tts.log
```

**Verify processes manually:**
```bash
./scripts/check-services.sh
```

### Dashboard Shows Service as Stopped but Process is Running

This usually means the HTTP endpoint isn't responding. Check:
```bash
# Test Ollama
curl http://localhost:11434/api/tags

# Test MCP
curl http://localhost:8002/openapi.json

# Test TTS
curl http://localhost:5003/health
```

If curl fails but process exists, restart the service.

### Auto-refresh Not Working

- Clear browser cache (Ctrl+Shift+R)
- Check browser console for JavaScript errors (F12)
- Verify /api/status endpoint: `curl http://localhost:5000/api/status`

## Technical Details

### Technology Stack
- **Backend**: Flask (Python web framework)
- **Frontend**: Vanilla JavaScript with modern fetch API
- **Styling**: Custom CSS with gradient themes
- **Monitoring**: psutil for system stats, requests for HTTP checks

### Auto-Refresh Mechanism
```javascript
// Fetches status every 3 seconds
setInterval(fetchStatus, 3000);
```

To change refresh rate, edit the interval in `templates/dashboard.html`.

### Process Management
Dashboard uses:
- `pgrep` to check if processes are running
- `pkill` to stop services
- PID files for tracking started processes

### Safety Features
- Confirmation required for "Stop All"
- Individual service confirmations for stop operations
- Graceful shutdown with fallback to force kill (SIGKILL)
- Error handling for failed start/stop operations

## Integration with Other Tools

### Command-Line Tools
The dashboard complements existing CLI tools:
- `./scripts/check-services.sh` - Quick status check
- `./scripts/start-mcp-unified.sh` - Start MCP server
- `./scripts/start-tts.sh` - Start Chatterbox TTS service

### OpenWebUI Integration
When services are running via dashboard, OpenWebUI can connect to:
- Ollama at `http://localhost:11434`
- MCP at `http://localhost:8002`

Configure in OpenWebUI settings:
1. Admin Panel → Settings → Connections
2. Add Ollama URL: `http://localhost:11434`
3. Add MCP endpoint: `http://localhost:8002`

## Customization

### Changing Dashboard Port
Edit `dashboard.py`:
```python
app.run(host='0.0.0.0', port=5000, debug=False)
```

Change `port=5000` to your desired port.

### Changing Auto-Refresh Rate
Edit `templates/dashboard.html`:
```javascript
refreshInterval = setInterval(fetchStatus, 3000); // 3000ms = 3 seconds
```

Change `3000` to your desired milliseconds (e.g., 5000 for 5 seconds).

### Adding New Services
Edit `dashboard.py` and add to `SERVICES` dictionary:
```python
'newservice': {
    'name': 'New Service',
    'description': 'Description of service',
    'port': 9000,
    'health_url': 'http://localhost:9000/health',
    'start_cmd': './scripts/start-newservice.sh',
    'stop_cmd': 'pkill -f newservice',
    'log_file': 'logs/newservice.log'
}
```

## Best Practices

1. **Always use the dashboard to manage services** - Prevents orphaned processes
2. **Check logs if service fails to start** - Use API endpoint or direct file access
3. **Monitor system resources** - Dashboard shows if you're running low on RAM/CPU
4. **Stop services when not in use** - Saves resources, especially GPU memory
5. **Keep dashboard logs clean** - Rotate logs periodically to save disk space

## Quick Reference

### Common Commands
```bash
# Start dashboard
./scripts/start-dashboard.sh

# Stop dashboard
./scripts/stop-dashboard.sh

# View dashboard logs
tail -f logs/dashboard.log

# Check if dashboard is running
pgrep -f "python.*dashboard.py"

# Test dashboard API
curl http://localhost:5000/api/status | jq '.services'

# Force restart dashboard
./scripts/stop-dashboard.sh && ./scripts/start-dashboard.sh
```

### Keyboard Shortcuts in Browser
- **Ctrl+R**: Refresh page
- **Ctrl+Shift+R**: Hard refresh (clear cache)
- **F12**: Open developer console
- **Ctrl+W**: Close tab

## Future Enhancements

Potential features for future versions:
- WebSocket for real-time log streaming
- GPU monitoring (rocm-smi integration)
- Service restart buttons
- Uptime tracking
- Historical system stats graphs
- Export status reports
- Email/webhook notifications for service failures

---

**Dashboard Version**: 1.0  
**Last Updated**: October 2025  
**Documentation**: Full  
**Status**: Production Ready ✓
