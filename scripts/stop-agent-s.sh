#!/bin/bash
# Stop Agent-S (Computer Use Automation)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "${SCRIPT_DIR}")"
LOG_DIR="$PROJECT_DIR/logs"
PID_FILE="$LOG_DIR/agent-s.pid"

if [ -f "$PID_FILE" ]; then
    AGENT_PID="$(cat "$PID_FILE")"
    if [[ -n "$AGENT_PID" ]] && kill -0 "$AGENT_PID" 2>/dev/null; then
    echo "Stopping Agent-S (PID: $AGENT_PID)"
        kill "$AGENT_PID" 2>/dev/null || true
        for attempt in {1..5}; do
            if ! kill -0 "$AGENT_PID" 2>/dev/null; then
                break
            fi
            sleep 1
        done
        if kill -0 "$AGENT_PID" 2>/dev/null; then
            echo "Agent-S still running, sending SIGKILL"
            kill -9 "$AGENT_PID" 2>/dev/null || true
        fi
    fi
    rm -f "$PID_FILE"
fi

# Fall back to pattern match in case PID file is stale
pkill -f "agent_s/server.py" 2>/dev/null || true

# Clean up Xvfb instances spawned by Agent-S
pkill -f "xvfb-run .*agent_s/server.py" 2>/dev/null || true

echo "Agent-S stopped"
