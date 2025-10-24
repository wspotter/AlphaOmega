#!/bin/bash
# Start SearXNG privacy-respecting metasearch engine

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SEARXNG_DIR="${PROJECT_ROOT}/searxng"
PORT="${SEARXNG_PORT:-8181}"
BIND="${SEARXNG_BIND:-127.0.0.1}"
PID_FILE="${PROJECT_ROOT}/logs/searxng.pid"
LOG_FILE="${PROJECT_ROOT}/logs/searxng.log"

# Check if already running
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "SearXNG already running (PID: $OLD_PID) on ${BIND}:${PORT}."
        exit 0
    else
        rm -f "$PID_FILE"
    fi
fi

# Check if SearXNG exists
if [ ! -d "$SEARXNG_DIR" ]; then
    echo "❌ SearXNG not found at $SEARXNG_DIR"
    echo "Run: git clone https://github.com/searxng/searxng.git $SEARXNG_DIR"
    exit 1
fi

# Create venv if needed
if [ ! -d "${SEARXNG_DIR}/.venv" ]; then
    echo "Creating SearXNG virtual environment..."
    cd "${SEARXNG_DIR}"
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -e .
fi

# Create logs directory
mkdir -p "${PROJECT_ROOT}/logs"

# Create settings if needed  
if [ ! -f "${SEARXNG_DIR}/searx/settings.yml" ]; then
    echo "Creating SearXNG settings..."
    cp "${SEARXNG_DIR}/utils/templates/etc/searxng/settings.yml" "${SEARXNG_DIR}/searx/settings.yml"
fi

echo "Starting SearXNG on ${BIND}:${PORT}..."

# Start SearXNG
cd "${SEARXNG_DIR}"
export SEARXNG_SETTINGS_PATH="${SEARXNG_DIR}/searx/settings.yml"
export FLASK_APP=searx.webapp
nohup .venv/bin/flask run --host=${BIND} --port=${PORT} > "${LOG_FILE}" 2>&1 &

SEARXNG_PID=$!
echo "$SEARXNG_PID" > "$PID_FILE"

# Wait for startup
sleep 3

if ps -p "$SEARXNG_PID" > /dev/null 2>&1; then
    echo "✓ SearXNG started successfully!"
    echo "   PID: $SEARXNG_PID"
    echo "   URL: http://${BIND}:${PORT}"
    echo "   Logs: ${LOG_FILE}"
else
    echo "✗ Failed to start SearXNG. Check logs: ${LOG_FILE}"
    rm -f "$PID_FILE"
    exit 1
fi