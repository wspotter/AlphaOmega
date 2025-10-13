#!/bin/bash
# AlphaOmega MCP Bridge Startup Script
# Starts the MCP OpenAI Bridge for OpenWebUI integration

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BRIDGE_SCRIPT="$PROJECT_ROOT/agent_s/mcp/openai_bridge.py"
LOG_FILE="$PROJECT_ROOT/logs/openai-bridge.log"
PID_FILE="/tmp/mcp-openai-bridge.pid"

echo "========================================================================"
echo "🚀 Starting MCP OpenAI Bridge"
echo "========================================================================"

# Check if already running
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "⚠️  Bridge already running (PID: $OLD_PID)"
        echo "   Use './stop-mcp-bridge.sh' to stop it first"
        exit 1
    else
        rm "$PID_FILE"
    fi
fi

# Verify mcpart is in the correct location
if [ ! -f "$PROJECT_ROOT/mcpart/build/index.js" ]; then
    echo "❌ Error: mcpart not found at $PROJECT_ROOT/mcpart/build/index.js"
    echo "   Please ensure mcpart is in the AlphaOmega root directory"
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p "$PROJECT_ROOT/logs"

# Start the bridge
echo "📦 Starting Python OpenAI Bridge..."
echo "   Script: $BRIDGE_SCRIPT"
echo "   Log: $LOG_FILE"
echo ""

cd "$PROJECT_ROOT"
nohup python "$BRIDGE_SCRIPT" >> "$LOG_FILE" 2>&1 &
BRIDGE_PID=$!

echo $BRIDGE_PID > "$PID_FILE"

# Wait a moment for startup
sleep 3

# Check if it's running
if ps -p "$BRIDGE_PID" > /dev/null 2>&1; then
    echo "✅ Bridge started successfully!"
    echo "   PID: $BRIDGE_PID"
    echo "   URL: http://localhost:8002"
    echo ""
    
    # Test the connection
    echo "🧪 Testing connection..."
    if curl -s http://localhost:8002/ > /dev/null 2>&1; then
        TOOLS_COUNT=$(curl -s http://localhost:8002/ | grep -o '"tools_loaded":[0-9]*' | grep -o '[0-9]*')
        echo "✅ Bridge is responding!"
        echo "   Tools loaded: $TOOLS_COUNT"
        echo ""
        echo "========================================================================"
        echo "🎯 Add to OpenWebUI:"
        echo "   Settings → Connections → Add Connection"
        echo "   URL: http://localhost:8002"
        echo "   Type: OpenAI"
        echo "   Model: mcp-assistant"
        echo "========================================================================"
    else
        echo "⚠️  Bridge started but not responding yet"
        echo "   Check logs: tail -f $LOG_FILE"
    fi
else
    echo "❌ Failed to start bridge"
    echo "   Check logs: tail -f $LOG_FILE"
    rm "$PID_FILE"
    exit 1
fi
