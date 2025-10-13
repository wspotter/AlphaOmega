#!/bin/bash
# AlphaOmega MCP Bridge Stop Script

PID_FILE="/tmp/mcp-openai-bridge.pid"

echo "========================================================================"
echo "🛑 Stopping MCP OpenAI Bridge"
echo "========================================================================"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "   Stopping bridge (PID: $PID)..."
        kill "$PID"
        sleep 2
        
        # Force kill if still running
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "   Force stopping..."
            kill -9 "$PID"
        fi
        
        rm "$PID_FILE"
        echo "✅ Bridge stopped successfully"
    else
        echo "⚠️  Bridge not running (stale PID file)"
        rm "$PID_FILE"
    fi
else
    echo "⚠️  Bridge not running (no PID file found)"
    
    # Try to kill by name anyway
    if pkill -f "openai_bridge.py"; then
        echo "✅ Stopped orphaned bridge process"
    fi
fi

echo "========================================================================"
