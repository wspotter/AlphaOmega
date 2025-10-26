#!/bin/bash
# Stop the MCPART dashboard (Node/Express)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PID_FILE="${PROJECT_ROOT}/logs/mcpart-dashboard.pid"
LOG_FILE="${PROJECT_ROOT}/logs/mcpart-dashboard.log"

stop_pid() {
    local pid="$1"
    if [ -z "$pid" ]; then
        return
    fi
    if ps -p "$pid" > /dev/null 2>&1; then
        echo "⏹️  Stopping MCPART dashboard (PID: $pid)..."
        kill "$pid" 2>/dev/null || true
        sleep 2
        if ps -p "$pid" > /dev/null 2>&1; then
            echo "⚠️  Force killing MCPART dashboard (PID: $pid)"
            kill -9 "$pid" 2>/dev/null || true
        fi
    fi
}

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE" 2>/dev/null || true)
    stop_pid "$PID"
    rm -f "$PID_FILE"
else
    echo "No PID file found, searching for process..."
    PID=$(pgrep -f "mcpart/.*/build/dashboard.js" || true)
    if [ -n "$PID" ]; then
        stop_pid "$PID"
    else
        PID=$(pgrep -f "node .*build/dashboard.js" || true)
        if [ -n "$PID" ]; then
            stop_pid "$PID"
        else
            echo "MCPART dashboard not running."
            exit 0
        fi
    fi
fi

echo "✓ MCPART dashboard stopped. Logs: $LOG_FILE"
