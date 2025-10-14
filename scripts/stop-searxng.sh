#!/bin/bash
# Stop SearxNG Docker container

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="$PROJECT_ROOT/docker-compose.yml"
CONTAINER_NAME="alphaomega-searxng"

DEFAULT_CONTAINER_HASH="cbc7656b6966d87f1d3f1cfe0adf59392f9152aa9cf8b9b7a7614016bb58fcc0"

TARGET_IDENTIFIERS=("alphaomega-searxng" "searxng" "$DEFAULT_CONTAINER_HASH")
if [ -n "${SEARXNG_CONTAINER_ID:-}" ]; then
    TARGET_IDENTIFIERS+=("$SEARXNG_CONTAINER_ID")
fi

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
    for target in "${TARGET_IDENTIFIERS[@]}"; do
        if [ "$cid" = "$target" ] || [ "$cname" = "$target" ]; then
            TARGET_CONTAINER="${cname:-$cid}"
            break 2
        fi
    done
done < <(docker ps --format '{{.ID}} {{.Names}}')

if [ -z "$TARGET_CONTAINER" ]; then
    ALT_CONTAINER="$(docker ps --filter ancestor=searxng/searxng --format '{{.Names}}' | head -n 1)"
    if [ -n "$ALT_CONTAINER" ]; then
        TARGET_CONTAINER="$ALT_CONTAINER"
    fi
fi

if [ -z "$TARGET_CONTAINER" ]; then
    log "SearxNG container not running."
    exit 0
fi

if [ "$TARGET_CONTAINER" = "$CONTAINER_NAME" ]; then
    "${COMPOSE_BIN[@]}" -f "$COMPOSE_FILE" stop searxng >/dev/null
else
    docker stop "$TARGET_CONTAINER" >/dev/null
fi

if docker ps --format '{{.Names}}' | grep -q "^${TARGET_CONTAINER}$"; then
    log "Failed to stop $TARGET_CONTAINER."
else
    log "SearxNG container stopped."
fi
