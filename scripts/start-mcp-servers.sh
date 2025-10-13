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

# Start MCP Filesystem Server (Port 8002)
echo -e "${BLUE}Starting MCP Filesystem Server (Port 8002)...${NC}"
mkdir -p "$PROJECT_DIR/artifacts"
mkdir -p "$PROJECT_DIR/logs"

$HOME/.local/bin/uvx mcpo --port 8002 -- npx -y @modelcontextprotocol/server-filesystem \
  "$PROJECT_DIR/artifacts" \
  "$PROJECT_DIR/logs" \
  "$PROJECT_DIR" \
  > "$PROJECT_DIR/logs/mcp-filesystem.log" 2>&1 &

sleep 3
if curl -s http://localhost:8002/docs > /dev/null; then
    echo -e "${GREEN}✓ MCP Filesystem Server running${NC}"
    echo "  Tools: File operations (read, write, edit, search)"
else
    echo -e "${RED}✗ Failed to start Filesystem server${NC}"
fi

# Start MCPart Server (Port 8003)
echo ""
echo -e "${BLUE}Starting MCPart Server (Port 8003)...${NC}"
cd "$PROJECT_DIR/agent_s/mcp/mcpart"

# Build if needed
if [ ! -d "build" ]; then
    echo "Building mcpart..."
    npm run build
fi

$HOME/.local/bin/uvx mcpo --port 8003 -- node build/index.js \
  > "$PROJECT_DIR/logs/mcpart.log" 2>&1 &

sleep 3
if curl -s http://localhost:8003/docs > /dev/null; then
    echo -e "${GREEN}✓ MCPart Server running${NC}"
    echo "  Tools: Business management (36 tools)"
else
    echo -e "${RED}✗ Failed to start MCPart server${NC}"
fi

echo ""
echo "=================================================="
echo -e "${GREEN}MCP Servers Started!${NC}"
echo "=================================================="
echo ""
echo "Available Servers:"
echo ""
echo -e "  ${BLUE}MCP Filesystem${NC} (14 tools)"
echo "    URL: http://localhost:8002"
echo "    Docs: http://localhost:8002/docs"
echo "    Tools: read_file, write_file, list_directory, etc."
echo ""
echo -e "  ${BLUE}MCPart${NC} (36 tools)"
echo "    URL: http://localhost:8003"
echo "    Docs: http://localhost:8003/docs"
echo "    Tools: inventory, customers, sales, analytics, etc."
echo ""
echo "=================================================="
echo ""
echo "Add to OpenWebUI:"
echo "  Admin Panel → Settings → External Tools"
echo "  Click [+] under 'Manage Tool Servers'"
echo ""
echo "  Server 1:"
echo "    Name: MCP Filesystem"
echo "    URL:  http://localhost:8002"
echo ""
echo "  Server 2:"
echo "    Name: MCPart Business Tools"
echo "    URL:  http://localhost:8003"
echo ""
echo "Total Tools Available: 50 tools"
echo ""
