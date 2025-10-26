# GUI Links Added to Dashboard

## Changes Made:

### 1. Updated Service Definitions (dashboard.py)
Added `gui_url` and `gui_name` to three services:

```python
"openwebui": {
    ...
    "gui_url": "http://localhost:8080",
    "gui_name": "Open Chat Interface"
},

"tts": {
    ...
    "gui_url": "http://localhost:7861",
    "gui_name": "Voice Cloning GUI"
},

"comfyui": {
    ...
    "gui_url": f"http://localhost:{COMFYUI_PORT}",
    "gui_name": "ComfyUI Workflow Editor"
}
```

### 2. Updated API Endpoint (dashboard.py line ~335)
Modified `/api/status` to include GUI info:

```python
for key in SERVICES:
    service_status = check_service_status(key)
    if SERVICES[key].get("gui_url"):
        service_status["gui_url"] = SERVICES[key]["gui_url"]
        service_status["gui_name"] = SERVICES[key].get("gui_name", "Open GUI")
    status["services"][key] = service_status
```

### 3. Updated Dashboard UI (templates/dashboard.html line ~545)
Modified service card rendering to show GUI buttons:

```javascript
} else if (service.running) {
    actionsHtml = `
        ${service.responsive && service.url ? `<a href="${service.url}" target="_blank" class="btn btn-link btn-small">🔗 Open Service</a>` : ''}
        ${service.gui_url ? `<a href="${service.gui_url}" target="_blank" class="btn btn-link btn-small" style="background: linear-gradient(135deg, #FA8BFF 0%, #2BD2FF 90%); color: white;">🎨 ${service.gui_name || 'GUI'}</a>` : ''}
        <button class="btn btn-stop btn-small" onclick="stopService('${key}')">⏹️ Stop</button>
    `;
}
```

### 4. Created Chatterbox GUI Startup Script
`scripts/start-chatterbox-gui.sh` - Launches the official Chatterbox voice cloning GUI on port 7861

## To Apply:

1. Restart dashboard: `./scripts/stop-dashboard.sh && ./scripts/start-dashboard.sh`
2. Start Chatterbox GUI: `./scripts/start-chatterbox-gui.sh`
3. Refresh browser (F5) on http://localhost:5000

## Result:

Each running service with a GUI will show a colorful **🎨 GUI** button with a pink-to-cyan gradient that opens the respective interface in a new tab.

## Troubleshooting:

If buttons don't appear:
- Clear browser cache (Ctrl+F5)
- Check API response: `curl http://localhost:5000/api/status | jq '.services.tts'`
- Verify gui_url is present in response
- Restart dashboard with: `pkill -f dashboard.py && ./scripts/start-dashboard.sh`
