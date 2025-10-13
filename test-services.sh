#!/bin/bash
# Test all AlphaOmega services

echo "================================"
echo "AlphaOmega Service Tests"
echo "================================"
echo ""

# Test OpenWebUI
echo "1. Testing OpenWebUI..."
if curl -s http://localhost:8080/api/config | grep -q "version"; then
    echo "   ✅ OpenWebUI is responding"
else
    echo "   ❌ OpenWebUI is not responding"
fi
echo ""

# Test Ollama
echo "2. Testing Ollama..."
MODEL_COUNT=$(curl -s http://localhost:11434/api/tags 2>/dev/null | jq -r '.models | length')
if [ ! -z "$MODEL_COUNT" ]; then
    echo "   ✅ Ollama is running with $MODEL_COUNT models"
else
    echo "   ❌ Ollama is not responding"
fi
echo ""

# Test Agent-S
echo "3. Testing Agent-S..."
AGENT_STATUS=$(curl -s http://localhost:8001/health 2>/dev/null | jq -r '.status')
if [ "$AGENT_STATUS" = "healthy" ]; then
    echo "   ✅ Agent-S is healthy"
    echo "   Testing screenshot capability..."
    curl -X POST http://localhost:8001/action \
        -H "Content-Type: application/json" \
        -d '{"prompt":"take a screenshot","safe_mode":true}' \
        -s | jq -r '.response' | head -3
    echo ""
else
    echo "   ❌ Agent-S is not responding"
fi
echo ""

# Test ComfyUI
echo "4. Testing ComfyUI..."
if curl -s http://localhost:8188/system_stats 2>/dev/null | grep -q "system"; then
    echo "   ✅ ComfyUI is running"
else
    echo "   ❌ ComfyUI is not running"
    echo "   (This is normal if you haven't started it yet)"
fi
echo ""

echo "================================"
echo "Test Complete"
echo "================================"
