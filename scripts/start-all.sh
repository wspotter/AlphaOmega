#!/bin/bash
# Start All AlphaOmega Services
# This script starts: Ollama, OpenWebUI, MCP Server, Agent-S

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=================================================="
echo "Starting AlphaOmega Stack"
echo "=================================================="
echo ""

# Load environment
if [ -f "$PROJECT_DIR/.env" ]; then
    source "$PROJECT_DIR/.env"
fi

# Export ROCm settings
export HSA_OVERRIDE_GFX_VERSION=9.0.0

# Create log directory
mkdir -p "$PROJECT_DIR/logs"

# Function to check if port is in use
port_in_use() {
    lsof -i:$1 > /dev/null 2>&1
}

# Function to start service in background
start_service() {
    local name=$1
    local command=$2
    local port=$3
    local logfile="$PROJECT_DIR/logs/${name}.log"
    
    if port_in_use $port; then
        echo -e "${YELLOW}⚠ $name already running on port $port${NC}"
    else
        echo -e "${BLUE}Starting $name on port $port...${NC}"
        eval "$command" > "$logfile" 2>&1 &
        local pid=$!
        echo $pid > "$PROJECT_DIR/logs/${name}.pid"
        sleep 2
        if ps -p $pid > /dev/null; then
            echo -e "${GREEN}✓ $name started (PID: $pid)${NC}"
        else
            echo -e "${RED}✗ $name failed to start. Check $logfile${NC}"
        fi
    fi
}

echo ""
echo "==> Step 1: Starting Ollama..."
echo ""

# Set GPU for Ollama (use GPU 1 - MI50 #1)
export ROCR_VISIBLE_DEVICES=1

if ! pgrep -x "ollama" > /dev/null; then
    start_service "ollama" "ollama serve" 11434
else
    echo -e "${GREEN}✓ Ollama already running${NC}"
fi

echo ""
echo "==> Step 2: Starting MCP Server (MCPart with 50 tools)..."
echo ""

# Create necessary directories
mkdir -p "$PROJECT_DIR/artifacts"
mkdir -p "$PROJECT_DIR/logs"

# Start unified MCP server (mcpart with filesystem, business, and universal tools)
# 50 total tools: 14 filesystem + 36 business management
MCP_CMD="cd $PROJECT_DIR/agent_s/mcp/mcpart && $HOME/.local/bin/uvx mcpo --port 8002 -- node build/index.js"
start_service "mcp-server" "$MCP_CMD" 8002

echo ""
echo "==> Step 3: Starting Agent-S..."
echo ""

# Activate venv and start Agent-S
AGENT_CMD="cd $PROJECT_DIR && source venv/bin/activate && python agent_s/server.py"
start_service "agent-s" "$AGENT_CMD" 8001

echo ""
echo "==> Step 4: Starting OpenWebUI..."
echo ""

# Set environment variables for OpenWebUI
export OLLAMA_BASE_URL=http://localhost:11434
export WEBUI_AUTH=false  # Disable auth for local dev
export DATA_DIR="$PROJECT_DIR/openwebui_data"

mkdir -p "$DATA_DIR"

# Start OpenWebUI
OPENWEBUI_CMD="cd $PROJECT_DIR && source venv/bin/activate && open-webui serve --host 0.0.0.0 --port 8080"
start_service "openwebui" "$OPENWEBUI_CMD" 8080

echo ""
echo "=================================================="
echo -e "${GREEN}All Services Started!${NC}"
echo "=================================================="
echo ""
echo "Access URLs:"
echo -e "  ${BLUE}OpenWebUI:${NC}    http://localhost:8080"
echo -e "  ${BLUE}Ollama:${NC}       http://localhost:11434"
echo -e "  ${BLUE}MCP Server:${NC}   http://localhost:8002"
echo -e "  ${BLUE}Agent-S:${NC}      http://localhost:8001"
echo ""
echo "Logs are in: $PROJECT_DIR/logs/"
echo ""
echo "To stop all services:"
echo "  $SCRIPT_DIR/stop-all.sh"
echo ""
echo "To view logs:"
echo "  tail -f $PROJECT_DIR/logs/openwebui.log"
echo "  tail -f $PROJECT_DIR/logs/mcp-server.log"
echo "  tail -f $PROJECT_DIR/logs/agent-s.log"
echo ""

# Wait a moment for services to stabilize
sleep 3

echo "Checking service status..."
echo ""

# Check each service
services=("ollama:11434" "mcp-server:8002" "agent-s:8001" "openwebui:8080")
for service in "${services[@]}"; do
    IFS=':' read -r name port <<< "$service"
    if port_in_use $port; then
        echo -e "  ${GREEN}✓${NC} $name (port $port)"
    else
        echo -e "  ${RED}✗${NC} $name (port $port) - NOT RUNNING"
    fi
done

echo ""
echo -e "${GREEN}Ready to use!${NC} Open http://localhost:8080 in your browser"
echo ""
