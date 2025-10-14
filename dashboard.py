#!/usr/bin/env python3
"""
AlphaOmega Control Dashboard
Web-based startup/shutdown interface with real-time status monitoring
"""

import json
import os
import subprocess
import time
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, jsonify
import requests
import psutil

app = Flask(__name__)

# Configuration
PROJECT_DIR = Path("/home/stacy/AlphaOmega")

DEFAULT_SEARXNG_HASH = "cbc7656b6966d87f1d3f1cfe0adf59392f9152aa9cf8b9b7a7614016bb58fcc0"
SEARXNG_CONTAINER_ID = os.getenv("SEARXNG_CONTAINER_ID", "").strip()
SEARXNG_CONTAINERS = ["alphaomega-searxng", "searxng", DEFAULT_SEARXNG_HASH]
if SEARXNG_CONTAINER_ID:
    SEARXNG_CONTAINERS.append(SEARXNG_CONTAINER_ID)

SEARXNG_PORT = int(os.getenv("SEARXNG_PORT", "8181"))
COMFYUI_PORT = int(os.getenv("COMFYUI_PORT", "8188"))
COMFYUI_CONTAINERS = ["alphaomega-comfyui", "comfyui"]
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
        "name": "MCP OpenAPI Proxy",
        "port": 8002,
        "check_url": "http://localhost:8002/openapi.json",
        "start_cmd": f"{PROJECT_DIR}/scripts/start-mcp-unified.sh",
        "stop_cmd": f"{PROJECT_DIR}/scripts/stop-mcp-unified.sh",
        "process_name": "mcpo.*8002",
        "description": "Unified mcpo proxy exposing 76 MCP tools via OpenAPI",
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
    "searxng": {
        "name": "SearxNG",
        "port": SEARXNG_PORT,
        "check_url": f"http://localhost:{SEARXNG_PORT}",
        "start_cmd": f"{PROJECT_DIR}/scripts/start-searxng.sh",
        "stop_cmd": f"{PROJECT_DIR}/scripts/stop-searxng.sh",
        "process_name": None,
        "container_name": SEARXNG_CONTAINERS,
        "description": "Privacy-preserving meta search engine (Docker)",
        "status": "ready"
    },
    "comfyui": {
        "name": "ComfyUI",
        "port": COMFYUI_PORT,
        "check_url": f"http://localhost:{COMFYUI_PORT}/system_stats",
        "start_cmd": f"{PROJECT_DIR}/scripts/start-comfyui.sh",
        "stop_cmd": f"{PROJECT_DIR}/scripts/stop-comfyui.sh",
        "process_name": None,
        "container_name": COMFYUI_CONTAINERS,
        "description": "Advanced image generation (SDXL, Flux workflows) [Docker]",
        "status": "ready"
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
    
    # Check if process or container is running
    try:
        if service.get("container_name"):
            targets = service["container_name"]
            if not isinstance(targets, list):
                targets = [targets]
            container_id = None
            for target in targets:
                result = subprocess.run(
                    [
                        "docker",
                        "ps",
                        "-q",
                        "--filter",
                        f"name={target}"
                    ],
                    capture_output=True,
                    text=True
                )
                candidate = result.stdout.strip().split('\n')[0] if result.stdout.strip() else None
                if candidate:
                    container_id = candidate
                    break
            if container_id:
                status["container_id"] = container_id
                try:
                    state_result = subprocess.run(
                        [
                            "docker",
                            "inspect",
                            "--format",
                            "{{json .State}}",
                            container_id
                        ],
                        capture_output=True,
                        text=True
                    )
                    if state_result.returncode == 0 and state_result.stdout.strip():
                        state_data = json.loads(state_result.stdout.strip())
                        container_state = state_data.get("Status")
                        status["container_state"] = container_state
                        status["running"] = container_state == "running"
                        status["details"].update({
                            "state": container_state,
                            "restart_count": state_data.get("RestartCount"),
                            "last_exit_code": state_data.get("ExitCode"),
                            "last_error": state_data.get("Error") or None
                        })
                    else:
                        status["running"] = True
                except Exception as inspect_error:
                    status["running"] = True
                    status["details"]["inspect_error"] = str(inspect_error)
            else:
                status["running"] = False
        elif service.get("process_name"):
            result = subprocess.run(
                ["pgrep", "-f", service["process_name"]],
                capture_output=True,
                text=True
            )
            status["running"] = result.returncode == 0
            if status["running"]:
                status["pid"] = result.stdout.strip().split('\n')[0]
    except FileNotFoundError:
        status["error"] = "Docker not available"
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
