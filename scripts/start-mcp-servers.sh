#!/bin/bash
# Start multiple MCP servers for OpenWebUI integration

set -e

PROJECT_DIR="/home/stacy/AlphaOmega"
cd "$PROJECT_DIR"

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo ""
echo "=================================================="
echo "Starting MCP Servers"
echo "=================================================="
echo ""

# Stop any existing MCP servers
echo "Stopping existing MCP servers..."
pkill -f "mcpo.*800[2-9]" 2>/dev/null || true
pkill -f "node.*mcpart" 2>/dev/null || true
sleep 1

# Start unified MCPart MCP Server (Port 8002)
echo -e "${BLUE}Starting MCPart Unified MCP Server (Port 8002)...${NC}"

MCPART_DIR="$PROJECT_DIR/mcpart"

# Ensure build artifacts exist
if [ ! -f "$MCPART_DIR/build/index.js" ]; then
    echo "Building mcpart..."
    (cd "$MCPART_DIR" && npm run build)
fi

mkdir -p "$PROJECT_DIR/logs"

(
  cd "$MCPART_DIR" && \
  $HOME/.local/bin/uvx mcpo --port 8002 -- node build/index.js
) > "$PROJECT_DIR/logs/mcpart.log" 2>&1 &

sleep 3
if curl -s http://localhost:8002/docs > /dev/null; then
    echo -e "${GREEN}✓ MCPart Unified MCP Server running${NC}"
    echo "  Tools: Filesystem + Business management (50 tools)"
else
    echo -e "${RED}✗ Failed to start MCPart server${NC}"
fi

echo ""
echo "=================================================="
echo -e "${GREEN}MCP Server Started!${NC}"
echo "=================================================="
echo ""
echo "Available Server:"
echo ""
echo -e "  ${BLUE}MCPart Unified MCP${NC}"
echo "    URL: http://localhost:8002"
echo "    Docs: http://localhost:8002/docs"
echo "    Tools: filesystem ops, inventory, CRM, scheduling, analytics, more"
echo ""
echo "=================================================="
echo ""
echo "Add to OpenWebUI:"
echo "  Admin Panel → Settings → External Tools"
echo "  Click [+] under 'Manage Tool Servers'"
echo ""
echo "  Server:"
echo "    Name: AlphaOmega MCP"
echo "    URL:  http://localhost:8002"
echo ""
