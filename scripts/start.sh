#!/bin/bash
# Start AlphaOmega services

set -e

echo "Starting AlphaOmega services..."

# Load environment
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
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

# Start Piper TTS API
echo "Starting Piper TTS API..."
if ! pgrep -f "piper_api.py" > /dev/null; then
    cd tts && python piper_api.py > ../logs/piper-api.log 2>&1 &
    cd ..
    sleep 2
    echo "Started Piper TTS API on port 5002"
else
    echo "Piper TTS API already running"
fi

# Start Docker services
echo "Starting Docker services..."
docker-compose up -d

echo ""
echo "✓ AlphaOmega is starting up..."
echo ""
echo "Services:"
echo "  - OpenWebUI: http://localhost:3000"
echo "  - Agent-S API: http://localhost:8001"
echo "  - ComfyUI: http://localhost:8188"
echo "  - MCP Server: http://localhost:8002"
echo "  - Piper TTS API: http://localhost:5002"
echo ""
echo "Check status: docker-compose ps"
echo "View logs: docker-compose logs -f"
echo "Stop: ./scripts/stop.sh"
echo ""
