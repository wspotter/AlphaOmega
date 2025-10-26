#!/bin/bash
# Start the MCPART dashboard (Node/Express)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
MCPART_DIR="${PROJECT_ROOT}/mcpart"
PID_FILE="${PROJECT_ROOT}/logs/mcpart-dashboard.pid"
LOG_FILE="${PROJECT_ROOT}/logs/mcpart-dashboard.log"

mkdir -p "${PROJECT_ROOT}/logs"

if [ ! -d "$MCPART_DIR" ]; then
    echo "❌ MCPART directory not found at $MCPART_DIR"
    echo "Run: git submodule update --init mcpart"
    exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
    echo "❌ npm is required to start the MCPART dashboard"
    exit 1
fi

if [ -f "$PID_FILE" ]; then
    EXISTING_PID=$(cat "$PID_FILE" 2>/dev/null || true)
    if [ -n "$EXISTING_PID" ] && ps -p "$EXISTING_PID" > /dev/null 2>&1; then
        echo "MCPART dashboard already running (PID: $EXISTING_PID)."
        exit 0
    else
        rm -f "$PID_FILE"
    fi
fi

: > "$LOG_FILE"

pushd "$MCPART_DIR" >/dev/null

if [ ! -d "node_modules" ]; then
    echo "📦 Installing MCPART dependencies..."
    npm install >> "$LOG_FILE" 2>&1
fi

echo "🔨 Building MCPART dashboard..."
npm run build >> "$LOG_FILE" 2>&1

echo "🚀 Launching MCPART dashboard on http://localhost:3000..."
nohup npm run dashboard >> "$LOG_FILE" 2>&1 &
MCPART_PID=$!

popd >/dev/null

echo "$MCPART_PID" > "$PID_FILE"

sleep 2
if ps -p "$MCPART_PID" > /dev/null 2>&1; then
    echo "✓ MCPART dashboard started (PID: $MCPART_PID)"
    echo "   Logs: $LOG_FILE"
else
    echo "✗ Failed to start MCPART dashboard. Check logs: $LOG_FILE"
    rm -f "$PID_FILE"
    exit 1
fi
