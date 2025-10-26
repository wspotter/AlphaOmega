#!/bin/bash
# Start AlphaOmega services

set -e

echo "Starting AlphaOmega services..."

# Load environment (properly filter comments and empty lines)
if [ -f .env ]; then
    set -a
    source <(grep -v '^#' .env | grep -v '^$' | sed 's/#.*$//')
    set +a
fi

# Set HSA override for MI50
export HSA_OVERRIDE_GFX_VERSION=9.0.0

echo "Starting Ollama services on GPUs..."
if ! pgrep -x "ollama" > /dev/null; then
    ROCR_VISIBLE_DEVICES=0 OLLAMA_HOST=127.0.0.1:11434 ollama serve > logs/ollama-vision.log 2>&1 &
    ROCR_VISIBLE_DEVICES=1 OLLAMA_HOST=127.0.0.1:11435 ollama serve > logs/ollama-reasoning.log 2>&1 &
    sleep 5
else
    echo "Ollama services already running"
fi
if curl -s http://localhost:11434/api/tags | grep -q "tags"; then
    echo "Ollama Vision (11434) is responsive."
else
    echo "Ollama Vision (11434) is NOT responsive!"
fi
if curl -s http://localhost:11435/api/tags | grep -q "tags"; then
    echo "Ollama Reasoning (11435) is responsive."
else
    echo "Ollama Reasoning (11435) is NOT responsive!"
fi

echo "Starting Chatterbox TTS service..."
if command -v docker >/dev/null 2>&1; then
    if ! docker ps --format '{{.Names}}' | grep -q '^alphaomega-chatterbox$'; then
        ./scripts/start-tts.sh > /dev/null 2>&1 || true
        sleep 3
    fi
    if curl -s http://localhost:5003/health | grep -q ok; then
        echo "Chatterbox TTS (5003) is responsive."
    else
        echo "Chatterbox TTS (5003) is NOT responsive!"
    fi
else
    echo "Docker not available; skipping Chatterbox startup"
fi

echo "Starting Agent-S server..."
if ! pgrep -f "agent_s/server.py" > /dev/null; then
    ./scripts/start-agent_s.sh > /dev/null 2>&1
    sleep 3
fi
if curl -s http://localhost:8001/health | grep -q ok; then
    echo "Agent-S (8001) is responsive."
else
    echo "Agent-S (8001) is NOT responsive!"
fi

echo "Starting MCP server..."
if ! pgrep -f "mcpo.*8002" > /dev/null; then
    ./scripts/start-mcp-unified.sh >/dev/null 2>&1
    sleep 3
fi
if curl -s http://localhost:8002/openapi.json | grep -q openapi; then
    echo "MCP Server (8002) is responsive."
else
    echo "MCP Server (8002) is NOT responsive!"
fi

# Start container services (Docker-approved trio only)
echo "Starting container services..."

if command -v docker >/dev/null 2>&1; then
    ./scripts/start-searxng.sh > /dev/null 2>&1 || true
    sleep 3
    if curl -s http://localhost:8181 | grep -q "<title>SearxNG"; then
        echo "SearxNG (8181) is responsive."
    else
        echo "SearxNG (8181) is NOT responsive!"
    fi
else
    echo "Docker not available; skipping SearxNG startup"
fi

if command -v docker >/dev/null 2>&1; then
    ./scripts/start-comfyui.sh > /dev/null 2>&1 || true
    sleep 3
    if curl -s http://localhost:8188/system_stats | grep -q system; then
        echo "ComfyUI (8188) is responsive."
    else
        echo "ComfyUI (8188) is NOT responsive!"
    fi
else
    echo "Docker not available; skipping ComfyUI startup"
fi

# Note: OpenWebUI runs on host unless launched separately
echo "OpenWebUI should be started manually if needed"

# Start Pipeline Server
echo "🔗 Starting Pipeline Server..."
./scripts/start-pipeline-server.sh

echo ""
echo "✓ AlphaOmega is starting up..."
echo ""
echo "Services:"
echo "  - OpenWebUI: http://localhost:8080"
echo "  - Agent-S API: http://localhost:8001"
echo "  - ComfyUI: http://localhost:${COMFYUI_PORT:-8188}"
echo "  - MCP Server: http://localhost:8002"
echo "  - Chatterbox TTS: http://localhost:5003"
echo "  - SearxNG Meta Search: http://localhost:${SEARXNG_PORT:-8081}"
echo ""
echo "Check status: ./scripts/status.sh"
echo "View logs: tail -f logs/*.log"
echo "Stop: ./scripts/stop.sh"
echo ""
