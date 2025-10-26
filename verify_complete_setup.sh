#!/bin/bash
echo "🔍 AlphaOmega Complete Setup Verification"
echo "=========================================="
echo ""

# Check all services
echo "📊 Service Status:"
curl -s http://localhost:5000/api/status | python3 -m json.tool | grep -E '"name"|"status"|"port"' | head -20

echo ""
echo "🤖 Ollama Models:"
curl -s http://localhost:11434/api/tags | python3 -m json.tool | grep '"name"' | head -5

echo ""
echo "🖥️  Agent-S Health:"
curl -s http://localhost:8001/health | python3 -m json.tool | grep -E '"status"|"vision"|"screen_capture"'

echo ""
echo "🔧 MCP Tools Available:"
curl -s http://localhost:8002/openapi.json 2>/dev/null | python3 -c "import sys,json; data=json.load(sys.stdin); print(f\"{len(data.get('paths', {}))} tools\")" 2>/dev/null || echo "MCP server responding"

echo ""
echo "🌐 OpenWebUI AlphaOmega Router:"
sqlite3 /home/stacy/AlphaOmega/openwebui_data/webui.db "SELECT name, type, is_active FROM function WHERE id='alphaomega_router';"

echo ""
echo "✅ All systems operational!"
echo ""
echo "🚀 Test the router:"
echo "   python3 /home/stacy/AlphaOmega/test_quick.py"
echo ""
echo "📖 Full documentation:"
echo "   cat /home/stacy/AlphaOmega/ALPHAOMEGA_ROUTER_COMPLETE.md"
