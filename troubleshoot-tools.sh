#!/bin/bash
echo "🔍 MCP Tools Troubleshooting"
echo ""

# 1. Check database
echo "1️⃣ Tools in Database:"
TOOL_COUNT=$(sqlite3 /home/stacy/AlphaOmega/openwebui_data/webui.db "SELECT COUNT(*) FROM tool WHERE id LIKE 'mcp_%'")
echo "   📊 $TOOL_COUNT MCP tools registered"

# 2. Check user
echo ""
echo "2️⃣ User Info:"
sqlite3 /home/stacy/AlphaOmega/openwebui_data/webui.db "SELECT email, role FROM user"

# 3. Check sample tool
echo ""
echo "3️⃣ Sample Tool (List Tasks):"
echo "   ID: mcp_tool_list_tasks_post"
echo "   Name:"
sqlite3 /home/stacy/AlphaOmega/openwebui_data/webui.db "SELECT '      ' || name FROM tool WHERE id = 'mcp_tool_list_tasks_post'"

# 4. Check access control
echo ""
echo "4️⃣ Access Control:"
GLOBAL_COUNT=$(sqlite3 /home/stacy/AlphaOmega/openwebui_data/webui.db "SELECT COUNT(*) FROM tool WHERE id LIKE 'mcp_%' AND access_control LIKE '%group_ids%'")
echo "   🌐 $GLOBAL_COUNT tools set to global access"

# 5. Check if OpenWebUI is running
echo ""
echo "5️⃣ OpenWebUI Status:"
if curl -s http://localhost:8080 > /dev/null 2>&1; then
    echo "   ✅ Running on port 8080"
else
    echo "   ❌ Not responding on port 8080"
fi

# 6. Check MCP server
echo ""
echo "6️⃣ MCP Server Status:"
if curl -s http://localhost:8002/openapi.json > /dev/null 2>&1; then
    echo "   ✅ mcpo running on port 8002"
else
    echo "   ❌ mcpo not responding"
fi

echo ""
echo "═══════════════════════════════════════════════════"
echo "🎯 HOW TO CHECK IN UI:"
echo ""
echo "1. Open http://localhost:8080"
echo "2. Log in as: admin@localhost"
echo "3. Click your profile (top right)"
echo "4. Go to: Settings → Workspace → Tools"
echo "5. OR in chat: Click 🔧 icon next to message input"
echo ""
echo "If still no tools visible:"
echo "- Check browser console (F12) for errors"
echo "- Clear browser cache (Ctrl+Shift+Delete)"
echo "- Try incognito/private window"
echo "═══════════════════════════════════════════════════"
