#!/bin/bash
echo "🔍 Verifying Individual MCP Tools Registration"
echo ""

# Check MCP server
echo "1️⃣ MCP Server (mcpo on port 8002):"
if curl -s http://localhost:8002/openapi.json > /dev/null; then
    TOOL_COUNT=$(curl -s http://localhost:8002/openapi.json | jq '.paths | length')
    echo "   ✅ Running - $TOOL_COUNT endpoints available"
else
    echo "   ❌ Not responding"
fi

# Check OpenWebUI
echo ""
echo "2️⃣ OpenWebUI (port 8080):"
if curl -s http://localhost:8080 > /dev/null; then
    echo "   ✅ Running"
else
    echo "   ❌ Not responding"
fi

# Check database registrations
echo ""
echo "3️⃣ Individual Tool Registrations in Database:"
DB_COUNT=$(sqlite3 /home/stacy/AlphaOmega/openwebui_data/webui.db "SELECT COUNT(*) FROM tool WHERE id LIKE 'mcp_%'")
echo "   ✅ $DB_COUNT individual tools registered"

# Show sample tools
echo ""
echo "4️⃣ Sample Registered Tools:"
sqlite3 /home/stacy/AlphaOmega/openwebui_data/webui.db "SELECT id, name FROM tool WHERE id LIKE 'mcp_%' LIMIT 10" | while IFS='|' read -r id name; do
    echo "   • $name ($id)"
done

# Check old monolithic tool
echo ""
echo "5️⃣ Old Monolithic Tool:"
OLD_COUNT=$(sqlite3 /home/stacy/AlphaOmega/openwebui_data/webui.db "SELECT COUNT(*) FROM tool WHERE id = 'mcp_tools_openapi'")
if [ "$OLD_COUNT" -eq 0 ]; then
    echo "   ✅ Removed (no longer exists)"
else
    echo "   ⚠️ Still exists (should be removed)"
fi

echo ""
echo "═══════════════════════════════════════════════════"
echo "🎯 READY TO TEST:"
echo "   1. Refresh OpenWebUI (Ctrl+Shift+R)"
echo "   2. Click 🔧 Tools icon in chat input"
echo "   3. Search for 'task' or 'inventory'"
echo "   4. Enable the tools you want"
echo "   5. Ask: 'What tasks do I have?'"
echo "═══════════════════════════════════════════════════"
