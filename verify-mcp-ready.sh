#!/bin/bash
# Quick verification that everything is ready for testing

echo "=========================================="
echo "MCP Routing Readiness Check"
echo "=========================================="
echo ""

# Check MCP Server
echo "1. Checking MCP Server (port 8002)..."
if curl -s http://localhost:8002/openapi.json > /dev/null 2>&1; then
    TOOL_COUNT=$(curl -s http://localhost:8002/openapi.json | jq '.paths | keys | length' 2>/dev/null)
    echo "   ✅ MCP Server running ($TOOL_COUNT tools available)"
else
    echo "   ❌ MCP Server NOT responding"
    echo "      Fix: bash scripts/start-mcp-unified.sh"
fi

echo ""

# Check OpenWebUI
echo "2. Checking OpenWebUI (port 8080)..."
if curl -s -I http://localhost:8080 | grep "200 OK" > /dev/null 2>&1; then
    echo "   ✅ OpenWebUI running"
    echo "      URL: http://localhost:8080"
else
    echo "   ❌ OpenWebUI NOT responding"
    echo "      Fix: bash scripts/start-openwebui.sh"
fi

echo ""

# Check Pipeline
echo "3. Checking Router Pipeline..."
if [ -f "/home/stacy/AlphaOmega/pipelines/alphaomega_router.py" ]; then
    LINE_COUNT=$(wc -l < /home/stacy/AlphaOmega/pipelines/alphaomega_router.py)
    echo "   ✅ Pipeline exists ($LINE_COUNT lines)"
    
    # Check syntax
    if python3 -c "import ast; ast.parse(open('/home/stacy/AlphaOmega/pipelines/alphaomega_router.py').read())" 2>/dev/null; then
        echo "   ✅ Syntax valid"
    else
        echo "   ❌ Syntax errors found"
    fi
else
    echo "   ❌ Pipeline file not found"
fi

echo ""

# Test MCP tool
echo "4. Testing MCP Tool (list_tasks)..."
TASKS_RESULT=$(curl -s -X POST http://localhost:8002/list_tasks -H "Content-Type: application/json" -d '{}' 2>/dev/null)
if [ $? -eq 0 ] && [ ! -z "$TASKS_RESULT" ]; then
    TASK_COUNT=$(echo "$TASKS_RESULT" | jq 'length' 2>/dev/null)
    echo "   ✅ MCP tool responding ($TASK_COUNT tasks found)"
else
    echo "   ⚠️  MCP tool returned empty result (might be no tasks)"
fi

echo ""

# Test Router Logic
echo "5. Testing Router Intent Detection..."
cd /home/stacy/AlphaOmega
TEST_OUTPUT=$(python3 test_mcp_router.py 2>&1)
if echo "$TEST_OUTPUT" | grep -q "Test Complete!"; then
    MCP_COUNT=$(echo "$TEST_OUTPUT" | grep "Intent: mcp" | wc -l)
    echo "   ✅ Router test passed ($MCP_COUNT MCP intents detected)"
else
    echo "   ❌ Router test failed"
fi

echo ""
echo "=========================================="
echo "Readiness Status"
echo "=========================================="
echo ""

# Count checks
ALL_CHECKS=5
PASSED_CHECKS=0

curl -s http://localhost:8002/openapi.json > /dev/null 2>&1 && ((PASSED_CHECKS++))
curl -s -I http://localhost:8080 | grep "200 OK" > /dev/null 2>&1 && ((PASSED_CHECKS++))
[ -f "/home/stacy/AlphaOmega/pipelines/alphaomega_router.py" ] && ((PASSED_CHECKS++))
python3 -c "import ast; ast.parse(open('/home/stacy/AlphaOmega/pipelines/alphaomega_router.py').read())" 2>/dev/null && ((PASSED_CHECKS++))
echo "$TEST_OUTPUT" | grep -q "Test Complete!" && ((PASSED_CHECKS++))

if [ $PASSED_CHECKS -eq $ALL_CHECKS ]; then
    echo "✅ READY TO TEST! ($PASSED_CHECKS/$ALL_CHECKS checks passed)"
    echo ""
    echo "Next Step: Open http://localhost:8080 and try:"
    echo "  • 'What tasks do I have?'"
    echo "  • 'Check inventory for paint'"
    echo "  • 'Show me all customers'"
    echo ""
    echo "Documentation:"
    echo "  • Test Guide: MCP_ROUTING_TEST_GUIDE.md"
    echo "  • Complete Guide: MCP_ROUTING_COMPLETE.md"
else
    echo "⚠️  Some checks failed ($PASSED_CHECKS/$ALL_CHECKS passed)"
    echo ""
    echo "Review the output above to see what needs fixing."
fi

echo ""
echo "=========================================="
