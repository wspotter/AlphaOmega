#!/bin/bash
# Stop AlphaOmega services

echo "Stopping AlphaOmega services..."

# Stop container services (if any)
# Note: No Docker containers are used in host-only mode

# Stop Ollama services
pkill -f "ollama serve" || true

# Stop Agent-S server
pkill -f "python.*agent_s.server" || true

# Stop MCP server
pkill -f "node.*build/index.js" || true

# Stop Coqui TTS API
./tts/stop_coqui_api.sh > /dev/null 2>&1 || true

echo "✓ All services stopped"
