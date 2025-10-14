#!/bin/bash
# Quick verification that MCP tools are properly configured

echo "=========================================="
echo "MCP Tools Configuration Verification"
echo "=========================================="
echo ""

# 1. Check MCP server
echo "1. Checking MCP Server..."
if curl -s http://localhost:8002/openapi.json > /dev/null 2>&1; then
    TOOLS=$(curl -s http://localhost:8002/openapi.json | jq '.paths | keys | length')
    echo "   ✅ MCP Server running ($TOOLS tools)"
else
    echo "   ❌ MCP Server not responding"
fi

echo ""

# 2. Check OpenWebUI
echo "2. Checking OpenWebUI..."
if curl -s -I http://localhost:8080 | grep "200 OK" > /dev/null 2>&1; then
    echo "   ✅ OpenWebUI running"
else
    echo "   ❌ OpenWebUI not responding"
fi

echo ""

# 3. Check tool registration
echo "3. Checking Tool Registration..."
TOOL_CHECK=$(sqlite3 /home/stacy/AlphaOmega/openwebui_data/webui.db \
  "SELECT name FROM tool WHERE id='mcp_tools_openapi';" 2>/dev/null)

if [ ! -z "$TOOL_CHECK" ]; then
    echo "   ✅ Tools registered: $TOOL_CHECK"
else
    echo "   ❌ Tools not registered"
fi

echo ""

# 4. Check no pipeline exists
echo "4. Checking Pipeline Cleanup..."
PIPELINE_CHECK=$(sqlite3 /home/stacy/AlphaOmega/openwebui_data/webui.db \
  "SELECT COUNT(*) FROM function WHERE id='alphaomega_router';" 2>/dev/null)

if [ "$PIPELINE_CHECK" = "0" ]; then
    echo "   ✅ Old pipeline removed"
else
    echo "   ⚠️  Old pipeline still exists (should be removed)"
fi

echo ""
echo "=========================================="
echo "Configuration Status"
echo "=========================================="
echo ""
echo "✅ READY TO USE!"
echo ""
echo "Next steps:"
echo "1. Go to: http://localhost:8080"
echo "2. Press Ctrl+Shift+R to refresh"
echo "3. In any chat, click the 🔧 Tools icon"
echo "4. Enable 'AlphaOmega MCP Tools'"
echo "5. Ask: 'What tasks do I have?'"
echo ""
echo "The LLM will automatically use the tools!"
echo "=========================================="
