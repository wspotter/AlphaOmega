#!/usr/bin/env python3
"""AlphaOmega Control Dashboard
Web-based startup/shutdown interface with real-time status monitoring"""

import json
import os
import shutil
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
LOG_DIR = PROJECT_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

DEFAULT_SEARXNG_HASH = "cbc7656b6966d87f1d3f1cfe0adf59392f9152aa9cf8b9b7a7614016bb58fcc0"
SEARXNG_CONTAINER_ID = os.getenv("SEARXNG_CONTAINER_ID", "").strip()
SEARXNG_CONTAINERS = ["alphaomega-searxng", "searxng", DEFAULT_SEARXNG_HASH]
if SEARXNG_CONTAINER_ID:
    SEARXNG_CONTAINERS.append(SEARXNG_CONTAINER_ID)

SEARXNG_PORT = int(os.getenv("SEARXNG_PORT", "8181"))
COMFYUI_PORT = int(os.getenv("COMFYUI_PORT", "8188"))
CHATTERBOX_CONTAINER = ["alphaomega-chatterbox"]

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
        "start_cmd": None,
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
    "mcpart_dashboard": {
        "name": "MCPART Dashboard",
        "port": 3000,
        "check_url": "http://localhost:3000",
        "start_cmd": f"{PROJECT_DIR}/scripts/start-mcpart-dashboard.sh",
        "stop_cmd": f"{PROJECT_DIR}/scripts/stop-mcpart-dashboard.sh",
        "process_name": None,
        "pid_file": PROJECT_DIR / "logs" / "mcpart-dashboard.pid",
        "description": "Web UI for exploring MCP tools and stats",
        "status": "ready"
    },
    "tts": {
        "name": "Chatterbox TTS",
        "port": 5003,
        "check_url": "http://localhost:5003/health",
        "start_cmd": f"{PROJECT_DIR}/scripts/start-tts.sh",
        "stop_cmd": f"{PROJECT_DIR}/scripts/stop-tts.sh",
        "process_name": None,
        "container_name": CHATTERBOX_CONTAINER,
        "description": "Dockerized Chatterbox TTS service with OpenAI-compatible API",
        "status": "ready"
    },
    "searxng": {
        "name": "SearxNG",
        "port": SEARXNG_PORT,
        "check_url": f"http://localhost:{SEARXNG_PORT}",
        "start_cmd": f"{PROJECT_DIR}/scripts/start-searxng.sh",
        "stop_cmd": f"{PROJECT_DIR}/scripts/stop-searxng.sh",
        "process_name": None,
        "pid_file": PROJECT_DIR / "logs" / "searxng.pid",
        "description": "Privacy-preserving meta search engine",
        "status": "ready"
    },
    "comfyui": {
        "name": "ComfyUI",
        "port": COMFYUI_PORT,
        "check_url": f"http://localhost:{COMFYUI_PORT}/system_stats",
        "start_cmd": f"{PROJECT_DIR}/scripts/start-comfyui.sh",
        "stop_cmd": f"{PROJECT_DIR}/scripts/stop-comfyui.sh",
        "process_name": None,
        "pid_file": PROJECT_DIR / "logs" / "comfyui.pid",
        "description": "Advanced image generation (SDXL, Flux workflows)",
        "status": "ready"
    },
    "agents": {
        "name": "Agent-S",
        "port": 8001,
        "check_url": "http://localhost:8001/health",
        "start_cmd": f"{PROJECT_DIR}/scripts/start-agent-s.sh",
        "stop_cmd": f"{PROJECT_DIR}/scripts/stop-agent-s.sh",
        "process_name": "agent_s/server.py",
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
    """Check if a service is running and responsive."""
    service = SERVICES[service_key]

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

    try:
        if service.get("container_name"):
            targets = service["container_name"]
            if not isinstance(targets, list):
                targets = [targets]
            container_id = None
            for target in targets:
                result = subprocess.run(
                    ["docker", "ps", "-q", "--filter", f"name={target}"],
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    status["details"]["docker_error"] = result.stderr.strip()
                    continue
                candidate = result.stdout.strip().split("\n")[0] if result.stdout.strip() else None
                if candidate:
                    container_id = candidate
                    break
            if container_id:
                status["container_id"] = container_id
                try:
                    state_result = subprocess.run(
                        ["docker", "inspect", "--format", "{{json .State}}", container_id],
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

        if not status["running"] and service.get("pid_file"):
            pid_path = Path(service["pid_file"])
            try:
                if pid_path.exists():
                    pid_raw = pid_path.read_text(encoding="utf-8").strip().splitlines()
                    pid_value = pid_raw[-1] if pid_raw else ""
                    if pid_value:
                        try:
                            pid_int = int(pid_value)
                            if psutil.pid_exists(pid_int):
                                status["running"] = True
                                status["pid"] = pid_value
                            else:
                                status["details"]["pid_file_status"] = "stale"
                        except ValueError:
                            status["details"]["pid_file_error"] = "invalid pid"
                    else:
                        status["details"]["pid_file_status"] = "empty"
            except Exception as pid_error:
                status["details"]["pid_file_error"] = str(pid_error)

        if not status["running"] and service.get("process_name"):
            result = subprocess.run(
                ["pgrep", "-f", service["process_name"]],
                capture_output=True,
                text=True
            )
            status["running"] = result.returncode == 0
            if status["running"]:
                status["pid"] = result.stdout.strip().split("\n")[0]
    except FileNotFoundError:
        status["error"] = "Docker not available"
    except Exception as exc:
        status["error"] = str(exc)

    response = None
    if service.get("check_url"):
        try:
            response = requests.get(service["check_url"], timeout=2)
            status["http_status"] = response.status_code
            status["responsive"] = response.status_code == 200
            status["running"] = True

            data = None
            if status["responsive"] and response.headers.get("content-type", "").startswith("application/json"):
                try:
                    data = response.json()
                except ValueError:
                    data = None

            if service_key == "ollama" and status["responsive"] and data:
                status["details"]["models"] = len(data.get("models", []))
            elif service_key == "mcp" and status["responsive"] and data:
                status["details"]["tools"] = len(data.get("paths", {}))
            elif service_key == "tts" and status["responsive"]:
                if data:
                    status["details"]["health"] = data
                else:
                    status["details"]["raw"] = response.text.strip()[:200]
            elif service_key == "agents" and status["responsive"] and data:
                services_info = data.get("services", {}) or {}
                config_info = data.get("config", {}) or {}
                status["details"].update({
                    "agent_status": data.get("status"),
                    "capabilities": services_info,
                    "vision_model": config_info.get("vision_model"),
                    "safe_mode": config_info.get("safe_mode"),
                    "ollama_host": config_info.get("ollama_host")
                })
        except Exception as exc:
            status["responsive"] = False
            if "error" not in status:
                status["error"] = str(exc)

    return status


def get_system_stats():
    """Return host CPU, memory, disk, and uptime statistics."""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    return {
        "cpu": {
            "percent": cpu_percent,
            "cores": psutil.cpu_count()
        },
        "memory": {
            "used_gb": round(memory.used / (1024 ** 3), 2),
            "total_gb": round(memory.total / (1024 ** 3), 2),
            "percent": memory.percent
        },
        "disk": {
            "used_gb": round(disk.used / (1024 ** 3), 2),
            "total_gb": round(disk.total / (1024 ** 3), 2),
            "percent": disk.percent
        },
        "uptime": time.time() - psutil.boot_time()
    }


def build_status_payload():
    """Assemble the status payload shared across endpoints."""
    return {
        "timestamp": datetime.now().isoformat(),
        "services": {key: check_service_status(key) for key in SERVICES},
        "system": get_system_stats()
    }


@app.route("/")
def index():
    """Main dashboard page."""
    return render_template("dashboard.html")


@app.route("/api/status")
def get_status():
    """Get current status of all services."""
    return jsonify(build_status_payload())


@app.route("/api/start/<service>")
def start_service(service):
    """Start a specific service."""
    if service not in SERVICES:
        return jsonify({"error": "Unknown service"}), 404

    service_config = SERVICES[service]

    if not service_config["start_cmd"]:
        return jsonify({"error": "Service cannot be started via dashboard"}), 400

    log_file = LOG_DIR / f"{service}.log"

    try:
        with open(log_file, "a") as logfile:
            subprocess.Popen(
                service_config["start_cmd"],
                shell=True,
                stdout=logfile,
                stderr=logfile,
                preexec_fn=os.setsid
            )
        time.sleep(2)
        return jsonify({
            "success": True,
            "message": f"{service_config['name']} started",
            "status": check_service_status(service)
        })
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/stop/<service>")
def stop_service(service):
    """Stop a specific service."""
    if service not in SERVICES:
        return jsonify({"error": "Unknown service"}), 404

    service_config = SERVICES[service]

    if not service_config["stop_cmd"]:
        return jsonify({"error": "Service cannot be stopped via dashboard"}), 400

    try:
        subprocess.run(service_config["stop_cmd"], shell=True, check=True)
        time.sleep(1)
        return jsonify({
            "success": True,
            "message": f"{service_config['name']} stopped",
            "status": check_service_status(service)
        })
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/start_all")
def start_all():
    """Start all services with available start commands."""
    results = {}
    for key, service in SERVICES.items():
        if service["start_cmd"]:
            log_file = LOG_DIR / f"{key}.log"
            try:
                with open(log_file, "a") as logfile:
                    subprocess.Popen(
                        service["start_cmd"],
                        shell=True,
                        stdout=logfile,
                        stderr=logfile,
                        preexec_fn=os.setsid
                    )
                results[key] = "starting"
            except Exception as exc:
                results[key] = f"error: {exc}"
    time.sleep(3)
    return jsonify({"results": results, "status": build_status_payload()})


@app.route("/api/stop_all")
def stop_all():
    """Stop all services with stop commands."""
    results = {}
    for key, service in SERVICES.items():
        if service["stop_cmd"]:
            try:
                subprocess.run(service["stop_cmd"], shell=True, check=True)
                results[key] = "stopped"
            except Exception as exc:
                results[key] = f"error: {exc}"
    time.sleep(1)
    return jsonify({"results": results, "status": build_status_payload()})


@app.route("/api/logs/<service>")
def get_logs(service):
    """Return recent logs for a service."""
    log_files = {
        "mcp": PROJECT_DIR / "logs" / "mcp-unified.log",
        "ollama": PROJECT_DIR / "logs" / "ollama-vision.log"
    }

    if service == "tts":
        if not shutil.which("docker"):
            return jsonify({"error": "Docker not available"}), 503
        for container_name in CHATTERBOX_CONTAINER:
            try:
                result = subprocess.run(
                    ["docker", "logs", "--tail", "50", container_name],
                    capture_output=True,
                    text=True,
                    check=False
                )
                if result.returncode == 0:
                    return jsonify({"lines": result.stdout.splitlines()})
            except FileNotFoundError:
                return jsonify({"error": "Docker not available"}), 503
        return jsonify({"error": "Chatterbox container not running"}), 404

    if service not in log_files:
        return jsonify({"error": "Unknown service"}), 404

    log_file = log_files[service]

    if not log_file.exists():
        return jsonify({"lines": []})

    try:
        result = subprocess.run(["tail", "-50", str(log_file)], capture_output=True, text=True)
        return jsonify({"lines": result.stdout.splitlines()})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
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

    app.run(host="0.0.0.0", port=5000, debug=False)
