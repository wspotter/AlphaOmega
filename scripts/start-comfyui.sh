#!/bin/bash
# Start ComfyUI Docker container

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="$PROJECT_ROOT/docker-compose.yml"
CONTAINER_NAME="alphaomega-comfyui"
DEFAULT_CONTAINER_NAME="comfyui"
DEFAULT_IMAGE="alphaomega-comfyui"
PORT_VALUE="${COMFYUI_PORT:-8188}"

log() {
    printf '%s\n' "$1"
}

if ! command -v docker >/dev/null 2>&1; then
    log "Docker not installed. Cannot start ComfyUI."
    exit 1
fi

if docker compose version >/dev/null 2>&1; then
    COMPOSE_BIN=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
    COMPOSE_BIN=(docker-compose)
else
    log "Docker Compose not available. Install docker compose plugin or docker-compose."
    exit 1
fi

ACTIVE_CONTEXT="$(docker context show 2>/dev/null || echo default)"
if [ "$ACTIVE_CONTEXT" = "desktop-linux" ]; then
    if docker --context default info >/dev/null 2>&1; then
        log "Docker context 'desktop-linux' (Docker Desktop) cannot map /dev/kfd."
        log "Run 'docker context use default' to talk to the host docker engine, then retry start-comfyui.sh."
    else
        log "Active Docker context '$ACTIVE_CONTEXT' cannot access /dev/kfd. Switch to a context backed by the host engine before retrying."
    fi
    exit 1
fi

if [ ! -e /dev/kfd ]; then
    log "GPU device /dev/kfd not found. ROCm drivers are not loaded, so ComfyUI cannot access the MI50 GPUs."
    log "Run 'sudo modprobe amdkfd amdgpu' (requires ROCm stack) and retry start-comfyui.sh."
    exit 1
fi

# Detect existing running container by name or image
EXISTING_MATCH=""
while read -r cid cname; do
    if [ "$cname" = "$CONTAINER_NAME" ] || [ "$cname" = "$DEFAULT_CONTAINER_NAME" ]; then
        EXISTING_MATCH="$cname"
        break
    fi
    image_name=$(docker inspect --format='{{.Config.Image}}' "$cid" 2>/dev/null || true)
    if [ "$image_name" = "$DEFAULT_IMAGE" ]; then
        EXISTING_MATCH="$cname"
        break
    fi
done < <(docker ps --format '{{.ID}} {{.Names}}')

if [ -n "$EXISTING_MATCH" ]; then
    log "ComfyUI container already running (${EXISTING_MATCH})."
    exit 0
fi

if lsof -Pi :$PORT_VALUE -sTCP:LISTEN -t >/dev/null 2>&1; then
    log "Port $PORT_VALUE already in use. Skipping ComfyUI startup."
    exit 0
fi

"${COMPOSE_BIN[@]}" -f "$COMPOSE_FILE" up -d comfyui

if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    log "ComfyUI started on http://localhost:${PORT_VALUE}/"
else
    log "Failed to start ComfyUI container."
    exit 1
fi
