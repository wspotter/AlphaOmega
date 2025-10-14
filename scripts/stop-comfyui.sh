#!/bin/bash
# Stop ComfyUI Docker container

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="$PROJECT_ROOT/docker-compose.yml"
CONTAINER_NAME="alphaomega-comfyui"
DEFAULT_CONTAINER_NAME="comfyui"

log() {
    printf '%s\n' "$1"
}

if ! command -v docker >/dev/null 2>&1; then
    log "Docker not installed. Nothing to stop."
    exit 0
fi

if docker compose version >/dev/null 2>&1; then
    COMPOSE_BIN=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
    COMPOSE_BIN=(docker-compose)
else
    log "Docker Compose not available."
    exit 0
fi

TARGET_CONTAINER=""
while read -r cid cname; do
    if [ "$cname" = "$CONTAINER_NAME" ] || [ "$cname" = "$DEFAULT_CONTAINER_NAME" ]; then
        TARGET_CONTAINER="$cname"
        break
    fi
done < <(docker ps --format '{{.ID}} {{.Names}}')

if [ -z "$TARGET_CONTAINER" ]; then
    log "ComfyUI container not running."
    exit 0
fi

if [ "$TARGET_CONTAINER" = "$CONTAINER_NAME" ]; then
    "${COMPOSE_BIN[@]}" -f "$COMPOSE_FILE" stop comfyui >/dev/null
else
    docker stop "$TARGET_CONTAINER" >/dev/null
fi

if docker ps --format '{{.Names}}' | grep -q "^${TARGET_CONTAINER}$"; then
    log "Failed to stop $TARGET_CONTAINER."
else
    log "ComfyUI container stopped."
fi
