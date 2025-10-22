#!/bin/bash
# Stop AlphaOmega services

echo "Stopping AlphaOmega services..."

# Stop container services (if any)
if [ -x ./scripts/stop-searxng.sh ]; then
	./scripts/stop-searxng.sh > /dev/null 2>&1 || true
fi

if [ -x ./scripts/stop-comfyui.sh ]; then
	./scripts/stop-comfyui.sh > /dev/null 2>&1 || true
fi

# Stop Ollama services
pkill -f "ollama serve" || true

# Stop Agent-S server
pkill -f "python.*agent_s.server" || true

# Stop MCP server
pkill -f "mcpo.*800[0-9]" || true
pkill -f "node.*build/index.js" || true

# Stop Chatterbox TTS (Docker)
if command -v docker >/dev/null 2>&1; then
	./scripts/stop-tts.sh > /dev/null 2>&1 || true
fi

echo "✓ All services stopped"
