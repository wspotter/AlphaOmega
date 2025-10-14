#!/bin/bash
echo "🔍 Final Verification - MCP Tools with Parameters"
echo ""

# Check one tool's parameter schema
echo "1️⃣ Sample Tool (List Tasks) - Parameter Schema:"
sqlite3 /home/stacy/AlphaOmega/openwebui_data/webui.db \
  "SELECT substr(content, 400, 600) FROM tool WHERE id = 'mcp_tool_list_tasks_post'" | \
  grep -A 10 "class tool_list_tasks_post_params"

echo ""
echo "2️⃣ Tool Count by Parameter Count:"
sqlite3 /home/stacy/AlphaOmega/openwebui_data/webui.db <<EOF
SELECT 
  CASE 
    WHEN content LIKE '%0 params%' THEN '0 params'
    WHEN content LIKE '%1 params%' THEN '1 param'
    WHEN content LIKE '%2 params%' THEN '2 params'
    WHEN content LIKE '%3 params%' THEN '3 params'
    WHEN content LIKE '%4 params%' THEN '4 params'
    WHEN content LIKE '%5 params%' THEN '5+ params'
    ELSE 'unknown'
  END as param_count,
  COUNT(*) as tools
FROM tool
WHERE id LIKE 'mcp_%'
GROUP BY param_count;
EOF

echo ""
echo "3️⃣ Tools with Proper Type Hints:"
if sqlite3 /home/stacy/AlphaOmega/openwebui_data/webui.db \
  "SELECT content FROM tool WHERE id = 'mcp_tool_list_tasks_post'" | \
  grep -q "Optional\[str\]"; then
  echo "   ✅ Type hints present (Optional[str], Optional[List], etc.)"
else
  echo "   ❌ Type hints missing"
fi

echo ""
echo "4️⃣ Tools with Pydantic BaseModel:"
if sqlite3 /home/stacy/AlphaOmega/openwebui_data/webui.db \
  "SELECT content FROM tool WHERE id = 'mcp_tool_list_tasks_post'" | \
  grep -q "class.*_params(BaseModel)"; then
  echo "   ✅ Pydantic parameter classes defined"
else
  echo "   ❌ Pydantic classes missing"
fi

echo ""
echo "═══════════════════════════════════════════════════"
echo "🎯 READY TO TEST (should work now!):"
echo "   1. Refresh OpenWebUI: Ctrl+Shift+R"
echo "   2. Enable 'List Tasks' tool in 🔧 Tools menu"
echo "   3. Ask: 'What tasks do I have?'"
echo "   4. Expected: No more 'parameters' error!"
echo "═══════════════════════════════════════════════════"
