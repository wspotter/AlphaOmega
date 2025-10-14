#!/bin/bash
# Start SearxNG Docker container

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="$PROJECT_ROOT/docker-compose.yml"
CONTAINER_NAME="alphaomega-searxng"

DEFAULT_CONTAINER_HASH="cbc7656b6966d87f1d3f1cfe0adf59392f9152aa9cf8b9b7a7614016bb58fcc0"

# Allow explicit container ID override (defaults include known hash)
TARGET_IDENTIFIERS=("alphaomega-searxng" "searxng" "$DEFAULT_CONTAINER_HASH")
if [ -n "${SEARXNG_CONTAINER_ID:-}" ]; then
    TARGET_IDENTIFIERS+=("$SEARXNG_CONTAINER_ID")
fi

log() {
    printf '%s\n' "$1"
}

if ! command -v docker >/dev/null 2>&1; then
    log "Docker not installed. Cannot start SearxNG."
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

ENV_FILE="$PROJECT_ROOT/.env"
if [ -f "$ENV_FILE" ]; then
    # shellcheck disable=SC1090
    set -a
    source "$ENV_FILE"
    set +a
fi

PORT_VALUE="${SEARXNG_PORT:-8181}"

# Return if a matching container is already running
EXISTING_MATCH=""
while read -r cid cname; do
    for target in "${TARGET_IDENTIFIERS[@]}"; do
        if [ "$cid" = "$target" ] || [ "$cname" = "$target" ]; then
            EXISTING_MATCH="${cname:-$cid}"
            break 2
        fi
    done
done < <(docker ps --format '{{.ID}} {{.Names}}')

if [ -n "$EXISTING_MATCH" ]; then
    log "SearxNG container already running (${EXISTING_MATCH})."
    exit 0
fi

EXISTING_CONTAINER="$(docker ps --filter ancestor=searxng/searxng --format '{{.Names}}' | head -n 1)"
if [ -n "$EXISTING_CONTAINER" ]; then
    log "SearxNG container already running (${EXISTING_CONTAINER})."
    exit 0
fi

if lsof -Pi :$PORT_VALUE -sTCP:LISTEN -t >/dev/null 2>&1; then
    log "Port $PORT_VALUE already in use. Skipping SearxNG startup."
    exit 0
fi

"${COMPOSE_BIN[@]}" -f "$COMPOSE_FILE" up -d searxng

if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    log "SearxNG started on http://localhost:${PORT_VALUE}/"
else
    log "Failed to start SearxNG container."
    exit 1
fi
