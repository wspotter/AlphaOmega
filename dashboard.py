#!/usr/bin/env python3
"""
AlphaOmega Control Dashboard
Web-based startup/shutdown interface with real-time status monitoring
"""

import subprocess
import json
import time
import os
import signal
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, jsonify, request
import requests
import psutil

app = Flask(__name__)

# Configuration
PROJECT_DIR = Path("/home/stacy/AlphaOmega")
SERVICES = {
    "openwebui": {
        "name": "OpenWebUI",
        "port": 8080,
        "check_url": "http://localhost:8080",
        "start_cmd": f"{PROJECT_DIR}/scripts/start-openwebui.sh",
        "stop_cmd": "pkill -f 'open-webui'",
        "process_name": "open-webui",
        "description": "Unified web interface for all AI interactions",
        "status": "ready"
    },
    "ollama": {
        "name": "Ollama",
        "port": 11434,
        "check_url": "http://localhost:11434/api/tags",
        "start_cmd": None,  # Already running
        "stop_cmd": "pkill ollama",
        "process_name": "ollama",
        "description": "LLM inference engine with 25+ models",
        "status": "ready"
    },
    "mcp": {
        "name": "MCP OpenAI Bridge",
        "port": 8002,
        "check_url": "http://localhost:8002/health",
        "start_cmd": f"{PROJECT_DIR}/scripts/start-mcp-bridge.sh",
        "stop_cmd": f"{PROJECT_DIR}/scripts/stop-mcp-bridge.sh",
        "process_name": "openai_bridge.py",
        "description": "Bridge exposing 76 MCP tools + OpenAI chat with auto tool calls",
        "status": "ready"
    },
    "tts": {
        "name": "Coqui TTS",
        "port": 5002,
        "check_url": "http://localhost:5002/health",
        "start_cmd": f"{PROJECT_DIR}/tts/start_coqui_api.sh",
        "stop_cmd": f"{PROJECT_DIR}/tts/stop_coqui_api.sh",
        "process_name": "coqui_api.py",
        "description": "Professional text-to-speech with voice cloning",
        "status": "ready"
    },
    "comfyui": {
        "name": "ComfyUI",
        "port": 8188,
        "check_url": "http://localhost:8188/system_stats",
        "start_cmd": None,  # TODO: Add startup script
        "stop_cmd": "pkill -f 'comfyui.*8188'",
        "process_name": "comfyui",
        "description": "Advanced image generation (SDXL, Flux workflows)",
        "status": "development"
    },
    "agents": {
        "name": "Agent-S",
        "port": 8001,
        "check_url": "http://localhost:8001/health",
        "start_cmd": f"{PROJECT_DIR}/agent_s/server.py",
        "stop_cmd": "pkill -f 'agent_s/server.py'",
        "process_name": "server.py",
        "description": "Computer use automation (screen, mouse, keyboard)",
        "status": "development"
    },
    "vip": {
        "name": "VIP System",
        "port": None,
        "check_url": None,
        "start_cmd": None,
        "stop_cmd": None,
        "process_name": None,
        "description": "Next integration: https://github.com/wspotter/VIP",
        "status": "planned"
    }
}


def check_service_status(service_key):
    """Check if a service is running and responsive"""
    service = SERVICES[service_key]
    
    # Handle planned/development services
    if service.get("status") == "planned":
        return {
            "name": service["name"],
            "port": service["port"],
            "running": False,
            "responsive": False,
            "details": {},
            "url": None,
            "description": service["description"],
            "status": "planned"
        }
    
    status = {
        "name": service["name"],
        "port": service["port"],
        "running": False,
        "responsive": False,
        "details": {},
        "url": f"http://localhost:{service['port']}" if service['port'] else None,
        "description": service["description"],
        "status": service.get("status", "ready")
    }
    
    # Check if process is running
    try:
        if service["process_name"]:
            result = subprocess.run(
                ["pgrep", "-f", service["process_name"]],
                capture_output=True,
                text=True
            )
            status["running"] = result.returncode == 0
            if status["running"]:
                status["pid"] = result.stdout.strip().split('\n')[0]
    except Exception as e:
        status["error"] = str(e)
    
    # Check if service is responsive
    if status["running"]:
        try:
            response = requests.get(service["check_url"], timeout=2)
            status["responsive"] = response.status_code == 200
            
            # Get service-specific details
            if service_key == "ollama" and status["responsive"]:
                data = response.json()
                status["details"]["models"] = len(data.get("models", []))
                
            elif service_key == "mcp" and status["responsive"]:
                data = response.json()
                status["details"]["tools"] = len(data.get("paths", {}))
                
            elif service_key == "tts" and status["responsive"]:
                data = response.json()
                status["details"]["status"] = data.get("status", "unknown")
                # Try to fetch Coqui voices
                try:
                    v = requests.get("http://localhost:5002/v1/voices", timeout=2).json()
                    voices = [item.get("id") for item in v.get("voices", [])]
                    status["details"]["voices"] = voices
                    # Curated downloadable names (for user convenience)
                    status["details"]["downloadable"] = [
                        "ljspeech",
                        "vctk",
                        "jenny",
                        "custom"
                    ]
                except Exception:
                    pass
                
        except Exception as e:
            status["responsive"] = False
            status["error"] = str(e)
    
    return status


def get_system_stats():
    """Get system resource usage"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "cpu": {
            "percent": cpu_percent,
            "cores": psutil.cpu_count()
        },
        "memory": {
            "used_gb": round(memory.used / (1024**3), 2),
            "total_gb": round(memory.total / (1024**3), 2),
            "percent": memory.percent
        },
        "disk": {
            "used_gb": round(disk.used / (1024**3), 2),
            "total_gb": round(disk.total / (1024**3), 2),
            "percent": disk.percent
        },
        "uptime": time.time() - psutil.boot_time()
    }


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')


@app.route('/api/status')
def get_status():
    """Get current status of all services"""
    status = {
        "timestamp": datetime.now().isoformat(),
        "services": {},
        "system": get_system_stats()
    }
    
    for key in SERVICES:
        status["services"][key] = check_service_status(key)
    
    return jsonify(status)


@app.route('/api/start/<service>')
def start_service(service):
    """Start a specific service"""
    if service not in SERVICES:
        return jsonify({"error": "Unknown service"}), 404
    
    service_config = SERVICES[service]
    
    if not service_config["start_cmd"]:
        return jsonify({"error": "Service cannot be started via dashboard"}), 400
    
    try:
        subprocess.Popen(
            service_config["start_cmd"],
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(2)  # Give service time to start
        
        return jsonify({
            "success": True,
            "message": f"{service_config['name']} started",
            "status": check_service_status(service)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/stop/<service>')
def stop_service(service):
    """Stop a specific service"""
    if service not in SERVICES:
        return jsonify({"error": "Unknown service"}), 404
    
    service_config = SERVICES[service]
    
    try:
        subprocess.run(
            service_config["stop_cmd"],
            shell=True,
            check=True
        )
        time.sleep(1)
        
        return jsonify({
            "success": True,
            "message": f"{service_config['name']} stopped",
            "status": check_service_status(service)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/start_all')
def start_all():
    """Start all services"""
    results = {}
    
    for key, service in SERVICES.items():
        if service["start_cmd"]:
            try:
                subprocess.Popen(
                    service["start_cmd"],
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                results[key] = "starting"
            except Exception as e:
                results[key] = f"error: {str(e)}"
    
    time.sleep(3)
    return jsonify({"results": results, "status": get_status().json})


@app.route('/api/stop_all')
def stop_all():
    """Stop all services"""
    results = {}
    
    for key, service in SERVICES.items():
        if service["stop_cmd"]:
            try:
                subprocess.run(service["stop_cmd"], shell=True, check=True)
                results[key] = "stopped"
            except Exception as e:
                results[key] = f"error: {str(e)}"
    
    time.sleep(1)
    return jsonify({"results": results, "status": get_status().json})


@app.route('/api/logs/<service>')
def get_logs(service):
    """Get recent logs for a service"""
    log_files = {
        "mcp": PROJECT_DIR / "logs" / "mcp-unified.log",
        "tts": PROJECT_DIR / "logs" / "coqui_tts.log",
        "ollama": PROJECT_DIR / "logs" / "ollama-vision.log"
    }
    
    if service not in log_files:
        return jsonify({"error": "Unknown service"}), 404
    
    log_file = log_files[service]
    
    if not log_file.exists():
        return jsonify({"lines": []})
    
    try:
        # Get last 50 lines
        result = subprocess.run(
            ["tail", "-50", str(log_file)],
            capture_output=True,
            text=True
        )
        lines = result.stdout.split('\n')
        
        return jsonify({"lines": lines})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    templates_dir = Path(__file__).parent / "templates"
    templates_dir.mkdir(exist_ok=True)
    
    print("=" * 60)
    print("AlphaOmega Control Dashboard")
    print("=" * 60)
    print()
    print("Starting dashboard on http://localhost:5000")
    print()
    print("Features:")
    print("  - Real-time service status monitoring")
    print("  - Start/Stop individual services")
    print("  - System resource monitoring")
    print("  - Service logs viewer")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()
    
    app.run(host='0.0.0.0', port=5000, debug=False)
