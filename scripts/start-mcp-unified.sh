#!/bin/bash
# Start UNIFIED MCP Server
# This starts ONE MCP server on port 8002 with ALL 76 tools unified
# DO NOT split this into multiple servers!

set -e

PROJECT_DIR="/home/stacy/AlphaOmega"
cd "$PROJECT_DIR"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo "=================================================="
echo "Starting UNIFIED MCP Server (76 Tools)"
echo "=================================================="
echo ""

# Stop any existing MCP servers
echo "Stopping existing MCP servers..."
pkill -f "mcpo.*800[0-9]" 2>/dev/null || true
sleep 2

# Ensure build directory exists
if [ ! -d "$PROJECT_DIR/mcpart/build" ]; then
    echo -e "${RED}✗ mcpart build directory not found${NC}"
    echo "Run: cd $PROJECT_DIR/mcpart && npm install && npm run build"
    exit 1
fi

# Verify index.js exists
if [ ! -f "$PROJECT_DIR/mcpart/build/index.js" ]; then
    echo -e "${RED}✗ mcpart/build/index.js not found${NC}"
    exit 1
fi

# Create logs directory
mkdir -p "$PROJECT_DIR/logs"

# Start UNIFIED MCP server on port 8002
echo -e "${YELLOW}Starting unified MCP server on port 8002...${NC}"
$HOME/.local/bin/uvx mcpo --port 8002 -- node mcpart/build/index.js \
  > "$PROJECT_DIR/logs/mcp-unified.log" 2>&1 &

MCP_PID=$!
echo $MCP_PID > /tmp/mcp-unified.pid

# Wait for server to start
sleep 4

# Verify server is running
if curl -s http://localhost:8002/openapi.json > /dev/null 2>&1; then
    TOOL_COUNT=$(curl -s http://localhost:8002/openapi.json | jq '.paths | keys | length')
    echo -e "${GREEN}✓ Unified MCP Server running${NC}"
    echo -e "  ${GREEN}Port: 8002${NC}"
    echo -e "  ${GREEN}Tools: $TOOL_COUNT${NC}"
    echo -e "  ${GREEN}PID: $MCP_PID${NC}"
    echo ""
    echo -e "${GREEN}Tool Categories:${NC}"
    echo "  • Inventory Management (12 tools)"
    echo "  • Sales & Analytics (8 tools)"
    echo "  • Social Media (12 tools)"
    echo "  • Task & Calendar (10 tools)"
    echo "  • File System (13 tools)"
    echo "  • Business Operations (11 tools)"
    echo "  • VIP Clients (6 tools)"
    echo "  • Universal Tools (4 tools)"
else
    echo -e "${RED}✗ Failed to start MCP server${NC}"
    echo "Check logs: tail -f $PROJECT_DIR/logs/mcp-unified.log"
    exit 1
fi

echo ""
echo "=================================================="
echo -e "${GREEN}MCP Server Ready!${NC}"
echo "=================================================="
echo ""
echo "API Documentation:"
echo "  http://localhost:8002/docs"
echo ""
echo "OpenAPI Spec:"
echo "  http://localhost:8002/openapi.json"
echo ""
echo "Test endpoint:"
echo "  curl http://localhost:8002/get_low_stock_items"
echo ""
echo "Logs:"
echo "  tail -f logs/mcp-unified.log"
echo ""
echo "Stop:"
echo "  pkill -f 'mcpo.*8002'"
echo ""
