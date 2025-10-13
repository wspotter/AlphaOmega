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

# Start Ollama services first (not in Docker)
echo "Starting Ollama services on GPUs..."

# Check if Ollama is already running
if ! pgrep -x "ollama" > /dev/null; then
    # Start Ollama for GPU 0 (Vision)
    ROCR_VISIBLE_DEVICES=0 OLLAMA_HOST=127.0.0.1:11434 ollama serve > logs/ollama-vision.log 2>&1 &
    echo "Started Ollama Vision (GPU 0) on port 11434"
    
    # Start Ollama for GPU 1 (Reasoning)
    ROCR_VISIBLE_DEVICES=1 OLLAMA_HOST=127.0.0.1:11435 ollama serve > logs/ollama-reasoning.log 2>&1 &
    echo "Started Ollama Reasoning (GPU 1) on port 11435"
    
    # Wait for Ollama to be ready
    sleep 5
else
    echo "Ollama services already running"
fi

# Start Coqui TTS API
echo "Starting Coqui TTS API..."
if ! pgrep -f "coqui_api.py" > /dev/null; then
    ./tts/start_coqui_api.sh > /dev/null 2>&1
    echo "Started Coqui TTS API on port 5002"
else
    echo "Coqui TTS API already running"
fi

# Start Agent-S server
echo "Starting Agent-S server..."
if ! pgrep -f "python.*agent_s.server" > /dev/null; then
    xvfb-run -a python -m agent_s.server > logs/agent_actions.log 2>&1 &
    echo "Started Agent-S on port 8001 (with virtual display)"
else
    echo "Agent-S already running"
fi

# Start MCP server
echo "Starting MCP server..."
if ! pgrep -f "node.*build/index.js" > /dev/null; then
    cd agent_s/mcp/mcpart && npm start > ../../../logs/mcp.log 2>&1 &
    echo "Started MCP Server on port 8002"
else
    echo "MCP Server already running"
fi

# Start container services (OpenWebUI and ComfyUI only)
echo "Starting container services..."
# Note: Running OpenWebUI and ComfyUI directly on host instead of Docker
echo "OpenWebUI and ComfyUI should be started manually if needed"

echo ""
echo "✓ AlphaOmega is starting up..."
echo ""
echo "Services:"
echo "  - OpenWebUI: http://localhost:3000"
echo "  - Agent-S API: http://localhost:8001"
echo "  - ComfyUI: http://localhost:8188"
echo "  - MCP Server: http://localhost:8002"
echo "  - Coqui TTS API: http://localhost:5002"
echo ""
echo "Check status: ./scripts/status.sh"
echo "View logs: tail -f logs/*.log"
echo "Stop: ./scripts/stop.sh"
echo ""
