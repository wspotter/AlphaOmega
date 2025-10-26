#!/bin/bash
# Stop SearXNG search engine

set -e

echo "Stopping SearXNG..."

# Check if running as system service
if systemctl list-unit-files | grep -q "^searxng.service"; then
    sudo systemctl stop searxng 2>/dev/null || true
    sudo systemctl stop uwsgi 2>/dev/null || true
    echo "✓ SearXNG system service stopped"
else
    echo "SearXNG not installed as system service"
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PID_FILE="${PROJECT_ROOT}/logs/searxng.pid"
VALKEY_PID_FILE="${PROJECT_ROOT}/logs/valkey.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE" 2>/dev/null || true)
    if [ -n "$PID" ] && ps -p "$PID" > /dev/null 2>&1; then
        kill "$PID" 2>/dev/null || true
        for _ in {1..10}; do
            if ! ps -p "$PID" > /dev/null 2>&1; then
                break
            fi
            sleep 0.5
        done
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "⚠️ Unable to stop local SearXNG process (PID $PID)."
        else
            echo "✓ Stopped local SearXNG process (PID $PID)."
        fi
    fi
    rm -f "$PID_FILE"
fi

if [ -f "$VALKEY_PID_FILE" ]; then
    VALKEY_PID=$(cat "$VALKEY_PID_FILE" 2>/dev/null || true)
    if [ -n "$VALKEY_PID" ] && ps -p "$VALKEY_PID" > /dev/null 2>&1; then
        kill "$VALKEY_PID" 2>/dev/null || true
        for _ in {1..10}; do
            if ! ps -p "$VALKEY_PID" > /dev/null 2>&1; then
                break
            fi
            sleep 0.5
        done
        if ps -p "$VALKEY_PID" > /dev/null 2>&1; then
            echo "⚠️ Unable to stop local Valkey/Redis process (PID $VALKEY_PID)."
        else
            echo "✓ Stopped local Valkey/Redis process (PID $VALKEY_PID)."
        fi
    fi
    rm -f "$VALKEY_PID_FILE"
fi

exit 0